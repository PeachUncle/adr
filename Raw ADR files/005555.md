---
title: Architectural Decision Record 1 – AI Watch Extension Project Basics
date: 2025-08-16
status: Accepted
---

# Architectural Decision Record 1: AI Watch VS Code Extension Project Basics

## Status
Accepted

## Context

AI Watch is a VS Code extension providing advanced date and time tools for AI assistants and developers. The extension is designed for maintainability, extensibility, and seamless integration with both VS Code commands and Language Model Tools (LM Tools). The project targets AI-assisted development workflows, global team coordination, and business day calculations, with a focus on type safety, modularity, and robust error handling.

## Decision

### 1. **Modular, Feature-First Architecture**
- The codebase is organized by feature modules under `src/modules/<feature>/`, each with its own `command/`, `lm-tool/`, and `model/` subfolders.
- Shared utilities, error types, and models are centralized in `src/modules/shared/`.
- A thin entry point (`src/extension.ts`) delegates all activation logic to a registration layer (`src/registration/`).
- Each feature exposes both a VS Code command and a Language Model Tool, following the "dual interface" pattern.

### 2. **Dual Interface Pattern**
- Every feature is accessible as both a VS Code command (for programmatic use) and a Language Model Tool (for AI assistant integration).
- Commands are registered in `src/registration/commands.ts` and tools in `src/registration/tools.ts`.
- This enables both direct API access and natural language-driven workflows.

### 3. **Strict TypeScript and Type Safety**
- All code is written in strict TypeScript, with no `any` types, explicit return types, and union types for key parameters (e.g., verbosity levels, duration units).
- Type safety is enforced at compile time for all options and results, reducing runtime errors and improving maintainability.

### 4. **Comprehensive Error Handling**
- All command functions validate input and throw specific error types (e.g., `InvalidDateError`, `InvalidTimezoneError`, `MissingDaysError`, `InvalidWeekDayError`).
- LM Tools catch and transform errors into structured, user-friendly responses.
- Error types are documented and tested, ensuring predictable behavior for both users and AI agents.

### 5. **Configuration via VS Code Settings**
- Extension settings are namespaced under `aiWatch.*` and support both user and workspace scopes.
- Settings include business days, excluded dates, week start, default date format, duration format, and max duration units.
- Per-call parameters always override configuration, ensuring flexibility for both users and AI agents.

### 6. **Testing and Quality Assurance**
- The test suite is organized by layer: `src/test/commands/`, `src/test/tools/`, and `src/test/utils/`.
- Tests are document-driven, validating API documentation as the primary goal, but also cover edge cases and implementation details for reliability.
- All date tests use UTC to avoid timezone issues.
- Pre-commit hooks (Husky + lint-staged) enforce code quality, formatting, and branch naming conventions.

### 7. **Performance and Extensibility**
- Feature modules are stateless and can be tree-shaken for efficient bundling.
- No global state or caching is used; all operations are stateless and memory-efficient.
- New features can be added by following the established module structure and registration workflow.

### 8. **External Dependencies**
- Uses `date-fns` and `date-fns-tz` for all date calculations and timezone handling.
- Only IANA timezone names are supported, with DST-aware conversions.
- No direct use of JavaScript's `Date` parsing for user input; always uses `parseISOString()` for safety.

## Consequences

- The extension is easy to maintain and extend, with clear boundaries between features and shared utilities.
- AI assistants and developers can rely on consistent, type-safe APIs and robust error handling.
- The architecture supports rapid addition of new time/date features without risk of breaking existing functionality.
- Comprehensive documentation and testing ensure reliability and ease of onboarding for new contributors.

## Alternatives Considered

- **Monolithic Design:** Rejected in favor of modularity for maintainability and testability.
- **Single Interface (Command-Only or Tool-Only):** Rejected to maximize both programmatic and AI-driven use cases.
- **Native Date Methods:** Rejected for parsing user input due to inconsistent behavior and lack of timezone safety.

## References

- [ARCHITECTURE.md](./ARCHITECTURE.md)
- [API_REFERENCE.md](./API_REFERENCE.md)
- [USER_GUIDE.md](./USER_GUIDE.md)
- [CONFIGURATION.md](./CONFIGURATION.md)
- [TESTING.md](./TESTING.md)
- [CHANGELOG.md](../CHANGELOG.md)
- [CONTRIBUTING.md](../CONTRIBUTING.md)

---
This ADR documents the foundational architectural decisions for the AI Watch extension as of August 2025. Future changes should be recorded in new ADRs and cross-referenced here.
