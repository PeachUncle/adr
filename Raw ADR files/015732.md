# ADR-0007: TypeScript Strict Mode

## Status
Accepted

## Date
2024-12-30

## Context

TypeScript configuration affects code quality, developer experience, and runtime safety. Key configuration decisions:

1. **Strict Mode**: Enable all strict type-checking options
2. **Path Aliases**: Simplify imports with `@/` prefix
3. **Module Resolution**: Handle Next.js and React patterns
4. **Build Target**: JavaScript output version

## Decision

Enable TypeScript strict mode with comprehensive type safety settings.

### Configuration

`tsconfig.json`:

```json
{
  "compilerOptions": {
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    },
    "plugins": [
      { "name": "next" }
    ]
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

### Strict Mode Enables

| Option | Description |
|--------|-------------|
| `strictNullChecks` | `null` and `undefined` have distinct types |
| `strictFunctionTypes` | Stricter function parameter checking |
| `strictBindCallApply` | Check `bind`, `call`, `apply` arguments |
| `strictPropertyInitialization` | Class properties must be initialized |
| `noImplicitAny` | Error on expressions with implied `any` |
| `noImplicitThis` | Error when `this` has `any` type |
| `alwaysStrict` | Emit `"use strict"` in all files |

### Path Aliases

```typescript
// Before
import { Button } from '../../../components/ui/button'

// After
import { Button } from '@/components/ui/button'
```

### Type Patterns

API Response Types:
```typescript
// src/types/api.ts
export interface APIResponse<T> {
  data: T
  message?: string
  error?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  limit: number
}
```

Component Props:
```typescript
// Explicit prop types
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  children: React.ReactNode
  onClick?: () => void
  disabled?: boolean
}

// Using with forwardRef
const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', ...props }, ref) => {
    return <button ref={ref} {...props} />
  }
)
```

Hook Return Types:
```typescript
interface UseDocumentsReturn {
  documents: UserDocument[]
  loading: boolean
  error: string | null
  fetchDocuments: () => Promise<void>
  removeDocument: (id: string) => Promise<void>
}

export function useDocuments(): UseDocumentsReturn {
  // implementation
}
```

## Consequences

### Positive

1. **Catch Errors Early**: Type errors caught at compile time
2. **Better Autocomplete**: IDE knows exact types
3. **Self-Documenting**: Types serve as documentation
4. **Refactor Confidence**: Type checker catches breaking changes
5. **Null Safety**: Forced to handle `null`/`undefined` cases
6. **API Contracts**: Shared types between frontend and BFF

### Negative

1. **Learning Curve**: Stricter rules require TypeScript knowledge
2. **Verbose**: Some patterns require more type annotations
3. **Third-Party Types**: Some libraries have poor type definitions
4. **Build Time**: Type checking adds to build time

### Mitigations

- Use `// @ts-expect-error` sparingly for known issues
- Install `@types/*` packages for third-party libraries
- Use `unknown` instead of `any` when type is truly unknown
- Extract complex types to `src/types/` for reuse

### Type Organization

```
src/types/
├── api.ts          # API request/response types
├── auth.ts         # Authentication types
├── cpr.ts          # CPR document types
├── documents.ts    # Document management types
└── index.ts        # Re-exports
```

## References

- [TypeScript Strict Mode](https://www.typescriptlang.org/tsconfig#strict)
- [Next.js TypeScript](https://nextjs.org/docs/basic-features/typescript)
- `tsconfig.json` - Full configuration
- `src/types/` - Type definitions
