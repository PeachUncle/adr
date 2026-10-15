# ADR-006: Project Structure

## Status

Accepted

## Context

Rule Bound needs a clear, maintainable project structure that:

- Scales as the application grows
- Makes code easy to find
- Separates concerns logically
- Follows React/TypeScript best practices
- Supports the testing and documentation requirements
- Works well with Vite's build system

Key considerations:

- Every `.ts`/`.tsx` file needs a corresponding `.spec.ts(x)` test file
- Every `.ts`/`.tsx` file needs a corresponding `.md` documentation file
- Need clear separation between components, pages, utilities, etc.
- Need to organize rules content data
- Mobile-first responsive components

## Options Considered

### 1. Feature-Based Structure

```
src/
  features/
    rules/
      components/
      hooks/
      types/
    bookmarks/
      components/
      hooks/
```

- **Pros:**
  - Groups related code together
  - Easy to understand feature boundaries
  - Good for large apps
- **Cons:**
  - Can be harder to find shared components
  - May lead to duplication
  - Overkill for initial setup

### 2. Layer-Based Structure (Traditional)

```
src/
  components/
  hooks/
  pages/
  utils/
  types/
```

- **Pros:**
  - Simple and intuitive
  - Easy to find things by type
  - Works well for small-to-medium apps
  - Clear separation of concerns
- **Cons:**
  - Can become unwieldy as app grows
  - Less clear feature boundaries

### 3. Hybrid Approach

```
src/
  components/    (shared UI components)
  features/      (feature-specific code)
  pages/         (route pages)
  lib/           (utilities, hooks)
```

- **Pros:**
  - Balances organization and simplicity
  - Clear home for shared vs feature code
  - Scales well
- **Cons:**
  - Need to decide when something is "shared"

## Decision

We will use a **Hybrid Layer-Based Structure** that's appropriate for the current scope while allowing growth:

```
rulebound/
├── src/
│   ├── components/          # Shared, reusable UI components
│   │   ├── ui/             # Basic UI elements (Button, Card, etc.)
│   │   ├── layout/         # Layout components (Header, Nav, Footer)
│   │   └── common/         # Common components (Loading, Error, etc.)
│   ├── pages/              # Route-level page components
│   │   ├── HomePage/
│   │   ├── RulesPage/
│   │   └── ...
│   ├── features/           # Feature-specific code (as needed)
│   │   ├── search/
│   │   ├── bookmarks/
│   │   └── ...
│   ├── lib/                # Utilities, helpers, hooks
│   │   ├── hooks/          # Custom React hooks
│   │   ├── utils/          # Utility functions
│   │   └── api/            # API/data fetching
│   ├── store/              # Zustand stores
│   ├── types/              # TypeScript type definitions
│   ├── data/               # Static data (rules content)
│   ├── styles/             # Global styles, Tailwind config
│   ├── routes/             # Route definitions
│   ├── App.tsx             # Root app component
│   ├── main.tsx            # App entry point
│   └── vite-env.d.ts       # Vite type definitions
├── public/                 # Static assets
├── tests/                  # Test utilities and setup
│   └── setup.ts
└── docs/                   # Project documentation
    ├── components/         # Component documentation
    ├── architecture/       # Architecture docs
    └── guides/             # Developer guides
```

**Key reasons:**

1. **Intuitive**: Easy to find code by its type
2. **Scalable**: Can add features/ directory as needed
3. **Clear Separation**: Components vs pages vs utilities
4. **Testing**: Colocate test files with source files
5. **Documentation**: Colocate .md files with source files
6. **Vite-Friendly**: Works naturally with Vite's conventions

## Consequences

### Positive

- Clear, predictable file locations
- Easy for new developers to understand
- Scales from simple to complex
- Works well with testing and documentation requirements
- Follows React community conventions

### Negative

- May need to refactor to feature-based if app becomes very large
- Need discipline to avoid dumping everything in one folder

### Neutral

- Will need to establish conventions for when something goes in components/ vs features/
- Test files colocated with source (e.g., `Button.tsx` and `Button.spec.tsx` in same folder)
- Documentation files colocated with source (e.g., `Button.tsx` and `Button.md` in same folder)

### File Organization Rules

#### 1. Components

```
src/components/ui/Button/
├── Button.tsx           # Component implementation
├── Button.spec.tsx      # Component tests
├── Button.md            # Component documentation
└── index.ts             # Public exports
```

#### 2. Pages

```
src/pages/RulesPage/
├── RulesPage.tsx        # Page component
├── RulesPage.spec.tsx   # Page tests
├── RulesPage.md         # Page documentation
└── index.ts             # Public exports
```

#### 3. Utilities

```
src/lib/utils/
├── formatRuleReference.ts
├── formatRuleReference.spec.ts
├── formatRuleReference.md
└── index.ts
```

#### 4. Hooks

```
src/lib/hooks/
├── useRuleSearch.ts
├── useRuleSearch.spec.ts
├── useRuleSearch.md
└── index.ts
```

### Naming Conventions

- **Components**: PascalCase (e.g., `Button.tsx`, `RuleCard.tsx`)
- **Utilities**: camelCase (e.g., `formatDate.ts`, `parseRule.ts`)
- **Hooks**: camelCase with `use` prefix (e.g., `useRules.ts`, `useSearch.ts`)
- **Types**: PascalCase (e.g., `Rule.ts`, `UserPreferences.ts`)
- **Tests**: Same name as source + `.spec.ts(x)`
- **Docs**: Same name as source + `.md`
- **Folders**: PascalCase for components, camelCase for utilities

### Index Files

Each directory should have an `index.ts` that exports its public API:

```typescript
// src/components/ui/index.ts
export { Button } from "./Button";
export { Card } from "./Card";
export { Input } from "./Input";
```

This allows clean imports:

```typescript
import { Button, Card } from "@/components/ui";
```

### Path Aliases

Configure in `tsconfig.json` and `vite.config.ts`:

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@/components/*": ["src/components/*"],
      "@/lib/*": ["src/lib/*"],
      "@/types/*": ["src/types/*"]
    }
  }
}
```

### Growth Strategy

As the app grows:

1. Start with this structure
2. If a domain area gets complex, move it to `features/`
3. Keep `components/` for truly shared UI components
4. Keep `lib/` for generic utilities

Example future state:

```
src/
  components/      # Still shared UI
  features/
    combat/        # Complex feature
      components/
      hooks/
      types/
      utils/
  lib/             # Generic utilities
  pages/           # Routes
```
