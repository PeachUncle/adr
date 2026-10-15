# ADR-008: Azure Cosmos DB for Data Persistence

**Date**: 2026-01-01  
**Status**: Accepted  
**Decision Makers**: Architecture Team  
**Technical Story**: Phase 2 - Data Persistence & Storage

## Context

CV Checker v1 operates as a stateless application where all data processing happens in-memory during the request lifecycle. While this approach enabled rapid MVP delivery without infrastructure complexity, it creates significant limitations:

### Current State Pain Points

- **No Data Persistence**: Analysis results are lost when users refresh the page or close their browser
- **Redundant Work**: Users must re-upload CVs every time they want to analyze against a different job description
- **No Historical Context**: Users cannot track how CV changes affect match scores over time
- **Poor User Retention**: Lack of saved state reduces incentive for return visits
- **Limited Product Value**: Cannot provide iterative improvement features or analytics

### User Requirements

Based on user feedback and product vision, we need to:

1. **Store CVs persistently** so users can analyze the same CV against multiple job descriptions
2. **Store job descriptions** to enable re-analysis and comparison across multiple CVs
3. **Store analysis results** to provide historical tracking and progress insights
4. **Support session-based user identification** without requiring authentication (Phase 2)
5. **Enable seamless local development** without Azure cloud dependencies
6. **Maintain production-ready scalability** for future growth

### Technical Constraints

- **No Authentication Yet**: Phase 2 focuses on storage; authentication comes in Phase 3
- **User Identification**: Must use session-based UUID stored in browser localStorage
- **Local Development**: Developers need to run full stack locally without Azure subscriptions
- **Cost Sensitivity**: MVP deployment must minimize infrastructure costs
- **Scalability Path**: Solution must support future multi-region, multi-user scenarios

## Decision

We will use **Azure Cosmos DB** (NoSQL, serverless tier) with the following design:

### Core Architecture

1. **Single Container Design**
   - Container Name: `cv-checker-data`
   - Partition Key: `/userId` (session UUID from frontend)
   - Entity Types: Differentiated by `type` field (`"cv"`, `"job"`, `"analysis"`)

2. **Data Model**
   - **CV Documents**: Store markdown content, metadata (filename, size, upload timestamp)
   - **Job Documents**: Store job descriptions, source type (manual/LinkedIn), extracted title
   - **Analysis Documents**: Store scores, recommendations, references to CV and job

3. **User Identification**
   - Frontend generates UUID v4 on first visit: `user-{uuid}`
   - Stored in browser localStorage: `cv-checker-userId`
   - Included in all API requests via `X-User-Id` header
   - No server-side session management or authentication required

4. **Local Development**
   - Cosmos DB Linux Emulator via Docker Compose
   - Default emulator connection string (well-known account key)
   - Database/container auto-created on backend startup
   - No Azure cloud resources required for development

5. **Production Deployment**
   - Azure Cosmos DB serverless tier
   - Connection string from environment variable (`COSMOS_CONNECTION_STRING`)
   - Same codebase, zero changes between local and production
   - Configuration-driven environment swap

### Python SDK Integration

```python
from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey
import os

# Initialize Cosmos Client
client = CosmosClient.from_connection_string(
    os.getenv("COSMOS_CONNECTION_STRING")
)

# Get/create database and container
async def init_database():
    database = await client.create_database_if_not_exists(id="cv-checker-db")
    container = await database.create_container_if_not_exists(
        id="cv-checker-data",
        partition_key=PartitionKey(path="/userId"),
        offer_throughput=None  # Serverless
    )
    return container

# Example: Store CV
async def store_cv(user_id: str, content: str, filename: str):
    cv_document = {
        "id": f"cv-{uuid4()}",
        "type": "cv",
        "userId": user_id,
        "content": content,
        "filename": filename,
        "fileSize": len(content),
        "uploadedAt": datetime.utcnow().isoformat()
    }
    await container.create_item(body=cv_document)
    return cv_document["id"]

# Example: Query user's analyses
async def get_user_analyses(user_id: str, limit: int = 10):
    query = """
    SELECT * FROM c 
    WHERE c.userId = @user_id AND c.type = 'analysis' 
    ORDER BY c.analyzedAt DESC 
    OFFSET 0 LIMIT @limit
    """
    items = container.query_items(
        query=query,
        parameters=[
            {"name": "@user_id", "value": user_id},
            {"name": "@limit", "value": limit}
        ],
        partition_key=user_id
    )
    return [item async for item in items]
```

### Container Schema Design

**Partition Strategy:**
- Partition Key: `/userId`
- Rationale: All user data co-located in single partition for efficient queries
- Limitation: Single user cannot exceed 20GB (acceptable for MVP, hundreds of CVs)
- Future: Hierarchical partition keys (`/userId`, `/type`) if scaling beyond 20GB per user

**Indexing Policy:**
```json
{
  "indexingPolicy": {
    "automatic": true,
    "includedPaths": [
      { "path": "/userId/*" },
      { "path": "/type/*" },
      { "path": "/analyzedAt/*" },
      { "path": "/overallScore/*" },
      { "path": "/cvId/*" },
      { "path": "/jobId/*" }
    ],
    "excludedPaths": [
      { "path": "/content/*" },
      { "path": "/recommendations/*" }
    ]
  }
}
```

**Rationale:**
- Include frequently queried fields (userId, type, timestamps, scores)
- Exclude large text fields (CV content, recommendations) to reduce index size and RU consumption
- Optimize for common access patterns: listing analyses by date, filtering by score

