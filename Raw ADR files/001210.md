# ADR-022: ActionList Integration Testing Strategy

## Status
**Accepted** | 2025-12-28

## Context

TaskMan-v2 backend-api Phase 3 Task T11 requires comprehensive integration testing across the three-tier ActionList architecture:

1. **API Router Layer** ([ADR-019](./ADR-019-ActionList-API-Router-Architecture.md)) — HTTP endpoints
2. **Service Layer** ([ADR-018](./ADR-018-ActionList-Service-Layer-Architecture.md)) — Business logic
3. **Repository Layer** ([ADR-017](./ADR-017-ActionList-Repository-Implementation-Strategy.md)) — Database access

### Current Testing State

**Existing Unit Test Coverage**:
- **T4**: Repository unit tests (10 test cases) — SQL generation, query validation
- **T6**: Service unit tests (15 test cases) — Business logic, error handling
- **T8**: API router unit tests (20 test cases) — Request/response validation

**Integration Testing Gap**:
- No cross-layer integration tests (API → Service → Repository)
- No end-to-end workflow validation (create → update → query → archive)
- No performance benchmarks for multi-component operations
- No regression testing against existing Task/Sprint/Project endpoints
- No concurrency testing for parallel list operations

**Testing Infrastructure**:
- **pytest** (v7.4.3): Test framework with async support
- **pytest-asyncio**: Async test execution
- **pytest-cov**: Coverage reporting (target: 90%+)
- **httpx**: TestClient for FastAPI endpoints
- **PostgreSQL 15**: Test database with transaction rollback

### Architecture Drivers

**Functional Requirements**:
- Verify complete CRUD workflows across all three layers
- Validate task relationship management (add/remove operations)
- Test error propagation from database to HTTP responses
- Confirm data persistence and retrieval accuracy
- Ensure OpenAPI schema compliance

**Quality Attributes**:
- **Reliability**: Zero flaky tests, deterministic results
- **Performance**: <200ms for 100-task list operations
- **Maintainability**: DRY test fixtures, clear test naming
- **Isolation**: Each test runs in clean transaction, no side effects
- **Coverage**: 90%+ overall, 100% critical paths

**Constraints**:
- Must not break existing Task/Sprint/Project tests
- Test database must support concurrent pytest workers
- CI pipeline execution time <5 minutes for full suite
- Memory footprint <512MB for test execution

## Decision Drivers

### Testing Pyramid Analysis

```
        /\
       /  \    E2E Tests (10%)
      /____\   - Full stack workflows
     /      \  - Performance validation
    /________\ Integration Tests (30%)
   /          \  - Multi-component
  /____________\  - Cross-layer
 /              \ Unit Tests (60%)
/________________\  - Repository (10)
                    - Service (15)
                    - API (20)
```

### Test Database Strategy Options

#### Option 1: SQLite In-Memory
```python
@pytest.fixture
async def test_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
```

**Pros**: Fast, no setup, parallel-safe
**Cons**: PostgreSQL-specific features missing (JSONB, CTEs)
**Verdict**: ❌ ActionList uses PostgreSQL-specific queries

#### Option 2: Test PostgreSQL with Transaction Rollback ⭐ **(Recommended)**
```python
@pytest.fixture
async def test_db():
    engine = create_async_engine(
        "postgresql+asyncpg://test:test@localhost:5433/taskman_test"
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
```

**Pros**: Full PostgreSQL feature parity, accurate query testing
**Cons**: Requires external database, slower than in-memory
**Verdict**: ✅ Accurate, supports all ActionList query patterns

#### Option 3: Docker-Compose Ephemeral PostgreSQL
```yaml
services:
  test-db:
    image: postgres:15-alpine
    environment:
      POSTGRES_PASSWORD: test
      POSTGRES_DB: taskman_test
    ports:
      - "5433:5432"
```

**Pros**: Isolated, reproducible, CI-friendly
**Cons**: Docker dependency, startup overhead
**Verdict**: ✅ Use in CI, optional for local development

## Decision

### Chosen Architecture: Layered Integration Testing

Implement **three-tier integration testing** with PostgreSQL test database, pytest-asyncio, and transaction rollback isolation.

### Test Levels

#### 1. Integration Tests (Multi-Component)

