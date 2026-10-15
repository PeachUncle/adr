# ADR-001: Metadata-Driven Architecture

## Status
Accepted

## Context

ToolVault needs to support a dynamic, evolving collection of analytical tools without requiring code changes to the user interface. The system must accommodate:

- Tools added and updated by both developers and trained analysts
- Approximately 100 tools across multiple categories
- Diverse tool types with varying input/output requirements
- Frequent tool updates and version management
- Consistent user experience across all tools

Three primary architectural approaches were considered:

1. **Hard-coded tool interfaces** - Each tool gets custom UI code
2. **Metadata-driven from index.json** - UI dynamically generated from metadata
3. **Hybrid approach** - Metadata-driven with custom UI override capability

## Decision

We will implement a **pure metadata-driven architecture** with the following characteristics:

### Core Architecture
- All tool interfaces dynamically generated from `index.json` metadata
- No hard-coded tool-specific UI components in the main application
- Single source of truth for tool definitions, parameters, and capabilities

### Metadata Generation
- Tool metadata auto-generated from pyDoc/jsDoc comments by upstream indexer process
- Validation and consistency checking handled by indexer, not ToolVault
- ToolVault trusts the validity of received `index.json` files

### Complex Tool Support
- Optional Jupyter notebooks provided for tools requiring detailed guidance
- Notebooks serve as interactive tutorials, not replacement UI
- Core tool execution remains metadata-driven

### Performance Strategy
- Lazy loading of detailed tool metadata (load names/categories first)
- Full metadata fetched on-demand when tool selected
- No browser caching of metadata to ensure freshness
- Approximately 100 tools expected, manageable without aggressive optimization

## Rationale

### Advantages
- **Rapid tool addition**: New tools require no UI code changes
- **Consistency**: All tools follow same interaction patterns
- **Maintainability**: Single metadata schema to maintain
- **Contributor accessibility**: Trained analysts can contribute tools via documented functions
- **Version management**: Tool versions naturally tracked in metadata
- **Automation**: Metadata generation from code comments reduces manual effort

### Trade-offs Accepted
- **UI flexibility**: Some tools may have suboptimal interfaces compared to custom UI
- **Performance overhead**: Dynamic form generation vs pre-built forms
- **Complexity limits**: Very complex tools may need Jupyter notebook guidance

### Mitigation Strategies
- Jupyter notebooks provide escape hatch for complex tool workflows
- Rich metadata schema supports common UI patterns (validation, defaults, help text)
- Progressive enhancement allows future addition of UI hints if needed

## Consequences

### Positive
- Tool contributors focus on functionality, not UI development
- Consistent user experience across all analytical tools
- Simplified testing and quality assurance processes
- Automatic UI adaptation to tool parameter changes

### Negative
- Some tools may have less intuitive interfaces than custom-designed UI
- Complex multi-step tools may require notebook guidance
- Performance impact from dynamic form generation (mitigated by lazy loading)

### Neutral
- Requires robust metadata schema design
- Upstream indexer becomes critical component for validation

## Implementation Notes

### Metadata Schema Requirements
- Support for common input types (string, number, boolean, JSON, GeoJSON, arrays)
- Validation rules and constraints
- Default values and help text
- Output type specifications
- Version and dependency information

### Loading Strategy
- Initial load: tool names, categories, descriptions for search/browse
- On-demand: full parameter schemas when tool selected
- No persistent caching to ensure users see latest tool definitions

### Quality Assurance
- Metadata validation performed by upstream indexer process
- Runtime type checking during tool execution
- Jupyter notebooks provide validation examples for complex tools

## Related Decisions
- ADR-002: Browser-First Execution Model (pending)
- ADR-003: Bundle-Based Tool Distribution (pending)
- ADR-007: W3C PROV Compliance for Provenance (pending)