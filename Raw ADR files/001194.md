# ADR-019: ActionList API Router Architecture

## Status
**Accepted** | 2025-12-28

## Context

TaskMan-v2 backend-api Phase 3 Task T7 requires implementing complete RESTful API endpoints for ActionList resource management. This builds upon existing FastAPI router infrastructure and completes the three-tier architecture stack:

1. **Repository Layer** ([ADR-017](./ADR-017-ActionList-Repository-Implementation-Strategy.md)) — Database access, query composition
2. **Service Layer** ([ADR-018](./ADR-018-ActionList-Service-Layer-Architecture.md)) — Business logic orchestration
3. **API Router Layer** (this ADR) — HTTP request/response handling, OpenAPI documentation

### Current State

**Existing Routers**:
- **tasks.py** (184 lines): CRUD + search with 10 query parameters, status validation, priority filtering
- **sprints.py** (187 lines): CRUD + metrics endpoints (velocity, burndown), date range filtering
- **projects.py** (171 lines): CRUD + health assessment, task aggregation queries

**ActionList Router** (current state):
- Basic CRUD operations implemented (277 lines)
- Missing: Task relationship management endpoints
- Missing: Advanced filtering (by task, date range, multi-status)
- Missing: Comprehensive error handling patterns
- Missing: OpenAPI documentation examples

**Integration Points**:
- **FastAPI Application** → Registers router at `/api/v1/action-lists` prefix
- **ActionListService** → Injected via dependency, handles business logic
- **Pydantic Schemas** → Request validation and response serialization
- **Result Monad** → Pattern matching for explicit error handling

### Architecture Drivers

**Functional Requirements**:
- Complete CRUD lifecycle for ActionList entities
- Task relationship management (add/remove tasks from lists)
- Cross-entity queries (find lists containing specific tasks)
- Advanced filtering (status, active/archived, date range)
- Pagination with cursor or offset support
- OpenAPI documentation with examples

**Quality Attributes**:
- **Usability**: Intuitive REST API design following conventions
- **Reliability**: Comprehensive error handling with appropriate HTTP status codes
- **Observability**: Structured logging for all operations
- **Performance**: Efficient pagination, minimal query overhead
- **Documentation**: Auto-generated OpenAPI/Swagger with clear examples

**Constraints**:
- Must follow existing router patterns (tasks, sprints, projects)
- Async/await throughout (TaskMan-v2 fully async)
- Result monad pattern for error handling
- FastAPI dependency injection for service layer
- OpenAPI 3.1 compliance for documentation

## Decision Drivers

### REST API Design Philosophy

**Resource-Oriented vs Action-Oriented**:
- ActionLists are **entities** → Use resource-oriented URLs
- Task relationships are **sub-resources** → Nest under parent resource
- Cross-cutting queries → Use query parameters or dedicated endpoints

**HTTP Method Semantics**:
| Method | Idempotent | Safe | Usage |
|--------|------------|------|-------|
| GET | ✅ | ✅ | Retrieve resources |
| POST | ❌ | ❌ | Create new resources or complex operations |
| PUT | ✅ | ❌ | Full resource replacement |
| PATCH | ❌ | ❌ | Partial updates |
| DELETE | ✅ | ❌ | Remove resources |

### Pagination Strategy Analysis

#### Option 1: Offset-Based Pagination
```python
GET /api/v1/action-lists?page=2&per_page=20
Response: { "page": 2, "per_page": 20, "total": 157, "has_more": true }
```

**Pros**:
- Simple to implement and understand
- Consistent with existing routers (tasks, sprints, projects)
- Easy to jump to arbitrary pages
- Total count available for UI pagination controls

**Cons**:
- Performance degrades with large offsets (OFFSET 10000)
- Inconsistent results if data changes between requests
- Not suitable for real-time feeds

**Verdict**: ✅ **Recommended** — Matches existing patterns, sufficient for current scale

#### Option 2: Cursor-Based Pagination
```python
GET /api/v1/action-lists?cursor=eyJ0aW1lIjoxNzM1...&limit=20
Response: { "items": [...], "next_cursor": "eyJ0aW1lIjox...", "has_more": true }
```

**Pros**:
- Consistent results even with concurrent updates
- Better performance for large datasets
- Ideal for infinite scroll UIs

