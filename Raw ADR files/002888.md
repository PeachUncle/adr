# ADR 002: Hybrid Query Routing Logic

**Date**: 2025-08-01

**Status**: Proposed

## Context

The Dual RAG memory system requires a routing layer to direct incoming queries to the appropriate database (Chroma DB for semantic search, Neo4j for graph-based queries). A simple, effective, and performant routing strategy is needed to ensure the best possible results are returned to the user.

## Decision

We will implement a keyword-based classification approach as the initial routing strategy. The router will inspect the query for specific keywords (e.g., "who", "where", "what") to determine if it's a narrative (graph) or semantic query.

## Rationale

-   **Simplicity**: This approach is simple to implement and understand, which is ideal for the initial version of the hybrid query system.
-   **Performance**: Keyword matching is extremely fast and will not add any significant overhead to the query process.
-   **Effectiveness**: For many common queries, this simple classification will be surprisingly effective. For example, questions starting with "who" are almost always about characters, which are best handled by the graph database.
-   **Extensibility**: This approach can be easily extended in the future. We can add more sophisticated classification logic, such as using a small, fine-tuned language model, without changing the overall architecture.

## Consequences

-   **Limited Accuracy**: This simple approach will not be able to correctly classify all queries. For example, a query like "what happened in Paris?" could be either semantic or narrative.
-   **Potential for Mis-routing**: Some queries may be mis-routed, leading to suboptimal results.
-   **Future Work**: We will need to invest in a more sophisticated classification model in the future to improve the accuracy of the query routing.

Despite these limitations, we believe that this approach is the best starting point for the hybrid query system. It will allow us to get a functional version of the system up and running quickly, and we can iterate and improve on it over time.
