# ADR-0002: IAM Foundation — Keycloak (AuthN) + Casbin (AuthZ)

Status
- Proposed

Context
- We need a portable, self-hostable IAM foundation to gate all API work. Requirements include: multi-tenant readiness, standards-based SSO (OIDC/OAuth2), service accounts, fine-grained authorization, auditable decisions, and minimal operational overhead.
- Per ARCH-04 — IAM and Prompt Management, we prefer full control and fewer moving parts vs. managed services.

Decision
- Identity Provider (AuthN): Keycloak (self-host). Use OIDC/OAuth2 with discovery (/.well-known/openid-configuration) and JWKS for token verification.
- Authorization (AuthZ): Casbin (embedded library) for application-level policy enforcement. Policies versioned alongside code; simple to operate without an external PDP.

Rationale
- Control: Self-hosted Keycloak and embedded Casbin give us full control over identity, federation, and policies without external dependencies.
- Standards: OIDC/OAuth2 provide broad compatibility and portability; Casbin supports RBAC/ABAC models and multiple policy backends.
- Simplicity: Avoids introducing and operating an additional PDP service (e.g., Cerbos/OPA) at Phase 1, reducing latency and ops complexity.

Consequences
- Operational ownership of Keycloak (backup, upgrades, HA). We will provide Terraform/scripts in a future phase; Phase 1 may run a single-node dev/test cluster.
- Policy lifecycle: Policies live with the app; we must enforce rigorous review/testing (contract tests) and audit logs for decisions.
- Future evolution: If cross-service policy centralization becomes necessary, we can introduce a PDP later and adapt the authorization port.

Implementation Guidance
- Token verification via OIDC discovery and JWKS; verify signature, exp, nbf, aud, iss; require tenant context (org/realm) and subject claims.
- Route guards call an authorization service which delegates to Casbin enforce(subject, resource, action, context). Policies stored in repo; environment selects policy set.
- Audit every allow/deny decision with correlation ID; emit structured logs and traces.
- Contracts: Define JSON Schemas for token claims and PDP request/response. Validate in CI and in non-prod at runtime.

Portability
- No vendor-specific IdP APIs in application code. Interact via standard OIDC flows and JWKS.
- Authorization port isolates Casbin behind an interface so we can swap to PDP if needed.

Decision Drivers
- Full control, low latency, minimal moving parts; compliance readiness and auditability.

Alternatives Considered
- ZITADEL + Cerbos: managed/self-managed IdP with external PDP; higher ops cost, strong decoupling.
- Keycloak + Cerbos/OPA: more components to run; better centralization at scale, not needed in Phase 1.

References
- Tracker: ARCH-04 — IAM and Prompt Management (Issue #4)
- Canonical rules: AI-agent conventions, documentation best practices, branching policy

Acceptance Criteria (for this ADR to be "Approved")
- Linked design spec (iam-foundation-spec.md)
- Contracts present for token claims and authz requests
- DoR gates documented for all API PRs
