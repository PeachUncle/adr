# ADR-005: LLM-Friendly Output Structure

## Status
Accepted

## Context
PackFS is designed specifically to enable LLM agents to interact with filesystems. However, feedback from real-world usage (v0.1.20 testing) revealed that the nested output structure was preventing LLMs from effectively using PackFS.

The original structure wrapped all results in a nested format:
```javascript
{
  success: true,
  data: {
    success: true,
    content: "file content here",  // LLMs cannot find this
    exists: true,
    files: [...]
  },
  metadata: {...}
}
```

LLMs are trained on millions of examples that use flat structures where properties are directly accessible at the top level. The nested structure caused a 100% failure rate when LLMs tried to access file content, even with explicit instructions about the structure.

## Decision
We will implement a flat output structure as the default behavior for all PackFS integrations. This ensures LLM compatibility out of the box.

The new structure provides direct access to all properties:
```javascript
{
  success: true,
  content: "file content here",    // Direct access
  exists: true,
  files: [...],
  metadata: {...}                  // Only metadata remains nested
}
```

## Consequences

### Positive
- **LLM Compatibility**: Works immediately with all major LLM providers (GPT-4, Claude, Llama) without custom wrappers
- **Reduced Errors**: Eliminates false negatives where successful operations were reported as failures
- **Better Developer Experience**: No need for every user to write wrapper functions
- **Increased Adoption**: Developers encounter immediate success rather than failures

### Negative
- **Breaking Change**: This is a breaking change for any existing users who depend on the nested structure
- **Version Bump**: Requires a minor version bump (0.2.0) to signal the breaking change

### Implementation Details
1. The flattening happens in the integration layer (`mastra.ts`, `langchain-js.ts`, etc.)
2. The semantic backends continue to return their natural flat structure
3. The integration tools spread the result object to flatten nested properties
4. Only metadata remains nested for organizational purposes

## Rationale
PackFS exists specifically to enable LLM-filesystem interaction. A structure that prevents LLMs from using it defeats the core purpose. This is analogous to building a voice assistant that only accepts typed commands - it's technically functional but misses the fundamental use case.

The flat structure aligns with:
- LLM training data patterns
- Common JavaScript/TypeScript conventions
- RESTful API response patterns
- Developer expectations

## Implementation
The change was implemented in the Mastra integration and can be applied consistently across all framework integrations. The pattern is:

```javascript
// Instead of wrapping in data
return {
  success,
  data: result,
  metadata: {...}
};

// Flatten the structure
return {
  success,
  ...result,  // Spread all properties to top level
  metadata: {...}
};
```

## References
- Feedback Report: PackFS v0.1.20 from Test Client Team
- Original Issue: LLMs consistently fail to parse nested structure
- Test Results: 100% failure rate with nested structure, 100% success with flat structure