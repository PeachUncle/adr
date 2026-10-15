# ADR-002: Assessments Entity Design and Implementation

**Date**: 2025-01-02  
**Status**: Accepted  
**Deciders**: Development Team  
**Consulted**: Product Team, UX Team  
**Informed**: Engineering Team  

## Context

The Alan Hirsch Digital Platform requires a comprehensive assessment system to support various ministry assessment frameworks, including APEST (Apostolic, Prophetic, Evangelistic, Shepherding, Teaching), MDNA (Missional DNA), and other leadership and spiritual gift assessments.

### Requirements

1. **Multiple Assessment Types**: Support for various assessment frameworks
2. **Question Management**: Flexible question bank with different question types
3. **User Progress Tracking**: Individual user assessment progress and results
4. **APEST Integration**: Specific support for APEST dimension scoring
5. **Cultural Adaptation**: Support for different cultural contexts
6. **Research Validation**: Track validity and reliability scores
7. **Privacy and Security**: Ensure user data privacy and security
8. **Scalability**: Support for large numbers of users and assessments

### Constraints

- Must integrate with existing Supabase infrastructure
- Must support Row Level Security (RLS) for data privacy
- Must be compatible with Next.js and TypeScript
- Must follow existing codebase patterns and conventions

## Decision

We will implement a comprehensive assessment system using a four-table design with the following components:

### Database Schema

**Core Tables**:
1. `assessments` - Assessment definitions and metadata
2. `assessment_questions` - Question bank with APEST dimension mapping
3. `user_assessments` - Individual user assessment results and scores
4. `assessment_responses` - Individual question responses

**Key Design Decisions**:

#### 1. Assessment Types as Enums
- **Decision**: Use database enums for assessment types
- **Rationale**: Ensures data consistency and type safety
- **Alternatives Considered**: 
  - Separate tables per assessment type (rejected - too complex)
  - JSON field for assessment type (rejected - no validation)

#### 2. APEST Dimension Integration
- **Decision**: Include APEST dimension fields in both questions and user assessments
- **Rationale**: APEST is a core framework that needs dedicated support
- **Alternatives Considered**:
  - Generic dimension system (rejected - too abstract)
  - Separate APEST table (rejected - unnecessary complexity)

#### 3. Cultural Adaptation Support
- **Decision**: Include cultural adaptation fields in assessments
- **Rationale**: Ministry assessments need cultural context awareness
- **Alternatives Considered**:
  - Separate cultural adaptation table (rejected - over-engineering)
  - No cultural support (rejected - requirement)

#### 4. JSONB for Flexible Data
- **Decision**: Use JSONB for answer options, scores, and recommendations
- **Rationale**: Provides flexibility for different question types and scoring methods
- **Alternatives Considered**:
  - Separate tables for each data type (rejected - too complex)
  - Text fields (rejected - no structure)

#### 5. Row Level Security (RLS)
- **Decision**: Implement comprehensive RLS policies
- **Rationale**: Ensures user data privacy and security
- **Alternatives Considered**:
  - Application-level security only (rejected - insufficient)
  - No security (rejected - unacceptable)

### API Design

**Request/Response DTOs**:
- Separate DTOs for input validation and output formatting
- UI-friendly computed fields (e.g., `isPublished`, `completionTimeText`)
- Type-safe validation with Zod schemas

**API Endpoints**:
- RESTful design following existing patterns
- Comprehensive input/output validation
- Consistent error handling

### Code Architecture

**Layers**:
1. **Database Layer**: Drizzle ORM with type-safe queries
2. **Mapper Layer**: DB rows → DTOs with computed fields
3. **API Layer**: Request/response validation and business logic
4. **Hook Layer**: React hooks with standard return shapes
5. **Form Layer**: React Hook Form with Zod validation

**Key Patterns**:
- DTOs only cross API boundaries (never raw DB rows)
- Mapper functions handle null coalescing and computed fields
- Standard hook return shapes (`{ data, loading, error }`)
- Comprehensive input/output validation

## Consequences

### Positive

1. **Type Safety**: Full TypeScript support with compile-time validation
2. **Data Integrity**: Database constraints and RLS policies ensure data quality
3. **Flexibility**: JSONB fields allow for different question types and scoring methods
4. **Scalability**: Efficient queries and indexing support large datasets
5. **Security**: RLS policies ensure user data privacy
6. **Maintainability**: Clear separation of concerns and consistent patterns
7. **APEST Integration**: Dedicated support for the core ministry framework
8. **Cultural Awareness**: Built-in support for different cultural contexts

