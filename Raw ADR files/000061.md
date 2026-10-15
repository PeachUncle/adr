# ADR-002: Database Schema Design

**Status:** Accepted  
**Date:** 2023-07-12  
**Deciders:** Development Team, Database Architect  
**Consulted:** Technical Advisors  
**Informed:** Project Stakeholders  

## Context and Problem Statement

We need to design a database schema for the 100 Days Challenge Tracker application that efficiently stores user data, challenges, and projects while supporting the application's core functionality.

### Problem
Designing a database schema that balances flexibility, performance, and simplicity for tracking 100-day coding challenges and associated projects.

### Goals
- Support core entities: users, challenges, and projects
- Enable efficient querying for dashboard analytics
- Allow for future extension of the data model
- Maintain data integrity and relationships

### Non-Goals
- Supporting complex reporting (can be added later)
- Real-time collaboration features
- Handling extremely large datasets (beyond typical user needs)

### Success Criteria
- Queries complete in < 100ms for typical operations
- Schema supports all core application features
- Data relationships are properly maintained
- Schema can evolve without major migrations

## Decision Drivers

### Technical Drivers
- MongoDB's document-oriented nature
- Query performance requirements
- Data relationship complexity
- Future extensibility needs

### Business Drivers
- Need to support core application features
- Timeline constraints for initial release
- Maintainability by a small development team

## Considered Options

### Option 1: Normalized Schema with References
**Description:** Create separate collections for users, challenges, and projects with references between them.

**Pros:**
- ✅ Clear separation of concerns
- ✅ Reduced data duplication
- ✅ Easier to maintain data integrity
- ✅ Simpler individual documents

**Cons:**
- ❌ Requires multiple queries for related data
- ❌ More complex aggregation for analytics
- ❌ Slightly higher query overhead

**Cost/Effort:** Medium
**Risk:** Low

### Option 2: Embedded Documents Approach
**Description:** Embed projects directly within challenge documents, and challenges within user documents.

**Pros:**
- ✅ Faster retrieval of complete data (single query)
- ✅ Simpler queries for common operations
- ✅ Better locality of data

**Cons:**
- ❌ Document size could grow very large
- ❌ Difficult to query embedded data independently
- ❌ Potential for hitting document size limits
- ❌ More complex updates for nested data

**Cost/Effort:** Low
**Risk:** Medium

### Option 3: Hybrid Approach
**Description:** Separate collections for users, challenges, and projects, with selective embedding of frequently accessed data.

**Pros:**
- ✅ Balance between normalization and performance
- ✅ Flexibility to optimize specific queries
- ✅ Avoids document size limitations
- ✅ Maintains clear data boundaries

**Cons:**
- ❌ More complex schema design
- ❌ Requires careful management of duplicated data
- ❌ Potential for data inconsistency if not managed properly

**Cost/Effort:** Medium
**Risk:** Low

## Decision Outcome

### Chosen Option
**Selected:** Option 3: Hybrid Approach

### Rationale
The decision was made based on:

1. **Performance**: The hybrid approach provides good query performance for common operations while avoiding the limitations of fully embedded documents.
2. **Flexibility**: Separate collections allow for independent querying and updating of entities.
3. **Scalability**: This approach scales better as users create more challenges and projects.
4. **Maintainability**: Clear boundaries between entities make the schema easier to understand and maintain.

### Confidence Level
**Confidence:** High

The hybrid approach is a well-established pattern for MongoDB applications and addresses the specific needs of our application.

### Expected Outcomes
**Short-term (0-3 months):**
- Efficient queries for dashboard and challenge views
- Clear data structure for development team
- Support for all core application features

**Medium-term (3-12 months):**
- Ability to add new fields and features without major schema changes
- Consistent performance as data volume grows
- Simplified aggregation for analytics features

**Long-term (12+ months):**
- Schema can evolve to support new features
- Maintainable data structure as application grows
- Ability to optimize specific queries as needed

## Consequences

### Positive Consequences
- ✅ Good query performance for common operations
- ✅ Clear separation of entities
- ✅ Flexibility for future extensions
- ✅ Avoids MongoDB document size limitations

### Negative Consequences
- ⚠️ Some data duplication for frequently accessed fields
- ⚠️ Need to maintain consistency for duplicated data
- ⚠️ Slightly more complex schema design

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Data inconsistency | Medium | Medium | Implement update logic to maintain consistency |
| Query performance issues | Low | Medium | Index key fields, monitor and optimize queries |
| Schema evolution challenges | Medium | Low | Design with extensibility in mind, use flexible schema |

## Implementation

### Schema Design

#### Users Collection
```javascript
{
  id: "string", // UUID
  email: "string",
  name: "string",
  picture: "string", // URL to profile picture
  created_at: Date
}
```

#### Sessions Collection
```javascript
{
  id: "string", // UUID
  user_id: "string", // Reference to Users
  session_token: "string",
  expires_at: Date,
  created_at: Date
}
```

#### Challenges Collection
```javascript
{
  id: "string", // UUID
  user_id: "string", // Reference to Users
  title: "string",
  description: "string",
  goals: ["string"],
  rules: ["string"],
  duration_days: Number,
  start_date: Date,
  end_date: Date,
  created_at: Date,
  updated_at: Date,
  // Denormalized data for quick access
  project_count: Number,
  completed_project_count: Number
}
```

#### Projects Collection
```javascript
{
  id: "string", // UUID
  challenge_id: "string", // Reference to Challenges
  user_id: "string", // Reference to Users
  title: "string",
  description: "string",
  repository_url: "string",
  demo_url: "string",
  tech_stack: ["string"],
  status: "string", // "not_started", "in_progress", "completed"
  progress_percentage: Number,
  created_at: Date,
  updated_at: Date,
  // URL monitoring data
  url_status: {
    repository: {
      url: "string",
      status: "string", // "online", "offline", "unknown"
      last_checked: Date
    },
    demo: {
      url: "string",
      status: "string", // "online", "offline", "unknown"
      last_checked: Date
    }
  },
  last_url_check: Date
}
```

### Action Items
- [ ] Create MongoDB schema validation rules - **Owner:** Backend Dev - **Due:** Week 1
- [ ] Implement data access layer with TypeScript interfaces - **Owner:** Backend Dev - **Due:** Week 2
- [ ] Create indexes for common queries - **Owner:** Database Architect - **Due:** Week 1
- [ ] Implement data consistency logic - **Owner:** Backend Dev - **Due:** Week 2

### Dependencies
- MongoDB Atlas cluster setup
- TypeScript type definitions

## Measurement and Validation

### Success Metrics
| Metric | Baseline | Target | Measurement Method |
|--------|----------|--------|--------------------|
| Query Response Time | N/A | < 100ms | MongoDB performance monitoring |
| Write Operation Time | N/A | < 50ms | MongoDB performance monitoring |
| Data Consistency | N/A | 100% | Automated tests |

### Validation Criteria
- [ ] All queries complete within target response times
- [ ] Data consistency is maintained across collections
- [ ] Schema supports all required application features
- [ ] Indexes are properly configured for common queries

### Review Schedule
- **Initial Review:** 30 days after implementation
- **Follow-up Review:** 90 days after implementation
- **Final Review:** 6 months after implementation

---

**ADR Template Version:** 1.0  
**Created:** 2023-07-12  
**Last Modified:** 2023-07-12  
**Next Review:** 2024-01-12