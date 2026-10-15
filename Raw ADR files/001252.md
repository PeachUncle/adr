# ADR-006: Soft Delete Implementation for Data Safety

## Status
Accepted

## Date
2025-01-29

## Context
In multi-tenant applications and production systems, accidentally deleting critical data can have severe business consequences. Traditional hard deletes remove data permanently from the database, making recovery impossible without restoring from backups. This poses significant risks, especially when dealing with tenant data or when bulk operations might affect multiple records.

Our application manages People and Roles data that could be critical for business operations. Accidental deletion of roles could orphan user assignments, and deleting people records could result in loss of important relationship data.

## Decision
We will implement soft delete functionality across all domain entities as our first line of defense against accidental data loss.

### Implementation Details:
1. **ISoftDeletable Interface**: All entities will implement this interface providing:
   - `IsDeleted`: Boolean flag indicating if the record is soft deleted
   - `DeletedAt`: Timestamp when the record was marked as deleted
   - `DeletedBy`: Track who/what performed the deletion
   - `SoftDelete()`: Method to mark entity as deleted
   - `Restore()`: Method to restore soft deleted entities

2. **BaseEntity Integration**: The `BaseEntity` class will implement `ISoftDeletable` so all entities inheriting from it automatically support soft deletes.

3. **Repository Pattern**: All repository delete operations will use soft delete by default:
   - `DeleteAsync()` methods will call `entity.SoftDelete()`
   - Query methods will automatically filter out soft deleted records
   - Add explicit methods for hard delete when absolutely necessary

4. **Database Schema**: Soft delete columns will be added via EF migrations:
   ```sql
   ALTER TABLE [EntityName] ADD IsDeleted bit NOT NULL DEFAULT 0
   ALTER TABLE [EntityName] ADD DeletedAt datetime2 NULL
   ALTER TABLE [EntityName] ADD DeletedBy nvarchar(255) NULL
   ```

5. **Query Filtering**: EF Core global query filters will automatically exclude soft deleted records from all queries unless explicitly included.

## Consequences

### Positive:
- **Data Safety**: Accidental deletions can be easily recovered
- **Audit Trail**: Complete history of when and who deleted records
- **Tenant Protection**: Critical safeguard for multi-tenant data
- **Regulatory Compliance**: Supports data retention requirements
- **Debugging**: Easier to investigate data issues and user actions
- **Rollback Capability**: Quick restoration without database restores

### Negative:
- **Storage Overhead**: Deleted records continue consuming database space
- **Query Complexity**: Need to handle soft deleted records in queries
- **Migration Complexity**: Existing data needs migration to add new columns
- **Performance Impact**: Additional WHERE clauses on all queries
- **Cleanup Strategy**: Need periodic cleanup processes for old deleted records

### Mitigation Strategies:
1. **Indexing**: Add indexes on `IsDeleted` column for query performance
2. **Cleanup Jobs**: Implement scheduled cleanup for records deleted > 90 days
3. **Hard Delete API**: Provide admin-only endpoints for permanent deletion when needed
4. **Monitoring**: Track soft delete storage usage and performance impact

## Implementation Status
- [x] Create `ISoftDeletable` interface
- [x] Update `BaseEntity` to implement soft deletes
- [x] Add soft delete support to `User` entity
- [ ] Update all repository implementations
- [ ] Add EF Core global query filters
- [ ] Create database migration
- [ ] Update command handlers to use soft delete
- [ ] Add restore functionality to admin interfaces
- [ ] Implement cleanup job for old deleted records

## Related Decisions
- This affects all CRUD operations and query patterns
- Integrates with existing concurrency control (RowVersion)
- Complements audit trail functionality in BaseEntity
- May require updates to caching strategies

## Notes
This implementation prioritizes data safety over storage efficiency, which aligns with our tenant protection requirements. The additional storage and query overhead is acceptable given the business value of preventing accidental data loss.