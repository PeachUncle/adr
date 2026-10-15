# ADR 003: Hook Registration Pattern

**Status:** Proposed
**Date:** 2026-01-12
**Deciders:** Development Team

## Context

WordPress plugins interact with the core and other plugins via hooks (`add_action`, `add_filter`). The plugin has ~26 hook registrations scattered across files. We need to decide whether to centralize hook registration in classes or keep them contextual.

### Current State

Hooks are registered inline where they're used:

```php
// includes/admin/admin-dashboard.php
add_action('admin_enqueue_scripts', function ($hook) {
    if ($hook !== 'toplevel_page_opcache-toolkit') {
        return;
    }
    wp_enqueue_script('chartjs', ...);
});

// includes/core/opcache-reset.php
add_action('upgrader_process_complete', function ($upgrader, $hook_extra) {
    if (!in_array($hook_extra['type'], ['plugin', 'theme'])) {
        return;
    }
    opcache_reset();
}, 10, 2);
```

### Hook Subscriber Pattern

Common in modern WordPress development:

```php
class AdminHooks {
    public function register(): void {
        add_action('admin_enqueue_scripts', [$this, 'enqueue_assets']);
        add_action('admin_menu', [$this, 'register_menu']);
    }

    public function enqueue_assets($hook): void {
        if ($hook !== 'toplevel_page_opcache-toolkit') return;
        // Asset logic here
    }
}
```

## Decision

We will **NOT centralize hooks in subscriber classes**. Hooks will remain **inline, near their context**, with one exception.

### Keep Hooks Contextual

**Asset enqueues stay in page files:**
```php
// includes/admin/admin-dashboard.php
add_action('admin_enqueue_scripts', function ($hook) {
    if ($hook !== 'toplevel_page_opcache-toolkit') return;
    // Enqueue scripts for THIS page
});
```

**Form submissions stay in settings files:**
```php
// includes/admin/admin-settings.php
add_action('admin_post_opcache_toolkit_save', function() {
    check_admin_referer('opcache_toolkit_settings');
    update_option('opcache_toolkit_alert_threshold', $_POST['threshold']);
});
```

**Cron jobs stay in cron file:**
```php
// includes/core/cron.php
add_action('opcache_toolkit_daily_log', function() {
    $status = opcache_get_status();
    opcache_toolkit_insert_stats_row(...);
});
```

### Exception: Global Plugin Hooks

Only truly **plugin-wide, cross-cutting** hooks get centralized:

```php
// OPcacheToolkit/Plugin.php
public static function boot(): void {
    // Plugin lifecycle
    add_action('plugins_loaded', [self::class, 'load_textdomain']);

    // REST API (registers multiple endpoints)
    add_action('rest_api_init', [self::class, 'register_rest_routes']);

    // Global auto-reset feature
    add_action('upgrader_process_complete', [self::class, 'maybe_auto_reset'], 10, 2);
}
```

## Consequences

### Positive

- ✅ **Context Clarity:** Hooks are near the code they trigger
- ✅ **Screen ID Checks:** Screen conditionals (e.g., `if ($hook === 'toplevel_page_opcache-toolkit')`) are next to menu registration
- ✅ **Easy Navigation:** Don't need to jump between files to understand page behavior
- ✅ **WordPress Familiar:** Matches typical WordPress plugin patterns
- ✅ **Less Boilerplate:** No need for class methods wrapping simple callbacks

### Negative

- ⚠️ **No Central Hook Registry:** Can't see all hooks in one place (but can search for `add_action`)
- ⚠️ **File Loading Order:** Procedural files must be loaded in correct order (non-issue with our structure)

### Neutral

- Hook subscriber pattern available for future features if needed
- Can still use classes as callbacks: `add_action('hook', [$object, 'method'])`

## Rationale

### Problem with Centralized Hooks

**Example: Dashboard assets**

