# ADR-005: State Architecture, Persistence, and Export Format

**Status**: Accepted (Updated)

**Date**: 2025-01-23 (Updated: 2025-11-25)

**Decision Makers**: Matthew Emerson, Claude Code

---

## Context

After completing Milestone 8, we have a functional allocation planner with paintbrush mode, keyboard shortcuts, and tooltips. However, we face several architectural challenges:

### Problem 1: Suboptimal Reactivity

Currently using a single `Signal<Plan>` containing all state:
- Team members (rarely changes)
- Sprint configuration (rarely changes)
- Roadmap projects (occasional changes)
- Technical projects (occasional changes)
- Allocations (changes constantly - every paintbrush click)

**Issue**: Dioxus signals track reactivity at the signal level, not at field granularity. When `plan.write().team_members.push()` executes, Dioxus marks the **entire signal as dirty**, triggering re-renders for **all components** that read from `plan()`, even if they only care about allocations.

**Performance Impact**: Low (VDOM diffing handles this efficiently), but indicates poor separation of concerns.

### Problem 2: Mixed Persistence Requirements

We identified two distinct persistence needs:

**Team Configuration (Long-Term)**:
- Team members roster
- Sprint anchor date
- Sprint length
- Default capacity

→ Should persist in **localStorage between sessions** (survives browser refresh)

**Planning Data (Short-Term)**:
- Roadmap projects
- Technical projects
- Allocations
- Quarter metadata

→ Should be **exported/imported per quarter** (versioned, shareable, archivable)

**Current limitation**: Single signal can't distinguish between these persistence strategies.

### Problem 3: Export Portability

Plans must be shareable for 1.0 use cases:
- Alice shares her Q1 plan with Bob for review
- Manager archives Q1 plan and starts planning Q2
- Team retrospective on Q4 allocations

**Current limitation**: Allocations reference `team_member_id` UUIDs. If we export only plan data (not team context), imports break because UUIDs have no meaning to the importing user.

**Required**: Self-contained exports that include full team context.

### Problem 4: Future Multi-Team Aggregation

**Post-1.0 Vision** (from roadmap discussion):
> Sr Managers should be able to load multiple team plans and view organization-level capacity. Each "team" would have a name, and all allocations could be rolled up into individual teams. So the org view would be something like teams for each column (instead of team members), and the weeks on the left. In each grid cell, maybe it has a breakdown of percentages for each project.

**Required**: Export format must support future aggregation **without breaking changes**. This means:
- Each export must identify which team it belongs to (`team_name`)
- Each export must be fully self-contained (include complete team roster)
- Multiple exports can be loaded and grouped by `team_name`

---

## Decision

We will implement a **two-signal architecture** with **self-contained exports** and **two-tier persistence**.

### 1. Two-Signal State Architecture

Split the monolithic `Plan` signal into two independent signals:

```rust
// Signal 1: Preferences (persisted in localStorage)
pub struct Preferences {
    pub team_name: String,               // NEW: Identifies this team
    pub team_members: Vec<TeamMember>,   // Full roster
    pub sprint_anchor_date: NaiveDate,   // Global sprint start
    pub sprint_length_weeks: usize,      // Sprint duration
    pub default_capacity: f32,           // Default weeks per person
}

// Signal 2: PlanState (exported/imported per quarter)
pub struct PlanState {
    pub quarter_name: String,            // "Q1 2025"
    pub quarter_start_date: NaiveDate,
    pub num_weeks: usize,
    pub roadmap_projects: Vec<RoadmapProject>,
    pub technical_projects: Vec<TechnicalProject>,
    pub allocations: Vec<Allocation>,
    pub metadata: PlanMetadata,          // version, created_at, modified_at
}

// App Context
#[derive(Clone, Copy)]
pub struct AppContext {
    pub preferences: Signal<Preferences>,
    pub plan_state: Signal<PlanState>,
}
```

**Component Access**:
```rust
// Read preferences
let preferences = use_preferences();
let team_name = preferences().team_name;
let members = preferences().team_members;

// Read/write plan state
let plan_state = use_plan_state();
let projects = plan_state().roadmap_projects;
plan_state.write().allocations.push(new_allocation);
```

### 2. Self-Contained Export Format

Exports combine both signals into a portable package:

```rust
#[derive(Serialize, Deserialize)]
pub struct PlanExport {
    pub version: String,  // "1.0"
    pub metadata: PlanMetadata,

    // TEAM CONTEXT (snapshot at export time)
    pub team_name: String,              // "Backend Team"
    pub team_members: Vec<TeamMember>,  // Full roster for portability

    // PLANNING DATA
    pub quarter_name: String,
    pub quarter_start_date: NaiveDate,
    pub num_weeks: usize,
    pub roadmap_projects: Vec<RoadmapProject>,
    pub technical_projects: Vec<TechnicalProject>,
    pub allocations: Vec<Allocation>,
}

impl PlanExport {
    pub fn from_signals(prefs: Preferences, state: PlanState) -> Self {
        PlanExport {
            version: "1.0".to_string(),
            metadata: state.metadata,

            // Snapshot team context
            team_name: prefs.team_name,
            team_members: prefs.team_members,

            // Planning data
            quarter_name: state.quarter_name,
            quarter_start_date: state.quarter_start_date,
            num_weeks: state.num_weeks,
            roadmap_projects: state.roadmap_projects,
            technical_projects: state.technical_projects,
            allocations: state.allocations,
        }
    }
}
```

### 3. Three-Tier Persistence Strategy

**Tier 1: Preferences (localStorage)**
- **Storage**: Browser localStorage (key: `"planner_preferences"`)
- **Trigger**: Auto-save on change via `use_effect`
- **Lifetime**: Persists across sessions, browser refreshes
- **Migration**: First-time users get smart defaults (next quarter based on current date)

```rust
use_effect(move || {
    let prefs = preferences();
    let _ = storage::save_preferences(&prefs);
});
```

**Tier 2: Plan State (localStorage - Working Copy)**
- **Storage**: Browser localStorage (key: `"planner_plan_state"`)
- **Trigger**: Auto-save on change via `use_effect`
- **Lifetime**: Persists across sessions as "working copy"
- **Purpose**: Prevents data loss during planning sessions
- **Migration**: First-time users get smart defaults (next quarter name/date)

```rust
use_effect(move || {
    let state = plan_state();
    let _ = storage::save_plan_state(&state);
});
```

**Tier 3: Plan Export (file/clipboard - Sharing & Archiving)**
- **Storage**: JSON files (manual export) OR base64 clipboard (copy/paste)
- **Trigger**: User-initiated (Settings → Export/Import, planned for M13)
- **Lifetime**: Per quarter, user-managed (versioned, archived, shareable)
- **Format**: Self-contained `PlanExport` struct (includes team snapshot)

> **Design Decision (M12.5)**: We added localStorage persistence for PlanState to prevent accidental data loss. Users were losing planning work when refreshing the browser. The export/import feature (M13) remains for intentional sharing and archiving, while localStorage serves as the automatic "working copy."

### 4. Storage Implementation

**Actual Implementation (M12.5)**: Direct platform APIs without abstraction layer

**Web (WASM)**: `web_sys::Storage` via localStorage
```rust
// src/storage/mod.rs
#[cfg(target_family = "wasm")]
const PREFERENCES_KEY: &str = "planner_preferences";
#[cfg(target_family = "wasm")]
const PLAN_STATE_KEY: &str = "planner_plan_state";

#[cfg(target_family = "wasm")]
pub fn save_preferences(prefs: &Preferences) -> Result<(), String> {
    let window = web_sys::window().ok_or("No window")?;
    let storage = window.local_storage()?.ok_or("No localStorage")?;
    let json = serde_json::to_string(prefs)?;
    storage.set_item(PREFERENCES_KEY, &json)?;
    Ok(())
}

#[cfg(target_family = "wasm")]
pub fn load_preferences() -> Option<Preferences> {
    let window = web_sys::window()?;
    let storage = window.local_storage().ok()??;
    let json = storage.get_item(PREFERENCES_KEY).ok()??;
    serde_json::from_str(&json).ok()
}
```

**Desktop (Native)**: `dirs` crate + file-based JSON storage
```rust
#[cfg(not(target_family = "wasm"))]
fn get_storage_dir() -> Option<PathBuf> {
    dirs::data_local_dir().map(|p| p.join("planner"))
}

#[cfg(not(target_family = "wasm"))]
pub fn save_preferences(prefs: &Preferences) -> Result<(), String> {
    let dir = get_storage_dir().ok_or("No data directory")?;
    std::fs::create_dir_all(&dir)?;
    let path = dir.join("preferences.json");
    let json = serde_json::to_string_pretty(prefs)?;
    std::fs::write(path, json)?;
    Ok(())
}
```

