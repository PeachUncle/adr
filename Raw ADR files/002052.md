# Design: Screenset Self-Containment Refactoring

## Context

HAI3's current screenset architecture requires extensive manual updates when duplicating a screenset. The duplicate-screenset workflow (`.ai/workflows/DUPLICATE_SCREENSET.md`) has 9 major steps with ~50+ individual changes. This creates friction for rapid UI prototyping and increases error risk.

### Current Pain Points

1. **Redux State**: Slice name, state key, interface name, and module augmentation must all be manually coordinated
2. **Event System**: Event enum name, event string prefixes, and EventPayloadMap must all use consistent namespace
3. **API Services**: Domain constant and ApiServicesMap must match screenset purpose
4. **Icons**: Icon IDs have no namespacing, creating collision risk
5. **Translations**: Already auto-derived, but documentation unclear
6. **Registration**: Manual import in screensetRegistry.tsx required

### Stakeholders

- **AI Developers**: Need fast screenset duplication for prototyping
- **Human Developers**: Need clear, consistent patterns
- **Future Contributors**: Need minimal learning curve

## Goals / Non-Goals

### Goals

1. **Reduce duplication to 3 steps**: Copy folder, change screenset ID, change screen IDs
2. **Convention over configuration**: Derive all names from screenset ID
3. **Auto-discovery**: Eliminate manual import/registration steps
4. **Type safety**: Enforce conventions at compile time where possible
5. **Zero breaking changes to runtime behavior**: Only developer experience changes
6. **Clear documentation**: Make conventions obvious and enforceable

### Non-Goals

1. **Dynamic screenset loading**: No runtime plugin system (build-time discovery only)
2. **Screenset versioning**: Out of scope
3. **Cross-screenset dependencies**: Each screenset remains isolated
4. **Conditional screenset loading**: All discovered screensets are loaded (can filter via naming convention if needed)

## Decisions

### Decision 1: Slice Name = State Key = Screenset ID

**Rationale**: Currently, slice name, state key in RootState, and file names can diverge. Enforcing equality eliminates 3 sources of error.

**Implementation**:
```typescript
// packages/uicore/src/store/registerSlice.ts
export function registerSlice<K extends string>(
  key: K,
  reducer: Reducer,
  initEffects?: () => void
): void {
  // Extract slice name from reducer
  const sliceName = (reducer as any).name;

  // ENFORCE: slice name must equal state key
  if (sliceName !== key) {
    throw new Error(
      `Slice name "${sliceName}" must match state key "${key}". ` +
      `This is required for screenset self-containment.`
    );
  }

  // ... rest of registration
}
```

**Example**:
```typescript
// src/screensets/chat/slices/chatSlice.ts
export const chatSlice = createSlice({
  name: 'chat', // MUST match screenset ID
  // ...
});

// src/screensets/chat/chatScreenset.tsx
registerSlice('chat', chatReducer, initChatEffects);
//            ^^^^^^ MUST match slice name
```

**Alternatives Considered**:
- ❌ **Auto-derive key from slice**: Breaks explicit API contract
- ❌ **Allow mismatch with warning**: Warnings get ignored
- ✅ **Enforce at registration time**: Fail fast, clear error message

### Decision 2: Event Namespace = `${screensetId}/`

**Rationale**: Events need namespacing to avoid collisions. Using screenset ID as prefix creates clear ownership.

**Implementation**:
```typescript
// Convention (not enforced by runtime, enforced by lint/docs)
export enum ChatEvents {
  ThreadSelected = 'chat/threadSelected',
  //                ^^^^^ MUST match screenset ID
  ThreadCreated = 'chat/threadCreated',
  // ...
}
```

**Helper Utility** (optional, for type safety):
```typescript
// packages/uicore/src/events/eventHelpers.ts
export type ScreensetEvent<
  ScreensetId extends string,
  EventName extends string
> = `${ScreensetId}/${EventName}`;

// Usage:
export enum ChatEvents {
  ThreadSelected: ScreensetEvent<'chat', 'threadSelected'> = 'chat/threadSelected',
  // Type error if prefix doesn't match!
}
```

