# ADR-003: Choice of Backend API Framework

**Date:** 2025-09-02

**Status:** Decided & Implemented

## Context

While Supabase serves as our primary BaaS for data, auth, and storage, a separate server-side component is required for specific business logic. This includes orchestrating calls to the third-party OpenAI API and implementing complex workflows that are not suitable for Postgres functions. The development team's primary language is TypeScript/JavaScript, as established by the React frontend.

## Decision

We will use **Node.js with the Express framework** to build our backend API. This API will act as a "thin" layer, primarily handling AI interactions and serving as a secure intermediary between the client and Supabase for complex operations.

## Consequences

*   **Pros:**
    *   **Language Synergy:** Using JavaScript/TypeScript across the entire stack (React frontend, Node.js backend) eliminates language context-switching for developers, streamlining the development process and simplifying the talent pool.
    *   **Vast Ecosystem:** The npm ecosystem provides mature, well-supported libraries for all our needs, including `express`, `cors`, `zod` for validation, and the official `openai` client.
    *   **Lightweight & Unopinionated:** Express is famously minimal, which is ideal for our use case. We don't need a heavy, opinionated framework, as our API has a focused set of responsibilities.
    *   **Serverless-Friendly:** The Express application is easily wrapped for serverless deployment, as seen in `netlify/functions/api.js`, which aligns perfectly with our hosting strategy.

*   **Cons:**
    *   **Unstructured by Default:** As an unopinionated framework, Express can lead to unstructured code if not managed carefully. This was mitigated by implementing a clear MVC-style pattern (`controllers`, `routes`, `middleware`), which provides excellent separation of concerns.
    *   **Single-Threaded Performance:** Node.js's single-threaded nature can be a bottleneck for CPU-intensive tasks. However, our API is almost entirely I/O-bound (making API calls, database queries), which is a perfect use case for Node.js's non-blocking event loop.

*   **Alternatives Considered:**
    *   **Python (FastAPI/Flask):** While popular in the AI space, this would introduce a second language and package manager into the project, increasing complexity without a compelling benefit, as the Node.js `openai` library is excellent.
    *   **Supabase Edge Functions:** These could have been used to house the AI logic. A separate Express server was chosen for a more traditional and portable local development experience and to avoid potential execution time limits of serverless functions for more complex, future AI chains.
