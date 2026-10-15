# ADR-014: Draft Mode for Articles

## Status
Accepted

## Context
We need to implement a draft mode functionality for articles that allows content creators to save work in progress and publish articles when ready. This feature is essential for content management workflow and editorial processes.

### Requirements
1. Articles must have two distinct states: `DRAFT` and `PUBLISHED`
2. Articles can be saved multiple times in `DRAFT` state
3. Articles can transition from `DRAFT` to `PUBLISHED`
4. Articles cannot transition from `PUBLISHED` back to `DRAFT` (unidirectional)
5. Only applies to articles (not books or other entities)
6. Public blog endpoints must only show `PUBLISHED` articles
7. Backoffice endpoints can manage both `DRAFT` and `PUBLISHED` articles

## Decision

### Domain Layer
- Create `ArticleStatus` value object with `DRAFT` and `PUBLISHED` states
- Add `status` property to `Article` aggregate root
- Implement state transition rules in domain methods (`publish()`, validation for unpublish attempt)
- Default status for new articles is `DRAFT`
- Update domain events to include status information

### Infrastructure Layer
- Add `status` column to `articles` table with constraints
- Set default value as `DRAFT` for new records
- Update existing articles to `PUBLISHED` during migration
- Modify repositories to handle status filtering:
  - `PostgresArticleRepository` (backoffice): no filtering
  - `PostgresBlogArticleRepository` (blog): filter only `PUBLISHED`

### Application Layer
- Update `CreateArticle` to accept optional status parameter
- Update `UpdateArticle` to handle status transitions with validation
- Create new `PublishArticle` service for explicit publishing workflow
- Maintain existing service interfaces for backward compatibility

### API Layer
- Add `status` field to article creation and update endpoints
- Create new `POST /api/backoffice/articles/{id}/publish` endpoint
- Validate status values in API layer
- Blog API automatically filtered via repository layer

## Consequences

### Positive
- Clear content workflow with draft and published states
- Editorial control over content visibility
- Backward compatibility maintained
- Clean separation between backoffice and blog concerns
- Explicit business rules enforcement

### Negative
- Database schema change requires migration
- Additional complexity in domain model
- More API endpoints to maintain

### Risks
- Migration must handle existing articles correctly
- Need comprehensive testing for state transitions
- API clients need to be aware of new status field

## Implementation Notes

### Migration Strategy
1. Add `status` column with `DRAFT` default
2. Update existing articles to `PUBLISHED` (assuming current articles are live)
3. Add database constraints for valid status values

### Testing Strategy
- Unit tests for `ArticleStatus` value object
- Unit tests for `Article` aggregate status behavior
- Integration tests for repository filtering
- E2E tests for API endpoints with status
- Migration tests for data integrity

### API Compatibility
- Existing endpoints remain functional
- New `status` field is optional for backward compatibility
- Default behavior preserves existing functionality

## Related Documents
- OBR-006: Draft Mode Business Rules
- Memory Bank: Progress and Active Context updates 