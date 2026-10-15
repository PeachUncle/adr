# ADR-003: High-Level Agent Architecture

**Status:** Accepted

## Context

Based on our business strategy of autonomous content generation, we need a system architecture that is modular, scalable, and incorporates quality gates directly into the workflow. The design must break down the complex task of campaign creation into manageable, specialized components.

## Decision

We will adopt a more sophisticated, multi-stage pipeline that incorporates a crucial validation and revision loop, followed by multi-platform distribution.

The new architecture is as follows:
1.  **Campaign Initiation:** An initial agent determines the required content type(s) (e.g., image, video, text) based on the business intent.
2.  **Parallel Content Generation:** Specialized agents for each content type run concurrently to produce the initial drafts.
3.  **Iterative Validation Loop:** This is a critical quality gate. A `ValidationAgent` inspects the generated content against multiple criteria: brand identity, narrative alignment, QA, and correct use of design assets. If the content fails validation, it is sent back to the appropriate generation agent with feedback for revision. This loop continues until the content is approved.
4.  **Queue & Schedule:** Once approved, a `SchedulingAgent` places the content into a prioritized queue for distribution.
5.  **Platform Funnel:** A final `ParallelAgent` contains multiple `PlatformPublisher` agents (e.g., for X/Twitter, TikTok, YouTube), which adapt and publish the content to their respective channels.

## User Journey / Workflow Diagram

```mermaid
flowchart TD
    A[Business Intent] --> B{Campaign Type<br>Selector};
    B --> C[Image Agent];
    B --> D[Video Agent];
    B --> E[Text Agent];

    subgraph "Content Generation & Validation Loop"
        direction LR
        C --> F{Validation Agent<br>(QA, Narrative, Brand)};
        D --> F;
        E --> F;
        F -- Revision Needed --> C;
    end

    F -- Approved --> G[Queue &<br>Scheduler];
    G --> H{Platform Funnel};
    H --> I[X/Twitter Post];
    H --> J[TikTok Post];
    H --> K[YouTube Post];
```

## Consequences

**Positive:**
- **Enhanced Quality:** The explicit validation and revision loop ensures a much higher level of quality and brand alignment before publication.
- **Greater Flexibility:** The architecture can handle multiple content types (image, video, text) in parallel.
- **Increased Robustness:** The system can self-correct by revising content that doesn't meet standards, reducing the need for manual intervention.
- **Scalable Distribution:** The final funnel structure allows for easily adding or removing social media platforms.

**Negative:**
- **Increased Complexity:** The introduction of a feedback loop (`LoopAgent`) and more parallel stages makes the overall agent orchestration more complex to build and debug.
- **Potential for Latency:** The revision loop could, in some cases, increase the total time to get content approved if the initial generations repeatedly fail validation.
