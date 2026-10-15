# ADR-004: No Database V1 with Future Storage Design

**Date**: 2025-12-31  
**Status**: Accepted  
**Decision Makers**: Architecture Team  
**Technical Story**: V1 In-Memory Processing with Cosmos DB Future-Proofing

## Context

CV Checker v1 is a proof-of-concept that needs to demonstrate value quickly without infrastructure complexity. However, we anticipate future requirements for:

- **Persistent Storage**: Storing analysis history, user preferences, and job descriptions
- **Audit Trail**: Tracking CV submissions and analysis results
- **Analytics**: Aggregating data for insights and model improvement
- **Multi-User Support**: User accounts and role-based access
- **Caching**: Avoiding re-analysis of identical CV/job combinations

The choice between implementing storage immediately vs. deferring it affects:
- Time to market
- Development complexity
- Infrastructure costs
- Architecture flexibility

## Decision

We will implement **V1 with in-memory processing only** while designing data models and repository patterns that enable seamless migration to **Azure Cosmos DB** in future versions.

### V1 Approach: Stateless Processing

- All analysis happens in-memory during request lifecycle
- No data persists between API calls
- Results returned immediately to client
- Client responsible for storing results if needed

### Future-Proofing Strategy

1. **Pydantic Models**: Define data models compatible with Cosmos DB document structure
2. **Repository Pattern**: Abstract data access behind interfaces
3. **Document Design**: Use Cosmos DB best practices (partition keys, hierarchical structure)
4. **Serialization Ready**: Ensure models serialize to JSON cleanly

## Implementation

### V1: In-Memory Data Models

```python
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from uuid import uuid4

class SkillMatch(BaseModel):
    """Individual skill matching result."""
    skill_name: str
    required: bool
    candidate_has: bool
    proficiency_level: Optional[str] = None  # "beginner", "intermediate", "advanced"
    years_experience: Optional[float] = None
    match_score: float = Field(ge=0.0, le=1.0)

class AnalysisResult(BaseModel):
    """Complete CV analysis result - Cosmos DB ready."""
    # Cosmos DB metadata (unused in v1, ready for v2)
    id: str = Field(default_factory=lambda: str(uuid4()))
    partition_key: str = Field(default="analysis", alias="partitionKey")
    document_type: str = "cv_analysis"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Analysis data
    overall_score: float = Field(ge=0.0, le=100.0)
    skill_matches: List[SkillMatch]
    experience_match: Dict[str, Any]
    education_match: Dict[str, Any]
    
    # Recommendations
    strengths: List[str]
    gaps: List[str]
    recommendations: List[str]
    
    # Context (for future filtering/search)
    job_title: Optional[str] = None
    industry: Optional[str] = None
    seniority_level: Optional[str] = None
    
    class Config:
        populate_by_name = True  # Allows both 'partition_key' and 'partitionKey'
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "partitionKey": "analysis",
                "document_type": "cv_analysis",
                "overall_score": 85.5,
                "skill_matches": [
                    {
                        "skill_name": "Python",
                        "required": True,
                        "candidate_has": True,
                        "proficiency_level": "advanced",
                        "years_experience": 5.0,
                        "match_score": 1.0
                    }
                ],
                "strengths": ["Strong Python experience", "Cloud architecture"],
                "gaps": ["Kubernetes experience needed"],
                "recommendations": ["Consider Kubernetes certification"]
            }
        }

class JobDescription(BaseModel):
    """Job description document - Cosmos DB ready."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    partition_key: str = Field(default="job_description", alias="partitionKey")
    document_type: str = "job_description"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Job data
    title: str
    company: Optional[str] = None
    description_text: str
    required_skills: List[str]
    preferred_skills: List[str]
    experience_years: Optional[int] = None
    education_level: Optional[str] = None
    
    # Metadata for future search
    industry: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    
    class Config:
        populate_by_name = True

class CVDocument(BaseModel):
    """CV document - Cosmos DB ready."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    partition_key: str = Field(default="cv_document", alias="partitionKey")
    document_type: str = "cv_document"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # CV data
    candidate_name: Optional[str] = None
    email: Optional[str] = None
    markdown_content: str
    skills: List[str]
    experience_years: Optional[float] = None
    education: List[Dict[str, str]]
    work_history: List[Dict[str, Any]]
    
    class Config:
        populate_by_name = True
```

### Repository Pattern (Ready for Future)

