# ADR-008: Model Consolidation and Relationship Strategy

## Context

The current project has multiple model definitions for similar entities across different apps, leading to potential inconsistencies and confusion:

1. Courses App:
   - Detailed Course model with status and visibility
   - Uses string-based foreign key to User

2. Learning Platform App:
   - Simplified Course model
   - Includes User, Course, Task, and Assessment models
   - Direct foreign key relationships

3. Tasks App:
   - Multiple task-related models with overlapping responsibilities
   - Complex inheritance structure

## Decision

We will consolidate and standardize our data models with the following approach:

### 1. Course Model

- Use the more comprehensive model from courses app
- Retain status, visibility, and detailed attributes
- Use explicit import for User model

### 2. User Model

- Use the custom User model from learningplatform app
- Extend AbstractUser for flexibility

### 3. Task/Learning Task Model

- Consolidate into a single, flexible model in the tasks app
- Support multiple task types through a type field or inheritance
- Include common attributes like course, creator, status

### 4. Assessment Model

- Keep as a separate model linking tasks to user submissions
- Support different assessment types

## Rationale

- Reduce model duplication
- Improve code maintainability
- Create a more consistent data model
- Support future extensibility

## Consequences

- Requires migration of existing data
- Potential short-term complexity during refactoring
- Improved long-term code organization

## Implementation Steps

1. Verify and merge Course model definitions
2. Update foreign key relationships
3. Consolidate task-related models
4. Create comprehensive migration strategy
5. Update serializers and views accordingly

## Risks

- Potential data loss during migration
- Temporary disruption to existing functionality
- Need for thorough testing

## Alternatives Considered

- Keeping current distributed model
- Creating a more complex, generic model system

## Decision Date

2025-02-27

## Status

Accepted
