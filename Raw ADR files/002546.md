# ADR-001: API Endpoint Structure and Versioning

## Status

**Accepted** - 2026-01-07

## Context

Luminote needs a clear and consistent API structure that:

- Supports future versioning as features evolve
- Follows REST conventions for predictability
- Enables GitHub Copilot to add new endpoints following patterns
- Allows frontend and backend teams to work independently
- Supports clear separation between public and internal APIs

Without a defined structure, endpoints could become inconsistent, making
maintenance difficult and confusing for both humans and AI agents.

## Decision

We will use the following API endpoint structure:

### URL Structure

```
/api/v1/{resource}[/{id}][/{action}]
```

**Examples:**

- `POST /api/v1/extract` - Extract content from URL
- `POST /api/v1/translate` - Translate content
- `POST /api/v1/translate/stream` - Stream translation
- `GET /api/v1/config/validate` - Validate configuration
- `POST /api/v1/history` - Save history entry
- `GET /api/v1/history/{id}` - Get specific history entry
- `DELETE /api/v1/history/{id}` - Delete history entry

### Endpoint Conventions

1. **Resource-Based Naming**

   - Use plural nouns for collections: `/translations`, `/extractions`
   - Use singular for singleton resources: `/config`

1. **HTTP Methods**

   - `GET` - Retrieve resource(s)
   - `POST` - Create new resource or trigger action
   - `PUT` - Update entire resource
   - `PATCH` - Partial update
   - `DELETE` - Remove resource

1. **Versioning**

   - Version prefix: `/api/v1/`
   - Major version only (no minor versions in URL)
   - Breaking changes require new major version

1. **Actions on Resources**

   - Use sub-resources for actions: `/translate/stream`
   - Avoid verbs in endpoint names except for actions

1. **Query Parameters**

   - Use for filtering: `?language=en`
   - Use for pagination: `?page=1&per_page=20`
   - Use for sorting: `?sort=date&order=desc`

### API Organization

```python
# backend/app/api/v1/router.py

from fastapi import APIRouter
from app.api.v1.endpoints import extract, translate, config, history

api_router = APIRouter()

api_router.include_router(
    extract.router,
    prefix="/extract",
    tags=["extraction"]
)

api_router.include_router(
    translate.router,
    prefix="/translate",
    tags=["translation"]
)

api_router.include_router(
    config.router,
    prefix="/config",
    tags=["configuration"]
)

api_router.include_router(
    history.router,
    prefix="/history",
    tags=["history"]
)
```

### Response Format

All responses follow consistent structure:

```python
# Success response
{
  "success": true,
  "data": { ... },
  "metadata": {
    "request_id": "uuid",
    "timestamp": "2026-01-07T12:00:00Z",
    "processing_time": 0.123
  }
}

# Error response
{
  "error": "Error type",
  "details": [
    {
      "code": "ERROR_CODE",
      "message": "Human-readable message",
      "field": "optional_field_name"
    }
  ],
  "request_id": "uuid"
}
```

## Consequences

### Positive

- **Predictable**: Developers and Copilot can infer endpoint patterns
- **Scalable**: Easy to add new versions without breaking existing clients
- **RESTful**: Follows industry standards, making onboarding easier
- **Organized**: Clear separation by resource type
- **Testable**: Consistent patterns make testing easier

### Negative

- **Verbosity**: URL paths are longer with version prefix
- **Migration Cost**: Moving to v2 requires client updates
- **Not GraphQL**: Less flexible than GraphQL for complex queries (acceptable
  trade-off for simplicity)

### Trade-offs

- Chose REST over GraphQL for simplicity and better Copilot compatibility
- Chose major-version-only to avoid URL complexity
- Chose resource-based over action-based for REST compliance

## Alternatives Considered

### 1. No Versioning

**Pros:**

- Simpler URLs
- Less boilerplate

**Cons:**

- Breaking changes break all clients
- No way to deprecate endpoints gradually
- Difficult to maintain backward compatibility

**Verdict:** Rejected - Versioning is essential for long-term maintenance

### 2. GraphQL

**Pros:**

- More flexible querying
- Single endpoint
- Strongly typed schema

**Cons:**

- More complex to implement
- Harder for Copilot to follow patterns
- Overkill for simple CRUD operations
- Requires specialized tooling

**Verdict:** Rejected - REST is sufficient for our use case

### 3. Action-Based Endpoints (RPC-style)

```
POST /api/v1/extractContent
POST /api/v1/translateText
POST /api/v1/validateApiKey
```

**Pros:**

- Clear action names
- Simple to understand

**Cons:**

- Not RESTful
- Harder to apply standard HTTP semantics
- Less predictable for Copilot

**Verdict:** Rejected - REST conventions are better for standardization

### 4. Header-Based Versioning

```
GET /api/extract
Header: API-Version: v1
```

**Pros:**

- Cleaner URLs
- Version can be changed per request

**Cons:**

- Less visible in documentation
- Harder to test with curl/browser
- Copilot might miss header requirement

**Verdict:** Rejected - URL-based versioning is more explicit

## Implementation Notes

### For GitHub Copilot

When creating new endpoints, follow this pattern:

```python
# backend/app/api/v1/endpoints/example.py

from fastapi import APIRouter, HTTPException
from app.models.schemas import ExampleRequest, ExampleResponse
from app.core.errors import LuminoteException

router = APIRouter()

@router.post("/", response_model=ExampleResponse)
async def create_example(request: ExampleRequest):
    """
    Create a new example resource.

    Args:
        request: Example creation request

    Returns:
        Created example resource

    Raises:
        HTTPException: On validation or processing errors
    """
    try:
        # Implementation here
        pass
    except LuminoteException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
```

### Endpoint Documentation

All endpoints must include:

- Docstring with description
- Request/response models (Pydantic)
- Example requests in docstring or API docs
- Error codes in docstring

### Testing Pattern

```python
# tests/api/test_example.py

def test_create_example_success(client):
    response = client.post(
        "/api/v1/example",
        json={"field": "value"}
    )
    assert response.status_code == 200
    assert response.json()["success"] is True

def test_create_example_validation_error(client):
    response = client.post(
        "/api/v1/example",
        json={"invalid": "data"}
    )
    assert response.status_code == 422
    assert "error" in response.json()
```

## References

- [REST API Design Best Practices](https://restfulapi.net/)
- [FastAPI Router Documentation](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [Feature Specifications](../feature-specifications.md)
- [Infrastructure Requirements](../infrastructure-requirements.md)

## Changelog

- 2026-01-07: Initial version accepted
