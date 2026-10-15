# ADR-5 Local accounts

## Context

The application requires user accounts, because users are each
managing their own data. The project constraints emphasize simplicity,
low operational cost, EU data residency, GDPR compliance, and a small
development team. The MVP spec allows either local,
application-specific accounts or integration with external identity
providers (e.g., Google, Microsoft). The choice should favor the
smaller undertaking that meets security and privacy requirements.

## Decision

Use local, application-managed user accounts for the MVP. Implement
email-based sign-up, email verification, password authentication, and
a password-reset flow.

## Expected Consequences

Simplicity and predictability: Building local accounts keeps
dependencies and operational complexity low and reduces surface area
for operational issues.

Data residency and GDPR: Storing authentication data locally makes it
straightforward to keep all user data in the EU and to implement
user-data deletion and export features required by GDPR.

Security responsibilities: The team must implement and operate secure
authentication features (strong password hashing, token handling,
email delivery, rate limiting, protection against enumeration).

Operational cost: No reliance on external identity providers reduces
the chance of unexpected costs or vendor lock-in. Email delivery may
require an SMTP or transactional email service, but with the low
expected volume of messages, the cost is expected to be reasonable.

Usability trade-offs: Some users prefer single-sign-on via existing
accounts. Local accounts entail users managing another password, which
may slightly raise friction.

## Candidate comparison

1. Local, application-managed accounts (chosen)
   - Pros:
     - Lowest initial implementation complexity and predictable
       behaviour.
     - Full control over data location (EU), making GDPR compliance
       and user-data deletion straightforward.
     - No vendor lock-in or unexpected provider costs.
     - Easier to run entirely locally during development.
   - Cons:
     - Team is responsible for implementing secure authentication
       (password hashing, token lifecycle, email workflows).
     - Slightly higher friction for users who prefer SSO.

2. External identity providers (OAuth / OpenID Connect)
   - Pros:
     - Users can sign in with existing accounts (better UX).
     - Offloads authentication security and password management to
       providers.
   - Cons:
     - Adds integration complexity (provider-specific quirks, callback
       URLs, token handling).
     - Potential data-residency and GDPR complications (user data
       stored/processed by third parties).
     - May introduce vendor lock-in or costs depending on provider
       policies.
     - Harder to run fully offline or locally for development without
       test accounts.

3. Hybrid: local accounts + optional third-party sign-in
   - Pros:
     - Best UX and flexibility for users; can migrate incrementally.
     - Allows users to choose preferred method.
   - Cons:
     - More implementation work than local-only for the MVP.
     - Requires careful account-linking UX and security considerations.

## Implementation notes (MVP scope)
- Passwords must be stored using a strong, adaptive hash (bcrypt or
  argon2) via a well-maintained library.
- Use email verification tokens for sign-up and single-use tokens for
  password resets; tokens should be time-limited and securely random.
- Add rate limiting and account lockout heuristics to mitigate
  brute-force attacks and enumerate-resistance (don't disclose whether
  an email is registered).
- Ensure all auth-related emails and any third-party services used for
  email comply with GDPR and, where feasible, host/configure to
  respect EU data residency.
- Design the user account schema with stable internal IDs. This will
  help linking provider identities later without migrating primary
  account data.

This approach satisfies the MVP goals of simplicity, low cost,
GDPR-aligned data residency, and local testability.