**Centralized (Bad):**
```php
// OPcacheToolkit/Hooks/AdminHooks.php
class AdminHooks {
    public function register(): void {
        add_action('admin_menu', [$this, 'register_menu']);
        add_action('admin_enqueue_scripts', [$this, 'enqueue_assets']);
    }

    public function register_menu(): void {
        add_menu_page(
            'OPcache Dashboard',
            'OPcache',
            'manage_options',
            'opcache-toolkit',  // ← Screen ID defined here
            [$this, 'render']
        );
    }

    public function enqueue_assets($hook): void {
        // Problem: Screen ID check is far from where 'opcache-toolkit' is defined
        if ($hook !== 'toplevel_page_opcache-toolkit') return;

        wp_enqueue_script(...);
    }
}
```

The screen ID (`'toplevel_page_opcache-toolkit'`) is defined in `register_menu()` but checked in `enqueue_assets()`. This disconnects related logic.

**Contextual (Good):**
```php
// includes/admin/admin-dashboard.php

// Menu registration
add_action('admin_menu', function() {
    add_menu_page(
        'OPcache Dashboard',
        'OPcache',
        'manage_options',
        'opcache-toolkit',  // ← Screen ID defined
        'opcache_toolkit_render_dashboard'
    );
});

// Asset enqueuing - screen ID check is RIGHT HERE
add_action('admin_enqueue_scripts', function($hook) {
    if ($hook !== 'toplevel_page_opcache-toolkit') return; // ← ID checked nearby

    wp_enqueue_script(...);
});
```

Both the screen ID definition and its usage are in the same file, making it obvious when to load assets.

### When Centralization Helps

**Global hooks that don't depend on page context:**

```php
// Plugin.php - These make sense centralized
add_action('plugins_loaded', ...);           // Always runs
add_action('rest_api_init', ...);            // Registers all endpoints
add_action('upgrader_process_complete', ...); // Plugin-wide behavior
```

These hooks:
- Have no screen-specific conditionals
- Affect the entire plugin
- Don't require understanding page context

## Alternatives Considered

### 1. Full Hook Subscriber Pattern

Every feature gets a `register()` method:

```php
(new AdminHooks())->register();
(new CronHooks())->register();
(new RestHooks())->register();
```

**Rejected because:**
- Adds boilerplate for simple hooks
- Disconnects hooks from their context
- No testing benefit (hooks still interact with WordPress)
- No performance benefit (same hook registration)

### 2. Hook Subscriber Only for Classes

Use subscriber pattern for class-based features, inline for procedural:

```php
// Class-based
class StatusEndpoint {
    public function register(): void {
        register_rest_route(...);
    }
}

// Procedural stays inline
add_action('admin_enqueue_scripts', function($hook) { ... });
```

**Rejected because:** This is exactly what we're doing! REST endpoints ARE classes with `register()` methods. We're not calling it a "hook subscriber pattern" but functionally it's the same.

## Implementation Guidelines

### Use Inline Hooks When:

1. Hook is specific to a page/screen
2. Hook logic is < 10 lines
3. Hook has conditional checks based on context (screen ID, post type, etc.)
4. Hook is one-off (not reused)

### Use Class Methods When:

1. Hook registers a complex feature (REST endpoints, WP-CLI)
2. Hook logic is complex and benefits from private helper methods
3. Logic needs to be tested in isolation
4. Logic is reused from multiple hooks

### Example Patterns

**✅ Good: Inline**
```php
// Simple, contextual
add_action('admin_notices', function() {
    if (isset($_GET['opcache_reset'])) {
        echo '<div class="notice notice-success">OPcache reset successfully</div>';
    }
});
```

**✅ Good: Class Method**
```php
// Complex, testable
class PreloadCommand {
    public function execute(): int {
        // 80 lines of complex logic
    }
}

add_action('opcache_toolkit_preload_async', function() {
    $command = new PreloadCommand(Plugin::opcache());
    $command->execute();
});
```

## References

- [WordPress Plugin Handbook - Hooks](https://developer.wordpress.org/plugins/hooks/)
- [Modern WordPress Development Patterns](https://torquemag.io/2019/01/wordpress-design-patterns/)
