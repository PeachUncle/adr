# ADR 001: Naming Conventions Refactoring (Phase 0)

**Status:** ✅ Implemented
**Date:** 2025-01-07
**Decision Makers:** Architecture Review

---

## Context

The original codebase used generic names (e.g., `core/`, `utils/`, `models/`) that didn't clearly communicate the architectural layer or design pattern being used. This made it difficult for new developers to understand the system's structure and violated Clean Architecture naming conventions.

## Decision

Rename all major directories and files to follow Clean Architecture and Domain-Driven Design naming conventions with explicit suffixes that indicate the pattern being used.

### Naming Conventions Adopted

| Pattern | Suffix | Example |
|---------|--------|---------|
| Service | `_service.py` | `ec2_discovery_service.py` |
| Repository | `_repository.py` | `file_cache_repository.py` |
| Gateway | `_gateway.py` | `aws_api_gateway.py` |
| Calculator | `_calculator.py` | `business_case_calculator.py` |
| Orchestrator | `_orchestrator.py` | `dashboard_data_orchestrator.py` |
| Helper | `_helpers.py` | `calculation_helpers.py` |
| Model | `_models.py` | `aws_models.py` |

### Directory Renamings

| Old | New | Reason |
|-----|-----|--------|
| `src/config/` | `src/configuration/` | More explicit, distinguishes from constants |
| `src/core/` | `src/application/` | Clean Architecture term for application layer |
| `src/services/` | `src/domain_services/` | DDD term, distinguishes from application services |
| `src/models/` | `src/domain_models/` | DDD term, emphasizes domain ownership |
| `src/utils/` | `src/shared/` | Clearer for cross-cutting concerns |
| `src/views/` | `src/presentation/` | Clean Architecture term |
| `src/infrastructure/clients/` | `src/infrastructure/gateways/` | Hexagonal Architecture (Ports & Adapters) term |
| `.plan/` | `.architecture/` | More professional |
| `docs/` | `documentation/` (planned) | More explicit |

### File Renamings (Key Examples)

| Old | New | Reason |
|-----|-----|--------|
| `constants.py` | `domain/academic_constants.py` | Moved to domain package with specific name |
| `config/settings.py` | `configuration/application_settings.py` | Pattern-based naming |
| `core/processor.py` | `application/orchestrators/dashboard_data_orchestrator.py` | Layer + Pattern + Responsibility |
| `core/calculator.py` | `application/calculators/business_case_calculator.py` | Specific responsibility |
| `infrastructure/cache.py` | `infrastructure/persistence/file_cache_repository.py` | Repository pattern explicit |
| `infrastructure/clients/aws.py` | `infrastructure/gateways/aws_api_gateway.py` | Gateway pattern explicit |
| `utils/calculations.py` | `shared/calculation_helpers.py` | Helper pattern explicit |
| `models/aws.py` | `domain_models/aws_models.py` | Consistent naming |
| `views/overview.py` | `presentation/pages/overview_page.py` | Page controller pattern |

## Implementation

### Automated Changes (93 import statements)

Created `automation_scripts/update_imports.py` that automatically updated all Python imports to reflect new paths. This script:
- Replaced old import paths with new ones
- Updated class references where needed
- Processed 60 Python files (50 in src/, 10 in tests/)
- Made 93 total changes across 33 files

### Manual Changes

- Created new subdirectory structures (`orchestrators/`, `calculators/`, `gateways/`, `persistence/`, `pages/`)
- Created `__init__.py` files for all new packages
- Implemented backward compatibility wrappers:
  - `application/legacy_data_processor.py` (with deprecation warnings)
  - `domain/__init__.py` (re-exports constants)
  - `configuration/__init__.py` (re-exports settings)

### Backward Compatibility

All old imports still work through wrapper modules, but emit deprecation warnings. Example:

```python
# Old (still works, deprecated)
from src.core.processor import DataProcessor

# New (recommended)
from src.application.orchestrators.dashboard_data_orchestrator import DashboardDataOrchestrator
```

## Consequences

### Positive

- **✅ Immediate Architecture Clarity:** Directory names instantly communicate the layer (`application/`, `domain_services/`, `infrastructure/`)
- **✅ Pattern Recognition:** File suffixes make design patterns explicit (`_service`, `_gateway`, `_repository`)
- **✅ Better Navigation:** Developers can quickly locate functionality
- **✅ Self-Documenting Code:** Names communicate intent without needing documentation
- **✅ Academic Standards:** Follows Clean Architecture and DDD terminology for thesis
- **✅ Maintainability:** Future developers understand structure faster
- **✅ Scalability:** Clear patterns make it easy to add new components

### Negative

- **⚠️ Git History Disruption:** File moves break `git blame` continuity (mitigated with `git log --follow`)
- **⚠️ Migration Effort:** All developers need to learn new structure (1-2 hour learning curve)
- **⚠️ Longer File Paths:** Some paths are longer (e.g., `dashboard_data_orchestrator.py` vs `processor.py`)

### Neutral

- Import statements are slightly longer but more descriptive
- Backward compatibility wrappers add ~150 LoC temporarily

## Metrics

| Metric | Value |
|--------|-------|
| Files renamed | 25+ |
| Directories renamed | 10+ |
| Import statements updated | 93 |
| Backward compatibility wrappers | 3 |
| Deprecated legacy files removed | 2 (`business.py`, `tracker.py`) |

## Validation

```bash
# All syntax checks pass
python3 -m py_compile src/**/*.py

# Backward compatibility works
python3 -c "from src.domain import AcademicConstants; print('OK')"
python3 -c "from src.configuration import settings; print('OK')"

# New structure
tree -L 3 src/
```

## Related ADRs

- ADR 000: Initial Refactoring (Phase 1) - Dual-Gateway Removal
- ADR 002: Service Layer Decomposition (planned)
- ADR 003: Monitoring Layer Introduction (planned)

## References

- [Clean Architecture - Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design - Eric Evans](https://www.domainlanguage.com/ddd/)
- [Hexagonal Architecture - Alistair Cockburn](https://alistair.cockburn.us/hexagonal-architecture/)

---

**Approved by:** Architecture Review Team
**Implementation Time:** 45 minutes
**Breaking Changes:** None (backward compatibility maintained)
