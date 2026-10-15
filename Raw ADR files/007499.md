# ADR-010 – GDPR-Compliant Session Management: Server-Side Session Storage

**Status:** Accepted  
**Date:** 2025-11-21  
**Author:** Niklas Häll

---

## Context

The application requires session management to maintain user authentication state and role information across requests. Initially, the system used cookie-based authentication with persistent cookies, which raised GDPR compliance concerns for European deployments. Under GDPR, storing personal data in client-side cookies requires explicit consent and proper data handling procedures. The application needs a solution that maintains user session state securely while complying with GDPR requirements.

---

## Decision

We implement **ASP.NET Core Session** with server-side storage for session management, using cookies only to store a session ID (no personal data). Additionally, we implement **ITicketStore** for cookie authentication to store authentication tickets server-side, with cookies containing only session keys (GUIDs) instead of entire encrypted tickets. This approach ensures GDPR compliance by keeping all personal data server-side while maintaining seamless authentication functionality. Sessions expire after 30 minutes of inactivity with sliding expiration enabled. The implementation uses in-memory storage with a clear migration path to Azure Cache for Redis for production scalability.

**Implementation Details:**
- ASP.NET Core Session middleware for general session data
- `ITicketStore` implementation (`TicketStore`) for authentication tickets
- Both use `IDistributedCache` (in-memory, ready for Redis migration)
- Cookies contain only identifiers (session IDs and ticket keys), no personal data

---

## Consequences

**Advantages:**
- GDPR compliant – no personal data stored in cookies, only session IDs and ticket keys. Personal data remains on the server, making it easier to comply with data subject rights (access, deletion, portability).
- Security – HttpOnly cookies prevent JavaScript access, reducing XSS attack surface. Server-side storage provides better control over session data. `ITicketStore` enables immediate logout invalidation – stolen cookies become useless immediately upon sign-out, addressing a security gap in default cookie authentication.
- Reduced cookie size – Authentication tickets stored server-side means cookies contain only session keys (GUIDs), not entire encrypted tickets. This reduces cookie size significantly, improving performance and avoiding cookie chunking issues.
- Automatic expiration – 30-minute timeout with sliding expiration balances security and user experience.
- Easy data management – Server-side storage enables immediate session and ticket deletion, essential for GDPR "right to be forgotten" requests.
- Scalability path – In-memory storage can be migrated to Azure Cache for Redis for production scalability and persistence across app restarts.

**Disadvantages:**
- Server memory usage – In-memory session storage consumes server memory. For high-traffic scenarios, Redis is recommended.
- Session loss on restart – In-memory sessions are lost when the application restarts (mitigated by Redis migration path).
- Stateful architecture – Requires session affinity in load-balanced scenarios (resolved with Redis distributed cache).

---

## Risks / Mitigations

- **Risk:** In-memory session storage may not scale for high-traffic scenarios, and sessions are lost on application restart.  
  **Mitigation:** Implementation uses `AddDistributedMemoryCache()` which provides a clear migration path to Azure Cache for Redis. Redis can be added without code changes by switching the session store provider.

- **Risk:** Session data could be exposed if server is compromised.  
  **Mitigation:** Session data is stored in memory with automatic expiration. For production, migrate to Azure Cache for Redis with encryption at rest. Implement proper access controls and monitoring.

- **Risk:** GDPR compliance may require additional measures beyond session storage (privacy policy, data processing agreements).  
  **Mitigation:** This decision addresses the technical implementation. Legal compliance (privacy policies, consent mechanisms) should be handled separately with legal counsel.

---

## Alternatives

- **Traditional Cookie-Based Storage (Personal Data in Cookies)** – Rejected. Stores personal data directly in cookies, requiring explicit GDPR consent and complex data handling procedures. Not compliant with GDPR "data minimization" principle.

- **JWT Tokens in Cookies** – Rejected. While JWTs can be stateless, storing user claims in tokens means personal data is stored client-side. Still requires GDPR compliance measures. Additionally, JWTs cannot be easily revoked without a token blacklist.

- **Token-Based Authentication with Database Lookup** – Rejected. Requires database queries on every request, adding latency and database load. More complex than session-based approach for this use case.

- **LocalStorage/SessionStorage** – Rejected. Client-side storage of personal data is explicitly not GDPR-compliant. Additionally, these storage mechanisms are vulnerable to XSS attacks.

---

## References

- [GDPR - Right to be Forgotten (Article 17)](https://gdpr-info.eu/art-17-gdpr/)
- [GDPR - Data Minimization (Article 5)](https://gdpr-info.eu/art-5-gdpr/)
- [Microsoft Docs - ASP.NET Core Session](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/app-state)
- [Microsoft Docs - Cookie Authentication](https://learn.microsoft.com/en-us/aspnet/core/security/authentication/cookie)
- [Improving ASP.NET Core Security By Putting Your Cookies On A Diet](https://nestenius.se/net/improving-asp-net-core-security-by-putting-your-cookies-on-a-diet/) – Blog post by Tore Nestenius explaining ITicketStore implementation and security benefits
- [Week 4 Journal - GDPR-Compliant Session Management](../journal/week_four.md)

