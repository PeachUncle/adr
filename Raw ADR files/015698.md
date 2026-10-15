# ADR-0011: Custom Markdown Splitting Strategy

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-11-30
- **Feature:** 001-physical-ai-robotics-book
- **Context:** The RAG pipeline for the "Physical AI & Humanoid Robotics" textbook relies on accurate context retrieval from Markdown source files. Standard text splitting methods often break semantic units like code blocks, Docusaurus admonitions (tip, danger), and headers, leading to fragmented context and potential hallucinations in AI responses. A custom splitting strategy is necessary to preserve these critical technical content structures.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

To ensure semantic integrity of technical content, a custom Markdown splitting strategy will be implemented within `scripts/ingest.py`. This strategy will:
- **Primary Splitters**: Utilize regex to identify and preserve entire Level 2-4 Markdown headers, fenced code blocks (```...```), and Docusaurus admonition blocks (:::tip...::: / :::danger...::: etc.) as distinct, unbreakable semantic units.
- **Secondary Splitter**: For regular prose within these identified blocks or between them, a `RecursiveCharacterTextSplitter` will be applied with a `chunk_size` of 512 tokens and `chunk_overlap` of 50 tokens.
- **Metadata**: Each chunk will include rich metadata such as `chapter_id`, `chapter_title`, `section`, `type` (e.g., `text`, `code_block`, `admonition`), `language` (for code blocks), and `admonition_type` for enhanced filtering and contextual retrieval.

## Consequences

### Positive

- **Improved Retrieval Quality**: By preserving complete code blocks and admonitions, the RAG system will retrieve more accurate and contextually rich information, crucial for explaining technical concepts and code snippets.
- **Reduced Hallucinations**: The LLM will receive semantically coherent chunks, significantly reducing the likelihood of generating inaccurate or misleading information due to fragmented context.
- **Enhanced User Experience**: Users will receive more precise answers, especially when querying about specific code examples or important tips/warnings in the textbook.
- **Flexibility in Retrieval**: Rich metadata associated with each chunk enables advanced filtering (e.g., retrieving only code blocks related to a specific chapter, or all tips) during the retrieval phase.

### Negative

- **Increased Implementation Complexity**: Developing and maintaining a custom Markdown splitter with robust regex and state management is more complex than using off-the-shelf splitters.
- **Potential for Edge Cases**: Markdown parsing can be complex, and the custom splitter might encounter unforeseen edge cases or unusual formatting that could lead to suboptimal chunking, requiring ongoing refinement.
- **Performance Overhead**: Custom parsing and explicit handling of different block types might introduce a slight overhead during the ingestion process compared to simpler splitting methods.

## Alternatives Considered

**1. Naive `RecursiveCharacterTextSplitter` (or similar basic splitters)**:
   - **Why rejected**: These splitters are agnostic to Markdown's semantic structure. They would blindly split code blocks, breaking their integrity, and fragment admonition blocks, leading to a loss of critical context for technical content. This would result in poor retrieval quality and increased hallucinations.

**2. LangChain's `MarkdownTextSplitter` (or similar pre-built Markdown splitters)**:
   - **Why rejected**: While better than naive splitters, many pre-built Markdown splitters do not offer the fine-grained control needed to specifically preserve Docusaurus admonition blocks or guarantee the integrity of all types of fenced code blocks as single, atomic units. Custom logic is required to meet the precise semantic preservation needs of this technical textbook.

## References

- Feature Spec: /home/abdullahiqbal/Abdullah/hackathon-book-project/specs/rag-chatbot/spec.md
- Implementation Plan: /home/abdullahiqbal/Abdullah/hackathon-book-project/specs/001-physical-ai-robotics-book/plan.md
- Related ADRs: 0009-text-selection-strategy.md, 0010-rag-system-model-choice-and-hybrid-search-strategy.md
- Evaluator Evidence: null