## Alternatives Considered

### Alternative 1: Azure SQL Database (Relational)

**Description:** Use Azure SQL Database with normalized tables (Users, CVs, Jobs, Analyses).

**Pros:**
- Strong consistency and ACID transactions
- Familiar SQL query language
- Robust tooling (Azure Data Studio, SSMS)
- Well-established patterns for relational data

**Cons:**
- **Over-engineered for document storage**: CVs and analysis results are inherently document-structured (JSON)
- **Schema rigidity**: Changing analysis output format requires schema migrations
- **Cost**: Minimum Basic tier ~$5/month even with zero usage (no true serverless)
- **Partitioning complexity**: Horizontal scaling requires manual sharding
- **Local development**: SQL Server Docker image is heavyweight (3GB+)

**Rejection Rationale:** CV Checker stores semi-structured documents (Markdown CVs, JSON analyses) that don't benefit from relational constraints. NoSQL flexibility better matches our evolving data model.

---

### Alternative 2: Azure Table Storage (Simple Key-Value)

**Description:** Use Azure Table Storage with partitioning by userId.

**Pros:**
- Lowest cost (~$0.045 per GB/month storage)
- Simple key-value API
- Native Azure integration
- Good for high-volume, low-complexity data

**Cons:**
- **Limited querying**: Only supports partition key + row key queries (no ORDER BY, no complex filters)
- **No indexing**: Cannot efficiently query by `analyzedAt` or `overallScore` without scanning all rows
- **Size limits**: 1MB per entity (large CVs or verbose recommendations may exceed)
- **No local emulator**: Azurite emulator exists but has compatibility gaps
- **Poor developer experience**: Primitive API compared to Cosmos DB SDK

**Rejection Rationale:** Table Storage's query limitations prevent building features like "sort by score" or "filter by date range". These are critical for analysis history UX.

---

### Alternative 3: Azure Blob Storage (File-Based)

**Description:** Store each CV, job, and analysis as separate JSON/Markdown files in Blob Storage.

**Pros:**
- Cheapest storage option (~$0.018 per GB/month)
- Unlimited file size
- Simple read/write operations
- Blob versioning supports historical tracking

**Cons:**
- **No querying**: Cannot list "all analyses sorted by score" without custom indexing layer
- **Manual indexing**: Would need separate index (Cosmos DB or SQL) to enable search, defeating the purpose
- **Poor performance**: Listing files in large directories is slow
- **Complex access patterns**: Implementing pagination, filtering, sorting requires custom code
- **Concurrency issues**: No built-in locking for concurrent writes

**Rejection Rationale:** Blob Storage is excellent for large binary files but poor for queryable structured data. We'd end up building a custom database on top of it.

---

### Alternative 4: In-Memory Only (Current State)

**Description:** Continue with stateless processing, no persistent storage.

**Pros:**
- Zero infrastructure costs
- Simplest possible architecture
- No data management overhead
- Fast development iteration

**Cons:**
- **No user retention**: Users lose all data on page refresh
- **No historical tracking**: Cannot implement core product features (progress tracking, score comparison)
- **Limited product value**: Positioned as disposable tool, not serious career assistant
- **Poor competitive position**: All similar tools offer data persistence

**Rejection Rationale:** Persistence is a core Phase 2 requirement. Staying stateless blocks all future feature development and user retention goals.

---

### Why Cosmos DB Was Chosen

**Decision Factors:**

1. **Document Model Alignment**: CVs (Markdown), Jobs (text), Analyses (JSON) are naturally document-structured
2. **Flexible Schema**: Analysis output evolves (new scoring algorithms, additional recommendations) without migrations
3. **Query Capabilities**: Supports SQL-like queries (ORDER BY, WHERE, pagination) critical for history features
4. **True Serverless**: Pay-per-request pricing ($0.25/million RU operations), ideal for MVP with unpredictable traffic
5. **Local Emulator**: Cosmos DB Linux Emulator provides full-fidelity local development (identical API to production)
6. **Scalability Path**: Supports global distribution, multi-region writes, automatic partitioning for future growth
7. **Python SDK Maturity**: Robust async SDK with excellent documentation and error handling
8. **Single Container Efficiency**: All entity types in one container reduces RU costs (queries within single partition are cheap)
9. **Developer Experience**: Superior tooling (Azure Portal Data Explorer), monitoring (Insights), and debugging

## Consequences

### Positive

**Technical Benefits:**
- **Flexible Data Model**: JSON documents adapt to changing analysis algorithms without schema migrations
- **Efficient Querying**: Partition-level queries (all data for one user) are fast and cheap (low RU consumption)
- **Local Development Parity**: Emulator provides identical API/behavior to production (no "works on my machine" issues)
- **Async Python SDK**: Native async/await support integrates cleanly with FastAPI
- **Automatic Indexing**: Cosmos DB indexes all fields by default (can optimize later if needed)
- **Built-in Metrics**: Azure Monitor integration for latency, RU consumption, error rates out-of-the-box

**Business Benefits:**
- **User Retention**: Persistent data encourages return visits (target: 50% 7-day return rate)
- **Feature Enablement**: Unlocks Phase 3 features (score trends, CV comparison, export)
- **Cost Efficiency**: Serverless tier scales from zero ($0 with no usage) to production (pay only for actual requests)
- **Time to Market**: Docker Compose setup allows developers to start coding immediately without Azure setup
- **Production Ready**: Same codebase deploys to Azure with zero code changes (config-driven)

