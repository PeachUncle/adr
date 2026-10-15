# ADR-011: Repository Pattern for Data Access

**Status:** ✅ Accepted  
**Date:** October 2025  
**Context:** Week 1 - Data Access Layer Design

## Context

The application needed a clean abstraction for database operations:

- Hide Entity Framework complexity from business logic
- Enable unit testing without database
- Support multiple database implementations (PostgreSQL now, others later)
- Enforce consistent query patterns
- Enable query optimization centralization

## Decision

Implement **Repository Pattern** with generic base repository and specific repositories per aggregate root.

## Rationale

1. **Abstraction**: Business logic depends on interfaces, not EF Core
2. **Testability**: Easy to mock repositories in unit tests
3. **Consistency**: All data access follows same patterns
4. **Query Optimization**: Centralize Include() and AsNoTracking() logic
5. **DDD Alignment**: Repositories match aggregate roots (Student, Assessment, Question)

## Consequences

### Positive

- Clean separation: Application layer doesn't reference EF Core
- Easy mocking: `Mock<IStudentRepository>` for unit tests
- Centralized queries: All Student queries in StudentRepository
- Easy to add caching layer in repository
- Migration path: Can swap PostgreSQL for SQL Server later

### Negative

- Additional code: IStudentRepository + StudentRepository for each aggregate
- Learning curve: Developers must understand repository pattern
- Temptation to expose IQueryable (breaks abstraction)
- Some duplication: Similar CRUD methods in each repository

## Implementation

**Base Repository Interface**:

```csharp
public interface IRepository<T> where T : class
{
    Task<T?> GetByIdAsync(Guid id);
    Task<IEnumerable<T>> GetAllAsync();
    Task<T> AddAsync(T entity);
    Task UpdateAsync(T entity);
    Task DeleteAsync(Guid id);
}
```

**Domain-Specific Repository**:

```csharp
public interface IStudentRepository : IRepository<Student>
{
    Task<Student?> GetByEmailAsync(string email);
    Task<IEnumerable<Student>> GetBySchoolIdAsync(Guid schoolId);
    Task<StudentProgress> GetProgressAsync(Guid studentId, Subject subject);
}
```

**Implementation with EF Core**:

```csharp
public class StudentRepository : IStudentRepository
{
    private readonly AcademicAssessmentDbContext _context;
    
    public async Task<Student?> GetByIdAsync(Guid id)
    {
        return await _context.Students
            .Include(s => s.Assessments)
            .Include(s => s.Progress)
            .AsNoTracking()
            .FirstOrDefaultAsync(s => s.Id == id);
    }
}
```

## Query Optimization Patterns

**Always use:**

- `AsNoTracking()` for read-only queries
- `Include()` for eager loading (avoid N+1 queries)
- `ProjectTo<DTO>()` for projections (select only needed columns)
- Pagination for large result sets

## Related Decisions

- ADR-005: PostgreSQL as Primary Database
- ADR-070: Entity Framework Core for ORM
- ADR-012: CQRS for Assessment Analytics (separates reads/writes)

## References

- `src/AcademicAssessment.Core/Interfaces/` - Repository interfaces
- `src/AcademicAssessment.Infrastructure/Repositories/` - Implementations
- Commit: `7d65db8` - Database integration
