# Job Description ID Decision

## Status

Accepted 2023-10-28

## Context

The `JobDescription` in our library holds the metadata for scheduled tasks. Among its attributes, the `id` plays a significant role. There are two primary considerations for this ID:
1. **Business ID**: An ID that is meaningful within the context of the business or application.
2. **Auto-Generated ID**: A system-generated, unique identifier.

Each approach has its merits and potential drawbacks.

## Decision

We will allow both types of IDs for `JobDescription`:
1. A business-provided ID, when there's a meaningful business context.
2. An auto-generated ID by the library, for ease of use and to ensure uniqueness when a business ID isn't available or relevant.

## Rationale

### Business ID:
1. **Business Context**: Having an ID that aligns with business logic can make operations more intuitive and contextual.
2. **Traceability**: If other systems or processes also recognize the ID, it's easier to trace jobs across multiple systems.
3. **Explicit Control**: The client has direct control over the ID, which can be beneficial for certain use cases.

### Auto-Generated ID:
1. **Ease of Use**: Clients can quickly schedule jobs without concerning themselves with ID generation.
2. **Guaranteed Uniqueness**: The library ensures the ID is unique, preventing potential ID conflicts.
3. **Abstraction**: Clients who don't require a specific ID don't need to deal with the underlying ID generation logic.

## Downsides

### Business ID:
1. **Potential for Conflicts**: If not managed carefully, there might be ID conflicts, especially if the ID isn't guaranteed unique across all jobs.
2. **Increased Responsibility**: It places the onus on the client to ensure the ID's uniqueness, especially within external systems like dkron.

### Auto-Generated ID:
1. **Lack of Context**: An auto-generated ID might not hold any meaningful information about the job.
2. **Dependency**: Relies on the library's generation logic, which might not be suitable for all use cases.
3. **Conditional Storage Overhead**: If a user of the library wishes to interact with the scheduled job in the feature (e.g., remove or update it), the auto-generated ID must be stored. This introduces potential clutter of entity/aggregate 

## Updates

