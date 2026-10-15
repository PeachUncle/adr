# ADR-014 – Sentinel Key Pattern: Hot-Reload Configuration Without Service Restart

**Status:** Accepted  
**Date:** 2025-11-27  
**Last Updated:** 2025-11-28  
**Author:** Niklas Häll

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-27 | Initial ADR - Sentinel key pattern implementation for hot-reload |
| 1.1 | 2025-11-28 | Added Admin Dashboard feature flag toggle UI, documented cold start behavior, added propagation polling UX |

---

## Context

The ticketing system implements a **permanent dual-system coexistence** architecture where both synchronous (chained API) and event-driven architectures run side-by-side. Feature flags in Azure App Configuration control which architecture path is active. This enables live demonstrations and runtime switching between modes without code changes.

**The Problem:**
- Azure App Configuration supports configuration refresh, but by default requires watching individual keys
- Feature flags and configuration values can change in App Configuration, but the application won't pick them up until restart
- For live demonstrations and presentations, we need to **toggle feature flags at runtime** without restarting the service
- Restarting the service causes:
  - **Downtime** - service unavailable during restart
  - **Lost connections** - active user sessions are terminated
  - **Poor user experience** - cannot demonstrate real-time switching
  - **Operational overhead** - requires deployment or manual restart

**Without Sentinel Key Pattern:**
```
1. Update feature flag in App Configuration (BookingEvents_Enabled = true)
2. Application still uses cached value (false)
3. Must restart service to pick up new value
4. Service unavailable during restart
5. Users lose active sessions
Result: Cannot demonstrate live switching, poor UX
```

**The Requirement:**
- **Hot-reload configuration** - pick up App Configuration changes without service restart
- **Zero-downtime switching** - toggle between architectures while service is running
- **Live demonstrations** - show both architectures in real-time during presentations
- **Operational flexibility** - change feature flags without deployment
- **Automatic refresh** - application should detect and apply changes automatically

---

## Decision

We implement the **Sentinel Key Pattern** for hot-reloading Azure App Configuration values. This pattern uses a dedicated "sentinel" key that, when its value changes, triggers a refresh of all configuration values (including feature flags).

**Implementation Details:**
- **Sentinel Key:** `Settings:Sentinel` in App Configuration
- **Refresh Configuration:** `refresh.Register("Settings:Sentinel", refreshAll: true)`
  - When sentinel key value changes, all configuration refreshes automatically
  - `refreshAll: true` ensures all keys (not just watched keys) are refreshed
- **Refresh Interval:** `SetRefreshInterval(TimeSpan.FromSeconds(30))` - checks for changes every 30 seconds (reduced from 1 minute for faster testing)
- **Refresher Access:** Store refresher directly during configuration using `options.GetRefresher()` in `ConfigurationExtensions.cs`
  - **Critical:** `IConfigurationRefresherProvider` may not be registered in service container
  - Store refresher in static variable: `private static IConfigurationRefresher? _configurationRefresher;`
  - Access via static method: `ConfigurationExtensions.GetConfigurationRefresher()`
  - This bypasses service container registration issues
- **Middleware:** Custom middleware in `WebApplicationExtensions.cs` calls `TryRefreshAsync()` on each HTTP request
  - Middleware must be placed early in pipeline (after static files, before routing)
  - Accesses refresher via static variable (primary) or service container (fallback)
  - Without this middleware, hot-reload will not work (only restart will pick up changes)
- **Cache Expiration:** 30 seconds for feature flags and configuration refresh (can be increased to 1 minute for production)
- **Fallback:** Sentinel key also exists in `appsettings.json` with initial value "1" for local development

**Updating Sentinel Key:**

**PowerShell:**
```powershell
az appconfig kv set --name examwork-appconfig-dev --key Settings:Sentinel --value "$([DateTimeOffset]::UtcNow.ToUnixTimeSeconds())" --yes
```

**Bash/Git Bash (Windows):**
```bash
# Note: Git Bash on Windows may interpret 'date' as PowerShell Get-Date
# Use Python instead for reliable Unix timestamp:
az appconfig kv set --name examwork-appconfig-dev --key Settings:Sentinel --value $(python -c "import time; print(int(time.time()))") --yes
```

**Flow:**
```
1. Feature flag changed in App Configuration (BookingEvents_Enabled = true)
   ↓
2. Update sentinel key value (Settings:Sentinel = "2" → "3")
   ↓
3. Application polls sentinel key (every 1 minute)
   ↓
4. Detects sentinel value changed
   ↓
5. Refreshes ALL configuration (refreshAll: true)
   ↓
6. Feature flag value updated in application
   ↓
7. Next booking uses new architecture path
   ↓
8. No service restart required - zero downtime
```

