# 2. TypeScript Path Alias Configuration

- **Status:** Accepted
- **Date:** 2025-09-25

## Context and Problem Statement

During the initial setup, we encountered module resolution issues when importing components using the `@/` alias. The error `Cannot find module '@/components/Header'` indicated that TypeScript couldn't resolve the path alias correctly. This led to a learning opportunity about the relationship between project structure, TypeScript configuration, and module resolution.

## Decision Drivers

- Need for clean, maintainable import statements without relative paths like `../../../components/Header`
- Requirement to maintain consistency with Next.js conventions
- The importance of proper TypeScript configuration for development experience

## Considered Options

- **Option 1:** Keep components in `src/app/components/` with `"@/*": ["./*"]` - This would require the alias to point to the project root, but components would be nested inside the app directory
- **Option 2:** Move components to project root with `"@/*": ["./*"]` - This would work but goes against Next.js conventions
- **Option 3:** Use standard Next.js structure with `src/components/` and configure alias accordingly - Follows best practices and conventions

## Decision

We decided to adopt **Option 3**:

1. **Project Structure:**
   - Components are located in `src/components/` (not in `src/app/components/`)
   - Pages remain in `src/app/` following the App Router convention

2. **TypeScript Configuration in `tsconfig.json`:**
   ```json
   {
     "compilerOptions": {
       "baseUrl": ".",
       "paths": {
         "@/*": ["src/*"]
       }
     }
   }
   ```

3. **Import Pattern:**
   - `import { Header } from '@/components/Header'` resolves to `src/components/Header`

## Consequences

### Positive

- Clean import statements without relative paths
- Follows Next.js and React community conventions
- Easy refactoring when moving files around
- Consistent with how most Next.js projects are structured

### Negative

- Required learning about TypeScript module resolution
- Needed to restart development server and reload VS Code for changes to take effect
- Initial confusion about the relationship between `baseUrl` and `paths` configuration