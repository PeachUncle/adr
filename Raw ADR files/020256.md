# 7. Testing and CI/CD Strategy

Date: 2025-06-18 (amended 2025-06-20)

## Status

Accepted

## Context

As a single-developer hobby project focused on learning TypeScript and modern web development, we need development tools that minimize configuration overhead while enforcing good practices. The priority is on tools that work well out-of-the-box, integrate seamlessly with our chosen stack, and provide fast feedback loops for learning.

## Decision

We will implement the following development toolchain:

### Testing
- **Vitest** + **React Testing Library** for unit and component testing
- **Playwright** for potential future E2E testing (when needed)

### Code Quality
- **Biome** for both linting and formatting
- **TypeScript strict mode** for enhanced type safety
- **Husky + git-format-staged** for git hook management

### CI/CD
- **GitHub Actions** for continuous integration
- **Sentry** for performance monitoring

### Alternatives Considered

**Testing Frameworks:**
- **Jest** - Rejected in favor of Vitest due to better Vite integration and faster performance
- **Cypress** - Rejected for E2E in favor of Playwright's better TypeScript support

**Code Quality Tools:**
- **ESLint + Prettier** - Rejected due to configuration complexity and potential conflicts between tools
- **dprint** - Rejected due to smaller community and less integration with VS Code

**Git Hook Managers:**
- **Lefthook** - Rejected due to suboptimal handling of mixed staged/unstaged changes
- **Husky + lint-staged** - Rejected due to multiple dependencies (~1500) and similar staging limitations
- **pre-commit** - Rejected due to unnecessary complexity for single-project use

### Key Decision Factors

Choices prioritized:
1. **Minimal configuration**: Tools that work with sane defaults
2. **Single-tool solutions**: Biome over ESLint+Prettier
3. **Workflow compatibility**: Support for partial staging (common when splitting commits logically)
4. **Integration**: Compatibility with React Router v7, Vite, and Docker deployment

## Consequences

**What becomes easier:**
- Zero-config code quality enforcement with Biome's defaults
- Precise control over what gets committed when using partial staging with git-format-staged
- Fast test feedback with Vitest's integration with our Vite-based stack
- TypeScript learning with strict mode preventing bad habits

**What becomes more difficult:**
- Less flexibility for highly customized linting rules compared to ESLint
- Smaller community for Biome troubleshooting compared to traditional tools

**Risks:**
- Biome is newer and may have fewer edge-case solutions than ESLint
- git-format-staged has smaller community than lint-staged for troubleshooting
- Migration complexity if switching back to traditional toolchain later
