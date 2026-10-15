---
title: [Users/User Profiles ADR] - [Use JWT for Session and Access Management]
status: Proposed
date: 05-25-2025
decision-makers: [Myat Thiha, Noeh Parrales, Vincent Nguyen]
---

## Summary

**One-sentence overview of the decision.**
We initially proposed using JWT for session and access management to support private/public memory cards and user accounts, but ultimately decided to **remove user authentication altogether** due to limited necessity and project scope.

---

## Context and Problem Statement

Originally, we identified a need for secure user authentication to allow people to manage personal memory cards, toggle visibility between public/private, and publish selected cards to a shared map. This required users to log in, store session tokens, and only view or edit their own cards.

As we began implementing this feature, we encountered challenges in backend complexity due to IndexDB operating on the client side. We found it doesn't make sense to store user data in IndexDB as it's intended for local storage, and not suitable for managing authenticated user data across multiple devices.

## Considered Options

- JWT(JSON Web Token)
- OAuth
- SAML SSO
- No user authentication (final decision)

## Decision Outcome

Chosen option: **No user authentication**, all memory card content is managed anonymously or client-side without user accounts.

### Consequences

- Good, because the app is significantly simpler to implement and maintain
- Good, no risk of token leakage, password security, or session vulnerabilities
- Good, removes the need for backend auth endpoints and client-side token logic
- Bad, users cannot privately save or manage personal cards across sessions
- Bad, no publishing control tied to identity (e.g., card ownership)
- Bad, future feature additions like commenting or profile pages will require redesign
- Bad, users can't showcase photocards to other users and explore other users' memory cards

### Confirmation

- Removed all authentication logic (login page, JWT handlers, secure endpoints)
- Simplified backend routes and frontend UX to remove user identity references
- Verified that public/private card toggles are no longer applicable
- Ensured card creation/editing works without user sessions

## Pros and Cons of the Options

### No Authentication

- Good, drastically reduces development and testing overhead
- Good, avoids external dependencies and token management
- Good, removes friction for new users — instant access
- Bad, no user persistence (cards are either saved locally or public)
- Bad, no account-based features like drafts, publishing, favorites, etc.

### JWT

Homepage: <https://www.npmjs.com/package/jsonwebtoken>

- Good, Auth logic and visibility enforcement live fully in your code
- Good, we can include custom fields (e.g., userId, role, visibilityPref) in the token payload
- Good, fewer dependencies and faster development time compared to OAuth or SAML
- Bad, we must handle token expiration, refresh tokens, and secure storage (e.g., localStorage vs. httpOnly cookies).
- Bad, users must create new credentials (no "Login with Google”)
- Bad, improper signing, verification, or storage of tokens can lead to security vulnerabilities (e.g., token leakage, forgery).

### OAuth

Homepage: <https://oauth.net/>

- Good, quick and easy for login users
- Log in with existing accounts (Google, Github, etc.)
- Good, has built in security features that handles token refresh and password recover
- Good, trustworthy and less account management for us
- Bad, relies on third party API’s
- Bad, more complex setting it up, configuring OAuth flows
- Bad, for the time limit set on use, can be overly complicated to implement

### SAML

Homepage: <https://docs.oasis-open.org/security/saml/Post2.0/sstc-saml-tech-overview-2.0.html/>

- Good, widely used in enterprise SSO environments
- Good, it supports strong identity federation and works will with IdPs
- Bad, SML-based format and harer to read/debug
- Bad, tests is complex and requires external tools
- Bad, unit tests are hard to construuct
- Bad, the re-direct login flow complicates integration and setup

## More Information

We attempted to integrate the login page and IndexedDB user logic, but we reassessed the need for authentication entirely. The decision was finalized after determining that anonymous users could still create, view, and share cards without requiring personal logins or accounts.

Comparison between JWT and OAuth:
<https://frontegg.com/blog/oauth-vs-jwt>.
