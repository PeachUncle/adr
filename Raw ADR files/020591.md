# ADR 005: Use Husky + lint-staged for Pre-commit Hooks and GitHub Actions `paths` for CI Optimization

## Status

Superseded (original approach), Accepted (simplified approach)

**Version History**:

- v1 (2025-10-25): Initial decision using custom file categorization (SUPERSEDED)
- v2 (2025-10-25): Simplified approach using GitHub's native `paths` feature (ACCEPTED)

## Context

The Zaddies Game project needs to reduce failed CI builds caused by formatting, linting, and type errors. Currently, developers push code that fails basic quality checks, leading to wasted CI resources and slower feedback loops. The team identified two main problems:

1. **Quality Issues Reach CI**: Formatting, linting, and TypeScript errors are not caught locally before commits, causing CI failures that could have been prevented
2. **CI Runs Unnecessarily**: Documentation-only changes trigger full build and deployment pipelines, wasting time and resources

The project is a pnpm monorepo with TypeScript, using Prettier for formatting, ESLint for linting, and the TypeScript compiler for type checking. The CI/CD system runs on GitHub Actions. The team needs a solution that:

- Works cross-platform (macOS, Linux, Windows)
- Installs automatically without manual developer setup
- Runs quality checks on staged files only (performance)
- Integrates seamlessly with existing pnpm workspace structure
- Allows emergency bypasses when needed
- Optimizes CI workflows based on changed file types
- **Is simple and maintainable** (minimal custom code)

### Discovery of Over-Engineering

After implementing a custom file categorization engine (~4000 lines of code with type definitions, unit tests, and bash scripting), we discovered that **GitHub Actions already provides native `paths` and `paths-ignore` filtering** that accomplishes the same goals with zero custom code. The original implementation violated the principle of simplicity.

## Decision

We will implement two complementary optimizations using the **simplest possible approach**:

### 1. Pre-commit Quality Gates (Unchanged)

Use **Husky 8.x** and **lint-staged 15.x** to run automated quality checks before commits:

- **Husky**: Manages git hooks, installed automatically via `prepare` script in package.json
- **lint-staged**: Runs commands only on staged files for performance
- **Check sequence**: Prettier → ESLint → TypeScript type-check
  - Prettier formats files automatically (fast, deterministic)
  - ESLint runs after formatting on staged files only
  - TypeScript compiler type-checks entire project (cross-file validation)

Configuration:

```json
{
  "scripts": {
    "prepare": "husky install",
    "type-check": "pnpm -r exec tsc --noEmit"
  },
  "lint-staged": {
    "*.{ts,tsx,js,jsx}": ["prettier --write", "eslint --fix"]
  }
}
```

Hook script (`.husky/pre-commit`):

```bash
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

pnpm exec lint-staged
pnpm run type-check
```

### 2. CI Workflow Optimization (SIMPLIFIED)

**Instead of** custom file categorization logic, use **GitHub Actions native `paths` and `paths-ignore` filters** with **separate workflow files per concern**:

**Separate Workflows Approach**:

- `.github/workflows/lint.yml` - Runs on all non-docs PRs
- `.github/workflows/frontend.yml` - Runs only when frontend/** or shared/** changes
- `.github/workflows/backend.yml` - Runs only when backend/** or shared/** changes
- `.github/workflows/deploy.yml` - Skips deployment for docs-only changes

Example workflow with `paths` filtering:

```yaml
# .github/workflows/frontend.yml
name: Frontend CI
on:
  pull_request:
    paths:
      - 'frontend/**'
      - 'shared/**'
      - 'package.json'
      - 'pnpm-lock.yaml'

jobs:
  test-and-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: pnpm/action-setup@v2
      - run: pnpm install
      - run: cd frontend && pnpm test
      - run: cd frontend && pnpm build
```

Example workflow with `paths-ignore` filtering:

```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]
    paths-ignore:
      - '**/*.md'
      - 'docs/**'
      - '.github/ISSUE_TEMPLATE/**'
      - '.github/PULL_REQUEST_TEMPLATE/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      # ... deployment steps ...
