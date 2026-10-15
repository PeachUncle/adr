# ADR 001: PSR-4 Conversion Strategy

**Status:** Proposed
**Date:** 2026-01-12
**Deciders:** Development Team

## Context

The OPcache Toolkit plugin is currently structured with 22 procedural PHP files using WordPress hooks and global functions. We want to improve testability, maintainability, and performance while moving to PSR-4 autoloading.

### Current Pain Points

1. **Testing:** Cannot test code without WordPress loaded; cannot mock `opcache_*()` functions
2. **Maintainability:** Large files (e.g., `rest.php` at 466 lines) mix multiple concerns
3. **Performance:** No centralized caching strategy; duplicate queries (PHP + JavaScript)

### Plugin Scope

- ~43 functions
- ~26 hook registrations
- ~5-6 database queries
- REST API, WP-CLI, Admin UI, Cron jobs

## Decision

We will adopt a **hybrid approach**: convert code to classes **only where it provides measurable benefits** in testing, maintainability, or performance. Keep procedural code for simple tasks.

### Conversion Criteria

**Convert to classes IF:**
- Needs mocking for unit tests (e.g., wrapping `opcache_*()` functions)
- Contains complex logic worth testing in isolation (e.g., preload file iteration)
- Benefits from state/caching (e.g., database queries with transient caching)
- File is too large and benefits from splitting (e.g., REST endpoints)
- Reused from multiple entry points (commands called from REST/CLI/Admin)

**Keep procedural IF:**
- Simple hook registration (less than 10 lines)
- Template rendering
- Asset enqueuing (needs page context)
- One-off admin pages

### Classes to Create

1. **Services/OPcacheService.php** - Wraps `opcache_*()` functions for mocking
2. **Database/StatsRepository.php** - Centralizes queries and adds caching
3. **Commands/PreloadCommand.php** - Complex preload logic (80 lines)
4. **Commands/ResetCommand.php** - Reusable reset operation
5. **Commands/WarmupCommand.php** - Reusable warmup operation
6. **REST/StatusEndpoint.php** - Split from monolithic rest.php
7. **REST/PreloadEndpoint.php** - Split from monolithic rest.php
8. **REST/ChartDataEndpoint.php** - Split from monolithic rest.php
9. **CLI/Commands.php** - Already a class, just namespace it

### Files to Keep Procedural

- `admin/admin-dashboard.php` - Asset enqueues need page context
- `admin/admin-settings.php` - Simple form rendering
- `admin/dashboard-widget.php` - Simple widget registration
- `core/cron.php` - Simple cron hook registration
- `core/db.php` - Schema creation and simple helpers
- `templates/*.php` - Plain PHP templates

## Consequences

### Positive

- ✅ **Testability:** Can mock OPcache functions and database
- ✅ **Performance:** Centralized caching in repository reduces queries
- ✅ **Maintainability:** REST endpoints split into manageable files
- ✅ **Reusability:** Commands usable from REST/CLI/Admin
- ✅ **Familiarity:** Procedural code remains for WordPress-style hooks

### Negative

- ⚠️ **Two Styles:** Developers need to understand when to use classes vs procedural
- ⚠️ **Migration Effort:** Converting ~9 files to classes
- ⚠️ **Documentation:** Need clear guidelines on conversion criteria

### Neutral

- Total ~8 class files + ~8 procedural files
- No framework dependencies (pure PHP + WordPress)

## Alternatives Considered

### 1. Convert Everything to Classes

**Rejected because:**
- Creates unnecessary boilerplate for simple hooks
- Example: 5-line notice becomes 15-line class
- No testing benefit for simple template includes
- Loses WordPress familiarity

### 2. Keep Everything Procedural

**Rejected because:**
- Cannot mock `opcache_*()` functions for testing
- No clean way to add caching to repository
- 466-line REST file remains difficult to navigate
- Complex preload logic difficult to test

## Implementation Plan

1. Add composer.json with PSR-4 autoloading
2. Create class files in `includes/OPcacheToolkit/`
3. Update consumers to use new classes
4. Keep procedural files in existing locations
5. Add PHPUnit tests for class-based code
6. Document conversion criteria in CONTRIBUTING.md
