# ADR-009: Store CV and Job Description Content with Analysis Results

**Date**: 2026-01-01  
**Status**: Accepted  
**Decision Makers**: Architecture Team  
**Technical Story**: Phase 2 - Tabbed Analysis Report Interface (Feature 4B)

## Context

The tabbed analysis report interface (Feature 4B) introduces a comprehensive view where users can see:
- **Analysis Tab**: Scores, recommendations, strengths, gaps
- **CV Tab**: The full CV content that was analyzed
- **Job Description Tab**: The full job description that was analyzed

### Current State

In the Phase 1 implementation:
- **Frontend → Backend**: CV markdown and job description sent to `/api/v1/analyze` endpoint
- **Backend Processing**: Analysis agents process these inputs and generate results
- **Backend → Frontend**: Only analysis results returned (scores, recommendations, strengths, gaps)
- **Storage**: Only analysis results stored in CosmosDB
- **Missing**: CV and job description content not stored or returned

**Current Analysis Document Schema:**
```json
{
  "id": "analysis-abc123",
  "type": "analysis",
  "userId": "user-xyz789",
  "overallScore": 85,
  "scores": { "skills": 90, "experience": 80 },
  "recommendations": ["..."],
  "strengths": ["..."],
  "gaps": ["..."],
  "analyzedAt": "2026-01-01T12:00:00Z"
}
```

### Problem

**For Current Analysis (just submitted):**
- Frontend has CV and job in component state → can display in tabs ✅
- Works fine until user refreshes page or navigates away ❌

**For Historical Analysis (from history view):**
- Frontend fetches analysis from `/api/v1/analyses` endpoint
- Gets scores and recommendations ✅
- **Cannot display CV or Job tabs** because content not stored ❌
- User sees "No data available" or missing tabs

**User Experience Gap:**
- **Current runs**: Show all 3 tabs (Analysis, CV, Job)
- **Historical runs**: Only show Analysis tab
- **Inconsistent interface**: Users confused why history missing CV/Job content
- **No context**: Cannot see what they submitted for past analyses

### Requirements from Feature 4B

