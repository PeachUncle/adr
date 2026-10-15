---
title: Linting Strategy
status: approved
date: 2025-12-05
decision-makers: [arustydev]
tags: [code-quality, linting, pre-commit, ci-cd, conventional-commits]
---

# Linting Strategy

## Context

This project requires comprehensive code quality enforcement across multiple languages (Rust, Python, JavaScript/TypeScript, Go, Shell), configuration files (TOML, JSON, YAML, Markdown), and commit messages. A unified strategy was needed to:

1. Provide fast local feedback to developers
2. Enforce standards consistently in CI/CD
3. Generate actionable SARIF reports for GitHub Security tab
4. Validate commit messages against conventional commits specification
5. Support custom commit types and scopes for project-specific needs

## Decision

### Hybrid Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         LINTING STRATEGY                                 │
├─────────────────────────────────────────────────────────────────────────┤
│  Layer 1: LOCAL PRE-COMMIT (Fast Feedback)                              │
│  • Format checks, fast lints, spelling, commit messages                 │
│  • Runs: Every commit locally                                           │
│  • Tools: pre-commit framework                                          │
├─────────────────────────────────────────────────────────────────────────┤
│  Layer 2: PRE-COMMIT.CI (PR Enforcement)                                │
│  • Same hooks as local, auto-fixes via commit                           │
│  • Runs: Every PR                                                       │
│  • Tools: pre-commit.ci service                                         │
├─────────────────────────────────────────────────────────────────────────┤
│  Layer 3: INDIVIDUAL WORKFLOWS (SARIF + Extended Analysis)              │
│  • SARIF → Security tab, type checking, slow/comprehensive checks       │
│  • Runs: Push to main, PR, scheduled                                    │
│  • Tools: GitHub Actions with language-specific linters                 │
└─────────────────────────────────────────────────────────────────────────┘
```

**Rationale**: This hybrid approach maximizes developer productivity (fast local feedback), ensures consistency (CI enforcement), and provides visibility (SARIF reports) without sacrificing any dimension.

---

## Tool Decisions by Category

### Language-Specific Linting

| Language | Linter | Formatter | SARIF | Rationale |
|----------|--------|-----------|-------|-----------|
| **Rust** | clippy | rustfmt | Yes (clippy-sarif) | Official Rust tools, excellent integration |
| **Python** | ruff | ruff | Yes | 10-100x faster than flake8/black, replaces multiple tools |
| **JavaScript** | eslint | prettier | Yes | Industry standard, extensive plugin ecosystem |
| **TypeScript** | eslint + tsc | prettier | Yes | Type checking via tsc --noEmit |
| **Go** | golangci-lint | gofmt | Yes | Meta-linter, aggregates 50+ linters |
| **Shell** | shellcheck | shfmt | Yes | SC codes are well-documented, SARIF support |
| **Dockerfile** | hadolint | - | Yes | DL codes follow best practices, dockle for CIS |

### Configuration File Linting

| File Type | Tool | Pre-commit | Workflow |
|-----------|------|------------|----------|
| **TOML** | taplo | Yes | lint-config.yml |
| **JSON** | check-json + prettier | Yes | lint-config.yml |
| **YAML** | yamllint | Yes | lint-config.yml |
| **Markdown** | markdownlint-cli2 | Yes | lint-config.yml |
| **EditorConfig** | editorconfig-checker | Yes | - |
| **GitHub Actions** | actionlint | Yes | lint-config.yml |

### Quality Assurance

| Category | Tool | Rationale |
|----------|------|-----------|
| **Spelling** | typos-cli | Rust-native, fast, low false positives |
| **Commit Linting** | Cocogitto + commitlint | Hybrid approach (see below) |

---

## Commit Linting Strategy

### Decision: Hybrid Cocogitto + commitlint

After evaluating multiple tools, we chose a hybrid approach using both **Cocogitto** (Rust) and **commitlint** (JavaScript):

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    COMMIT LINTING TOOLS                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  COCOGITTO (Rust)                                                │    │
│  │  Purpose: Custom types, scopes, changelog, versioning            │    │
│  │  Config: cog.toml                                                │    │
│  │  Commands: cog commit, cog check, cog bump, cog changelog        │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              +                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  COMMITLINT (JavaScript)                                         │    │
│  │  Purpose: Header/body/footer validation, length limits           │    │
│  │  Config: .commitlintrc.js                                        │    │
│  │  Hooks: commit-msg via pre-commit                                │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Tool Comparison

| Feature | commitlint | Cocogitto | conventional_commits_linter |
|---------|:----------:|:---------:|:---------------------------:|
| Custom types | Full | Full | Not yet |
| Custom scopes | Full | Partial | Not yet |
| Header length validation | Yes | No | Planned |
| Body/footer rules | Full | No | No |
| Signed-off-by | Yes | No | No |
| Changelog generation | No | Yes | No |
| Version bumping | No | Yes | No |
| Monorepo support | No | Yes | No |
| No Node.js required | No | Yes | Yes |
| SARIF output | No | No | No |

### Why Both Tools?

1. **Cocogitto excels at**:
   - Custom commit types with changelog behavior (`bump_minor`, `bump_patch`, `omit_from_changelog`)
   - Automatic changelog generation from conventional commits
   - Semver version bumping with pre/post hooks
   - Monorepo package versioning

2. **commitlint excels at**:
   - Detailed header validation (min/max length, case, full-stop)
   - Body rules (leading blank, line length)
   - Footer rules (leading blank, line length)
   - Signed-off-by enforcement
   - References validation (issue links)
   - 30+ configurable rules

**Neither tool alone covers all requirements**, so combining them provides complete coverage.

### Alternatives Considered

| Tool | Decision | Reason |
|------|----------|--------|
| **Commitizen** | Not chosen | Interactive prompts only, no validation |
| **conventional_commits_linter** | Not chosen | Config file not yet implemented |
| **git-cliff** | Complementary | May add for changelog customization |

---

## Custom Commit Types

### Standard Types (Conventional Commits + Angular)

| Type | Description | Changelog | Version Bump |
|------|-------------|-----------|--------------|
| `feat` | New feature | ✨ Features | minor |
| `fix` | Bug fix | 🐛 Bug Fixes | patch |
| `docs` | Documentation | 📚 Documentation | - |
| `style` | Code style (formatting) | 💄 Styling | - |
| `refactor` | Code refactoring | ♻️ Refactoring | - |
| `perf` | Performance improvement | ⚡ Performance | patch |
| `test` | Tests | 🧪 Tests | - |
| `build` | Build system | 📦 Build | - |
| `ci` | CI/CD | 👷 CI/CD | - |
| `chore` | Maintenance | (omitted) | - |
| `revert` | Revert commit | ⏪ Reverts | patch |

### Custom Types (Project-Specific)

| Type | Description | Changelog | Version Bump | Rationale |
|------|-------------|-----------|--------------|-----------|
| `hotfix` | Critical fix | 🚑 Hotfixes | patch | Distinguish from regular fixes |
| `security` | Security fix | 🔒 Security | patch | Highlight security changes |
| `deps` | Dependencies | 📦 Dependencies | patch | Track dependency updates |
| `wip` | Work in progress | (omitted) | - | Allow incomplete commits |
| `release` | Release prep | (omitted) | - | Version bump commits |

---

## Custom Scopes

### Core Components

| Scope | Description |
|-------|-------------|
| `core` | Core functionality |
| `api` | API layer |
| `cli` | Command-line interface |
| `config` | Configuration |

### MCP-Specific

| Scope | Description |
|-------|-------------|
| `mcp` | MCP protocol |
| `transport` | Transport layer (stdio, sse, http) |
| `tools` | MCP tools |
| `resources` | MCP resources |
| `prompts` | MCP prompts |

### Infrastructure

| Scope | Description |
|-------|-------------|
| `ci` | CI/CD pipelines |
| `docker` | Container configuration |
| `deps` | Dependencies |
| `docs` | Documentation |

---

## Validation Rules

### Header Rules

| Rule | Value | Severity |
|------|-------|----------|
| `header-max-length` | 72 characters | Error |
| `header-min-length` | 10 characters | Error |
| `header-full-stop` | Never (no trailing period) | Error |
| `header-trim` | Always (no leading/trailing whitespace) | Error |

### Subject Rules

| Rule | Value | Severity |
|------|-------|----------|
| `subject-case` | Never sentence-case, start-case, pascal-case, upper-case | Error |
| `subject-empty` | Never (required) | Error |
| `subject-full-stop` | Never (no trailing period) | Error |

### Body Rules

| Rule | Value | Severity |
|------|-------|----------|
| `body-leading-blank` | Always (blank line before body) | Error |
| `body-max-line-length` | 100 characters | Error |
| `body-min-length` | 0 (optional body) | Disabled |

### Footer Rules

| Rule | Value | Severity |
|------|-------|----------|
| `footer-leading-blank` | Always (blank line before footer) | Error |
| `footer-max-line-length` | 100 characters | Error |
| `references-empty` | Never (warn if no issue refs) | Warning |
| `signed-off-by` | Optional | Disabled |

---

## Pre-commit Integration

### Commit Message Hooks

```yaml
# .pre-commit-config.yaml (excerpt)
repos:
  - repo: local
    hooks:
      - id: cocogitto
        name: cocogitto (conventional commits check)
        entry: cog check --from-latest-tag
        language: system
        stages: [commit-msg]
        pass_filenames: false

      - id: commitlint
        name: commitlint (header/body/footer validation)
        entry: npx --no -- commitlint --edit
        language: system
        stages: [commit-msg]
        pass_filenames: false