**Cons**:
- Cannot jump to arbitrary pages
- More complex implementation
- Requires encoding/decoding cursor state

**Verdict**: ⏸️ **Deferred** — Consider for v2.0 if scale demands it

### Error Handling Strategy

**HTTP Status Code Mapping**:
| Status Code | Scenario | Example |
|-------------|----------|---------|
| 200 OK | Successful GET | Retrieved action list |
| 201 Created | Successful POST | Created new list |
| 204 No Content | Successful DELETE | Deleted list |
| 400 Bad Request | Invalid input | Malformed JSON, invalid enum |
| 404 Not Found | Resource missing | List ID doesn't exist |
| 409 Conflict | Duplicate resource | ID already exists |
| 422 Unprocessable Entity | Validation error | Business rule violation |
| 500 Internal Server Error | Unexpected error | Database connection failure |

**Error Response Schema**:
```json
{
  "detail": "Action list not found: AL-12345",
  "error_code": "NOT_FOUND",
  "context": {
    "list_id": "AL-12345",
    "timestamp": "2025-12-28T10:30:00Z"
  }
}
```

## Considered Options

### Option 1: Minimal Router (Only Basic CRUD)
```python
@router.get("", response_model=ActionListCollection)
async def list_action_lists(service: ActionListSvc, page: int = 1) -> ActionListCollection:
    # ... basic listing

@router.post("", response_model=ActionListResponse)
async def create_action_list(data: ActionListCreate, service: ActionListSvc) -> ActionListResponse:
    # ... basic create

@router.get("/{list_id}", response_model=ActionListResponse)
async def get_action_list(list_id: str, service: ActionListSvc) -> ActionListResponse:
    # ... basic retrieval

@router.put("/{list_id}", response_model=ActionListResponse)
async def update_action_list(list_id: str, data: ActionListUpdate, service: ActionListSvc) -> ActionListResponse:
    # ... basic update

@router.delete("/{list_id}", status_code=204)
async def delete_action_list(list_id: str, service: ActionListSvc) -> None:
    # ... basic delete
```

**Pros**: Simple, follows CRUD conventions
**Cons**: Insufficient for task relationship management, no advanced queries
**Verdict**: ❌ Does not meet functional requirements

### Option 2: Rich Router with Sub-Resources ⭐ **(Recommended)**
```python
# ===== Basic CRUD =====
@router.get("", response_model=ActionListCollection)
async def list_action_lists(...) -> ActionListCollection: ...

@router.post("", response_model=ActionListResponse)
async def create_action_list(...) -> ActionListResponse: ...

@router.get("/{list_id}", response_model=ActionListResponse)
async def get_action_list(...) -> ActionListResponse: ...

@router.put("/{list_id}", response_model=ActionListResponse)
async def update_action_list(...) -> ActionListResponse: ...

@router.delete("/{list_id}", status_code=204)
async def delete_action_list(...) -> None: ...

# ===== Task Relationships =====
@router.post("/{list_id}/tasks", response_model=ActionListResponse)
async def add_task_to_list(...) -> ActionListResponse: ...

@router.delete("/{list_id}/tasks/{task_id}", status_code=204)
async def remove_task_from_list(...) -> None: ...

@router.post("/{list_id}/tasks/reorder", response_model=ActionListResponse)
async def reorder_list_tasks(...) -> ActionListResponse: ...

# ===== Cross-Entity Queries =====
@router.get("/tasks/{task_id}", response_model=ActionListCollection)
async def find_lists_by_task(...) -> ActionListCollection: ...
```

**Pros**: Complete feature coverage, follows REST conventions, clear resource hierarchy
**Cons**: More endpoints to maintain, slightly larger codebase
**Verdict**: ✅ **Recommended** — Meets all requirements, aligns with existing patterns

### Option 3: Action-Oriented Design
```python
@router.post("/add-task")
async def add_task(...): ...

@router.post("/remove-task")
async def remove_task(...): ...

@router.post("/search-by-task")
async def search_by_task(...): ...
```

**Pros**: Explicit intent, flexible operation naming
**Cons**: Violates REST conventions, inconsistent with existing routers
**Verdict**: ❌ Does not align with architecture standards

## Decision

We will implement **Option 2: Rich Router with Sub-Resources** for the following reasons:

1. **Complete Feature Coverage**: Supports all required operations (CRUD + task relationships + queries)
2. **REST Conventions**: Uses resource-oriented URLs and standard HTTP methods
3. **Consistency**: Aligns with existing task, sprint, and project routers
4. **Scalability**: Easy to extend with additional sub-resources or filters
5. **OpenAPI Documentation**: Auto-generates clear, hierarchical API documentation

## API Endpoint Specification

### Core CRUD Operations

#### 1. List Action Lists
```http
GET /api/v1/action-lists?status=active&page=1&per_page=20
```

**Query Parameters**:
- `status` (optional): Filter by status (`active`, `archived`, `all`)
- `is_active` (optional): Boolean filter for active status
- `created_after` (optional): ISO 8601 date filter
- `created_before` (optional): ISO 8601 date filter
- `page` (optional, default=1): Page number
- `per_page` (optional, default=20, max=100): Items per page

**Response** (200 OK):
```json
{
  "action_lists": [
    {
      "id": "AL-001",
      "name": "Sprint 42 Blockers",
      "description": "Critical blockers requiring immediate attention",
      "status": "active",
      "is_active": true,
      "task_count": 7,
      "created_at": "2025-12-28T08:00:00Z",
      "updated_at": "2025-12-28T10:30:00Z"
    }
  ],
  "total": 157,
  "page": 1,
  "per_page": 20,
  "has_more": true
}
```

**OpenAPI Tags**: `["action-lists"]`

#### 2. Create Action List
```http
POST /api/v1/action-lists
Content-Type: application/json

{
  "name": "Q1 2025 Tech Debt",
  "description": "Technical debt items for Q1 cleanup sprint",
  "status": "active",
  "metadata": {
    "priority": "high",
    "owner": "engineering-team"
  }
}
```

**Request Schema** (Pydantic):
```python
class ActionListCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    status: str = Field(default="active", pattern="^(active|archived)$")
    metadata: dict[str, Any] | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Q1 2025 Tech Debt",
                "description": "Technical debt cleanup items",
                "status": "active"
            }
        }
    )
```

**Response** (201 Created):
```json
{
  "id": "AL-158",
  "name": "Q1 2025 Tech Debt",
  "description": "Technical debt items for Q1 cleanup sprint",
  "status": "active",
  "is_active": true,
  "task_count": 0,
  "created_at": "2025-12-28T14:22:00Z",
  "updated_at": "2025-12-28T14:22:00Z"
}
```

**Error Responses**:
- 400 Bad Request: Invalid JSON or validation failure
- 409 Conflict: List with same name already exists (if enforced)

#### 3. Get Action List by ID
```http
GET /api/v1/action-lists/AL-158
```

**Response** (200 OK):
```json
{
  "id": "AL-158",
  "name": "Q1 2025 Tech Debt",
  "description": "Technical debt items for Q1 cleanup sprint",
  "status": "active",
  "is_active": true,
  "task_ids": ["TASK-101", "TASK-203", "TASK-305"],
  "task_count": 3,
  "metadata": {
    "priority": "high",
    "owner": "engineering-team"
  },
  "created_at": "2025-12-28T14:22:00Z",
  "updated_at": "2025-12-28T15:10:00Z"
}
```

**Error Responses**:
- 404 Not Found: List ID does not exist

#### 4. Update Action List
```http
PUT /api/v1/action-lists/AL-158
Content-Type: application/json

{
  "name": "Q1 2025 Tech Debt (Updated)",
  "status": "archived"
}
```

**Request Schema**:
```python
class ActionListUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    status: str | None = Field(None, pattern="^(active|archived)$")
    metadata: dict[str, Any] | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "archived"
            }
        }
    )
```

**Response** (200 OK):
```json
{
  "id": "AL-158",
  "name": "Q1 2025 Tech Debt (Updated)",
  "status": "archived",
  "is_active": false,
  ...
}
```

**Error Responses**:
- 404 Not Found: List ID does not exist
- 400 Bad Request: Validation failure
- 422 Unprocessable Entity: Business rule violation

#### 5. Delete Action List
```http
DELETE /api/v1/action-lists/AL-158
```

**Response** (204 No Content):
```
(empty body)
```

**Error Responses**:
- 404 Not Found: List ID does not exist

### Task Relationship Operations

