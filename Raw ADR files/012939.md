# ADR-006: Observability Strategy

**Status:** Accepted
**Date:** 2026-01-12
**Deciders:** Development Team

---

## Context

The plugin currently lacks structured logging, diagnostics tools, and troubleshooting capabilities. When issues occur in production:

1. **No visibility** into what the plugin is doing (operations succeed/fail silently)
2. **No diagnostic tools** to verify plugin health or configuration
3. **No structured logs** - just scattered `error_log()` calls with inconsistent formatting
4. **Support burden** - users can't self-diagnose, must describe issues manually

This makes debugging production issues extremely difficult and increases support overhead.

---

## Decision

Implement a three-tier observability strategy:

### 1. Structured Logging
Create a `Logger` service with consistent, JSON-formatted log entries.

**Rationale:**
- JSON logs are parseable by log aggregation tools (Datadog, Splunk, etc.)
- Structured format enables filtering, searching, and alerting
- Consistent timestamps and context make debugging easier
- Minimal performance overhead (only logs when enabled)

### 2. Debug Mode Toggle
Add a setting to enable verbose logging independent of `WP_DEBUG`.

**Rationale:**
- `WP_DEBUG` is global and affects all plugins/themes
- Users may want verbose OPcache Toolkit logs without enabling global debug mode
- Production-safe debugging (doesn't expose PHP errors to visitors)
- Can be enabled temporarily to troubleshoot specific issues

**Note:** This decision is tentative and may be adjusted based on real-world usage.

### 3. System Diagnostics
Provide self-service diagnostic tools:
- **WP-CLI `doctor` command** - Automated health checks
- **System Report page** - Environment, config, and plugin details in copyable format

**Rationale:**
- Users can verify plugin is configured correctly
- Reduces support requests for common issues (missing OPcache extension, wrong PHP version, etc.)
- System report provides all context needed for support tickets
- WP-CLI command enables CI/CD health checks

---

## Implementation

**Note:** The implementation uses a proven logger pattern distilled from 5 production WordPress plugins (EA Messaging, EA Events Calendar, EA Student Parent Access, EA Transfer). This pattern provides file-based logging with rotation, cleanup, and comprehensive features.

**See:**
- **`docs/LOGGER-BLUEPRINT.md`** - Reusable logger template with full documentation
- **`docs/LOGGER-OPCACHE-TOOLKIT.md`** - OPcache Toolkit-specific implementation

### Why File-Based Logging Over error_log()

The logger uses file-based logging instead of PHP's `error_log()` for several reasons:

1. **Isolation:** Plugin logs separate from general PHP error log (easier to debug)
2. **Management:** Automatic rotation at 5MB and cleanup after 30 days
3. **Context:** Rich metadata (memory usage, user ID, timestamps, stack traces)
4. **Separation:** Separate `plugin.log` and `js.log` for clarity
5. **Security:** Logs protected via `.htaccess` and `index.php`

### Key Features

The logger implementation includes:

1. **File-Based Logging**
   - Separate `plugin.log` and `js.log` files
   - Stored in `wp-content/uploads/opcache-toolkit-logs/`
   - Automatic rotation at 5MB
   - 30-day automatic cleanup via cron

2. **Rich Context**
   - Timestamp, log level, message
   - User ID tracking
   - Memory usage (PHP logs only)
   - Stack traces on errors (when debug enabled)
   - Pretty-printed JSON context

3. **Security**
   - `.htaccess` denies direct access
   - `index.php` prevents directory listing
   - All input sanitized before logging

4. **JavaScript Integration**
   - Batched logging (10 logs or 5s interval)
   - Data sanitization (circular refs, truncation)
   - Global error handlers (error + unhandledrejection)
   - REST API transport

5. **Debug Mode**
   - Respects `WP_DEBUG` OR `opcache_toolkit_debug_mode` setting
   - DEBUG level logs only when debug enabled
   - Independent control from global WordPress debug

### Usage Examples

```php
// In PreloadCommand::execute()
Plugin::logger()->info('Preload started', [
    'paths' => $this->paths,
    'async' => $this->async,
]);

// ... preload logic ...

Plugin::logger()->info('Preload completed', [
    'compiled' => $compiled,
    'failed' => $failed,
    'duration_ms' => $duration,
]);

// In REST endpoint error handling
catch (\Exception $e) {
    Plugin::logger()->error('REST endpoint failed', [
        'endpoint' => '/chart-data',
        'error' => $e->getMessage(),
        'trace' => $e->getTraceAsString(),
    ]);

    return $this->error_response('internal_error', 'Operation failed', 500);
}

// In StatsRepository for slow queries
if ($duration > 100) {
    Plugin::logger()->warning('Slow query detected', [
        'method' => 'getChartData',
        'duration_ms' => $duration,
    ]);
}
```

### JavaScript Usage

```javascript
const logger = window.opcacheToolkitLogger;

// Dashboard operations
logger.info('Dashboard loaded', { loadTime: Date.now() - startTime });

// Error handling
catch (err) {
    logger.error('Failed to fetch status', {
        error: err.message,
        endpoint: '/status',
    });
}

// Warnings
logger.warn('Circuit breaker opened', {
    failures: this.failureCount,
});
```

### Debug Mode Toggle

```php
// In admin-settings.php
add_settings_field(
    'opcache_toolkit_debug_mode',
    __('Debug Mode', 'opcache-toolkit'),
    function() {
        $enabled = get_option('opcache_toolkit_debug_mode', false);
        ?>
        <label>
            <input type="checkbox"
                   name="opcache_toolkit_debug_mode"
                   value="1"
                   <?php checked($enabled); ?>>
            <?php _e('Enable verbose logging', 'opcache-toolkit'); ?>
        </label>
        <p class="description">
            <?php _e('Log detailed information about plugin operations. Independent of WP_DEBUG. Logs are written to your PHP error log.', 'opcache-toolkit'); ?>
        </p>
        <?php
    },
    'opcache-toolkit',
    'opcache_toolkit_advanced'
);

register_setting('opcache-toolkit', 'opcache_toolkit_debug_mode', [
    'type' => 'boolean',
    'default' => false,
    'sanitize_callback' => 'rest_sanitize_boolean',
]);
```

### WP-CLI Doctor Command

```php
/**
 * Run system diagnostics.
 *
 * ## EXAMPLES
 *
 *     wp opcache-toolkit doctor
 */
public function doctor($args, $assoc_args) {
    WP_CLI::line('Running diagnostics...');

    $checks = [
        'PHP Version' => PHP_VERSION,
        'WP Version' => get_bloginfo('version'),
        'Plugin Version' => OPCACHE_TOOLKIT_VERSION,
        'OPcache Enabled' => extension_loaded('Zend OPcache') ? '✓ Yes' : '✗ No',
        'OPcache Memory' => ini_get('opcache.memory_consumption') . 'MB',
        'Hit Rate' => number_format($this->opcache->getHitRate(), 2) . '%',
        'Cached Scripts' => $this->opcache->getStatus()['opcache_statistics']['num_cached_scripts'] ?? 0,
        'DB Schema' => $this->checkSchema() ? '✓ OK' : '✗ Missing',
        'Cron Jobs' => wp_next_scheduled('opcache_toolkit_daily_log') ? '✓ Scheduled' : '✗ Missing',
        'Debug Mode' => get_option('opcache_toolkit_debug_mode') ? 'Enabled' : 'Disabled',
    ];

    $table_data = [];
    foreach ($checks as $check => $result) {
        $table_data[] = ['check' => $check, 'result' => $result];
    }

    WP_CLI\Utils\format_items('table', $table_data, ['check', 'result']);
    WP_CLI::success('Diagnostics complete');
}
```

### System Report Page

```php
function opcache_toolkit_render_system_report() {
    ?>
    <div class="wrap">
        <h1><?php _e('System Report', 'opcache-toolkit'); ?></h1>
        <p><?php _e('Copy and paste this report when requesting support.', 'opcache-toolkit'); ?></p>
        <textarea readonly style="width:100%;height:400px;font-family:monospace;"><?php
            echo esc_textarea(opcache_toolkit_generate_system_report());
        ?></textarea>
        <button class="button button-primary" onclick="navigator.clipboard.writeText(this.previousElementSibling.value).then(() => alert('Copied!'))">
            <?php _e('Copy to Clipboard', 'opcache-toolkit'); ?>
        </button>
    </div>
    <?php
}

function opcache_toolkit_generate_system_report(): string {
    $report = [];

    $report[] = '### OPcache Toolkit System Report';
    $report[] = 'Generated: ' . current_time('mysql');
    $report[] = '';

    $report[] = '### Environment';
    $report[] = 'PHP Version: ' . PHP_VERSION;
    $report[] = 'WordPress Version: ' . get_bloginfo('version');
    $report[] = 'Plugin Version: ' . OPCACHE_TOOLKIT_VERSION;
    $report[] = 'Multisite: ' . (is_multisite() ? 'Yes' : 'No');
    $report[] = 'WP_DEBUG: ' . (defined('WP_DEBUG') && WP_DEBUG ? 'Enabled' : 'Disabled');
    $report[] = 'Debug Mode: ' . (get_option('opcache_toolkit_debug_mode') ? 'Enabled' : 'Disabled');
    $report[] = '';

    $report[] = '### OPcache Status';
    $status = opcache_get_status();
    $report[] = 'Enabled: ' . ($status !== false ? 'Yes' : 'No');
    if ($status) {
        $report[] = 'Hit Rate: ' . number_format($status['opcache_statistics']['opcache_hit_rate'], 2) . '%';
        $report[] = 'Cached Scripts: ' . $status['opcache_statistics']['num_cached_scripts'];
        $report[] = 'Memory Used: ' . size_format($status['memory_usage']['used_memory']);
        $report[] = 'Wasted Memory: ' . size_format($status['memory_usage']['wasted_memory']);
    }
    $report[] = '';

    $report[] = '### OPcache Configuration';
    $config = ini_get_all('opcache');
    foreach ($config as $key => $value) {
        $report[] = sprintf('%s: %s', $key, $value['local_value']);
    }
    $report[] = '';

    $report[] = '### Active Plugins';
    $plugins = get_option('active_plugins');
    foreach ($plugins as $plugin) {
        $plugin_data = get_plugin_data(WP_PLUGIN_DIR . '/' . $plugin);
        $report[] = sprintf('- %s (v%s)', $plugin_data['Name'], $plugin_data['Version']);
    }

    return implode("\n", $report);
}
```

---

## Consequences

### Positive

✅ **Easier Debugging**
- Structured logs enable filtering by level, operation, or error
- Context arrays capture all relevant state at time of error
- Timestamps enable correlation across log entries

✅ **Reduced Support Burden**
- Users can run `wp opcache-toolkit doctor` to self-diagnose
- System report provides all necessary info for support tickets
- Common issues (missing extension, wrong PHP version) caught immediately

✅ **Production-Safe**
- Logging disabled by default (zero overhead)
- Debug mode doesn't expose errors to visitors (unlike `WP_DEBUG`)
- No PII or sensitive data in logs

✅ **CI/CD Integration**
- `wp opcache-toolkit doctor` can be run in CI pipelines
- Automated health checks after deployment
- Exit codes enable alerting on failures

✅ **Log Aggregation Friendly**
- JSON format parseable by Datadog, Splunk, ELK stack, etc.
- Structured fields enable filtering and alerting
- No need to parse unstructured strings

### Negative

⚠️ **Additional Complexity**
- One more service to maintain (`Logger`)
- One more setting to document (debug mode)
- Developers must remember to add logging to new features

⚠️ **Debug Mode Confusion** (Tentative)
- Having both `WP_DEBUG` and `opcache_toolkit_debug_mode` may confuse users
- Users may not understand when to use which
- May need to adjust or remove if proves confusing in practice

⚠️ **Log Volume**
- Verbose logging with high traffic could generate large log files
- May need log rotation or volume limits in future
- Currently mitigated by: logs only when explicitly enabled

⚠️ **System Report Exposure**
- Report contains plugin list and configuration
- Users might share publicly without realizing
- Mitigated by: clear warning "Copy and paste this report when requesting support"

---

## Alternatives Considered

### 1. Use PHP error_log() Directly
**Rejected:**
- OPcache logs would be mixed with all other PHP errors/warnings
- No way to view OPcache-specific logs without grepping entire error log
- No built-in rotation (PHP error log can grow huge)
- No automatic cleanup (logs persist forever)
- Less context (no memory usage, user tracking, etc.)

**Decision:** File-based logging with rotation and cleanup is superior for plugin-specific logs

### 2. Use WordPress Debug Log Directly
**Rejected:** Similar issues to error_log() - unstructured format, no context arrays, mixed with all other WordPress logs

### 3. Third-Party Logging Library (Monolog, Analog)
**Rejected:** Adds dependency, overkill for our needs, increases plugin size

### 4. Always-On Logging
**Rejected:** Performance overhead, log volume concerns, unnecessary for most users

### 5. Debug Mode via Constant (WP_DEBUG_OPCACHE_TOOLKIT)
**Considered:** Would avoid UI complexity, but harder for non-technical users to enable

### 6. Email-Based Diagnostics
**Rejected:** Requires email configuration, privacy concerns, less immediate than WP-CLI/admin page

---

## Open Questions

1. **Debug Mode Necessity:** Is the debug mode toggle actually needed, or is `WP_DEBUG` sufficient?
   - **Decision:** Implement as planned, gather feedback, remove if unused
   - **Rationale:** Low implementation cost, easy to remove if proves unnecessary

2. **Log Retention:** Should we implement automatic log rotation or size limits?
   - **Decision:** YES - Implemented in blueprint with 5MB rotation and 30-day cleanup
   - **Rationale:** Prevents unbounded log growth, proven pattern from existing plugins

3. **Privacy:** Should we sanitize paths or URLs in logs?
   - **Decision:** No - logs are server-side only, sanitization would reduce debugging value
   - **Note:** Never log user input verbatim (always sanitize first)

---

## Success Metrics

### Adoption
- **Target:** 30% of users run `wp opcache-toolkit doctor` within 30 days of install
- **Target:** 50% of support requests include system report

### Support Impact
- **Target:** 25% reduction in "How do I troubleshoot X?" support requests
- **Target:** 50% reduction in "What's my configuration?" support requests

### Debug Mode Usage
- **Metric:** Track how many users enable debug mode (via telemetry or support requests)
- **Decision Point:** If < 5% of users enable it after 6 months, consider removing

---

## Related Decisions

- **ADR-001:** PSR-4 Conversion Strategy - `Logger` is a PSR-4 class
- **ADR-002:** Service Instantiation - `Logger` accessible via `Plugin::logger()`
- **ADR-005:** Strict Type Safety - `Logger` uses `declare(strict_types=1);`

---

## References

- [PSR-3 Logger Interface](https://www.php-fig.org/psr/psr-3/) - Inspiration for log levels
- [WordPress Debug Log](https://developer.wordpress.org/advanced-administration/debug/debug-wordpress/) - Why we need better
- [Structured Logging Best Practices](https://www.loggly.com/ultimate-guide/structured-logging/) - JSON format rationale

---

## Changelog

- **2026-01-12:** Initial decision - Observability strategy accepted
- **2026-01-12:** Updated implementation to reference logger blueprint distilled from 5 production plugins (EA Messaging, EA Events Calendar, EA Student Parent Access, EA Transfer). Changed from error_log() approach to file-based logging with rotation and cleanup for better isolation, management, and context.