**Alternatives Considered**:
- ❌ **Global events**: Namespace collisions inevitable
- ❌ **Enforce at runtime**: Too costly, events are hot path
- ✅ **Convention + type helpers**: Best balance of safety and performance

### Decision 3: Icon ID = `${screensetId}:${iconName}`

**Rationale**: Icons currently use flat namespace (e.g., `MESSAGE_SQUARE_ICON_ID`). Duplicating creates collision risk.

**Implementation**:
```typescript
// src/screensets/chat/uikit/icons/MessageSquareIcon.tsx
export const MESSAGE_SQUARE_ICON_ID = 'chat:message-square';
//                                     ^^^^ screenset namespace

// Derived helper:
export const chatIcon = (name: string) => `chat:${name}`;
export const MESSAGE_SQUARE_ICON_ID = chatIcon('message-square');
```

**Example**:
```typescript
// Before (collision risk):
// src/screensets/chat/icons.ts
export const MESSAGE_SQUARE_ICON_ID = 'message-square';

// src/screensets/chat-copy/icons.ts
export const MESSAGE_SQUARE_ICON_ID = 'message-square'; // ❌ COLLISION!

// After (namespaced):
// src/screensets/chat/icons.ts
export const MESSAGE_SQUARE_ICON_ID = 'chat:message-square';

// src/screensets/chat-copy/icons.ts
export const MESSAGE_SQUARE_ICON_ID = 'chat-copy:message-square'; // ✅ UNIQUE
```

**Alternatives Considered**:
- ❌ **Generate random IDs**: Breaks referential transparency
- ❌ **Auto-prefix in registry**: Magical behavior, hard to debug
- ✅ **Explicit namespace in constant**: Clear and greppable

### Decision 4: API Domain Namespacing

**Rationale**: Screensets may have multiple API services (e.g., completion, history, settings). Domain should namespace under screenset ID + service name, similar to icon IDs.

**Implementation**:
```typescript
// src/screensets/chat/api/ChatApiService.ts
import { CHAT_SCREENSET_ID } from '../chatScreensetId';

export const CHAT_DOMAIN = `${CHAT_SCREENSET_ID}:chat` as const;
// Result: 'chat:chat'

// Multiple services in same screenset:
export const CHAT_HISTORY_DOMAIN = `${CHAT_SCREENSET_ID}:history` as const;
// Result: 'chat:history'

export const CHAT_SETTINGS_DOMAIN = `${CHAT_SCREENSET_ID}:settings` as const;
// Result: 'chat:settings'
```

**After duplication** (changing `CHAT_SCREENSET_ID = 'chat-copy'`):
```typescript
// ALL domains auto-update:
CHAT_DOMAIN = 'chat-copy:chat'
CHAT_HISTORY_DOMAIN = 'chat-copy:history'
CHAT_SETTINGS_DOMAIN = 'chat-copy:settings'
```

**Pattern**: `${screensetId}:${serviceName}` - matches icon ID pattern for consistency.

**Edge Case**: Shared API services (e.g., `accounts` used by multiple screensets)
- **Solution**: Framework services defined in `uicore`, mocks owned by screensets
- **Pattern**: Service in `packages/uicore/src/api/services/`, mocks in `src/screensets/*/api/mocks.ts`
- **Domain**: Framework services use simple names like `'accounts'`, not namespaced

**Alternatives Considered**:
- ❌ **Domain = Screenset ID only**: Doesn't support multiple services per screenset
- ❌ **Allow arbitrary domains**: Loses discoverability
- ✅ **Namespace with colon separator**: Consistent with icon IDs, supports multiple services

### Decision 5: Translation Namespace (Already Implemented)

**Current State**: Already follows convention via `screenset.${id}:...` and `screen.${screensetId}.${screenId}:...`

**No Change Needed**: This decision documents existing pattern.