**Scope**: Service + Repository (no HTTP layer)
**Purpose**: Verify business logic executes correct database operations
**Count**: 12 test cases

```python
# tests/integration/test_action_list_integration.py

class TestActionListServiceIntegration:
    """Service + Repository integration tests."""

    @pytest.fixture
    async def service(self, test_db_session):
        """Create service with real repository and database."""
        return ActionListService(session=test_db_session)

    async def test_create_list_with_tasks_integration(self, service, test_tasks):
        """Should create list and add tasks in single transaction."""
        # Arrange
        list_data = ActionListCreateRequest(
            title="Sprint Planning",
            description="Tasks for next sprint"
        )
        task_ids = [task.id for task in test_tasks[:3]]

        # Act
        result = await service.create(list_data)
        assert result.is_ok()
        list_id = result.ok_value.id

        for task_id in task_ids:
            await service.add_task_to_list(list_id, task_id)

        # Assert
        list_result = await service.get(list_id)
        assert len(list_result.ok_value.tasks) == 3

    async def test_archive_list_updates_status(self, service, test_list):
        """Should update status and set archived_at timestamp."""
        # Act
        result = await service.archive(test_list.id)

        # Assert
        assert result.is_ok()
        updated = result.ok_value
        assert updated.status == "archived"
        assert updated.archived_at is not None
```

#### 2. E2E Tests (Full Stack)

**Scope**: API → Service → Repository → Database
**Purpose**: Validate complete HTTP workflows
**Count**: 15 test cases

```python
# tests/e2e/test_action_list_api_e2e.py

class TestActionListAPIE2E:
    """Full stack API integration tests."""

    @pytest.fixture
    def client(self, test_app):
        """Create TestClient with test database."""
        return TestClient(test_app)

    def test_create_list_add_tasks_query_workflow(self, client, test_tasks):
        """Should support complete list lifecycle via API."""
        # Step 1: Create list
        response = client.post("/api/v1/action-lists", json={
            "title": "Feature Development",
            "description": "Backend tasks"
        })
        assert response.status_code == 201
        list_id = response.json()["id"]

        # Step 2: Add tasks
        for task in test_tasks[:5]:
            response = client.post(
                f"/api/v1/action-lists/{list_id}/tasks/{task['id']}"
            )
            assert response.status_code == 200

        # Step 3: Query list
        response = client.get(f"/api/v1/action-lists/{list_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) == 5

        # Step 4: Archive list
        response = client.post(f"/api/v1/action-lists/{list_id}/archive")
        assert response.status_code == 200
        assert response.json()["status"] == "archived"

    def test_error_propagation_404_not_found(self, client):
        """Should return 404 when list doesn't exist."""
        response = client.get("/api/v1/action-lists/nonexistent-id")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
```

#### 3. Performance Tests

**Scope**: Response time benchmarks
**Purpose**: Prevent performance regressions
**Count**: 6 test cases

```python
# tests/performance/test_action_list_performance.py

class TestActionListPerformance:
    """Performance benchmarks for ActionList operations."""

    @pytest.mark.benchmark
    async def test_add_100_tasks_under_200ms(self, service, test_list, test_tasks):
        """Should add 100 tasks in <200ms total."""
        import time
        start = time.perf_counter()

        # Act
        for task in test_tasks[:100]:
            await service.add_task_to_list(test_list.id, task.id)

        duration = (time.perf_counter() - start) * 1000  # Convert to ms

        # Assert
        assert duration < 200, f"Operation took {duration:.2f}ms (limit: 200ms)"

    @pytest.mark.benchmark
    async def test_query_list_with_100_tasks_under_50ms(self, service, test_list_with_tasks):
        """Should query list with 100 tasks in <50ms."""
        import time
        start = time.perf_counter()

        # Act
        result = await service.get(test_list_with_tasks.id)

        duration = (time.perf_counter() - start) * 1000

        # Assert
        assert result.is_ok()
        assert duration < 50, f"Query took {duration:.2f}ms (limit: 50ms)"
```

#### 4. Regression Tests

**Scope**: Existing Task/Sprint/Project endpoints
**Purpose**: Ensure ActionList doesn't break existing features
**Count**: 8 test cases

