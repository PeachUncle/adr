# ADR 001: Use of JWT (JSON Web Tokens) for Authentication

## Status
Accepted

## Context
The Ticketeer project consists of an API that will serve multiple clients (Web Front-end, Mobile, partners).
We need an authentication mechanism that is:
1.  **Secure**: Protects user credentials.
2.  **Stateless**: Allows horizontal scaling of the API without depending on server affinity (sticky sessions).
3.  **Client Agnostic**: Works well for both browsers (Web) and native applications (Mobile) or server-to-server calls.

## Alternatives Considered and Rejected

### 1. Session Cookies
*   **Description**: The server creates a session on the backend and sends an ID via HttpOnly Cookie.
*   **Reason for Rejection**: Although it is the gold standard for security in Monolithic Web applications (MVC/Razor), Cookies present significant challenges in **decoupled Front-end** scenarios (CORS issues, SameSite policies) and are natively difficult to manage in **mobile apps** or server-to-server integrations.

### 2. Basic Authentication
*   **Description**: The client sends `Authorization: Basic base64(user:pass)` in every request.
*   **Reason for Rejection**:
    *   **Security**: Requires sending the user's real password in *every* request, drastically increasing the attack surface.
    *   **Performance**: The server needs to validate the password (hash and compare) in the database for every request. Secure hash algorithms (like BCrypt or Argon2) are intentionally slow, which would destroy API performance under load.
    *   **Functionality**: Does not have a native concept of expiration or refresh.

### 3. OAuth 2.0 / OpenID Connect (IdentityServer/Duende)
*   **Description**: A centralized and dedicated identity server issues tokens.
*   **Reason for Rejection**: Adds disproportionate **accidental complexity** for the initial stage of the project. Configuring and maintaining a separate Identity Provider (IdP) requires extra infrastructure.
*   **Note**: The current choice for JWT leaves us prepared to migrate to OAuth in the future with ease, as the transport mechanism (Bearer Token) is identical.

## Decision
We decided to use **JWT (JSON Web Tokens)** in conjunction with **ASP.NET Core Identity**.

The flow will be:
1.  The client sends credentials (Login/Password) to an endpoint `/auth/login`.
2.  The API validates and returns an **Access Token** (JWT) with a short lifespan.
3.  The client stores the token and sends it in the `Authorization: Bearer <token>` header in subsequent requests.

## Consequences

### Positive
*   **Decoupling**: The API does not need to maintain session state (memory/database) to know if the user is logged in.
*   **Flexibility**: The same endpoint works for React, iOS, Android, and Postman.
*   **Performance**: Token validation is fast (cryptographic signature) and does not require a database trip for every request.
*   **Roadmap**: Aligned with the "Must Know" requirements of the project.

### Negative
*   **Revocation**: Invalidating a JWT before expiration is complex (requires blocklist/blacklist). We will mitigate this by using tokens with short validity.
*   **Client Storage**: Requires care on the front-end to store the token securely (avoid LocalStorage if possible, prefer memory or HttpOnly Cookies for the token, if the client is a browser).
