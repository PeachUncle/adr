# ADR 0003: Hierarchical Tide Context System

Date: 2025-08-14

## Status

Draft

## Context

The Tides application currently treats daily, weekly, monthly, and project tides as separate, independent entities. Users must manually create and manage different tide types, switching between contexts to track their workflows at different time scales.

### Current Implementation Analysis

**Current Tide Architecture**:

```typescript
// Independent tide entities
interface Tide {
  id: string;
  name: string;
  flow_type: "daily" | "weekly" | "monthly" | "project";
  status: "active" | "completed" | "paused";
  flow_sessions: FlowSession[];
  energy_updates: EnergyUpdate[];
  task_links: TaskLink[];
}

// Users must explicitly create each tide type
const dailyTide = await mcpClient.callTool("tide_create", {
  name: "Today's Focus",
  flow_type: "daily",
});

const weeklyTide = await mcpClient.callTool("tide_create", {
  name: "This Week's Goals",
  flow_type: "weekly",
});
```

**User Experience Problems**:

1. **Cognitive Overhead**: Users must decide which tide context to use before starting work
2. **Manual Management**: Requires explicit creation and switching between tide types
3. **Data Fragmentation**: Flow sessions exist in isolation within single tide contexts
4. **Limited Insights**: No automatic aggregation of daily flows into weekly/monthly views
5. **Workflow Interruption**: Must stop and choose context instead of just starting to work

### The Decision Question

Should we implement a hierarchical tide system where:

1. **Single Entry Point**: Users start flows that automatically contribute to daily, weekly, and monthly contexts
2. **Automatic Context Creation**: System auto-generates daily/weekly/monthly tides as needed
3. **Hierarchical Relationships**: Daily tides roll up into weekly tides, weekly into monthly
4. **Context Switching**: Users can toggle between time-scale views of the same underlying data
5. **Unified Insights**: Analytics span across all time horizons automatically

Alternative approaches considered:

- **Status Quo**: Keep independent tide system
- **Manual Linking**: Add UI for users to link related tides
- **View-Only Aggregation**: Aggregate data in reporting without changing storage model

## Decision

We will **implement a hierarchical tide context system** with automatic flow aggregation:

1. **Automatic Tide Creation**: System auto-creates daily/weekly/monthly tides based on current date
2. **Flow Distribution**: When users start a flow, it contributes to all relevant time contexts
3. **Hierarchical Storage**: Database schema supports parent-child relationships between tides
4. **Context Views**: UI allows seamless switching between daily/weekly/monthly perspectives
5. **Unified Analytics**: Insights and reports work across all time scales

**Architecture**:

```typescript
// Enhanced tide with hierarchical relationships
interface Tide {
  id: string;
  name: string;
  flow_type: "daily" | "weekly" | "monthly" | "project";
  parent_tide_id?: string; // Links to parent tide
  child_tide_ids: string[]; // Links to child tides
  date_range: {
    start: string; // ISO date
    end: string; // ISO date
  };
  auto_created: boolean; // System vs user-created
  status: "active" | "completed" | "paused";
  flow_sessions: FlowSession[];
  energy_updates: EnergyUpdate[];
  task_links: TaskLink[];
}

// New MCP tool behavior
const result = await mcpClient.callTool("tide_flow", {
  intensity: "moderate",
  duration: 25,
  work_context: "Morning standup prep",
});

// Automatically contributes to:
// - Today's daily tide (auto-created if needed)
// - This week's weekly tide (auto-created if needed)
// - This month's monthly tide (auto-created if needed)
```

**Rationale**: Users want to focus on work, not tide management. A hierarchical system provides the benefits of multi-scale tracking without cognitive overhead, enabling natural journaling workflows while automatically building rich temporal context.

## Consequences

### Positive

1. **Seamless User Experience**
   - Single "start flow" action contributes to all relevant contexts
   - No decisions required about tide type before starting work
   - Natural journaling workflow - just start writing/working
   - Automatic context creation removes setup friction

2. **Rich Multi-Scale Insights**
   - Daily patterns: energy flows throughout the day
   - Weekly trends: productive days vs challenging periods
   - Monthly views: long-term productivity and growth patterns
   - Cross-scale analysis: how daily energy affects weekly outcomes

3. **Unified Data Model**
   - All flows connected across time scales
   - Consistent analytics regardless of viewing context
   - Rich relationship queries between temporal contexts
   - Simplified client-side state management

4. **Enhanced Analytics Capabilities**
   - "Show me how my morning energy affects weekly productivity"
   - "Compare this month's flow patterns to last month"
   - "What weekly rhythms lead to the most successful months?"
   - Cross-temporal correlation analysis

### Negative

1. **Implementation Complexity**
   - Auto-tide creation logic for different time boundaries
   - Parent-child relationship management in database
   - Complex sync logic for hierarchical updates
   - Date-range boundary handling (weeks, months, timezones)

2. **Data Storage Overhead**
   - Additional foreign key relationships
   - Potential data duplication in hierarchical views
   - More complex database queries for aggregations
   - Cache invalidation across multiple contexts

3. **Migration Challenges**
   - Existing independent tides need relationship retrofitting
   - Complex data migration from flat to hierarchical model
   - Backwards compatibility during transition period

### Mitigations

1. **For Implementation Complexity**:
   - Use well-defined date boundary logic (Monday-Sunday weeks, calendar months)
   - Implement atomic operations for multi-tide updates
   - Create comprehensive test suite for edge cases (year boundaries, timezones)
   - Build helper functions for common hierarchical operations

