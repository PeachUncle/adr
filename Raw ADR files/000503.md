# ADR-021: Async Visual Content Generation Architecture

**Status**: ❌ SUPERSEDED by ADR-023  
**Date**: 2025-06-28  
**Author**: JP + Claude Sonnet  
**Context**: Google ADK Hackathon Submission - Progressive Loading UX  

## Context

The original synchronous visual content generation approach caused several critical UX issues:

### **Problems with Synchronous Approach**
1. **UI Blocking**: 30-60+ second waits with no feedback
2. **Interdependent Processing**: Text generation blocked image generation, which blocked video generation
3. **Poor UX**: Users saw spinning loaders with no real progress indication
4. **Resource Waste**: Failed image generation would prevent video generation
5. **No Cancellation**: Users couldn't cancel long-running operations
6. **Frontend Timeouts**: Browser timeouts on long API calls

### **Business Impact**
- **Demo Quality**: Poor impression during hackathon demonstrations
- **User Engagement**: Users abandon the application during long waits
- **MVP Credibility**: Appeared unfinished/prototype-quality

## Decision

Implement **Independent Async Visual Content Generation** with real-time progress tracking.

### **Core Architectural Principles**

#### **1. Complete Independence**
```
Text Generation    ──► Immediate Response (< 2s)
Image Generation   ──► Background Jobs (30-45s each)
Video Generation   ──► Background Jobs (60-120s each)
```

#### **2. Job-Based Processing**
```
Frontend Request ──► Queue Jobs ──► Immediate Response ──► Polling ──► Progressive Updates
```

#### **3. Real-Time UI Reflection**
- Loading states reflect actual backend job status
- Progress bars show real completion percentages
- Visual content appears as soon as individual jobs complete
- No blocking between different content types

## Implementation Architecture

### **Backend Components**

#### **1. Async Visual Manager** (`async_visual_manager.py`)
```python
class AsyncVisualManager:
    - Background worker pool (2 concurrent workers)
    - Job queue with priority handling
    - Campaign-aware job tracking
    - Real-time progress monitoring
    - File system integration
```

#### **2. Job Status Models**
```python
VisualGenerationJob:
    - job_id: Unique identifier
    - status: queued|processing|completed|failed
    - progress: 0.0 to 1.0 completion
    - content_type: image|video
    - result_url: Final file URL when complete
```

#### **3. API Endpoints**
```
POST /api/v1/content/generate-visuals-async
  ├── Returns: Job IDs + estimated times
  ├── Response Time: < 500ms
  └── Starts: Background processing

GET /api/v1/content/visual-status/{campaign_id}
  ├── Returns: Real-time job status
  ├── Polling Frequency: Every 3 seconds
  └── Progressive: posts_with_visuals array
```

### **Frontend Components**

#### **1. Async Visual Hook** (`useAsyncVisualGeneration.ts`)
```typescript
interface UseAsyncVisualGenerationState {
  // Real-time status
  isGenerating: boolean
  overallProgress: number // 0.0 to 1.0
  completedJobs: number
  estimatedTimeRemaining: number
  
  // Progressive results
  postsWithVisuals: Array<{
    id: string
    image_url?: string
    video_url?: string
  }>
  
  // Actions
  startGeneration()
  cancelGeneration()
}
```

#### **2. Independent Processing Flow**
```
User Action ──► Generate Text Posts (immediate)
            ├── Show Text Posts Instantly
            ├── Start Image Jobs (background)
            └── Start Video Jobs (background)

Background  ──► Image Job 1 Complete ──► Update UI
            ├── Image Job 2 Complete ──► Update UI
            ├── Video Job 1 Complete ──► Update UI
            └── Video Job 2 Complete ──► Update UI
```

### **UX Design Principles**

#### **1. Immediate Feedback**
- Text posts appear instantly (< 2s)
- Visual placeholders show with loading states
- Job counts and estimated times displayed immediately

#### **2. Progressive Loading**
- Images appear as individual jobs complete
- Videos appear independently of images
- No content type blocks others

#### **3. Real Progress Indication**
```
┌─ Campaign Progress ──────────────────┐
│ Generating Visual Content: 60% ░░▓▓▓░░│
│ ├── Images: 2/3 complete           │
│ ├── Videos: 1/2 complete           │
│ └── Est. Time: 2m 30s remaining    │
└────────────────────────────────────┘
```

#### **4. Error Resilience**
- Failed image job doesn't affect video jobs
- Partial completion is valuable
- Clear error states with retry options

## Technical Implementation

### **Phase 1: Backend Job Processing**
```python
# Independent job creation
for post in posts:
    if post_type == 'text_image':
        jobs.append(create_image_job(post))
    elif post_type == 'text_video':
        jobs.append(create_image_job(post))  # Thumbnail
        jobs.append(create_video_job(post))  # Video

# Parallel processing
async def worker(worker_name):
    while running:
        job = await queue.get()
        await process_job_independently(job)
```