```python
# tests/regression/test_existing_endpoints.py

class TestExistingEndpointsRegression:
    """Verify ActionList doesn't break existing features."""

    def test_task_crud_still_works(self, client):
        """Should create, read, update, delete tasks."""
        # Create
        response = client.post("/api/v1/tasks", json={
            "title": "Test Task",
            "priority": 3
        })
        assert response.status_code == 201
        task_id = response.json()["id"]

        # Read
        response = client.get(f"/api/v1/tasks/{task_id}")
        assert response.status_code == 200

        # Update
        response = client.put(f"/api/v1/tasks/{task_id}", json={
            "title": "Updated Task"
        })
        assert response.status_code == 200

        # Delete
        response = client.delete(f"/api/v1/tasks/{task_id}")
        assert response.status_code == 204

    def test_task_deletion_cascades_to_action_lists(self, client, test_task_in_list):
        """Should remove task from all lists when task is deleted."""
        task_id = test_task_in_list["task_id"]
        list_id = test_task_in_list["list_id"]

        # Delete task
        response = client.delete(f"/api/v1/tasks/{task_id}")
        assert response.status_code == 204

        # Verify removed from list
        response = client.get(f"/api/v1/action-lists/{list_id}")
        task_ids = [t["id"] for t in response.json()["tasks"]]
        assert task_id not in task_ids
```

### Test Fixtures Architecture

```python
# tests/conftest.py
"""Shared test fixtures for ActionList integration testing."""

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient

from src.main import app
from src.models.base import Base


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        "postgresql+asyncpg://test:test@localhost:5433/taskman_test",
        echo=False,
        pool_pre_ping=True
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def test_db_session(test_engine):
    """Create test database session with transaction rollback."""
    async_session = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        async with session.begin():
            yield session
            await session.rollback()  # Rollback after each test


@pytest.fixture
async def test_client(test_db_session):
    """Create test client with dependency overrides."""
    async def override_get_session():
        yield test_db_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
async def test_tasks(test_db_session):
    """Factory: Create 100 test tasks for performance testing."""
    from src.models.task import Task

    tasks = [
        Task(
            title=f"Test Task {i}",
            description=f"Description {i}",
            priority=i % 5 + 1,
            status="draft"
        )
        for i in range(100)
    ]

    test_db_session.add_all(tasks)
    await test_db_session.commit()

    return tasks


@pytest.fixture
async def test_list(test_db_session):
    """Factory: Create single test ActionList."""
    from src.models.action_list import ActionList

    action_list = ActionList(
        title="Test Action List",
        description="Test description",
        status="active"
    )

    test_db_session.add(action_list)
    await test_db_session.commit()

    return action_list


@pytest.fixture
async def test_list_with_tasks(test_db_session, test_list, test_tasks):
    """Factory: ActionList with 100 associated tasks."""
    from src.models.action_list_task import ActionListTask

    associations = [
        ActionListTask(
            action_list_id=test_list.id,
            task_id=task.id
        )
        for task in test_tasks[:100]
    ]

    test_db_session.add_all(associations)
    await test_db_session.commit()

    return test_list
```

### Test Scenarios Coverage Matrix

| Scenario | Unit | Integration | E2E | Performance | Regression |
|----------|------|-------------|-----|-------------|------------|
| Create list | ✅ T4,T6,T8 | ✅ | ✅ | — | — |
| Add task to list | ✅ T4,T6,T8 | ✅ | ✅ | ✅ | — |
| Remove task from list | ✅ T4,T6,T8 | ✅ | ✅ | — | — |
| Query list with tasks | ✅ T4,T6,T8 | ✅ | ✅ | ✅ | — |
| Archive list | ✅ T6,T8 | ✅ | ✅ | — | — |
| Filter by status | ✅ T4,T6,T8 | ✅ | ✅ | — | — |
| 404 error handling | ✅ T6,T8 | ✅ | ✅ | — | — |
| Validation errors | ✅ T8 | — | ✅ | — | — |
| Duplicate task prevention | ✅ T6 | ✅ | ✅ | — | — |
| Concurrent list operations | — | — | — | ✅ | — |
| Task deletion cascade | — | ✅ | ✅ | — | ✅ |
| Existing Task CRUD | — | — | — | — | ✅ |
| Existing Sprint CRUD | — | — | — | — | ✅ |
| Existing Project CRUD | — | — | — | — | ✅ |

