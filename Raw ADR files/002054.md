# Design: Component Decomposition Enforcement

## Context

The HAI3 framework guides AI assistants to generate screensets, but the current guidelines focus on data flow and naming conventions while ignoring component architecture. This results in:

1. **Monolithic screens** - All components defined inline in screen files
2. **No local uikit components** - Only icons created in `screensets/*/uikit/`
3. **Poor reusability** - Components copy-pasted instead of extracted
4. **Styling violations** - Inline styles and hex colors scattered through code

The `demo` screenset shows the desired pattern:
- `screens/uikit/CategoryMenu.tsx` (screen-local component)
- `demo/components/LayoutElements.tsx` (screenset-wide component)
- `demo/uikit/icons/ExpandableButton.tsx` (reusable presentational component)

The `dashboards` screenset (AI-generated) shows the problem:
- `HomeScreen.tsx` with 5 inline component definitions
- Only `DraggableCard.tsx` properly extracted
- Mock data hardcoded inline

## Goals / Non-Goals

**Goals:**
- Define clear decision tree for component placement (semantic, not numerical)
- Enforce component planning at AI proposal stage (proactive)
- Detect structural violations via ESLint and CLI (reactive)
- Maintain backward compatibility

**Non-Goals:**
- Arbitrary numerical limits (line counts, component counts)
- Automatically refactoring existing screens
- Runtime component validation

## Decisions

### Decision 1: Component Placement Decision Tree

```
IS THE CODE PURELY PRESENTATIONAL?
├─ What makes it presentational:
│   - Accepts value/onChange pattern for state
│   - No hooks that access external state (useAppSelector, useQuery, etc.)
│   - No side effects (API calls, event emissions)
│   - Uses only props and local useState/useEffect
│
├─ YES → screensets/{name}/uikit/{Component}.tsx
│        Examples: StatCard, ChartWrapper, DraggableCard, ExpandableButton
│        Rules:
│        - FORBIDDEN: import from @hai3/uicore (except types)
│        - REQUIRED: value/onChange pattern for controlled state
│        - REQUIRED: theme tokens only (no inline styles)
│
└─ NO → IS IT USED BY MULTIPLE SCREENS IN THIS SCREENSET?
         │
         ├─ YES → screensets/{name}/components/{Component}.tsx
         │        Examples: ThreadList, MessageComposer, SharedToolbar
         │        Rules:
         │        - MAY import from @hai3/uicore
         │        - MAY use Redux selectors and actions
         │        - SHOULD be screen-agnostic
         │
         └─ NO → screens/{screen}/components/{Component}.tsx
                  Examples: HomeRevenueChart, SettingsForm, ProfileHeader
                  Rules:
                  - MAY import from @hai3/uicore
                  - MAY be tightly coupled to screen state
                  - SHOULD be extracted when screen file has inline definitions
```

**Rationale:** Semantic criteria (presentational vs business logic, single vs multi-use) are more meaningful than arbitrary line/component counts.

### Decision 2: Proactive Enforcement via AI Commands

**Prevention is better than detection.** Modify AI commands to require component planning BEFORE generating code.

```markdown
## hai3-new-screenset / hai3-new-screen

### COMPONENT PLANNING PHASE (NEW - MANDATORY)

Before writing ANY code, analyze requirements:

1. List UI sections user described (e.g., "stats cards, charts, activity feed")

2. For EACH section, ask:
   - Is it presentational (stateless display)? → Plan in uikit/
   - Will it be reused across screens? → Plan in components/
   - Is it screen-specific with business logic? → Plan in screens/*/components/

3. Include Component Plan in proposal.md BEFORE tasks.md

4. Create component files FIRST, screen file LAST
   - This forces decomposition by design
   - Screen file should only orchestrate/compose
```

**Rationale:** AI generates better code when given explicit structure upfront. Asking about component structure before coding prevents monolithic files.

### Decision 3: CLI Validation Command

Create `hai3 validate components` to check structural patterns:

```bash
hai3 validate components [path]

# Checks performed:
# 1. Inline FC Detection - React.FC definitions in *Screen.tsx files
# 2. UIKit Purity - No @hai3/uicore imports in screensets/*/uikit/
# 3. Styling Violations - Inline styles and hex colors
# 4. Inline Data Arrays - Must use API services instead
```

**Implementation:**

```typescript
// packages/cli/src/commands/validate.ts

interface ValidationResult {
  file: string;
  rule: string;
  message: string;
  severity: 'error' | 'warning';
  suggestion?: string;
}

const validators = {
  // Detect: const Foo: React.FC in *Screen.tsx
  inlineComponents: (ast: AST, filename: string): ValidationResult[] => {
    if (!filename.endsWith('Screen.tsx')) return [];

    const inlineFCs = findNodes(ast, 'VariableDeclarator', node =>
      hasReactFCType(node) && !isExportDefault(node)
    );

    return inlineFCs.map(node => ({
      file: filename,
      rule: 'inline-component',
      message: `Inline component "${node.id.name}" should be extracted`,
      severity: 'warning',
      suggestion: `Move to screens/{screen}/components/${node.id.name}.tsx`
    }));
  },

  // Detect: import { useAppSelector } from '@hai3/uicore' in uikit/
  uikitPurity: (ast: AST, filename: string): ValidationResult[] => {
    if (!filename.includes('/uikit/') || filename.includes('/icons/')) return [];

    const uicoreImports = findImports(ast, '@hai3/uicore');
    const forbidden = uicoreImports.filter(imp =>
      !imp.specifiers.every(s => isTypeImport(s))
    );

    return forbidden.map(node => ({
      file: filename,
      rule: 'uikit-purity',
      message: 'UIKit components must be presentational - no @hai3/uicore imports',
      severity: 'error',
      suggestion: 'Move to components/ if business logic is needed'
    }));
  },

  // Detect: style={{}} and #hex colors
  inlineStyles: (ast: AST, filename: string): ValidationResult[] => {
    // Skip base uikit components
    if (filename.includes('/uikit/src/base/')) return [];

    const results: ValidationResult[] = [];

    // Find style={{}} JSX attributes
    const styleAttrs = findNodes(ast, 'JSXAttribute', n => n.name.name === 'style');
    results.push(...styleAttrs.map(node => ({
      file: filename,
      rule: 'inline-style',
      message: 'Inline style={{}} is forbidden',
      severity: 'error',
      suggestion: 'Use Tailwind classes or CSS variables'
    })));

    // Find hex color literals
    const hexColors = findNodes(ast, 'Literal', n =>
      typeof n.value === 'string' && /^#[0-9a-fA-F]{3,8}$/.test(n.value)
    );
    results.push(...hexColors.map(node => ({
      file: filename,
      rule: 'hex-color',
      message: `Hex color "${node.value}" is forbidden`,
      severity: 'error',
      suggestion: 'Use CSS variable like "hsl(var(--primary))"'
    })));

    return results;
  }
};
```

**AI Command Integration:**

```markdown
# hai3-validate.md (updated)

After completing implementation tasks, run:

\`\`\`bash
hai3 validate components src/screensets/{name}
\`\`\`

If violations found:
1. List each violation with file:line
2. Apply placement decision tree to determine correct location
3. Propose fix following component rules
```

### Decision 4: ESLint Rules

Add to `eslint-plugin-local`:

| Rule | Detects | Severity |
|------|---------|----------|
| `no-inline-styles` | `style={{}}` props, hex colors | error |
| `uikit-no-business-logic` | @hai3/uicore imports in uikit/ | error |
| `screen-inline-components` | React.FC definitions in *Screen.tsx | warning |

```typescript
// no-inline-styles.ts
const rule: Rule.RuleModule = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Disallow inline styles and hex colors outside base uikit',
      category: 'Styling',
    },
    messages: {
      noInlineStyle: 'Inline style={{}} is forbidden. Use Tailwind classes.',
      noHexColor: 'Hex color "{{color}}" is forbidden. Use hsl(var(--token)).',
    },
  },
  create(context) {
    const filename = context.getFilename();
    // Allow in packages/uikit/src/base/ only
    if (filename.includes('/uikit/src/base/')) return {};

    return {
      'JSXAttribute[name.name="style"][value.type="JSXExpressionContainer"]'(node) {
        context.report({ node, messageId: 'noInlineStyle' });
      },
      'Literal'(node) {
        if (typeof node.value === 'string' && /^#[0-9a-fA-F]{3,8}$/.test(node.value)) {
          context.report({
            node,
            messageId: 'noHexColor',
            data: { color: node.value }
          });
        }
      },
    };
  },
};
```

