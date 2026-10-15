# ADR-001: Flexible Barrel Configuration

## Status
**Implemented** - 2025-12-01

Database entities, EF configurations, and backend services updated. Migration created: `FlexibleBarrelConfiguration`.

## Context

The current data model assumes a fixed barrel configuration based on the TumblerModel seed data. However, real-world usage reveals more complex scenarios:

1. **Variable barrel setups**: A Lortone 33B with 6lb motor capacity could have 2×3lb barrels OR 1×6lb barrel OR 3×3lb + 1×6lb (with only some running at once)
2. **DIY tumblers**: Custom-built tumblers with 50-100lb capacity running multiple barrels simultaneously
3. **Multi-barrel stages**: A single stage run might use multiple barrels on the same tumbler (e.g., 4×3lb barrels all grinding at once)
4. **Stage planning**: Users want to pre-configure future stages while current ones are running

## Decision

### 1. Motor Capacity Model

**TumblerModel (seed data)**
- Add `MotorCapacityLbs` column (the max total weight the motor can handle)
- Keep `DefaultBarrelCount` and `DefaultCapacityLbs` as suggestions only

**Tumbler (user instance)**
- Add `MotorCapacityLbs` column (nullable - uses model default if not set)
- Motor capacity is LOCKED if `TumblerModel.DefaultCapacityLbs > 0`
- Motor capacity is EDITABLE if model is: Generic, Other, DIY, or MJR Tumblers
- MJR Tumblers have a max limit of 50lbs

### 2. Barrel Configuration

**Barrel entity changes:**
- `CapacityLbs` is user-defined when creating the barrel
- Each barrel's capacity must be ≤ tumbler's motor capacity
- Capacity is **immutable** after creation (delete and recreate to change)
- Nickname remains user-editable

**Validation rules:**
- Single barrel capacity ≤ motor capacity (hard block)
- Sum of active barrels > motor capacity (soft warning only)

### 3. Stage-Barrel Relationship

**Current model:**
```
StageRun → BarrelId (single barrel)
```

**New model:**
```
StageRun → StageRunBarrels (join table) → Barrel (many-to-many)
```

A single StageRun can use multiple barrels simultaneously (all spinning on the same tumbler).

### 4. Stage Status Enhancement

**Current statuses:**
- Active (0)
- Completed (1)

**New statuses:**
- Planned (0) - Stage configured but not started
- Active (1) - Stage currently running
- Completed (2) - Stage finished

### 5. Barrel "Mounted" State

Derived property (not stored):
```csharp
Barrel.IsMounted = EXISTS(StageRunBarrel WHERE BarrelId = this.Id
                          AND StageRun.Status = Active)
```

- **Planned** stages do NOT mount barrels (same barrel can be planned for multiple future stages)
- **Active** stages DO mount barrels (barrel is "in use")
- **Completed** stages release barrels

### 6. Water Amount Tracking

**Current model:**
- `WaterLevel` enum (JustCovering, Halfway, ThreeQuarters, Full) for quick qualitative selection

**Enhancement:**
- Keep `WaterLevel` enum for quick selection
- Add `WaterAmountMl` (int, nullable) for precise measurement
- Stored in milliliters, displayed as ml (Metric) or fl oz (Imperial) per user preference

```csharp
// StageRun - add column
public int? WaterAmountMl { get; set; } // Precise measurement in milliliters
```

This allows users to optionally record exact water amounts while still having the quick enum selection.

### 7. Capacity Warning Logic

Show warning banner when:
```sql
SELECT SUM(b.CapacityLbs)
FROM StageRunBarrels srb
JOIN Barrels b ON srb.BarrelId = b.Id
JOIN StageRuns sr ON srb.StageRunId = sr.Id
WHERE sr.Status = 'Active'
  AND b.TumblerId = @TumblerId
> Tumbler.MotorCapacityLbs
```

This is a **soft warning** only - users can proceed (they might be running barrels on different motor units).

## Schema Changes

### New/Modified Entities

```csharp
// TumblerModel - add column
public decimal MotorCapacityLbs { get; set; }

// Tumbler - add column
public decimal? MotorCapacityLbs { get; set; } // Override if allowed

// StageRunStatus - update enum
public enum StageRunStatus
{
    Planned = 0,
    Active = 1,
    Completed = 2
}

// StageRun - change relationship
// Remove: public Guid BarrelId { get; set; }
// Add: public virtual ICollection<StageRunBarrel> StageRunBarrels { get; set; }

// New join table
public class StageRunBarrel
{
    public Guid StageRunId { get; set; }
    public Guid BarrelId { get; set; }

    public virtual StageRun StageRun { get; set; }
    public virtual Barrel Barrel { get; set; }
}
```

### Migration Notes

Since there is no production data yet, we can drop and recreate tables to reorganize columns logically.

