# Web Search Module for OpenAI Responses API

- Status: accepted
- Deciders: Engineering Team, AI Platform Team
- Date: 2025-10-30
- ADR ID: ADR-002
- Tags: architecture, ai-platform, openai-integration

## Context and Problem Statement

The application needs to provide AI agents and services with the ability to search the web for current information before generating responses. OpenAI's Responses API offers comprehensive web search capabilities including non-reasoning search, agentic search with reasoning models, and deep research modes. We need a reusable, well-typed module that encapsulates these capabilities and can be used across the codebase.

## Decision Drivers

- **Consistency**: Need a standardized way to use web search across all services (RAG service, web app, agents)
- **Type Safety**: Comprehensive TypeScript types for all web search features
- **Reusability**: Single source of truth for web search logic that can be imported as needed
- **Feature Completeness**: Support for all OpenAI web search features (domain filtering, user location, cache-only mode, citations, sources)
- **Developer Experience**: Simple API that follows existing patterns (similar to file-search module)
- **Maintainability**: Centralized implementation that's easier to update when OpenAI API changes

## Considered Options

1. **Create a new module in @prisma/lib package** (chosen)
   - Place types, utilities, and API function in packages/lib/src/openai/web-search.ts
   - Export from the lib package index
   - Similar pattern to existing file-search.ts module

2. **Keep implementation in services/rag only**
   - Use existing types in services/rag/types/web-search.ts
   - Keep utilities in services/rag/web-search-utils.ts
   - Import where needed

3. **Create a separate @prisma/ai-search package**
   - New workspace package dedicated to AI search functionality
   - More modular but adds complexity

## Decision Outcome

Chosen option: "Create a new module in @prisma/lib package", because:

1. **Follows existing patterns**: The lib package already has openai/file-search.ts which serves a similar purpose
2. **Centralized types**: All web search types, utilities, and functions in one place
3. **Easy import**: Simple `import { runWebSearch } from '@prisma/lib'`
4. **Reduces duplication**: Eliminates need to copy types and utilities between services
5. **Better testing**: Comprehensive unit tests in one location
6. **Type safety**: Full TypeScript support with exported interfaces

### Positive Consequences

- **Single source of truth** for web search implementation
- **Improved developer experience** with clear, well-documented API
- **Better testability** with isolated unit tests
- **Easier maintenance** when OpenAI API evolves
- **Consistent usage** across all services and applications
- **Type safety** prevents runtime errors related to web search configuration

### Negative Consequences

- **Dependency addition**: Services now depend on the lib package for web search (already a dependency)
- **Build order**: lib package must be built before dependent services (already the case)
- **Migration effort**: Existing code using services/rag utilities may need updates (minimal impact)

## Implementation Details

### Module Structure

```typescript
// Types
- WebSearchTool, WebSearchPreviewTool
- WebSearchUserLocation, WebSearchFilters
- WebSearchResponse, WebSearchCallItem, MessageItemWithCitations
- UrlCitationAnnotation, WebSearchSource
- ExtractedWebSearchResults

// Tool Builders
- createWebSearchTool()
- createWebSearchPreviewTool()
- createUserLocation()

// Response Extraction
- extractTextFromWebSearchResponse()
- extractUrlCitations()
- extractWebSearchSources()
- extractWebSearchResults()

// Domain Utilities
- validateDomainFormat()
- normalizeDomain()
- normalizeAllowedDomains()

// High-Level API
- runWebSearch() - primary function for web searches
```

### Key Features Supported

1. **Non-reasoning web search**: Fast lookups without internal planning
2. **Agentic search**: Reasoning models that manage the search process
3. **Deep research**: Extended investigations with hundreds of sources
4. **Domain filtering**: Up to 20 allowed domains
5. **User location**: Geographic customization (country, city, region, timezone)
6. **Live internet access control**: Cache-only mode via external_web_access flag
7. **Citations extraction**: Inline URL citations with positions
8. **Sources extraction**: Complete list of consulted URLs
9. **Preview tool variant**: web_search_preview for testing

### Usage Example

```typescript
import { getOpenAIClient } from '@prisma/lib/openai/client';
import { runWebSearch } from '@prisma/lib/openai/web-search';

const client = getOpenAIClient();

const results = await runWebSearch({
  client,
  query: 'latest IFRS amendments',
  model: 'gpt-5',
  allowedDomains: ['ifrs.org', 'iasplus.com'],
  reasoningEffort: 'medium',
  includeSources: true,
});

console.log(results.answer);     // Generated answer text
console.log(results.citations);  // Array of URL citations
console.log(results.sources);    // All consulted sources
```

## Pros and Cons of the Options

### Option 1: Create module in @prisma/lib (chosen)

- Good, because follows existing patterns (file-search.ts)
- Good, because centralizes all web search logic
- Good, because provides comprehensive TypeScript types
- Good, because easy to import and use
- Good, because testable in isolation
- Bad, because adds to lib package size (minimal impact)

### Option 2: Keep in services/rag only

- Good, because no new files in lib package
- Good, because existing implementation works
- Bad, because types and utilities are not reusable
- Bad, because duplicates code if other services need web search
- Bad, because harder to maintain consistency
- Bad, because tests scattered across codebase

### Option 3: Create separate package

- Good, because highly modular
- Good, because dedicated to AI search features
- Bad, because adds workspace complexity
- Bad, because overkill for current needs
- Bad, because more build steps and dependencies

## Links

- [OpenAI Web Search Documentation](https://platform.openai.com/docs/guides/web-search)
- [OpenAI Responses API](https://platform.openai.com/docs/api-reference/responses)
- [Existing file-search module](../packages/lib/src/openai/file-search.ts)
- [Web search types](../services/rag/types/web-search.ts)
- [Web search utilities](../services/rag/web-search-utils.ts)