#### 6. Add Task to List
```http
POST /api/v1/action-lists/AL-001/tasks
Content-Type: application/json

{
  "task_id": "TASK-505",
  "position": 3
}
```

**Request Schema**:
```python
class ActionListAddItemRequest(BaseModel):
    task_id: str = Field(..., pattern="^TASK-[0-9]+$")
    position: int | None = Field(None, ge=0, description="0-indexed position, or append if null")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "task_id": "TASK-505",
                "position": 3
            }
        }
    )
```

**Response** (200 OK):
```json
{
  "id": "AL-001",
  "name": "Sprint 42 Blockers",
  "task_ids": ["TASK-101", "TASK-203", "TASK-305", "TASK-505"],
  "task_count": 4,
  ...
}
```

**Error Responses**:
- 404 Not Found: List or task does not exist
- 409 Conflict: Task already in list
- 422 Unprocessable Entity: Invalid position

#### 7. Remove Task from List
```http
DELETE /api/v1/action-lists/AL-001/tasks/TASK-505
```

**Response** (204 No Content):
```
(empty body)
```

**Error Responses**:
- 404 Not Found: List or task does not exist
- 422 Unprocessable Entity: Task not in list

#### 8. Reorder Tasks in List
```http
POST /api/v1/action-lists/AL-001/tasks/reorder
Content-Type: application/json

{
  "task_ids": ["TASK-305", "TASK-101", "TASK-203"]
}
```

**Request Schema**:
```python
class ReorderItemsRequest(BaseModel):
    task_ids: list[str] = Field(..., min_length=1)

    @field_validator("task_ids")
    @classmethod
    def validate_unique_tasks(cls, v: list[str]) -> list[str]:
        if len(v) != len(set(v)):
            raise ValueError("Duplicate task IDs in reorder request")
        return v
```

**Response** (200 OK):
```json
{
  "id": "AL-001",
  "task_ids": ["TASK-305", "TASK-101", "TASK-203"],
  ...
}
```

**Error Responses**:
- 404 Not Found: List does not exist
- 422 Unprocessable Entity: Task IDs do not match current list membership

### Cross-Entity Queries

#### 9. Find Lists Containing Task
```http
GET /api/v1/action-lists/tasks/TASK-305
```

**Response** (200 OK):
```json
{
  "action_lists": [
    {
      "id": "AL-001",
      "name": "Sprint 42 Blockers",
      "task_count": 3,
      ...
    },
    {
      "id": "AL-042",
      "name": "Critical Path Items",
      "task_count": 12,
      ...
    }
  ],
  "total": 2,
  "page": 1,
  "per_page": 20,
  "has_more": false
}
```

**Error Responses**:
- 404 Not Found: Task does not exist

## Technical Implementation

### Router Structure
```python
"""
Action Lists API Router
CRUD operations and task relationship management.
"""

import structlog
from fastapi import APIRouter, HTTPException, Query, status

from taskman_api.core.errors import AppError, NotFoundError, ValidationError
from taskman_api.core.result import Err, Ok
from taskman_api.dependencies import ActionListSvc
from taskman_api.schemas import (
    ActionListAddItemRequest,
    ActionListCollection,
    ActionListCreate,
    ActionListResponse,
    ActionListUpdate,
    ReorderItemsRequest,
)

logger = structlog.get_logger()

router = APIRouter(
    prefix="/action-lists",
    tags=["action-lists"],
    responses={
        404: {"description": "Action list not found"},
        500: {"description": "Internal server error"},
    },
)
```

### Dependency Injection Pattern
```python
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from taskman_api.core.database import get_session
from taskman_api.services.action_list_service import ActionListService

async def get_action_list_service(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> ActionListService:
    """Dependency for ActionListService with database session."""
    return ActionListService(session)

# Type alias for cleaner signatures
ActionListSvc = Annotated[ActionListService, Depends(get_action_list_service)]
```

### Error Handling Pattern
```python
@router.get("/{list_id}", response_model=ActionListResponse)
async def get_action_list(list_id: str, service: ActionListSvc) -> ActionListResponse:
    """Get action list by ID with comprehensive error handling."""
    result = await service.get(list_id)

    match result:
        case Ok(action_list):
            logger.info("action_list_retrieved", list_id=list_id)
            return action_list
        case Err(NotFoundError() as e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=e.message,
            )
        case Err(AppError() as e):
            logger.error("action_list_get_failed", list_id=list_id, error=e.message)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=e.message,
            )
```

