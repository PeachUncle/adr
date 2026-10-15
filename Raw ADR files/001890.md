# ADR-004: Saga Pattern for Publishing Workflow

**Date:** 2023-10-27

**Status:** Proposed

**Title:** Implementing Saga Pattern for AI-Powered Publishing Workflows

## Context

The project aims to create a blog expansion series, taking an AI banking license concept and transforming it into a narrative. This involves multiple stages, including AI content generation, asset creation, editorial review, and final publication. These stages are complex, involve multiple services (e.g., AI content generation service, image generation service, CMS integration service, notification service), and require a robust mechanism to handle failures and ensure data consistency across these distributed services.

Covenant 69 mandates the use of choreography principles for distributed systems. The publishing workflow, with its inherent complexity and potential for partial failures, is a prime candidate for a distributed transaction management pattern.

## Decision

We will adopt the **Saga pattern** for managing the complex, multi-service publishing workflow. Specifically, we will implement a **choreographed Saga**.

In a choreographed Saga, each service involved in the workflow publishes events that trigger subsequent services. There is no central orchestrator; instead, services react to each other's events. This aligns directly with the principles of Covenant 69.

The publishing workflow will be broken down into a series of steps, each handled by a dedicated service. Each service will perform its task and then publish an event indicating success or failure. Other services will subscribe to these events and react accordingly.

**Example Workflow Steps & Services:**

1.  **AI Content Generation Service:**
    *   **Action:** Generates the main blog post content based on prompts.
    *   **Success Event:** `ArticleContentGenerated` (payload: article text, metadata)
    *   **Failure Event:** `ArticleContentGenerationFailed`

2.  **AI Asset Generation Service:**
    *   **Action:** Generates accompanying images or other media based on the article content.
    *   **Triggered By:** `ArticleContentGenerated` event.
    *   **Success Event:** `ArticleAssetsGenerated` (payload: image URLs, media metadata)
    *   **Failure Event:** `ArticleAssetGenerationFailed`

3.  **Editorial Review Service:**
    *   **Action:** Allows for human review and editing of the generated content and assets.
    *   **Triggered By:** `ArticleAssetsGenerated` event.
    *   **Success Event:** `ArticleApprovedForPublishing` (payload: final article content, final assets)
    *   **Failure Event:** `ArticleRejectedForPublishing`

4.  **CMS Integration Service:**
    *   **Action:** Publishes the approved article to the blog CMS.
    *   **Triggered By:** `ArticleApprovedForPublishing` event.
    *   **Success Event:** `ArticlePublishedToCMS` (payload: article URL, publication timestamp)
    *   **Failure Event:** `ArticlePublishingToCMSFailed`

5.  **Notification Service:**
    *   **Action:** Notifies relevant parties (e.g., social media, internal teams) about the new publication.
    *   **Triggered By:** `ArticlePublishedToCMS` event.
    *   **Success Event:** `PublicationNotificationSent`
    *   **Failure Event:** `PublicationNotificationFailed`

**Compensation Actions:**

For each step, a corresponding compensation action will be defined to undo the work if a subsequent step fails.

*   If `ArticleAssetGenerationFailed`: The AI Content Generation Service might need to mark the content as draft or unpublishable.
*   If `ArticlePublishingToCMSFailed`: The Editorial Review Service might need to revert the article status, and the AI Asset Generation Service might need to clean up generated assets.

**Event Bus:**

A reliable event bus (e.g., Kafka, RabbitMQ, AWS SNS/SQS) will be used to facilitate the communication between services. This ensures asynchronous processing and decoupling.

## Rationale

*   **Distributed Transactions:** The Saga pattern is ideal for managing transactions that span multiple services in a distributed system. It ensures eventual consistency.
*   **Choreography Alignment:** Implementing a choreographed Saga directly adheres to Covenant 69's requirement for choreography principles, promoting loose coupling and decentralized control.
*   **Resilience and Fault Tolerance:** The pattern inherently handles partial failures by defining compensation actions. If a step fails, the system can roll back to a consistent state.
*   **Scalability:** Each service can be scaled independently based on its load.
*   **Maintainability:** Services are decoupled, making it easier to update or replace individual components without affecting the entire system.
*   **Clarity of Workflow:** The event-driven nature makes the workflow steps explicit and observable.

## Alternatives Considered

*   **Two-Phase Commit (2PC):** Not suitable for highly distributed, microservice-based architectures due to its blocking nature, performance overhead, and single point of failure (the transaction coordinator).
*   **Orchestrated Saga:** While also a valid Saga implementation, choreography is preferred here to strictly adhere to Covenant 69's emphasis on decentralized control and event-driven interactions. An orchestrator would introduce a central point of logic and coupling.
*   **Idempotency:** While not a pattern for distributed transactions, idempotency will be a crucial design principle within each service's operations to ensure that processing the same event multiple times does not lead to unintended side effects. This will be implemented at the service level.

## Consequences

*   **Increased Complexity:** Managing events, compensation logic, and ensuring idempotency adds complexity to service development.
*   **Eventual Consistency:** The system will be eventually consistent, meaning there might be a short period where data is inconsistent across services. This needs to be acceptable for the publishing workflow.
*   **Debugging Challenges:** Debugging distributed systems can be more challenging. Robust logging and tracing will be essential.
*   **Event Bus Dependency:** The reliability of the event bus is critical for the entire system's operation.

## Implementation Details

*   **Event Schema:** Standardized event schemas will be defined for all inter-service communication.
*   **Idempotency Keys:** Each event will carry an idempotency key to prevent duplicate processing.
*   **Dead Letter Queues (DLQs):** Failed events that cannot be processed after retries will be sent to DLQs for manual inspection and resolution.
*   **Monitoring and Alerting:** Comprehensive monitoring will be set up for event production/consumption, service health, and compensation actions.
*   **Tracing:** Distributed tracing will be implemented to track requests across service boundaries.

This ADR will be revisited as the project evolves and specific implementation choices for the event bus and service interactions are finalized.