**Developer Experience:**
- **Simple Setup**: `docker-compose up -d` → database ready in 30 seconds
- **No Cloud Dependencies**: Developers work offline (emulator runs locally)
- **Familiar Patterns**: Repository pattern, dependency injection, async/await—standard Python practices
- **Clear Migration Path**: ADR-004's repository abstraction makes Cosmos DB integration straightforward

### Negative

**Learning Curve:**
- **NoSQL Mindset Shift**: Developers familiar with SQL must learn partition key design, RU optimization
- **Query Limitations**: No JOINs (must denormalize data or make multiple queries)
- **Consistency Tradeoffs**: Session consistency (default) means eventual consistency across regions (not relevant for single-region MVP)

**Cost Considerations:**
- **RU Consumption Monitoring Required**: Inefficient queries can spike costs (e.g., cross-partition queries)
- **No Fixed Cost Ceiling**: Serverless pricing is unpredictable (unlike provisioned throughput with budget caps)
- **Indexing Costs**: Every indexed field consumes RU on write operations (must exclude large text fields)

**Operational Complexity:**
- **Docker Requirement**: Local development requires Docker Desktop (6GB RAM recommended for emulator)
- **Emulator Limitations**: Self-signed SSL certificate requires disabling verification in SDK (local only)
- **Connection String Management**: Production secret (AccountKey) must be secured in Key Vault or App Service settings
- **No ACID Transactions**: Multi-document updates not atomic (acceptable for our use case)

### Mitigation Strategies

**Addressing Learning Curve:**
- Provide clear documentation with partition key design rationale (see FRD data model section)
- Include code examples in repository pattern for common operations (create, query, delete)
- Reference Cosmos DB best practices documentation in README
- Team knowledge-sharing session on NoSQL fundamentals

**Addressing Cost Concerns:**
- Implement custom indexing policy (exclude content, recommendations) to reduce write RUs
- Use partition-scoped queries exclusively (avoid cross-partition queries)
- Set up Azure Monitor alerts for RU consumption spikes (e.g., >10,000 RU/hour)
- Budget: Estimate $10-20/month for 1,000 analyses (validate with Azure Pricing Calculator)

**Addressing Operational Complexity:**
- Docker Compose includes health checks for Cosmos DB emulator readiness
- Backend initialization script auto-creates database/container (idempotent, safe to run repeatedly)
- `.env.example` file documents required environment variables
- Production deployment uses Azure Key Vault for connection string (not hardcoded)

### Neutral Consequences

**Developer Tooling:**
- Requires Docker Desktop installation (one-time setup burden)
- Emulator UI at `https://localhost:8081/_explorer` provides data inspection (useful but not mandatory)
- Python SDK includes diagnostic logging (helpful for debugging RU consumption)

**Data Management:**
- No built-in versioning (unlike Git) → must implement manually if CV version history needed (Phase 3 feature)
- No automatic backups on serverless tier → Azure handles point-in-time restore (up to 30 days)
- User data deletion requires API implementation (`DELETE /api/v1/users/{userId}/data`)

## Implementation Notes

### Partition Key Design

**Choice: `/userId`**
- **Path:** `/userId` (the partition key path in Cosmos DB container definition)
- **Field Value:** The actual UUID stored in the document's `userId` field (e.g., `"user-abc123def456"`)
- **Important Distinction:** 
  - The partition key **path** is `/userId` (tells Cosmos DB which field to use)
  - The partition key **value** is the specific user's UUID (e.g., `"user-{uuid}`), NOT a static string like `"cv"`, `"job"`, or `"analysis"`
  - Each user's data is isolated in their own logical partition identified by their unique userId value
- **Pros:** All user data co-located → single-partition queries (fast, cheap)
- **Cons:** Single user cannot exceed 20GB (acceptable—thousands of CVs per user)
- **Future:** If users exceed 20GB, migrate to hierarchical partition keys (subpartition by `/type` or `/date`)

**Example Documents in Same Partition:**
```json
// All these documents share userId "user-abc123" → same partition
{
  "id": "cv-111",
  "type": "cv",
  "userId": "user-abc123",  // Partition key value
  ...
}
{
  "id": "job-222",
  "type": "job",
  "userId": "user-abc123",  // Same partition
  ...
}
{
  "id": "analysis-333",
  "type": "analysis",
  "userId": "user-abc123",  // Same partition
  ...
}

// Different user → different partition
{
  "id": "cv-444",
  "type": "cv",
  "userId": "user-xyz789",  // Different partition
  ...
}
```

**Alternative Considered: `/type`**
- **Pros:** Distributes data across multiple partitions (better for global scale)
- **Cons:** Queries like "all analyses for user X" become cross-partition (slow, expensive)
- **Rejection:** User-scoped queries are 99% of access patterns; optimizing for this case

---

### Document Type Discrimination

**Pattern: Single container with `type` field**
```json
{ "type": "cv", "userId": "user-123", ... }
{ "type": "job", "userId": "user-123", ... }
{ "type": "analysis", "userId": "user-123", ... }
```

**Alternative: Separate Containers**
- Create `cvs`, `jobs`, `analyses` containers
- **Rejected:** Increases cost (RU charged per container), complicates cross-entity queries

---

### RU/s Considerations