**Rationale for Direct Implementation**:
- `dioxus-sdk` storage had compatibility issues with Dioxus 0.7
- Direct `web_sys` is lightweight (already a dependency) and well-documented
- `dirs` crate provides cross-platform data directory paths
- No abstraction layer needed - conditional compilation (`#[cfg]`) is sufficient
- Simpler code, fewer dependencies, easier to debug

**For Plan Export**:
- Serialization format: **JSON for v1.0** (human-readable, debuggable)
  - Considered MessagePack (smaller, faster) - **may be added in v1.0 if simple**
  - Decision: Build JSON foundation with serialization abstraction to make binary format trivial to add
  - Binary format would enable compact URL import: `planner.app?import=<base64-msgpack>`
- Export methods:
  - **Primary**: File download (`plan-backend-q1-2025-01-15.json`)
  - **Fallback**: Base64 clipboard (for Slack/email sharing)

**Serialization Abstraction** (enables easy binary format):
```rust
pub trait PlanSerializer {
    fn serialize(&self, plan: &PlanExport) -> Result<Vec<u8>, SerializeError>;
    fn deserialize(&self, data: &[u8]) -> Result<PlanExport, DeserializeError>;
}

// Easy to add: MessagePackSerializer, BincodeSerializer, etc.
```

**File naming**: `plan-{team_name}-{quarter}-{date}.json`

### 5. Settings Modal UI (M12.5)

The Settings Modal provides user access to configuration and storage management:

**Plan Configuration Section**:
- Plan Name (e.g., "Q1 2025", "H1 2025")
- Start Date (date picker)
- Number of Weeks (1-52)

**Sprint Configuration Section**:
- Sprint Anchor Date (known sprint start for alignment)
- Sprint Length (1-4 weeks)

**Storage Section**:
- **Load Sample Data**: Populates demo data for testing/onboarding
- **Clear Preferences**: Resets team members, sprint config to defaults (with confirmation)

**Validation**:
- Inline validation for date formats (YYYY-MM-DD)
- Range validation for weeks/sprint length
- Single "Apply" button validates all sections before saving

**Smart Defaults**:
- First-time users get next quarter based on current date
- Quarter start date is actual first day (Jan 1, Apr 1, Jul 1, Oct 1)
- Default sprint anchor aligns with quarter start

---

## Consequences

### Positive

✅ **Isolated Reactivity**: Team changes only trigger components reading `preferences`, not those reading `plan_state`

✅ **No Data Loss (M12.5)**: Both signals auto-save to localStorage, preventing accidental data loss from browser refresh or navigation

✅ **Natural Persistence Model**: Three-tier storage aligns with business requirements:
- Team config persists between quarters (localStorage - Tier 1)
- Plan state persists as working copy (localStorage - Tier 2)
- Plans exported for sharing/archiving (file export - Tier 3, M13)

✅ **Portable Exports**: Self-contained format enables:
- **1.0 Sharing**: Alice exports → Bob imports and sees all team member names/roles correctly
- **1.0 Archiving**: Save Q1 plan before starting Q2
- **1.0 Review**: Share with colleagues or management for feedback

✅ **Future-Proof for Multi-Team Aggregation**: Export format supports v2.0 org-level views **without breaking changes**:
- Each export has `team_name` → group by team
- Each export has full `team_members` → drill down to individual allocations
- Multiple exports can be loaded simultaneously
- Aggregation logic works on existing format (no migration needed)

✅ **Maintainability**: Clear separation of concerns:
- Preferences = long-term team config
- Plan state = quarter-specific planning data

✅ **Testability**: Easier to test persistence and export logic independently

### Negative

⚠️ **Slightly More Complex State Access**: Components need two signals instead of one
```rust
// Before: let plan = use_plan_state();
// After:  let preferences = use_preferences(); let plan_state = use_plan_state();
```
→ **Mitigation**: Clear documentation, consistent patterns across codebase

⚠️ **Larger Export Files**: Including team snapshot increases file size
- Estimated: ~10-20 KB vs ~5-10 KB (for 10-person team)
- **Acceptable**: Human-readable JSON is worth the tradeoff, files are still tiny

