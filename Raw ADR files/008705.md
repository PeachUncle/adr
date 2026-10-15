# ADR-012: Directory Structure Alignment

## Status
- [x] Accepted

**Date:** 2025-08-20  
**Authors:** GitHub Copilot AI Assistant  
**Reviewers:** Project Team

## Context

The Discord publishing bot's directory structure for published content needed realignment with the user's existing site organization. The current system was using an outdated directory structure:

- **Current Structure**: Notes were being published to `_src/feed/` and bookmarks to `_src/responses/`
- **Required Structure**: Notes should go to `_src/notes/` and bookmarks should go to `_src/bookmarks/`

### Background Information
- The user's static site generator expects content in specific directories for proper categorization and URL structure
- The original implementation used a generic `_src/feed/` directory for notes, which doesn't align with the user's content taxonomy
- Bookmarks were being treated as responses and placed in `_src/responses/`, when they should have their own dedicated directory
- Site URL generation and navigation depends on correct directory structure

### Technical Constraints
- Must maintain backward compatibility with existing PR creation workflow
- Content frontmatter and processing logic should remain unchanged
- GitHub repository structure must align with static site generator expectations
- Directory changes should not break existing published content

## Decision

We will update the directory mapping configuration in the publishing service to align with the user's required directory structure:

- **Notes** (`PostType.NOTE`): `_src/notes/` (changed from `_src/feed/`)
- **Bookmarks** (`PostType.BOOKMARK`): `_src/bookmarks/` (changed from `_src/responses/`)
- **Responses** (`PostType.RESPONSE`): `_src/responses/` (unchanged)
- **Media** (`PostType.MEDIA`): `_src/media/` (unchanged)

## Alternatives Considered

### Option 1: Maintain current structure with configuration override
- **Pros:** No code changes required, could use environment variables
- **Cons:** Would require complex configuration management, unclear which directories are canonical
- **Rationale for rejection:** Adds unnecessary complexity and doesn't solve the fundamental alignment issue

### Option 2: Make directories fully configurable per post type
- **Pros:** Maximum flexibility for future changes
- **Cons:** Over-engineering for current needs, adds configuration complexity
- **Rationale for rejection:** Current requirements are clear and specific, no need for extensive configurability

## Consequences

### Positive Consequences
- Content will be organized according to user's established site taxonomy
- URL structure will align with user's expected navigation patterns
- Clear separation between notes and bookmarks for better content management
- Simplified content discovery and site organization

### Negative Consequences
- Existing integration tests needed updates to reflect new directory structure
- Environment configuration files required updates
- Documentation needs updates to reflect new structure

### Neutral/Unknown Consequences
- Future content migrations may need consideration of directory changes
- Static site build processes should automatically handle new directory structure

## Implementation

### Action Items
- [x] Update `CONTENT_TYPE_DIRECTORIES` mapping in `PublishingService`
- [x] Update environment configuration files (`.env.production`, `.env.production.example`)
- [x] Update integration tests to expect new directory structure
- [x] Update documentation to reflect new structure
- [x] Create ADR to document this architectural decision

### Timeline
- **Start Date:** 2025-08-20
- **Target Completion:** 2025-08-20
- **Key Milestones:** All implementation completed in single session

## Compliance

### Architecture Alignment
- [x] Aligns with user's site architecture requirements
- [x] Follows established content organization patterns
- [x] Compatible with existing GitHub PR workflow

### Review Process
- [x] Technical implementation completed
- [x] Configuration impact assessed
- [x] Test coverage updated

## Related Documents
- **User Guide:** `docs/team/user-guide.md` - Documents content organization
- **Technical Specs:** `specs/technical/discord-publish-bot-technical-spec.md` - System architecture
- **API Documentation:** `specs/api/discord-publishing-api.md` - Publishing endpoints

## Notes

This change is a direct response to user feedback about directory structure alignment. The implementation maintains all existing functionality while ensuring content is published to the correct directories for the user's static site generator.

The change is backward compatible in terms of functionality - existing PRs and published content will continue to work, and new content will be published to the updated directories.

---
*Template Version: 1.0*  
*Last Updated: 2025-08-20*
