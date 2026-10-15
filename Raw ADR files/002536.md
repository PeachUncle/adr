# Decision 005: Database Schema and Model Strategy

**Date:** 2025-11-10  
**Status:** Accepted  
**Deciders:** Project Team

## Context

We must store two distinct types of data for the application:

1. **Application Data**: Dynamic, transactional data created by our app (e.g., user assessments, scraped program lists, custom occupation notes). This data is in the `public` schema.

2. **O*NET Data**: A large, static, read-only dataset that is bulk-loaded and periodically refreshed (e.g., O*NET occupations, skills, interests, and their relationships).

We need a database model strategy that allows our app to use both datasets seamlessly, supports flexible app-specific models (like `Occupation` and `HSSkill`), and does not create conflicts with our Alembic migration tool or the O*NET data refresh process.

## Options Considered

1. **Option A: Single Schema (Monolith)**
   - Description: Store all tables (app data and O*NET data) in the default `public` schema
   - Pros: Simplest setup; no cross-schema joins
   - Cons: Alembic would try to manage the O*NET tables, creating migration chaos. Refreshing the O*NET data (which involves dropping and bulk-loading) would be catastrophic, as it would require deleting all user data due to foreign key constraints

2. **Option B: Alter O*NET Tables (Extension Anti-Pattern)**
   - Description: Load O*NET data into a separate `onet` schema. Add our custom app columns (e.g., `hawaii_notes`) directly to the `onet.occupation_data` table
   - Pros: Keeps all occupation-related data in a single table
   - Cons: Breaks the "read-only" nature of the O*NET data. The `DROP SCHEMA onet` / `BULK LOAD` refresh process would permanently delete all custom application data. Alembic cannot (and should not) be configured to manage tables in the `onet` schema

3. **Option C: Dual-Schema with One-to-One Extension Tables ("Profile" Pattern)**
   - Description: Store O*NET data in a read-only `onet` schema, with models matching the official ERD (e.g., `OnetOccupation`, `ContentModelReference`, `skills`, `interests`). Store app-specific data in the `public` schema. Create app-specific "extension" tables (e.g., `Occupation`, `HSSkill`) in the `public` schema that link to the `onet` tables using a one-to-one (PrimaryKey=ForeignKey) relationship
   - Pros:
     - Clean separation of concerns (app data vs. static data)
     - Alembic only manages the `public` schema, keeping migrations safe and clean
     - O*NET data refreshes are simple (`DROP`/`LOAD` the `onet` schema) and have zero impact on app data
     - App models (`Occupation`, `HSSkill`) are fully flexible and can be modified at any time
   - Cons:
     - Requires slightly more complex cross-schema joins in queries
     - Requires more model definitions upfront

## Decision

We chose **Option C: Dual-Schema with One-to-One Extension Tables**.

This pattern provides the best of all options: the flexibility and extensibility of app-specific models, the safety of clean Alembic migrations, and the robustness of a non-destructive data refresh process for the large O*NET dataset.

## Consequences

- **Positive:**
  - Alembic migrations will be simple, fast, and safe, as they will ignore the `onet` schema
  - The O*NET data refresh process is non-destructive to our application data
  - Our app-specific models (like `Occupation` and `HSSkill`) can be modified freely to add new features

- **Negative:**
  - Requires careful setup of `ForeignKey` definitions to explicitly include the schema name (e.g., `ForeignKey("onet.occupation_data.onet_code")`)

- **Neutral:**
  - Application queries for occupations or skills will frequently require a `joinedload` to fetch the data from both schemas at once

## Implementation Notes

- **When:** Immediately. This is a foundational part of the 001-database-models.md spec

- **Where:**
  - All O*NET data models (`OnetOccupation`, `ContentModelReference`, `Skill`, `Interest`, `ScaleReference`, etc.) must include `__table_args__ = {"schema": "onet"}`
  - All app-specific models (`Occupation`, `HSSkill`, `Program`, `Sector`, `SkillsAssessment`, etc.) will not include a schema argument, defaulting to `public`

- **How:**
  - Models in the `public` schema will link to the `onet` schema using a foreign key that explicitly names the target schema
  - Example (in `public.Occupation`): `onet_code: Mapped[str] = mapped_column(ForeignKey("onet.occupation_data.onet_code"), primary_key=True)`
  - Example (in `public.HSSkill`): `onet_element_id: Mapped[str] = mapped_column(ForeignKey("onet.content_model_reference.element_id"), primary_key=True)`