⚠️ **Team Mismatch Handling**: Import needs to detect when plan is for different team
- Alice (Backend) exports → Bob (Frontend) imports
- Must offer: View read-only, Merge teams, or Cancel
→ **Mitigation**: Clear UI for team mismatch detection (M13)

### Neutral

○ **Refactoring Required**: ~15 components need to switch from single signal to two signals
- Estimated effort: 4-6 hours (mostly find/replace)
- Low risk: Mechanical refactor with clear pattern

---

## Alternatives Considered

### Alternative 1: Three-Signal Architecture

**Proposal**: Split `plan_state` further into `projects` and `allocations` signals

```rust
let preferences = use_signal(|| Preferences { ... });
let projects = use_signal(|| Projects { roadmap_projects, technical_projects });
let allocations = use_signal(|| AllocationState { allocations, metadata });
```

**Rationale**: Paintbrush clicks only dirty `allocations` → RoadmapView/TechnicalView never re-render

**Decision**: **REJECTED**

**Reasons**:
1. **VDOM diffing already optimizes re-renders**: When RoadmapView re-renders (even though `roadmap_projects` unchanged), Dioxus generates new VDOM, diffs against old VDOM, detects **zero changes**, performs **zero DOM updates**. Performance impact is negligible for simple tables.

2. **Adds complexity without solving real problem**:
   - Export/import becomes messier (combine 3 signals instead of 2)
   - More state to reason about (which signal for this operation?)
   - No measurable performance benefit at our scale (10-15 projects, 130 allocations)

3. **Premature optimization**: Current scale (10 engineers × 13 weeks = 130 cells) doesn't warrant this complexity

**When we'd reconsider**: If profiling showed allocation updates causing perf issues (unlikely)

### Alternative 2: Single Signal with Nested Structs

**Proposal**: Keep single `Signal<Plan>` but add persistence layer on top

**Decision**: **REJECTED**

**Reasons**:
- Doesn't solve reactivity problem (entire signal still marked dirty)
- Doesn't solve persistence separation (still need to split plan vs preferences at export time)
- Loses opportunity for clear architectural separation

### Alternative 3: HashMap for Allocations

**Proposal**: Use `HashMap<(Uuid, NaiveDate), Allocation>` instead of `Vec<Allocation>` for O(1) lookup

**Decision**: **DEFERRED to post-1.0**

**Reasons**:
- Current scale: 130 allocations max (O(n) scan ~100 nanoseconds)
- Vec is simpler to serialize/iterate
- HashMap would complicate insertion/removal slightly
- No performance issues observed

**When we'd reconsider**: If profiling shows allocation lookup is bottleneck (very unlikely)

### Alternative 4: Server-Side State (Firebase, Supabase, etc.)

**Proposal**: Store state in cloud backend instead of localStorage/files

**Decision**: **DEFERRED to v3.0**

**Reasons**:
- Adds complexity (authentication, sync, conflicts)
- Requires backend infrastructure
- Client-side-first approach is simpler for 1.0
- File-based export is more portable (no vendor lock-in)

**When we'd reconsider**: v3.0 when adding real-time collaboration

---

## Implementation Plan

### Milestone 9: State Architecture Refactor (2-3 days)

**9.1: Spike** (2-4 hours) ✅ COMPLETE
- Evaluated storage options: `dioxus-sdk` (chosen), `gloo-storage` (fallback)
- Confirmed JSON serialization for v1.0, with abstraction for future binary format
- Designed self-contained export with team snapshot

**9.2-9.4: Create Models**
- `Preferences` model with `team_name`
- `PlanState` model with `metadata`
- `PlanExport` model (combines both)

**9.5-9.6: Update State Management**
- Refactor `src/state.rs` to use `AppContext` with two signals
- Update `create_sample_plan()` to return tuple

**9.7: Update Components** (~15 files, 4-6 hours)
- Replace `use_plan_state()` with `use_preferences()` + `use_plan_state()`
- Update all state access points

**9.8: Implement Preferences Persistence**
- Auto-save to localStorage on change
- Load from localStorage on startup

**9.9: Update Sprint Calculation**
- Refactor `get_sprint_boundaries()` to use global `sprint_anchor_date`

**Deliverable**: ADR-004 (this document) finalized with spike results

### Milestone 13: Plan Import/Export (2-3 days)

