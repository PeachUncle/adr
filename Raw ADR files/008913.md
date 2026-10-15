# ADR-001: Analytics Service Organization

## Status
Accepted - Implemented on 2025-11-25

## Context
During backend cleanup, we identified three analytics services with overlapping concerns:
- `AnalyticsService` (1,208 lines)
- `EnhancedStudentAnalyticsService` (598 lines)
- `EnhancedTeacherAnalyticsService` (450 lines)

Initial proposal was to consolidate all three into a single `AnalyticsService` file, which would result in a 2,256-line monolith.

## Decision
Keep analytics services separate in an organized package structure:

```
src/application/services/analytics/
├── __init__.py
├── analytics_utils.py          # Shared utilities
├── analytics_service.py         # General analytics & CO/PO
├── student_analytics_service.py # Student dashboard & internals
└── teacher_analytics_service.py # Teacher dashboard & class insights
```

## Rationale

### SOLID Principles
**Single Responsibility Principle:**
- `AnalyticsService`: General analytics, CO/PO attainment, Bloom's taxonomy
- `StudentAnalyticsService`: Student-specific dashboard, performance trends
- `TeacherAnalyticsService`: Teacher-specific dashboard, class management, at-risk students

Each service has a distinct, focused purpose.

### Maintainability
- **Smaller files** (450-1,200 lines) are easier to understand and modify
- **Clear boundaries** between student, teacher, and general analytics
- **Easier testing** - each service can be tested independently

### Scalability
- Easy to add new specialized analytics services
- Clear pattern for organization
- Package structure allows for future growth

## Consequences

### Positive
- Better code organization following SOLID principles
- Easier to navigate and understand
- Each service is independently testable
- Clear separation of concerns
- Smaller, more maintainable files

### Negative
- More imports required across codebase
- Three service files instead of one
- Need to understand package organization

### Neutral
- Total lines of code roughly the same
- Slightly more complex directory structure

## Alternatives Considered

### Alternative 1: Single Consolidated Service
Merge all analytics into one `AnalyticsService` file.

**Rejected because:**
- Would create 2,256-line file (unmaintainable)
- Violates Single Responsibility Principle
- Difficult to navigate and test
- High risk of merge conflicts

### Alternative 2: Microservices
Split into completely separate microservices.

**Rejected because:**
- Overengineering for current scale
- Adds deployment complexity
- Shared database access patterns
- Current monolithic architecture is appropriate

## References
- Implementation: `/Users/deepstacker/WorkSpace/dsaba-lms-04/backend/src/application/services/analytics/`
- Related ADRs: ADR-002 (Shared Utilities Pattern)
