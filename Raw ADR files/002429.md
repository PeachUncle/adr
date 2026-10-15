# ADR-003: Data Model Design

## Status
Accepted

## Context
Lead Tracker requires a flexible data model that supports:
- Multi-tenant lead management with customizable pipelines
- Task and reminder system with due dates and assignments
- Audit trail for lead changes and activities
- Scalable search and filtering capabilities
- Import/export functionality with data validation

## Decision
We will implement a **Domain-Driven Design (DDD)** approach with EF Core:

### Core Entities:

#### Organization (Tenant Root)
```csharp
public class Organization
{
    public Guid Id { get; set; }
    public string Name { get; set; }
    public string Slug { get; set; } // URL-friendly identifier
    public DateTime CreatedAt { get; set; }
    public bool IsActive { get; set; }
    
    // Navigation properties
    public ICollection<User> Users { get; set; }
    public ICollection<Lead> Leads { get; set; }
    public ICollection<Stage> Stages { get; set; }
}
```

#### User (Identity + Profile)
```csharp
public class User : IdentityUser<Guid>
{
    public string FirstName { get; set; }
    public string LastName { get; set; }
    public Guid OrganizationId { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime? LastLoginAt { get; set; }
    public bool IsActive { get; set; }
    
    // Navigation properties
    public Organization Organization { get; set; }
    public ICollection<Lead> AssignedLeads { get; set; }
    public ICollection<Task> AssignedTasks { get; set; }
}
```

#### Lead (Core Business Entity)
```csharp
public class Lead : TenantEntity, IAuditable
{
    public Guid Id { get; set; }
    public string FirstName { get; set; }
    public string LastName { get; set; }
    public string Email { get; set; }
    public string Phone { get; set; }
    public string Company { get; set; }
    public string Title { get; set; }
    public decimal? Value { get; set; } // Estimated deal value
    public LeadSource Source { get; set; } // Enum: Website, Referral, etc.
    public LeadStatus Status { get; set; } // Enum: New, Qualified, Lost, Won
    
    // Pipeline management
    public Guid StageId { get; set; }
    public Stage Stage { get; set; }
    public Guid? AssignedToId { get; set; }
    public User AssignedTo { get; set; }
    
    // Metadata
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
    public Guid CreatedById { get; set; }
    public User CreatedBy { get; set; }
    
    // Navigation properties
    public ICollection<Task> Tasks { get; set; }
    public ICollection<Note> Notes { get; set; }
    public ICollection<LeadTag> Tags { get; set; }
    public ICollection<Activity> Activities { get; set; }
}
```

#### Stage (Pipeline Configuration)
```csharp
public class Stage : TenantEntity
{
    public Guid Id { get; set; }
    public string Name { get; set; }
    public string Color { get; set; } // Hex color for UI
    public int Order { get; set; } // Display order
    public bool IsActive { get; set; }
    public StageType Type { get; set; } // Enum: Prospect, Qualified, Negotiation, Closed
    
    // Navigation properties
    public ICollection<Lead> Leads { get; set; }
}
```

#### Task (Activities & Reminders)
```csharp
public class Task : TenantEntity
{
    public Guid Id { get; set; }
    public string Title { get; set; }
    public string Description { get; set; }
    public TaskType Type { get; set; } // Enum: Call, Email, Meeting, Follow-up
    public TaskPriority Priority { get; set; } // Enum: Low, Medium, High, Urgent
    public TaskStatus Status { get; set; } // Enum: Pending, In Progress, Completed, Cancelled
    
    // Scheduling
    public DateTime? DueDate { get; set; }
    public DateTime? CompletedAt { get; set; }
    public bool HasReminder { get; set; }
    public DateTime? ReminderAt { get; set; }
    
    // Relationships
    public Guid? LeadId { get; set; }
    public Lead Lead { get; set; }
    public Guid AssignedToId { get; set; }
    public User AssignedTo { get; set; }
    public Guid CreatedById { get; set; }
    public User CreatedBy { get; set; }
    
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
}
```

#### Supporting Entities:
```csharp
// Notes for leads
public class Note : TenantEntity
{
    public Guid Id { get; set; }
    public string Content { get; set; }
    public Guid LeadId { get; set; }
    public Lead Lead { get; set; }
    public Guid CreatedById { get; set; }
    public User CreatedBy { get; set; }
    public DateTime CreatedAt { get; set; }
}

// Tags for categorization
public class Tag : TenantEntity
{
    public Guid Id { get; set; }
    public string Name { get; set; }
    public string Color { get; set; }
    public ICollection<LeadTag> LeadTags { get; set; }
}

// Many-to-many relationship
public class LeadTag
{
    public Guid LeadId { get; set; }
    public Lead Lead { get; set; }
    public Guid TagId { get; set; }
    public Tag Tag { get; set; }
}

// Audit trail for changes
public class Activity : TenantEntity
{
    public Guid Id { get; set; }
    public string Action { get; set; } // "Created", "Updated", "Stage Changed"
    public string Details { get; set; } // JSON with change details
    public Guid LeadId { get; set; }
    public Lead Lead { get; set; }
    public Guid UserId { get; set; }
    public User User { get; set; }
    public DateTime CreatedAt { get; set; }
}
```

## Database Design Principles

### 1. Indexing Strategy:
- **Composite indexes** starting with `org_id` for tenant isolation
- **Covering indexes** for common query patterns
- **Partial indexes** for active records only
- **Full-text search** indexes for name/email/company fields

### 2. Data Types:
- `Guid` for all primary keys (better for distributed systems)
- `DateTime` with UTC storage (consistent timezone handling)
- `decimal` for monetary values (precise calculations)
- `jsonb` for flexible metadata storage

### 3. Constraints:
- **Unique constraints** on email per organization
- **Check constraints** for data validation
- **Foreign key constraints** with cascading rules
- **Not null constraints** on required fields

## Consequences

### Positive:
- **Scalable**: Proper indexing and normalization
- **Flexible**: Easy to add new fields and relationships
- **Auditable**: Complete activity tracking
- **Searchable**: Full-text search capabilities
- **Maintainable**: Clear domain boundaries

### Negative:
- **Complexity**: Multiple tables and relationships
- **Storage**: Audit trail increases data volume
- **Performance**: Complex queries with multiple joins

### Migration Strategy:
1. Create core entities first (Organization, User, Lead)
2. Add pipeline management (Stage)
3. Implement task system (Task, Note)
4. Add tagging and activities (Tag, Activity)
5. Create indexes and optimize performance

## Performance Considerations:
- **Connection pooling** for database connections
- **Query optimization** with proper indexes
- **Caching strategy** for frequently accessed data
- **Pagination** for large result sets
- **Archiving strategy** for old data