```

### Execution Order

1. **cocogitto**: Validates commit type/scope against cog.toml
2. **commitlint**: Validates header/body/footer structure

Both must pass for commit to succeed.

---

## CI/CD Workflow

### lint-commits.yml

Three parallel jobs:

| Job | Tool | Purpose |
|-----|------|---------|
| `cocogitto` | cog check | Validate conventional commits, preview changelog |
| `commitlint` | npx commitlint | Validate message structure |
| `pr-title` | action-semantic-pull-request | Validate PR title (for squash merges) |

---

## Configuration Files

| File | Tool | Purpose |
|------|------|---------|
| `cog.toml` | Cocogitto | Custom types, scopes, changelog, versioning |
| `.commitlintrc.js` | commitlint | Header/body/footer validation rules |
| `.pre-commit-config.yaml` | pre-commit | Hook definitions |
| `.typos.toml` | typos-cli | Spelling exceptions |
| `.markdownlint.json` | markdownlint | Markdown rules |
| `.yamllint.yml` | yamllint | YAML rules |
| `.shellcheckrc` | shellcheck | Shell linting rules |
| `.editorconfig` | editorconfig-checker | Editor settings |
| `taplo.toml` | taplo | TOML formatting |
| `clippy.toml` | clippy | Rust linting |
| `rustfmt.toml` | rustfmt | Rust formatting |
| `ruff.toml` | ruff | Python linting/formatting |
| `.eslintrc.js` | eslint | JS/TS linting |
| `.prettierrc` | prettier | JS/TS/JSON/YAML formatting |
| `.golangci.yml` | golangci-lint | Go linting |

---

## Consequences

### Positive

- Fast local feedback via pre-commit hooks
- Consistent enforcement across all contributors
- SARIF reports provide visibility in GitHub Security tab
- Custom types/scopes support project-specific needs
- Automatic changelog generation from commits
- PR title validation ensures clean merge commits

### Negative

- Two commit linting tools require synchronization (types/scopes must match)
- Node.js dependency for commitlint
- Learning curve for contributors unfamiliar with conventional commits
- Pre-commit hook installation required for local development

### Mitigations

- Document types/scopes in CONTRIBUTING.md
- Provide `cog commit` as interactive alternative
- pre-commit.ci catches developers who skip local hooks
- CI workflow provides clear error messages with examples

---

## References

- [Conventional Commits Specification](https://www.conventionalcommits.org/en/v1.0.0/)
- [commitlint Documentation](https://commitlint.js.org/)
- [commitlint Rules Reference](https://commitlint.js.org/reference/rules.html)
- [Cocogitto Documentation](https://docs.cocogitto.io/)
- [Cocogitto GitHub](https://github.com/cocogitto/cocogitto)
- [pre-commit Framework](https://pre-commit.com/)
- [pre-commit.ci](https://pre-commit.ci/)
- [typos-cli](https://github.com/crate-ci/typos)
- [ruff](https://docs.astral.sh/ruff/)
- [actionlint](https://github.com/rhysd/actionlint)
