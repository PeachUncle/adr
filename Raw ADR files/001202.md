# ADR-010: Auth Provider Selection (GitHub-First Strategy)

**Status**: Accepted  
**Date**: 2025-12-27  
**Updated**: 2025-12-27 (GitHub ecosystem optimization)  
**Deciders**: James (Owner)  
**Technical Story**: P0-005 JWT Authentication Implementation

## Context and Problem Statement

TaskMan-v2 requires authentication for production deployment. Given that James has **GitHub Pro subscription** and the target users are **developers**, we should maximize GitHub ecosystem value.

Requirements:
- JWT-based authentication for FastAPI backend
- React 19 SPA integration
- RBAC (Role-Based Access Control) with 4 roles: admin, developer, viewer, guest
- Audit logging (required by ContextForge Codex)
- Docker/Kubernetes deployment compatibility

## Decision Drivers

* **GitHub Pro Already Paid** - Maximize existing investment
* **Developer Tool** - All users will have GitHub accounts
* **Cost Optimization** - Save $240-480/month vs Auth0
* **Time to MVP** - Comparable to Auth0 (~12-16 hours)
* **Vendor Alignment** - GitHub is already core to workflow

## Considered Options

1. **GitHub OAuth** - Use GitHub as identity provider ($0)
2. **Auth0** - Managed identity platform ($240-480/month)
3. **Keycloak** - Self-hosted open-source IAM ($0, ops overhead)
4. **Custom JWT** - Build from scratch (risk)

## Decision Outcome

**Chosen option: GitHub OAuth**, because:
- All TaskMan-v2 users are developers with GitHub accounts
- $0 monthly cost vs $240-480/month for Auth0
- 12-16 hour implementation (comparable to Auth0)
- Native integration with existing GitHub ecosystem
- Simple RBAC via database UserRole enum

### Positive Consequences

* **$0/month** vs $240-480/month (saves $2,880-5,760/year)
* Native GitHub integration (users already logged into GitHub)
* Leverages existing GitHub Pro subscription
* Simple implementation with `authlib` (FastAPI) + `@octokit/auth-oauth-app` (React)
* User profile, avatar, email from GitHub API

### Negative Consequences

* Must implement RBAC manually (simple UserRole table)
* Must implement audit logging in database (vs Auth0 built-in)
* Users must have GitHub accounts (acceptable for dev tool)
* Token refresh flow required for long sessions

## Implementation

### FastAPI Backend (authlib)

```python
# backend-api/auth/github_oauth.py
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

config = Config('.env')
oauth = OAuth(config)

oauth.register(
    name='github',
    client_id=config('GITHUB_CLIENT_ID'),
    client_secret=config('GITHUB_CLIENT_SECRET'),
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'read:user user:email'},
)

# Routes
@router.get('/auth/github')
async def github_login(request: Request):
    redirect_uri = request.url_for('github_callback')
    return await oauth.github.authorize_redirect(request, redirect_uri)

@router.get('/auth/github/callback')
async def github_callback(request: Request):
    token = await oauth.github.authorize_access_token(request)
    user_info = await oauth.github.get('user', token=token)
    # Create/update user in database with role
    return create_session_token(user_info.json())
```

### React Frontend

```typescript
// src/auth/github-auth.ts
const GITHUB_CLIENT_ID = import.meta.env.VITE_GITHUB_CLIENT_ID;

export function initiateGitHubLogin() {
  const params = new URLSearchParams({
    client_id: GITHUB_CLIENT_ID,
    redirect_uri: `${window.location.origin}/auth/callback`,
    scope: 'read:user user:email',
    state: crypto.randomUUID(),
  });
  window.location.href = `https://github.com/login/oauth/authorize?${params}`;
}
```

### RBAC Schema

```sql
-- Simple role-based access control
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    github_id BIGINT UNIQUE NOT NULL,
    github_login VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    avatar_url VARCHAR(512),
    role VARCHAR(50) DEFAULT 'viewer',  -- admin, developer, viewer, guest
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(255) NOT NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(100),
    details JSONB,
    ip_address INET,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Comparison Matrix

| Dimension | GitHub OAuth | Auth0 | Keycloak |
|-----------|-------------|-------|----------|
| Monthly Cost | **$0** | $240-480 | $0 (ops cost) |
| Implementation | 12-16h | 18h | 30h |
| RBAC | DIY (simple) | Built-in | Built-in |
| Audit Logging | DIY | Enterprise | Built-in |
| MFA | GitHub's | Built-in | Built-in |
| Ops Overhead | None | None | 2-4h/month |
| User Requirement | GitHub account | Any email | Any email |
| **Score for Dev Tool** | **⭐⭐⭐⭐⭐** | ⭐⭐⭐⭐ | ⭐⭐⭐ |

## GitHub OAuth App Setup

1. Go to https://github.com/settings/developers
2. Click "New OAuth App"
3. Fill in:
   - Application name: `TaskMan-v2`
   - Homepage URL: `https://taskman.app` (or your domain)
   - Authorization callback URL: `https://api.taskman.app/auth/github/callback`
4. Save Client ID and generate Client Secret
5. Add to environment variables

## Migration Path

If requirements change (non-developer users needed):
- GitHub OAuth → Auth0: ~8 hours (add OAuth provider, migrate user table)
- GitHub OAuth → Keycloak: ~12 hours (self-host, migrate users)

## Links

* [GitHub OAuth Documentation](https://docs.github.com/en/apps/oauth-apps)
* [Authlib OAuth Client](https://docs.authlib.org/en/latest/client/starlette.html)
* [GitHub OAuth Scopes](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps)
