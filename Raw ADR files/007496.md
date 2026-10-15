# ADR-006 – Event-driven architecture: Azure Service Bus + Azure Function + Outbox Pattern

**Status:** Accepted (Dual-System Implementation)  
**Date:** 2025-10-30  
**Last Updated:** 2025-11-27  
**Author:** Niklas Häll

---

## Context
The existing system that the project is inspired by is built with sequential and chained API calls (API chaining).  
This leads to high coupling between services and difficulties with error handling and scaling.  
To modernize the architecture, a transition to **event-driven communication** is planned, where the system reacts to published events rather than synchronous API calls.

---

## Decision
The system implements **permanent dual-system coexistence** - both synchronous (chained API) and event-driven architectures run side-by-side permanently. This simulates a real-world refactoring scenario where old and new systems coexist.

**Implementation:**
- **Outbox Pattern** implemented in the API (booking events are logged simultaneously as data is written to the database)
- **Azure Service Bus** created for publishing and subscribing to events
- **Azure Function** will react to selected events (e.g., `BookingCreated`) and perform post-processing, notification, or audit logging
- **Feature flags** in Azure App Configuration control which architecture path is active
- **Sentinel key pattern** enables hot-reload of feature flags without service restart

**Dual-System Architecture:**
- **Synchronous Path (default):** When `BookingEvents_Enabled = false`, bookings work exactly as before via chained API calls. No breaking changes.
- **Event-Driven Path:** When `BookingEvents_Enabled = true`, events are published to Service Bus for asynchronous processing.
- **Both paths coexist permanently** - feature flags remain in the system to allow runtime switching between architectures.
- **Always write to outbox** - events are stored in outbox regardless of feature flag state (for audit and future activation).

This approach enables:
- Live demonstrations of both architectures without code changes
- Gradual migration and testing
- Comparison of both approaches side-by-side
- Zero-downtime switching between modes

---

## Consequences
**Advantages:**  
- Looser coupling between components.  
- Easy to build out new features that subscribe to existing events.  
- Improved robustness and scalability under high load.  
- A realistic model for simulating modernization of older API-based systems.
- **Dual-system coexistence** allows comparison and demonstration of both architectures.
- **No breaking changes** - synchronous flow remains fully functional when events are disabled.
- **Hot-reload support** - switch between architectures at runtime without service restart.
- **Performance isolation** - no performance degradation when event-driven path is disabled.

**Disadvantages:**  
- Increased complexity in troubleshooting (the flow becomes asynchronous).  
- Requires more Azure resources and can increase costs.  
- Functions must be designed idempotent to avoid duplicate events.
- **Dual-system overhead** - outbox is always written (minimal performance impact).
- **Feature flag management** - requires operational discipline to manage flags correctly.  

---

## Risks / Mitigations
- **Risk:** Events can be lost in case of errors in Service Bus or Function.  
  **Mitigation:** Use Dead Letter Queue and monitoring via Application Insights.  

- **Risk:** Too early activation of the event flow can increase costs in the MVP phase.  
  **Mitigation:** Keep Service Bus and Functions provisioned but inactive until test or demo.  

- **Risk:** Asynchronicity makes system behavior harder to predict.  
  **Mitigation:** Keep the core flow synchronous and log events separately in Outbox until maturity is reached.

- **Risk:** Feature flag failures could break the system.  
  **Mitigation:** Feature flag service defaults to `false` (synchronous mode) if flag check fails, ensuring system remains functional.

- **Risk:** Dual-system complexity could confuse developers.  
  **Mitigation:** Clear logging of which architecture path is taken, comprehensive documentation, and feature flag status visible in health endpoint.  

---

## Alternatives
- **Pure API-based architecture:** Simpler but difficult to scale and handle errors.  
- **Azure Event Grid:** More advanced and a good service in itself, but unnecessary for MVP and risks increasing costs when multiple event types are introduced.   
- **Service Bus Topics + multiple Functions:** Can be introduced in a later version for broader event distribution.  
  
Note: each additional messaging service (Service Bus, Event Grid, Event Hubs) entails additional costs over time. Therefore, the MVP is kept to Service Bus + Function as the minimum event-driven core.  

---

## Implementation Details

### Feature Flag Configuration
- **Flag Name:** `BookingEvents_Enabled`
- **Default Value:** `false` (synchronous mode)
- **Location:** Azure App Configuration
- **Hot-Reload:** Enabled via sentinel key pattern (`Settings:Sentinel`)

### Architecture Flow

**Synchronous Path (BookingEvents_Enabled = false):**
1. Booking created in Cosmos DB
2. Outbox event created (for audit)
3. Booking returned to client
4. No Service Bus publishing
5. No Function processing

**Event-Driven Path (BookingEvents_Enabled = true):**
1. Booking created in Cosmos DB
2. Outbox event created
3. Event published to Service Bus (Phase 5)
4. Azure Function processes event (Phase 6)
5. Booking returned to client

### Separation of Concerns
- **Feature Flag Service:** Isolated service for flag checking, defaults to safe mode on failure
- **Outbox Service:** Always writes events regardless of flag state
- **Event Publisher:** (Phase 5) Only publishes when flag is enabled
- **Booking Service:** Unchanged - no knowledge of event system
- **Clear boundaries:** Each component has single responsibility

### Performance Characteristics
- **Feature flag check:** Async but lightweight (~1ms overhead)
- **Outbox write:** Always performed (~5-10ms overhead)
- **Service Bus publish:** Only when flag enabled (Phase 5)
- **No blocking:** All event operations are fire-and-forget, don't block booking creation

