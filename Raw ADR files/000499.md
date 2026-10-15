# ADR-013: Visual Content File Storage Architecture

**Date:** 2025-06-22  
**Status:** ACCEPTED  
**Author:** JP

## Context

The AI Marketing Campaign Post Generator generates visual content (images and videos) using Google Imagen 3.0 and Veo models. Initially, generated images were being stored as base64 data URLs embedded in JSON cache files, causing severe performance and display issues.

## Problem

### Original Implementation Issues:
1. **Massive JSON Files**: Cache files became 1.6MB+ each containing base64 image data
2. **Frontend Display Failure**: Browsers couldn't properly render large base64 data URLs
3. **API Response Bloat**: Responses grew from ~2KB to 6MB+ for 4 images
4. **Storage Inefficiency**: JSON files storing binary data instead of metadata
5. **Cache Performance**: Cache reads/writes became extremely slow

### Root Cause:
```python
# PROBLEMATIC: Embedding base64 data in JSON
img_base64 = base64.b64encode(image_data_bytes).decode('utf-8')
return f"data:image/png;base64,{img_base64}"
```

## Decision

**Implement proper file storage architecture for visual content with HTTP serving endpoints.**

### Architecture Components:

1. **File Storage Structure**:
   ```
   data/images/generated/<campaign_id>/img_<timestamp>_<uuid>_<index>.png
   ```

2. **URL Generation**:
   ```python
   # Generate absolute URLs for frontend access
   file_url = f"http://localhost:8000/api/v1/content/images/{campaign_id}/{image_filename}"
   ```

3. **HTTP Serving Endpoint**:
   ```python
   @router.get("/images/{campaign_id}/{filename}")
   async def serve_generated_image(campaign_id: str, filename: str):
       return FileResponse(path=image_path, media_type="image/png")
   ```

4. **Cache Optimization**:
   - Store file URLs in cache instead of base64 data
   - Cache files now contain metadata (~200 bytes) instead of binary data

## Consequences

### Positive:
- ✅ **Performance**: Cache size reduced from 1.6MB+ to ~200 bytes per image
- ✅ **API Efficiency**: Response size reduced from 6MB+ to ~2KB for 4 images
- ✅ **Frontend Display**: Images load instantly and display correctly
- ✅ **Storage Organization**: Proper file system usage with campaign-specific directories
- ✅ **Scalability**: File-based storage scales better than JSON-embedded data
- ✅ **Caching**: HTTP caching headers for browser optimization
- ✅ **Security**: Path validation prevents directory traversal attacks

### Negative:
- ➖ **Complexity**: Additional HTTP endpoint required for image serving
- ➖ **Dependencies**: Frontend now depends on backend image serving endpoint
- ➖ **File Management**: Need to manage file cleanup and organization

### Neutral:
- 🔄 **Migration**: Existing base64 cache files need to be cleared for new architecture
- 🔄 **Configuration**: Absolute URLs require backend URL configuration

## Implementation Details

### File Storage Method:
```python
async def _save_generated_image_data(self, image_data_bytes: bytes, index: int, campaign_id: str = "default") -> str:
    # Create campaign-specific directory
    images_dir = Path("data/images/generated") / campaign_id
    images_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    timestamp = int(time.time())
    image_filename = f"img_{timestamp}_{uuid.uuid4().hex[:8]}_{index}.png"
    image_path = images_dir / image_filename
    
    # Save actual PNG file
    with open(image_path, 'wb') as img_file:
        img_file.write(image_data_bytes)
    
    # Return absolute URL for frontend
    return f"http://localhost:8000/api/v1/content/images/{campaign_id}/{image_filename}"
```

### Security Considerations:
- Path validation prevents directory traversal
- File type validation (PNG/JPG only)
- Campaign ID sanitization
- HTTP caching headers for performance

## Production Roadmap

### MVP (Current):
- Local file storage in `data/images/generated/`
- HTTP serving via FastAPI FileResponse
- Campaign-specific organization

### Production (Future):
- Migrate to Google Cloud Storage buckets
- CDN integration for global distribution
- Image optimization and resizing
- Automatic cleanup policies

## Alternatives Considered

1. **Continue with Base64 Data URLs**: Rejected due to performance issues
2. **Database BLOB Storage**: Rejected due to complexity and performance
3. **External Image Hosting**: Rejected due to cost and complexity for MVP
4. **Temporary File URLs**: Rejected due to persistence requirements

## Validation

### Testing Results:
- ✅ Images generate and save as PNG files (1.3MB typical size)
- ✅ HTTP endpoint serves images correctly with proper headers
- ✅ Frontend displays images instantly
- ✅ Cache performance dramatically improved
- ✅ API response times reduced from 10s+ to <1s

### Browser Compatibility:
- ✅ Chrome: Images display correctly
- ✅ Safari: Images display correctly  
- ✅ Firefox: Images display correctly

## Related ADRs

- [ADR-012: Campaign-Specific Content Caching](ADR-012-Campaign-Specific-Content-Caching.md) - Caching strategy
- [ADR-003: Backend ADK Implementation](ADR-003-backend-adk-implementation.md) - Agent architecture

## References

- Google Imagen 3.0 API Documentation
- FastAPI FileResponse Documentation
- HTTP Caching Best Practices
- Web Performance Optimization Guidelines 