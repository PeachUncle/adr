# ADR-001: Adopt Auth0 now with an exit path to self-hosted IdP (authentik/Keycloak)
Status: Accepted  
Date: 2025-08-13  
Authors: @kylenunn

## Context
We need auth for a C#/.NET app.  
Self-hosting (Authelia/authentik) adds infra/ops complexity. Auth0 is fast to ship but raise cost/lock-in concerns.  
We want speed now, with a clear migration path later (Auth0 migration docs located below in references).

## Decision
Use **Auth0** as the initial Identity Provider (OIDC) for all environments. Going to setup Email verification for now and then setup MFA as needed later. This will help prevent the use of throwaway emails being used to access our app.

Keep **authorization and app user data in our own DB** (keyed by `(issuer, sub)`), and design all auth integrations to be **IdP-agnostic** so we can later migrate to **authentik or Keycloak** or another auth provider without major code changes.

## Rationale
- **Time-to-value:** Ship sooner with hosted flows, MFA, social, and good docs.
- **Free-tier:** The service is basically free up until a certain point so why not take advantage

## Consequences
- **Positive**
  - Fast implementation; reduced security/ops surface.
  - Enterprise features available if needed (paid), while free tier covers early stages.
  - Clear migration playbook due to standards use.
- **Negative**
  - Ongoing SaaS dependency and potential per-MAU cost growth.
  - Some features (orgs/enterprise SSO/SAML) may be paywalled.
- **Neutral/Unknown**
  - Actual MAU growth and cost trajectory are uncertain.

## What to do now (to enable future migration)
- **Standards-only integration**
  - Use **OIDC Authorization Code + PKCE**; scopes: `openid email profile` (+ minimal custom claims).
  - Validate JWTs via **JWKS** with caching & rotation; handle clock skew and expiry.
- **Own authorization**
  - Store users by `(issuer, sub)` in our DB; keep **roles/permissions/orgs** locally.
  - Map any IdP groups → internal roles in our API layer (not in front-end).
- **Abstraction**
  - Wrap token validation and userinfo in a small **AuthService** interface so swapping issuers is config.
- **Session model**
  - Prefer **httpOnly cookies** (BFF pattern) over `localStorage` for tokens.
- **Avoid lock-in**
  - Minimize vendor-specific Rules/Actions; if used, encapsulate and document.
  - Keep IdP config (clients, connections) in **IaC** where possible.
- **Data portability**
  - Schedule **periodic user exports** to cold storage.
  - Record **external_idp_issuer** and **subject** on each user for easy remapping.
- **Readiness checks**
  - Add a **Keycloak/authentik dev container** in CI for smoke tests against a second issuer.
- **Migration triggers & playbook**
  - Triggers: cost thresholds, SAML/enterprise SSO requirement, data residency/compliance.
  - Playbook: stand up authentik/Keycloak in parallel → configure OIDC client → enable **progressive migration** (re-auth to rehash) or do **forced password reset** → switch issuer URLs → monitor.

## Alternatives Considered
- **Authelia (self-hosted OIDC, lightweight):** Lower footprint but still ops to run; no SAML. Chosen later only if needs remain simple and we want self-hosting.
- **authentik (self-hosted IdP):** Rich features incl. SAML; heavier ops now. Good target for migration.
- **Keycloak (self-hosted IdP):** Very feature-complete (OIDC/SAML/SCIM); heaviest ops; good long-term option.
- **Clerk (SaaS):** Similar benefits to Auth0; we prefer Auth0 ecosystem/docs for .NET fit.
- **BetterAuth (library, Node-centric):** Great DX for Node stacks; misaligned with our .NET backend.
- **DIY (.NET Identity + OpenIddict):** Maximum control, zero per-MAU cost, but higher security/maintenance burden now.

## References
- Video context that influenced consideration of BetterAuth (YouTube): https://www.youtube.com/watch?v=lxslnp-ZEMw  
- .NET Web API Configuration: https://learn.microsoft.com/en-us/aspnet/core/security/authentication/configure-jwt-bearer-authentication?view=aspnetcore-9.0

- ASP.NET Core Code Sample: Web API Authorization: https://developer.auth0.com/resources/code-samples/api/aspnet-core/basic-authorization

- Vue.js Authentication By Example: Composition API: https://developer.auth0.com/resources/guides/spa/vue/basic-authentication?_gl=1*19hulz3*_gcl_au*MTM5NzY3NDgxMS4xNzU1MTE3NTg3*_ga*MjE0Mjk3NDEyNy4xNzU1MTE3NTg3*_ga_QKMSDV5369*czE3NTU0NDc5NDUkbzQkZzEkdDE3NTU0NDgwNzIkajU4JGwwJGgw

- First Party and Third Party Application: https://auth0.com/docs/get-started/applications/confidential-and-public-applications/first-party-and-third-party-applications#third-party-applications

- Migrating off Auth0: https://community.auth0.com/t/migrating-off-auth0/96457 , https://auth0.com/docs/manage-users/user-migration

- Verifying Emails Using Auth0: https://auth0.com/docs/manage-users/user-accounts/verify-emails


