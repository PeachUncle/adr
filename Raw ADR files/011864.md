# ADR: Single Table Inheritance for Polymorphic Domain Entities

Status
- Superseded (see ADR 20251020-root-group-type-calculation)

Context
- The domain model contains polymorphic entities (groups and criteria) with two type variants: Average and Weighted
- Type variants differ minimally - only by presence of weight_basis_points field
- Groups form hierarchical tree structures with parent-child relationships
- Forms are loaded as complete aggregates requiring all related data
- Future extensions may introduce additional type variants with unique characteristics

Decision
- Single table design remains, but the original requirement to include `group_type` and `criterion_type` discriminators has been deprecated
- Root form configuration (`root_group_type`) drives calculation strategy for every nested element
- Database schema no longer persists redundant discriminators alongside groups or criteria
- Nullable `weight_basis_points` fields remain constrained by the root calculation mode

Scope
- Infrastructure layer database schema design
- Applies to `form_groups`, `form_criteria`, and related polymorphic entities
- Does not affect domain model architecture (interfaces and implementations remain unchanged)

Rationale
- **Minimal type differences**: Average and Weighted variants differ only by one field, making separate tables unnecessary
- **Hierarchical queries**: Self-referencing parent_id relationships are simpler with single table
- **Unified ordering**: order_index must work across types within same context
- **Performance**: Loading complete form aggregates requires fewer JOINs
- **Simplicity**: Queries, migrations, and repository code remain straightforward
- **Type safety**: Calculation mode is centralized at the form root ensuring a single source of truth

Consequences
- Weight columns remain nullable and are enforced by application services based on `root_group_type`
- Database-level validation for redundant discriminators is no longer required
- Repository implementations no longer need to project or parse per-node calculation modes
- Adding new types expands the enumeration at the form level only

Alternatives Considered
- **Table Per Type (TPT)**: Separate tables for Average and Weighted variants — rejected due to complexity in hierarchical queries, difficulty maintaining order across types, and performance overhead from UNION operations
- **Table Per Hierarchy with JSONB for all differences**: Store all type-specific data in JSONB column — rejected for initial implementation as single nullable column is simpler; remains option for future complex types
- **Class Table Inheritance**: Base table with type-specific child tables — rejected due to foreign key complexity and JOIN overhead for aggregate loading

References
- Martin Fowler - Patterns of Enterprise Application Architecture (Single Table Inheritance pattern)
- Database schema scripts under `src/management/Infrastructure/Database/Scripts`
