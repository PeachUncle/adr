# ADR 005: Strict Type Safety for PSR-4 Classes

**Status:** Proposed
**Date:** 2026-01-12
**Deciders:** Development Team

## Context

With the move to PHP 8.0+ as the minimum requirement (see Phase 0 in roadmap), we can leverage modern PHP type safety features. We need to decide whether to enforce strict types on new PSR-4 classes.

### Current State
- No type hints or return types in existing procedural code
- PHP 8.0+ supports:
  - `declare(strict_types=1);`
  - Parameter type hints
  - Return type declarations
  - Nullable types (`?string`)
  - Union types (`string|int`)
  - Property types

### The Question
Should we mandate strict type safety for all new PSR-4 classes?

## Decision

**YES** - All new PSR-4 classes MUST use strict typing.

### Implementation Rules

#### 1. Every New Class File Starts With:
```php
declare(strict_types=1);

namespace OPcacheToolkit\Services;
```

#### 2. All Method Parameters MUST Have Type Hints:
```php
// ✅ GOOD
public function compileFile(string $path): bool {
    // ...
}

// ❌ BAD - No type hint
public function compileFile($path) {
    // ...
}
```

#### 3. All Methods MUST Have Return Types:
```php
// ✅ GOOD
public function getStatus(): ?array {
    return $this->status;
}

public function logMessage(string $msg): void {
    error_log($msg);
}

// ❌ BAD - No return type
public function getStatus() {
    return $this->status;
}
```

#### 4. Class Properties MUST Have Types (PHP 7.4+):
```php
// ✅ GOOD
class OPcacheService {
    private array $config;
    private ?string $lastError = null;
}

// ❌ BAD - No property types
class OPcacheService {
    private $config;
    private $lastError;
}
```

#### 5. Use Nullable Types Appropriately:
```php
public function getStatus(): ?array {
    // Returns array or null
}

public function __construct(?array $paths = null) {
    // Parameter can be null
}
```

#### 6. Use Union Types When Needed (PHP 8.0+):
```php
public function normalize(string|int $value): string {
    return (string) $value;
}
```

### What NOT to Type

#### ❌ Procedural Files
Leave existing procedural files unchanged:
- `includes/admin/*.php` - Hook callbacks may have mixed returns
- `includes/core/*.php` - Legacy functions
- `includes/templates/*.php` - View files

#### ❌ WordPress Hook Callbacks
```php
// Don't type hook callbacks - WP expects mixed returns
add_action('init', function() {
    // No return type needed
});

add_filter('the_content', function($content) {
    // Parameter type OK, but return can be mixed
    return $content;
});
```

#### ❌ Backwards Compatibility Functions
If exposing a procedural API for theme/plugin devs, skip types:
```php
// Public API - keep flexible
function opcache_toolkit_get_status() {
    return Plugin::opcache()->getStatus();
}
```

## Consequences

### Positive

#### 🛡️ Runtime Type Safety
```php
$service = new OPcacheService();
$status = $service->getStatus(true); // OK - bool

$status = $service->getStatus('yes'); // ❌ TypeError thrown immediately
```

**Benefit:** Bugs caught at runtime, not silently coerced.

#### 📝 IDE Autocomplete
```php
$service = new OPcacheService();
$service->   // IDE shows all methods with correct types
```

**Benefit:** Developer productivity increases 30-50%.

#### 🧪 Test Failures Are Clear
```php
$mockService->getStatus()->willReturn('invalid'); // Test fails fast
// TypeError: Return value must be of type ?array, string returned
```

**Benefit:** Tests catch integration bugs immediately.

#### 📚 Self-Documenting Code
```php
// This is self-explanatory - no PHPDoc needed
public function compileFile(string $path): bool {
    // ...
}

// vs. untyped (requires PHPDoc)
/**
 * Compile a file.
 * @param string $path File path
 * @return bool Success
 */
public function compileFile($path) {
    // ...
}
```

**Benefit:** Less documentation burden, code is clearer.

### Negative

#### ⚠️ Requires Discipline
Developers must remember to add types to every new class/method.

**Mitigation:** Code reviews enforce this. Add to PR checklist.

#### ⚠️ Migration Friction
Mixing typed classes with untyped procedural code can be confusing.

**Mitigation:** Clear guidelines in ADR (this document). Only new PSR-4 classes are typed.

