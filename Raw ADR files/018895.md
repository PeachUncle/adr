# Testing Strategy for Thicker Application

## Status

Accepted

## Context

Testing is a cornerstone of the development process for the Thicker application. Our goal is to ensure that all
components, from the domain to the CLI, are reliable, maintainable, and align with the principles of Clean Architecture.
To achieve this, we follow a rigorous testing strategy rooted in Test-Driven Development (TDD) and emphasize:

1. Isolating components for unit testing.
2. Verifying integration between layers.
3. End-to-end validation of the entire application.
4. Addressing edge cases and potential failure modes.

## Decision

We adopt a layered testing strategy comprising the following types of tests:

### Unit Tests

Unit tests are the foundation of our testing strategy. Each test:

- Targets a single class or function, focusing on isolated behavior.
- Mocks external dependencies, such as file systems or network calls.
- Includes tests for both the domain and adapters.

#### Example

```python
# Domain test
from thicker.domain import calculate_thickness

def test_calculate_thickness():
    input_mesh = ...  # mock or sample mesh
    offset = 0.1
    result = calculate_thickness(input_mesh, offset)
    assert result == expected_mesh
```

### Integration Tests

Integration tests validate interactions between multiple layers, such as:

- Domain and adapters.
- CLI and use case layers.

#### Example

```python
# Adapter integration test
from thicker.adapters.stl_mesh_reader import STLMeshReader

def test_stl_reader_integration():
    reader = STLMeshReader()
    mesh = reader.read("sample.stl")
    assert mesh.vertices == expected_vertices
```

### End-to-End Tests

End-to-end tests verify the complete flow of the application from the CLI to the final output. These tests run the
application in subprocesses and validate the generated outputs.

#### Example

```python
import subprocess

def test_cli_integration():
    result = subprocess.run(
        ["python", "-m", "thicker.cli.cli", "--input", "input.stl", "--output", "output.stl", "--offset", "0.1"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Processing complete" in result.stdout
```

### Edge Case Testing

Special attention is given to edge cases to ensure robustness. This includes:

- Missing or corrupt input files.
- Invalid offsets (e.g., negative values).
- Large files that test scalability.

#### Example

```python
# Edge case test
from thicker.cli.cli import main
import pytest

def test_invalid_offset():
    with pytest.raises(ValueError):
        main(["--input", "input.stl", "--output", "output.stl", "--offset", "-0.1"])
```

### Mocking and Dependency Injection

Mocking is used extensively to:

- Simulate external dependencies (e.g., file system or mesh libraries).
- Ensure tests remain fast and reliable.

Dependency injection ensures:

- Testability of components by allowing mock replacements.
- Adherence to the Dependency Inversion Principle.

### Pre-Commit Testing

We use pre-commit hooks to enforce test execution and code quality checks before committing changes. This ensures:

- All tests pass locally before merging code.
- Static analysis and linting compliance.

#### Pre-Commit Tools

- **Ruff**: For linting and formatting.
- **pytest**: For running all test suites.

### Folder Structure for Tests

Tests are organized to mirror the project structure, for example:

```bash
/tests
    /domain
    /adapters
    /cli
    /integration
    /e2e
```

## Implications

### Advantages

1. **High Confidence:** Comprehensive test coverage reduces the risk of regressions.
2. **Faster Feedback:** Clear separation of test types allows for focused debugging.
3. **Alignment with Clean Architecture:** Testing reinforces architectural boundaries.

### Potential Drawbacks

1. **Increased Overhead:** Writing and maintaining tests requires additional time and effort.
2. **Complexity:** Managing mocks and dependency injection can add complexity to test setup.

## Alternatives Considered

- **Minimal Testing:** Rejected due to the critical nature of the application.
- **Combined Tests:** Rejected to maintain clear boundaries between unit, integration, and e2e tests.

## Decision Owner

Tom Willis

## Date

2024-12-20

---
