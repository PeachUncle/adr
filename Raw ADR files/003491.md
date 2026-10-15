Use Shadow Foreign Keys Instead of Cross-Namespace Entity References
---
Date: 24-12-2025

###  Problem
Due to poor initial design decisions that violated the "no cross-namespace class references" rule, the EmployeeDbContext was directly referencing `User.Data.User` entity in foreign key relationships:

```csharp
builder.HasOne<User.Data.User>()
    .WithMany()
    .HasForeignKey(e => e.CreatedBy)
    .HasPrincipalKey(u => u.Id)
    .OnDelete(DeleteBehavior.Cascade);
```

This caused Entity Framework to:
1. Take control of the User table in EmployeeDbContext migrations
2. Rename User table columns to match class property names (ignoring UserDbContext configurations)
3. Create duplicate table definitions with conflicting schemas
4. Break the separation of concerns between different bounded contexts

The EmployeeDbContext was overriding UserDbContext's table configurations, leading to:
- `users` table being renamed to `User`
- Column names changing from snake_case to PascalCase
- Migration conflicts between contexts

### Decision
Override the cross-namespace restriction design and implement shadow foreign keys instead of direct entity references.

### Implementation
- Remove all direct entity references to `User.Data.User`, `User.Data.Plan`, and `User.Data.UserRole` from EmployeeDbContext
- Use shadow foreign keys (integer properties without EF relationships)
- **No database-level foreign key constraints** - sacrificing referential integrity for architectural cleanliness
- Keep foreign key properties (like `CreatedBy`) as simple integer fields

## Consequences

### Positive
- **Clean separation**: Each DbContext manages only its own entities
- **No schema conflicts**: UserDbContext maintains full control over User table schema
- **Better maintainability**: Changes to User entity don't affect Employee migrations
- **Scalable design**: Keeps slices separate and loose coupled

### Negative
- **No navigation properties**: Cannot use `employee.CreatedByUser` navigation
- **Manual relationship handling**: Must manually join tables when needed
- **Less type safety**: Foreign key values are not validated at EF level
- **No referential integrity**: Database won't enforce FK constraints automatically
- **Manual cascade operations**: Must handle cascade deletes in application code
- **Orphaned records risk**: No database-level prevention of orphaned entities
- **Complex joins**: Relational operations require manual SQL joins or multiple queries

## Notes
This decision prioritizes architectural cleanliness and prevents migration conflicts over referential integrity and convenience features. The trade-off sacrifices database-level data consistency for cleaner bounded context separation. Application-level validation and cascade handling will be required to maintain data integrity.