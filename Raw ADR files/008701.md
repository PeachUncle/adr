# ADR-010: Discord Modal Routing Parameter Fix

## Status
- [x] Accepted
- [x] Implemented

**Date:** 2025-08-10  
**Authors:** GitHub Copilot, lqdev  
**Reviewers:** Production validation

## Context

A critical bug was discovered in production where Discord slash commands for non-note post types (response, bookmark, media) were incorrectly displaying the note modal instead of their specific modals. This prevented users from accessing the proper fields required for different post types.

### Background Information
- The Discord Publish Bot supports multiple post types via slash commands: `/post note`, `/post response`, `/post bookmark`, `/post media`
- Each post type requires different modal fields (e.g., response posts need a "Reply URL" field, bookmark posts need a "Bookmark URL" field)
- The production deployment uses HTTP interactions handler (`interactions.py`) rather than the WebSocket bot (`bot.py`)
- User testing revealed that all post types were showing the same note modal interface

### Technical Investigation
- **Root Cause**: Parameter name mismatch between implementations
  - WebSocket bot (`bot.py`): Uses parameter name `post_type` 
  - HTTP interactions handler (`interactions.py`): Was looking for parameter name `type`
- **Impact**: Complete loss of functionality for response, bookmark, and media post types
- **Location**: `src/discord_publish_bot/discord/interactions.py` line 196
- **Discovery Method**: User feedback and production testing

## Decision

We will **fix the parameter name mismatch in the HTTP interactions handler** to correctly parse the `post_type` parameter instead of `type`.

**Specific Change**: In `_handle_post_command` method, change:
```python
if option["name"] == "type":
```
to:
```python
if option["name"] == "post_type":
```

This aligns the HTTP interactions implementation with the WebSocket bot implementation and Discord's actual parameter structure.

## Alternatives Considered

### Option 1: Modify WebSocket bot to use "type" parameter
- **Pros:** Would make HTTP handler work without changes
- **Cons:** Would break existing working WebSocket implementation, larger change surface
- **Rationale for rejection:** Higher risk, affects working code unnecessarily

### Option 2: Support both "type" and "post_type" parameters
- **Pros:** Maximum compatibility
- **Cons:** Added complexity, technical debt, unclear which is canonical
- **Rationale for rejection:** Unnecessary complexity for a clear mismatch issue

### Option 3: Deprecate HTTP interactions, use only WebSocket
- **Pros:** Single code path, less maintenance
- **Cons:** Production deployment architecture change, higher resource usage
- **Rationale for rejection:** Major architectural change for simple bug fix

## Consequences

### Positive Consequences
- **Restored Functionality**: All Discord post types now work correctly in production
- **User Experience**: Users can access proper modals with correct fields for each post type
- **Code Consistency**: HTTP and WebSocket implementations now aligned
- **Minimal Risk**: Single-line change with clear scope and impact
- **Immediate Value**: Critical production issue resolved with minimal deployment overhead

### Negative Consequences
- **None Identified**: This is a straightforward bug fix with no downside

### Neutral/Unknown Consequences
- **Future Maintenance**: Need to ensure both implementations stay aligned during future changes

## Implementation

### Action Items
- [x] Identify exact location of parameter mismatch
- [x] Update HTTP interactions handler parameter name
- [x] Build and test application locally
- [x] Create validation test script
- [x] Deploy fix to Azure Container Apps production
- [x] Verify health endpoint responds correctly
- [x] Test all post type modals in Discord

### Timeline
- **Start Date:** 2025-08-10
- **Completion Date:** 2025-08-10 (same day)
- **Deployment Time:** 1 hour total including testing and deployment

### Deployment Process
1. **Fix Applied**: Changed parameter lookup in `interactions.py`
2. **Local Validation**: Created test script validating modal routing for all post types
3. **Container Build**: Docker build successful with fix included
4. **Azure Deployment**: Used `az containerapp up` following established runbook
5. **Environment Configuration**: Applied secret references per deployment standards
6. **Production Verification**: Health endpoint confirmed application healthy
7. **User Testing**: Discord modal functionality verified for all post types

## Compliance

### Architecture Alignment
- [x] Aligns with existing Discord integration patterns
- [x] Follows established HTTP interactions architecture
- [x] Maintains consistency between WebSocket and HTTP implementations

### Review Process
- [x] Technical validation via automated testing
- [x] Production health verification completed
- [x] User acceptance testing via Discord interface
- [x] Deployment following established runbook procedures

## Related Documents
- **Deployment Runbook:** `docs/team/azure-deployment-runbook.md`
- **Technical Specs:** `specs/api/discord-publishing-api.md`
- **Implementation:** `src/discord_publish_bot/discord/interactions.py`
- **Changelog:** Version 2.0.1 entry documenting fix

## Notes

This issue highlights the importance of:
1. **Integration Testing**: Need end-to-end testing across both WebSocket and HTTP implementations
2. **Parameter Validation**: Consider adding parameter validation to catch mismatches earlier
3. **Deployment Verification**: User acceptance testing should be part of deployment process
4. **Code Review**: Cross-implementation consistency should be checked during reviews

**Lesson Learned**: When supporting multiple interaction methods (WebSocket + HTTP), parameter parsing must be identical across implementations. Future changes should include validation that both paths handle the same command structure.

---
*Implemented: 2025-08-10*  
*Production Status: ✅ Deployed and Verified*