**Key Properties:**
- **Single Trigger Key:** One sentinel key triggers refresh of all configuration
- **Atomic Refresh:** All configuration refreshes together, preventing partial updates
- **Automatic Detection:** Application polls for changes, no manual intervention needed
- **Zero Downtime:** Configuration updates without service restart
- **Operational Simplicity:** Update sentinel value to trigger refresh (simple increment)

**Usage:**
1. Change feature flag value in App Configuration UI
2. Update sentinel key value (increment: "1" → "2" → "3", etc.)
3. Wait up to 1 minute for automatic refresh
4. Configuration and feature flags are updated
5. Application uses new values immediately

**Admin Dashboard Toggle UI (v1.1 Addition):**
After implementing the sentinel key pattern, we recognized an opportunity to add a **feature flag toggle UI directly in the Admin Dashboard**. This was not originally planned but became feasible once hot-reload was working.

**Implementation:**
- **Location:** `/admin` page (Admin Dashboard)
- **Components:**
  - Mini health check section displaying App Configuration status, feature flag value, and outbox pending events
  - Toggle button to enable/disable event-driven mode
  - Real-time propagation status with polling to detect when changes take effect
- **API Endpoints:**
  - `GET /api/featureflag/mini-health` - Returns simplified health status
  - `POST /api/featureflag/toggle` - Toggles feature flag and updates sentinel key (Admin role only)
- **Features:**
  - Debouncing (2-second minimum between clicks)
  - 5-second cooldown after successful toggle
  - Automatic polling every 3 seconds to detect when change takes effect
  - Visual feedback: "Waiting for change..." (yellow) → "Change applied!" (green)
  - Timeout handling (60 seconds max wait)
  - ETag-based optimistic concurrency control
  - Retry logic with exponential backoff for transient errors
- **Benefits:**
  - **Faster Testing** - No need to use Azure CLI or Portal to toggle flags
  - **Live Demonstrations** - Perfect for showing architecture switching in real-time
  - **Better UX** - Clear visual feedback when changes propagate
  - **Operational Convenience** - Admins can toggle flags directly from the dashboard

**Propagation Behavior & Cold Start:**
During testing, we observed that feature flag toggles become faster after the application "warms up":
- **First toggle:** 3-7 checks (9-21 seconds) - App Service B1 tier cold start
- **Subsequent toggles:** 1-3 checks (3-9 seconds) - Application warmed up

**Root Causes:**
1. **Azure App Service B1 Tier Cold Start** - After idle time, the first request can be slower. Once warm, subsequent requests are faster.
2. **30-Second Refresh Interval** - The sentinel key triggers refresh, but refresh only runs if 30 seconds have elapsed since the last refresh. If toggling within 30 seconds, it may wait for the next refresh window.
3. **App Configuration Propagation** - Changes can take a few seconds to propagate through Azure's infrastructure. Once the app is active, it may pick up changes faster.

**Mitigation:**
- **Polling UX** - The Admin Dashboard polls every 3 seconds to detect when changes take effect, providing real-time feedback regardless of propagation timing
- **Visual Status** - Shows elapsed time and check count, so users understand the system is working even during cold starts
- **Production Considerations:**
  - Enable "Always On" for production (reduces cold starts, additional cost)
  - Consider higher tier for better performance
  - Or accept cold start delays with the polling UX (current approach)

---

## Consequences

**Advantages:**
- **Zero-Downtime Updates** – Configuration and feature flags can be updated without service restart. Critical for production environments and live demonstrations.
- **Live Demonstrations** – Can switch between synchronous and event-driven architectures in real-time during presentations. Shows both approaches side-by-side without code changes.
- **Operational Flexibility** – Operators can change feature flags without deployment or code changes. Enables A/B testing, gradual rollouts, and emergency toggles.
- **Better User Experience** – No service interruption when updating configuration. Active user sessions remain connected.
- **Automatic Refresh** – Application automatically detects and applies changes. No manual intervention required.
- **Atomic Updates** – All configuration refreshes together (`refreshAll: true`), preventing partial updates that could cause inconsistent state.
- **Simple Operation** – Updating sentinel key value is straightforward (just increment a number). No complex procedures required.
- **Cost Effective** – No additional infrastructure needed. Uses existing App Configuration refresh capabilities.
- **Admin Dashboard Toggle (v1.1)** – Feature flag can be toggled directly from Admin Dashboard with real-time propagation feedback. Eliminates need for Azure CLI or Portal access during demonstrations.

