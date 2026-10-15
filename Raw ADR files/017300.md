# ADR-003: Selecting a Data-Access Strategy for PostgreSQL

---

**Status:** Accepted  
**Author:** Ivan Rybachyk  
**Date:** 13.06.2025  

---

Our Weather App has already standardized on PostgreSQL(see [ADR‑001-DB](001-db.md)). 
We now need a data-access layer to:

- Simplify data-access code and reduce boilerplate  
- Ensure type‑safe mapping between Go structs and database tables  
- Leverage the existing Go ecosystem  
- Balance ease of development (especially for prototypes) with performance and maintainability 

## Solution
### Options Considered
- **Raw SQL with** `pgx`
- **sqlc**
- **gorm**

### Evaluation
- **Raw SQL with** `pgx`  
   - *Pros:*  
     - Maximum control over queries
     - Zero abstraction overhead
     - Excellent performance.  
   - *Cons:* 
     - Repetitive boilerplate
     - Manual SQL-writing increases risk of bugs
     - Upon any change in the schema, all SQL queries must be manually updated to match the new structure.

- `sqlc` **(Compile‑time SQL code generation)**  
   - *Pros:* 
     - Strong type safety (queries defined in `.sql` → Go code).
     - No runtime reflection.
     - Easy to audit exact SQL.  
   - *Cons:* 
     - Requires maintaining separate SQL files
     - Less flexible for dynamic query building
     - Steeper onboarding for simple CRUD.

- `gorm` 
   - *Pros:*  
     - Popular and well‑supported in Go.
     - Declarative API for CRUD operations and relationships.
     - Chainable, intuitive query API.
     - Built‑in support for associations, transactions, soft deletes, JSONB, arrays.
   - *Cons:*  
     - Performance overhead due to reflection and dynamic query building.
     - “Magic” conventions can be non‑obvious.
     - Overuse of `AutoMigrate` risks unmanaged schema drift.
     

## Decision

We choose `gorm` as our ORM layer for PostgreSQL.

## Consequences
**Positive**:

- **Less Boilerplate:** CRUD operations and joins expressed declaratively.
- **Rapid Prototyping:** AutoMigrate speeds up schema evolution during early development.
- **Community Support:** Battle‑tested patterns, numerous tutorials, and community plugins.
- **Advanced Features:** JSONB, full‑text search, array types, and soft‑delete support out of the box.

**Negative**:

- **Performance Overhead:** Reflection and query building add latency vs. raw SQL or `sqlc`‑generated code.
- **Hidden Complexity:** Implicit conventions (e.g., table naming, zero-value handling) require discipline and clear code reviews.
- **Migration Discipline:** Relying too heavily on `AutoMigrate` can lead to drift; must integrate with versioned migrations for production.
