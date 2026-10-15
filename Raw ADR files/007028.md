# ADR 013: Choosing an authentication provider

- Date created: 13/02/2025
- Driver: Alex Foxleigh (Foxy)

## Status

![accepted]

## Context

We need a way to authenticate users with our application. We want the following functionality:

- Users can sign up
- Users can subscribe to a paid tier
- Most (if not all) PII is stored externally so we don’t have to concern ourselves with GDPR
- Data is linked to user records in the database via the auth ID
- Users can add profile information like avatars, names, email addresses, actual addresses, phone numbers, etc., directly with the auth provider
- Users can use social sign-in options

The initial plan was to use AWS Cognito, but it was determined to be overkill for our needs and clunky to integrate with `next-auth` during the UI build.

## Alternatives Considered

### AWS Cognito

✅ Fully managed by AWS
✅ Good security features
❌ Complicated setup & poor developer experience
❌ Limited NextAuth.js support
❌ Poor refresh token support in SPAs
❌ Requires manual Stripe billing integration

### Firebase Auth

✅ Well-integrated with Google services
✅ Simple setup & solid NextAuth.js support
❌ Not GDPR-friendly (user data stored within Google ecosystem)
❌ Limited enterprise scalability
❌ Requires manual Stripe billing integration

### Auth0

✅ Excellent NextAuth.js support
✅ Supports multiple identity providers
✅ Enterprise-ready with fine-grained access control
❌ Free tier has strict limits & pricing gets expensive
❌ Requires manual Stripe billing integration

### Clerk (Chosen)

✅ Built for Next.js with first-class NextAuth.js support
✅ Handles social logins, email/password, and WebAuthn easily
✅ Stores PII externally for better GDPR compliance
✅ Natively integrates with Stripe for subscription management
✅ Developer-friendly with an excellent API and UI components
✅ Great free tier with generous limits

## Decision

We have decided to use Clerk as our authentication provider.

### Rationale

- Clerk provides the best NextAuth.js integration, making it easy to integrate with our frontend.
- It handles PII storage, so we don’t have to worry about GDPR compliance.
- It offers built-in Stripe integration, simplifying subscription management.
- It supports multiple authentication methods, including social logins and WebAuthn.
- The developer experience is far superior compared to Cognito.

## Consequences

- Simplified authentication setup with Clerk’s managed services.
- No need to store or manage user PII in our database.
- Easier subscription management with Clerk’s Stripe integration.
- Faster and smoother onboarding for users with social logins.
- Some minor vendor lock-in with Clerk, but alternatives exist if needed.
- Limited customization compared to a self-hosted auth solution, but this is acceptable for our use case.

[proposed]: https://img.shields.io/badge/Proposed-yellow?style=for-the-badge
[accepted]: https://img.shields.io/badge/Accepted-green?style=for-the-badge
[superceded]: https://img.shields.io/badge/Superceded-orange?style=for-the-badge
[rejected]: https://img.shields.io/badge/Rejected-red?style=for-the-badge
[deprecated]: https://img.shields.io/badge/Deprecated-grey?style=for-the-badge