```python
from abc import ABC, abstractmethod
from typing import Optional

class AnalysisRepository(ABC):
    """Abstract repository for analysis results."""
    
    @abstractmethod
    async def save(self, analysis: AnalysisResult) -> str:
        """Save analysis result. Returns document ID."""
        pass
    
    @abstractmethod
    async def get_by_id(self, analysis_id: str) -> Optional[AnalysisResult]:
        """Retrieve analysis by ID."""
        pass
    
    @abstractmethod
    async def list_recent(self, limit: int = 10) -> List[AnalysisResult]:
        """List recent analyses."""
        pass

class InMemoryAnalysisRepository(AnalysisRepository):
    """V1 implementation: No persistence, returns immediately."""
    
    async def save(self, analysis: AnalysisResult) -> str:
        """No-op save - returns ID without persisting."""
        return analysis.id
    
    async def get_by_id(self, analysis_id: str) -> Optional[AnalysisResult]:
        """Always returns None in v1."""
        return None
    
    async def list_recent(self, limit: int = 10) -> List[AnalysisResult]:
        """Returns empty list in v1."""
        return []

# Future Cosmos DB implementation (not used in v1)
class CosmosDBAnalysisRepository(AnalysisRepository):
    """V2+ implementation: Persists to Cosmos DB."""
    
    def __init__(self, cosmos_client, database_name: str, container_name: str):
        self.container = cosmos_client.get_database_client(database_name)\
                                      .get_container_client(container_name)
    
    async def save(self, analysis: AnalysisResult) -> str:
        """Save to Cosmos DB with partition key."""
        item = analysis.model_dump(by_alias=True)
        await self.container.upsert_item(item)
        return analysis.id
    
    async def get_by_id(self, analysis_id: str) -> Optional[AnalysisResult]:
        """Retrieve from Cosmos DB."""
        try:
            item = await self.container.read_item(
                item=analysis_id,
                partition_key="analysis"
            )
            return AnalysisResult(**item)
        except Exception:
            return None
    
    async def list_recent(self, limit: int = 10) -> List[AnalysisResult]:
        """Query recent analyses."""
        query = """
        SELECT * FROM c 
        WHERE c.document_type = 'cv_analysis' 
        ORDER BY c.created_at DESC 
        OFFSET 0 LIMIT @limit
        """
        items = self.container.query_items(
            query=query,
            parameters=[{"name": "@limit", "value": limit}],
            partition_key="analysis"
        )
        return [AnalysisResult(**item) async for item in items]
```

### Cosmos DB Container Design (Future)

```json
{
  "containerName": "cv_checker",
  "partitionKeyPath": "/partitionKey",
  "hierarchicalPartitionKeys": ["/partitionKey", "/document_type"],
  "indexingPolicy": {
    "automatic": true,
    "includedPaths": [
      {"path": "/document_type/?"},
      {"path": "/created_at/?"},
      {"path": "/overall_score/?"},
      {"path": "/job_title/?"}
    ],
    "excludedPaths": [
      {"path": "/markdown_content/?"},
      {"path": "/description_text/?"}
    ]
  },
  "throughput": 400
}
```

### Service Layer (V1)

```python
from fastapi import Depends

class CVCheckerService:
    """Service layer - storage-agnostic."""
    
    def __init__(self, repository: AnalysisRepository):
        self.repository = repository
    
    async def analyze_cv(
        self, 
        cv_markdown: str, 
        job_description: str
    ) -> AnalysisResult:
        """Analyze CV against job description."""
        # Agent workflow processes in-memory
        result = await self._run_agent_workflow(cv_markdown, job_description)
        
        # Save (no-op in v1, persists in v2+)
        await self.repository.save(result)
        
        return result
    
    async def _run_agent_workflow(
        self, 
        cv_markdown: str, 
        job_description: str
    ) -> AnalysisResult:
        """Execute agent workflow - implementation omitted."""
        # This calls the workflow from ADR-001
        pass

# Dependency injection
def get_repository() -> AnalysisRepository:
    """Returns in-memory repo for v1, Cosmos repo for v2+."""
    # V1: return InMemoryAnalysisRepository()
    # V2: return CosmosDBAnalysisRepository(...)
    return InMemoryAnalysisRepository()

def get_service(repo: AnalysisRepository = Depends(get_repository)) -> CVCheckerService:
    return CVCheckerService(repo)
```

## Consequences

### Positive

- **Fast V1 Delivery**: No database setup, deployment, or management overhead
- **Zero Infrastructure Costs**: No storage costs in v1
- **Simplified Testing**: No database mocking required for unit tests
- **Clear Migration Path**: Repository pattern enables drop-in Cosmos DB support
- **Cosmos DB Optimized**: Models follow best practices (partition keys, hierarchical keys)
- **No Technical Debt**: Architecture supports storage without refactoring

### Negative

- **No Persistence**: Users lose analysis results when session ends
- **No History**: Cannot track analysis trends or improvements
- **No Caching**: Re-analyzing identical CV/job pairs wastes resources
- **Limited Analytics**: Cannot aggregate data for insights

### Migration to Cosmos DB (V2+)

When ready to add persistence:

1. **Provision Cosmos DB**:
   ```bash
   az cosmosdb create --name cv-checker-db --resource-group cv-checker-rg
   az cosmosdb sql database create --account-name cv-checker-db --name cvchecker
   az cosmosdb sql container create \
     --account-name cv-checker-db \
     --database-name cvchecker \
     --name analyses \
     --partition-key-path /partitionKey \
     --throughput 400
   ```

2. **Update Dependency Injection**:
   ```python
   def get_repository() -> AnalysisRepository:
       cosmos_client = CosmosClient.from_connection_string(
           os.getenv("COSMOS_DB_CONNECTION_STRING")
       )
       return CosmosDBAnalysisRepository(cosmos_client, "cvchecker", "analyses")
   ```

3. **No Code Changes Required**: Service layer and API remain unchanged

### Cosmos DB Design Rationale

- **Partition Key**: `/partitionKey` allows flexible partitioning strategy
  - V2: Can switch to `/user_id` for multi-tenant scenarios
  - Hierarchical keys support scaling beyond 20GB per logical partition
- **Document Types**: Enable multiple entity types in single container (cost-effective)
- **Indexing**: Excludes large text fields, optimizes for common queries
- **Throughput**: 400 RU/s sufficient for MVP, scales elastically

## Related Decisions

- ADR-001: Sequential orchestration enables stateless processing
- ADR-005: FastAPI endpoints designed for stateless operation

## References

- [Azure Cosmos DB Best Practices](https://learn.microsoft.com/azure/cosmos-db/best-practices)
- [Cosmos DB Hierarchical Partition Keys](https://learn.microsoft.com/azure/cosmos-db/hierarchical-partition-keys)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)
