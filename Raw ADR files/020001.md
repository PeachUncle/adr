# ADR-001: Offline-First Architecture

**Status:** Accepted  
**Date:** 2025-12-16  
**Deciders:** Development Team

## Context

Volleyball coaches need to track statistics during live matches in environments where internet connectivity is unreliable or unavailable (gymnasiums, tournament venues, outdoor courts). The app must work seamlessly offline while capturing real-time rally data without any degradation in functionality.

Traditional online-first architectures would fail or provide a degraded experience in these conditions, potentially causing coaches to lose critical match data.

## Decision

We will implement an **offline-first architecture** where:

1. **All data is stored locally first** using Flutter's local storage solutions (Hive/SQLite)
2. **All features work without network connectivity** - match setup, rally capture, statistics viewing
3. **Sync is opportunistic** - when online, data syncs to Supabase in the background
4. **Conflicts are resolved** - last-write-wins initially, with potential for more sophisticated resolution later
5. **No auth blocking** - users can use the app without signing in, with data stored locally and synced when they do authenticate

## Consequences

### Positive
- **Reliable data capture** - No data loss due to connectivity issues
- **Better user experience** - No loading spinners or "no connection" errors during critical match moments
- **Performance** - All operations are instant (no network latency)
- **Works anywhere** - Gyms, outdoor venues, rural locations, tournaments with poor WiFi

### Negative
- **Increased complexity** - Need to manage local storage, sync queue, conflict resolution
- **Larger app size** - Bundling database libraries and sync logic
- **Testing overhead** - Must test offline scenarios, sync edge cases, conflict resolution
- **Data synchronization** - Risk of sync failures requiring retry logic and error handling

### Neutral
- **Storage requirements** - Local database grows over time, but volleyball stats are relatively small
- **Battery usage** - Slightly higher due to background sync, but negligible for typical usage

## Alternatives Considered

1. **Online-Only Architecture**
   - **Rejected**: Would fail completely without connectivity, unacceptable for live match use
   - Coaches can't afford to lose rally data mid-match

2. **Hybrid (Online-First with Offline Cache)**
   - **Rejected**: Degraded experience when offline, complex state management between modes
   - "Offline mode" feels like a second-class citizen

3. **Manual Sync Only**
   - **Rejected**: Requires user to remember to sync, risk of data loss if they forget
   - Better UX to handle sync automatically

## References

- [QA Remediation Plan](../reports/qa-remediation-plan.md) - Phase 1.1: Implement Offline Persistence
- [Simplified Development Plan](../archive/simplified-dev-plan.md) - Phase 2 & 3: Local storage and sync queue
- Flutter packages: `hive`, `sqflite`, `drift` for local storage
- Supabase for cloud sync when available

