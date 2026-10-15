# ADR-0008: No Auto-Formatting Hooks During Conversations

**Status:** Accepted
**Date:** 2025-11-06
**Deciders:** Project maintainers

## Context

Claude Code supports hooks that can execute after tool uses, including hooks that modify files (e.g., running Prettier to format code). While automatic formatting seems convenient, community research reveals significant hidden costs.

From production Claude Code usage (6+ months, 300k+ LOC):

> "After publishing, a reader shared detailed data showing that file modifications trigger `<system-reminder>` notifications that can consume significant context tokens. In their case, Prettier formatting led to **160k tokens consumed in just 3 rounds** due to system-reminders showing file diffs."
>
> — Reddit: Claude Code is a beast (diet103, November 2025)

The problem affects:

- Token budget consumption (costs and context limits)
- Conversation length before compaction
- Ability to maintain context for large features
- Developer productivity (premature compaction interruptions)

## Decision

**Never implement file-modifying hooks during active Claude Code conversations.**

Specifically:

- ❌ No Prettier hooks that format on Save/Edit
- ❌ No ESLint --fix hooks that auto-fix issues
- ❌ No hooks that modify files mid-conversation
- ✅ Manual formatting between sessions: `bun run format`
- ✅ Read-only hooks are acceptable (display info, check status)

## Alternatives Considered

### Option 1: Auto-Format Hooks

**Description:**
Add PostToolUse hooks that run Prettier/ESLint after every Edit/Write.

**Pros:**

- Convenient (no manual formatting needed)
- Ensures consistent formatting always
- Catches formatting issues immediately
- Developer doesn't need to remember to format

**Cons:**

- **Token cost**: 160k+ tokens in 3 rounds (documented)
- **System reminders**: Each file modification triggers diff display
- **Context pollution**: Repeated formatting changes fill context
- **Premature compaction**: Forces conversation resets earlier
- **Hidden cost**: Token usage not visible to user
- **Large files**: Bigger diffs = more tokens consumed

**Decision:** ❌ Rejected

**Rationale:** The 160k token cost (53%+ of typical conversation budget) far outweighs the convenience. This is not a theoretical cost—it's documented from production usage.

### Option 2: Manual Formatting (Selected)

**Description:**
Run formatting commands manually between sessions or before commits.

**Pros:**

- **Zero token cost**: No mid-conversation file modifications
- **User control**: Developer chooses when to format
- **Batch efficiency**: Format many files at once
- **Better for iteration**: Claude can make multiple changes before formatting
- **Transparent**: Developer sees when formatting happens

**Cons:**

- Requires discipline (remembering to format)
- Inconsistent formatting during development
- May forget before commits (mitigated by pre-commit hooks)

**Decision:** ✅ Selected

**Rationale:** Zero token cost and user control outweigh the minor inconvenience. Pre-commit hooks can catch forgotten formatting.

### Option 3: Format Only on Explicit Request

**Description:**
Hook that only formats when user says "format" or similar.

**Pros:**

- User control over when formatting happens
- Avoids surprise token costs
- Batch formatting still possible

**Cons:**

- Still consumes tokens when used
- User might not realize token cost
- Adds complexity (when to use vs not?)

**Decision:** ❌ Rejected

**Rationale:** If formatting is explicit, might as well run `bun run format` manually. Adding a hook doesn't provide enough value to justify the implementation complexity.

## Consequences

### Positive

- **Token savings**: 160k+ tokens saved per session (massive ROI)
- **Longer conversations**: Can work on larger features without compaction
- **Better context**: Token budget used for actual work, not formatting
- **Predictable costs**: No hidden token consumption
- **Faster responses**: No hook execution overhead

### Negative

- **Manual step**: Developer must remember `bun run format`
- **Inconsistent during dev**: Files may have formatting issues mid-conversation
- **Discipline required**: Need to run format before commits

### Neutral

- **Pre-commit hooks**: Can still enforce formatting at commit time (not during conversation)
- **Editor integration**: Developers can still use editor auto-format (doesn't affect Claude Code)
- **Documentation**: Need to document manual formatting workflow

## Implementation Notes

**How will this be enforced?**

- Never create hooks with `type: "command"` that modify files during conversations
- Document manual formatting workflow in development guides
- Use pre-commit hooks (lefthook) to enforce formatting before commits
- Hook reviews check for file modifications

**When does this take effect?**

- Immediately for all hook development
- Applies to all plugins (workflow, testing, meta, etc.)

**What needs to change to comply?**

- No existing auto-formatting hooks (none to remove)
- Document `bun run format` workflow in guides
- Add pre-commit hook for formatting enforcement (safe: runs outside Claude conversations)
- Code reviews verify hooks don't modify files

**Acceptable hook patterns:**

```typescript
// ✅ GOOD: Read-only hook (displays info)
async function buildCheckerHook() {
  const result = await runTypeScriptCheck();
  console.log('TypeScript errors found:', result.errors);
  // No file modifications
}

// ❌ BAD: File-modifying hook
async function formatterHook() {
  await runPrettier(); // Modifies files!
  // Triggers system-reminders with diffs
}
```

## References

**Related ADRs:**

- ADR-0010: Hook Type Selection (Command vs Prompt)

**OpenSpec Proposals:**

- [add-workflow-command-hooks](../../../openspec/changes/add-workflow-command-hooks/) - Build checker hook (read-only)

**External Resources:**

- [Reddit: Claude Code is a beast](https://www.reddit.com/r/ClaudeAI/comments/1oivjvm/claude_code_is_a_beast_tips_from_6_months_of/) - Production usage insights
- [Claude Code Hooks Documentation](https://code.claude.com/docs/en/hooks.md)

**Community Research:**

> "Hook #3: Prettier Formatter... ⚠️ Update: I No Longer Recommend This Hook. After publishing, a reader shared detailed data showing that file modifications trigger <system-reminder> notifications that can consume significant context tokens."

## Notes

This decision is based on:

1. **Empirical evidence**: 160k tokens consumed in 3 rounds (documented production usage)
2. **Cost-benefit analysis**: Convenience doesn't justify 53%+ token budget loss
3. **User feedback**: Community consensus after real-world testing
4. **Project values**: Token efficiency is a top priority

**Important distinction:**

- **Pre-commit hooks** (outside conversation): ✅ Acceptable
- **Mid-conversation hooks** (during development): ❌ Not acceptable

Pre-commit hooks run outside Claude Code conversations, so they don't trigger system-reminders or consume context tokens. This is the recommended approach for enforcing formatting.

**Alternative solutions explored:**

- Smarter formatting (only changed lines): Still triggers system-reminders
- Conditional formatting (only if needed): Complexity doesn't justify benefit
- Delayed formatting (end of session): User might forget; doesn't save much

**When to revisit:**

If Claude Code changes how file modifications work (e.g., no system-reminders for hook modifications), we should revisit this decision. Until then, the token cost is too high.
