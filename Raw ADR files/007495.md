# ADR-004 – Frontend technology choice: .NET 8 Blazor Server

**Status:** Accepted  
**Date:** 2025-10-30  
**Author:** Niklas Häll

---

## Context
The project should mimic an existing solution where the Microsoft/Azure stack is used to its full extent.  
The frontend needs to:
- be able to integrate with .NET-based APIs without extra layers,
- support login for both internal roles (admin/inspector via Entra ID) and regular users,
- be able to run locally to keep costs down during development,
- be able to deploy easily to Azure App Service.

Alternatives like React, Angular, and Vue would work technically, but would require a separate build chain (npm) and add unnecessary complexity for an 8-week MVP.  
HTMX, however, could have been an attractive alternative thanks to its philosophy around **Hypermedia-Driven Applications (HDA)**, where interaction is controlled by the server and not by a heavy frontend.  
It would have fit well for a ticketing system where the logic already exists in the backend, and where low complexity, rapid development, and clear server-state are important goals.  
HTMX provides a modern, responsive interface without building an SPA, but lacks the deep integration that Blazor offers in a pure .NET environment.

---

## Decision
We use **.NET 8 Blazor Server** as the frontend framework for the application.  
It provides an all-C# solution where UI, business logic, and authentication can be close together and where real-time updates (SignalR) are handled by the platform.  
Blazor Server can also run locally during development to reduce the use of CI/CD minutes and Azure resources.

---

## Consequences
**Advantages:**
- Same technology stack (.NET) throughout the project → easier onboarding and fewer tools.
- Easy integration with ASP.NET Identity and Entra ID.
- Server-driven UI → easier to protect admin views behind login.
- Suitable for rapid MVP development (no separate SPA build chain).
- Easy to host in Azure App Service.

**Disadvantages:**
- Requires a working and relatively stable server connection (SignalR).
- Can become more expensive in the long run than static Blazor WASM if you have many concurrent users.
- UI performance is more affected by the server than in a pure client app.

---

## Risks / Mitigations
- **Risk:** App Service on Free/F1 can "sleep", which affects the SignalR connection.  
  **Mitigation:** Scale up to B1 before demo or when the system is shown to external parties.

- **Risk:** Too heavy logic in Blazor components can make the UI slow.  
  **Mitigation:** Move business logic to API/domain layer and let Blazor only call services.

- **Risk:** Future need for public, fully anonymous traffic (e.g., open ticket viewing) may fit less well in the Server model.  
  **Mitigation:** Open for complementary Razor Pages / static views or future Blazor WASM module.

---

## Alternatives
- **Blazor WebAssembly:** Good for static hosting, but more work for auth and API security in MVP.
- **React/Angular:** Well-established, but requires its own build chain and breaks "pure .NET stack". Increased complexity and high maintenance needs.
- **Razor Pages / MVC Views:** Simpler, but worse for future interactions and real-time.
- **HTMX:** Modern and resource-efficient, provides fast and server-driven interaction without a heavy frontend stack. Fits well for applications with strong backend logic, but is not yet as established in the .NET ecosystem and has weaker support in the Azure toolchain. 

---

## References
- [System overview](../system_overview.md)
- [Microsoft Docs – Host and deploy Blazor Server](https://learn.microsoft.com/en-us/aspnet/core/blazor/host-and-deploy/server)