### Feature Flag Usage

#### How to Enable/Disable Event Flow

**Via Azure Portal:**
1. Navigate to Azure Portal → App Configuration → `examwork-appconfig-dev`
2. Go to **Feature Manager** → **Feature flags**
3. Find or create feature flag: `BookingEvents_Enabled`
4. Set value:
   - **`false`** = Synchronous mode (chained API calls, no Service Bus publishing)
   - **`true`** = Event-driven mode (events published to Service Bus)
5. **Update sentinel key** to trigger hot-reload:
   - Go to **Configuration explorer** → **Create** → Key: `Settings:Sentinel`
   - Set value to increment (e.g., "1" → "2" → "3")
   - This triggers automatic refresh of all configuration within 1 minute
6. Verify in application:
   - Check `/api/health` endpoint - `FeatureFlagTest` shows current flag value
   - Create a booking and check logs - should show "Synchronous" or "Event-Driven" architecture path

**Via Azure CLI:**
```bash
# Enable feature flag (event-driven mode)
az appconfig feature enable \
  --name examwork-appconfig-dev \
  --feature BookingEvents_Enabled \
  --yes

# Update sentinel key to trigger refresh
az appconfig kv set \
  --name examwork-appconfig-dev \
  --key Settings:Sentinel \
  --value "2" \
  --yes
```

#### Use Cases for Each Mode

**Synchronous Mode (`BookingEvents_Enabled = false`):**
- **Development:** Default mode during initial development and testing
- **Cost Optimization:** No Service Bus message costs, Functions not triggered
- **Simplified Debugging:** All operations synchronous, easier to trace
- **Legacy Compatibility:** Matches original chained API architecture
- **Low Load Scenarios:** Sufficient for small-scale operations
- **Testing:** Verify core booking functionality without event complexity

**Event-Driven Mode (`BookingEvents_Enabled = true`):**
- **Demonstrations:** Show event-driven architecture capabilities
- **Production:** Scalable architecture for high-load scenarios
- **Integration Testing:** Test Service Bus and Function integration
- **Performance Testing:** Measure event-driven flow performance
- **Gradual Migration:** Test event-driven path alongside synchronous
- **Future Features:** Enable new features that depend on events

#### Switching Modes During Demonstrations

**Step-by-Step Instructions:**

1. **Prepare:**
   - Ensure App Configuration is accessible
   - Have Azure Portal open to App Configuration resource
   - Have application health endpoint ready (`/api/health`)

2. **Switch to Event-Driven Mode:**
   - Azure Portal → App Configuration → Feature Manager → Feature flags
   - Set `BookingEvents_Enabled` to `true` (or create if doesn't exist)
   - Configuration explorer → Update `Settings:Sentinel` value (increment: "1" → "2")
   - Wait up to 1 minute for automatic refresh
   - Verify: Check `/api/health` - `FeatureFlagTest` should show `BookingEvents_Enabled = true`
   - Create booking - logs should show "Event-Driven" architecture path

3. **Switch Back to Synchronous Mode:**
   - Azure Portal → App Configuration → Feature Manager → Feature flags
   - Set `BookingEvents_Enabled` to `false`
   - Configuration explorer → Update `Settings:Sentinel` value (increment: "2" → "3")
   - Wait up to 1 minute for automatic refresh
   - Verify: Check `/api/health` - `FeatureFlagTest` should show `BookingEvents_Enabled = false`
   - Create booking - logs should show "Synchronous" architecture path

4. **Verify Both Modes:**
   - Create bookings in both modes
   - Check Application Insights logs - should see architecture path in log messages
   - Verify outbox container - events should be created in both modes
   - Compare performance and behavior between modes

**Important Notes:**
- **No service restart required** - sentinel key pattern enables hot-reload
- **Zero downtime** - switching happens without interrupting service
- **Outbox always writes** - events are stored regardless of mode (for audit)
- **Service Bus publishing** - only happens in event-driven mode (Phase 5)
- **Logging** - all operations log which architecture path was taken

#### Permanent Dual-System Approach

The feature flags are **permanent** and will remain in the system indefinitely. This enables:
- **Runtime Flexibility:** Switch between architectures without code changes
- **A/B Testing:** Compare both approaches with real traffic
- **Gradual Migration:** Migrate users or features gradually
- **Rollback Capability:** Quickly revert to synchronous mode if issues arise
- **Demonstration Value:** Show both architectures side-by-side

**Flag Lifecycle:**
- Flags are created in App Configuration (not in code)
- Flags persist across deployments
- Flags can be environment-specific (dev vs prod)
- Flags support hot-reload via sentinel key pattern
- Flags default to safe mode (`false`) if check fails

## References
- [Architecture overview](../initial_outtakes/architecture.md)  
- [System overview](../initial_outtakes/system_overview.md)  
- [Event-Driven Roadmap](../journal/eventdriven_roadmap.md)
- [Microsoft Docs – Azure Service Bus](https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-messaging-overview)  
- [Microsoft Docs – Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/functions-overview)  
- [Transactional outbox pattern with Azure Cosmos DB](https://learn.microsoft.com/sv-se/azure/architecture/databases/guide/transactional-outbox-cosmos)
- [ADR-012: Azure App Configuration](../adr/ADR-012-azure-app-configuration.md)
- [ADR-013: Outbox Pattern](../adr/ADR-013-outbox-pattern.md)
- [ADR-014: Sentinel Key Pattern](../adr/ADR-014-sentinel-key-pattern.md)  
  