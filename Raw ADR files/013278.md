# ADR-001: Enhanced Agent Progress Tracking System

Date: 2025-11-03
Status: Proposed
Architect: Kai

## Context

The Orchestra Plugin currently implements basic progress tracking through TodoWrite integration, but faces several limitations:

### Current Implementation

**Components:**
- `progress-tracker-display.sh` - Basic text-based display hook
- `.orchestra/cache/progress.json` - Minimal progress data storage
- `post_code_write.sh` - PostToolUse hook triggered after TodoWrite
- `hooks.json` - Hook registration (PostToolUse:TodoWrite matcher)

**Current Schema (progress.json):**
```json
{
  "todos": [
    {
      "id": "string",
      "content": "string",
      "activeForm": "string",
      "status": "pending|in_progress|completed",
      "parentId": "string|null"
    }
  ]
}
```

### Problems

1. **Visibility**: Progress information scrolls out of view in chat, becoming invisible
2. **Limited Metadata**: No tracking of agent assignment, execution time, or token usage
3. **No Agent Context**: Cannot identify which agent is executing which task
4. **Poor Scannability**: Plain text output lacks visual hierarchy and prominence
5. **No Concurrent Agent Support**: Cannot track multiple agents working simultaneously

### Requirements

- Real-time agent progress display with indicator-style formatting
- Track which agents are active and how many are running concurrently
- Detailed progress metadata (agent name, task, execution time, progress rate)
- Minimal user cognitive overhead
- Integration with existing TodoWrite tool and hook system

### Constraints

1. **No Claude Code API for Custom UI**: Claude Code does not provide APIs for persistent status displays or custom UI overlays
2. **Hook Execution Model**: Hooks run synchronously after tool execution; cannot inject persistent visual elements
3. **Agent Context Detection**: No built-in environment variable exposes current agent context (CLAUDE_AGENT_NAME, etc.)
4. **File I/O Performance**: Each hook invocation reads/writes JSON files; must minimize I/O overhead
5. **Token Budget**: Target 15-20K tokens for analysis and design

## Decision

Implement a **hybrid enhanced chat display + external monitoring** approach:

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                       TodoWrite Tool                             │
│                  (Invoked by Agent)                              │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       │ PostToolUse Hook Trigger
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│              post_code_write.sh (Hook Entry)                     │
│  1. Extract agent context from tool parameters                  │
│  2. Capture timestamp                                            │
│  3. Call progress-tracker-update.sh                              │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│         progress-tracker-update.sh (Logic Layer)                │
│  1. Parse TodoWrite parameters (todos array)                    │
│  2. Extract agent from activeForm or heuristics                 │
│  3. Update progress.json with atomic file operations            │
│  4. Maintain activeAgents list                                  │
│  5. Calculate progress metrics                                  │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       │ Update Schema
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│              .orchestra/cache/progress.json                      │
│  Enhanced schema with agent, timing, progress metadata          │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       │ Read & Display
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│       progress-tracker-display.sh (Display Layer)               │
│  1. Format enhanced progress display (chat injection)           │
│  2. Generate status bar summary                                 │
│  3. Export to .orchestra/cache/progress-status.txt              │
│  4. Colorized, structured terminal output                       │
└──────────────────────┬──────────────────────────────────────────┘
                       │
            ┌──────────┴──────────┐
            │                     │
            ▼                     ▼
   ┌─────────────────┐   ┌──────────────────────┐
   │  Chat Display   │   │  External Monitor    │
   │  (visible once) │   │  (tail -f / watch)   │
   └─────────────────┘   └──────────────────────┘
