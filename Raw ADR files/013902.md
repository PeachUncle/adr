# ADR-004: RAG Function Tools Architecture

> **Scope**: Decision to use OpenAI Agents SDK function tools for vector database integration in the RAG chatbot.

- **Status:** Accepted
- **Date:** 2025-11-30
- **Feature:** 004-rag-vector-retrieval-fix
- **Context:** The RAG chatbot was not retrieving data from the vector database. The agent needed a mechanism to search textbook content and retrieve user context for personalization.

## Decision

Use OpenAI Agents SDK `@function_tool` decorator to create tools for:
1. **search_textbook**: Vector database search for relevant textbook content
2. **get_user_context**: User background retrieval for personalization

### Implementation Details

- **Framework**: OpenAI Agents SDK (`openai-agents>=0.0.7`)
- **Tool Pattern**: Synchronous function tools with `@function_tool` decorator
- **Agent Configuration**: Tools passed to Agent constructor
- **Context Passing**: HTTP headers (X-User-ID, X-Current-Page) for metadata

```python
from agents import Agent, function_tool

@function_tool
def search_textbook(query: str) -> str:
    """Search the Physical AI textbook for relevant content."""
    # Vector search implementation
    return context

agent = Agent(
    name="Physical AI Textbook Assistant",
    instructions=system_prompt,
    model=model,
    tools=[search_textbook, get_user_context]
)
```

## Consequences

### Positive

- **Agent autonomy**: Agent decides when to search based on query context
- **Clean separation**: Search logic encapsulated in dedicated tools
- **Error isolation**: Tool failures don't crash the agent
- **Extensibility**: Easy to add new tools (e.g., navigation, code execution)
- **SDK alignment**: Follows OpenAI Agents SDK best practices
- **Testability**: Tools can be unit tested independently

### Negative

- **Synchronous constraint**: Function tools must be synchronous
- **Tool overhead**: Each tool call adds latency
- **Prompt engineering**: System prompt must guide tool usage
- **Debugging complexity**: Tool execution is less transparent

## Alternatives Considered

### Alternative 1: Direct RAG Pipeline

Retrieve context before agent invocation, inject into system prompt.

**Why rejected**: 
- Less flexible - always retrieves even when not needed
- Larger context window usage
- Agent can't refine searches

### Alternative 2: Async Tool Execution

Use async function tools with await patterns.

**Why rejected**:
- OpenAI Agents SDK function tools work best with synchronous code
- Added complexity without significant benefit
- Vector search operations are fast enough synchronously

### Alternative 3: MCP Server Integration

Use Model Context Protocol server for vector search.

**Why rejected**:
- Overkill for single-purpose search
- Additional infrastructure complexity
- Function tools are simpler for this use case

## References

- Feature Spec: specs/004-rag-vector-retrieval-fix/spec.md
- Implementation Plan: specs/004-rag-vector-retrieval-fix/plan.md
- Related ADRs: history/adr/003-gemini-api-migration.md
- OpenAI Agents SDK Docs: https://github.com/openai/openai-agents-python