### OpenAPI Documentation Enhancement
```python
@router.post(
    "/{list_id}/tasks",
    response_model=ActionListResponse,
    summary="Add task to action list",
    description="""
    Add a task to an action list at a specific position.

    **Position Behavior**:
    - If `position` is null or omitted, task is appended to end
    - If `position` is specified, existing tasks shift right
    - Position is 0-indexed (0 = first position)

    **Error Conditions**:
    - 404: Action list or task not found
    - 409: Task already exists in list
    - 422: Invalid position (exceeds list size)
    """,
    responses={
        200: {
            "description": "Task successfully added",
            "content": {
                "application/json": {
                    "example": {
                        "id": "AL-001",
                        "name": "Sprint Blockers",
                        "task_ids": ["TASK-101", "TASK-202", "TASK-303"],
                        "task_count": 3
                    }
                }
            }
        },
        409: {
            "description": "Task already in list",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Task TASK-202 already exists in list AL-001"
                    }
                }
            }
        }
    },
    tags=["action-lists", "task-relationships"]
)
async def add_task_to_list(
    list_id: str,
    request: ActionListAddItemRequest,
    service: ActionListSvc
) -> ActionListResponse:
    # ... implementation
```

### Authentication/Authorization Integration
```python
from taskman_api.dependencies import CurrentUser

@router.post("", response_model=ActionListResponse)
async def create_action_list(
    request: ActionListCreate,
    service: ActionListSvc,
    user: CurrentUser,  # JWT-authenticated user
) -> ActionListResponse:
    """Create action list with owner tracking."""
    logger.info("action_list_create_attempt", user_id=user.id)

    # Service layer enforces ownership and permissions
    result = await service.create(request, owner_id=user.id)

    match result:
        case Ok(created):
            logger.info("action_list_created", list_id=created.id, owner=user.id)
            return created
        case Err(error):
            raise HTTPException(status_code=400, detail=str(error))
```

## Integration Test Requirements

**Test Coverage Target**: 20 E2E tests covering:

1. **CRUD Operations** (5 tests):
   - Create list with valid/invalid data
   - List all with pagination
   - Get by ID (exists/not found)
   - Update list (full/partial)
   - Delete list

2. **Task Relationships** (7 tests):
   - Add task to list (success/duplicate/invalid task)
   - Remove task from list (success/not in list)
   - Reorder tasks (valid/invalid order)
   - Add task with position specification

3. **Filtering & Queries** (5 tests):
   - Filter by status (active/archived/all)
   - Filter by date range
   - Find lists by task ID
   - Pagination edge cases (first/last page)

4. **Error Handling** (3 tests):
   - Malformed JSON (400)
   - Resource not found (404)
   - Validation errors (422)

**Test Framework**: `pytest` + `httpx.AsyncClient`

**Example Test**:
```python
@pytest.mark.asyncio
async def test_add_task_to_list_success(client: AsyncClient, db_session: AsyncSession):
    """Test adding a task to an action list."""
    # Arrange: Create list and task
    list_response = await client.post("/api/v1/action-lists", json={
        "name": "Test List",
        "status": "active"
    })
    list_id = list_response.json()["id"]

    task_response = await client.post("/api/v1/tasks", json={
        "title": "Test Task",
        "status": "todo"
    })
    task_id = task_response.json()["id"]

    # Act: Add task to list
    response = await client.post(
        f"/api/v1/action-lists/{list_id}/tasks",
        json={"task_id": task_id}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert task_id in data["task_ids"]
    assert data["task_count"] == 1
```

## Consequences

### Positive

✅ **Complete API Surface**: All ActionList operations accessible via REST API
✅ **Consistency**: Follows established patterns from tasks/sprints/projects routers
✅ **Documentation**: Auto-generated OpenAPI/Swagger with comprehensive examples
✅ **Testability**: Clear endpoint boundaries enable focused E2E testing
✅ **Extensibility**: Easy to add filters, sorting, or sub-resources in future
✅ **Observability**: Structured logging provides operation-level insights

### Negative

