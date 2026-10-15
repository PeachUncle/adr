# ADR-0010: Hook Type Selection (Command vs Prompt)

**Status:** Accepted
**Date:** 2025-11-06
**Deciders:** Project maintainers

## Context

Claude Code supports two hook execution types:

1. **Command hooks** (`type: "command"`): Execute shell scripts/programs locally
2. **Prompt hooks** (`type: "prompt"`): Query an LLM (Haiku) for context-aware evaluation

Each type has different performance characteristics, token costs, and use cases. Choosing the wrong type can lead to unnecessary costs, latency, or unreliable behavior.

### Command Hooks

- Execute local scripts/programs (bash, TypeScript, Python, etc.)
- Deterministic logic implemented by developer
- Fast (<50ms typical)
- Zero token cost
- Works offline
- Simple pass/fail logic

### Prompt Hooks

- Send prompt to Haiku for LLM-based evaluation
- Context-aware natural language understanding
- Slower (200-1000ms typical)
- Token cost: ~200-500 per invocation
- Requires network/API
- Complex heuristics and semantic analysis

The choice affects:

- Development costs (token usage)
- Response latency (user experience)
- Reliability (offline support)
- Complexity (code vs prompts)
- Maintenance (logic changes)

## Decision

**Use command hooks by default. Only use prompt hooks when context-aware evaluation is essential and the value justifies the cost.**

### Command Hooks (Default)

Use for:

- ✅ Deterministic validation (type checking, linting, tests)
- ✅ Simple pass/fail checks (file exists, build succeeds)
- ✅ Performance-critical operations (<50ms required)
- ✅ Offline workflows (CI/CD, local development)
- ✅ Displaying information (git status, task lists)
- ✅ Clear success criteria

### Prompt Hooks (Selective)

Use only when:

- ✅ Semantic code analysis required (not just syntax)
- ✅ Subjective quality assessment needed
- ✅ Complex context evaluation (multiple related factors)
- ✅ Natural language understanding required
- ✅ 200-1000ms latency acceptable
- ✅ Token cost (200-500) justified by value
- ✅ Network dependency acceptable

## Alternatives Considered

### Option 1: Command Hooks Only

**Description:**
Never use prompt hooks, always implement logic in code.

**Pros:**

- Zero token cost always
- Fast (<50ms) always
- Works offline
- Predictable behavior
- No API dependency

**Cons:**

- **Complex heuristics**: Some checks difficult to implement in code
- **Maintenance burden**: Complex regex/parsing for semantic checks
- **False positives**: Hard to match LLM's context understanding
- **Limited flexibility**: Can't adapt to nuanced situations

**Decision:** ❌ Rejected (but close)

**Rationale:** While command hooks should be default, some checks genuinely benefit from LLM evaluation. Completely avoiding prompt hooks would force complex regex logic that's harder to maintain and less accurate.

### Option 2: Prompt Hooks Only

**Description:**
Always use prompt hooks for maximum context-awareness.

**Pros:**

- Context-aware decisions
- Natural language prompts (easier to write/understand)
- Semantic understanding
- Flexible evaluation

**Cons:**

- **Token waste**: 200-500 tokens per hook invocation
- **Latency**: 200-1000ms per hook (poor UX)
- **API dependency**: Doesn't work offline
- **Rate limits**: Multiple hooks = multiple API calls
- **Cost**: Adds up with frequent use
- **Overkill**: Simple checks don't need LLM

**Decision:** ❌ Rejected

**Rationale:** Massive waste for simple checks. Prompt hooks should be rare, not default.

### Option 3: Hybrid Approach (Selected)

**Description:**
Command hooks by default, prompt hooks only when necessary.

**Pros:**

- **Best of both**: Fast/cheap for simple, context-aware for complex
- **Appropriate tool**: Use right hook type for each job
- **Cost efficient**: Tokens spent only when valuable
- **Performance**: Most hooks fast (<50ms)
- **Flexibility**: Can use prompt hooks when needed

**Cons:**

- **Decision required**: Must choose type for each hook
- **Mixed patterns**: Two different hook styles to maintain
- **Complexity**: Different testing/debugging approaches

**Decision:** ✅ Selected

