# ADR: Choosing API Key Authentication for Landing Page Data Access

- **Status**: accepted
- **Date**: 2025-10-24

## Context

A NestJS backend has been developed and connected to a database. An admin React-based CMS panel is used to manage data, and authentication for it is handled through username and password. Additionally, a public NextJS landing page is required to display selected read-only data from the same database. The landing page is intended to remain publicly accessible without requiring user authentication.

A need was identified to enable the landing page to securely fetch publicly visible data from the backend, while maintaining strict protection for administrative routes and sensitive resources. The situation required a method that would balance security, performance, and ease of maintenance while keeping the system consistent with the existing backend authentication logic.

## Decision

The chosen solution is the use of **API Key Authentication** for the endpoints accessed by the public-facing landing page. Dedicated read-only API routes are protected using API key validation within the NestJS backend. The NextJS landing page retrieves data through server components that securely use the API key stored in environment variables.

This approach was selected because it provides a strong balance between security and performance. It allows requests from trusted server environments to be identified and validated without exposing sensitive credentials on the client side. In addition, API keys can be scoped, rotated, or revoked if needed, offering more flexibility and resilience compared to public or unauthenticated endpoints.

## Options Considered

| Option                 | Security Level | Performance | Complexity | Maintenance | Summary                                                                                                |
| ---------------------- | -------------- | ----------- | ---------- | ----------- | ------------------------------------------------------------------------------------------------------ |
| Public Endpoints       | Medium         | High        | Low        | Low         | Implementation is simple, but vulnerability to misuse exists if endpoints are not properly restricted. |
| API Key Authentication | High           | High        | Low        | Medium      | Security is improved with low complexity; key management adds moderate operational effort.             |
| Read-Only DB User      | High           | High        | Medium     | Medium      | Read-only database access enhances safety but increases configuration complexity.                      |
| Dedicated Microservice | Very High      | Medium      | High       | High        | Isolation improves security but requires additional infrastructure and introduces latency.             |
| Caching Layer          | Medium         | Very High   | Medium     | Medium      | High performance is achieved, but data consistency and cache invalidation must be managed.             |
| Static Site Generation | Medium         | Very High   | Low        | Low         | Performance is excellent but unsuitable for frequently changing or dynamic data.                       |

The API Key Authentication method was chosen for its strong combination of secure endpoint control and simplicity in implementation. It facilitates backend data exposure for the landing page with limited risk of unauthorized access.

## Consequences

- Backend endpoints intended for the landing page are secured using API key verification within NestJS.
- Only read operations are exposed to the public interface; create, update, and delete actions remain protected behind admin authentication.
- API keys are generated and stored securely, with hashing and rotation policies applied.
- NextJS server components use environment variables for confidential storage of API keys, ensuring that no keys are sent to the client.
- Rate limiting, monitoring, and logging are implemented to prevent abuse and to audit API usage.
- Maintenance requires periodic key rotation and monitoring of access logs, but overall system complexity remains low.

## References

- API key authentication patterns and server-side validation best practices
  - [API Keys: API Authentication Methods & Examples (Stoplight)](https://blog.stoplight.io/api-keys-best-practices-to-authenticate-apis) [94]
  - [API Authentication Security - Best Practices (Impart Security)](https://www.impart.security/api-security-best-practices/api-authentication-security-best-practices) [123]
  - [API key security best practices: 8 Essential Tips (MultitaskAI)](https://multitaskai.com/blog/api-key-security-best-practices/) [127]

- NestJS guards and secure public endpoint configuration
  - [NestJS Authentication Guide Secure Your APIs Like A Pro (AST Consulting)](https://astconsulting.in/java-script/nodejs/nestjs/nestjs-authentication-guide) [21]
  - [How to secure a REST API with an API key - NestJS (StackOverflow)](https://stackoverflow.com/questions/72238595/how-to-secure-a-rest-api-with-an-api-key) [31]
  - [Understanding Guards in NestJS (DigitalOcean)](https://www.digitalocean.com/community/tutorials/understanding-guards-in-nestjs) [74]

- NextJS data fetching using server components and API headers
  - [Getting Started: Fetching Data (NextJS official docs)](https://nextjs.org/docs/app/getting-started/fetching-data) [11]
  - [Functions: headers (NextJS official docs)](https://nextjs.org/docs/app/api-reference/functions/headers) [72]
  - [Functions: fetch (NextJS official docs)](https://nextjs.org/docs/app/api-reference/functions/fetch) [82]

- Key storage, hashing, and rotation strategies for secure implementations
  - [Best Practices For Storing User API Keys With Node/Mongo (Reddit)](https://www.reddit.com/r/node/comments/8zf5zs/best_practices_for_storing_user_api_keys_with/) [87]
  - [How to safely store API Keys in a database for a REST API? (StackOverflow)](https://stackoverflow.com/questions/78580774/how-to-safely-store-api-keys-in-a-database-for-a-rest-api) [89]
  - [10 API Key Management Best Practices (Serverion)](https://www.serverion.com/uncategorized/10-api-key-management-best-practices/) [92]

- Performance and architectural impact of different data access options
  - [Imperva API Security: Authentication Risk Report—Key Findings and Fixes (Imperva)](https://www.imperva.com/blog/imperva-api-security-authentication-risk-report-key-findings-fixes/) [124]
  - [API Authentication: Part II. API Keys (Dev.to)](https://dev.to/eugene-zimin/api-authentication-part-ii-api-keys-2l51) [125]