```

### Enhanced Schema Design

```json
{
  "todos": [
    {
      "id": "string",
      "content": "string",
      "activeForm": "string",
      "status": "pending|in_progress|completed",
      "parentId": "string|null",

      // NEW FIELDS
      "agent": "string",                    // "Skye", "Nova", "Kai", etc.
      "startTime": "number",                // Unix timestamp (milliseconds)
      "lastUpdateTime": "number",           // Unix timestamp
      "estimatedDuration": "number|null",   // Estimated milliseconds
      "currentStep": "number|null",         // Step number within task
      "totalSteps": "number|null",          // Total steps if known
      "tags": ["string"]                    // ["backend", "database", "migration"]
    }
  ],
  "metadata": {
    "sessionStartTime": "number",           // Unix timestamp
    "lastUpdateTime": "number",             // Unix timestamp
    "activeAgents": ["string"],             // ["Skye", "Leo"]
    "totalTokensEstimated": "number",       // Estimated tokens consumed
    "completionRate": "number",             // 0-100 percentage
    "totalTasks": "number",
    "completedTasks": "number",
    "inProgressTasks": "number",
    "pendingTasks": "number"
  },
  "history": [
    {
      "timestamp": "number",
      "event": "task_started|task_completed|agent_assigned",
      "taskId": "string",
      "agent": "string|null",
      "details": "string|null"
    }
  ]
}
```

**Field Rationale:**
- `agent`: Identifies task ownership; enables concurrent agent tracking
- `startTime` / `lastUpdateTime`: Enables duration calculation, stale task detection
- `estimatedDuration`: Allows progress bar rendering (time-based)
- `currentStep` / `totalSteps`: Enables step-based progress indicators
- `tags`: Facilitates filtering and grouping by concern (frontend/backend/infra)
- `history`: Audit trail for debugging and analytics

### Agent Context Detection Strategy

**Problem**: TodoWrite tool does not pass agent context in parameters.

**Solution - Multi-layered Heuristic Detection:**

1. **Parse activeForm field** (highest confidence)
   - Pattern: "Kai is designing...", "Skye implementing..."
   - Extract agent name from present continuous verb phrase

2. **Analyze content field** (medium confidence)
   - Pattern: "Design API schema (Kai)", "[Nova] Build dashboard"
   - Look for agent name in parentheses or brackets

3. **Session-based inference** (low confidence)
   - Track last UserPromptSubmit agent routing suggestion
   - Persist "current agent" in progress.json metadata
   - Fallback: Assign to "Unknown"

4. **Future enhancement**: Request TodoWrite tool to accept agent parameter

**Implementation:**
```bash
# Agent detection function (pseudocode)
detect_agent() {
    local active_form="$1"
    local content="$2"

    # Strategy 1: Parse activeForm
    if [[ "$active_form" =~ ^(Skye|Nova|Leo|Kai|Mina|Iris|Eden|Theo|Alex|Blake|Finn|Riley)[[:space:]] ]]; then
        echo "${BASH_REMATCH[1]}"
        return
    fi

    # Strategy 2: Parse content
    if [[ "$content" =~ \(([A-Z][a-z]+)\) ]] || [[ "$content" =~ \[([A-Z][a-z]+)\] ]]; then
        local candidate="${BASH_REMATCH[1]}"
        if is_valid_agent "$candidate"; then
            echo "$candidate"
            return
        fi
    fi

    # Strategy 3: Use last known agent
    local last_agent=$(jq -r '.metadata.currentAgent // "Unknown"' progress.json)
    echo "$last_agent"
}
```

### File Locking Strategy

**Problem**: Concurrent TodoWrite calls may corrupt progress.json.

**Solution - Advisory Lock with flock:**

```bash
# Atomic update wrapper
atomic_update_progress() {
    local lock_file="/tmp/orchestra-progress.lock"
    local progress_file=".orchestra/cache/progress.json"

    # Acquire exclusive lock (wait up to 5 seconds)
    (
        flock -w 5 200 || {
            echo "ERROR: Could not acquire progress.json lock" >&2
            return 1
        }

        # Critical section: read, modify, write
        local temp_file=$(mktemp)
        jq --arg agent "$AGENT" \
           --arg task_id "$TASK_ID" \
           --argjson timestamp "$TIMESTAMP" \
           '(.todos[] | select(.id == $task_id)) |= (. + {
               agent: $agent,
               lastUpdateTime: $timestamp
           })' "$progress_file" > "$temp_file"

        mv "$temp_file" "$progress_file"

    ) 200>"$lock_file"
}
```

## Alternatives Considered

### Option A: Enhanced Chat Display (SELECTED)

**Description**: Improve current hook-based display with rich formatting.

**Pros:**
- No client-side implementation required
- Works within existing hook framework
- Immediate implementation path
- Leverages jq for formatting

**Cons:**
- Still scrolls out of view
- No persistent display
- Limited visual fidelity (terminal formatting only)

**Implementation Complexity**: LOW (2-3 hours)

**User Experience Score**: 6/10
- Visibility: 5/10 (scrolls away)
- Information Density: 8/10 (rich metadata)
- Real-time Updates: 7/10 (on each TodoWrite)

**Recommended as primary solution with external monitoring as supplement.**

---

### Option B: Status Line Integration

**Description**: Update Claude Code status line via `.claude/settings.json`.

**Investigation Results:**
- Claude Code does NOT support dynamic status line updates
- `statusline` field is static, evaluated once at session start
- No mechanism to re-evaluate statusline from hooks

**Verdict**: NOT FEASIBLE with current Claude Code capabilities.

---

### Option C: External File Monitoring

**Description**: Generate `.orchestra/cache/progress-status.txt`, user monitors with `tail -f`.

**Pros:**
- Always visible (separate terminal)
- Real-time updates
- Full terminal formatting (colors, box drawing)
- Works alongside chat display

**Cons:**
- Requires user to run monitoring command
- Extra terminal window needed
- Manual setup friction

**Implementation Complexity**: LOW (1 hour additional)

**User Experience Score**: 7/10
- Visibility: 9/10 (always visible)
- Setup Friction: 4/10 (manual command required)
- Real-time Updates: 9/10 (inotify-based)

**Recommended as OPTIONAL supplement.**

**User Command:**
```bash
# In separate terminal
watch -n 1 cat .orchestra/cache/progress-status.txt
# OR
tail -f .orchestra/cache/progress-status.txt
```

---

### Option D: Hook Output Capture (Browser Extension)

**Description**: Special marker format in hook stdout, captured by hypothetical browser extension.

**Investigation Results:**
- Claude Code CLI is terminal-based, not browser-based
- No extension API available
- Would require forking Claude Code

**Verdict**: NOT FEASIBLE without Claude Code upstream changes.

---

### Comparison Matrix

| Option | Visibility | Setup | Complexity | Feasibility | UX Score |
|--------|-----------|-------|------------|-------------|----------|
| A: Enhanced Chat | Low | None | Low | High | 6/10 |
| B: Status Line | High | None | Low | **NOT POSSIBLE** | N/A |
| C: External Monitor | High | Manual | Low | High | 7/10 |
| D: Browser Extension | High | High | Very High | **NOT POSSIBLE** | N/A |

**Decision**: Implement A + C hybrid (Enhanced Chat + Optional External Monitor).

## Implementation Plan

### Phase 1: Enhanced Schema & Update Logic (Core)

**Files to Create:**
- `hooks/progress-tracker-update.sh` - Core update logic with locking
- `hooks/lib/progress-utils.sh` - Shared utility functions (agent detection, formatting)

**Files to Modify:**
- `hooks/post_code_write.sh` - Call update script before display
- `.orchestra/cache/progress.json` - Migrate to new schema

**Key Functions:**
```bash
# progress-tracker-update.sh
- detect_agent_from_todo()
- atomic_update_progress()
- calculate_progress_metrics()
- update_active_agents_list()