**Pattern**:
```typescript
// Screenset-level:
t(`screenset.${CHAT_SCREENSET_ID}:name`)
// → 'screenset.chat:name'

// Screen-level:
t(`screen.${CHAT_SCREENSET_ID}.${CHAT_SCREEN_ID}:title`)
// → 'screen.chat.chat:title'
```

### Decision 6: Auto-Discovery via Vite Glob Imports

**Rationale**: Manual imports in `screensetRegistry.tsx` are the last remaining duplication step. Vite's `import.meta.glob` provides build-time auto-discovery with zero runtime overhead.

**Implementation**:
```typescript
// src/screensets/screensetRegistry.tsx

/**
 * Auto-discover and import all screensets
 * Pattern matches: */chatScreenset.tsx, */demoScreenset.tsx, etc.
 * Eager loading triggers side-effect registration immediately
 */
const screensetModules = import.meta.glob('./*/*[Ss]creenset.tsx', { eager: true });

// No manual imports needed - glob handles everything!
// Each screenset file's side effects (screensetRegistry.register() calls) execute automatically
```

**Naming Convention**:
```typescript
// REQUIRED: Screenset files MUST end with 'Screenset.tsx' or 'screenset.tsx'
// src/screensets/chat/chatScreenset.tsx     ✅
// src/screensets/demo/demoScreenset.tsx     ✅
// src/screensets/chat/ChatScreenset.tsx     ✅ (also works)
// src/screensets/chat/index.tsx             ❌ (won't be discovered)
// src/screensets/chat/config.tsx            ❌ (won't be discovered)
```

**How It Works**:
1. Vite processes glob at build time (no runtime scanning)
2. Each matched file is imported eagerly
3. Side effect in each file registers the screenset:
   ```typescript
   // src/screensets/chat/chatScreenset.tsx
   export const chatScreenset: ScreensetConfig = { /* ... */ };

   // Side effect - executes on import
   screensetRegistry.register(chatScreenset);
   ```
4. All screensets registered before app renders

**Type Safety**:
- Glob pattern is statically analyzable by TypeScript
- Import errors fail at build time
- No `any` types or dynamic requires

**Alternatives Considered**:
- ❌ **Manual imports**: Current approach, error-prone
- ❌ **Barrel exports (index.ts per screenset)**: Extra file, still needs glob
- ❌ **Runtime directory scanning**: Impossible in browser
- ❌ **Build-time codegen**: More complex, harder to debug
- ✅ **Vite glob with eager loading**: Declarative, zero overhead, type-safe

**Edge Cases**:
- **Non-screenset files in directory**: Avoided by strict naming convention (`*Screenset.tsx`)
- **Nested screensets**: Pattern `./*/*Screenset.tsx` only matches 2 levels deep (intentional)
- **Disabled screensets**: Rename to `.disabled.screenset.tsx` or move out of directory

## Automated Enforcement

### ESLint Rules (Custom)

**Location**: `eslint-plugin-local/` (new directory for project-specific rules)

#### Rule 1: `screenset-slice-name-matches-id`

**Purpose**: Enforce that slice name uses the SCREENSET_ID constant (not a hardcoded string)

**Implementation**:
```javascript
// Check createSlice() calls
module.exports = {
  create(context) {
    return {
      CallExpression(node) {
        if (node.callee.name === 'createSlice') {
          const nameProperty = node.arguments[0].properties.find(p => p.key.name === 'name');
          const nameValue = nameProperty.value;

          // ERROR if value is a string literal: name: 'chat'
          if (nameValue.type === 'Literal') {
            context.report({
              node: nameValue,
              message: 'Slice name must reference SCREENSET_ID constant, not hardcoded string',
              fix: (fixer) => fixer.replaceText(nameValue, 'SCREENSET_ID')
            });
          }

          // OK if value is an identifier: name: CHAT_SCREENSET_ID
          // When CHAT_SCREENSET_ID changes, slice name auto-updates
        }
      }
    };
  }
};
```

