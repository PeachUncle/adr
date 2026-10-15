# ADR-012: Campaign-Specific Content Caching Architecture

**Date:** 2025-01-16
**Author:** JP
**Status:** Implemented
**Context:** Google ADK Hackathon - AI Marketing Campaign Post Generator

## Summary

Implement campaign-aware caching system for visual content generation to ensure consistent user experience, prevent image disappearing issues, and establish clear path from MVP to Production deployment on Google Cloud Platform.

## Context and Problem Statement

### Current Challenges
1. **Visual Content Inconsistency**: Images generated for campaigns would disappear between user sessions due to lack of persistent caching
2. **Poor User Experience**: Users would see "generation in progress" indefinitely when cached content was not properly managed
3. **Resource Inefficiency**: Regenerating identical visual content multiple times for same campaign context
4. **No Campaign Isolation**: All cached content was stored globally without campaign-specific organization
5. **MVP-to-Production Gap**: No clear strategy for migrating local caching to cloud storage for production

### Business Requirements
- **Consistent User Experience**: Users should see the same generated images for a campaign across sessions
- **Cost Optimization**: Avoid regenerating identical content (Imagen 3.0 API costs)
- **Campaign Isolation**: Different campaigns should have separate cached content
- **Performance**: Fast retrieval of previously generated content
- **Production Readiness**: Clear migration path to Google Cloud Storage

## Decision

Implement **Campaign-Specific Content Caching Architecture** with the following components:

### 1. Campaign-Aware Cache Structure
```
data/images/cache/
├── <campaign_id>/
│   ├── curr_<imagehash>.json     # Current/latest images (persistent)
│   └── <imagehash>.json          # Previous images (cleaned on restart)
└── <other_campaign_id>/
    ├── curr_<imagehash>.json
    └── <imagehash>.json
```

### 2. Current vs. Historical Image Management
- **Current Images (`curr_` prefix)**: Latest generated images, never expire, survive app restarts
- **Historical Images (no prefix)**: Previous generations, cleaned up on app restart to save space
- **Cache Key Strategy**: `campaign_id + prompt + model` for unique identification

### 3. Cache Lifecycle Management
- **On Generation**: Save as current image, replace any existing current image for same prompt
- **On App Restart**: Cleanup old images, keep current images for consistent UX
- **On Campaign Completion**: Optional cleanup of campaign-specific cache

### 4. API Enhancement
- **Campaign ID Integration**: All visual generation endpoints accept `campaign_id` parameter
- **Auto-Generated Campaign IDs**: When not provided, generate from `company_name + campaign_objective`
- **Cache Management Endpoints**: Stats, cleanup, and clear operations per campaign

## Implementation Details

### Core Classes

#### CampaignImageCache
```python
class CampaignImageCache:
    """Campaign-aware image caching system"""
    
    def get_cached_image(self, prompt: str, model: str, campaign_id: str) -> Optional[str]:
        # Priority: current images > regular cache with expiry
    
    def cache_image(self, prompt: str, model: str, campaign_id: str, 
                   image_data: str, is_current: bool = True) -> bool:
        # Save with campaign isolation and current/historical distinction
    
    def cleanup_old_images(self, campaign_id: Optional[str] = None) -> int:
        # Remove non-current images, keep curr_ prefixed files
```

### API Integration
```python
# Visual content generation with campaign awareness
visual_results = await generate_visual_content_for_posts(
    social_posts=social_posts,
    business_context=business_context,
    campaign_objective=campaign_objective,
    target_platforms=target_platforms,
    campaign_id=campaign_id  # New parameter
)
```

### Cache Management Endpoints
- `GET /api/v1/content/cache/stats?campaign_id=<id>` - Campaign-specific stats
- `POST /api/v1/content/cache/clear` - Clear all or specific campaign
- `POST /api/v1/content/cache/cleanup` - Remove old images, keep current

### Makefile Integration
```makefile
setup-logging:
    @mkdir -p data/images/cache
    @echo "🗑️ Cleaning up old cached images (keeping current images)..."
    @python3 -c "from backend.agents.visual_content_agent import CampaignImageCache; cache = CampaignImageCache(); cache.cleanup_old_images()"
```

## MVP-to-Production Roadmap

### Current State (MVP - Local Development)
- **Storage**: Local filesystem (`data/images/cache/`)
- **Scope**: Single-instance caching
- **Management**: Manual cleanup via Makefile

