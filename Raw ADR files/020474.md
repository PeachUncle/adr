# ADR 002: Supabase for Database and Authentication

## Status

Accepted

## Context

We need a persistent data store and an authentication mechanism for Writegy. The solution should be reliable, scalable, and cost-effective, aligning with our "Zero-Cost" philosophy for the MVP.

## Decision

We have chosen to use **Supabase** for both the PostgreSQL database and user authentication.

## Consequences

### Positive

*   **Cost-Effective:** Supabase offers a generous free tier that includes a PostgreSQL database, authentication, and storage. This is ideal for our MVP.
*   **Managed Service:** As a managed service, Supabase handles the database setup, maintenance, and backups, reducing our operational overhead.
*   **Integrated Auth:** Supabase provides a complete authentication solution out-of-the-box, including JWT-based authentication, social logins, and user management. This saves significant development time.
*   **Scalability:** Supabase's paid tiers offer a clear path for scaling as the application grows.
*   **Standard Technologies:** It uses standard PostgreSQL and JWT, so we are not locked into a proprietary ecosystem.

### Negative

*   **Vendor Lock-in:** While it uses standard technologies, a deep integration with Supabase's features could make it harder to migrate to another provider in the future.
*   **Data Egress Costs:** Like any cloud provider, there can be costs associated with data egress if we exceed the free tier limits.
*   **Cold Starts:** The free tier of Supabase may have "cold start" issues where the database can be slow to respond after periods of inactivity. This is also mentioned in `context.md`.

### Mitigation of Negatives

*   We will primarily use Supabase for its standard PostgreSQL and authentication capabilities, avoiding deep integration with its more proprietary features to ease potential future migrations.
*   The application architecture will be designed to be database-agnostic by relying on JPA and standard SQL, which will simplify a potential move to a different PostgreSQL provider.
*   For the MVP, the potential for cold starts is an acceptable trade-off for the benefits of a free, managed service.
