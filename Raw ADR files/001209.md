# ADR-021: ActionList API Documentation Strategy

## Status
**Accepted** | 2025-12-28

## Context

TaskMan-v2 backend-api Phase 3 Task T10 requires comprehensive OpenAPI/Swagger documentation for ActionList endpoints. High-quality API documentation is critical for:

1. **Developer Onboarding** — New team members understanding endpoints quickly
2. **Integration Efficiency** — Frontend/client developers consuming the API correctly
3. **Maintenance** — Understanding endpoint contracts during refactoring
4. **Testing** — Clear examples for manual and automated testing

### Current State

**Existing Documentation**:
- FastAPI auto-generates OpenAPI 3.1.0 schema
- Swagger UI available at `/docs` (interactive playground)
- ReDoc available at `/redoc` (clean reference documentation)
- Pydantic models provide basic field validation

**Documentation Gaps**:
- **Endpoint descriptions**: Many endpoints lack summary and detailed descriptions
- **Request examples**: Missing realistic request body examples
- **Response examples**: Auto-generated examples use placeholder values
- **Error documentation**: HTTP error codes not explicitly documented
- **Field descriptions**: Pydantic model fields lack docstrings
- **Usage guides**: No developer walkthrough for common workflows
- **Authentication**: Auth requirements not clearly documented

**Comparable Systems**:
- **Stripe API**: Comprehensive inline examples, error code catalog, guides
- **GitHub API**: Extensive OpenAPI annotations, tutorial sequences
- **Twilio API**: Interactive examples, SDK code snippets, error reference

### Architecture Drivers

**Functional Requirements**:
- Complete OpenAPI schema coverage for all ActionList endpoints
- Request/response examples for every operation
- Field-level documentation for all Pydantic models
- Error response catalog with status codes and meanings
- Developer onboarding guide with sequential workflow

**Quality Attributes**:
- **Usability**: Developers can understand API without asking questions
- **Completeness**: Every endpoint, model, and error documented
- **Accuracy**: Documentation matches actual implementation
- **Maintainability**: Documentation lives with code, updated in same PR
- **Discoverability**: Examples appear in Swagger UI automatically

**Constraints**:
- Must leverage FastAPI's auto-generation capabilities
- Documentation should live in code (no separate doc repos)
- Minimal overhead for developers adding new endpoints
- Must pass quality gate: 100% endpoint coverage

## Decision

**Adopt Enhanced Auto-Generated Documentation Strategy** with four-tier approach:

### Tier 1: Inline OpenAPI Annotations

Use FastAPI decorators and Pydantic docstrings for automatic schema generation:

```python
@router.post(
    "/",
    response_model=ActionListResponse,
    status_code=201,
    summary="Create new action list",
    description="""
    Creates a new action list with the specified title and optional metadata.

    The created list will have 'draft' status by default. Use the 'archived'
    field to create an archived list directly (uncommon).

    Returns the created ActionList with generated UUID and timestamps.
    """,
    responses={
        201: {
            "description": "Action list created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "title": "Sprint 2025-Q1 Backend Tasks",
                        "description": "Core API implementation tasks",
                        "status": "draft",
                        "archived": false,
                        "created_at": "2025-12-28T10:30:00Z",
                        "updated_at": "2025-12-28T10:30:00Z"
                    }
                }
            }
        },
        400: {"description": "Invalid request data (validation error)"},
        409: {"description": "Action list with title already exists"},
        500: {"description": "Internal server error"}
    }
)
async def create_action_list(request: ActionListCreate):
    """Create new action list endpoint handler."""
    ...
```

### Tier 2: Pydantic Schema Documentation

Add comprehensive field descriptions using Pydantic `Field()`:

```python
class ActionListCreate(BaseModel):
    """Request schema for creating new action lists."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Action list title (unique within workspace)",
        examples=["Sprint 2025-Q1 Tasks", "Technical Debt Backlog"]
    )

    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Optional detailed description of the action list purpose",
        examples=["Backend API implementation tasks for Q1 sprint cycle"]
    )

    archived: bool = Field(
        default=False,
        description="Whether the list is archived (rarely set on creation)"
    )
```

### Tier 3: Error Response Documentation

Create centralized error catalog with FastAPI exception handlers:

```python
# docs/api/error-codes.md
| Status | Code | Description | Example Scenario |
|--------|------|-------------|------------------|
| 400 | VALIDATION_ERROR | Request data failed validation | Missing required field |
| 404 | NOT_FOUND | Requested resource doesn't exist | GET /action-lists/{invalid-uuid} |
| 409 | CONFLICT | Resource already exists | Create list with duplicate title |
| 500 | INTERNAL_ERROR | Server-side processing error | Database connection failure |
```