**Serverless Tier:**
- **No provisioning**: Auto-scales from 0 to 5,000 RU/s per second
- **Pricing**: $0.25 per million request units (RUs)
- **Estimate:** Typical operations:
  - Create CV: ~10 RU (2KB document)
  - Query analyses (10 results): ~5 RU (partition-scoped)
  - Create analysis: ~15 RU (5KB document with recommendations)
- **Monthly cost for 1,000 analyses**: ~30,000 RU = $0.0075 (~negligible)
- **Monitoring:** Track RU consumption in Azure Portal (Metrics → Request Units)

**Optimization Best Practices:**
- Use partition-scoped queries (`WHERE c.userId = @user_id`)
- Exclude large fields from indexing (`content`, `recommendations`)
- Use point reads when ID is known (`container.read_item(id, partition_key)`)
- Implement pagination with continuation tokens (more efficient than OFFSET)

---

## RU Monitoring and Cost Optimization

### Budget and Alerts

**MVP Budget (Dev Lead Decision Q3):**
- **Target:** <100,000 RU/month (approximately <$3/month at $0.25/1M RU)
- **Alert Threshold:** 50,000 RU/month (50% of budget)
- **Action:** When alert triggers, review RU consumption patterns and optimize queries

**Azure Monitor Configuration:**
```bash
# Create alert rule for RU consumption
az monitor metrics alert create \
  --name "cv-checker-ru-budget-alert" \
  --resource-group cv-checker-rg \
  --scopes "/subscriptions/{sub-id}/resourceGroups/cv-checker-rg/providers/Microsoft.DocumentDB/databaseAccounts/cv-checker-cosmos" \
  --condition "total NormalizedRUConsumption > 50000" \
  --window-size 1d \
  --evaluation-frequency 1h \
  --description "Alert when RU consumption exceeds 50,000/month threshold"
```

**Monitoring Dashboard:**
- Track key metrics in Azure Portal:
  - **Request Units Consumed:** Total RUs used per hour/day/month
  - **Request Rate:** Requests per second (should stay under 5,000 RU/s for serverless)
  - **Throttled Requests:** Count of 429 errors (indicates hitting limits)
  - **Storage Used:** Total data size (serverless supports up to 50GB)
  - **Average Request Latency:** P50, P95, P99 latencies

### Cost Optimization Strategies

**1. Indexing Policy Optimization**
```json
{
  "indexingPolicy": {
    "automatic": true,
    "includedPaths": [
      { "path": "/userId/*" },
      { "path": "/type/*" },
      { "path": "/analyzedAt/*" },
      { "path": "/overallScore/*" },
      { "path": "/cvId/*" },
      { "path": "/jobId/*" }
    ],
    "excludedPaths": [
      { "path": "/content/*" },              // Large CV/job text
      { "path": "/recommendations/*" },      // Large array of strings
      { "path": "/strengths/*" },
      { "path": "/gaps/*" }
    ]
  }
}
```
**Impact:** Excluding large text fields reduces write RUs by ~40% (only index query fields)

**2. Query Optimization**
- **Always use partition key:** `WHERE c.userId = @user_id` (5 RU vs 50+ RU cross-partition)
- **Avoid SELECT \*:** Only retrieve needed fields (e.g., `SELECT c.id, c.overallScore, c.analyzedAt`)
- **Use point reads:** When ID is known, use `read_item()` instead of query (1 RU vs 5+ RU)
- **Limit result sets:** Default limit=10, max=50 (prevents expensive large queries)

**3. Pagination with Continuation Tokens**
```python
# Efficient pagination (uses continuation tokens)
async def get_analyses_paginated(user_id: str, limit: int = 10):
    query = "SELECT * FROM c WHERE c.userId = @user_id AND c.type = 'analysis' ORDER BY c.analyzedAt DESC"
    
    items = []
    async for item in container.query_items(
        query=query,
        parameters=[{"name": "@user_id", "value": user_id}],
        partition_key=user_id,
        max_item_count=limit
    ):
        items.append(item)
    
    return items

# Avoid: OFFSET-based pagination (rescans all skipped items)
# Bad: "SELECT * FROM c OFFSET 100 LIMIT 10" → Scans first 100 items every time
```

**4. Batch Operations**
- When deleting all user data, use batch delete (transactional batch API) to reduce RU overhead
- Cosmos DB supports up to 100 operations in a single batch (all same partition key)

**5. Caching (Future Optimization)**
- Cache frequently accessed analyses in Redis (Phase 3)
- Reduces Cosmos DB read RUs for popular content
- Invalidate cache on data updates

### RU Consumption Estimates

**Typical User Journey (1,000 users, 3 analyses each = 3,000 analyses/month):**

| Operation | RU Cost | Frequency | Monthly RU |
|-----------|---------|-----------|------------|
| Create CV | 10 RU | 3,000 | 30,000 |
| Create Job | 10 RU | 3,000 | 30,000 |
| Create Analysis | 15 RU | 3,000 | 45,000 |
| List Analyses (10 results) | 5 RU | 6,000 (2x per user) | 30,000 |
| Get Single Analysis | 3 RU | 3,000 | 9,000 |
| Health Checks | 1 RU | 43,200 (every 2 min) | 43,200 |
| **Total** | | | **187,200 RU** |

**Monthly Cost:** 187,200 RU × $0.25/1M RU = **$0.047 (~$0.05/month)**

**Alert Threshold:** 50,000 RU/month is conservative—actual usage likely lower