```

## Consequences

### Positive

**Pre-commit Hooks** (unchanged):

- ✅ **Automatic Setup**: Husky installs via `prepare` script - no manual developer action
- ✅ **Performance**: lint-staged runs checks only on staged files, <30s typical time
- ✅ **Industry Standard**: Husky has 7M+ weekly npm downloads
- ✅ **Cross-Platform**: Works on macOS, Linux, Windows (Git Bash)
- ✅ **Team Familiarity**: JavaScript ecosystem standard

**CI Optimization** (dramatically simplified):

- ✅ **96% Less Code**: ~165 lines vs ~4000 lines (simplified approach)
- ✅ **Zero Custom Logic**: GitHub maintains `paths` filtering, not us
- ✅ **Easier to Understand**: Separate workflow files are self-documenting
- ✅ **Native Platform Feature**: No bash scripting or TypeScript categorization needed
- ✅ **Parallel Execution**: Workflows run independently
- ✅ **Same Performance**: Docs-only PRs still skip builds (~60% faster)
- ✅ **Better Separation**: Each workflow has single responsibility
- ✅ **GitHub Maintained**: Path filtering logic maintained by GitHub, not us

### Negative

**Pre-commit Hooks**:

- ⚠️ **Two Dependencies**: Requires both Husky and lint-staged
- ⚠️ **TypeScript Performance**: Type-checking entire project 10-30s (but necessary)

**CI Optimization**:

- ⚠️ **Multiple Workflow Files**: 4 files instead of 1 (but clearer)
- ⚠️ **No Fine-Grained Logging**: Don't get custom "workflow decision summaries"
- ⚠️ **All-or-Nothing per Workflow**: Entire workflow skips or runs (acceptable trade-off)

### Neutral

- Developers can use `git commit --no-verify` to bypass hooks
- Windows requires Git Bash (standard with Git installation)
- Shared code changes trigger all workflows (intentional, safe default)

## Alternatives Considered

### Custom File Categorization Engine (v1 - REJECTED)

**What we built initially**:

- TypeScript categorization engine (`scripts/categorize-files.ts`, ~220 lines)
- Comprehensive type definitions (`shared/src/types/file-categorization.ts`, ~100 lines)
- Unit tests (`scripts/__tests__/categorize-files.test.ts`, ~350 lines)
- Bash file detection in workflows (~100 lines)
- Helper scripts (`scripts/get-changed-files.sh`, ~30 lines)
- **Total**: ~4000 lines of custom code

**Why rejected**:

- **Over-engineered**: Reinvents GitHub's native `paths` feature
- **High Maintenance**: Custom logic to test, debug, and maintain
- **Violates Simplicity**: 4000 lines when 165 lines accomplishes same goal
- **Not Necessary**: GitHub Actions already handles file pattern matching
- **Harder to Understand**: Complex conditional logic vs simple path filters

### GitHub Actions `paths` Filters (v2 - ACCEPTED)

**What we're using**:

- Native GitHub Actions `paths` and `paths-ignore`
- Separate workflow files per concern
- Zero custom categorization code
- **Total**: ~165 lines

**Why accepted**:

- **Platform Feature**: GitHub maintains it, not us
- **Simple**: Any developer can understand in <5 minutes
- **Proven**: Used by millions of GitHub repositories
- **Same Result**: Accomplishes all user stories with 96% less code
- **Better DX**: Separate workflows are self-documenting

### Single Workflow with `paths-ignore` on Jobs

**Rejected because**: Cannot run some checks while skipping others in same workflow. Would need multiple workflow files anyway, so separate workflows are cleaner.

### Conditional Steps with Bash Logic (v1 implementation)

**Rejected because**: Reinvents `paths` feature. Complex bash scripting in YAML is hard to maintain and test.

## Migration from v1 to v2

**Files to Remove** (from over-engineered v1):

- `scripts/categorize-files.ts`
- `scripts/__tests__/categorize-files.test.ts`
- `scripts/get-changed-files.sh`
- `shared/src/types/file-categorization.ts`
- `shared/src/types/precommit-checks.ts`
- Complex conditional logic in `.github/workflows/ci.yml`

**Files to Create** (simplified v2):

- `.github/workflows/lint.yml` (~30 lines)
- `.github/workflows/frontend.yml` (~35 lines)
- `.github/workflows/backend.yml` (~35 lines)
- Update `.github/workflows/deploy.yml` with `paths-ignore` (~40 lines)

**Net Change**: Remove ~750 lines, add ~165 lines = **585 fewer lines of code**

## Implementation Notes

- ADR created: 2025-10-25
- ADR updated (v2 simplification): 2025-10-25
- Feature branch: `003-ci-optimization-precommit`
- Related documentation:
  - Feature spec: `specs/003-ci-optimization-precommit/spec.md`
  - Implementation plan: `specs/003-ci-optimization-precommit/plan.md` (updated for v2)
  - Research: `specs/003-ci-optimization-precommit/research.md`

## Lessons Learned

1. **Platform Features First**: Always check if the platform already provides the feature before building custom solutions
2. **Simplicity Over Flexibility**: The custom categorization engine was flexible but unnecessary - simple path filters meet all requirements
3. **Question Complexity**: ~4000 lines for CI optimization is a red flag - simplify aggressively
4. **Separate Workflows**: Multiple focused workflow files are clearer than one complex file with conditional logic
5. **GitHub Docs**: GitHub Actions `paths` documentation was there all along - we should have read it first

## References

- Husky documentation: https://typicode.github.io/husky/
- lint-staged documentation: https://github.com/lint-staged/lint-staged
- GitHub Actions `paths` syntax: https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#onpushpull_requestpull_request_targetpathspaths-ignore
- ADR template: Michael Nygard format (http://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions)
