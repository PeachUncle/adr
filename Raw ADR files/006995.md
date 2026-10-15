---
id: "001"
title: Schema-First Contract-Based Development
created: 2025-11-27
status: accepted
scope: process
tags: [schema, contract, development-order, phase]
related: []
supersedes: null
superseded-by: null
---

# ADR-001: Schema-First Contract-Based Development

## Context

We need to decide the order of creating template files for the Agent Orchestration Framework. The options considered were:

1. **Horizontal approach**: Complete all files in one layer before moving to the next (all Constitutions → all Workers → all Schemas → all Gates)
2. **Vertical approach**: Complete one workflow end-to-end (Specifier workflow complete → Implementer workflow → ...)
3. **MVP approach**: Create minimum viable set first, test, then expand
4. **Schema-first approach**: Define schemas as contracts first, then create documents that conform to them

### Key Considerations

- **Token efficiency**: Constitution + Worker Constitution should be ~1,300 tokens total
- **Consistency**: All documents must follow the same front matter structure
- **Validation**: Documentation Gate validates documents against schemas
- **Maintainability**: Changes to document structure should be caught early

## Decision

We will use **Schema-First Contract-Based Development**.

### Implementation Order

```
Phase 1: Schema Definition (Contracts)
├── common.schema.md
├── constitution.schema.md
├── gate.schema.md
├── aspect.schema.md
├── feature.schema.md
└── artifact.schema.md

Phase 2: Constitution (Following Schema)
├── base.md
└── workers/*.md

Phase 3: Workers (Referencing Constitution)
└── .claude/agents/*.md

Phase 4: Gates (Using Schemas for Validation)
└── gates/**/*.md

Phase 5: Tooling
├── init.sh
└── commands/*.md
```

## Rationale

1. **Schema as Contract**: Schemas define the "contract" that all documents must fulfill. Creating them first ensures consistency from the start.

2. **Early Validation**: With schemas defined first, we can validate every subsequent document immediately using Documentation Gate.

3. **Reduced Rework**: If we create documents first and schemas later, we risk having to modify all documents when schema issues are discovered.

4. **Token Budget Enforcement**: Schemas can include guidelines for token limits, ensuring Constitution files stay within the ~500-800 token budget.

5. **Clear Reference**: When writing Constitution or Gate files, authors have a clear reference for required fields and valid values.

## Consequences

### Positive

- All documents are validated from creation
- Consistent structure across all document types
- Schema changes are caught before documents are created
- Clear contract for contributors

### Negative

- More upfront work before seeing "working" components
- Schema design errors affect all subsequent work
- May need to iterate on schemas based on practical usage

### Mitigations

- Keep schemas minimal initially (only required fields)
- Review schemas carefully before proceeding to Phase 2
- Be prepared to update schemas and documents together if needed

## Related

- `templates/blueprint/front-matters/README.md` - FrontMatter definitions documentation
- `templates/blueprint/gates/documentation/README.md` - Documentation Gate that uses schemas
- `README.md` - Global Rules section defines base schema fields
