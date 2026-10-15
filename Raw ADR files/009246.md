# ADR-007: Redis Token Revocation Strategy

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2025-12-05 |
| **Decision Makers** | Project Team |

## Context

The project-starter template uses JWT access tokens for API authentication. JWTs are stateless by design - the token contains all information needed for validation (signature, claims, expiration). However, this creates a security challenge:

1. **Logout Requirement**: When a user logs out, their access token should be immediately invalidated
2. **Security Incidents**: Compromised tokens must be revokable before natural expiration
3. **Forced Logout**: Administrators may need to force logout users (account compromise, policy violation)
4. **Token Lifetime**: Shorter tokens require more frequent refresh; longer tokens have larger compromise windows

The system needs a mechanism to revoke tokens before their natural expiration while maintaining the performance benefits of stateless JWTs.

## Decision

We implement a **Redis-based token blacklist** for tracking revoked tokens with automatic TTL-based cleanup.

**Token Revocation Service** (`backend/app/services/token_revocation.py`):
```python
class TokenRevocationService:
    """
    Redis-based token revocation service for blacklisting JWT tokens.

    Security Model:
    - Fail closed: If Redis is unavailable during revocation check, reject the token
    - Fail open for revocation: If Redis is unavailable during revocation, return 503
    """

    async def revoke_token(self, jti: str, exp: int) -> None:
        """Add a token to the revocation blacklist with TTL."""
        current_time = int(time.time())
        ttl = exp - current_time

        if ttl <= 0:
            return  # Token already expired, no need to blacklist

        redis_key = f"revoked_token:{jti}"
        await self.redis_client.setex(name=redis_key, time=ttl, value="revoked")

    async def is_token_revoked(self, jti: str) -> bool:
        """Check if token is in blacklist. Returns True if revoked OR Redis fails."""
        redis_key = f"revoked_token:{jti}"
        try:
            return await self.redis_client.exists(redis_key)
        except redis.RedisError:
            # SECURITY: Fail closed - reject token if Redis unavailable
            return True
```

**Integration with Authentication** (`backend/app/api/dependencies/auth.py`):
```python
# Check if token has been revoked (blacklist check)
is_revoked = await token_revocation_service.is_token_revoked(token_payload.jti)
if is_revoked:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"error": "invalid_token", "error_description": "Token has been revoked"},
    )
```

**Revocation Endpoint** (`backend/app/api/routers/auth.py`):
```python
@router.post("/revoke", response_model=RevokeTokenResponse)
async def revoke_token(user: CurrentUser, token_revocation_service: ...) -> RevokeTokenResponse:
    """Revoke the current access token (logout)."""
    await token_revocation_service.revoke_token(jti=user.jti, exp=user.exp)
    return RevokeTokenResponse(message="Token revoked successfully", jti=user.jti)
```

## Consequences

### Positive

1. **Immediate Revocation**: Tokens are invalidated instantly across all backend instances:
   ```python
   # User logs out
   await token_revocation_service.revoke_token(jti="abc-123", exp=1762903147)

   # Subsequent request with same token (any backend instance)
   is_revoked = await token_revocation_service.is_token_revoked("abc-123")
   # is_revoked == True, request rejected
   ```

2. **Automatic Cleanup**: Redis TTL matches token expiration. When the token would have expired naturally, Redis automatically removes it from the blacklist:
   ```python
   # Token expires in 3600 seconds
   await redis_client.setex("revoked_token:abc-123", 3600, "revoked")
   # After 3600 seconds, key automatically deleted
   ```

3. **Memory Efficiency**: Only revoked tokens are stored (not all issued tokens). Typical patterns have <1% revocation rate, keeping blacklist small

4. **Sub-Millisecond Lookups**: Redis `EXISTS` command is O(1), adding negligible latency to authentication:
   ```
   # Typical lookup time
   EXISTS revoked_token:abc-123  # ~0.1ms
   ```