2. **For Storage Overhead**:
   - Use database views for complex aggregations
   - Implement intelligent caching at application level
   - Add periodic cleanup of orphaned relationships
   - Monitor query performance and optimize indexes

3. **For Migration Challenges**:
   - Phase migration over multiple releases
   - Maintain backwards compatibility during transition
   - Provide manual tools for data relationship repair
   - Allow opt-in to new system before full migration

## Implementation Notes

### Database Schema Changes

```sql
-- Updated tides table with hierarchical support
ALTER TABLE tides ADD COLUMN parent_tide_id TEXT REFERENCES tides(id);
ALTER TABLE tides ADD COLUMN date_start TEXT; -- ISO date
ALTER TABLE tides ADD COLUMN date_end TEXT;   -- ISO date
ALTER TABLE tides ADD COLUMN auto_created BOOLEAN DEFAULT FALSE;

-- Indexes for hierarchical queries
CREATE INDEX idx_tides_parent ON tides(parent_tide_id);
CREATE INDEX idx_tides_date_range ON tides(date_start, date_end);
CREATE INDEX idx_tides_auto_created ON tides(auto_created, flow_type);

-- Composite index for time-based queries
CREATE INDEX idx_tides_user_date_type ON tides(user_id, date_start, flow_type);
```

### Enhanced MCP Tools

```typescript
// Updated tide_flow tool
server.registerTool("tide_flow", {
  // ... existing config
  async handler(args) {
    const today = new Date().toISOString().split("T")[0];
    const flowSession = await createFlowSession(args);

    // Auto-create and link to hierarchical tides
    const dailyTide = await getOrCreateDailyTide(today);
    const weeklyTide = await getOrCreateWeeklyTide(today);
    const monthlyTide = await getOrCreateMonthlyTide(today);

    // Add flow session to all relevant tides
    await Promise.all([
      addFlowToTide(dailyTide.id, flowSession),
      addFlowToTide(weeklyTide.id, flowSession),
      addFlowToTide(monthlyTide.id, flowSession),
    ]);

    return {
      session: flowSession,
      contexts: {
        daily: dailyTide,
        weekly: weeklyTide,
        monthly: monthlyTide,
      },
    };
  },
});

// New context switching tool
server.registerTool("tide_switch_context", {
  title: "Switch Tide Context",
  description:
    "Switch between daily, weekly, monthly views of the same underlying data",
  schema: {
    type: "object",
    properties: {
      context: {
        type: "string",
        enum: ["daily", "weekly", "monthly"],
        description: "Time context to switch to",
      },
      date: {
        type: "string",
        description: "ISO date for context (defaults to today)",
      },
    },
    required: ["context"],
  },
  async handler({ context, date = new Date().toISOString().split("T")[0] }) {
    return await getTideByContext(context, date);
  },
});
```

### Mobile App Changes

```typescript
// Enhanced MCPContext with hierarchical support
interface MCPContextState {
  currentContext: "daily" | "weekly" | "monthly";
  activeTides: {
    daily?: Tide;
    weekly?: Tide;
    monthly?: Tide;
  };
  selectedDate: string; // ISO date
}

// Simplified flow starting
const startFlow = async (
  intensity: string,
  duration: number,
  context?: string
) => {
  const result = await mcpClient.callTool("tide_flow", {
    intensity,
    duration,
    work_context: context,
  });

  // Automatically updates all relevant tide contexts
  setActiveTides(result.contexts);
  return result.session;
};

// Context switching
const switchContext = async (newContext: "daily" | "weekly" | "monthly") => {
  const tide = await mcpClient.callTool("tide_switch_context", {
    context: newContext,
    date: selectedDate,
  });

  setCurrentContext(newContext);
  setActiveTide(newContext, tide);
};
```

### Auto-Creation Logic

```typescript
// Daily tide creation
async function getOrCreateDailyTide(date: string): Promise<Tide> {
  const existing = await findTideByDateAndType(date, "daily");
  if (existing) return existing;

  return await createTide({
    name: `Daily Focus - ${formatDate(date)}`,
    flow_type: "daily",
    date_start: date,
    date_end: date,
    auto_created: true,
  });
}

// Weekly tide creation (Monday-Sunday)
async function getOrCreateWeeklyTide(date: string): Promise<Tide> {
  const weekStart = getWeekStart(date); // Monday
  const weekEnd = getWeekEnd(date); // Sunday

  const existing = await findTideByDateRange(weekStart, weekEnd, "weekly");
  if (existing) return existing;

  const weeklyTide = await createTide({
    name: `Week of ${formatDate(weekStart)}`,
    flow_type: "weekly",
    date_start: weekStart,
    date_end: weekEnd,
    auto_created: true,
  });

  // Link existing daily tides as children
  await linkExistingDailyTides(weeklyTide, weekStart, weekEnd);
  return weeklyTide;
}
```

## Related Decisions

- Tide data storage format (see ADR 0002) - relational schema supports hierarchical relationships
- MCP session storage strategy (see ADR 0001) - cache hierarchical data for performance
- Analytics and reporting architecture - multi-scale insights require cross-tide queries

## References

- Current tide implementation: `apps/server/src/storage/index.ts`
- Current MCP tools: `apps/server/src/handlers/tools.ts`
- User experience flows: `docs/ux/flows/app-entry.md`
- Mobile context management: `apps/mobile/src/context/MCPContext.tsx`
- Database schema: `apps/server/src/db/schema.sql`