Document in OpenAPI schema:

```python
@router.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors with structured response."""
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": exc.errors()
            }
        }
    )
```

### Tier 4: Developer Usage Guide

Create markdown tutorial walking through common workflows:

```markdown
# ActionList API Quick Start

## Creating Your First Action List

1. **Create the list**:
   ```bash
   POST /api/v1/action-lists
   {
     "title": "My Tasks",
     "description": "Personal task tracking"
   }
   ```

2. **Add tasks to the list**:
   ```bash
   POST /api/v1/action-lists/{list_id}/tasks
   {
     "task_id": "task-uuid-here"
   }
   ```

3. **Query the list with tasks**:
   ```bash
   GET /api/v1/action-lists/{list_id}?include_tasks=true
   ```
```

## Alternatives Considered

### Alternative 1: Minimal Auto-Generated Only

**Approach**: Rely solely on FastAPI's default schema generation without annotations.

**Advantages**:
- Zero documentation overhead
- No maintenance burden
- Automatic updates with code changes

**Disadvantages**:
- ❌ Poor developer experience (generic examples)
- ❌ Missing context about when/why to use endpoints
- ❌ No error guidance
- ❌ Difficult to understand complex workflows

**Verdict**: Rejected — Inadequate for production API

### Alternative 2: External Documentation Tools

**Approach**: Use Postman Collections, Stoplight Studio, or Readme.io for separate documentation.

**Advantages**:
- Rich editing interfaces
- Better styling and presentation
- Can include SDK code examples

