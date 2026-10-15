# ADR 001: Dual RAG Database Selection

**Date**: 2025-08-01

**Status**: Accepted

## Context

The Storyline application requires a sophisticated memory system that can understand both the semantic content of a user's story and the complex narrative structure, including characters, plot points, and their relationships. A single database solution is unlikely to handle both of these requirements efficiently.

-   **Semantic Search**: Requires a vector database to perform fast similarity searches on text embeddings.
-   **Narrative Structure**: Requires a graph database to model and query the relationships between story entities.

## Decision

We have decided to implement a Dual RAG (Retrieval-Augmented Generation) architecture using two specialized databases:

1.  **Chroma DB** for the Traditional RAG (semantic search) component.
2.  **Neo4j** for the Graph RAG (narrative structure) component.

## Rationale

### Chroma DB

-   **Open-Source and Self-Hostable**: Gives us full control over the data and infrastructure, which is crucial for our privacy-first approach.
-   **Performance**: Optimized for fast vector similarity search, which is essential for real-time context retrieval.
-   **Ease of Use**: Simple API and good documentation, which will speed up development.
-   **Python Ecosystem**: Strong integration with the Python ecosystem, which is where our embedding and NLP models will be developed.

### Neo4j

-   **Leading Graph Database**: The most mature and widely used graph database, with a rich feature set and strong community support.
-   **Cypher Query Language**: A powerful and expressive query language specifically designed for graph traversal, which will be essential for querying our narrative structure.
-   **Scalability**: Proven to scale to handle large and complex graphs.
-   **Data Modeling**: Provides a natural way to model the complex relationships between characters, locations, and events in a story.

## Consequences

-   **Increased Complexity**: This approach introduces the complexity of managing two separate database systems.
-   **Integration Overhead**: We will need to build a hybrid query system to route queries and synthesize results from both databases.
-   **Data Consistency**: We will need to implement mechanisms to ensure data consistency between the two databases.
-   **Operational Overhead**: We will need to manage the deployment, monitoring, and scaling of both Chroma DB and Neo4j.

Despite these challenges, we believe that the benefits of using specialized databases for each task far outweigh the drawbacks. This approach will allow us to build a truly intelligent and powerful memory system that will be a key differentiator for the Storyline application.