### **Phase 2: Real-Time Updates**
```javascript
// Frontend polling with progressive updates
const pollStatus = async () => {
  const status = await fetch(`/visual-status/${campaignId}`)
  
  // Update UI immediately with completed content
  setPostsWithVisuals(status.posts_with_visuals)
  setProgress(status.overall_progress)
  
  // Continue polling until complete
  if (!status.is_complete) {
    setTimeout(pollStatus, 3000)
  }
}
```

### **Phase 3: UI Components**
```tsx
// Progressive content display
{posts.map(post => (
  <PostCard key={post.id}>
    <TextContent>{post.content}</TextContent>
    
    <VisualContent>
      {post.imageUrl ? (
        <img src={post.imageUrl} alt="Generated" />
      ) : (
        <ImageLoadingPlaceholder progress={getImageProgress(post.id)} />
      )}
      
      {post.videoUrl ? (
        <video src={post.videoUrl} controls />
      ) : post.type === 'text_video' ? (
        <VideoLoadingPlaceholder progress={getVideoProgress(post.id)} />
      ) : null}
    </VisualContent>
  </PostCard>
))}
```

## Future Enhancements

### **Google Cloud Production Architecture**
```
┌─ Frontend ─┐    ┌─ Cloud Run ─┐    ┌─ Pub/Sub ─┐    ┌─ Workers ─┐
│ React App  │───►│ FastAPI     │───►│ Job Queue │───►│ Imagen API │
│ (Polling)  │◄───│ (Webhooks)  │◄───│ Updates   │◄───│ Veo API    │
└────────────┘    └─────────────┘    └───────────┘    └───────────┘
```

#### **Pub/Sub Integration**
- **Job Queue**: Pub/Sub topic for visual generation jobs
- **Progress Updates**: Pub/Sub topic for real-time status
- **Webhooks**: Replace polling with push notifications
- **Scaling**: Auto-scale workers based on queue depth

#### **WebSocket Enhancement**
```javascript
// Real-time updates without polling
const ws = new WebSocket('/ws/visual-status/${campaignId}')
ws.onmessage = (event) => {
  const update = JSON.parse(event.data)
  updateVisualContent(update)
}
```

## Success Metrics

### **Performance Targets**
- **Initial Response**: < 500ms for job creation
- **Text Posts**: < 2s end-to-end generation
- **Image Generation**: 30-45s per image (background)
- **Video Generation**: 60-120s per video (background)
- **UI Updates**: < 3s latency for progress updates

### **UX Quality Indicators**
- **No Blocking**: Text generation never waits for visuals
- **Real Progress**: Progress bars reflect actual job completion
- **Partial Value**: Users get immediate value from text posts
- **Error Resilience**: Individual job failures don't break experience

### **Technical Quality**
- **Independence**: Content types process completely independently
- **Cancellation**: Users can cancel long-running operations
- **Cleanup**: Proper resource management and job cleanup
- **Monitoring**: Full observability of job processing

## Alternatives Considered

### **1. Synchronous Processing** ❌
- **Pros**: Simple implementation
- **Cons**: Poor UX, blocking, timeouts
- **Verdict**: Rejected due to UX impact

### **2. Server-Sent Events (SSE)** ⚖️
- **Pros**: Real-time updates, simpler than WebSockets
- **Cons**: Less flexible than Pub/Sub for production
- **Verdict**: Consider for future enhancement

### **3. Client-Side Generation** ❌
- **Pros**: No backend complexity
- **Cons**: Limited AI capabilities, resource constraints
- **Verdict**: Rejected due to quality requirements

## Implementation Status

- ✅ **Backend Job Manager**: Async visual manager with worker pool
- ✅ **API Endpoints**: Async generation + polling endpoints  
- ✅ **Frontend Hook**: Real-time status management
- 🔄 **UI Components**: Progressive loading components (in progress)
- 📋 **Testing**: End-to-end async workflow testing (planned)
- 📋 **Monitoring**: Job performance metrics (planned)

## Migration Strategy

### **Phase 1**: Parallel Implementation ✅
- Keep existing sync endpoint for compatibility
- Add new async endpoints
- Test async flow independently

### **Phase 2**: Frontend Integration 🔄
- Update UI components for progressive loading
- Add real-time progress indicators
- Implement proper error handling

### **Phase 3**: Full Migration
- Switch default to async generation
- Remove sync endpoint
- Add performance monitoring

### **Phase 4**: Production Enhancement
- Integrate Google Cloud Pub/Sub
- Add WebSocket support
- Implement auto-scaling

## Conclusion

This async architecture solves the fundamental UX problems while providing a scalable foundation for production deployment. The key insight is **independence**: each content type (text, images, videos) should process completely independently, allowing users to get immediate value from text content while visual content generates in the background.

The implementation provides real-time progress reflection, ensuring the UI accurately represents backend processing state, eliminating the disconnect between loading indicators and actual work being performed.

**This ADR prevents regression by documenting the architectural reasoning and ensuring future development maintains the independence and real-time feedback principles.** 