**13.1: Export Plan**
- Combine signals into `PlanExport`
- Serialize to JSON
- Trigger file download OR clipboard copy

**13.2: Import Plan**
- Load JSON file
- Validate format and version
- Detect team mismatch
- Offer read-only or merge options

**13.3: Base64 Clipboard**
- Copy plan as base64 (for Slack/email)
- Paste from clipboard

---

## Validation & Success Criteria

### How We'll Know This Decision is Correct

**Short-term (Milestone 9)**:
- ✅ All existing features work unchanged
- ✅ Components only re-render when their specific data changes
- ✅ Preferences persist across browser refresh
- ✅ Build passes, no regressions

**Medium-term (Milestone 13)**:
- ✅ Alice can export her plan and send to Bob
- ✅ Bob can import and see all team member names correctly
- ✅ Team mismatch is detected and handled gracefully
- ✅ Exported files are human-readable JSON

**Long-term (v2.0)**:
- ✅ Sr Manager can load 5 team plans simultaneously
- ✅ Multi-team aggregation works without format migration
- ✅ Existing 1.0 plans load in 2.0 without conversion

### Metrics

- **Component re-renders**: Measure before/after M9 using browser DevTools
  - Expected: Team changes should NOT trigger allocation grid re-renders
  - Expected: Allocation changes should NOT trigger roadmap view re-renders

- **Export file size**: ~10-20 KB for typical 10-person team plan (acceptable)

- **Import success rate**: 100% for valid 1.0 exports (comprehensive validation)

---

## References

- **Dioxus Documentation**: Signals and reactivity (https://dioxuslabs.com/learn/0.6/reference/signals)
- **Roadmap Discussion**: State refactor rationale (conversation logs)
- **Post-1.0 Vision**: Multi-team aggregation design (roadmap M2.0)
- **WCAG 2.1 AA Guidelines**: Informed "no toasts" decision (accessibility)

---

## Revision History

- **2025-01-17**: Initial draft (proposal status)
- **2025-01-23**: Finalized after M9 spike - Accepted status
  - Confirmed `dioxus-sdk` storage with abstraction layer
  - JSON serialization for v1.0, binary format may be added if implementation is simple
  - Storage abstraction enables web/desktop parity and easy library pivoting
- **2025-11-25**: Updated after M12.5 implementation - Renumbered to ADR-005
  - Changed from two-tier to three-tier persistence (added localStorage for PlanState)
  - Replaced `dioxus-sdk` with direct `web_sys::Storage` (WASM) and `dirs` crate (native)
  - Added Settings Modal UI section documenting configuration interface
  - Updated code examples to match actual implementation
  - Documented smart defaults (next quarter based on current date)
- **Future**: Update after M13 import/export implementation

---

## Appendix: Example Export File

```json
{
  "version": "1.0",
  "metadata": {
    "version": "1.0",
    "created_at": "2025-01-15T10:30:00Z",
    "modified_at": "2025-01-20T14:45:00Z"
  },
  "team_name": "Backend Team",
  "team_members": [
    {
      "id": "a1b2c3d4-...",
      "name": "Alice Kim",
      "role": "Engineering",
      "capacity": 12.0
    },
    {
      "id": "e5f6g7h8-...",
      "name": "Bob Martinez",
      "role": "Engineering",
      "capacity": 12.0
    }
  ],
  "quarter_name": "Q1 2025",
  "quarter_start_date": "2025-01-06",
  "num_weeks": 13,
  "roadmap_projects": [
    {
      "id": "...",
      "name": "Q1 Platform Improvements",
      "engineering_estimate": 24.0,
      "science_estimate": 8.0,
      "start_date": "2025-01-06",
      "launch_date": "2025-03-31",
      "color": "Blue"
    }
  ],
  "technical_projects": [
    {
      "id": "...",
      "name": "Payment API",
      "roadmap_project_id": "...",
      "estimated_weeks": 8.0,
      "start_date": "2025-01-06",
      "expected_completion": "2025-02-28"
    }
  ],
  "allocations": [
    {
      "team_member_id": "a1b2c3d4-...",
      "week_start_date": "2025-01-06",
      "assignments": [
        {
          "technical_project_id": "...",
          "percentage": 100.0
        }
      ]
    }
  ]
}
```

**Note**: This format is self-contained (includes full team context) and supports future multi-team aggregation without breaking changes.