# progress-utils.sh
- is_valid_agent()
- format_duration()
- format_progress_bar()
- sanitize_json_field()
```

**Testing:**
- Unit tests for agent detection (shellspec or bats)
- Concurrent update test (spawn 5 parallel TodoWrite simulations)
- Schema validation test (jq schema validation)

### Phase 2: Enhanced Display Rendering

**Files to Modify:**
- `hooks/progress-tracker-display.sh` - Rewrite with rich formatting

**Display Format:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 ORCHESTRA PROGRESS                Session: 1h 23m  |  75% Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👥 Active Agents (3)
   😐 Skye    ⚡ Implementing authentication middleware      [▓▓▓▓▓▓▓░░░] 70%  (3m 42s)
   😄 Nova    🎨 Designing dashboard UI components          [▓▓▓▓▓░░░░░] 50%  (5m 12s)
   😌 Leo     🧪 Writing integration tests                  [▓▓▓▓▓▓▓▓░░] 80%  (2m 15s)

📋 Task Summary
   ✅ Completed: 8 tasks  (2h 14m total)
   ⚡ In Progress: 3 tasks  (11m elapsed)
   ⏳ Pending: 4 tasks

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Formatting Techniques:**
- ANSI color codes (green=completed, yellow=in_progress, gray=pending)
- Box drawing characters (━ ═ ▓ ░)
- Emoji agent identifiers (from .claude.json subagent_type)
- Progress bars with percentage
- Duration formatting (3m 42s, 1h 23m)

### Phase 3: External Monitoring Support (Optional)

**Files to Create:**
- `hooks/progress-tracker-export.sh` - Generate progress-status.txt
- `.orchestra/cache/progress-status.txt` - Formatted status file

**User Documentation:**
```markdown
## Real-time Progress Monitoring

For persistent progress visibility, run in a separate terminal:

### Option 1: Watch (refreshes every second)
watch -n 1 cat .orchestra/cache/progress-status.txt

### Option 2: Tail (updates on write)
tail -f .orchestra/cache/progress-status.txt

