# ADR-002: RAG Pipeline URL Discovery and Text Chunking Strategy

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Proposed
- **Date:** 2025-12-18
- **Feature:** 002-rag-data-ingestion
- **Context:** Decisions regarding how the data ingestion pipeline will identify the content to scrape from a Docusaurus website and how that content will be segmented into manageable pieces for embedding. These choices directly impact the pipeline's efficiency, coverage, and the quality of subsequent RAG retrieval.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

The RAG data ingestion pipeline will implement the following strategies for URL discovery and text chunking:
-   **URL Discovery:** The pipeline will discover URLs by parsing the `sitemap.xml` file of the deployed Docusaurus website.
-   **Text Chunking:** Extracted text content will be chunked specifically by paragraph. This means that the content within each HTML `<p>` tag will be treated as a distinct text chunk.

## Consequences

### Positive

-   **URL Discovery (`sitemap.xml`):**
    -   **Efficiency:** Parsing `sitemap.xml` provides a direct and efficient way to obtain a comprehensive list of public URLs, avoiding the overhead and potential complexities of recursive web crawling.
    -   **Completeness:** Ensures that all pages explicitly declared for indexing in the sitemap are included in the ingestion process.
-   **Text Chunking (By Paragraph):**
    -   **Semantic Cohesion:** Chunking by paragraph naturally preserves the semantic integrity of the text. Paragraphs typically represent a single, coherent idea or topic, which is highly beneficial for generating contextually relevant embeddings and improving retrieval accuracy.
    -   **Simplicity:** This method is straightforward to implement using standard HTML parsing libraries.

### Negative

-   **URL Discovery (`sitemap.xml`):**
    -   **Dependence and Brittleness:** The pipeline's robustness is dependent on the `sitemap.xml` file being present, correctly formatted, and kept up-to-date. If the sitemap is missing, contains errors, or is not updated, the pipeline might fail or process outdated/incomplete content.
    -   **Limited Scope:** Only discovers URLs explicitly listed in the sitemap. Dynamically generated pages or content not indexed in the sitemap will be missed.
-   **Text Chunking (By Paragraph):**
    -   **Variable Chunk Sizes:** Paragraphs can vary significantly in length. Very short paragraphs might lack sufficient context for effective embeddings, while very long paragraphs could exceed the input token limits of embedding models or dilute the contextual density.
    -   **Sub-optimal Context Boundary:** Important information or context might occasionally span across multiple paragraphs. Chunking strictly by paragraph could inadvertently split related information, potentially impacting embedding quality for such cases.

## Alternatives Considered

-   **Alternative URL Discovery (Crawl from a root URL):**
    -   **Description:** Start from a given root URL and recursively follow all internal links within the domain.
    -   **Why rejected:** While more resilient to missing sitemaps and capable of discovering unindexed content, it is significantly slower, more resource-intensive, and complex to implement (requires managing visited URLs, handling redirects, respecting `robots.txt`, and managing recursion depth). The user's explicit preference for `sitemap.xml` for its efficiency and directness was a primary factor.
-   **Alternative URL Discovery (Explicit List):**
    -   **Description:** The pipeline is provided with a manually curated, explicit list of URLs to process.
    -   **Why rejected:** Offers maximum control but is not scalable for large or frequently updated websites due to the manual effort required for maintenance and curation.
-   **Alternative Text Chunking (Fixed Token Count):**
    -   **Description:** Split text into chunks of a predefined, fixed number of tokens (e.g., 512 tokens).
    -   **Why rejected:** While providing uniform chunk sizes, this method risks splitting sentences or ideas mid-paragraph, leading to fragmented context and potentially poorer embedding quality. It sacrifices semantic cohesion for uniformity.
-   **Alternative Text Chunking (Recursive Character Splitting):**
    -   **Description:** A sophisticated method (e.g., `RecursiveCharacterTextSplitter` from `langchain`) that attempts to split text using a hierarchical list of separators (e.g., `

`, `
`, `.` , ` `) to maintain semantic integrity while also controlling chunk size and overlap.
    -   **Why rejected:** While often a recommended strategy for RAG for its balance of semantic preservation and size control, the user explicitly chose the simpler, paragraph-based chunking. This alternative adds more complexity to the chunking logic.

## References

- Feature Spec: `specs/002-rag-data-ingestion/spec.md`
- Implementation Plan: `specs/002-rag-data-ingestion/plan.md`
- Related ADRs: N/A
- Evaluator Evidence: `specs/002-rag-data-ingestion/research.md`
