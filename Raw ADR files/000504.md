# ADR-022: Event-Driven Progress Updates Architecture

**Status**: 🔄 ENHANCED by ADR-023  
**Date**: 2025-06-28  
**Author**: JP + Claude Sonnet  
**Context**: Integrate real-time progress with existing FastAPI infrastructure  

## Context

The current solution has a mature architecture with:
- ✅ **FastAPI + SQLite** - Operational database with 7 tables
- ✅ **ADK Agent Workflow** - Real AI processing via `execute_campaign_workflow()`
- ✅ **Database Persistence** - Campaign and content storage
- ✅ **API Patterns** - 12+ endpoints with proper orchestration

**Problem**: Visual content generation takes 30-60+ seconds with no real-time feedback, but we shouldn't create architectural silos.

## Decision

**Enhance existing FastAPI infrastructure** with event-driven progress updates, leveraging current patterns.

### **Core Principle: Architectural Coherence**
- **Extend, don't replace** existing API endpoints
- **Use SQLite database** for job state tracking
- **Leverage FastAPI SSE** for real-time updates
- **Enhance ADK agents** to emit progress events
- **Maintain current patterns** while adding real-time capabilities

## Architecture Enhancement

### **1. Database-Driven Job Tracking**

Enhance existing SQLite schema with job tracking:

```sql
-- Extend existing database with job tracking
CREATE TABLE IF NOT EXISTS generation_jobs (
    id TEXT PRIMARY KEY,
    campaign_id TEXT NOT NULL,
    job_type TEXT NOT NULL, -- 'text', 'image', 'video'
    status TEXT NOT NULL,   -- 'queued', 'processing', 'completed', 'failed'
    progress REAL NOT NULL DEFAULT 0.0,
    content_id TEXT,
    result_data JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
);

-- Index for efficient queries
CREATE INDEX IF NOT EXISTS idx_generation_jobs_campaign_status 
ON generation_jobs(campaign_id, status);
```

### **2. Enhanced FastAPI Endpoints**

Extend current endpoints with real-time capabilities:

```python
# backend/api/routes/content.py - Enhanced existing endpoints

from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

@router.post("/generate-with-progress")
async def generate_content_with_progress(
    request: ContentGenerationRequest,
    background_tasks: BackgroundTasks
) -> ContentGenerationResponse:
    """Enhanced version of existing /generate endpoint with progress tracking."""
    
    # Create job entries in database
    jobs = await create_generation_jobs(request)
    
    # Start background processing with progress updates
    background_tasks.add_task(
        execute_workflow_with_progress,
        request, jobs
    )
    
    # Return immediate response with job information
    return ContentGenerationResponse(
        jobs=jobs,
        status="processing",
        progress_endpoint=f"/content/progress/{request.campaign_id}"
    )

@router.get("/progress/{campaign_id}")
async def get_progress_stream(campaign_id: str):
    """Server-Sent Events endpoint for real-time progress updates."""
    
    async def event_generator():
        while True:
            # Query database for current job status
            jobs = await get_campaign_jobs(campaign_id)
            
            # Calculate overall progress
            overall_progress = calculate_progress(jobs)
            
            # Send progress update
            yield {
                "event": "progress",
                "data": json.dumps({
                    "campaign_id": campaign_id,
                    "overall_progress": overall_progress,
                    "jobs": jobs,
                    "timestamp": datetime.utcnow().isoformat()
                })
            }
            
            # Stop when all jobs complete
            if all(job.status in ['completed', 'failed'] for job in jobs):
                break
                
            await asyncio.sleep(2)  # Update every 2 seconds
    
    return EventSourceResponse(event_generator())
```

### **3. Progress-Aware ADK Agent Workflow**

Enhance existing ADK agents to emit progress events:

```python
# backend/agents/marketing_orchestrator.py - Enhanced existing workflow

import asyncio
from database.database import update_job_progress

async def execute_campaign_workflow_with_progress(
    business_description: str,
    objective: str,
    **kwargs
) -> dict:
    """Enhanced version of existing workflow with progress tracking."""
    
    campaign_id = kwargs.get('campaign_id')
    
    try:
        # Phase 1: Business Analysis (20% of total)
        await update_job_progress(campaign_id, 'text', 0.1, "Starting business analysis...")
        
        business_analysis = await business_analysis_agent.execute({
            "business_description": business_description,
            "objective": objective
        })
        
        await update_job_progress(campaign_id, 'text', 0.2, "Business analysis complete")
        
        # Phase 2: Content Generation (60% of total)
        await update_job_progress(campaign_id, 'text', 0.3, "Generating social content...")
        
        social_content = await content_generation_agent.execute({
            "business_analysis": business_analysis,
            "post_count": kwargs.get('post_count', 6)
        })
        
        await update_job_progress(campaign_id, 'text', 0.8, "Social content generated")
        
        # Phase 3: Visual Content (if requested)
        if kwargs.get('generate_visuals'):
            await update_job_progress(campaign_id, 'image', 0.1, "Starting image generation...")
            
            # Process images independently
            for i, post in enumerate(social_content.get('posts', [])):
                if post.get('type') in ['text_image', 'text_video']:
                    await generate_post_image(post, campaign_id)
                    progress = (i + 1) / len(social_content['posts'])
                    await update_job_progress(campaign_id, 'image', progress, f"Generated image {i+1}")
        
        await update_job_progress(campaign_id, 'text', 1.0, "Workflow complete")
        
        return {
            "business_analysis": business_analysis,
            "generated_content": social_content,
            "status": "completed"
        }
        
    except Exception as e:
        await update_job_progress(campaign_id, 'text', 0.0, f"Error: {str(e)}", status='failed')
        raise
```

