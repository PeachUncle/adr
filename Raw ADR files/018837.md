# ADR: Introducing OAuth Application Types and Reorganizing LoginSpaApplication Responsibilities

- **Date**: 2025-12-25
- **Status**: Decided
- **Deciders**: Akira Suenami

## Context

### Current Problems

1. **All OAuth clients redirect to the same login URL**
   - `resource_owner_authenticator` in `doorkeeper.rb` references `Tenant.current.login_spa_application.login_url`
   - Traditional Web applications (Rails, Express, etc.) are also redirected to the SPA login screen

2. **LoginSpaApplication has unclear responsibilities**
   - Login settings for external OAuth clients (`login_url`, etc.)
   - Enabling/disabling My Page functionality (`enable_web_login`, etc.)
   - These two concerns are mixed together

3. **No application type concept like Auth0**
   - Cannot distinguish between SPA, Native, Traditional Web, and M2M

### OAuth Scope

```
OAuth Flow (auth-platform's responsibility)
┌──────────────────────────────────────────────────────────┐
│ Authorization Request → Login → Authorization → Token   │
└──────────────────────────────────────────────────────────┘
                         ↓
                   Access Token
                         ↓
┌──────────────────────────────────────────────────────────┐
│ API (Profile, Payment Info, etc.)                        │  ← Outside OAuth scope
│ Protected by token, but spec is up to each service       │    (Regular REST API)
└──────────────────────────────────────────────────────────┘
```

Without creating an OAuth Application, tokens cannot be obtained and APIs cannot be called. Therefore, `enable_api_*` flags are unnecessary.

### auth-platform Function Separation

```
auth-platform
├── IdP Functions (OAuth/OIDC)     ← Required
│   └── /oauth/authorize, /oauth/token, etc.
│
├── API (Profile, etc.)            ← Required (Protected by OAuth)
│   └── /api/v1/users/me, etc.
│
└── My Page Web UI                 ← Optional (enable_my_page)
    └── /my, /my/profile, etc.
    └── Session-based web app, independent of OAuth
```

My Page does not need to be treated as an OAuth client. It is a web application that operates with auth-platform's own session and is different from external clients.

## Decision

### 1. Add `application_type` to OAuth Application

Following Auth0, introduce application types.

**Types implemented this time**:

| Type | Description | Login Screen |
|------|-------------|--------------|
| `spa` | React, Vue, etc. (default) | External `login_url` |
| `traditional_web` | Rails, Express, etc. | Internal `/user_area/logins` |

**Types planned for future** (concept only, not implemented short-term):

| Type | Description | Login Screen |
|------|-------------|--------------|
| `native` | iOS, Android, Electron, etc. | External `login_url` (with PKCE requirement, etc.) |
| `m2m` | Backend services | None (Client Credentials Grant only) |

### 2. Limit LoginSpaApplication's Role to "My Page Settings"

Reorganize LoginSpaApplication's responsibilities as follows:

**Settings migrated to OauthApplication**:
- `login_url` → Owned by each OauthApplication
- `sign_up_url` → Owned by each OauthApplication

**Settings remaining in LoginSpaApplication (for My Page)**:
- `enable_web_login` → Enable/disable web login for My Page (`/my`)
- `enable_web_sign_up` → Enable/disable web signup for My Page
- `redirect_url_on_password_reset` → Redirect destination after password reset

**Settings removed**:
- `enable_api_login` → Unnecessary (cannot call API without OAuth Application)
- `enable_api_sign_up` → Unnecessary (same as above)

### 3. Future Simplification

Consider simplifying LoginSpaApplication:
- Simplify to just `enable_my_page: boolean`
- Or integrate into `TenantSetting`

## Rationale

### Why application_type belongs in OauthApplication

- OAuth flow is determined by `client_id`
- It's natural for different clients to have different login methods
- Same conceptual model as existing IdPs like Auth0

### Why remove enable_api_*

- Cannot obtain tokens without creating an OAuth Application
- Cannot access protected APIs without tokens
- Therefore, API access ON/OFF is controlled by the existence of OAuth Application

### Why not treat My Page as an OAuth client

- My Page is auth-platform's own feature
- No need to go through OAuth flow (session-based is sufficient)
- Simplifies the design

## Impact

### Components Requiring Changes

| Component | Changes |
|-----------|---------|
| `oauth_applications` schema | Add `application_type`, `login_url`, `sign_up_url` |
| `login_spa_applications` schema | Remove `enable_api_*` |
| `OauthApplication` model | Add `application_type` enum |
| `doorkeeper.rb` | Branching based on `application_type` |
| Admin UI | Add OauthApplication settings |

### Backward Compatibility

- Existing OauthApplications default to `application_type: 'spa'`
- Falls back to LoginSpaApplication settings if `login_url` is not set
- Gradual migration is possible

## Implementation Phases

### Phase 1: Minimal Changes (Current Scope)

1. Add `application_type`, `login_url`, `sign_up_url` to `oauth_applications` schema
   - `application_type` is only `spa` (default) and `traditional_web`
   - `native`, `m2m` are included in enum definition for future extension but not implemented now
2. Remove `enable_api_*` from `login_spa_applications` schema
3. Implement branching based on `application_type` in `doorkeeper.rb`
   - `spa`: Redirect to external `login_url` (existing behavior)
   - `traditional_web`: Redirect to internal `/user_area/logins`
4. Add OauthApplication settings in admin UI

### Phase 2: Reorganize LoginSpaApplication (Future)

- Rename LoginSpaApplication to `MyPageSetting`
- Simplify `enable_web_login`, `enable_web_sign_up` → `enable_my_page`
- Remove `login_url`, `sign_up_url` after migration to OauthApplication is complete

### Phase 3: Reorganize My Page Functionality (Future)

- `/my`, `/user_area/*` accessible only when `enable_my_page = true`
- Show 404 or disabled message when `enable_my_page = false`

## Final Structure

```
Tenant
├── OauthApplication (multiple)        ← For external clients
│   ├── application_type: spa | traditional_web (future: native | m2m)
│   ├── login_url, sign_up_url (for SPA, not needed for traditional_web)
│   └── Other OAuth settings
│
└── MyPageSetting (one)                ← My Page feature settings (future)
    └── enable_my_page                 ← Enable/disable My Page functionality
```

## References

- [Auth0 Application Types](https://auth0.com/docs/get-started/applications)
- `config/initializers/doorkeeper.rb`
- `app/models/oauth_application.rb`
- `app/models/login_spa_application.rb`