### Production State (Google Cloud Platform)
- **Storage**: Google Cloud Storage buckets
- **Structure**: `gs://marketing-content-cache/<user_id>/<campaign_id>/`
- **Features**: 
  - Multi-user isolation
  - Automatic lifecycle management
  - CDN integration for fast delivery
  - Cross-region replication

### Migration Strategy
1. **Phase 1 (Current)**: Local campaign-aware caching
2. **Phase 2**: GCS integration with local fallback
3. **Phase 3**: Full cloud-native with user authentication
4. **Phase 4**: CDN integration and global distribution

## Architecture Benefits

### User Experience
- **Consistency**: Same images appear across sessions for same campaign
- **Performance**: Instant loading of previously generated content
- **Reliability**: No more "generation in progress" indefinitely

### Development Benefits
- **Cost Control**: Avoid duplicate API calls to expensive generation services
- **Debugging**: Clear separation of current vs. historical content
- **Testing**: Predictable content for test scenarios

### Production Benefits
- **Scalability**: Campaign isolation supports multi-user scenarios
- **Maintenance**: Easy cleanup of old content without affecting active campaigns
- **Migration Path**: Clear evolution to cloud storage

## Video Content Extension

Apply same architecture pattern to video generation:

```
data/videos/cache/
├── <campaign_id>/
│   ├── curr_<videohash>.json     # Current/latest videos
│   └── <videohash>.json          # Previous videos
```

**Implementation Consistency**:
- Same cache key strategy: `campaign_id + prompt + model`
- Same current vs. historical management
- Same cleanup lifecycle
- Same API patterns

## Testing Strategy

### Validation Tests
- **Cache Hit/Miss Logging**: Verify cache behavior with detailed console output
- **Campaign Isolation**: Ensure campaigns don't interfere with each other
- **Cleanup Verification**: Confirm old images removed, current images preserved
- **API Integration**: Test campaign_id parameter flow through all endpoints

### Performance Tests
- **Cache Performance**: Measure retrieval speed vs. generation time
- **Storage Growth**: Monitor cache size growth patterns
- **Cleanup Efficiency**: Verify cleanup removes appropriate files

## Monitoring and Observability

### Cache Statistics
```json
{
  "total_campaigns": 3,
  "total_images": 15,
  "total_size_mb": 45.2,
  "campaigns": {
    "abc123ef": {
      "current_images": 3,
      "regular_images": 2,
      "total_size_mb": 12.1
    }
  }
}
```

### Logging Strategy
- **Cache Operations**: Hit/miss/save operations with campaign context
- **Cleanup Activities**: Detailed logging of what gets removed/preserved
- **Performance Metrics**: Generation time vs. cache retrieval time

## Compliance and Security

### Data Management
- **Campaign Isolation**: Prevents cross-campaign data leakage
- **Cleanup Procedures**: Clear data retention policies
- **Access Control**: Campaign-specific access (ready for user authentication)

### Production Considerations
- **User Data Isolation**: Each user's campaigns isolated in cloud storage
- **Content Lifecycle**: Automatic expiration of unused content
- **Privacy Compliance**: Clear data retention and deletion policies

## Success Metrics

### Technical Metrics
- **Cache Hit Rate**: Target >70% for repeated campaign iterations
- **User Experience**: Eliminate "infinite loading" issues
- **Cost Reduction**: Reduce duplicate API calls by >50%
- **Performance**: <100ms cache retrieval vs. >30s generation

### Business Metrics
- **User Satisfaction**: Consistent visual content across sessions
- **Development Velocity**: Faster testing with predictable content
- **Production Readiness**: Clear migration path to scalable architecture

## Implementation Status

- ✅ **CampaignImageCache Class**: Implemented with full feature set
- ✅ **API Integration**: Campaign ID parameter added to all endpoints
- ✅ **Cache Management**: Stats, clear, and cleanup endpoints
- ✅ **Makefile Integration**: Automatic cleanup on app restart
- ✅ **Logging and Monitoring**: Comprehensive cache operation logging
- 🔄 **Video Content Extension**: Architecture defined, implementation pending
- 📋 **Production GCS Migration**: Architecture defined, implementation planned

## Related ADRs

- **ADR-003**: API Structure Definition (endpoint patterns)
- **ADR-008**: Visual Content Generation Strategy (generation approach)
- **ADR-010**: API Timeout Configuration (performance requirements)

---

**Next Steps:**
1. Extend architecture to video content caching
2. Implement production GCS migration layer
3. Add user-specific campaign isolation
4. Integrate with authentication system for multi-user support 