**Key Point**: Checks AST node type (Identifier vs Literal), NOT the actual value. When you change `CHAT_SCREENSET_ID = 'chat-copy'`, the slice name automatically changes because it references the constant.

**Severity**: Error (blocks commit)

#### Rule 2: `screenset-event-namespace`

**Purpose**: Enforce event enum values use template literals with SCREENSET_ID constant

**Implementation**:
```javascript
// Check enum declarations in *Events.ts files
module.exports = {
  create(context) {
    return {
      'TSEnumMember': (node) => {
        const initializer = node.initializer;

        // ERROR if value is a plain string: ThreadSelected = 'chat/threadSelected'
        if (initializer.type === 'Literal') {
          context.report({
            node: initializer,
            message: 'Event enum must use template literal with SCREENSET_ID: `${SCREENSET_ID}/eventName`',
          });
        }

        // OK if value is template literal: ThreadSelected = `${CHAT_SCREENSET_ID}/threadSelected`
        // When CHAT_SCREENSET_ID changes, all event names auto-update
        if (initializer.type === 'TemplateLiteral') {
          // Optionally verify it includes SCREENSET_ID identifier in template
        }
      }
    };
  }
};
```

**Key Point**: Checks for TemplateLiteral AST node type, NOT the resulting string value. Template literals auto-update when the constant changes.

**Severity**: Error (blocks commit)

#### Rule 3: `screenset-icon-namespace`

**Purpose**: Enforce icon IDs use template literals with SCREENSET_ID constant

**Implementation**:
```javascript
// Check icon ID exports in screenset files
module.exports = {
  create(context) {
    return {
      'VariableDeclarator': (node) => {
        if (node.id.name.endsWith('_ICON_ID')) {
          const init = node.init;

          // ERROR if value is a plain string: const ICON_ID = 'chat:message-square'
          if (init.type === 'Literal') {
            context.report({
              node: init,
              message: 'Icon ID must use template literal with SCREENSET_ID: `${SCREENSET_ID}:iconName`',
            });
          }

          // OK if value is template literal: const ICON_ID = `${CHAT_SCREENSET_ID}:message-square`
          // When CHAT_SCREENSET_ID changes, icon IDs auto-update
        }
      }
    };
  }
};
```

**Key Point**: Enforces template literal usage, NOT namespace prefix matching. The prefix automatically changes when the constant changes.

**Severity**: Error (blocks commit)

#### Rule 4: `screenset-api-domain-convention`

**Purpose**: Warn if API domain doesn't reference the SCREENSET_ID constant

**Implementation**:
```javascript
// Check API service files for domain constant
module.exports = {
  create(context) {
    return {
      'VariableDeclarator': (node) => {
        if (node.id.name.endsWith('_DOMAIN')) {
          const init = node.init;

          // WARN if value is a string literal: const DOMAIN = 'chat'
          if (init.type === 'Literal') {
            context.report({
              node: init,
              message: 'API domain should reference SCREENSET_ID constant for screenset-owned services',
              severity: 'warning'
            });
          }

          // OK if value is identifier: const CHAT_DOMAIN = CHAT_SCREENSET_ID
          // OK if value is 'as const': const ACCOUNTS_DOMAIN = 'accounts' as const (framework service)
          // When CHAT_SCREENSET_ID changes, domain auto-updates
        }
      }
    };
  }
};
```

**Key Point**: Warns about hardcoded strings, encourages constant reference. Framework services can use `as const` to opt out.

**Severity**: Warning (reviewable)

#### Rule 5: `screenset-file-naming`

**Purpose**: Enforce screenset files end with `Screenset.tsx`

**Implementation**:
```javascript
// Check file paths in src/screensets/
module.exports = {
  create(context) {
    const filename = context.getFilename();
    if (filename.match(/src\/screensets\/[^/]+\/[^/]+\.tsx$/)) {
      // Verify filename matches *Screenset.tsx or *screenset.tsx
    }
  }
};
```