### Option 3: iTerm2 Status Bar (macOS)
# Add to iTerm2 status bar:
cat ~/.orchestra-current-project/progress-status.txt
```

### Phase 4: Session-Start Initialization

**Files to Modify:**
- `hooks/session-start.sh` - Initialize progress.json metadata

**Initialization Logic:**
```bash
# On session start
- Set metadata.sessionStartTime
- Clear metadata.activeAgents
- Archive previous session history to .orchestra/cache/history/YYYY-MM-DD-HHmmss.json
- Display monitoring setup instructions (if not dismissed)
```

### Performance Optimization

**Bottleneck Analysis:**

1. **jq Processing Overhead**
   - Current: Parse entire JSON on every TodoWrite (~10-50ms)
   - Solution: Cache parsed data in shell variables, batch updates
   - Impact: Reduce hook execution time from ~50ms to ~20ms

2. **File I/O**
   - Current: Read + Write progress.json on every update
   - Solution: Use tmpfs for progress.json (in-memory filesystem)
   - Impact: Reduce I/O latency by 80%
   ```bash
   # Setup (optional, in setup.sh)
   mkdir -p /tmp/orchestra-cache
   ln -s /tmp/orchestra-cache .orchestra/cache
   ```

3. **Lock Contention**
   - Current: flock waits up to 5 seconds
   - Solution: Optimistic locking with retry logic
   - Impact: Prevent hook timeout failures

**Target Performance:**
- Hook execution: < 100ms (p95)
- Lock wait time: < 50ms (p95)
- File size: < 50KB (100 tasks)

## Consequences

### Positive

- **Comprehensive Tracking**: Captures agent, timing, progress metadata
- **Concurrent Agent Support**: Accurately tracks multiple agents simultaneously
- **Extensible Schema**: Easily add new fields (token usage, step details)
- **Backward Compatible**: Existing progress.json files migrate gracefully
- **External Monitoring Option**: Users can choose persistent visibility
- **Audit Trail**: History array enables debugging and analytics

### Negative

- **Schema Migration Required**: Existing progress.json needs one-time upgrade
- **Increased Hook Complexity**: More logic in critical path (PostToolUse)
- **File I/O Overhead**: Additional reads/writes on every TodoWrite
- **Agent Detection Uncertainty**: Heuristic-based, may misidentify agent (10-20% error rate)
- **External Monitor Friction**: Users must manually set up separate terminal

### Neutral

- **No Persistent In-Chat Display**: Fundamental Claude Code limitation
- **jq Dependency**: Already required by Orchestra Plugin
- **Manual Monitoring Setup**: Power users benefit, casual users ignore

## Implementation Notes

### Migration Strategy

**Automatic Schema Migration (hooks/lib/progress-migrate.sh):**
```bash
migrate_progress_schema() {
    local progress_file=".orchestra/cache/progress.json"
    local schema_version=$(jq -r '.schemaVersion // "1.0"' "$progress_file")

    if [[ "$schema_version" == "1.0" ]]; then
        # Backup original
        cp "$progress_file" "$progress_file.v1.backup"

        # Add new fields with defaults
        jq '
            .schemaVersion = "2.0" |
            .metadata = {
                sessionStartTime: now,
                lastUpdateTime: now,
                activeAgents: [],
                totalTokensEstimated: 0
            } |
            .history = [] |
            .todos |= map(. + {
                agent: "Unknown",
                startTime: now,
                lastUpdateTime: now,
                estimatedDuration: null,
                currentStep: null,
                totalSteps: null,
                tags: []
            })
        ' "$progress_file" > "${progress_file}.tmp"

        mv "${progress_file}.tmp" "$progress_file"
        echo "✅ Migrated progress.json to schema v2.0"
    fi
}
```

### Error Handling

**Graceful Degradation:**
- If jq not available: Skip progress tracking, log warning
- If progress.json corrupted: Reinitialize with empty schema
- If lock timeout: Log event, skip update (don't block TodoWrite)
- If agent detection fails: Assign to "Unknown", continue

**Logging Strategy:**
```bash
LOG_FILE=".orchestra/logs/progress-tracker.log"

