# ADR 002: Service Instantiation Strategy

**Status:** Proposed
**Date:** 2026-01-12
**Deciders:** Development Team

## Context

After deciding to convert portions of the codebase to PSR-4 classes (see ADR-001), we need to determine how to instantiate and share service instances throughout the plugin.

### Services to Manage

- **OPcacheService** - Wraps `opcache_*()` functions
- **StatsRepository** - Database access with caching
- Used from: REST endpoints, WP-CLI commands, cron jobs, admin handlers

### Requirements

1. **IDE Support:** Full autocomplete and type inference
2. **Testability:** Must be able to inject mocks
3. **Performance:** Minimal overhead
4. **Simplicity:** Low cognitive load for WordPress developers

## Decision

We will use **static accessor methods** on a `Plugin` class to provide shared service instances.

### Implementation

```php
namespace OPcacheToolkit;

class Plugin {
    private static ?Services\OPcacheService $opcache = null;
    private static ?Database\StatsRepository $stats = null;

    public static function opcache(): Services\OPcacheService {
        return self::$opcache ??= new Services\OPcacheService();
    }

    public static function stats(): Database\StatsRepository {
        global $wpdb;
        return self::$stats ??= new Database\StatsRepository($wpdb);
    }

    public static function boot(): void {
        // Initialize plugin
    }
}
```

### Usage Examples

**From REST endpoint:**
```php
use OPcacheToolkit\Plugin;

$endpoint = new StatusEndpoint(Plugin::opcache());
```

**From procedural cron file:**
```php
use OPcacheToolkit\Plugin;

add_action('opcache_toolkit_daily_log', function() {
    $opcache = Plugin::opcache();
    $stats = Plugin::stats();

    $status = $opcache->getStatus();
    // ...
});
```

**Testing with mocks:**
```php
// Can still inject mocks via constructor
$mockOpcache = new MockOPcacheService();
$command = new PreloadCommand($mockOpcache);
```

## Consequences

### Positive

- ✅ **Full IDE Support:** `Plugin::opcache()->getHitRate()` provides complete autocomplete
- ✅ **Type Safety:** Return types explicitly declared on each method
- ✅ **Shared Instances:** Services instantiated once, reused (minimal memory benefit)
- ✅ **Testable:** Can still pass mock objects via constructor injection
- ✅ **Simple:** No complex container, just 2-3 typed methods
- ✅ **WordPress-Familiar:** Similar to `WP_Query`, `wpdb` global patterns

### Negative

- ⚠️ **Static State:** Services stored as static properties (acceptable for singleton services)
- ⚠️ **Testing Globals:** Tests that rely on shared state need cleanup between runs

### Neutral

- Only ~3 services need this pattern (OPcache, Stats, possibly Alerts)
- One additional class file (`Plugin.php`)

## Alternatives Considered

### 1. Direct Instantiation Everywhere

```php
// In every file that needs it
$opcache = new OPcacheService();
$stats = new StatsRepository($wpdb);
```

**Pros:**
- Zero magic
- Perfect IDE support
- Explicit dependencies

**Cons:**
- Repeated instantiation code throughout codebase
- Multiple instances of stateless services (wasteful, though negligible)
- No centralized initialization point

**Rejected because:** Too much repetition; plugin-wide services deserve shared instances.

### 2. Dependency Injection Container

```php
class Container {
    private array $services = [];

    public function get(string $name): mixed {
        return $this->services[$name] ??= $this->make($name);
    }
}

// Usage
$opcache = $container->get('opcache'); // ❌ No type information
```

**Pros:**
- Flexible for many services
- Can configure bindings

**Cons:**
- ❌ **No IDE autocomplete** without additional wrapper methods
- String keys are fragile and error-prone
- Overkill for ~3 services
- Higher cognitive load (need to understand container lifecycle)

**Rejected because:** Complexity doesn't justify benefits for small service count.

### 3. Service Locator with Typed Methods

```php
class ServiceLocator {
    private static Container $container;

    public static function opcache(): OPcacheService {
        return self::$container->get(OPcacheService::class);
    }
}
```

**Rejected because:** This is functionally identical to our chosen solution, but with extra container abstraction layer providing no benefit.

## Implementation Notes

### Service Requirements

Services managed by `Plugin` class must be:
- **Stateless** or manage their own state internally
- **Singleton-appropriate** (shared instance makes sense)
- **Used from multiple locations** (REST, CLI, cron, admin)

### Not All Classes Need This

Classes that don't need shared instances:
- Commands (instantiated per-use)
- REST Endpoints (registered once)
- Value Objects (instantiated as needed)

### Testing Strategy

```php
// Production code
$endpoint = new StatusEndpoint(Plugin::opcache());

// Test code
$mockOpcache = $this->createMock(OPcacheService::class);
$endpoint = new StatusEndpoint($mockOpcache);
```

Constructor injection allows mock substitution without affecting static accessor.

## Future Considerations

If the plugin grows to 15+ shared services, we may need to revisit this decision and consider a proper DI container. At current scale (3-5 services), static accessors provide the best balance.

## References

- [WordPress Global Variables Pattern](https://developer.wordpress.org/reference/classes/wpdb/)
- [Singleton Pattern Considerations](https://www.php.net/manual/en/language.oop5.patterns.php)