```typescript
// uikit-no-business-logic.ts
const rule: Rule.RuleModule = {
  meta: {
    type: 'problem',
    docs: {
      description: 'UIKit components must be presentational only',
      category: 'Screenset Architecture',
    },
    messages: {
      noUicoreImport: 'UIKit components cannot import from @hai3/uicore. Move to components/ if business logic is needed.',
    },
  },
  create(context) {
    const filename = context.getFilename();
    // Only check screensets/*/uikit/ (not icons)
    if (!filename.includes('/screensets/') ||
        !filename.includes('/uikit/') ||
        filename.includes('/icons/')) {
      return {};
    }

    return {
      ImportDeclaration(node) {
        if (node.source.value === '@hai3/uicore') {
          // Allow type-only imports
          const hasValueImports = node.specifiers.some(s =>
            s.type !== 'ImportSpecifier' ||
            !context.getSourceCode().getText(s).includes('type ')
          );
          if (hasValueImports) {
            context.report({ node, messageId: 'noUicoreImport' });
          }
        }
      },
    };
  },
};
```

### Decision 5: Optional ast-grep Rules

For more complex structural patterns, use [ast-grep](https://ast-grep.github.io/) YAML rules:

```yaml
# .ast-grep/rules/screen-inline-components.yml
id: screen-inline-components
language: tsx
rule:
  pattern: const $NAME: React.FC<$PROPS> = ($PARAMS) => $BODY
  not:
    follows:
      pattern: export default
  inside:
    kind: program
files:
  - "src/screensets/**/screens/**/*Screen.tsx"
message: |
  Inline component "$NAME" detected in screen file.
  Consider extracting to:
  - screens/{screen}/components/$NAME.tsx (if screen-specific)
  - screensets/{name}/components/$NAME.tsx (if multi-screen)
  - screensets/{name}/uikit/$NAME.tsx (if presentational)
severity: warning
```

```yaml
# .ast-grep/rules/inline-data-array.yml
id: inline-data-array
language: tsx
rule:
  pattern: const $NAME = [$$$ITEMS]
  has:
    pattern: "{ $$$PROPS }"
    stopBy: end
  inside:
    kind: program
files:
  - "src/screensets/**/screens/**/*Screen.tsx"
message: |
  Inline data array "$NAME" violates architecture.
  Data must come from API services via event-driven flow:
  - Create api/{domain}/{Domain}ApiService.ts
  - Add mocks in api/{domain}/mocks.ts
  - Fetch via action -> event -> effect -> slice
severity: error
```

**Run with:** `ast-grep scan --rule .ast-grep/rules/`

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| AI agents ignore component planning | CLI validation catches violations post-generation |
| Complex legitimate cases flagged | Use warnings not errors for structural patterns |
| Over-decomposition | Decision tree focuses on semantics, not arbitrary limits |
| Learning curve for developers | Clear examples in guidelines |

## Migration Plan

1. **Phase 1**: Add guidelines and AI command changes
   - No enforcement, documentation only

2. **Phase 2**: Add ESLint rules (styling) as errors
   - `no-inline-styles` immediately enforced

3. **Phase 3**: Add CLI validation command
   - Can be run manually or by AI

4. **Phase 4**: Add structural ESLint rules as warnings
   - `screen-inline-components` as warning
   - `uikit-no-business-logic` as error

**Rollback:** Rules can be disabled in eslint.config.js

## Open Questions

1. Should `hai3 validate components` be integrated into `npm run arch:check`?
2. Should we add VS Code extension for instant feedback?
3. Should ast-grep rules be mandatory or optional tooling?