log_event() {
    local level="$1"  # INFO, WARN, ERROR
    local message="$2"
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] [$level] $message" >> "$LOG_FILE"
}
```

### Testing Strategy

**Unit Tests (shellspec):**
- Agent detection with various activeForm patterns
- Progress calculation edge cases (0 tasks, all completed)
- Duration formatting (seconds, minutes, hours)
- JSON escaping and sanitization

**Integration Tests:**
- TodoWrite → Hook → progress.json update flow
- Concurrent update simulation (10 parallel writes)
- Schema migration from v1.0 to v2.0
- Lock timeout and recovery

**Manual Testing Scenarios:**
1. Single agent, linear task execution
2. Multiple agents, concurrent tasks
3. Long-running session (1000+ TodoWrite calls)
4. Session restart and resume
5. External monitor display accuracy

## Security Considerations

- **File Permissions**: progress.json should be 0644 (readable by all, writable by owner)
- **Lock File**: /tmp/orchestra-progress.lock should be 0600 (owner only)
- **No Sensitive Data**: Avoid logging sensitive information (API keys, passwords) in progress data
- **Injection Prevention**: Sanitize all JSON string fields to prevent injection attacks

## Future Enhancements

### Post-MVP Improvements

1. **Token Usage Tracking**
   - Hook into Claude Code API (if exposed) to capture actual token counts
   - Display cumulative session tokens in metadata

2. **Agent Performance Analytics**
   - Track average task duration per agent
   - Identify bottleneck agents
   - Export to CSV for analysis

3. **Web Dashboard**
   - Optional HTTP server (port 3001) serving real-time progress
   - WebSocket updates for live refresh
   - D3.js visualizations (Gantt chart, agent timeline)

4. **IDE Integration**
   - VS Code extension with sidebar progress view
   - JetBrains plugin with tool window
   - Sublime Text status bar integration

5. **TodoWrite Tool Enhancement**
   - Submit PR to Claude Code to add `agent` parameter to TodoWrite
   - Eliminates heuristic detection uncertainty

### Stretch Goals

- **Slack Notifications**: Post progress updates to Slack channel
- **GitHub Issue Sync**: Link tasks to GitHub issues, update status
- **AI-Powered Estimation**: Use historical data to predict task durations
- **Voice Announcements**: Text-to-speech progress updates (ElevenLabs integration)

## References

- [Claude Code Hooks Documentation](https://docs.anthropic.com/claude-code/hooks)
- [TodoWrite Tool Specification](https://docs.anthropic.com/claude-code/tools/todo-write)
- [Orchestra Plugin Architecture](https://github.com/tstomtimes/orchestra)
- [ANSI Escape Codes Reference](https://en.wikipedia.org/wiki/ANSI_escape_code)
- [flock(1) Manual](https://man7.org/linux/man-pages/man1/flock.1.html)

## Appendix A: JSON Schema Definition

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Orchestra Progress Tracking Schema v2.0",
  "type": "object",
  "required": ["schemaVersion", "todos", "metadata"],
  "properties": {
    "schemaVersion": {
      "type": "string",
      "enum": ["2.0"],
      "description": "Schema version for migration tracking"
    },
    "todos": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "content", "activeForm", "status"],
        "properties": {
          "id": {
            "type": "string",
            "description": "Unique task identifier"
          },
          "content": {
            "type": "string",
            "description": "Task description (imperative form)"
          },
          "activeForm": {
            "type": "string",
            "description": "Task description (present continuous form)"
          },
          "status": {
            "type": "string",
            "enum": ["pending", "in_progress", "completed"],
            "description": "Task execution status"
          },
          "parentId": {
            "type": ["string", "null"],
            "description": "Parent task ID for subtasks"
          },
          "agent": {
            "type": "string",
            "description": "Agent assigned to task (Skye, Nova, Kai, etc.)"
          },
          "startTime": {
            "type": "number",
            "description": "Unix timestamp (milliseconds) when task started"
          },
          "lastUpdateTime": {
            "type": "number",
            "description": "Unix timestamp (milliseconds) of last update"
          },
          "estimatedDuration": {
            "type": ["number", "null"],
            "description": "Estimated task duration in milliseconds"
          },
          "currentStep": {
            "type": ["number", "null"],
            "description": "Current step number (1-indexed)"
          },
          "totalSteps": {
            "type": ["number", "null"],
            "description": "Total number of steps in task"
          },
          "tags": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "Task categorization tags"
          }
        }
      }
    },
    "metadata": {
      "type": "object",
      "required": [
        "sessionStartTime",
        "lastUpdateTime",
        "activeAgents",
        "totalTokensEstimated"
      ],
      "properties": {
        "sessionStartTime": {
          "type": "number",
          "description": "Unix timestamp (milliseconds) when session started"
        },
        "lastUpdateTime": {
          "type": "number",
          "description": "Unix timestamp (milliseconds) of last progress update"
        },
        "activeAgents": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "List of currently active agent names"
        },
        "totalTokensEstimated": {
          "type": "number",
          "description": "Estimated total tokens consumed in session"
        },
        "completionRate": {
          "type": "number",
          "minimum": 0,
          "maximum": 100,
          "description": "Percentage of tasks completed"
        },
        "totalTasks": {
          "type": "number",
          "description": "Total number of tasks"
        },
        "completedTasks": {
          "type": "number",
          "description": "Number of completed tasks"
        },
        "inProgressTasks": {
          "type": "number",
          "description": "Number of in-progress tasks"
        },
        "pendingTasks": {
          "type": "number",
          "description": "Number of pending tasks"
        },
        "currentAgent": {
          "type": "string",
          "description": "Last known active agent (fallback for detection)"
        }
      }
    },
    "history": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["timestamp", "event"],
        "properties": {
          "timestamp": {
            "type": "number",
            "description": "Unix timestamp (milliseconds) of event"
          },
          "event": {
            "type": "string",
            "enum": [
              "task_started",
              "task_completed",
              "task_failed",
              "agent_assigned",
              "session_started",
              "session_ended"
            ],
            "description": "Event type"
          },
          "taskId": {
            "type": ["string", "null"],
            "description": "Task ID associated with event"
          },
          "agent": {
            "type": ["string", "null"],
            "description": "Agent associated with event"
          },
          "details": {
            "type": ["string", "null"],
            "description": "Additional event details"
          }
        }
      }
    }
  }
}
```

