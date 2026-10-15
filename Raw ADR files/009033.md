# ADR-070: Entity Framework Core for ORM

**Status:** ✅ Accepted  
**Date:** October 2025  
**Context:** Object-Relational Mapping Selection

## Context

The application needed an ORM to:

- Map C# classes to database tables
- Generate and execute SQL queries
- Handle migrations for schema changes
- Support LINQ queries
- Manage relationships and navigation properties
- Integrate with PostgreSQL

Options:

- Entity Framework Core (Microsoft, feature-rich)
- Dapper (micro-ORM, high performance)
- NHibernate (mature, complex)
- Raw ADO.NET (no abstraction, manual SQL)

## Decision

Selected **Entity Framework Core 8.0** with **Npgsql provider** for PostgreSQL.

## Rationale

1. **Full ORM**: Complete object-relational mapping (vs Dapper's micro-ORM)
2. **LINQ Support**: Type-safe queries with IntelliSense
3. **Migrations**: Code-first migrations for schema evolution
4. **Change Tracking**: Automatic detection of entity changes
5. **Navigation Properties**: Automatic join generation
6. **PostgreSQL Integration**: Excellent Npgsql provider
7. **.NET Native**: First-class Microsoft support

## Consequences

### Positive

- **Productivity**: LINQ queries instead of raw SQL
- **Type safety**: Compile-time query validation
- **Migrations**: Easy schema evolution (`dotnet ef migrations add`)
- **Relationships**: Automatic join handling via Include()
- **Testing**: In-memory database for unit tests

### Negative

- **Performance overhead**: ~10-15% slower than Dapper
- **Learning curve**: Developers must understand EF patterns
- **N+1 queries**: Easy to accidentally create (use Include())
- **Complex queries**: Sometimes raw SQL is simpler
- **Memory usage**: Change tracking adds overhead

### Risks Mitigated

- Used `AsNoTracking()` for read-only queries (60% of queries)
- Explicit `Include()` for eager loading (avoid N+1)
- Raw SQL for complex analytics queries
- Query performance logging (detect slow queries)
- Pagination for large result sets

## Implementation

**DbContext Definition** (src/AcademicAssessment.Infrastructure/Data/AcademicAssessmentDbContext.cs):

```csharp
public class AcademicAssessmentDbContext : DbContext
{
    public DbSet<Student> Students { get; set; }
    public DbSet<Assessment> Assessments { get; set; }
    public DbSet<Question> Questions { get; set; }
    public DbSet<Response> Responses { get; set; }
    public DbSet<LearningObjective> LearningObjectives { get; set; }
    
    public AcademicAssessmentDbContext(DbContextOptions<AcademicAssessmentDbContext> options)
        : base(options)
    {
    }
    
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        // Configure entities
        modelBuilder.Entity<Student>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Name).IsRequired().HasMaxLength(200);
            entity.Property(e => e.Email).IsRequired().HasMaxLength(200);
            entity.HasIndex(e => e.Email).IsUnique();
            
            // Relationships
            entity.HasMany(e => e.Assessments)
                .WithOne(e => e.Student)
                .HasForeignKey(e => e.StudentId)
                .OnDelete(DeleteBehavior.Cascade);
        });
        
        modelBuilder.Entity<Assessment>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Subject).IsRequired();
            entity.Property(e => e.Grade).IsRequired();
            
            // JSON column for metadata
            entity.Property(e => e.Metadata)
                .HasColumnType("jsonb");
        });
        
        // Apply configurations from separate files
        modelBuilder.ApplyConfigurationsFromAssembly(typeof(AcademicAssessmentDbContext).Assembly);
    }
}
```

**Repository Example**:

```csharp
public class StudentRepository : IStudentRepository
{
    private readonly AcademicAssessmentDbContext _context;
    
    public async Task<Student?> GetByIdAsync(Guid id)
    {
        return await _context.Students
            .Include(s => s.Assessments)
                .ThenInclude(a => a.Responses)
            .Include(s => s.Progress)
            .AsNoTracking()  // Read-only, no change tracking
            .FirstOrDefaultAsync(s => s.Id == id);
    }
    
    public async Task<IEnumerable<Student>> GetBySchoolIdAsync(Guid schoolId)
    {
        return await _context.Students
            .Where(s => s.SchoolId == schoolId)
            .OrderBy(s => s.Name)
            .AsNoTracking()
            .ToListAsync();
    }
    
    public async Task<Student> AddAsync(Student student)
    {
        _context.Students.Add(student);
        await _context.SaveChangesAsync();
        return student;
    }
}
```

**Migrations**:

```bash
# Create migration
dotnet ef migrations add InitialCreate --project src/AcademicAssessment.Infrastructure

# Apply migration
dotnet ef database update --project src/AcademicAssessment.Infrastructure

# Rollback migration
dotnet ef database update PreviousMigration --project src/AcademicAssessment.Infrastructure

# Generate SQL script
dotnet ef migrations script --project src/AcademicAssessment.Infrastructure -o migrations.sql
```

**Service Registration**:

```csharp
services.AddDbContext<AcademicAssessmentDbContext>(options =>
    options.UseNpgsql(
        configuration.GetConnectionString("edumind"),
        npgsqlOptions => npgsqlOptions
            .EnableRetryOnFailure(maxRetryCount: 3, maxRetryDelay: TimeSpan.FromSeconds(5), errorCodesToAdd: null)
            .CommandTimeout(30)
            .MigrationsAssembly("AcademicAssessment.Infrastructure")));
```

## Performance Optimization Patterns

**1. AsNoTracking() for Read-Only Queries**:

```csharp
// ✅ Good (60% faster for read-only)
var students = await _context.Students
    .AsNoTracking()
    .ToListAsync();

// ❌ Bad (unnecessary change tracking)
var students = await _context.Students.ToListAsync();
```

**2. Explicit Include() for Eager Loading**:

```csharp
// ✅ Good (1 query with joins)
var assessment = await _context.Assessments
    .Include(a => a.Questions)
    .Include(a => a.Responses)
    .FirstOrDefaultAsync(a => a.Id == id);

// ❌ Bad (N+1 queries)
var assessment = await _context.Assessments.FindAsync(id);
var questions = assessment.Questions; // Lazy load = extra query
```

**3. Pagination for Large Result Sets**:

```csharp
// ✅ Good (only 20 rows)
var students = await _context.Students
    .OrderBy(s => s.Name)
    .Skip((page - 1) * 20)
    .Take(20)
    .ToListAsync();

// ❌ Bad (loads all rows)
var students = await _context.Students.ToListAsync();
```

**4. Raw SQL for Complex Analytics**:

```csharp
// When LINQ is too complex or slow
var stats = await _context.Database
    .SqlQueryRaw<StudentStats>(
        @"SELECT s.id, s.name, AVG(r.score) as average_score
          FROM students s
          JOIN assessments a ON a.student_id = s.id
          JOIN responses r ON r.assessment_id = a.id
          GROUP BY s.id, s.name
          HAVING COUNT(a.id) > 5")
    .ToListAsync();
```

## Database Schema

**Tables** (17 total):

- Students (student data)
- Assessments (assessment metadata)
- Questions (question bank)
- Responses (student answers)
- LearningObjectives (curriculum standards)
- StudentProgress (progress tracking)
- Schools, Classes, Teachers (multi-tenant)

**Relationships**:

- Student → Assessments (1:N)
- Assessment → Responses (1:N)
- Question → Responses (1:N)
- School → Students (1:N)
- Class → Students (M:N via junction table)

## Migration Strategy

**Development**:

- Create migrations locally
- Apply to local PostgreSQL (via Aspire)
- Test migrations before committing

**Production**:

- Generate SQL script from migrations
- Review script in PR
- Apply during deployment (automated via azd)
- Backup database before migration

## Testing with In-Memory Database

```csharp
public class StudentRepositoryTests
{
    private AcademicAssessmentDbContext CreateInMemoryContext()
    {
        var options = new DbContextOptionsBuilder<AcademicAssessmentDbContext>()
            .UseInMemoryDatabase(databaseName: Guid.NewGuid().ToString())
            .Options;
        
        return new AcademicAssessmentDbContext(options);
    }
    
    [Fact]
    public async Task AddStudent_ValidStudent_SavesSuccessfully()
    {
        using var context = CreateInMemoryContext();
        var repository = new StudentRepository(context);
        
        var student = new Student { Name = "Test", Email = "test@example.com" };
        
        await repository.AddAsync(student);
        
        var saved = await repository.GetByIdAsync(student.Id);
        Assert.NotNull(saved);
    }
}
```

## Alternative Considered: Dapper

**Rejected because:**

- Manual SQL writing (less productive)
- No automatic migrations
- No LINQ support
- Would need hand-written relationship loading
- Performance gain (10-15%) not worth productivity loss

**When to use Dapper**: Complex read-only queries where EF LINQ is insufficient.

## Related Decisions

- ADR-005: PostgreSQL as Primary Database
- ADR-011: Repository Pattern for Data Access
- ADR-071: Database Migration Strategy

## References

- `src/AcademicAssessment.Infrastructure/Data/` - DbContext and configurations
- `src/AcademicAssessment.Infrastructure/Migrations/` - EF migrations
- Commit: `7d65db8` - "feat: Implement database integration and JWT authentication"
- Commit: `cd5e46c` - "Add EF Core design-time factory and load demo base data"
