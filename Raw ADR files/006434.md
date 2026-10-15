# ADR-001: Use Ash Framework

## Status

Accepted

## Date

2024-12-30

## Context

We need an application layer that:
- Reduces boilerplate for CRUD operations
- Provides declarative authorization
- Generates APIs (GraphQL, REST) from resources
- Supports state machines for workflow management
- Is AI-friendly (declarative, consistent patterns)

### Options Considered

1. **Vanilla Phoenix + Ecto** — Maximum flexibility, most boilerplate
2. **Ash Framework** — Declarative resources, batteries included
3. **Commanded (CQRS/ES)** — Event sourcing, complex architecture

## Decision

Use **Ash Framework 3.x** as the application layer.

## Rationale

| Factor | Ash | Vanilla Phoenix | Commanded |
|--------|-----|-----------------|-----------|
| Boilerplate | Low | High | Medium |
| Learning curve | Medium | Low | High |
| Authorization | Built-in (policies) | DIY | DIY |
| API generation | AshGraphql, AshJsonApi | Manual Absinthe | DIY |
| State machines | AshStateMachine | DIY | Built-in |
| Audit logging | AshPaperTrail | DIY | Built-in |
| AI code generation | Excellent (declarative) | Good | Medium |

### Key Benefits

1. **Declarative resources** — AI generates consistent, valid code
2. **Built-in authorization** — Policies are co-located with resources
3. **Extension ecosystem** — GraphQL, state machines, audit trails
4. **Consistent patterns** — Every resource follows the same structure

## Consequences

### Positive

- Less code to write and maintain
- Authorization is auditable (policies in code)
- GraphQL API generated from resources
- Property-based testing aligns with declarative nature

### Negative

- Team needs to learn Ash patterns
- Debugging can be harder (abstraction layers)
- Smaller community than vanilla Phoenix
- Some advanced Ecto patterns require workarounds

### Mitigations

- Document patterns in CONVENTIONS.md
- Use Ash's built-in debugging tools
- Keep resources simple, extract complex logic to plain modules
- Fallback to raw Ecto available when needed

## References

- [Ash Documentation](https://hexdocs.pm/ash)
- [Ash Framework GitHub](https://github.com/ash-project/ash)
- [Alembic (company behind Ash)](https://alembic.com.au)