### **4. Frontend Real-Time Integration**

Enhance existing React components with SSE:

```typescript
// src/hooks/useProgressiveGeneration.ts - New hook for existing components

import { useEffect, useState } from 'react';

interface GenerationProgress {
  overall_progress: number;
  jobs: Array<{
    id: string;
    type: 'text' | 'image' | 'video';
    status: string;
    progress: number;
    message: string;
  }>;
}

export function useProgressiveGeneration(campaignId: string) {
  const [progress, setProgress] = useState<GenerationProgress | null>(null);
  const [isComplete, setIsComplete] = useState(false);
  
  useEffect(() => {
    if (!campaignId) return;
    
    // Use existing API patterns but with SSE
    const eventSource = new EventSource(
      `/api/v1/content/progress/${campaignId}`
    );
    
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setProgress(data);
      
      // Check if all jobs are complete
      const allComplete = data.jobs.every(
        job => job.status === 'completed' || job.status === 'failed'
      );
      
      if (allComplete) {
        setIsComplete(true);
        eventSource.close();
      }
    };
    
    return () => eventSource.close();
  }, [campaignId]);
  
  return { progress, isComplete };
}
```

## Production Architecture (Google Cloud)

### **Pub/Sub Migration Path**

```python
# Future enhancement - Google Cloud Pub/Sub integration
from google.cloud import pubsub_v1

class ProgressPublisher:
    def __init__(self):
        self.publisher = pubsub_v1.PublisherClient()
        self.topic_path = self.publisher.topic_path(
            'your-project', 'campaign-progress'
        )
    
    async def publish_progress(self, campaign_id: str, progress_data: dict):
        """Publish progress to Pub/Sub topic."""
        message_data = json.dumps({
            'campaign_id': campaign_id,
            **progress_data
        }).encode('utf-8')
        
        future = self.publisher.publish(
            self.topic_path, 
            message_data
        )
        
        return future.result()

# Cloud Run webhook endpoint
@router.post("/webhooks/progress")
async def receive_progress_webhook(request: dict):
    """Receive progress updates from Pub/Sub."""
    campaign_id = request['campaign_id']
    
    # Update database
    await update_job_progress(**request)
    
    # Broadcast to connected SSE clients
    await broadcast_progress_update(campaign_id, request)
```

## Implementation Benefits

### **1. Architectural Coherence**
- ✅ **Uses existing FastAPI patterns** - No separate async system
- ✅ **Leverages SQLite database** - Existing table structure enhanced
- ✅ **Maintains ADK workflow** - Existing agents emit progress
- ✅ **Consistent API design** - Extends current endpoints

### **2. Real-Time User Experience**
- ✅ **Independent processing** - Text, images, videos process separately
- ✅ **Progressive loading** - Content appears as it's generated
- ✅ **Real progress indication** - Database-driven, not fake spinners
- ✅ **Error resilience** - Individual job failures don't break UX

### **3. Production Scalability**
- ✅ **Database-driven state** - Survives server restarts
- ✅ **Google Cloud ready** - Easy Pub/Sub migration
- ✅ **Resource efficient** - No additional infrastructure needed
- ✅ **Monitoring friendly** - All events stored in database

## Implementation Strategy

### **Phase 1: Database Enhancement**
- Add `generation_jobs` table to existing SQLite schema
- Create progress tracking functions
- Test with existing workflow

### **Phase 2: FastAPI SSE Integration**
- Add Server-Sent Events endpoint to existing routes
- Enhance existing content generation endpoints
- Test real-time progress updates

### **Phase 3: ADK Agent Enhancement**
- Add progress callbacks to existing agent workflow
- Ensure independent processing for visual content
- Maintain existing API contracts

### **Phase 4: Frontend Integration**
- Create progressive loading components
- Integrate with existing UI patterns
- Test end-to-end user experience

### **Phase 5: Production Migration**
- Migrate to Google Cloud Pub/Sub
- Add WebSocket support for bi-directional communication
- Implement auto-scaling based on job queue depth

## Success Metrics

- **Architectural**: No duplicate code, uses existing patterns
- **Performance**: < 2s for initial response, real-time progress updates
- **UX**: Independent content types, progressive loading
- **Scalability**: Database-driven state, Google Cloud ready

## Conclusion

This approach **enhances rather than replaces** the existing mature architecture. By using FastAPI SSE, SQLite job tracking, and progress-aware ADK agents, we get real-time user experience while maintaining architectural coherence.

**Key insight**: The existing FastAPI + SQLite + ADK infrastructure is the **single source of truth** for both API responses AND real-time progress updates. 