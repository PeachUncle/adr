# 001: Modular Package Architecture

## Status

Accepted

## Date

2025-12-15

## Context

The initial implementation was a monolithic single-file script (`book_recommender.py`) containing all functionality: UI, recommendation logic, API calls, configuration, and styling. As the project grew to include features like caching, Google Books integration, session history, and export functionality, the single file became difficult to maintain, test, and extend.

Key issues:
- Difficulty in testing individual components
- Poor separation of concerns
- Code reusability challenges
- Hard to navigate and understand
- Violated professional Python project standards

Alternatives considered:
1. Keep monolithic structure with better comments/organization
2. Split into a few large modules (ui, logic, config)
3. **Full modular architecture with `src/` layout** ✓

## Decision

Adopt a modular package architecture under `src/book_recommender/` with clear separation of concerns:

```
src/book_recommender/
├── __init__.py          # Package exports
├── analytics.py         # Usage analytics tracking
├── app.py              # Application bootstrap
├── config.py           # Configuration and CSS constants
├── google_books.py     # Google Books API integration
├── logger.py           # Structured logging
├── recommender.py      # Core recommendation logic
└── ui.py               # Gradio UI assembly
```

Each module has a single, well-defined responsibility:
- **config.py**: Environment vars, constants, styling
- **google_books.py**: External API integration
- **recommender.py**: LLM chain, caching, guardrails
- **ui.py**: Gradio interface assembly
- **app.py**: Entry point, wiring components
- **logger.py**: Structured logging with context
- **analytics.py**: Usage tracking and metrics

## Consequences

### Positive
- **Testability**: Each module can be tested in isolation with mocks
- **Maintainability**: Clear boundaries make changes localized
- **Readability**: Easier to understand individual components
- **Reusability**: Components can be imported and reused
- **Standards**: Follows Python package best practices
- **CI/CD**: Easier to configure linting, testing, coverage
- **Collaboration**: Multiple developers can work on different modules

### Negative
- **Initial overhead**: More files to navigate initially
- **Import complexity**: Need to manage internal imports correctly
- **Migration effort**: Required refactoring existing code

### Neutral
- Module boundaries require discipline to maintain
- Need clear documentation of module responsibilities

### Risks
- Import cycles if dependencies not managed carefully
- Over-modularization could fragment simple logic

## Implementation Notes

Key changes:
1. Created `src/book_recommender/` package structure
2. Split monolithic file into 7 focused modules
3. Updated `book_recommender.py` as thin entry point that adds `src/` to path
4. Added `__init__.py` with clear exports
5. Updated tests to import from new module structure
6. Configured `pyproject.toml` for package metadata

Migration was smooth because:
- Used sys.path manipulation to avoid import conflicts
- Kept original file as entry point for backward compatibility
- All tests updated to use new imports

## References

- [Python Packaging User Guide](https://packaging.python.org/)
- [src layout discussion](https://blog.ionelmc.ro/2014/05/25/python-packaging/)
- [Clean Architecture principles](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