⚠️ **Endpoint Proliferation**: 9 endpoints vs typical 5 for basic CRUD
⚠️ **Maintenance Overhead**: More endpoints require more tests and documentation
⚠️ **Complexity**: Task relationship endpoints add cognitive load for API consumers
⚠️ **Performance**: N+1 query risk when loading task details (mitigation: use `task_ids` only)

### Neutral

🔵 **Offset Pagination**: Simple but not ideal for large-scale; acceptable for current scope
🔵 **No Versioning**: API at `/api/v1/` — future breaking changes require v2
🔵 **No Rate Limiting**: Defer to infrastructure layer (API gateway/middleware)

## Mitigation Strategies

**For Endpoint Proliferation**:
- Group related endpoints with OpenAPI tags
- Provide API client SDKs to abstract complexity
- Maintain comprehensive Postman/Insomnia collection

**For N+1 Queries**:
- Use `task_ids` field instead of embedding full task objects
- Implement `?include=tasks` query parameter for expanded responses (future)
- Monitor query performance with structured logging

**For Breaking Changes**:
- Use deprecation warnings before removing endpoints
- Maintain backwards compatibility within v1
- Plan v2 API with cursor pagination and GraphQL consideration

## Related Decisions

- **[ADR-016: Schema Audit - ActionList Integration](./ADR-016-Schema-Audit-ActionList-Integration.md)** — Database schema and field mappings
- **[ADR-017: ActionList Repository Implementation](./ADR-017-ActionList-Repository-Implementation-Strategy.md)** — Data access layer patterns
- **[ADR-018: ActionList Service Layer Architecture](./ADR-018-ActionList-Service-Layer-Architecture.md)** — Business logic orchestration
- **[ADR-003: TaskMan-v2 Backend API Placeholder](./ADR-003-TaskMan-v2-Backend-API-Placeholder.md)** — Overall backend architecture
- **[ADR-001: QSE-UTMW Architecture](./ADR-001-QSE-UTMW-Architecture.md)** — Result monad pattern foundation

## Implementation Checklist

**Phase 1: Core CRUD** (Priority: High):
- [ ] Implement `list_action_lists` with filtering
- [ ] Implement `create_action_list` with validation
- [ ] Implement `get_action_list` with error handling
- [ ] Implement `update_action_list` with partial updates
- [ ] Implement `delete_action_list` with cascade behavior

**Phase 2: Task Relationships** (Priority: High):
- [ ] Implement `add_task_to_list` with position support
- [ ] Implement `remove_task_from_list` with validation
- [ ] Implement `reorder_list_tasks` with atomic update
- [ ] Implement `find_lists_by_task` cross-query

**Phase 3: Documentation** (Priority: Medium):
- [ ] Add OpenAPI examples for all endpoints
- [ ] Create Postman collection with sample requests
- [ ] Document error response schemas
- [ ] Add authentication/authorization notes

**Phase 4: Testing** (Priority: High):
- [ ] Write 20 E2E tests covering all endpoints
- [ ] Add integration tests for error scenarios
- [ ] Performance test pagination with 10,000+ records
- [ ] Load test concurrent task additions

**Phase 5: Observability** (Priority: Medium):
- [ ] Add structured logging to all endpoints
- [ ] Instrument with OpenTelemetry spans
- [ ] Create Grafana dashboard for endpoint metrics
- [ ] Set up alerting for 4xx/5xx rates

## Notes

**Design Rationale**:
- Sub-resource pattern (`/action-lists/{id}/tasks`) chosen over query parameters (`/action-lists/add-task?list_id=...`) for clarity and REST compliance
- Offset pagination preferred over cursor for implementation simplicity and consistency
- Result monad pattern ensures explicit error handling at API boundary

**Future Enhancements** (Out of Scope):
- GraphQL endpoint for flexible querying
- WebSocket support for real-time list updates
- Bulk operations (create/update/delete multiple lists)
- Export/import endpoints (JSON/CSV)
- List templates and cloning

**References**:
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [REST API Design Guidelines](https://restfulapi.net/)
- [OpenAPI Specification 3.1](https://spec.openapis.org/oas/v3.1.0)
- [Richardson Maturity Model](https://martinfowler.com/articles/richardsonMaturityModel.html)

---

**Word Count**: ~1,150 words (excluding code examples)
**Author**: GitHub Copilot (Architect Mode)
**Reviewers**: TBD
**Next Steps**: Begin Phase 1 implementation with T7 task