## Appendix B: Display Format Examples

### Compact View (Default)
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 PROGRESS  |  3 agents  |  67% complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
😐 Skye   [▓▓▓▓▓▓▓░░░] 70%  Auth middleware
😄 Nova   [▓▓▓▓▓░░░░░] 50%  Dashboard UI
😌 Leo    [▓▓▓▓▓▓▓▓░░] 80%  Integration tests
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Detailed View (with --verbose flag)
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 ORCHESTRA PROGRESS TRACKER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Session: 1h 23m 45s  |  Started: 2025-11-03 14:30:00
Overall: [▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░] 67% (10/15 tasks)

👥 Active Agents (3)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

😐 Skye (Backend Implementation)
   Task: Implementing authentication middleware
   Progress: [▓▓▓▓▓▓▓░░░] 70%  (Step 7/10)
   Duration: 3m 42s  |  Est. remaining: 1m 35s
   Tags: backend, security, auth

😄 Nova (Frontend Development)
   Task: Designing dashboard UI components
   Progress: [▓▓▓▓▓░░░░░] 50%  (Step 5/10)
   Duration: 5m 12s  |  Est. remaining: 5m 12s
   Tags: frontend, ui, react

😌 Leo (Quality Assurance)
   Task: Writing integration tests
   Progress: [▓▓▓▓▓▓▓▓░░] 80%  (Step 8/10)
   Duration: 2m 15s  |  Est. remaining: 34s
   Tags: testing, qa, integration

📋 Task Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Completed (8 tasks)
   - Setup project structure (Alex, 12m)
   - Configure database schema (Skye, 8m)
   - Design API endpoints (Kai, 15m)
   - Implement user model (Skye, 6m)
   - Create login endpoint (Skye, 9m)
   - Write unit tests (Leo, 11m)
   - Setup CI pipeline (Theo, 18m)
   - Deploy staging (Theo, 7m)

⚡ In Progress (3 tasks)
   - Implementing authentication middleware (Skye)
   - Designing dashboard UI components (Nova)
   - Writing integration tests (Leo)

⏳ Pending (4 tasks)
   - Code review and refactoring
   - Update documentation
   - Performance optimization
   - Production deployment

📊 Performance Metrics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Avg Task Duration: 10m 45s
Total Time: 1h 23m 45s
Est. Completion: 14m 30s
Tokens Used: ~12,500 (estimated)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Last updated: 2025-11-03 15:53:45
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Appendix C: Hook Integration Pseudocode

### post_code_write.sh (Entry Point)
```bash
#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Source utility libraries
source "$SCRIPT_DIR/lib/progress-utils.sh"

# 1. Extract TodoWrite parameters from environment/stdin
# Claude Code may pass tool parameters via CLAUDE_TOOL_PARAMS env var
TOOL_PARAMS="${CLAUDE_TOOL_PARAMS:-}"

if [ -z "$TOOL_PARAMS" ]; then
    # Fallback: read from stdin (if available)
    TOOL_PARAMS=$(cat)
fi

# 2. Update progress data
if [ -n "$TOOL_PARAMS" ]; then
    "$SCRIPT_DIR/progress-tracker-update.sh" "$TOOL_PARAMS"
fi

# 3. Display progress
"$SCRIPT_DIR/progress-tracker-display.sh"

# 4. Export to external monitoring file
"$SCRIPT_DIR/progress-tracker-export.sh"

# 5. Run code quality checks (existing logic)
if [ -n "$1" ]; then
    run_code_quality_checks "$1"
fi

exit 0
```

