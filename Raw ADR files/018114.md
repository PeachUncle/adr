# ADR-0007: Skill Auto-Activation System

**Status:** Accepted
**Date:** 2025-10-22
**Deciders:** Project maintainers

## Context

Claude Code skills traditionally require manual invocation - users must explicitly tell Claude to use a specific skill. This creates friction:

- Users must remember skill names
- Users must know which skills are available
- Users must explicitly request skills in each session
- Skills are underutilized (forgotten or unknown)

Requirements:

- Automatic skill activation based on user intent
- No manual invocation required for common use cases
- Fast execution (< 50ms overhead)
- Per-plugin configuration (each plugin manages its own rules)
- Project-level overrides (customize for specific projects)
- Zero configuration for basic usage (works out of box)

The activation system affects:

- Skill discoverability and usage
- User experience (friction vs automation)
- Token efficiency (auto-activated skills must be lightweight)
- Plugin architecture (how skills advertise their capabilities)

## Decision

**Implement automatic skill activation based on prompt analysis using a hook-based system with per-plugin rules and project overrides.**

**Architecture:**

1. **Per-plugin skill-rules.json** - Each plugin defines activation rules for its skills
2. **Runtime aggregation** - Hook discovers and merges all plugin rules
3. **Project overrides** - Optional `.claude/skills/skill-rules.json` for project customization
4. **UserPromptSubmit hook** - Analyzes prompts and suggests relevant skills
5. **Keyword & intent matching** - Match against keywords and regex patterns

**Activation flow:**

```txt
User submits prompt
  ↓
UserPromptSubmit hook executes
  ↓
Discover all skill-rules.json files (plugins/)
  ↓
Merge with project overrides (.claude/skills/skill-rules.json)
  ↓
Analyze prompt for keywords and intent patterns
  ↓
Rank matching skills by priority
  ↓
Suggest top N skills to Claude
  ↓
Claude uses suggested skills in response
```

## Alternatives Considered

### Option 1: Manual Invocation Only

**Description:**
Users explicitly request skills by name.

```txt
User: "Use skill-creator to create a new skill"
```

**Pros:**

- Explicit and predictable
- No automation overhead
- Users have full control
- Simple implementation

**Cons:**

- **High friction**: Users must know and remember skill names
- **Underutilization**: Skills forgotten or unknown
- **Poor UX**: Requires memorization
- **Discovery problem**: How do users learn about skills?

**Decision:** ❌ Rejected

**Rationale:** Manual invocation creates too much friction and leads to skill underutilization. Users shouldn't need to memorize skill names.

### Option 2: Global skill-rules.json

**Description:**
Single global configuration file with all skill activation rules.

**Pros:**

- Centralized configuration
- Easy to browse all rules
- Simple to understand

**Cons:**

- **Doesn't scale**: Adding plugins requires modifying global file
- **Merge conflicts**: Multiple plugins editing same file
- **No plugin isolation**: Plugins can't manage their own rules
- **Distribution problem**: How to include rules with plugins?

**Decision:** ❌ Rejected

**Rationale:** Doesn't support the plugin marketplace model. Each plugin should manage its own activation rules.

### Option 3: YAML Frontmatter Only

**Description:**
Use only YAML frontmatter in SKILL.md for activation triggers.

```yaml
---
name: skill-creator
triggers:
  keywords: [create skill, new skill]
  patterns: ['(create|add).*?skill']
---
```

**Pros:**

- Rules live with skill documentation
- Simple (no separate file)
- Easy to maintain

**Cons:**

- **Limited configuration**: Can't define plugin-level settings
- **No project overrides**: Can't customize per project
- **Parsing overhead**: Must read all SKILL.md files
- **Less flexible**: Can't express complex rules

**Decision:** ❌ Rejected

**Rationale:** Not flexible enough for advanced configuration (priorities, thresholds, project overrides). Also creates parsing overhead.

### Option 4: Per-Plugin Rules + Runtime Aggregation (Selected)

**Description:**
Each plugin has its own skill-rules.json, discovered and merged at runtime.

```txt
plugins/meta/skills/skill-rules.json
plugins/tanstack/skills/skill-rules.json
.claude/skills/skill-rules.json (project overrides)
```

**Pros:**

- **Scalable**: Plugins manage their own rules
- **Isolated**: No conflicts between plugins
- **Distributable**: Rules ship with plugins
- **Override-able**: Projects can customize
- **Fast**: Rules cached and merged once per session
- **Clean install/uninstall**: Add/remove plugin = add/remove rules

**Cons:**

- More complex (discovery + merging logic)
- Need to document file locations
- Precedence rules (project > plugin)

