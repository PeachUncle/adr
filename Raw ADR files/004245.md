# ADR-001: Multi-Agent Patterns - Spawn vs Role-Switch

> "The problem is choice." - The Architect

## Status
**Proposed** | 2025-01-09

## Context

The Matrix system supports multiple agent personas (Oracle, Neo, Smith, Trinity, Architect, Tank, Morpheus, Scribe). Currently, we have two patterns for multi-agent work:

1. **Role-Switch**: Single Claude instance changes persona sequentially
2. **Spawn**: Task tool creates parallel AI instances (Haiku/Opus)

We need clarity on when to use each pattern.

## Decision

### Use Role-Switch When:

| Scenario | Rationale |
|----------|-----------|
| Sequential workflow | Output of Agent A feeds Agent B |
| Voice/persona theater | User wants to "hear" different agents |
| Single-threaded tasks | No parallelization benefit |
| Human-in-the-loop | User needs to approve between steps |

**Implementation**: `/neo`, `/smith`, `/oracle` slash commands

```
User → Oracle (route) → Neo (implement) → Smith (review) → User
         ↓                    ↓                  ↓
      Same Claude instance, different personas
```

### Use Spawn (Task Tool) When:

| Scenario | Rationale |
|----------|-----------|
| Independent parallel tasks | 7 files to analyze = 7 Haiku agents |
| Bulk data gathering | Speed matters, tasks don't depend on each other |
| Research from multiple angles | Different perspectives simultaneously |
| Cost optimization | Haiku is 67% cheaper than Opus for bulk work |

**Implementation**: Task tool with `model: haiku` or `model: opus`

```
Oracle (Opus) spawns:
├── Task(haiku): "Search for X"     ─┐
├── Task(haiku): "Search for Y"      ├── Run in parallel
└── Task(haiku): "Search for Z"     ─┘
         │
         └── Results return to Oracle for synthesis
```

## Decision Matrix

| Question | Role-Switch | Spawn |
|----------|-------------|-------|
| Tasks depend on each other? | ✅ | ❌ |
| Need parallelism? | ❌ | ✅ |
| User wants agent voices? | ✅ | ❌ |
| Bulk repetitive work? | ❌ | ✅ |
| Complex judgment needed? | ✅ (Opus) | ❌ |
| Speed critical? | ❌ | ✅ |

## Consequences

### Positive
- Clear guidance for when to parallelize
- Cost optimization (Haiku for bulk, Opus for synthesis)
- Faster execution for independent tasks
- Maintains agent personality experience for users

### Negative
- Two patterns to remember
- Spawned agents don't have conversation context
- Need to design tasks that don't require coordination

## Implementation Notes

### Spawning Pattern (Tank's Role)
```bash
# Tank spawns parallel search agents
Task(subagent_type: "Explore", model: "haiku", prompt: "Find X in codebase")
Task(subagent_type: "Explore", model: "haiku", prompt: "Find Y in codebase")
```

### Role-Switch Pattern (Oracle's Role)
```
/oracle → routes to appropriate agent
/neo → implements (same instance, Neo persona)
/smith → reviews (same instance, Smith persona)
```

### Hybrid Pattern (Recommended)
```
Oracle (role-switch) decides strategy
  └── Spawns Haiku agents for parallel gathering
  └── Returns to Oracle for synthesis
  └── Role-switches to Neo for implementation
  └── Role-switches to Smith for review
```

## References
- `psi/The_Source/04_multi_agent.md` - Chapter 4: Multi-Agent Patterns
- `psi/lab/simulations/matrix_demo.sh` - Workflow prototype
- `psi/active/operator_spawn.sh` - Tank's parallel spawner

---
*Authored by: The Architect*
*In collaboration with: Jarkius*