**Rationale:** Provides flexibility while keeping costs and latency low for most use cases. Decision overhead is minimal (clear guidelines).

## Decision Matrix

### Use Command Hook When

| Criterion           | Command Hook                   |
| ------------------- | ------------------------------ |
| Logic type          | ✅ Deterministic (clear rules) |
| Latency requirement | ✅ <50ms needed                |
| Token budget        | ✅ Zero cost preferred         |
| Offline support     | ✅ Required                    |
| Success criteria    | ✅ Objective (pass/fail)       |
| Complexity          | ✅ Simple to moderate          |

**Examples:**

- TypeScript type checking (`tsc --noEmit`)
- Linting (`eslint`, `markdownlint`)
- Test execution (`vitest run`)
- File existence checks
- Git status display
- Build verification

### Use Prompt Hook When

| Criterion        | Prompt Hook                   |
| ---------------- | ----------------------------- |
| Logic type       | ✅ Subjective or semantic     |
| Evaluation       | ✅ Context-aware required     |
| Token budget     | ✅ 200-500 cost acceptable    |
| Network          | ✅ API access available       |
| Success criteria | ✅ Nuanced (quality judgment) |
| Complexity       | ✅ Complex heuristics         |

**Examples:**

- Error handling adequacy (is try/catch sufficient?)
- Security issue detection (hardcoded secrets, XSS patterns)
- Code quality assessment (complexity, readability)
- Accessibility compliance (semantic, not just syntax)

## Consequences

### Positive

- **Cost efficiency**: Tokens spent only when necessary
- **Fast default**: Most hooks <50ms (command hooks)
- **Offline support**: Command hooks work without network
- **Flexibility**: Can use prompt hooks for complex checks
- **Clear guidelines**: Easy to decide which type to use
- **Best tool for job**: Match hook type to use case

### Negative

- **Two patterns**: Need to learn both hook types
- **Decision overhead**: Must choose type for each hook
- **Mixed codebase**: Some hooks in TypeScript, some as prompts
- **Testing complexity**: Different approaches for each type

### Neutral

- **Documentation**: Need to document both patterns
- **Examples**: Should provide examples of each type
- **Reviews**: Must verify appropriate type chosen

## Implementation Notes

### Command Hook Template

```typescript
#!/usr/bin/env bun
/**
 * Hook Name: {name}
 * Type: Command
 * Event: {event}
 * Purpose: {purpose}
 *
 * Performance target: <50ms
 */

import { parseStdin } from './utils';

async function main() {
  const input = await parseStdin();

  // Deterministic logic here
  const result = checkSomething(input);

  if (result.failed) {
    console.log('⚠️  Check failed:', result.message);
    process.exit(1); // Block if needed
  }

  console.log('✅ Check passed');
  process.exit(0);
}

await main();
```

### Prompt Hook Template

```json
{
  "event": "Stop",
  "type": "prompt",
  "prompt": "Analyze the code changes in $ARGUMENTS for {criteria}.\n\nIf {issue} found:\n{\"decision\": \"block\", \"reason\": \"...\", \"systemMessage\": \"...\"}\n\nIf adequate:\n{\"decision\": \"approve\", \"reason\": \"...\"}",
  "timeout": 30
}
```

### When does this take effect?

- **Immediately** for all new hooks
- **Guidance** for existing hooks (migrate if mismatched)

### What needs to change to comply?

**New hooks:**

- Follow decision matrix
- Default to command hooks
- Justify prompt hooks in PR description

**Existing hooks:**

- Audit for appropriate type
- Migrate if mismatched (priority: high-frequency hooks)

**Hook reviews:**

- Verify appropriate type chosen
- Check if simpler command hook would suffice
- Ensure prompt hooks justify token cost

### Enforcement

1. **Code reviews**: Check hook type appropriateness
2. **Documentation**: Provide decision matrix
3. **Examples**: Show both types with clear use cases
4. **Guidelines**: This ADR serves as reference

## Performance Comparison