### Quality Gates

**Pre-Commit**:
- All unit tests pass (T4, T6, T8)
- Linting clean (ruff, mypy)

**CI Pipeline**:
- All integration tests pass (12 cases)
- All E2E tests pass (15 cases)
- Performance benchmarks meet targets (<200ms, <50ms)
- Regression tests pass (8 cases)
- Overall coverage ≥90%

**Blocking Criteria**:
- ❌ Any test failure (zero tolerance)
- ❌ Coverage drop below 90%
- ❌ Performance regression >10%
- ❌ Flaky tests (non-deterministic failures)

## Consequences

### Positive

✅ **Comprehensive Coverage**: 90%+ ensures critical paths validated
✅ **Regression Protection**: Existing features remain stable
✅ **Performance Baseline**: Benchmarks prevent future regressions
✅ **Isolation**: Transaction rollback ensures clean test state
✅ **CI Integration**: Automated testing in GitHub Actions

### Negative

⚠️ **Test Execution Time**: Full suite ~3-5 minutes (acceptable for CI)
⚠️ **PostgreSQL Dependency**: Requires test database setup
⚠️ **Fixture Complexity**: Shared fixtures increase maintenance burden

### Mitigations

- Use pytest markers to run fast tests in development: `pytest -m "not slow"`
- Provide Docker Compose setup for one-command test database
- Document fixture architecture in `tests/README.md`
- Monitor test execution time, optimize slow tests

## Alternatives Considered

### Alternative 1: SQLite In-Memory Only
**Rejected**: ActionList queries use PostgreSQL-specific features (JSONB, CTEs)

### Alternative 2: Mock Everything
**Rejected**: Integration tests require real database interactions for confidence

### Alternative 3: Manual Testing Only
**Rejected**: Non-deterministic, slow, doesn't scale with codebase growth

## Implementation Notes

### File Structure
```
tests/
├── conftest.py                    # Shared fixtures
├── integration/
│   ├── __init__.py
│   └── test_action_list_integration.py  # 12 tests
├── e2e/
│   ├── __init__.py
│   └── test_action_list_api_e2e.py      # 15 tests
├── performance/
│   ├── __init__.py
│   └── test_action_list_performance.py  # 6 tests
├── regression/
│   ├── __init__.py
│   └── test_existing_endpoints.py       # 8 tests
└── README.md                      # Testing documentation
```

### pytest Configuration
```ini
# pytest.ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    integration: Multi-component integration tests
    e2e: Full stack end-to-end tests
    performance: Performance benchmark tests
    regression: Regression protection tests
    slow: Tests that take >1 second

addopts =
    --strict-markers
    --tb=short
    --cov=src
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=90
```

### CI Integration (GitHub Actions)
```yaml
# .github/workflows/test.yml
name: Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: taskman_test
        ports:
          - 5433:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run integration tests
        run: pytest tests/ --cov --cov-fail-under=90

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### Test Execution Commands

```bash
# Run all tests
pytest tests/

# Run only integration tests
pytest tests/integration/ -v

# Run E2E tests
pytest tests/e2e/ -v

# Run performance benchmarks
pytest tests/performance/ -m performance

# Run fast tests only (development)
pytest tests/ -m "not slow"

# Run with coverage report
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/integration/test_action_list_integration.py -v

# Run with detailed output
pytest tests/ -vv --tb=long
```

### Success Metrics

- **Coverage**: 90%+ overall, 100% on critical paths
- **Speed**: Full suite <5 minutes in CI
- **Reliability**: Zero flaky tests over 100 runs
- **Maintainability**: Adding new test <30 minutes
- **Documentation**: Every test has clear docstring

---

**Related ADRs**:
- [ADR-017: ActionList Repository Implementation Strategy](./ADR-017-ActionList-Repository-Implementation-Strategy.md)
- [ADR-018: ActionList Service Layer Architecture](./ADR-018-ActionList-Service-Layer-Architecture.md)
- [ADR-019: ActionList API Router Architecture](./ADR-019-ActionList-API-Router-Architecture.md)

**Implementation Task**: T11 - Integration Testing Strategy
**Dependencies**: T4 (Repository Tests), T6 (Service Tests), T8 (API Tests)
**Next Steps**: T12 - Documentation & Deployment
