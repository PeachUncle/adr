# ADR-0006: Testing Framework and TDD Approach

**Status:** Accepted  
**Date:** 2025-12-02  
**Supersedes:** None  
**Superseded By:** N/A

---

## Context

The work-prod application requires a comprehensive testing strategy to support Test-Driven Development (TDD) using vertical slice architecture. We need to select appropriate testing frameworks for:

1. **Backend Testing** (Python/Flask)
2. **Frontend Testing** (React/Vite)
3. **CLI Testing** (Click-based commands)
4. **End-to-End Testing** (Full stack integration)

### Requirements

- Support TDD workflow (write tests first, then implement)
- Fast test execution for rapid feedback
- Easy database setup/teardown for backend tests
- Component testing for React UI
- Full integration testing across backend and frontend
- Code coverage reporting (>80% target)
- CI/CD integration (GitHub Actions)

### Constraints

- Must integrate well with existing tech stack:
  - Backend: Flask with application factory pattern
  - Frontend: React 18 + Vite
  - Database: SQLite with SQLAlchemy
  - State Management: Zustand
- Should minimize configuration overhead
- Should have active community support

---

## Decision

We will use the following testing frameworks:

### Backend: pytest

- **Framework:** pytest with pytest-flask, pytest-cov, pytest-mock plugins
- **Test Types:** Unit tests (models, services) and integration tests (API endpoints)
- **Coverage Tool:** pytest-cov with HTML and terminal reports
- **Coverage Target:** >80% overall, >90% for models

### Frontend: Vitest

- **Framework:** Vitest with @testing-library/react
- **Test Types:** Component tests and store tests (Zustand)
- **Coverage Tool:** Vitest built-in coverage (v8 provider)
- **Coverage Target:** >75% overall, >90% for stores

### E2E: Playwright

- **Framework:** @playwright/test
- **Test Types:** End-to-end user flows across full stack
- **Browsers:** Chromium, Firefox, WebKit (cross-browser testing)
- **Debugging:** Trace Viewer, screenshots, video capture

### CLI: Click's CliRunner

- **Framework:** Click's built-in CliRunner (part of click package)
- **Test Types:** Integration tests for CLI commands
- **Coverage Tool:** pytest-cov (CLI tests run with pytest)
- **Coverage Target:** >80% for CLI commands

### Test Organization

**Backend:**
```
backend/tests/
├── conftest.py              # Shared fixtures
├── unit/models/             # Model unit tests
├── unit/services/           # Service unit tests
├── integration/api/         # API endpoint integration tests
└── fixtures/                # Test data factories
```

**Frontend:**
```
frontend/src/
├── components/*.test.jsx    # Colocated component tests
├── stores/*.test.js         # Colocated store tests
└── tests/
    ├── setup.js             # Test environment setup
    └── mocks/               # Mock API responses
```

**E2E:**
```
tests/e2e/
├── projects/                # Feature-based E2E tests
├── fixtures/                # Shared test data
└── utils/                   # Test helpers
```

**CLI:**
```
scripts/project_cli/tests/
├── integration/             # CLI command integration tests (co-located with CLI code)
│   ├── test_list_cmd.py
│   ├── test_get_cmd.py
│   ├── test_crud_cmds.py
│   ├── test_config_cmd.py
│   ├── test_convenience_cmds.py
│   ├── test_import_cmd.py
│   ├── test_error_handling.py
│   ├── test_edge_cases.py
│   └── test_helpers.py      # FlaskTestClientAdapter
└── conftest.py              # CLI test fixtures (imports backend fixtures)
```

---

## Consequences

### Positive

**pytest:**
- Industry standard for Python testing, massive ecosystem
- Excellent Flask integration via pytest-flask plugin
- Powerful fixture system for database setup/teardown
- Clean, readable test syntax (simple functions, assert statements)
- Rich plugin ecosystem (100+ plugins available)

**Vitest:**
- Zero-configuration integration with Vite projects
- 10-20x faster than Jest due to Vite's esbuild transforms
- Jest-compatible API (familiar to most developers)
- Native ESM support, no transpilation needed
- Lightning-fast watch mode for TDD workflow

**Playwright:**
- Modern, reliable, less flaky than older tools (Selenium, Cypress)
- Excellent debugging tools (Trace Viewer, Inspector, VS Code extension)
- Cross-browser support (Chromium, Firefox, Safari/WebKit)
- Auto-wait reduces flaky tests
- Superior CI/CD integration

**CliRunner:**
- Built into Click framework (no additional dependencies)
- Simple API: `runner.invoke(cli, ['command', 'args'])`
- Captures stdout/stderr and exit codes
- Works seamlessly with pytest fixtures
- Can mock environment variables and config files

**Overall:**
- Complete testing coverage across all layers
- Fast feedback loop for TDD workflow
- Industry-standard tools with strong community support
- Clear test organization aligned with vertical slices

### Negative

**Learning Curve:**
- Team needs to learn pytest fixtures and pytest-flask patterns
- Playwright has more concepts than simpler tools like Cypress
- Multiple testing frameworks to maintain (pytest, Vitest, Playwright, CliRunner)

**Configuration:**
- Multiple configuration files (pytest.ini, vitest.config.js, playwright.config.js)
- Need to ensure consistent coverage thresholds across layers
- E2E tests require running both backend and frontend servers

**Maintenance:**
- E2E tests are more brittle than unit/integration tests
- Need to keep test frameworks updated separately
- Playwright browser binaries require installation and updates

