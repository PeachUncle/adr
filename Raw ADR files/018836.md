# ADR: Deterministic Column Order Sorting in Tapioca DSL Generation

- **Date**: 2025-12-20
- **Status**: Approved
- **Deciders**: Akira Suenami

## Context

The twogate/tapioca fork uses `constant.column_names` to generate keyword arguments when creating RBI files for ActiveRecord model `where` methods.

However, `column_names` depends on the physical column order in the database.

### PostgreSQL Column Order Constraints

PostgreSQL uses an append-only architecture, where `ALTER TABLE ADD COLUMN` can only add new columns at the end of the table. To change the physical order of columns, you must recreate the table and migrate the data.

### Ridgepole and Schemafile

This project uses Ridgepole to manage the schema. In the Schemafile, we want to list columns in a natural order for humans to read (e.g., id, primary columns, timestamps). However, Ridgepole preserves existing columns regardless of the Schemafile's column order and only adds new columns.

### The Root Cause

As a result, the physical column order differs between these environments:

- **DBs with incremental migrations** (most engineers' local environments): Columns are added in the order migrations were executed
- **DBs recreated with `db:reset`** (CI environments or fresh setups): Created at once from `structure.sql`, closer to the Schemafile definition order

This causes generated RBI files to differ between environments even with the same schema, failing diff checks in CI.

## Decision

Monkey patch `ActiveRecord::ModelSchema::ClassMethods#column_names` to sort the return value alphabetically.

```ruby
module TapiocaColumnOrderPatch
  def column_names
    super.sort
  end
end

ActiveRecord::ModelSchema::ClassMethods.prepend(TapiocaColumnOrderPatch)
```

This patch is placed in `sorbet/tapioca/compilers/deterministic_column_order.rb` and loaded as a Tapioca DSL compiler.

## Rationale

### Why we chose monkey patching

1. **Difficult to judge upstream modification**: twogate/tapioca is widely used in other projects, and we were uncertain whether this change would be appropriate. Column order sorting may not be suitable for some use cases
2. **Limited scope of impact**: This patch only affects Tapioca DSL generation and does not affect application runtime (files under `sorbet/tapioca/compilers/` are only loaded during Tapioca execution)
3. **Simple solution**: The problem is solved with just 3 lines of code

### Why we chose alphabetical order

1. **Deterministic**: Guarantees the same order for the same set of columns
2. **Readability**: Makes it easier to find columns when reviewing RBI files
3. **Precedent**: Other frameworks like EF Core have adopted alphabetical sorting for similar issues (Reference: https://github.com/dotnet/efcore/issues/2272)

## Alternatives Considered

### 1. Fix column order in structure.sql

Due to PostgreSQL's append-only architecture, changing existing table column order requires table recreation and data migration. Doing this for all tables is impractical.

### 2. Force all engineers to use db:reset

Always use `db:reset` in local environments. However:
- Development data would be lost
- Time-consuming for environments with large test datasets
- Significant operational burden

### 3. Reproduce incremental migrations in CI

Use `db:migrate` in CI environment as well. However:
- Would significantly increase CI execution time
- Complete reproduction of migration history is difficult

## Impact

- Tapioca RBI generation becomes environment-independent
- RBI file diff checks in CI become stable
- Column order in generated RBI files changes to alphabetical order (requires one-time regeneration of all files)

## Related

- [sorbet/tapioca/compilers/deterministic_column_order.rb](../../../sorbet/tapioca/compilers/deterministic_column_order.rb)
- https://github.com/dotnet/efcore/issues/2272 (Similar issue in EF Core)