**Disadvantages**:
- ❌ Documentation drift (code changes don't update docs)
- ❌ Additional tooling complexity
- ❌ Split sources of truth
- ❌ Requires separate review/approval process

**Verdict**: Rejected — Violates "documentation lives with code" principle

### Alternative 3: Full Technical Writing Process

**Approach**: Dedicated technical writer creates comprehensive documentation suite.

**Advantages**:
- Professional quality
- User-focused language
- Comprehensive tutorials

**Disadvantages**:
- ❌ Overkill for internal API
- ❌ Slow iteration (writer bottleneck)
- ❌ High maintenance cost
- ❌ Documentation lag behind implementation

**Verdict**: Rejected — Not proportional to team size

### Alternative 4: Enhanced Auto-Generated (Selected)

**Approach**: Inline OpenAPI annotations + Pydantic docstrings + usage guide.

**Advantages**:
- ✅ Lives with code (same PR for updates)
- ✅ Auto-generates Swagger UI and ReDoc
- ✅ Minimal overhead (docstrings are good practice anyway)
- ✅ FastAPI native (no new tools)
- ✅ Scales with codebase

**Disadvantages**:
- Requires discipline to write good descriptions
- Initial time investment for existing endpoints

**Verdict**: **Selected** — Best balance of quality and maintainability

## Documentation Quality Standards

### Quality Gate Checklist

All ActionList endpoints must meet these criteria:

**Per-Endpoint Requirements**:
- [ ] Endpoint has `summary` (one-line description)
- [ ] Endpoint has `description` (detailed usage notes)
- [ ] All success responses documented with examples
- [ ] All error responses documented (400, 404, 409, 500)
- [ ] Request model has field descriptions
- [ ] Response model has field descriptions
- [ ] At least one realistic example provided

**Per-Model Requirements**:
- [ ] Model has class docstring
- [ ] Every field has `description` in `Field()`
- [ ] Complex fields have `examples` parameter
- [ ] Validation rules documented (min_length, max_length, etc.)

**API-Level Requirements**:
- [ ] Error code catalog exists (docs/api/error-codes.md)
- [ ] Developer quick start guide exists (docs/api/quickstart.md)
- [ ] Authentication documented (docs/api/authentication.md)
- [ ] Postman collection exported (optional, for convenience)

### Documentation Coverage Metric

**Target**: 100% endpoint coverage

**Measurement**:
```python
documented_endpoints = endpoints_with_summary_and_description
total_endpoints = all_router_endpoints
coverage = (documented_endpoints / total_endpoints) * 100
```

**Automated Check**:
```python
# tests/test_api_documentation.py
def test_all_endpoints_documented():
    """Verify all endpoints have required OpenAPI annotations."""
    from main import app

    undocumented = []
    for route in app.routes:
        if not route.summary or not route.description:
            undocumented.append(route.path)

    assert not undocumented, f"Undocumented endpoints: {undocumented}"
```

## Consequences

### Positive

**Developer Experience**:
- New developers onboard faster with clear examples
- Frontend team can work independently from API docs
- Less Slack/email back-and-forth about "how do I...?"

**Code Quality**:
- Writing documentation forces clarity about endpoint purpose
- Examples serve as lightweight integration tests
- Inconsistencies become obvious during documentation

**Maintenance**:
- Documentation stays synchronized with code (same PR)
- FastAPI regenerates schema automatically
- Swagger UI provides interactive testing environment

**Testing**:
- Examples in docs can be extracted for test fixtures
- Clear error documentation guides test case design
- Postman collection enables manual testing workflows

### Negative

**Developer Overhead**:
- Every new endpoint requires docstrings and examples
- Initial time investment documenting existing endpoints (~4-6 hours)
- Code reviews must include documentation review

**Mitigation**:
- Add documentation checklist to PR template
- Create VSCode snippets for common patterns
- Automate coverage checks in CI

### Neutral

**Tooling**:
- Swagger UI sufficient for internal use (no Postman Pro needed)
- ReDoc provides cleaner reading experience for reference
- Can export OpenAPI schema for external tools if needed

**Migration Path**:
- Document new endpoints immediately (T7-T9 router work)
- Backfill existing endpoints incrementally
- Prioritize most-used endpoints first

## Implementation Plan

### Phase 1: Documentation Infrastructure (T10.1)

**Tasks**:
1. Create error code catalog (docs/api/error-codes.md)
2. Document authentication requirements (docs/api/authentication.md)
3. Set up automated documentation coverage check
4. Add documentation checklist to PR template

**Deliverables**:
- Error reference table
- Auth guide
- CI check for doc coverage
- Updated PR template

**Estimated Effort**: 2-3 hours

### Phase 2: ActionList Endpoint Documentation (T10.2)

**Tasks**:
1. Add OpenAPI annotations to all ActionList CRUD endpoints
2. Enhance Pydantic models with field descriptions
3. Create realistic request/response examples
4. Document all error responses with status codes

**Endpoints to Document**:
- `POST /action-lists` — Create
- `GET /action-lists` — List with filtering
- `GET /action-lists/{id}` — Get single
- `PATCH /action-lists/{id}` — Update
- `DELETE /action-lists/{id}` — Delete
- `POST /action-lists/{id}/tasks` — Add task
- `DELETE /action-lists/{id}/tasks/{task_id}` — Remove task

**Deliverables**:
- Fully annotated router endpoints
- Enhanced Pydantic schemas
- Passing documentation coverage check

**Estimated Effort**: 4-5 hours

### Phase 3: Developer Quick Start Guide (T10.3)

**Tasks**:
1. Create quickstart tutorial (docs/api/quickstart.md)
2. Add workflow examples (create → populate → query)
3. Document common pitfalls and solutions
4. Export Postman collection for convenience

**Deliverables**:
- Quick start guide
- Workflow examples
- Postman collection (actionlist-api.postman_collection.json)

**Estimated Effort**: 2-3 hours

### Acceptance Criteria

**Definition of Done**:
- [ ] All ActionList endpoints have summary and description
- [ ] All Pydantic models have field descriptions
- [ ] Error code catalog complete and accurate
- [ ] Quick start guide includes end-to-end workflow
- [ ] Documentation coverage check passes in CI
- [ ] Swagger UI displays all examples correctly
- [ ] ReDoc renders cleanly without warnings
- [ ] Postman collection exported and validated

**Quality Verification**:
```bash
# Manual verification
1. Open http://localhost:8002/docs
2. Verify all endpoints show descriptions
3. Test "Try it out" with provided examples
4. Confirm error responses match catalog

# Automated verification
pytest tests/test_api_documentation.py -v
```

## References

- [FastAPI Documentation Best Practices](https://fastapi.tiangolo.com/tutorial/schema-extra-example/)
- [OpenAPI 3.1.0 Specification](https://swagger.io/specification/)
- [Pydantic Field Documentation](https://docs.pydantic.dev/latest/concepts/fields/)
- [ADR-019: ActionList API Router Architecture](./ADR-019-ActionList-API-Router-Architecture.md)
- [Stripe API Documentation](https://stripe.com/docs/api) — Example of excellence
- [Postman Collection Format](https://www.postman.com/collection/) — For export reference

---

**Decision Made By**: ContextForge Documenter Agent
**Stakeholders**: Backend Team, Frontend Team, DevOps
**Review Date**: 2026-03-28 (3 months) — Assess coverage metrics and developer feedback