### progress-tracker-update.sh (Update Logic)
```bash
#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PROGRESS_FILE="$PROJECT_ROOT/.orchestra/cache/progress.json"
LOCK_FILE="/tmp/orchestra-progress.lock"

# Source utility functions
source "$SCRIPT_DIR/lib/progress-utils.sh"

# Parse TodoWrite parameters
TOOL_PARAMS="$1"
TODOS=$(echo "$TOOL_PARAMS" | jq -r '.todos // []')

# Acquire lock and update atomically
(
    flock -w 5 200 || {
        log_event "ERROR" "Failed to acquire lock for progress update"
        exit 1
    }

    # Ensure progress file exists
    init_progress_file_if_missing "$PROGRESS_FILE"

    # Current timestamp
    TIMESTAMP=$(date +%s%3N)  # milliseconds

    # Process each todo
    echo "$TODOS" | jq -c '.[]' | while read -r todo; do
        TASK_ID=$(echo "$todo" | jq -r '.id')
        CONTENT=$(echo "$todo" | jq -r '.content')
        ACTIVE_FORM=$(echo "$todo" | jq -r '.activeForm')
        STATUS=$(echo "$todo" | jq -r '.status')

        # Detect agent
        AGENT=$(detect_agent_from_todo "$ACTIVE_FORM" "$CONTENT")

        # Check if task already exists
        EXISTING=$(jq --arg id "$TASK_ID" '.todos[] | select(.id == $id)' "$PROGRESS_FILE")

        if [ -z "$EXISTING" ]; then
            # New task: add with full metadata
            jq --arg id "$TASK_ID" \
               --arg content "$CONTENT" \
               --arg activeForm "$ACTIVE_FORM" \
               --arg status "$STATUS" \
               --arg agent "$AGENT" \
               --argjson startTime "$TIMESTAMP" \
               --argjson lastUpdateTime "$TIMESTAMP" \
               '.todos += [{
                   id: $id,
                   content: $content,
                   activeForm: $activeForm,
                   status: $status,
                   parentId: null,
                   agent: $agent,
                   startTime: $startTime,
                   lastUpdateTime: $lastUpdateTime,
                   estimatedDuration: null,
                   currentStep: null,
                   totalSteps: null,
                   tags: []
               }]' "$PROGRESS_FILE" > "$PROGRESS_FILE.tmp"

            log_event "INFO" "Created task $TASK_ID (Agent: $AGENT)"
        else
            # Existing task: update status and lastUpdateTime
            OLD_STATUS=$(echo "$EXISTING" | jq -r '.status')

            jq --arg id "$TASK_ID" \
               --arg status "$STATUS" \
               --arg agent "$AGENT" \
               --argjson lastUpdateTime "$TIMESTAMP" \
               '(.todos[] | select(.id == $id)) |= (. + {
                   status: $status,
                   agent: $agent,
                   lastUpdateTime: $lastUpdateTime
               })' "$PROGRESS_FILE" > "$PROGRESS_FILE.tmp"

            # Log status change
            if [ "$OLD_STATUS" != "$STATUS" ]; then
                log_event "INFO" "Task $TASK_ID: $OLD_STATUS → $STATUS (Agent: $AGENT)"
            fi
        fi

        mv "$PROGRESS_FILE.tmp" "$PROGRESS_FILE"
    done

    # Update metadata
    update_metadata "$PROGRESS_FILE" "$TIMESTAMP"

    # Add history entry
    add_history_entry "$PROGRESS_FILE" "$TIMESTAMP" "task_updated"

) 200>"$LOCK_FILE"

exit 0
```

