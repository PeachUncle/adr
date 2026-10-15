# ADR-0009: Text Selection Strategy

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-11-30
- **Feature:** 001-physical-ai-robotics-book
- **Context:** The RAG pipeline for the "Physical AI & Humanoid Robotics" textbook requires a feature for users to highlight text and ask the AI a question about the selection. This decision defines how the system handles the user's selected text to provide context-aware explanations.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

To implement the "Ask about selection" feature, Strategy B (Augmented) will be used. This strategy uses the `selection_text` as the primary context but also searches Qdrant for *related* concepts to provide a more comprehensive answer.
     - Endpoint: `POST /explain-selection` in `api/main.py`.
     - Input: `selection_text` (primary context) and optional `query`.
     - Retrieval: Uses `selection_text` to seed a Qdrant search for related content.

<!-- For technology stacks, list all components:
     - Framework: Next.js 14 (App Router)
     - Styling: Tailwind CSS v3
     - Deployment: Vercel
     - State Management: React Context (start simple)
-->

## Consequences

### Positive

- **Enhanced Context**: Provides richer, more relevant explanations by augmenting the selected text with related information from the book.
- **Improved User Experience**: Allows users to quickly get answers to specific highlighted sections while still benefiting from the broader context of the book.
- **Flexibility**: Supports both direct explanation of the selected text and exploration of related concepts.

<!-- Example: Integrated tooling, excellent DX, fast deploys, strong TypeScript support -->

### Negative

- **Increased Complexity**: Strategy B is more complex to implement compared to Strategy A (Pure Context) due to the need for combining `selection_text` with vector search results.
- **Potential for Irrelevance (Mitigated)**: There's a slight risk of introducing less relevant information if the Qdrant search for related concepts isn't perfectly aligned with the user's implicit intent. This is mitigated by using `selection_text` as *primary* context and careful tuning of retrieval.
- **Higher Latency**: Performing an additional Qdrant search might slightly increase response latency compared to using only the selected text.

<!-- Example: Vendor lock-in to Vercel, framework coupling, learning curve -->

## Alternatives Considered

- **Strategy A (Pure Context)**: Use `selection_text` as the *only* context for the LLM.
     - **Why rejected**: While simpler and safer for "Explain this specific paragraph," it lacks the ability to provide broader context or relate the selection to other parts of the book, which could limit the depth of explanations for a textbook companion. It would also lead to "I don't know" responses more frequently if the selected text alone is insufficient.

<!-- Group alternatives by cluster:
     Alternative Stack A: Remix + styled-components + Cloudflare
     Alternative Stack B: Vite + vanilla CSS + AWS Amplify
     Why rejected: Less integrated, more setup complexity
-->

## References

- Feature Spec: /home/abdullahiqbal/Abdullah/hackathon-book-project/specs/001-physical-ai-robotics-book/spec.md
- Implementation Plan: /home/abdullahiqbal/Abdullah/hackathon-book-project/specs/001-physical-ai-robotics-book/plan.md
- Related ADRs: null
- Evaluator Evidence: null <!-- link to eval notes/PHR showing graders and outcomes -->