| Metric             | Command Hook | Prompt Hook |
| ------------------ | ------------ | ----------- |
| **Latency**        | <50ms        | 200-1000ms  |
| **Token Cost**     | 0            | 200-500     |
| **Offline**        | ✅ Yes       | ❌ No       |
| **API Dependency** | ❌ No        | ✅ Yes      |
| **Complexity**     | Code         | Prompt      |
| **Context-Aware**  | ❌ Limited   | ✅ Yes      |

## Use Case Examples

### ✅ Command Hook: Build Checker

**Why command hook:**

- Deterministic (either builds or doesn't)
- Fast (<1s with tsc-files)
- Zero tokens
- Clear pass/fail
- Works offline

```typescript
// build-checker.ts
const result = await run('tsc --noEmit');
if (result.exitCode !== 0) {
  console.log('⚠️ TypeScript errors found');
  process.exit(1);
}
```

### ✅ Prompt Hook: Security Guardrail

**Why prompt hook:**

- Semantic analysis (context matters)
- Subjective (what counts as "secret"?)
- Natural language prompt easier than regex
- Worth 300-500 tokens to catch security issues
- Network available at commit time

```json
{
  "type": "prompt",
  "prompt": "Analyze for hardcoded secrets, SQL injection, XSS..."
}
```

### ❌ Wrong: Prompt Hook for File Existence

**Why wrong:**

- Deterministic check (file exists or doesn't)
- Zero context needed
- Wastes 200 tokens
- Adds 200-1000ms latency
- Doesn't work offline

**Should be:**

```typescript
// ✅ Command hook instead
if (!existsSync(filePath)) {
  console.log('❌ File not found');
  process.exit(1);
}
```

### ❌ Wrong: Command Hook for Code Quality

**Why wrong:**

- Subjective assessment (what is "quality"?)
- Context-dependent (what's appropriate here?)
- Complex heuristics needed
- Would require extensive regex/AST parsing

**Should be:**

```json
{
  "type": "prompt",
  "prompt": "Analyze code quality: complexity, readability, maintainability..."
}
```

## References

**Related ADRs:**

- ADR-0008: No Auto-Formatting Hooks
- ADR-0009: Token-Efficient Skill Design

**OpenSpec Proposals:**

- [add-workflow-command-hooks](../../../openspec/changes/add-workflow-command-hooks/) - Command hook examples
- [add-workflow-prompt-hooks](../../../openspec/changes/add-workflow-prompt-hooks/) - Prompt hook examples (experimental)

**External Resources:**

- [Claude Code Hooks Documentation](https://code.claude.com/docs/en/hooks.md)
- [Hooks Reference](https://code.claude.com/docs/en/hooks-guide.md)

## Notes

This decision is based on:

1. **Performance**: Command hooks 20-40x faster than prompt hooks
2. **Cost efficiency**: 200-500 tokens per prompt hook adds up
3. **Offline support**: Command hooks work without network
4. **Appropriate tooling**: Use right tool for each job

### Why not always command hooks?

Some checks genuinely benefit from LLM evaluation:

- **Security**: "Is this a secret?" is context-dependent
- **Quality**: "Is this readable?" is subjective
- **Accessibility**: "Is this accessible?" requires semantic understanding

For these, prompt hooks are worth the cost.

### Why not always prompt hooks?

Most checks are simple and deterministic:

- **Type checking**: Either compiles or doesn't
- **Linting**: Clear rules
- **File existence**: Boolean check
- **Build status**: Pass or fail

For these, prompt hooks waste tokens and add latency.

### Token cost comparison

**Scenario: 10 commits per day**

- **Command hooks**: 0 tokens
- **Prompt hooks**: 10 commits × 300 tokens = 3,000 tokens/day
- **Monthly**: ~90,000 tokens (significant cost)

For deterministic checks, this is pure waste.

### When to use prompt hooks

Only when **all** of these are true:

1. Check requires semantic/context understanding
2. Deterministic logic would be complex (>100 lines of regex/parsing)
3. 200-1000ms latency is acceptable
4. 200-500 token cost is justified by value
5. Network dependency is acceptable for this use case

If any of these are false, use a command hook.

### When to revisit

- If Haiku becomes significantly faster (<50ms)
- If token costs drop significantly (

<10 tokens)

- If offline Haiku becomes available
- If prompt hooks gain major new capabilities

Until then, command hooks should be the default choice.