### lib/progress-utils.sh (Shared Utilities)
```bash
#!/bin/bash

# Valid Orchestra agent names
VALID_AGENTS=("Alex" "Blake" "Eden" "Finn" "Iris" "Kai" "Leo" "Mina" "Nova" "Riley" "Skye" "Theo")

# Detect agent from todo fields
detect_agent_from_todo() {
    local active_form="$1"
    local content="$2"

    # Strategy 1: Parse activeForm (e.g., "Skye is implementing...")
    for agent in "${VALID_AGENTS[@]}"; do
        if [[ "$active_form" =~ ^$agent[[:space:]] ]]; then
            echo "$agent"
            return
        fi
    done

    # Strategy 2: Parse content (e.g., "[Nova] Build dashboard")
    if [[ "$content" =~ \[([A-Z][a-z]+)\] ]]; then
        local candidate="${BASH_REMATCH[1]}"
        if is_valid_agent "$candidate"; then
            echo "$candidate"
            return
        fi
    fi

    # Strategy 3: Parse content (e.g., "Design API (Kai)")
    if [[ "$content" =~ \(([A-Z][a-z]+)\) ]]; then
        local candidate="${BASH_REMATCH[1]}"
        if is_valid_agent "$candidate"; then
            echo "$candidate"
            return
        fi
    fi

    # Strategy 4: Use last known agent from metadata
    if [ -f "$PROGRESS_FILE" ]; then
        local last_agent=$(jq -r '.metadata.currentAgent // "Unknown"' "$PROGRESS_FILE")
        echo "$last_agent"
        return
    fi

    # Fallback
    echo "Unknown"
}

# Check if agent name is valid
is_valid_agent() {
    local name="$1"
    for agent in "${VALID_AGENTS[@]}"; do
        if [ "$agent" = "$name" ]; then
            return 0
        fi
    done
    return 1
}

# Format duration in human-readable form
format_duration() {
    local ms="$1"
    local seconds=$((ms / 1000))
    local minutes=$((seconds / 60))
    local hours=$((minutes / 60))

    if [ $hours -gt 0 ]; then
        echo "${hours}h $((minutes % 60))m"
    elif [ $minutes -gt 0 ]; then
        echo "${minutes}m $((seconds % 60))s"
    else
        echo "${seconds}s"
    fi
}

# Generate ASCII progress bar
format_progress_bar() {
    local percentage="$1"
    local width=10
    local filled=$((percentage * width / 100))
    local empty=$((width - filled))

    printf "["
    for ((i=0; i<filled; i++)); do printf "▓"; done
    for ((i=0; i<empty; i++)); do printf "░"; done
    printf "]"
}

# Initialize progress file with empty schema
init_progress_file_if_missing() {
    local file="$1"

    if [ ! -f "$file" ]; then
        mkdir -p "$(dirname "$file")"
        cat > "$file" << 'EOF'
{
  "schemaVersion": "2.0",
  "todos": [],
  "metadata": {
    "sessionStartTime": 0,
    "lastUpdateTime": 0,
    "activeAgents": [],
    "totalTokensEstimated": 0,
    "completionRate": 0,
    "totalTasks": 0,
    "completedTasks": 0,
    "inProgressTasks": 0,
    "pendingTasks": 0,
    "currentAgent": "Unknown"
  },
  "history": []
}
EOF
    fi
}

# Update metadata section
update_metadata() {
    local file="$1"
    local timestamp="$2"

    jq --argjson timestamp "$timestamp" '
        .metadata.lastUpdateTime = $timestamp |
        .metadata.totalTasks = (.todos | length) |
        .metadata.completedTasks = ([.todos[] | select(.status == "completed")] | length) |
        .metadata.inProgressTasks = ([.todos[] | select(.status == "in_progress")] | length) |
        .metadata.pendingTasks = ([.todos[] | select(.status == "pending")] | length) |
        .metadata.completionRate = (
            if .metadata.totalTasks > 0 then
                (.metadata.completedTasks * 100 / .metadata.totalTasks)
            else 0 end
        ) |
        .metadata.activeAgents = ([.todos[] | select(.status == "in_progress") | .agent] | unique)
    ' "$file" > "$file.tmp" && mv "$file.tmp" "$file"
}

# Add history entry
add_history_entry() {
    local file="$1"
    local timestamp="$2"
    local event="$3"
    local task_id="${4:-null}"
    local agent="${5:-null}"

    jq --argjson timestamp "$timestamp" \
       --arg event "$event" \
       --arg taskId "$task_id" \
       --arg agent "$agent" \
       '.history += [{
           timestamp: $timestamp,
           event: $event,
           taskId: $taskId,
           agent: $agent,
           details: null
       }]' "$file" > "$file.tmp" && mv "$file.tmp" "$file"
}

# Logging function
log_event() {
    local level="$1"
    local message="$2"
    local log_file="$PROJECT_ROOT/.orchestra/logs/progress-tracker.log"

    mkdir -p "$(dirname "$log_file")"
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] [$level] $message" >> "$log_file"
}
```

---

**End of ADR-001**