**Tables to modify (reorganize columns while we're touching them):**

| Table | Changes |
|-------|---------|
| `tumbler_models` | Add `MotorCapacityLbs`, reorganize columns |
| `tumblers` | Add `MotorCapacityLbs`, reorganize columns |
| `barrels` | Reorganize columns (group FKs, capacity, metadata) |
| `stage_runs` | Remove `BarrelId`, add `WaterAmountMl`, reorganize into logical groups |
| `stage_run_barrels` | NEW join table |

**Column organization strategy:**
1. Foreign keys first
2. Primary identifiers/names
3. Core data fields (grouped by purpose)
4. Timestamps/audit fields last

**StageRun column groups:**
- FKs: `CycleId`
- Basic info: `StageName`, `Status`
- Timing: `StartDateTime`, `DurationDays`, `DurationHours`, `EndDateTime`
- Reminders: `ReminderEnabled`, `RemindAfterDays`, `RemindAtEndOfStage`, `DateReminderSent`
- Load/setup: `LoadWeightBeforeGrams`, `LoadWeightAfterGrams`, `BarrelRpm`, `IsRpmEstimated`, `FillLevelPercent`, `WaterLevel`, `WaterAmountMl`
- Results: `ResultRating`, `ResultShapeRounding`, `ResultScratchLevel`, `ResultPitting`, `ResultShine`
- Issues: `IssueScratches`, `IssueChips`, `IssueUnderRounded`, `IssueContamination`
- Notes: `LessonsLearned`, `NextAction`, `Notes`

## Examples

### Example 1: Standard User
```
Tumbler: "My Lortone 33B" (Model: Lortone 33B, 6lb motor capacity - LOCKED)
├── Barrel: "Big Blue" (6lb)
├── Barrel: "Left Side" (3lb)
└── Barrel: "Right Side" (3lb)

Cycle: "Oregon Agates"
├── Stage 1 (60 grit): Active, Barrels: ["Big Blue"]
├── Stage 2 (220 grit): Planned, Barrels: ["Left Side", "Right Side"]
└── Stage 3 (polish): Planned, Barrels: ["Big Blue"]
```

### Example 2: DIY Power User
```
Tumbler: "Beast Mode" (Model: DIY, 100lb motor capacity - USER SET)
├── Barrel: "A" (3lb)
├── Barrel: "B" (3lb)
├── Barrel: "C" (6lb)
├── Barrel: "D" (6lb)
└── Barrel: "E" (12lb)

Cycle: "Mixed Agates"
└── Stage 1 (60 grit): Active, Barrels: ["A", "B", "C", "D", "E"] (30lb total)
    └── Motor capacity warning: NO (30lb < 100lb)

Cycle: "Beach Jasper"
└── Stage 1 (60 grit): Active, Barrels: ["A", "B"] (6lb total, same tumbler)
    └── Combined with above: 36lb total, still under 100lb
```

### Example 3: Cross-Cycle Parallel Work
```
Cycle: "Oregon Agates" - Stage 2 Active using "Left 3lb"
Cycle: "Ocean Jasper" - Stage 1 Active using "Right 3lb"

Both stages running simultaneously on same tumbler = OK
Total: 6lb (within 6lb motor capacity)
```

## Future Considerations

### Cycle Merge Feature (Not in scope of this ADR)
- Allow merging Cycle A specimens into Cycle B
- Cycle A marked as "Merged into {Cycle B name}"
- History preserved, merged cycle becomes read-only
- Will require separate ADR when prioritized

## Implementation Tasks

| Task | Description | Effort | Status |
|------|-------------|--------|--------|
| D1 | Add `MotorCapacityLbs` to TumblerModel entity + seed data | Low | ✅ |
| D2 | Add `MotorCapacityLbs` to Tumbler entity | Low | ✅ |
| D3 | Create `StageRunBarrel` join table entity | Low | ✅ |
| D4 | Update `StageRunStatus` enum with Planned status | Low | ✅ |
| D5 | Add `WaterAmountMl` to StageRun entity | Low | ✅ |
| D6 | Reorganize StageRun columns (drop/recreate - no data yet) | Low | ✅ |
| D7 | Create EF migration for all schema changes | Medium | ✅ |
| B1 | Update TumblerService for motor capacity logic | Low | ✅ |
| B2 | Update barrel creation validation (capacity ≤ motor) | Low | ✅ |
| B3 | Update StageRun service for multi-barrel support | Medium | ✅ |
| B4 | Add mounted status derivation logic | Low | ✅ |
| B5 | Add capacity warning calculation | Low | ✅ |
| F1 | Update Tumbler edit UI (motor capacity for DIY/Generic) | Medium | ✅ |
| F2 | Update Barrel management UI (add/remove/view) | Medium | ✅ |
| F3 | Update Stage creation UI (multi-barrel picker) | Medium | ✅ |
| F4 | Add capacity warning banner component | Low | ✅ |
| F5 | Add "mounted" indicator to barrel list | Low | ✅ |
| F6 | Add water amount input to Stage form (alongside WaterLevel) | Low | ✅ |

**Estimated Total Effort**: 3-4 hours

## Consequences

### Positive
- Supports real-world tumbler configurations
- Enables DIY/custom tumbler users
- Pre-planning stages improves UX
- Multi-barrel stages match actual usage patterns

### Negative
- Schema migration required (medium complexity)
- UI changes needed in multiple places
- Slightly more complex barrel selection workflow

### Neutral
- Existing single-barrel users unaffected (just select one barrel)
- Warning system is advisory only - respects user knowledge