**Decision:** ✅ Selected

**Rationale:** Best balance of scalability, flexibility, and plugin isolation. Supports marketplace distribution and project customization.

## Consequences

### Positive

- **Zero-friction**: Skills activate automatically (no manual invocation)
- **Consistent usage**: Skills always available when relevant
- **Discoverable**: Users learn about skills through auto-activation
- **Plugin-friendly**: Each plugin manages its own activation rules
- **Customizable**: Projects can override activation behavior
- **Fast**: < 50ms execution time (cached and optimized)
- **Clean architecture**: Each plugin isolated, no global state

### Negative

- **Complexity**: More moving parts than manual invocation
- **Debugging**: Need to trace why a skill did/didn't activate
- **False positives**: Skills may activate when not needed
- **Maintenance**: Rules need updating as skills evolve

### Neutral

- **Documentation**: Need guides for configuring activation rules
- **Performance**: Must ensure < 50ms execution time
- **Testing**: Need to test activation logic thoroughly

## Implementation Notes

**How will this be enforced?**

- meta-plugin provides UserPromptSubmit hook
- Plugins include skill-rules.json in .claude/skills/
- Hook discovers and merges rules automatically
- No configuration required for basic usage

**skill-rules.json format:**

```json
{
  "plugin": {
    "name": "meta",
    "version": "1.0.0",
    "namespace": "meta"
  },
  "skills": {
    "skill-creator": {
      "type": "domain",
      "enforcement": "suggest",
      "priority": "high",
      "promptTriggers": {
        "keywords": ["create skill", "new skill"],
        "intentPatterns": ["(create|add).*?skill"]
      }
    }
  }
}
```

**Project overrides:**

```json
{
  "version": "1.0",
  "overrides": {
    "meta/skill-creator": {
      "priority": "critical",
      "promptTriggers": {
        "keywords": ["scaffold skill"]
      }
    }
  },
  "disabled": ["meta/old-skill"],
  "global": {
    "maxSkillsPerPrompt": 3,
    "priorityThreshold": "high"
  }
}
```

**When does this take effect?**

- Immediately after implementing the hook
- Existing skills work with manual invocation (backward compatible)
- Plugins add skill-rules.json when ready

**What needs to change to comply?**

- Implement UserPromptSubmit hook in meta-plugin
- Each plugin adds skill-rules.json
- Document activation rule format
- Create /configure-activation command for project overrides

**File locations:**

```txt
plugins/{plugin}/skills/skill-rules.json     # Plugin rules
.claude/skills/skill-rules.json               # Project overrides
```

**Hook implementation:**

```typescript
// plugins/meta/hooks/skill-activation-prompt.ts
export async function onUserPromptSubmit(prompt: string) {
  // 1. Discover all skill-rules.json files
  // 2. Merge with project overrides
  // 3. Match prompt against keywords/patterns
  // 4. Rank skills by priority
  // 5. Return top N suggestions
}
```

## References

**Related ADRs:**

- ADR-0006: Progressive Disclosure Pattern (auto-activated skills must be token-efficient)

**OpenSpec Proposals:**

- [add-skill-auto-activation](../../../openspec/changes/add-skill-auto-activation/) - Full implementation proposal

**External Resources:**

- [Claude Code Hooks Documentation](https://docs.claude.com/en/docs/claude-code/hooks)
- [Intent Recognition Patterns](https://en.wikipedia.org/wiki/Intent_recognition)

## Notes

**Performance requirements:**

- Hook execution: < 50ms for typical projects
- Rule discovery: Cached per session
- Pattern matching: Optimized regex compilation

**Backward compatibility:**

- Manual invocation still works
- Skills without activation rules aren't affected
- Graceful degradation if hook fails

**Security considerations:**

- Project overrides are user-controlled (trusted)
- Plugin rules are reviewed during plugin review
- No arbitrary code execution in rules

**Evolution path:**

This system can evolve to support:

- Machine learning-based activation (learn from usage)
- Context-aware activation (file types, git state)
- Usage analytics (which skills activate most)
- Smart suggestions (based on conversation history)

**Example activation:**

```txt
User: "Create a new skill for generating Hono API routes"

Hook matches:
- "create" + "skill" → meta/skill-creator (high priority)
- "hono" + "API" → api/hono-api-builder (medium priority)

Claude sees:
"Suggested skills: skill-creator, hono-api-builder"

Claude response:
"I'll help create a skill for Hono API generation. Let me use skill-creator to scaffold the SKILL.md..."
```

This decision makes skills feel native and integrated, not like separate tools users must remember to invoke.