**Scaling Estimate (10,000 users):**
- 10x traffic: ~1.87M RU/month = **$0.47/month**
- Still well under $3/month budget
- Serverless tier handles burst traffic automatically (up to 5,000 RU/s)

### Monitoring Best Practices

1. **Weekly Review:** Check RU consumption trends in Azure Portal (Metrics blade)
2. **Query Insights:** Use Cosmos DB Insights to identify expensive queries
3. **Diagnostic Logging:** Enable diagnostic logs for detailed request-level analysis
4. **Optimize Hot Paths:** If specific queries consume high RUs, optimize indexing or rewrite query
5. **Budget Alerts:** Set up Azure Cost Management alerts at 50% and 80% of $3/month budget

**Related:** See [Cosmos DB Request Units documentation](https://learn.microsoft.com/azure/cosmos-db/request-units) for detailed RU pricing

---

## Security Best Practices

### Connection String Management

**Dev Lead Decision (Q1): Use Azure Key Vault for MVP**

**Rationale:**
- **Option 1 (Chosen): Azure Key Vault** - Secure secret storage with audit logging
- **Option 2 (Deferred): Managed Identity** - More complex setup, defer to Phase 3 with authentication
- **MVP Approach:** Key Vault provides good security with simpler implementation than full managed identity

**Production Setup (Key Vault):**

```bash
# Step 1: Create Key Vault
az keyvault create \
  --name cv-checker-vault \
  --resource-group cv-checker-rg \
  --location eastus \
  --enable-rbac-authorization false  # Use access policies for simplicity

# Step 2: Store Cosmos DB connection string as secret
az keyvault secret set \
  --vault-name cv-checker-vault \
  --name CosmosConnectionString \
  --value "AccountEndpoint=https://cv-checker-cosmos.documents.azure.com:443/;AccountKey=..."

# Step 3: Grant App Service access to Key Vault (via Managed Identity)
az webapp identity assign \
  --name cv-checker-api \
  --resource-group cv-checker-rg

# Get the principal ID from output, then grant access
az keyvault set-policy \
  --name cv-checker-vault \
  --object-id <app-service-principal-id> \
  --secret-permissions get list

# Step 4: Configure App Service to reference Key Vault secret
az webapp config appsettings set \
  --resource-group cv-checker-rg \
  --name cv-checker-api \
  --settings COSMOS_CONNECTION_STRING="@Microsoft.KeyVault(SecretUri=https://cv-checker-vault.vault.azure.net/secrets/CosmosConnectionString)"
```

**Backend Code (No Changes Required):**
```python
import os
from azure.cosmos.aio import CosmosClient

# App Service automatically resolves Key Vault reference
connection_string = os.getenv("COSMOS_CONNECTION_STRING")
client = CosmosClient.from_connection_string(connection_string)
```

**Security Benefits:**
- ✅ Connection string never exposed in code, logs, or environment variables (only Key Vault reference)
- ✅ Key Vault audit logs track who accessed secrets and when
- ✅ Secrets can be rotated without redeploying application (update Key Vault, restart App Service)
- ✅ Managed Identity eliminates need for separate credentials to access Key Vault

**Local Development:**
```bash
# .env.local (git-ignored)
COSMOS_CONNECTION_STRING=AccountEndpoint=https://localhost:8081/;AccountKey=C2y6yDjf5/R+ob0N8A7Cgv35VFMA6rHH9NX0x6UqOgE=;
```
- Emulator uses well-known connection string (acceptable for local development)
- No need for Key Vault access in local environment

---

### Data Isolation and Authorization

**Partition Key Enforcement:**
- Every document includes `userId` field (partition key)
- Cosmos DB enforces logical isolation: queries scoped to single partition cannot access other partitions
- Backend validates `userId` in request header matches query parameter (prevents cross-user access)

**Authorization Pattern:**
```python
from fastapi import Header, HTTPException

def get_user_id(x_user_id: str = Header(..., alias="X-User-Id")) -> str:
    """Extract and validate userId from request header."""
    if not x_user_id.startswith("user-"):
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    # Validate UUID format
    try:
        uuid_part = x_user_id.replace("user-", "")
        uuid.UUID(uuid_part)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    return x_user_id

@app.get("/api/v1/cvs/{cv_id}")
async def get_cv(
    cv_id: str,
    user_id_query: str = Query(..., alias="userId"),
    user_id_header: str = Depends(get_user_id)
):
    # Verify header matches query parameter
    if user_id_header != user_id_query:
        raise HTTPException(status_code=401, detail="User ID mismatch")
    
    # Query with partition key (enforces data isolation)
    try:
        cv = await container.read_item(item=cv_id, partition_key=user_id_header)
    except CosmosResourceNotFoundError:
        raise HTTPException(status_code=404, detail="CV not found")
    
    return cv
```

**Security Properties:**
- ✅ User A cannot query User B's data (different partition keys)
- ✅ Even if User A knows User B's CV ID, query returns 404 (not found in User A's partition)
- ✅ No SQL injection risk (parameterized queries)
- ✅ No NoSQL injection (Cosmos DB SDK sanitizes inputs)

---

### Transport Security

**HTTPS Enforcement:**
- **Production:** All API endpoints use HTTPS (enforced by Azure App Service)
- **Cosmos DB:** Connections use TLS 1.2+ (Azure default, cannot be disabled)
- **Frontend → Backend:** HTTPS required (configured in App Service)
- **Backend → Cosmos DB:** HTTPS required (connection string uses `https://` endpoint)