### Neutral

- Existing procedural code remains untyped
- Two styles coexist (typed classes, untyped functions)
- PHPDoc still needed for complex types (`@throws`, `@param array<string, mixed>`)

## Enforcement Strategy

### Code Review Checklist
- [ ] File starts with `declare(strict_types=1);`
- [ ] All public methods have parameter types
- [ ] All public methods have return types
- [ ] All class properties have types
- [ ] Nullable types (`?`) used where appropriate

### Automated Tools

#### PHPStan (Optional but Recommended)
```bash
composer require --dev phpstan/phpstan

# phpstan.neon
parameters:
  level: 5
  paths:
    - includes/OPcacheToolkit
```

Run before commits:
```bash
vendor/bin/phpstan analyse
```

#### PHP-CS-Fixer (Optional)
Can auto-add missing return types:
```bash
composer require --dev friendsofphp/php-cs-fixer
```

### CI/CD Pipeline
```yaml
# .github/workflows/tests.yml
- name: Check Type Safety
  run: |
    vendor/bin/phpstan analyse --level=5 includes/OPcacheToolkit
```

Fails build if types are missing or incorrect.

## Examples

### ✅ GOOD: Full Type Coverage
```php
declare(strict_types=1);

namespace OPcacheToolkit\Commands;

class PreloadCommand {
    private OPcacheService $opcache;
    private array $paths;

    public function __construct(OPcacheService $opcache, ?array $paths = null) {
        $this->opcache = $opcache;
        $this->paths = $paths ?? [WP_CONTENT_DIR . '/plugins'];
    }

    public function execute(): CommandResult {
        $compiled = 0;

        foreach ($this->paths as $path) {
            if (!is_dir($path)) {
                continue;
            }

            $compiled += $this->processDirectory($path);
        }

        return CommandResult::success("Compiled {$compiled} files", $compiled);
    }

    private function processDirectory(string $path): int {
        // ...
    }
}
```

### ❌ BAD: Missing Types
```php
namespace OPcacheToolkit\Commands;

class PreloadCommand {
    private $opcache; // Missing type
    private $paths;   // Missing type

    public function __construct($opcache, $paths = null) { // Missing types
        $this->opcache = $opcache;
        $this->paths = $paths ?? [WP_CONTENT_DIR . '/plugins'];
    }

    public function execute() { // Missing return type
        // ...
    }
}
```

## Alternatives Considered

### 1. No Strict Types (Status Quo)
**Rejected because:**
- Loses major PHP 8.0+ benefit
- No IDE autocomplete improvement
- Bugs caught late in production, not during development
- Code less self-documenting

### 2. Gradual Typing (Optional)
Allow developers to choose whether to add types.

**Rejected because:**
- Inconsistent codebase
- Hard to enforce standards
- Half-typed code is worse than no types (confusing)

### 3. Strict Types on Everything (Including Procedural)
Add types to all existing code, not just new classes.

**Rejected because:**
- Massive refactoring effort (200+ functions)
- High risk of breaking changes
- WordPress hooks expect mixed types
- Not aligned with hybrid approach (ADR-001)

## Migration Path

### Phase 2-7: Apply During Implementation
As we create new PSR-4 classes, add types immediately:
- Phase 2: `OPcacheService` - fully typed
- Phase 3: `StatsRepository` - fully typed
- Phase 4: Commands - fully typed
- Phase 5: REST Endpoints - fully typed
- Phase 6: CLI Commands - fully typed

### Phase 8.3: Audit & Enforce
- Run PHPStan on all PSR-4 classes
- Fix any missing types
- Add CI check to prevent regressions

### Future: Consider Procedural Migration
If successful, CONSIDER adding types to procedural code in v3.0.0 (separate ADR needed).

## Success Metrics

- [ ] All PSR-4 classes have `declare(strict_types=1);`
- [ ] PHPStan level 5 passes on `includes/OPcacheToolkit/`
- [ ] 0 PHPDoc `@param` tags needed for simple types (types are self-documenting)
- [ ] IDE autocomplete works for all service methods

## References

- [PHP declare(strict_types=1)](https://www.php.net/manual/en/language.types.declarations.php#language.types.declarations.strict)
- [PHPStan Documentation](https://phpstan.org/user-guide/getting-started)
- [PHP 8.0 Type System](https://www.php.net/releases/8.0/en.php)