**Severity**: Warning (helps auto-discovery)

#### Rule 6: `screenset-translation-keys`

**Purpose**: Prefer template literals over hardcoded translation keys

**Implementation**:
```javascript
// Check t() calls in screenset files
module.exports = {
  create(context) {
    return {
      'CallExpression': (node) => {
        if (node.callee.name === 't') {
          const firstArg = node.arguments[0];

          // WARN if key is hardcoded: t('screenset.chat:name')
          if (firstArg.type === 'Literal' &&
              firstArg.value.match(/^(screenset|screen)\./)) {
            context.report({
              node: firstArg,
              message: 'Use template literal for translation keys: `screenset.${SCREENSET_ID}:key`',
              severity: 'warning'
            });
          }

          // OK if template literal: t(`screenset.${CHAT_SCREENSET_ID}:name`)
          // When CHAT_SCREENSET_ID changes, translation keys auto-update
        }
      }
    };
  }
};
```

**Key Point**: Suggests template literals so translation namespace updates automatically when screenset ID changes.

**Severity**: Warning (best practice)

### Dependency Cruiser Rules

**Location**: `.dependency-cruiser.js`

#### Rule 1: Screenset Isolation

```javascript
{
  name: 'no-cross-screenset-imports',
  severity: 'error',
  from: { path: '^src/screensets/([^/]+)/' },
  to: {
    path: '^src/screensets/(?!\\1)[^/]+/',
    pathNot: '^src/screensets/screensetRegistry\\.tsx$'
  },
  comment: 'Screensets must not import from other screensets (vertical slice isolation)'
}
```

#### Rule 2: Package Import Restrictions

```javascript
{
  name: 'screensets-use-workspace-packages',
  severity: 'error',
  from: { path: '^src/screensets/' },
  to: {
    path: '^packages/',
    pathNot: '^@hai3/'
  },
  comment: 'Screensets must import via @hai3/* workspace names, not direct paths'
}
```

#### Rule 3: No Uicore Internals

```javascript
{
  name: 'no-uicore-internal-imports',
  severity: 'warn',
  from: { path: '^src/screensets/' },
  to: { path: '^@hai3/uicore/src/internal/' },
  comment: 'Screensets should use public uicore API only'
}
```

#### Rule 4: Circular Dependencies

```javascript
{
  name: 'no-circular-screenset-deps',
  severity: 'warn',
  from: { path: '^src/screensets/([^/]+)/' },
  to: { path: '^src/screensets/\\1/', circular: true },
  comment: 'Avoid circular dependencies within screenset modules'
}
```

### Enforcement Strategy

**Pre-commit Hooks** (optional, but recommended):
```json
{
  "husky": {
    "hooks": {
      "pre-commit": "npm run lint && npm run arch:deps"
    }
  }
}
```

**CI Pipeline**:
```yaml
- name: Lint
  run: npm run lint

- name: Architecture Check
  run: npm run arch:check

- name: Dependency Check
  run: npm run arch:deps
```

**Developer Experience**:
- ESLint auto-fix where possible (e.g., suggest template literals)
- Clear error messages with examples
- Documentation links in error messages
- VS Code integration for real-time feedback

## Risks / Trade-offs

### Risk 1: Enforcement Overhead

**Risk**: Runtime checks in `registerSlice()` add overhead.

**Mitigation**:
- Check only runs once per screenset during registration (not hot path)
- Error thrown early in app lifecycle (fail fast)
- Can be disabled in production builds if needed

**Impact**: Low - registration is one-time initialization

### Risk 2: Migration Effort

**Risk**: All existing screensets need updates.

**Mitigation**:
- Migration is mechanical (search-replace pattern)
- Start with simplest screenset (demo) to validate approach
- Can migrate one screenset at a time (not atomic)
- TypeScript errors guide migration

**Impact**: Medium - one-time cost for long-term benefit

### Risk 3: Convention Learnability

**Risk**: New developers might not understand conventions.

