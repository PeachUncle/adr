# ADR-002: State Management with Dioxus Signals

**Status:** Accepted
**Date:** 2025-01-13
**Phase:** Phase 2 - Data Models & State Management

## Context

The Quarterly Planner needs to manage complex application state including:

- Quarter configuration (start date, number of weeks)
- Engineers list with roles and capacities
- Roadmap projects with estimates and dates
- Technical projects linked to roadmap projects
- Weekly allocations for each engineer
- UI state (current view, paintbrush mode, selections)

We needed to decide on a state management approach that:

1. Works well with Dioxus's reactive UI model
2. Provides efficient re-rendering when state changes
3. Is simple enough for a single-user desktop/web application
4. Allows components to easily access and modify shared state
5. Supports undo/redo functionality (future requirement)

## Decision

We adopted **Dioxus Signals** as our primary state management solution with a single global state hook: `use_plan_state()`.

### Architecture

**Global State Hook:**

```rust
// src/state.rs
pub fn use_plan_state() -> Signal<Plan> {
    use_context::<Signal<Plan>>()
}
```

**State Initialization:**

```rust
// src/main.rs
fn App() -> Element {
    use_context_provider(|| Signal::new(Plan::with_sample_data()));
    // ...
}
```

**Usage in Components:**

```rust
// Read-only access
fn MyComponent() -> Element {
    let plan = use_plan_state();
    let plan_data = plan();  // Get immutable reference
    // Use plan_data...
}

// Read-write access
fn EditComponent() -> Element {
    let mut plan = use_plan_state();
    plan.write().engineers.push(new_engineer);  // Modify state
}
```

### Key Principles

1. **Single Source of Truth**: All plan data flows through one `Signal<Plan>`
2. **Context-Based Sharing**: Context provider makes state available to all components
3. **Automatic Reactivity**: Components automatically re-render when their accessed state changes
4. **Granular Updates**: Dioxus tracks which parts of state are used by each component

## Alternatives Considered

### 1. Multiple Separate Signals

**Approach:**
```rust
use_context_provider(|| Signal::new(engineers));
use_context_provider(|| Signal::new(projects));
use_context_provider(|| Signal::new(allocations));
```

**Rejected because:**
- Harder to maintain data consistency across related entities
- More complex to serialize/deserialize for file operations
- Difficult to implement undo/redo (would need to track multiple signals)
- Referential integrity harder to enforce (e.g., allocations referencing engineers)
- More boilerplate to access multiple signals in components

**When it might be better:**
- If state was truly independent with no cross-references
- If we needed per-entity update granularity for performance

### 2. Redux/Flux Pattern

**Approach:**
```rust
dispatch(Action::AddEngineer(engineer));
dispatch(Action::UpdateAllocation { ... });
```

**Rejected because:**
- Significant boilerplate (actions, reducers, dispatch)
- Overkill for single-user application
- No Dioxus-idiomatic Redux library
- Would need to build custom Redux implementation
- Harder to implement straightforward CRUD operations

**When it might be better:**
- Multi-user application with complex state synchronization
- Need for middleware (logging, time-travel debugging)
- Large team requiring enforced state update patterns

### 3. Direct Props Drilling

**Approach:**
```rust
fn App() -> Element {
    let plan = use_signal(|| Plan::default());
    rsx! {
        TopNav { plan }
        AllocationView { plan }
    }
}
```

**Rejected because:**
- Deep component trees require passing props through many levels
- Refactoring component structure breaks prop chains
- Verbose and error-prone
- Doesn't scale with application complexity

**When it might be better:**
- Very simple applications with shallow component trees
- When explicit data flow is more important than convenience

### 4. External State Management (Recoil/Zustand-like)

**Rejected because:**
- No mature Rust equivalent for Dioxus
- Would need to build custom solution
- Signals already provide reactive state
- Additional complexity without clear benefits for our use case

## Consequences

### Positive

- **Simple API**: Single `use_plan_state()` hook for all components
- **Automatic Reactivity**: Components re-render when relevant state changes
- **Easy Serialization**: Single `Plan` struct can be directly serialized to JSON
- **Type Safety**: Full Rust type system ensures state consistency
- **Undo/Redo Ready**: Single state object makes command pattern implementation straightforward
- **Developer Friendly**: Familiar React-like hooks API
- **Performance**: Dioxus's fine-grained reactivity only re-renders affected components

### Negative

- **Coarse-Grained Updates**: Updating any part of `Plan` could theoretically trigger broader re-renders (mitigated by Dioxus's smart diffing)
- **No Built-in Middleware**: Manual implementation needed for logging, persistence, etc.
- **No Time-Travel Out of Box**: Must implement undo/redo manually (planned for Phase 12)

### Neutral

- **State Structure Mirrors Domain**: Plan struct directly represents the domain model
- **Manual Validation**: State updates don't automatically validate (but gives us control over when/how)

## Implementation Details

### State Structure

```rust
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Plan {
    pub quarter_start_date: NaiveDate,
    pub weeks_in_quarter: usize,
    pub engineers: Vec<Engineer>,
    pub roadmap_projects: Vec<RoadmapProject>,
    pub technical_projects: Vec<TechnicalProject>,
    pub allocations: Vec<Allocation>,
}
```

### Computed Values

We implement computed values as methods on `Plan`:

```rust
impl Plan {
    pub fn calculate_total_capacity(&self) -> f32 {
        self.engineers.iter()
            .map(|e| e.capacity)
            .sum()
    }

    pub fn calculate_allocated_weeks(&self, engineer_id: &str) -> f32 {
        self.allocations.iter()
            .filter(|a| a.engineer_id == engineer_id)
            .flat_map(|a| &a.assignments)
            .map(|a| a.percentage / 100.0)
            .sum()
    }
}
```

**Benefits:**
- Always up-to-date (computed on demand)
- No risk of stale derived state
- Easy to test independently
- Clear code organization

## Future Considerations

1. **Performance Optimization**: If large datasets cause performance issues, consider:
   - Memoizing computed values
   - Splitting state into multiple signals for independent update paths
   - Using `Memo` for expensive calculations

2. **Undo/Redo (Phase 12)**: Current architecture supports command pattern:
   ```rust
   trait Command {
       fn execute(&self, plan: &mut Plan);
       fn undo(&self, plan: &mut Plan);
   }
   ```

3. **State Persistence**: Auto-save could be implemented by:
   - Subscribing to signal changes
   - Debouncing writes to disk
   - Using `Signal::on_change()` when available

4. **Multi-User/Sync**: If collaboration is needed:
   - Consider CRDTs for conflict-free replication
   - Operational transformation for real-time sync
   - Would require significant architectural changes

## References

- Dioxus Signals documentation: https://dioxuslabs.com/learn/0.7/reference/hooks
- State implementation: `src/state.rs`
- Data models: `src/models/plan.rs`
- State management patterns: `docs/state-management.md`
