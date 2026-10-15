# ADR-013: PKCE Enforcement for Public Clients

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2025-12-05 |
| **Decision Makers** | Project Team |

## Context

The project-starter template uses OAuth 2.0 Authorization Code flow for user authentication. The frontend is a Single Page Application (SPA) running in the browser - a "public client" that cannot securely store client secrets.

Security considerations:

1. **Public Client Limitations**: Browser-based applications cannot keep secrets. Any client_secret in JavaScript is extractable
2. **Authorization Code Interception**: The authorization code is passed via URL redirect, potentially visible to browser extensions, logs, or attackers
3. **OAuth 2.1 Direction**: The upcoming OAuth 2.1 specification mandates PKCE for all clients, not just public ones
4. **Best Practices**: RFC 7636 (PKCE) and OAuth 2.0 Security BCP recommend PKCE for all authorization code flows

The authentication flow must protect against authorization code interception attacks while working within browser security constraints.

## Decision

We enforce **PKCE (Proof Key for Code Exchange)** for all public OAuth clients.

PKCE adds a cryptographic challenge-response to the authorization code flow, ensuring that only the client that initiated the flow can exchange the authorization code for tokens.

**Frontend OIDC Configuration** (`frontend/src/auth/config.ts`):
```typescript
export const OIDC_CONFIG = {
  authority: 'http://keycloak.localtest.me:{{ cookiecutter.keycloak_port }}/realms/{{ cookiecutter.keycloak_realm_name }}',
  client_id: '{{ cookiecutter.keycloak_frontend_client_id }}',
  response_type: 'code',  // Authorization Code flow
  scope: 'openid profile email',
  automaticSilentRenew: true,
}
```

The `oidc-client-ts` library automatically implements PKCE when `response_type: 'code'` is configured.

**Keycloak Client Configuration** (`keycloak/setup-realm.sh`):
```json
{
    "clientId": "{{ cookiecutter.keycloak_frontend_client_id }}",
    "publicClient": true,
    "standardFlowEnabled": true,
    "implicitFlowEnabled": false,
    "directAccessGrantsEnabled": false,
    "attributes": {
        "pkce.code.challenge.method": "S256"
    }
}
```

**Backend OAuth Client** (`backend/app/services/oauth_client.py`):
```python
def generate_pkce_challenge(self) -> PKCEChallenge:
    """Generate PKCE code verifier and challenge."""
    # Generate random code verifier (43-128 characters, base64url)
    code_verifier = base64.urlsafe_b64encode(
        secrets.token_bytes(32)
    ).decode("utf-8").rstrip("=")

    # Generate code challenge (SHA256 hash, base64url)
    challenge_bytes = hashlib.sha256(
        code_verifier.encode("utf-8")
    ).digest()
    code_challenge = base64.urlsafe_b64encode(
        challenge_bytes
    ).decode("utf-8").rstrip("=")

    return PKCEChallenge(
        code_verifier=code_verifier,
        code_challenge=code_challenge,
        code_challenge_method="S256",
    )
```

**Configuration Enforcement** (`backend/app/core/config.py`):
```python
OAUTH_USE_PKCE: bool = True  # Enable PKCE for enhanced security
```

## Consequences

### Positive

1. **Authorization Code Protection**: Even if an attacker intercepts the authorization code, they cannot exchange it for tokens without the code_verifier:
   ```
   Attacker has: authorization_code
   Attacker missing: code_verifier (generated client-side, never transmitted until token exchange)
   Result: Token exchange fails
   ```

2. **No Client Secret Required**: Public clients don't need (and can't securely use) client secrets. PKCE provides equivalent security

3. **OAuth 2.1 Compliance**: Prepares for OAuth 2.1 which mandates PKCE for all authorization code grants

4. **Defense Against Multiple Attack Vectors**:
   - Browser history/logs capturing authorization codes
   - Malicious browser extensions reading URL parameters
   - Cross-site request forgery (combined with state parameter)
   - Open redirector attacks

5. **Keycloak Enforcement**: Setting `pkce.code.challenge.method: "S256"` makes Keycloak require PKCE - requests without code_challenge are rejected

6. **Standard Implementation**: Using `oidc-client-ts` means PKCE is implemented correctly without custom code. The library handles verifier generation, challenge computation, and token exchange

### Negative

