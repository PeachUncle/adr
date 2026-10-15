# ADR-004: Logging Implementation Strategy

## Status

Proposed

## Context

ADR-003 established use-case-based logging classification with six categories:

1. Tracing - Track execution flow
2. Error Tracking - Identify and resolve issues
3. User Behavior - Analyze for UX improvements
4. Performance - Monitor resource usage
5. Security Audit - Compliance and audit trails
6. Business Metrics - KPIs and analytics

Now we need to decide on the concrete implementation approach for each use case, considering:

- Tabler is a CLI application with different needs than web services
- Need to minimize dependencies and complexity
- Some use cases may not be immediately relevant
- Future extensibility is important

## Decision

**Implement a phased approach with custom lightweight modules**, prioritizing immediate needs:

### Phase 1: Core Use Cases (Immediate)

1. **Tracing** - Custom lightweight implementation
   - Context-based propagation using Go's context.Context
   - Defer-based API: `defer logging.Trace(ctx, "operation")()`
   - Environment variable control: `TABLER_TRACE=1`
   - ~200 lines of code

2. **Error Tracking** - Structured error logging
   - Enhanced error types with context
   - Stack trace capture for unexpected errors
   - JSON output to stderr
   - Integration with trace IDs

3. **User Behavior** - Command usage tracking
   - Track which commands and features are used
   - Success/failure patterns
   - Optional analytics (opt-in)
   - Local file storage

### Phase 2: Advanced Use Cases (Future)

1. **Performance** - Not immediately needed
   - CLI commands typically complete quickly
   - Can add later if performance issues arise

2. **Security Audit** - Not immediately needed
   - No multi-user access in current scope
   - No sensitive operations requiring audit

3. **Business Metrics** - Not immediately needed
   - No business KPIs for personal task management

### Implementation Structure

```text
internal/logging/
├── trace.go          # Tracing implementation
├── errors.go         # Error tracking
├── behavior.go       # User behavior tracking
├── logger.go         # Common logging interface
└── format.go         # Output formatting
```

### Common Requirements

All logging modules will:

- Include mandatory fields: `use_case`, `timestamp`, `trace_id`
- Support JSON output format
- Be controllable via environment variables
- Have minimal performance impact
- Be testable with mock implementations

## Consequences

### Positive

- **Gradual adoption**: Implement only what's needed now
- **Minimal complexity**: Each module is simple and focused
- **No heavy dependencies**: Custom implementation keeps binary small
- **Clear separation**: Each use case has its own module
- **Easy to extend**: Can add more use cases as needed

### Negative

- **Maintenance burden**: We own all implementations
- **Limited initial features**: Starting with basic functionality
- **No ecosystem integration**: Can't use existing log analysis tools immediately
- **Potential duplication**: Some code might be similar across modules

### Neutral

- **Learning curve**: Developers need to understand use-case approach
- **Migration path**: May need to adapt if requirements change
- **Tool compatibility**: May need adapters for standard tools

## Options Considered

### Option 1: Single Unified Logging Library

Use one library (like zap or logrus) for all use cases.

- **Pros**:
  - Single dependency
  - Consistent API
  - Well-tested code
  - Tool ecosystem
- **Cons**:
  - Doesn't naturally fit use-case model
  - May include unnecessary features
  - Harder to customize per use case
- **Evaluation**: Forces use-case model into level-based paradigm

### Option 2: OpenTelemetry for Everything

Use OpenTelemetry SDK for all logging needs.

- **Pros**:
  - Industry standard
  - Covers tracing, metrics, logs
  - Rich ecosystem
- **Cons**:
  - Very heavy for CLI
  - Complex configuration
  - Designed for distributed systems
  - Steep learning curve
- **Evaluation**: Massive overkill for current needs

### Option 3: Phased Custom Implementation (Selected)

Build lightweight modules for immediate needs.

- **Pros**:
  - Start simple, grow as needed
  - Perfect fit for requirements
  - No unnecessary complexity
  - Learn from usage
- **Cons**:
  - More code to maintain
  - No immediate tool support
  - Risk of inconsistency
- **Evaluation**: Best matches CLI constraints and growth path

### Option 4: Mix of Libraries

Use different libraries for different use cases.

- **Pros**:
  - Best tool for each job
  - Leverage existing work
  - Feature-rich options
- **Cons**:
  - Multiple dependencies
  - Inconsistent APIs
  - Complex dependency management
  - Harder to maintain
- **Evaluation**: Complexity outweighs benefits

## Implementation Notes

### Phase 1 Priorities

1. **Tracing** (Week 1)
   - Most useful for debugging
   - Helps understand program flow
   - Easy to add incrementally

2. **Error Tracking** (Week 1)
   - Critical for reliability
   - Helps identify issues
   - Improves error messages

3. **User Behavior** (Week 2)
   - Understand usage patterns
   - Guide future development
   - Optional/opt-in

### Environment Variables

```bash
# Tracing
TABLER_TRACE=1              # Enable tracing
TABLER_TRACE_FORMAT=json    # JSON output

# Error tracking
TABLER_ERROR_STACK=1        # Include stack traces

# User behavior
TABLER_ANALYTICS=1          # Enable usage tracking
TABLER_ANALYTICS_FILE=~/.tabler/analytics.jsonl
```

### Future Considerations

- Keep APIs simple for potential migration
- Document use case for each log point
- Consider batching for performance
- Plan for log rotation/cleanup
