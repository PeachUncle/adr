# ADR-003: Field Mapping Fix for Discord Bot Integration

## Status
**Accepted** - Implemented on 2025-08-08

## Context

### Problem Statement
The Discord publishing bot was experiencing validation errors for response and bookmark posts:
- Error: "target_url: Target URL missing for response/bookmark"
- Root cause: Discord bot called `/publish` endpoint with `reply_to_url`/`bookmark_url` fields
- Publishing service expected `target_url` field for proper validation
- No field mapping logic existed between Discord bot and publishing service

### Technical Analysis
1. **Discord Bot Architecture**: Uses old `/publish` API endpoint with message-based format
2. **Publishing Service**: Validates frontmatter requiring `target_url` for response/bookmark posts  
3. **Field Name Mismatch**: Discord forms use `reply_to_url`/`bookmark_url`, service expects `target_url`
4. **Integration Gap**: No mapping layer between Discord field names and publishing service schema

### User Impact
- Response posts failing validation despite having valid URLs
- Bookmark posts showing warnings for missing target URLs
- Inconsistent user experience with validation error messages
- Manual workaround required for proper post creation

## Decision

### Selected Solution: Combined App Field Mapping
Implement field mapping logic in the combined app's `/publish` endpoint to automatically convert Discord field names to publishing service schema.

#### Implementation Approach
1. **Enhanced Combined App**: Add `/publish` endpoint with field mapping logic
2. **Frontmatter Parsing**: Parse Discord message frontmatter to identify conversion needs
3. **Field Conversion**: Map `reply_to_url` → `target_url` and `bookmark_url` → `target_url`
4. **Message Reconstruction**: Rebuild message with corrected field names before publishing
5. **Backward Compatibility**: Maintain existing Discord bot integration without changes

#### Alternative Solutions Considered

**Option A: Update Discord Bot**
- Pros: Direct fix at source, cleaner architecture
- Cons: Requires Discord bot changes, testing, deployment coordination
- Decision: Rejected due to complexity and deployment dependencies

**Option B: Update Publishing Service**  
- Pros: Central fix, handles all input sources
- Cons: Changes core validation logic, impacts other integrations
- Decision: Rejected to maintain publishing service schema consistency

**Option C: Field Mapping in Combined App** ⭐ **SELECTED**
- Pros: Backward compatible, isolated fix, no Discord bot changes required
- Cons: Additional layer of complexity in combined app
- Decision: Selected for minimal impact and immediate resolution

## Implementation Details

### Combined App Enhancement
```python
@app.post("/publish", response_model=PublishResponse)
async def publish_post_discord_compat(request: PublishRequest):
    # Parse frontmatter and apply field mapping fix
    # Convert reply_to_url/bookmark_url → target_url
    # Rebuild message with corrected fields
    # Call publishing service with fixed message
```

### Field Mapping Logic
1. **Parse Message**: Extract frontmatter section from Discord message
2. **Identify Fields**: Look for `reply_to_url:` and `bookmark_url:` patterns
3. **Convert Fields**: Replace with `target_url:` using same URL value
4. **Reconstruct**: Rebuild complete message with corrected frontmatter
5. **Validate**: Ensure converted message passes publishing service validation

### Response Model Updates
Updated `PublishResponse` to match actual publishing service return format:
```python
class PublishResponse(BaseModel):
    status: str
    workflow: str  
    filepath: str
    branch_name: Optional[str] = None
    commit_sha: Optional[str] = None
    pr_url: Optional[str] = None
    # ... additional fields
```

## Consequences

### Positive Impact
- **✅ Validation Errors Eliminated**: No more "target_url missing" warnings for response/bookmark posts
- **✅ Backward Compatibility**: Existing Discord bot integration works without changes
- **✅ User Experience**: Seamless post creation with proper field validation
- **✅ Isolated Fix**: Changes contained within combined app, minimal system impact

### Technical Benefits
- **Field Mapping Transparency**: Conversion happens automatically in background
- **Robust Error Handling**: Comprehensive error handling with fallback mechanisms
- **Service Separation**: Publishing service maintains clean schema validation
- **Testing Verified**: Solution validated through test PRs #124-125

### Maintenance Considerations
- **Additional Logic**: Combined app now handles field mapping responsibility
- **Documentation**: Field mapping behavior documented in API endpoints
- **Testing**: Requires ongoing testing of field mapping logic
- **Monitoring**: Should monitor for field mapping failures or edge cases

### Risk Mitigation
- **Fallback Handling**: Pass-through for messages not requiring field mapping
- **Error Logging**: Comprehensive logging for debugging field mapping issues  
- **Validation**: Ensure converted messages pass publishing service validation
- **Testing**: Extensive testing with real GitHub PR creation for verification

## Verification

### Test Results
- **PR #124**: Response post with `reply_to_url` successfully converted to `target_url`
- **PR #125**: Bookmark post with `bookmark_url` successfully converted to `target_url`  
- **Zero Validation Errors**: No warnings after field mapping implementation
- **End-to-End Success**: Complete Discord → Combined App → Publishing Service → GitHub workflow

### Success Metrics
- ✅ **Field Mapping Accuracy**: 100% successful conversion in testing
- ✅ **Validation Pass Rate**: No validation errors post-implementation
- ✅ **Backward Compatibility**: Existing Discord bot functionality preserved
- ✅ **Performance Impact**: Negligible latency added to publishing workflow

## Future Considerations

### Potential Improvements
1. **Field Mapping Configuration**: Make field mappings configurable for future schema changes
2. **Validation Enhancement**: Add validation for field mapping accuracy and completeness
3. **Monitoring**: Add metrics for field mapping usage and success rates
4. **Documentation**: Enhance API documentation with field mapping behavior details

### Schema Evolution
- Monitor for future Discord form field changes requiring mapping updates
- Consider standardizing field names across Discord and publishing service
- Plan for deprecation of field mapping if systems can be unified

### Alternative Integration Patterns
- Evaluate Discord HTTP interactions as replacement for current bot architecture
- Consider GraphQL or other integration patterns for future enhancements
- Plan for unified schema approach in next major version

## Related Documents
- [Technical Specification](../../specs/technical/discord-publish-bot-technical-spec.md)
- [API Documentation](../../specs/api/discord-publishing-api.md)
- [Changelog Entry](../../changelog.md#210---2025-08-08---field-mapping-fix-complete)

## References
- Test PRs: #124 (response), #125 (bookmark)
- Commit: 24e1915 - "Fix target_url field mapping for Discord posts"
- Implementation files: `src/combined_app.py`, `src/publishing_api/main.py`