### Negative

1. **Complexity**: Four-table design adds some complexity
2. **JSONB Overhead**: JSONB fields require careful validation and indexing
3. **Migration Complexity**: Schema changes require careful migration planning
4. **Learning Curve**: Team needs to understand the assessment domain

### Risks

1. **Performance**: Complex queries with JSONB fields may impact performance
2. **Data Consistency**: JSONB fields require careful validation
3. **Migration Issues**: Schema changes could break existing data
4. **Security Gaps**: RLS policies must be carefully maintained

### Mitigation Strategies

1. **Performance**: 
   - Index frequently queried columns
   - Use materialized views for complex aggregations
   - Monitor query performance

2. **Data Consistency**:
   - Validate JSONB structure in application code
   - Use database constraints where possible
   - Implement comprehensive testing

3. **Migration Issues**:
   - Test migrations on development database
   - Implement rollback procedures
   - Use feature flags for gradual rollout

4. **Security Gaps**:
   - Regular security audits
   - Automated testing of RLS policies
   - Monitor access patterns

## Implementation Plan

### Phase 1: Core Schema (Completed)
- [x] Create database tables with proper constraints
- [x] Implement RLS policies
- [x] Set up Drizzle schema definitions

### Phase 2: API Layer (Completed)
- [x] Create request/response DTOs
- [x] Implement mapper functions
- [x] Build API routes with validation

### Phase 3: Frontend Integration (Completed)
- [x] Create React hooks with standard shapes
- [x] Build form components with Zod validation
- [x] Implement assessment creation form

### Phase 4: Documentation (Completed)
- [x] Create schema guide
- [x] Write RLS playbook
- [x] Document API endpoints

### Phase 5: Testing and Validation (Pending)
- [ ] Implement comprehensive test suite
- [ ] Validate RLS policies
- [ ] Performance testing
- [ ] Security audit

## Alternatives Considered

### Alternative 1: Single Table Design
**Description**: Store all assessment data in a single table with JSONB fields

**Pros**:
- Simpler schema
- Easier to implement initially

**Cons**:
- Poor performance for complex queries
- Difficult to maintain data integrity
- No foreign key relationships
- Poor scalability

**Decision**: Rejected - insufficient for requirements

### Alternative 2: Microservice Architecture
**Description**: Separate assessment service with its own database

**Pros**:
- Service isolation
- Independent scaling
- Technology flexibility

**Cons**:
- Increased complexity
- Network overhead
- Data consistency challenges
- Operational overhead

**Decision**: Rejected - over-engineering for current needs

### Alternative 3: GraphQL API
**Description**: Use GraphQL instead of REST for API layer

**Pros**:
- Flexible querying
- Strong typing
- Client-side optimization

**Cons**:
- Learning curve
- Caching complexity
- Tooling overhead
- Inconsistent with existing patterns

**Decision**: Rejected - inconsistent with existing codebase

### Alternative 4: NoSQL Database
**Description**: Use MongoDB or similar for assessment data

**Pros**:
- Flexible schema
- Good for JSON data
- Horizontal scaling

**Cons**:
- No ACID transactions
- Complex queries
- Inconsistent with existing infrastructure
- Learning curve

**Decision**: Rejected - inconsistent with existing PostgreSQL infrastructure

## Related Decisions

- [ADR-001: Database Technology Selection](../database-design/comprehensive-brief.md)
- [ADR-003: API Design Patterns](../MASTER/API_DOCUMENTATION.md)
- [ADR-004: Frontend Architecture Patterns](../MASTER/FRONTEND_ARCHITECTURE.md)

## References

- [Supabase Documentation](https://supabase.com/docs)
- [Drizzle ORM Documentation](https://orm.drizzle.team/)
- [Zod Validation Library](https://zod.dev/)
- [React Hook Form](https://react-hook-form.com/)
- [APEST Framework](https://www.5qcentral.com/)

## Review

**Next Review Date**: 2025-04-02  
**Reviewers**: Development Team, Product Team  
**Review Criteria**: 
- Performance metrics
- Security audit results
- User feedback
- Maintenance overhead

---

**Approved by**: Development Team  
**Date**: 2025-01-02  
**Version**: 1.0