5. **Distributed by Design**: All backend instances share the same Redis, providing consistent revocation state without synchronization logic

6. **Fail-Closed Security**: If Redis is unavailable, tokens are rejected (security over availability):
   ```python
   except redis.RedisError as e:
       # SECURITY: Fail closed - if Redis is unavailable, reject the token
       return True  # Treat as revoked
   ```

### Negative

1. **Redis Dependency**: Token validation now requires Redis availability:
   - Redis failure causes all authentication to fail (fail-closed)
   - Adds infrastructure component to manage
   - Requires Redis HA (Sentinel/Cluster) for production reliability

2. **Lookup Overhead**: Every authenticated request requires a Redis lookup:
   - Adds ~0.1-0.5ms latency per request
   - Increases Redis operations linearly with request rate
   - At 10,000 req/sec, adds 10,000 Redis ops/sec

3. **Not Cryptographically Secure**: Revocation is based on JWT ID (jti), not cryptographic proof. If an attacker can predict or forge jti values, they could potentially check revocation status of other tokens (information disclosure, not security bypass)

4. **Clock Synchronization**: TTL calculation depends on synchronized clocks:
   ```python
   ttl = exp - current_time  # If clocks drift, TTL may be wrong
   ```

### Neutral

1. **Stateless vs Stateful Tradeoff**: Adds state (blacklist) to otherwise stateless JWT system. This is a conscious tradeoff for revocation capability

2. **jti Requirement**: Tokens must have unique `jti` claim. Keycloak includes this by default; custom token issuers must ensure this

## Alternatives Considered

### Short-Lived Tokens Only (No Revocation)

**Approach**: Use very short access tokens (5 minutes) so revocation isn't needed.

**Why Not Chosen**:
- **UX Impact**: Frequent token refresh degrades user experience
- **Refresh Token Attacks**: If refresh token is compromised, attacker has indefinite access
- **Security Gap**: 5 minutes is still too long for some security incidents
- **Network Overhead**: More frequent token refresh increases load

### Database-Based Blacklist

**Approach**: Store revoked tokens in PostgreSQL instead of Redis.

**Why Not Chosen**:
- **Latency**: Database queries are 10-100x slower than Redis lookups
- **Connection Pool**: Adds load to database connection pool
- **No Auto-Expiry**: Would need scheduled job to clean up expired entries
- **Wrong Tool**: Relational database for key-value lookups is inefficient

### Token Introspection (OAuth 2.0)

**Approach**: Call Keycloak's token introspection endpoint for every request.

**Why Not Chosen**:
- **Latency**: HTTP call adds 10-50ms per request
- **Keycloak Load**: Every API request hits Keycloak
- **Network Dependency**: Keycloak availability affects every request
- **Not Scalable**: Doesn't scale with API request rate

### Token Versioning in Database

**Approach**: Store token version per user; increment on logout.

**Why Not Chosen**:
- **Database Lookup**: Still requires database query per request
- **Granularity**: Revokes all tokens, not specific ones
- **Can't Revoke Specific**: Admin can't revoke single session

### Signed Revocation Lists

**Approach**: Periodically publish signed revocation list that clients cache.

**Why Not Chosen**:
- **Delay**: Revocation not immediate (depends on publish interval)
- **Complexity**: Requires distribution mechanism and client caching
- **Synchronization**: Harder to ensure all clients have latest list

---

## Related ADRs

- [ADR-004: Keycloak as Identity Provider](./004-keycloak-identity-provider.md) - JWT token issuance with jti claim
- [ADR-009: Cookie-Based Authentication Transport](./009-cookie-authentication.md) - How tokens reach the backend

## Implementation References

- `backend/app/services/token_revocation.py` - TokenRevocationService class
- `backend/app/api/dependencies/auth.py` - Revocation check in authentication flow
- `backend/app/api/routers/auth.py` - `/auth/revoke` endpoint
- `backend/app/core/config.py` - Redis connection configuration (`REDIS_URL`)
