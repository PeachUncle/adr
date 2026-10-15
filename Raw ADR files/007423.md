# ADR-011: Acknowledgment and Inspiration

## Status
Approved

## Context
The CodeCompass project is heavily inspired by the Medium article "Claude 3.7 Sonnet: the first AI model that understands your entire codebase" by Thack. This article provided the foundational ideas, structure, and technical approaches that form the core of this project.

As we develop CodeCompass, it's important to acknowledge the sources of inspiration and give proper credit to those whose work has influenced this project. While we have expanded upon the ideas presented in the original article, the credit for the core concepts belongs to the original author.

## Decision
We will:

1. Explicitly acknowledge Thack as the author of the inspiring article in our documentation
2. Maintain a dedicated page in our documentation that thanks the original author and links to the source material
3. Clearly attribute specific concepts and code examples when they are directly adapted from the original article
4. Distinguish between original concepts in the article and our extensions/implementations
5. Reach out to the author to inform them of our project and seek their feedback if possible

## Consequences
- **Positive**: Provides proper attribution and respects intellectual contributions
- **Positive**: Creates a more ethical project that acknowledges its inspirations
- **Positive**: May foster goodwill with the original author, potentially leading to collaboration
- **Positive**: Sets expectations about which concepts come from the original article versus our own extensions
- **Negative**: Creates an obligation to maintain attribution as the project evolves
- **Negative**: May create some constraints on how we describe or position the project

## Implementation Details

```markdown
# Acknowledgments

## Original Inspiration

CodeCompass was inspired by the article ["Claude 3.7 Sonnet: the first AI model that understands your entire codebase"](https://medium.com/@DaveThackeray/claude-3-7-sonnet-the-first-ai-model-that-understands-your-entire-codebase-560915c6a703) by Thack, published in February 2025. This insightful article presented the core concepts of:

- Semantic chunking for efficient codebase ingestion
- Differential updates to minimize token usage
- Hybrid local/Claude architecture
- Context-aware caching
- Strategic session management

Our project has implemented these concepts in a practical framework while adding additional features such as our multi-LLM experimental framework.

## Project Development

This GitHub repository is maintained by Tosin Akinosho, who has developed the concepts from the original article into a practical, production-ready framework.

## Special Thanks

We extend our gratitude to:

- Thack for the original vision and technical insights
- Anthropic for developing Claude 3.7 Sonnet
- The open source community for their various contributions to the tools used in this project
``` 