From [PRD Feature 4B](../features/tabbed-analysis-report.md) and [Frontend FRD FR-FE6](../frontend-frd.md#fr-fe6):
- Display CV content in dedicated tab
- Display job description in dedicated tab
- **Must work for both current AND historical analyses**
- User should be able to review what they submitted in the past
- Tabs should be identical whether viewing current or historical analysis

### Options Considered

**Option 1: Frontend-Only State Management**
- Store CV/job in frontend state (React context or localStorage)
- Pros: No backend changes, minimal implementation
- Cons: Only works for current session, doesn't support historical analyses

**Option 2: Store with Analysis in CosmosDB** ⭐ (Chosen)
- Store full cv_markdown and job_description with each analysis document
- Pros: Single source of truth, supports historical access, consistent UX
- Cons: Increased storage costs, data duplication

**Option 3: Separate CV/Job Collections with References**
- Store CVs and jobs in separate documents, reference by ID in analysis
- Pros: No data duplication if same CV analyzed multiple times
- Cons: Complex queries (multi-document reads), doesn't solve fundamental need

## Decision

We will **store the full cv_markdown and job_description content with each analysis result** in CosmosDB and return them in the API response.

### Modified Analysis Document Schema

**New Fields Added:**
```typescript
interface Analysis {
  // Existing fields
  id: string;
  type: 'analysis';
  userId: string;
  overallScore: number;
  scores: { skills: number; experience: number; education: number; cultural_fit: number };
  recommendations: string[];
  strengths: string[];
  gaps: string[];
  analyzedAt: string;
  
  // NEW FIELDS
  cv_markdown: string;           // Full CV content in Markdown format
  job_description: string;        // Full job description text
  source_type: 'manual' | 'linkedin_url';  // How job was provided
  source_url?: string;            // LinkedIn URL if applicable (optional)
}
```

**Example Analysis Document:**
```json
{
  "id": "analysis-abc123",
  "type": "analysis",
  "userId": "user-xyz789",
  "overallScore": 85,
  "scores": {
    "skills": 90,
    "experience": 80,
    "education": 85,
    "cultural_fit": 88
  },
  "recommendations": [
    "Add cloud certifications to stand out",
    "Quantify project impact with metrics"
  ],
  "strengths": [
    "Strong Python and FastAPI experience",
    "Cloud-native architecture knowledge"
  ],
  "gaps": [
    "Limited Kubernetes experience",
    "No mention of CI/CD pipelines"
  ],
  "cv_markdown": "# John Doe\n\n## Experience\n\n**Senior Software Engineer** at TechCorp...",
  "job_description": "We are seeking a Senior Backend Engineer with expertise in...",
  "source_type": "linkedin_url",
  "source_url": "https://www.linkedin.com/jobs/view/123456789",
  "analyzedAt": "2026-01-01T12:00:00Z"
}
```

### Backend API Changes

**POST /api/v1/analyze Response:**
```json
{
  "analysis": {
    "overallScore": 85,
    "scores": {...},
    "recommendations": [...],
    "strengths": [...],
    "gaps": [...],
    "cv_markdown": "# John Doe...",
    "job_description": "We are seeking...",
    "source_type": "manual",
    "source_url": null,
    "analyzedAt": "2026-01-01T12:00:00Z"
  }
}
```

**GET /api/v1/analyses Response:**
```json
{
  "analyses": [
    {
      "id": "analysis-abc123",
      "overallScore": 85,
      "cv_markdown": "# John Doe...",
      "job_description": "We are seeking...",
      "analyzedAt": "2026-01-01T12:00:00Z"
    }
  ]
}
```

### Frontend Display Logic

```typescript
// src/components/AnalysisReport.tsx
interface AnalysisReportProps {
  analysis: Analysis;  // Contains cv_markdown and job_description
}

export function AnalysisReport({ analysis }: AnalysisReportProps) {
  return (
    <Tabs defaultValue="analysis">
      <TabsList>
        <TabsTrigger value="analysis">Analysis</TabsTrigger>
        <TabsTrigger value="cv">CV</TabsTrigger>
        <TabsTrigger value="job">Job Description</TabsTrigger>
      </TabsList>
      
      <TabsContent value="analysis">
        <ScoreDisplay scores={analysis.scores} />
        <RecommendationsList items={analysis.recommendations} />
      </TabsContent>
      
      <TabsContent value="cv">
        <MarkdownDisplay content={analysis.cv_markdown} />
      </TabsContent>
      
      <TabsContent value="job">
        <MarkdownDisplay content={analysis.job_description} />
      </TabsContent>
    </Tabs>
  );
}
```

**Works identically for:**
- Current analysis (just submitted)
- Historical analysis (fetched from API)

## Consequences

### Positive

**Data Completeness**
- ✅ Each analysis is self-contained with full context
- ✅ Historical analyses include all information user submitted
- ✅ No orphaned references or missing data scenarios

**User Experience**
- ✅ Consistent interface: current and historical analyses display identically
- ✅ Users can review exactly what they submitted
- ✅ "Did I apply to this job before?" question answered by viewing past submissions
- ✅ Side-by-side comparison: open two analyses, compare CVs and scores

**Single Source of Truth**
- ✅ CosmosDB is authoritative for all analysis data
- ✅ No state synchronization between frontend and backend
- ✅ Refresh/navigation doesn't lose data
- ✅ Works across devices (if user ID shared via authentication in Phase 3)

**Future-Proof Architecture**
- ✅ Supports data export ("Download My Data" GDPR feature)
- ✅ Enables analytics: "Which job descriptions get highest match scores?"
- ✅ Supports multi-device access (Phase 3 with authentication)
- ✅ Enables diff view: "What changed in my CV between analyses?"

**Simplified Frontend**
- ✅ No need to manage separate display state for current vs. historical
- ✅ Single `<AnalysisReport>` component works for all cases
- ✅ No complex localStorage management for CV/job content
- ✅ Fewer edge cases and error states

### Negative

**Increased Storage Costs**
- ❌ Each analysis stores full CV and job text
- ❌ Average analysis size increases from ~2KB to ~12KB (6x larger)
- ❌ 1,000 analyses: 2MB → 12MB storage (still negligible cost)
- ❌ More significant at scale: 100,000 analyses = 1.2GB storage

**Data Duplication**
- ❌ Same CV analyzed against 10 different jobs → CV stored 10 times
- ❌ Popular job description → duplicated across multiple users' analyses
- ❌ No deduplication at storage level

**Storage Size Estimates**
- **CV**: ~5KB (average Markdown resume)
- **Job Description**: ~3KB (average posting)
- **Analysis Results**: ~2KB (scores + recommendations)
- **Metadata**: ~1KB (timestamps, IDs, source info)
- **Total per Analysis**: ~11KB

**Cost Impact (CosmosDB Serverless):**
- **Storage**: $0.25 per GB/month
- 1,000 analyses × 11KB = 11MB = **$0.003/month**
- 100,000 analyses × 11KB = 1.1GB = **$0.28/month**
- **Negligible compared to compute costs** (RU consumption for writes)

**Write RU Impact:**
- Larger documents consume more RUs on write
- 2KB document: ~5 RU to write
- 11KB document: ~12 RU to write (2.4x increase)
- **Mitigation**: Still within budget (see ADR-008 RU monitoring)

### Mitigation Strategies

**1. Use CosmosDB Serverless Tier**
- Pay only for actual storage used (no fixed costs)
- $0.25/GB/month is cost-effective for MVP scale
- 10,000 analyses = ~110MB = $0.03/month

**2. Implement Data Retention Policy (Phase 3)**
- Auto-delete analyses older than 6 months
- Configurable per-user: "Keep my data for X months"
- Reduces long-term storage costs
- Example: 6-month retention → max 6 months × 1,000 analyses/month = 6,000 analyses × 11KB = 66MB

**3. Compress Large Documents (Future Optimization)**
- If individual CVs exceed 20KB, apply gzip compression before storage
- CosmosDB supports binary data (store compressed blob)
- Decompress on read (minimal CPU overhead)
- Example: 50KB CV → 15KB compressed (70% reduction)

**4. Indexing Policy Optimization**
- Exclude large text fields from indexing (reduce write RUs)
- Only index queryable fields (userId, type, analyzedAt, overallScore)
```json
{
  "indexingPolicy": {
    "excludedPaths": [
      { "path": "/cv_markdown/*" },
      { "path": "/job_description/*" },
      { "path": "/recommendations/*" },
      { "path": "/strengths/*" },
      { "path": "/gaps/*" }
    ]
  }
}
```

**5. Monitor Storage Growth**
- Azure Portal Metrics: Track total storage size
- Alert when storage exceeds 1GB (indicates high usage or retention issue)
- Review retention policy effectiveness quarterly

## Alternatives Considered

### Alternative 1: Frontend-Only State Management

**Description:**
Store CV and job description only in frontend state (React context, localStorage, or sessionStorage).

**Implementation:**
```typescript
// Store in localStorage when analysis submitted
localStorage.setItem(`cv-${analysisId}`, cvMarkdown);
localStorage.setItem(`job-${analysisId}`, jobDescription);

// Retrieve when displaying historical analysis
const cv = localStorage.getItem(`cv-${analysisId}`);
const job = localStorage.getItem(`job-${analysisId}`);
```

**Pros:**
- ✅ No backend changes required
- ✅ Zero storage cost (uses browser storage)
- ✅ Fast access (no API call for CV/job content)

**Cons:**
- ❌ **Doesn't work for historical analyses fetched from API**
  - User clears browser data → all CV/job content lost
  - User switches devices → cannot access CV/job content
  - localStorage limited to 5-10MB → cannot store hundreds of analyses
- ❌ **Inconsistent user experience**
  - Current analysis: Shows all 3 tabs ✅
  - Historical analysis fetched from API: Missing CV/Job tabs ❌
- ❌ **No cross-device support**
  - User analyzes on laptop, views history on phone → missing content
- ❌ **Complex state management**
  - Must sync localStorage with API responses
  - Handle edge cases (localStorage full, data corruption, expired entries)
- ❌ **Doesn't scale to Phase 3 features**
  - Multi-user accounts require server-side storage
  - Data export requires backend access to full data

**Rejection Rationale:**
This approach only solves the problem for current session and breaks down for historical analyses. The core requirement is **consistent display for current AND historical analyses**, which frontend-only state cannot provide.

---

### Alternative 2: Separate CV/Job Collections with References

**Description:**
Create separate collections (containers) for CVs and Jobs, store them once, reference by ID in analysis documents.

**Schema Design:**
```json
// CV Document (in "cvs" container)
{
  "id": "cv-abc123",
  "type": "cv",
  "userId": "user-xyz789",
  "content": "# John Doe\n\n## Experience...",
  "uploadedAt": "2026-01-01T12:00:00Z"
}

// Job Document (in "jobs" container)
{
  "id": "job-def456",
  "type": "job",
  "userId": "user-xyz789",
  "description": "We are seeking a Senior Backend Engineer...",
  "source_type": "linkedin_url",
  "source_url": "https://linkedin.com/jobs/123",
  "createdAt": "2026-01-01T12:00:00Z"
}

// Analysis Document (in "analyses" container)
{
  "id": "analysis-ghi789",
  "type": "analysis",
  "userId": "user-xyz789",
  "cvId": "cv-abc123",         // Reference to CV
  "jobId": "job-def456",       // Reference to Job
  "overallScore": 85,
  "recommendations": [...],
  "analyzedAt": "2026-01-01T12:00:00Z"
}
```

**Pros:**
- ✅ No data duplication: CV stored once, referenced by multiple analyses
- ✅ Efficient storage: 100 analyses of same CV → 1 CV copy + 100 references
- ✅ Supports future features: "Show all analyses for this CV", "Compare all jobs I analyzed against"

**Cons:**
- ❌ **Complex queries**: Fetching historical analysis requires 3 API calls
  1. GET /api/v1/analyses/{id} → returns cvId and jobId
  2. GET /api/v1/cvs/{cvId} → returns CV content
  3. GET /api/v1/jobs/{jobId} → returns job content
- ❌ **Increased latency**: 3 round-trips to CosmosDB vs. 1 (especially problematic on slow connections)
- ❌ **Higher RU consumption**: 3 separate read operations (3× RU cost per historical view)
- ❌ **More API endpoints**: Must implement CRUD for CVs, Jobs, Analyses (vs. just Analyses)
- ❌ **Orphaned data management**:
  - Delete analysis → CV and Job orphaned (no references)
  - Need garbage collection to clean up unused CVs/Jobs
- ❌ **Doesn't solve fundamental problem**: User still wants to see CV/job with historical analysis
  - Frontend must make 3 API calls and assemble data client-side
  - More complex than simply storing content with analysis
- ❌ **MVP over-engineering**: Premature optimization for deduplication
  - Adds complexity without proven benefit (storage cost is negligible at MVP scale)
  - Would revisit if storage costs become significant (Phase 3+)

**Additional Complexity:**
- **Transaction Management**: If user deletes analysis, should CV/Job be deleted?
  - Need reference counting or soft deletes
  - Adds complexity to delete operations
- **Container Management**: 3 containers vs. 1 (ADR-008 uses single container)
  - More RU consumption (queries across containers)
  - More complex partitioning strategy

**Rejection Rationale:**
This approach optimizes for storage deduplication at the cost of query complexity and latency. At MVP scale, storage costs are negligible ($0.03/month for 10,000 analyses), but query complexity is significant (3× API calls, 3× RU consumption, 3× latency). The architectural complexity doesn't justify the minimal storage savings.

**Future Consideration:**
If storage costs become problematic (e.g., millions of analyses, multi-GB storage), we can migrate to this model in Phase 4+. The abstraction layer (Repository pattern from ADR-004) makes this migration straightforward without frontend changes.

---

### Alternative 3: Store Hashed References with Content Deduplication

**Description:**
Store CV/job content with hash-based deduplication: identical content stored once, referenced by SHA-256 hash.

**Schema Design:**
```json
// Content Store (deduplicated)
{
  "id": "content-sha256-abc...",
  "content": "# John Doe\n\n## Experience...",
  "type": "cv",
  "hash": "sha256:abc123def456..."
}

// Analysis Document
{
  "id": "analysis-ghi789",
  "cvHash": "sha256:abc123def456...",
  "jobHash": "sha256:xyz789...",
  "overallScore": 85,
  ...
}
```

**Pros:**
- ✅ Automatic deduplication: identical CVs stored once
- ✅ No manual reference management

**Cons:**
- ❌ **Immutable content**: Any CV change (even typo fix) creates new hash
  - User updates "Senior Engineer" → "Staff Engineer"
  - New hash generated → content duplicated again
  - Defeats deduplication purpose for evolving CVs
- ❌ **Complex retrieval**: Must hash content on read to look up
- ❌ **Poor developer experience**: Debugging requires hash lookup
- ❌ **No versioning**: Cannot track CV evolution over time

**Rejection Rationale:**
Over-engineered for problem domain. CVs change frequently, making content-addressable storage ineffective.

## Related Documents

**Product Requirements:**
- [PRD Section 3.4.2: Feature 4B - Tabbed Analysis Report Interface](../prd.md#342-feature-4b-tabbed-analysis-report-interface)

**Functional Requirements:**
- [Frontend FRD FR-FE6: Tabbed Analysis Report Interface](../frontend-frd.md#fr-fe6-tabbed-analysis-report-interface)

**Architecture Decisions:**
- [ADR-004: No Database v1, Future Storage Design](ADR-004-no-database-v1-future-storage-design.md) - Defined initial data models
- [ADR-008: Cosmos DB for Data Persistence](ADR-008-cosmos-db-data-persistence.md) - Storage infrastructure decision

**Implementation:**
- [Backend Phase 1-2 Summary](../../backend/IMPLEMENTATION_STATUS.md) - Analysis endpoint implementation
- [Frontend Phase 3 Delivery](../../frontend/PHASE3_DELIVERY.md) - Tabbed report interface

## Implementation Checklist

**Backend Changes:**

- [ ] Update `Analysis` Pydantic model with new fields:
  - `cv_markdown: str`
  - `job_description: str`
  - `source_type: Literal['manual', 'linkedin_url']`
  - `source_url: Optional[str]`

- [ ] Modify `POST /api/v1/analyze` endpoint:
  - Store cv_markdown in analysis document
  - Store job_description in analysis document
  - Store source_type and source_url (if applicable)
  - Return all fields in response

- [ ] Modify `GET /api/v1/analyses` endpoint:
  - Include cv_markdown and job_description in response
  - Update API documentation (OpenAPI schema)

- [ ] Update CosmosDB indexing policy:
  - Exclude `/cv_markdown/*` from indexing
  - Exclude `/job_description/*` from indexing
  - Reduces write RU consumption

- [ ] Add input validation:
  - cv_markdown max size: 100KB
  - job_description max size: 50KB
  - Prevents oversized documents

**Frontend Changes:**

- [ ] Update `Analysis` TypeScript interface:
  - Add `cv_markdown: string`
  - Add `job_description: string`
  - Add `source_type: 'manual' | 'linkedin_url'`
  - Add `source_url?: string`

- [ ] Modify `AnalysisReport` component:
  - Display CV in dedicated tab (Markdown rendering)
  - Display Job in dedicated tab (text display)
  - Show source badge if `source_type === 'linkedin_url'`
  - Link to original posting if `source_url` present

- [ ] Update API client:
  - Expect new fields in `/api/v1/analyze` response
  - Expect new fields in `/api/v1/analyses` response

**Testing:**

- [ ] Backend unit tests:
  - Verify analysis document includes cv_markdown and job_description
  - Verify API responses include new fields
  - Test input validation (size limits)

- [ ] Frontend integration tests:
  - Verify CV tab displays content correctly
  - Verify Job tab displays content correctly
  - Verify historical analyses show all tabs

- [ ] E2E tests:
  - Submit analysis → verify all tabs visible
  - Fetch historical analysis → verify all tabs visible
  - Refresh page → verify data persists

**Documentation:**

- [ ] Update API documentation:
  - Document new fields in OpenAPI schema
  - Add examples to `/api/v1/analyze` endpoint
  - Update `/api/v1/analyses` response schema

- [ ] Update Frontend README:
  - Document `Analysis` interface changes
  - Update component usage examples

**Deployment:**

- [ ] Update CosmosDB container indexing policy (production)
- [ ] Monitor RU consumption after deployment (first 48 hours)
- [ ] Verify storage growth aligns with estimates

## References

**Azure Cosmos DB:**
- [Indexing Policies](https://learn.microsoft.com/azure/cosmos-db/index-policy)
- [Optimize Costs with Indexing](https://learn.microsoft.com/azure/cosmos-db/nosql/optimize-indexing-policy)
- [Request Unit Consumption](https://learn.microsoft.com/azure/cosmos-db/request-units)

**Design Patterns:**
- [Single Source of Truth](https://en.wikipedia.org/wiki/Single_source_of_truth)
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html) (Martin Fowler)

**Related Features:**
- [Feature 4B: Tabbed Analysis Report](../features/tabbed-analysis-report.md)
- [Data Persistence Requirements](../features/data-persistence.md)
