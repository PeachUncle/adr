# ADR-006: No Unused Variables - No Underscore Prefix

## Status

**Accepted** - October 23, 2025

## Context

It's common in JavaScript/TypeScript codebases to prefix unused variables with an underscore (`_variable`) to silence linter warnings. However, this practice hides real problems and can lead to bugs.

### The Problem

**Underscore prefixing** to silence linters:

```typescript
// ❌ Hiding unused variable
const types = schema.anyOf
  .map((prop) => getZodSchema({ schema: prop }))
  .map((type) => {
    let _isObject = true; // Unused! Hidden with underscore
    return type.toString();
  })
  .join(', ');
```

**Why this is problematic:**

1. **Hides mistakes**: Variable was added for a reason, now forgotten
2. **Dead code**: Clutters the codebase
3. **Misleading**: Suggests the variable matters when it doesn't
4. **Maintenance burden**: Future developers waste time understanding unused code
5. **Bugs**: Unused variables often indicate incomplete logic

### Forces at Play

**For underscore prefixing:**

- Quick way to silence linter
- Keeps variable in case it's needed later
- "Documents" that it's intentionally unused

**Against underscore prefixing:**

- Hides real problems
- Creates clutter
- Misleading to readers
- Prevents refactoring
- Indicates incomplete thinking

## Decision

**All symbols must be used or removed. Never prefix with underscore to hide unused variables.**

### Policy

1. **Remove unused variables entirely**
2. **Remove unused function parameters** (with rare exceptions)
3. **Remove unused imports**
4. **If truly needed unused**, document why with ESLint disable comment

### Exceptions

#### 1. Interface/Callback Signatures

When a function signature must match an interface, unused parameters are acceptable:

```typescript
// ✅ OK: Signature must match Array.map
array.map((value, _index, _array) => transform(value));

// Better: Just omit the parameters
array.map((value) => transform(value));
```

#### 2. Future-proofing (Rare)

If a variable is genuinely needed for upcoming work:

```typescript
// ✅ OK: Documented reason
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const futureFeature = extractData();
// TODO: Use futureFeature in phase 2 implementation
```

### How to Handle

```typescript
// ❌ BAD: Underscore prefix
function processSchema(schema: SchemaObject, _options?: Options) {
  // _options is never used
  return transform(schema);
}

// ❌ BAD: Unused local variable
function calculate(x: number) {
  let _intermediate = x * 2; // Never used
  return x + 1;
}

// ✅ GOOD: Remove unused parameters
function processSchema(schema: SchemaObject) {
  return transform(schema);
}

// ✅ GOOD: Remove unused local variables
function calculate(x: number) {
  return x + 1;
}

// ✅ GOOD: If truly needed, document why
function processSchema(
  schema: SchemaObject,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  options?: Options, // Reserved for future enhancement - see issue #123
) {
  return transform(schema);
}
```

## Consequences

### Positive

✅ **Cleaner code**: No clutter from unused variables  
✅ **Prevents bugs**: Catches incomplete implementations  
✅ **Clear intent**: Every variable has a purpose  
✅ **Easier refactoring**: No dead code to navigate  
✅ **Better reviews**: Unused variables trigger discussion  
✅ **Linter alignment**: Follows best practices

### Negative

⚠️ **Extra step**: Need to actually remove variables  
⚠️ **Interface matching**: May need more explicit handling

### Mitigation

- **Code reviews**: Catch underscore prefixes
- **Linter rules**: Enable `no-unused-vars` strictly
- **Clear exceptions**: Document when unused is acceptable
- **Team education**: Explain why this matters

## Before & After

### Before

```typescript
// ❌ Multiple unused variables hidden
const types = schema.anyOf
  .map((prop) => getZodSchema({ schema: prop }))
  .map((type, _index) => {
    let _isObject = true; // Never used
    let _depth = 0; // Never used
    return type.toString();
  })
  .join(', ');

function processEndpoint(
  operation: OperationObject,
  _path: string, // Never used
  _method: string, // Never used
) {
  return operation.operationId;
}
```

### After

```typescript
// ✅ Clean, only what's needed
const types = schema.anyOf
  .map((prop) => getZodSchema({ schema: prop }))
  .map((type) => type.toString())
  .join(', ');

function processEndpoint(operation: OperationObject) {
  return operation.operationId;
}
```

## Real Example from Codebase

**Before refactoring:**

```typescript
const types = schema.anyOf
  .map((prop) => getZodSchema({ schema: prop }))
  .map((type) => {
    let _isObject = true; // ❌ Unused, hidden with underscore
    return type.toString();
  })
  .join(', ');
```

**After refactoring:**

```typescript
const types = schema.anyOf
  .map((prop) => getZodSchema({ schema: prop }))
  .map((type) => type.toString()) // ✅ Simplified, removed unused
  .join(', ');
```

## Linter Configuration

```javascript
// eslint.config.js
export default [
  {
    rules: {
      '@typescript-eslint/no-unused-vars': [
        'error',
        {
          argsIgnorePattern: '^_', // Allow _param in interface matching only
          varsIgnorePattern: '^_', // Warn if used (should be removed or documented)
          caughtErrorsIgnorePattern: '^_', // Allow _error in catch blocks
        },
      ],
    },
  },
];
```

## Common Patterns

### Pattern 1: Array methods with unused indices

```typescript
// ❌ BAD
items.map((item, _index) => process(item));

// ✅ GOOD
items.map((item) => process(item));
```

### Pattern 2: Object destructuring with unused properties

```typescript
// ❌ BAD
const { used, _unused } = getConfig();

// ✅ GOOD
const { used } = getConfig();
```

### Pattern 3: Function parameters required by interface

```typescript
// ✅ Acceptable when signature must match
interface Handler {
  handle(data: Data, context: Context): Result;
}

class MyHandler implements Handler {
  // Must accept both parameters even if context is unused
  handle(data: Data, _context: Context): Result {
    return process(data);
  }
}
```

## Related Decisions

- [ADR-004: Pure Functions and Single Responsibility](./ADR-004-pure-functions-single-responsibility.md) - Simpler functions have fewer unused variables

## References

- RULES.md Section: "Code Organization" → "No unused vars"
- ESLint rule: `@typescript-eslint/no-unused-vars`
