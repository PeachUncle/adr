# ADR-004: Native Mastra Integration Layer

## Status
Accepted

## Context

Based on real-world usage feedback from a PackFS Test Client project, significant boilerplate code and complexity exists when integrating PackFS with the Mastra agent framework. The current implementation requires:

1. **Custom Wrapper Classes**: 160+ lines of boilerplate code to bridge PackFS and Mastra patterns
2. **Schema Duplication**: Manual Zod schema creation for each tool implementation
3. **Inconsistent Security**: Each project implements its own security validation approach
4. **Pattern Repetition**: Similar filesystem operation patterns recreated across projects

The feedback specifically identified the need for native Mastra support to reduce integration complexity from 160+ lines to under 20 lines while improving security and consistency.

## Decision

We will implement a dedicated Mastra integration layer within PackFS that provides:

### 1. Native Tool Factory
- Export `createPackfsTools()` function that generates ready-to-use Mastra tools
- Support permission-based tool generation (read, write, search, list)
- Integrate with PackFS security system automatically
- Provide configurable schemas and security policies

### 2. Standardized Intent-Based API
- Define consistent intent patterns for all filesystem operations:
  - `AccessIntent` for read operations
  - `DiscoverIntent` for search/list operations  
  - `UpdateIntent` for write operations
- Each intent includes purpose, target, and options/preferences

### 3. Pre-Built Zod Schemas
- Export ready-to-use schemas for all tool types
- Standardized input/output schemas with comprehensive validation
- Support for optional and extensible schema customization

### 4. Enhanced Security Integration
- Built-in security validation at the tool level
- Configurable path restrictions, file size limits, extension filtering
- Rate limiting support for production deployments
- Automatic path sandboxing within configured root

### 5. Semantic Content Support
- Specialized tools for structured content like context networks
- Document relationship extraction and preservation
- Semantic search capabilities with relevance scoring

## Implementation Plan

### Phase 1: Core Integration Module
- Create `/src/integrations/mastra/` directory structure
- Implement tool factory and intent-based API
- Add comprehensive Zod schemas
- Integrate with existing security system

### Phase 2: Enhanced Features
- Add semantic processing capabilities
- Implement relationship mapping for structured content
- Add batch operation support
- Performance optimizations

### Phase 3: Documentation and Migration
- Update documentation with Mastra examples
- Create migration guide from custom wrappers
- Add integration tests for Mastra-specific functionality

## Benefits

- **90% reduction in boilerplate code** for Mastra integrations
- **Consistent security patterns** across all PackFS-using projects
- **Improved developer experience** with ready-to-use tools
- **Better maintainability** through standardized approaches
- **Enhanced performance** through optimized implementations

## Example Usage

After implementation, the current complex wrapper pattern:

```typescript
// Current: 160+ lines of custom wrapper code
class SimpleFilesystemWrapper {
  // Complex implementation...
}
```

Becomes:

```typescript
// New: Simple configuration-based approach
import { createPackfsTools } from "packfs-core/mastra";

export const { fileReader, fileSearcher, fileWriter } = createPackfsTools({
  rootPath: "/project/context-network",
  permissions: ["read", "write", "search"],
  security: {
    maxFileSize: 1024 * 1024,
    allowedExtensions: [".md", ".txt", ".json"],
  },
});
```

## Consequences

### Positive
- Significantly reduced integration complexity for Mastra users
- Standardized security patterns improve overall ecosystem security
- Framework-native integration improves performance and reliability
- Reduced maintenance burden for projects using PackFS with Mastra

### Negative
- Additional dependency on Mastra framework (mitigated by optional peer dependency)
- Increased complexity in PackFS core (managed through modular architecture)
- Need to maintain compatibility with Mastra API changes

### Neutral
- Existing non-Mastra integrations remain unchanged
- Backward compatibility maintained through existing API
- Optional nature means projects can choose integration level

## Related Decisions
- Builds upon ADR-001 (TypeScript/NPM package setup)
- Extends ADR-003 (Semantic interface redesign)
- Prepares for future framework integration expansions