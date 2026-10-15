# Decision: Customizable Decision Types

## Status
Draft | 2024-04-04 | AI Assistant | v1.0

## Context
The current decision type system is rigid with predefined types:
- architectural
- implementation
- security
- performance
- user_experience

This limits flexibility and doesn't accommodate project-specific needs. We need a system that allows:
- Custom decision types
- Project-specific types
- Type hierarchies
- Type metadata
- Type validation

## Analysis

### Current State
- Fixed set of decision types
- No customization options
- Limited flexibility
- Hard-coded validation
- No type metadata
- No inheritance

### Requirements
1. Type Definition
   - Custom type names
   - Type descriptions
   - Type metadata
   - Validation rules

2. Project Configuration
   - Project-specific types
   - Type inheritance
   - Default types
   - Type templates

3. Validation
   - Type validation
   - Metadata validation
   - Required fields
   - Custom rules

4. Integration
   - CLI support
   - API support
   - UI support
   - Export/Import

### Options Considered

1. **Configuration File Based**
   - Pros:
     - Easy to implement
     - Simple to modify
     - Version controlled
   - Cons:
     - Less dynamic
     - Requires restart
     - Limited runtime changes

2. **Database Driven**
   - Pros:
     - Dynamic updates
     - Runtime changes
     - Better scalability
   - Cons:
     - More complex
     - Requires DB setup
     - Additional dependencies

3. **Hybrid Approach**
   - Pros:
     - Best of both worlds
     - Flexible configuration
     - Good performance
   - Cons:
     - More complex
     - Higher maintenance
     - Learning curve

## Decision
We will implement a hybrid approach that combines:
1. Configuration file defaults
2. Runtime customization
3. Project-specific overrides
4. Type inheritance

### Implementation Details

#### Type Definition Format
```yaml
types:
  enhancement:
    description: "Feature enhancements and improvements"
    metadata:
      - impact
      - effort
      - priority
    required_fields:
      - description
      - rationale
    inherits: implementation
    validation:
      - min_description_length: 50
      - require_impact: true

  bugfix:
    description: "Bug fixes and corrections"
    metadata:
      - severity
      - reproduction
      - affected_versions
    required_fields:
      - description
      - steps_to_reproduce
    inherits: implementation
    validation:
      - require_reproduction: true
```

#### Project Configuration
```yaml
project:
  name: "sigfile-cli"
  decision_types:
    - type: enhancement
      enabled: true
      custom_fields:
        - regression_testing
    - type: bugfix
      enabled: true
      custom_validation:
        - require_regression_test
```

#### CLI Integration
```shell
# List available types
sigfile decision types

# Create custom type
sigfile decision type create "enhancement" --description "Feature enhancements" --metadata impact,effort

# Modify existing type
sigfile decision type modify "bugfix" --add-field regression_testing

# Project-specific override
sigfile decision type project "sigfile-cli" --add-type "security_audit"
```

### Affected Files
- `src/scripts/models/decision_type.py`
- `src/scripts/config/decision_types.yaml`
- `src/scripts/cli/decision_commands.py`
- `src/scripts/validation/decision_validator.py`
- `tests/test_decision_types.py`

## Implementation Plan

### Phase 1: Core Types
1. Implement type definition
2. Add basic validation
3. Create CLI commands
4. Add project support

### Phase 2: Advanced Features
1. Add type inheritance
2. Implement metadata
3. Create templates
4. Add validation rules

### Phase 3: Integration
1. Update CLI interface
2. Add API support
3. Create UI components
4. Implement export/import

## Consequences

### Positive
- More flexibility
- Better customization
- Project-specific needs
- Enhanced usability

### Negative
- Implementation complexity
- Learning curve
- Maintenance overhead
- Validation complexity

## Next Steps
1. Create type definition system
2. Implement basic validation
3. Add CLI commands
4. Create project configuration
5. Add type inheritance

## Related Documents
- [Decision Type System](../docs/architecture/decision_types.md)
- [CLI Reference](../docs/guides/cli.md)
- [Validation Rules](../docs/guides/validation.md) 