**Disadvantages:**
- **Polling Overhead** – Application polls App Configuration every minute, consuming resources even when no changes occur. However, this is minimal (single key check).
- **Refresh Delay** – Changes take up to 1 minute to propagate (refresh interval). For immediate updates, would need to reduce interval (increases polling overhead).
- **Sentinel Key Management** – Requires discipline to update sentinel key when changing configuration. If forgotten, changes won't be picked up until next sentinel update. (Mitigated by Admin Dashboard toggle which updates sentinel automatically.)
- **Cache Complexity** – Configuration is cached, and refresh logic adds complexity to configuration pipeline. Requires understanding of refresh behavior.
- **Potential Race Conditions** – If multiple configuration values change simultaneously, refresh happens atomically but timing could cause brief inconsistencies (mitigated by `refreshAll: true`).
- **Cold Start Delays (v1.1)** – On Azure App Service B1 tier, first toggle after idle period can take 9-21 seconds due to cold start. Subsequent toggles are faster (3-9 seconds). Mitigated by polling UX that provides real-time feedback.

---

## Risks / Mitigations

- **Risk:** Sentinel key value not updated when changing feature flags, causing changes to not be picked up.  
  **Mitigation:** Document the process clearly. Consider automation (script or Azure Function) to automatically update sentinel when feature flags change. Add monitoring/alerting if sentinel hasn't changed in expected timeframe.

- **Risk:** Refresh interval too long (1 minute) causes delays in configuration updates during demonstrations.  
  **Mitigation:** Can reduce refresh interval to 30 seconds or less for faster updates. Balance between responsiveness and polling overhead. For production, 1 minute is acceptable.

- **Risk:** Multiple operators updating sentinel key simultaneously could cause refresh conflicts.  
  **Mitigation:** Sentinel key updates are simple increments, conflicts are unlikely. App Configuration handles concurrent updates. Refresh is idempotent - multiple refreshes are safe.

- **Risk:** Application crashes or restarts before refresh completes, losing configuration updates.  
  **Mitigation:** Configuration is persisted in App Configuration. On restart, application loads latest values. Refresh is for runtime updates, not persistence.

- **Risk:** Polling overhead increases costs or impacts performance at scale.  
  **Mitigation:** Polling is lightweight (single key check). Refresh interval can be increased if needed. Consider push-based refresh (Azure Functions or Logic Apps) for future enhancement if polling becomes bottleneck.

- **Risk:** Configuration refresh fails silently, leaving application with stale values.  
  **Mitigation:** Implement health checks to verify configuration refresh is working. Monitor sentinel key value in health endpoint. Log refresh events for observability.

- **Risk:** Cold start delays on B1 tier cause slow feature flag toggles during demonstrations.  
  **Mitigation:** Admin Dashboard polling UX provides real-time feedback showing propagation status. Users understand the system is working even during cold starts. For production, consider "Always On" or higher tier to reduce cold starts.

---

## Alternatives

- **Individual Key Watching** – Rejected. Would require watching every feature flag and configuration key individually. Complex to maintain, easy to miss keys. Sentinel pattern is simpler and more maintainable.

- **Push-Based Refresh (Webhooks)** – Considered for future. Azure App Configuration can trigger webhooks when values change. Would eliminate polling overhead. However, requires additional infrastructure (webhook endpoint, Azure Functions, or Logic Apps). Can be implemented as Phase 10 enhancement if polling becomes bottleneck.

- **Manual Service Restart** – Rejected. Causes downtime, poor user experience, and operational overhead. Not suitable for production or live demonstrations.

- **Configuration Reload Endpoint** – Initially rejected. However, after implementing sentinel key pattern, we added Admin Dashboard toggle UI (`POST /api/featureflag/toggle`) which provides convenient UI for toggling flags while maintaining security (Admin role only) and automatic sentinel key updates. This combines the benefits of both approaches.

- **Change Feed (Cosmos DB Style)** – Not applicable. App Configuration doesn't have change feed. Would need to build custom solution, adding complexity.

- **Longer Refresh Intervals** – Considered. Could increase to 5-10 minutes to reduce polling. However, 1 minute provides good balance between responsiveness and overhead. Can be adjusted per environment (shorter for dev, longer for prod).

- **No Refresh (Restart Required)** – Rejected. Doesn't meet requirement for zero-downtime updates and live demonstrations. Poor operational experience.

---

## References

- [Event-Driven Architecture Roadmap](../journal/eventdriven_roadmap.md)
- [ADR-006 - Event-Driven Architecture](./ADR-006-eventdriven.md)
- [ADR-012 - Azure App Configuration](./ADR-012-azure-app-configuration.md)
- [Week 5 Journal - Admin Dashboard Feature Flag Toggle](../journal/week_five.md#admin-dashboard-feature-flag-toggle-side-mission)
- [Azure App Configuration - Refresh Configuration](https://learn.microsoft.com/en-us/azure/azure-app-configuration/enable-dynamic-configuration-dotnet-core)
- [Sentinel Key Pattern - Microsoft Docs](https://learn.microsoft.com/en-us/azure/azure-app-configuration/enable-dynamic-configuration-dotnet-core#refreshall)