**Local Development:**
- **Frontend → Backend:** HTTP acceptable (`http://localhost:8000`)
- **Backend → Emulator:** HTTPS with self-signed certificate (disable SSL verification in SDK):
  ```python
  def is_local_emulator() -> bool:
      conn_str = os.getenv("COSMOS_CONNECTION_STRING", "")
      return "localhost:8081" in conn_str
  
  client = CosmosClient.from_connection_string(
      os.getenv("COSMOS_CONNECTION_STRING"),
      connection_verify=not is_local_emulator()  # Disable for emulator only
  )
  ```

---

### CORS Configuration

**Production:**
```bash
# Configure allowed origins (not wildcard)
az webapp cors add \
  --resource-group cv-checker-rg \
  --name cv-checker-api \
  --allowed-origins "https://cv-checker.azurewebsites.net"
```

**Local Development:**
```python
# backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "https://cv-checker.azurewebsites.net"  # Production frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### Input Validation and Sanitization

**Size Limits:**
- CV content: 100KB max (prevents DoS via large payloads)
- Job description: 50KB max
- Enforced in FastAPI request models:
  ```python
  from pydantic import BaseModel, Field, validator
  
  class AnalyzeRequest(BaseModel):
      cv_markdown: str = Field(..., max_length=100_000)
      job_description: str = Field(..., max_length=50_000)
      
      @validator("cv_markdown", "job_description")
      def validate_size(cls, v):
          if len(v.encode("utf-8")) > 100_000:  # CV limit
              raise ValueError("Content exceeds size limit")
          return v
  ```

**User ID Format Validation:**
- Enforce UUID v4 format: `user-{uuid}`
- Reject malformed IDs (prevents injection attacks)
- Example validation regex: `^user-[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$`

**Content Sanitization:**
- CV and job descriptions stored as-is (Markdown expected, no HTML)
- No executable code allowed (validated on frontend before submission)
- Filenames sanitized to alphanumeric + underscore/hyphen only

---

### Secrets Management Checklist

- [x] **Never commit secrets to Git:** `.env` files in `.gitignore`
- [x] **Use Key Vault for production:** Connection string stored securely
- [x] **Use Managed Identity:** App Service accesses Key Vault without credentials
- [x] **Rotate secrets regularly:** Update Key Vault secret, restart app (no code changes)
- [x] **Audit secret access:** Key Vault diagnostic logs track who accessed what and when
- [x] **Separate environments:** Different Key Vaults for dev/staging/production

---

### Future Security Enhancements (Phase 3)

- **Managed Identity for Cosmos DB:** Eliminate connection string entirely, use Azure AD authentication
- **Field-Level Encryption:** Encrypt CV content at application level (before storing in Cosmos DB)
- **Audit Logging:** Log all data access operations (create, read, delete) with userId and timestamp
- **Rate Limiting:** Per-user API rate limits (e.g., 100 analyses per day)
- **Data Retention Policies:** Auto-delete analyses older than 365 days (GDPR compliance)
- **GDPR Compliance:** "Download My Data" (export), "Right to be Forgotten" (delete)

**Related:** See [Azure Cosmos DB Security Best Practices](https://learn.microsoft.com/azure/cosmos-db/database-security) for comprehensive guidance

---

## Dependencies and Configuration

### Python Package Dependencies

**Required Package:**
```toml
# backend/pyproject.toml or requirements.txt
azure-cosmos>=4.6.0
```

**Version Justification:**
- `4.6.0` includes async client (`azure.cosmos.aio.CosmosClient`) for FastAPI integration
- Supports serverless tier (no `offer_throughput` parameter)
- Includes diagnostic logging for RU consumption tracking
- Stable release with production-ready SDK features

**Installation:**
```bash
cd backend
pip install azure-cosmos>=4.6.0

# Or using poetry
poetry add "azure-cosmos>=4.6.0"
```

**Import Example:**
```python
from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey, exceptions
from azure.cosmos.exceptions import CosmosResourceNotFoundError, CosmosHttpResponseError
```

---

### Environment Variables

**Required Configuration:**

| Variable | Description | Example (Local) | Example (Production) |
|----------|-------------|-----------------|----------------------|
| `COSMOS_CONNECTION_STRING` | Cosmos DB connection string | `AccountEndpoint=https://localhost:8081/;AccountKey=C2y6yDjf5...` | `@Microsoft.KeyVault(SecretUri=https://cv-checker-vault.vault.azure.net/secrets/CosmosConnectionString)` |
| `COSMOS_DATABASE_NAME` | Database name | `cv-checker-db` | `cv-checker-db` |
| `COSMOS_CONTAINER_NAME` | Container name | `cv-checker-data` | `cv-checker-data` |

**Optional Configuration:**

| Variable | Description | Default |
|----------|-------------|----------|
| `COSMOS_MAX_RETRIES` | Max connection retry attempts | `3` |
| `COSMOS_RETRY_BACKOFF_MS` | Retry backoff (milliseconds) | `1000` |
| `COSMOS_TIMEOUT_SECONDS` | Request timeout | `30` |

**Local Development (.env.local):**
```bash
# .env.local (git-ignored)
COSMOS_CONNECTION_STRING=AccountEndpoint=https://localhost:8081/;AccountKey=C2y6yDjf5/R+ob0N8A7Cgv35VFMA6rHH9NX0x6UqOgE=;
COSMOS_DATABASE_NAME=cv-checker-db
COSMOS_CONTAINER_NAME=cv-checker-data
```

**Production (Azure App Service):**
```bash
# Set via Azure CLI or Portal
az webapp config appsettings set \
  --resource-group cv-checker-rg \
  --name cv-checker-api \
  --settings \
    COSMOS_CONNECTION_STRING="@Microsoft.KeyVault(...)" \
    COSMOS_DATABASE_NAME="cv-checker-db" \
    COSMOS_CONTAINER_NAME="cv-checker-data"
```

**Backend Configuration Loading:**
```python
# backend/app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    cosmos_connection_string: str
    cosmos_database_name: str = "cv-checker-db"
    cosmos_container_name: str = "cv-checker-data"
    cosmos_max_retries: int = 3
    cosmos_retry_backoff_ms: int = 1000
    cosmos_timeout_seconds: int = 30
    
    class Config:
        env_file = ".env.local"
        case_sensitive = False

settings = Settings()
```

---

### Docker Compose Configuration

**docker-compose.yml (Local Development):**
```yaml
version: '3.8'

services:
  cosmosdb:
    image: mcr.microsoft.com/cosmosdb/linux/azure-cosmos-emulator:latest
    container_name: cv-checker-cosmosdb
    ports:
      - "8081:8081"     # HTTPS endpoint
      - "10251:10251"   # Data Explorer
      - "10252:10252"
      - "10253:10253"
      - "10254:10254"
    environment:
      - AZURE_COSMOS_EMULATOR_PARTITION_COUNT=10
      - AZURE_COSMOS_EMULATOR_ENABLE_DATA_PERSISTENCE=false
    volumes:
      - cosmos-data:/tmp/cosmos
    healthcheck:
      test: ["CMD", "curl", "-k", "https://localhost:8081/_explorer/emulator.pem"]
      interval: 30s
      timeout: 10s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: cv-checker-backend
    ports:
      - "8000:8000"
    environment:
      - COSMOS_CONNECTION_STRING=AccountEndpoint=https://cosmosdb:8081/;AccountKey=C2y6yDjf5/R+ob0N8A7Cgv35VFMA6rHH9NX0x6UqOgE=;
      - COSMOS_DATABASE_NAME=cv-checker-db
      - COSMOS_CONTAINER_NAME=cv-checker-data
    depends_on:
      cosmosdb:
        condition: service_healthy
    volumes:
      - ./backend:/app

volumes:
  cosmos-data:
```

**Usage:**
```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Clean up data
docker-compose down -v
```

---

### Configuration Management Best Practices

1. **Never Commit Secrets:** Add `.env*` to `.gitignore`
2. **Use Environment-Specific Files:**
   - `.env.local` (local development, git-ignored)
   - `.env.example` (template, committed to Git)
   - Azure App Service settings (production)
3. **Validate Configuration on Startup:** Backend checks required environment variables exist
4. **Fail Fast:** If `COSMOS_CONNECTION_STRING` missing, backend refuses to start (don't use defaults)
5. **Document All Variables:** README includes table of required environment variables

**Related:** See [FRD Configuration Requirements](../features/data-persistence.md#fr-dp5-local-development-with-cosmos-db-emulator) for detailed setup instructions

---

### Local Emulator Connection String

**Default Emulator Connection String:**
```
AccountEndpoint=https://localhost:8081/;AccountKey=C2y6yDjf5/R+ob0N8A7Cgv35VFMA6rHH9NX0x6UqOgE=;
```

**Notes:**
- Account key is well-known (same for all developers)
- Endpoint uses self-signed SSL certificate → disable SSL verification in SDK:
  ```python
  from azure.cosmos.aio import CosmosClient
  
  client = CosmosClient.from_connection_string(
      conn_str=os.getenv("COSMOS_CONNECTION_STRING"),
      connection_verify=False  # Local emulator only
  )
  ```
- Production: Remove `connection_verify=False`, use valid Azure certificate

---

### Database Initialization Script

**Backend Startup (`app/database.py`):**
```python
async def init_cosmos_db():
    """Initialize Cosmos DB database and container if not exists."""
    client = CosmosClient.from_connection_string(
        os.getenv("COSMOS_CONNECTION_STRING"),
        connection_verify=not is_local_emulator()
    )
    
    # Create database
    database = await client.create_database_if_not_exists(id="cv-checker-db")
    
    # Create container with partition key
    container = await database.create_container_if_not_exists(
        id="cv-checker-data",
        partition_key=PartitionKey(path="/userId"),
        offer_throughput=None  # Serverless
    )
    
    logger.info("Cosmos DB initialized: database and container ready")
    return container

def is_local_emulator() -> bool:
    """Detect if running against local emulator."""
    conn_str = os.getenv("COSMOS_CONNECTION_STRING", "")
    return "localhost:8081" in conn_str
```

**Call on FastAPI Startup:**
```python
@app.on_event("startup")
async def startup_event():
    app.state.cosmos_container = await init_cosmos_db()
```

---

### Session-Based User Identification

**Frontend (TypeScript):**
```typescript
// src/utils/session.ts
export function getUserId(): string {
  const storageKey = 'cv-checker-userId';
  let userId = localStorage.getItem(storageKey);
  
  if (!userId) {
    userId = `user-${crypto.randomUUID()}`;
    localStorage.setItem(storageKey, userId);
  }
  
  return userId;
}
```

**Backend (FastAPI Dependency):**
```python
# app/dependencies.py
from fastapi import Header, HTTPException

def get_user_id(x_user_id: str = Header(..., alias="X-User-Id")) -> str:
    """Extract and validate userId from request header."""
    if not x_user_id.startswith("user-"):
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    # Validate UUID format
    try:
        uuid_part = x_user_id.replace("user-", "")
        uuid.UUID(uuid_part)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    return x_user_id
```

**Usage in Endpoints:**
```python
@app.post("/api/v1/analyze")
async def analyze_cv(
    request: AnalyzeRequest,
    user_id: str = Depends(get_user_id),
    container = Depends(get_cosmos_container)
):
    # Store CV with userId as partition key
    cv_doc = {
        "id": f"cv-{uuid4()}",
        "type": "cv",
        "userId": user_id,  # Partition key
        "content": request.cv_markdown,
        ...
    }
    await container.create_item(body=cv_doc)
```

---

### Production Connection String (Azure)

**Secure Storage Options:**

**Option 1: Azure Key Vault (Recommended for Production)**
```bash
# Store connection string in Key Vault
az keyvault secret set \
  --vault-name cv-checker-vault \
  --name CosmosConnectionString \
  --value "AccountEndpoint=https://cv-checker-cosmos.documents.azure.com:443/;AccountKey=..."

# App Service retrieves from Key Vault
az webapp config appsettings set \
  --resource-group cv-checker-rg \
  --name cv-checker-api \
  --settings COSMOS_CONNECTION_STRING="@Microsoft.KeyVault(SecretUri=https://cv-checker-vault.vault.azure.net/secrets/CosmosConnectionString)"
```

**Option 2: App Service Environment Variable (Simpler for MVP)**
```bash
az webapp config appsettings set \
  --resource-group cv-checker-rg \
  --name cv-checker-api \
  --settings COSMOS_CONNECTION_STRING="AccountEndpoint=https://...;AccountKey=..."
```

**Backend Code (Same for Both):**
```python
# No code changes—reads from environment variable
client = CosmosClient.from_connection_string(
    os.getenv("COSMOS_CONNECTION_STRING")
)
```

---

### Error Handling

**Common Scenarios:**

**1. Connection Failure (Emulator Not Running)**
```python
try:
    await container.read_item(item=item_id, partition_key=user_id)
except CosmosHttpResponseError as e:
    if e.status_code == 503:
        raise HTTPException(
            status_code=503, 
            detail="Database unavailable. Is Cosmos DB emulator running?"
        )
```

**2. Item Not Found**
```python
from azure.cosmos.exceptions import CosmosResourceNotFoundError

try:
    item = await container.read_item(item=cv_id, partition_key=user_id)
except CosmosResourceNotFoundError:
    raise HTTPException(status_code=404, detail="CV not found")
```

**3. Partition Key Mismatch (Authorization)**
```python
# Wrong: Querying with incorrect partition key
await container.read_item(item=cv_id, partition_key="wrong-user")
# Raises CosmosResourceNotFoundError (not 403—Cosmos DB doesn't distinguish)

# Correct: Always use userId from authenticated request
await container.read_item(item=cv_id, partition_key=user_id)
```

**4. Health Check Implementation (Dev Lead Decision Q4)**
```python
@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint showing database connectivity status.
    
    Dev Lead Decision Q4: Binary connected/disconnected status only.
    Detailed metrics (RU consumption, latency) available via Azure Portal.
    """
    try:
        # Simple connectivity test (1 RU operation)
        await container.read_item(
            item="health-check-probe",
            partition_key="system"
        )
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
```

**Note:** For detailed performance metrics (RU consumption, latency percentiles, throttling), use Azure Portal Metrics blade. Health check provides only binary status for uptime monitoring.

## Related Decisions

- **ADR-001**: Sequential orchestration produces analysis results → these results now persisted in Cosmos DB
- **ADR-004**: Defined data models and repository pattern → now implemented with Cosmos DB backend
- **ADR-005**: FastAPI architecture → dependency injection integrates Cosmos container
- **PRD (Section 3.7)**: Data persistence requirements → this ADR fulfills those requirements
- **FRD**: [specs/features/data-persistence.md](../features/data-persistence.md) → detailed functional requirements

## References

### Azure Cosmos DB Documentation
- [Azure Cosmos DB Overview](https://learn.microsoft.com/azure/cosmos-db/introduction)
- [Cosmos DB Serverless](https://learn.microsoft.com/azure/cosmos-db/serverless)
- [Partitioning in Azure Cosmos DB](https://learn.microsoft.com/azure/cosmos-db/partitioning-overview)
- [Cosmos DB Python SDK](https://learn.microsoft.com/python/api/overview/azure/cosmos-readme)
- [Cosmos DB Linux Emulator](https://learn.microsoft.com/azure/cosmos-db/docker-emulator-linux)

### Best Practices
- [Cosmos DB Data Modeling](https://learn.microsoft.com/azure/cosmos-db/nosql/modeling-data)
- [Request Unit Optimization](https://learn.microsoft.com/azure/cosmos-db/nosql/optimize-request-units)
- [Indexing Best Practices](https://learn.microsoft.com/azure/cosmos-db/index-policy)

### SDK Examples
- [Cosmos DB Python SDK Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cosmos/azure-cosmos/samples)
- [Async Operations with Cosmos DB](https://learn.microsoft.com/python/api/overview/azure/cosmos-readme#async-client)

### Related Architecture
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html) (Martin Fowler)
- [Docker Compose for Local Development](https://docs.docker.com/compose/)
