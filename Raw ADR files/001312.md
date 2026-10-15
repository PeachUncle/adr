# ADR-010: Browser-Only Website

## Status

Accepted

## Context

The project requires a lightweight, scalable, and cost-effective solution for
delivering content to users. By adopting a server-less, browser-only approach,
the website can operate entirely in the client’s browser without relying on a
traditional server backend. This design leverages modern web technologies to
provide a seamless user experience while minimizing operational overhead.

## Decision

We decided to implement the website as a server-less, browser-only solution.

## Reasons

1. **Enhanced Data Privacy**:
   - Since all computations and data handling occur directly in the user's
     browser without communicating with a server, sensitive information never
     leaves the client side. This approach significantly reduces the risk of
     data breaches and ensures a higher level of privacy for users.

2. **Offline Capability**:
   - By leveraging technologies like Service Workers and local storage, the
     website can be made accessible even without an internet connection. This
     enhances user experience by allowing access to previously loaded content
     and certain functionalities while offline.

3. **Cost Efficiency**:
   - Eliminating a server backend reduces hosting and maintenance costs, as only
     static assets need to be served (e.g., HTML, CSS, JavaScript).

4. **Scalability**:
   - The browser-only approach easily scales with demand, as all computation
     occurs on the client side, with minimal strain on the hosting
     infrastructure.

5. **Improved Performance**:
   - Static files can be served via Content Delivery Networks (CDNs) for faster
     load times and reduced latency, providing a better user experience.

6. **Simplicity**:
   - A server-less model simplifies the architecture, reducing the complexity of
     managing server-side logic, databases, and APIs.

7. **Resilience and Uptime**:
   - Without a central server, there is no single point of failure, increasing
     the website’s reliability and uptime.

8. **Modern Development Practices**:
   - Leveraging browser-side rendering aligns with modern web development
     practices, allowing the use of tools and frameworks optimized for
     client-side execution (e.g., TypeScript, ESM, and frameworks like Vite or
     React).

## Consequences

1. **Limited Server-side Features**:
   - The server-less approach restricts functionality that requires server-side
     computation, such as authentication, dynamic content generation, or complex
     data processing.

2. **Increased Client Requirements**:
   - The browser-only model shifts computational load to the client, requiring
     users to have modern browsers and potentially higher-performing devices.

3. **Complexity in Client-side Data Management**:
   - Implementing features like data fetching or persistence requires additional
     effort, such as using third-party APIs or browser storage mechanisms.

## Alternatives Considered

### Traditional Server-based Website:

- **Pros**: Supports server-side rendering and dynamic content.
- **Cons**: Higher operational costs, more complex architecture, and
  increased maintenance requirements.

### Hybrid Approach:

- **Pros**: Combines the benefits of server-side and client-side rendering
  for dynamic and static content.
- **Cons**: Adds architectural complexity, requiring management of both
  server and client components.
