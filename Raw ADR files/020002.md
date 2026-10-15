# ADR-002: Riverpod State Management

**Status:** Accepted  
**Date:** 2025-12-16  
**Deciders:** Development Team

## Context

Flutter volleyball stats app requires robust state management for:
- Match and rally data that changes frequently during live capture
- Running totals (FBK, wins, losses, transition points) that update in real-time
- Player statistics that recalculate after each action
- UI state (expanded/collapsed cards, filters, selections)
- Sync status and offline/online mode

We needed a state management solution that handles complex dependencies, provides good testability, and scales well as the app grows.

## Decision

We chose **Riverpod** as our state management solution because:

1. **Type-safe** - Compile-time safety with no runtime strings or magic
2. **Testable** - Easy to mock providers and test business logic in isolation
3. **Composable** - Providers can depend on other providers cleanly
4. **Performance** - Fine-grained reactivity, only rebuilds what changes
5. **No BuildContext** - Can read/write state anywhere without passing context
6. **Provider scoping** - Can override providers for testing or feature flags
7. **Ecosystem maturity** - Well-maintained, strong community, extensive documentation

## Consequences

### Positive
- **Better developer experience** - Clear separation between UI and business logic
- **Easier testing** - Can test providers without widget tests
- **Type safety** - Catch errors at compile time instead of runtime
- **Performance** - Fine-grained rebuilds, efficient for real-time stat updates
- **Scalability** - Easy to add new providers as features grow
- **Debugging** - Riverpod DevTools shows provider state and dependencies

### Negative
- **Learning curve** - Team must learn Riverpod patterns and best practices
- **Boilerplate** - More code compared to setState for simple use cases
- **Migration cost** - If we ever need to change, would require significant refactoring

### Neutral
- **Package dependency** - Adds `flutter_riverpod` and `riverpod_annotation` to dependencies
- **Code generation** - Uses `build_runner` for generated providers (already using for other purposes)

## Alternatives Considered

1. **Provider (older package)**
   - **Rejected**: Less type-safe, deprecated in favor of Riverpod
   - Riverpod is the successor with better API

2. **Bloc/Cubit**
   - **Rejected**: More verbose, event-driven architecture feels heavy for this use case
   - Better for large teams with strict architectural requirements
   - Overkill for single developer / small team

3. **GetX**
   - **Rejected**: Too "magical", relies on global state and service locator pattern
   - Poor testability, harder to reason about dependencies
   - Community concerns about maintenance and API stability

4. **setState() only**
   - **Rejected**: Doesn't scale, too much prop drilling, hard to share state
   - Running totals and player stats need to be accessed from multiple screens

## References

- [Riverpod Documentation](https://riverpod.dev/)
- Implementation: `lib/features/rally_capture/providers.dart`, `lib/features/match_setup/providers.dart`
- [Repository Guidelines](../guidelines.md) - Coding standards mention Riverpod patterns
- Running totals provider example: manages FBK, wins, losses, transition points state