**Mitigation**:
- Document conventions prominently in CLAUDE.md
- Add JSDoc comments with convention reminders
- Enforce via architecture checks where possible
- Clear error messages when conventions violated

**Impact**: Low - conventions are intuitive (name matches purpose)

### Risk 4: Existing Screenset Compatibility

**Risk**: Breaking changes might affect in-progress work.

**Mitigation**:
- Communicate breaking changes clearly
- Provide migration guide
- Use OpenSpec process for visibility
- TypeScript compilation errors prevent silent breakage

**Impact**: Low - HAI3 is in active development, breaking changes acceptable

## Migration Plan

### Phase 1: Infrastructure (1-2 hours)

1. Update `registerSlice()` with validation
2. Add event/icon helper utilities
3. Update uicore documentation

**Validation**: TypeScript compilation, unit tests

### Phase 2: Documentation (1 hour)

1. Update CLAUDE.md
2. Update .ai/targets/SCREENSETS.md
3. Simplify duplicate-screenset workflow

**Validation**: Documentation review

### Phase 3: Screenset Migration (2-4 hours)

**Per Screenset** (~30 minutes each):
1. Update slice name in `createSlice()`
2. Update event namespace in events enum
3. Update icon IDs with namespace prefix
4. Verify `registerSlice()` call
5. Test via Chrome Studio MCP

**Validation**: Architecture checks, MCP testing

### Phase 4: Validation (1 hour)

1. Test duplication workflow with new 4-step process
2. Verify all architecture checks pass
3. Test production build

**Validation**: End-to-end testing

### Total Estimated Effort: 5-8 hours

## Open Questions

### Q1: Should we auto-generate event enums?

**Question**: Could we generate event enums from a config to enforce namespace?

**Answer**: Not in this change. Explicit enums are more greppable and easier to understand. Consider for future iteration.

### Q2: Should registerSlice auto-derive key from reducer?

**Question**: Instead of `registerSlice('chat', chatReducer)`, could we do `registerSlice(chatReducer)` and auto-extract the key?

**Answer**: No. Explicit is better than implicit. The validation approach (`registerSlice('chat', chatReducer)` validates name='chat') provides clarity without magic.

### Q3: How to handle screenset renaming?

**Question**: If we rename a screenset, what's the process?

**Answer**: Renaming = delete + create new. Since everything derives from ID, renaming is equivalent to creating a new screenset. This is intentional - screenset ID is the source of truth.

### Q4: Should we enforce icon/event conventions at compile time?

**Question**: Can TypeScript enforce `'chat/threadSelected'` format?

**Answer**: Partially. We can create type helpers that validate format, but can't prevent manual string literals. Focus on documentation and code review for now. Consider ESLint rules in future.

## Validation Strategy

### Compile-Time Validation

- ✅ **TypeScript**: Slice name type matches state key type
- ✅ **TypeScript**: Event enum values match type constraints (via helpers)
- ✅ **Architecture checks**: `npm run arch:check` validates dependency rules

### Runtime Validation

- ✅ **registerSlice()**: Throws if slice name ≠ state key
- ⚠️ **Event namespace**: Convention-based (no runtime check)
- ⚠️ **Icon namespace**: Convention-based (no runtime check)
- ⚠️ **API domain**: Convention-based (optional warning)

### Developer Validation

- ✅ **Documentation**: CLAUDE.md clearly describes conventions
- ✅ **Error messages**: Clear, actionable guidance
- ✅ **Examples**: All examples follow conventions
- ✅ **MCP Testing**: Required before commit

## Success Criteria

1. **Duplication reduced to 4 steps** - Verified by creating test duplicate
2. **Zero runtime behavior changes** - Verified by MCP testing
3. **All architecture checks pass** - Verified by CI
4. **Clear documentation** - Verified by peer review
5. **Type-safe conventions** - Verified by TypeScript compilation
6. **Reduced error surface** - Measured by lines of code that must change during duplication
   - Before: ~50+ lines
   - After: ~4 lines
   - Reduction: ~92%