### Mitigations

- **Learning:** Provide examples and templates in Phase 0
- **Configuration:** Document all settings in testing-strategy.md
- **Maintenance:** Start with minimal E2E tests, focus on unit/integration
- **Consistency:** Use pre-commit hooks to enforce test runs

---

## Alternatives Considered

### Alternative 1: unittest (Backend)

- **Description:** Python's built-in testing framework
- **Pros:** No external dependencies, familiar to Python developers
- **Cons:** More boilerplate (class-based, `self.assertEqual`), less flexible fixtures
- **Why Not Chosen:** pytest is more Pythonic, has better Flask integration, and superior fixture system

### Alternative 2: Jest (Frontend)

- **Description:** Popular JavaScript testing framework
- **Pros:** Massive ecosystem, widely adopted, many tutorials
- **Cons:** Requires configuration for Vite, slower than Vitest, ESM issues
- **Why Not Chosen:** Vitest provides zero-config Vite integration and 10-20x faster execution

### Alternative 3: Cypress (E2E)

- **Description:** End-to-end testing framework with nice developer experience
- **Pros:** Excellent time-travel debugging, nice UI, good documentation
- **Cons:** Chromium-only by default, slower than Playwright, less powerful
- **Why Not Chosen:** Playwright has better cross-browser support, faster execution, and superior debugging tools (Trace Viewer)

### Alternative 4: nose2 (Backend)

- **Description:** Successor to nose testing framework
- **Pros:** Compatible with unittest, plugin system
- **Cons:** Maintenance mode, smaller community than pytest
- **Why Not Chosen:** pytest is actively developed with much larger ecosystem

---

## Implementation Notes

### Phase 0 Setup

In Phase 0 (Development Environment), implement:

1. Install testing frameworks:
   ```bash
   # Backend
   pip install pytest pytest-flask pytest-cov pytest-mock
   
   # Frontend
   npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom
   
   # E2E
   npm install -D @playwright/test
   npx playwright install
   
   # CLI (no additional install needed - CliRunner is part of click)
   # CliRunner is already available if click is installed
   ```

2. Create configuration files (pytest.ini, vitest.config.js, playwright.config.js)

3. Set up shared fixtures (backend conftest.py, frontend setup.js)

4. Write first test (health check endpoint) to verify setup

### TDD Workflow

For each vertical slice (e.g., "List Projects"):

1. **Backend Model Test** → Implement model
2. **Backend API Test** → Implement endpoint
3. **CLI Test** (for CLI commands) → Implement CLI command
4. **Frontend Component Test** → Implement component
5. **Frontend Store Test** → Implement Zustand store
6. **E2E Test** (optional) → Verify full flow

### Coverage Enforcement

**Local Development:**
```bash
# Backend (includes CLI tests)
pytest --cov=app --cov-fail-under=80

# Frontend
npm test -- --coverage

# E2E
npx playwright test
```

### CLI Testing Pattern

Example CLI test using CliRunner:

```python
# scripts/project_cli/tests/integration/test_list_cmd.py
import pytest
from click.testing import CliRunner
from app.models.project import Project
from app import db

# CLI import handled via importlib in test file
# Backend fixtures (app, client, db) imported from backend/tests/conftest.py

def test_list_command_success(cli_runner, app, mock_api_for_cli):
    """Test list command returns successfully."""
    with app.app_context():
        result = cli_runner.invoke(cli, ['list'])
        assert result.exit_code == 0
        assert 'Projects' in result.output

def test_list_command_with_filters(cli_runner, app, mock_api_for_cli):
    """Test list command with status filter."""
    with app.app_context():
        result = cli_runner.invoke(cli, ['list', '--status', 'active'])
        assert result.exit_code == 0
```

**CI/CD (GitHub Actions):**
- Run all test suites on pull requests
- Block merge if coverage drops below threshold
- Generate coverage reports and upload to PR comments
- Run E2E tests only on main integration tests (not every PR)

### Pre-commit Hooks

Consider adding pre-commit hooks to:
- Run unit tests before commit
- Check coverage thresholds
- Run linters (flake8, ESLint)

---

## References

### Research Documents

- [Testing Strategy Research](../research/tech-stack/testing-strategy.md) - Comprehensive analysis of testing frameworks and patterns (300+ lines)

### Official Documentation

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-flask Plugin](https://pytest-flask.readthedocs.io/)
- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Playwright Documentation](https://playwright.dev/)
- [Click Testing Documentation](https://click.palletsprojects.com/en/8.1.x/testing/)

### Related ADRs

- **ADR-0001:** Flask Backend Architecture - Backend patterns that tests must cover
- **ADR-0002:** React Frontend Architecture - Frontend patterns that tests must cover
- **ADR-0003:** SQLite Database Design - Database testing considerations
- **ADR-0004:** Flask-React Integration Strategy - Integration testing approach
- **ADR-0005:** Projects as Foundation Architecture - First feature to implement with TDD

### Project Learnings

- **Phase 6 Reflection:** CLI Enhancement learnings - Identified CliRunner as testing approach

### External Resources

- [Testing Flask Applications with pytest](https://testdriven.io/blog/flask-pytest/)
- [Testing React with Vitest](https://www.robinwieruch.de/vitest-react-testing-library/)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)

---

**Last Updated:** 2025-12-06  
**Status:** ✅ Accepted and Active  
**Implementation:** Phase 0 - Development Environment (CLI testing added Phase 7)