1. **Slightly More Complex Flow**: PKCE adds steps to the authorization flow:
   - Generate code_verifier
   - Compute code_challenge
   - Send code_challenge with authorization request
   - Send code_verifier with token request

2. **State Management**: The code_verifier must be stored (typically in session storage) between authorization request and callback. If lost, the flow fails

3. **Debugging Complexity**: When troubleshooting authentication issues, PKCE adds another potential point of failure to investigate

4. **Older Library Compatibility**: Very old OAuth libraries may not support PKCE (though this is rare with modern libraries)

### Neutral

1. **S256 Method Only**: We use SHA256 for the code challenge method. The "plain" method exists but provides no security and is not configured

2. **Backend Also Uses PKCE**: The backend OAuth client (`OAuthClient` class) also implements PKCE for consistency, even though as a confidential client it could rely on client_secret

## PKCE Flow Details

**1. Authorization Request (Frontend to Keycloak)**:
```
GET /realms/{realm}/protocol/openid-connect/auth?
  response_type=code&
  client_id=frontend-client&
  redirect_uri=http://localhost:5173/auth/callback&
  scope=openid profile email&
  state={random_state}&
  code_challenge={SHA256(code_verifier)}&
  code_challenge_method=S256
```

**2. Authorization Response (Keycloak to Frontend)**:
```
HTTP/1.1 302 Found
Location: http://localhost:5173/auth/callback?
  code={authorization_code}&
  state={random_state}
```

**3. Token Request (Frontend to Keycloak)**:
```
POST /realms/{realm}/protocol/openid-connect/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&
code={authorization_code}&
redirect_uri=http://localhost:5173/auth/callback&
client_id=frontend-client&
code_verifier={original_code_verifier}
```

**4. Keycloak Validation**:
```
computed_challenge = BASE64URL(SHA256(code_verifier))
IF computed_challenge == stored_code_challenge THEN
  return tokens
ELSE
  return error (invalid_grant)
```

## Alternatives Considered

### Implicit Flow (response_type=token)

**Why Not Chosen**:
- **Deprecated**: OAuth 2.0 Security BCP recommends against implicit flow
- **Token Exposure**: Access token in URL fragment is logged, cached, and visible to JavaScript
- **No Refresh Tokens**: Implicit flow doesn't support refresh tokens
- **PKCE Exists**: PKCE solves the problems implicit flow was designed for, but better

### Client Credentials (Public Client Secret)

**Why Not Chosen**:
- **Impossible Security**: Browser JavaScript cannot keep secrets
- **Extractable**: Any client_secret in the bundle is visible to users and attackers
- **False Security**: Provides no actual protection while adding complexity

### Backend-for-Frontend (BFF) Pattern

**Approach**: Route all OAuth through the backend; frontend never handles tokens directly.

**Why Not Chosen**:
- **Added Complexity**: Requires additional backend endpoints for auth
- **Session Management**: Backend must manage sessions and token storage
- **PKCE Sufficient**: For most SPAs, PKCE provides adequate security
- **Latency**: Additional round-trip through backend for every auth operation

**When BFF Would Be Better**: Applications with extreme security requirements or needing to hide tokens from browser completely

---

## Related ADRs

- [ADR-002: Lit as Frontend Framework](./002-lit-frontend-framework.md) - Frontend implementing PKCE
- [ADR-004: Keycloak as Identity Provider](./004-keycloak-identity-provider.md) - IdP enforcing PKCE
- [ADR-001: FastAPI as Backend Framework](./001-fastapi-backend-framework.md) - Backend OAuth client with PKCE

## Implementation References

- `frontend/src/auth/service.ts` - AuthService using oidc-client-ts with PKCE
- `frontend/src/auth/config.ts` - OIDC configuration
- `backend/app/services/oauth_client.py` - PKCE challenge generation
- `backend/app/api/routers/oauth.py` - OAuth endpoints using PKCE
- `keycloak/setup-realm.sh` - Keycloak client PKCE configuration

## References

- [RFC 7636: Proof Key for Code Exchange](https://tools.ietf.org/html/rfc7636)
- [OAuth 2.0 Security Best Current Practice](https://tools.ietf.org/html/draft-ietf-oauth-security-topics)
- [OAuth 2.1 Draft](https://tools.ietf.org/html/draft-ietf-oauth-v2-1)
