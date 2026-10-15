# ADR-001: Plugin Architecture

**Status:** Accepted
**Date:** 2025-11-27
**Deciders:** Project Catalyst Team
**Technical Story:** Phase 1 Foundation & Infrastructure

---

## Context

### Background

Project Catalyst is a Claude Code plugin providing language-agnostic project utilities through AI-powered analysis and 40+ production-ready templates. The plugin must integrate seamlessly with Claude Code's plugin system while maintaining strict project isolation and token optimization.

### Critical Requirements

1. **Anthropic Compliance:** Must follow all official Claude Code plugin specifications
2. **Project Isolation:** 100% enforcement to prevent context contamination between projects
3. **Token Optimization:** Target 87% reduction through progressive disclosure and caching
4. **Production Quality:** Comprehensive testing (80%+ coverage), security validation
5. **Maintainability:** Clear structure for 12-week development and long-term maintenance
6. **Extensibility:** Support for phased template expansion (15 → 25 → 40+)

### Technical Constraints

- **Mandatory Naming:** Skills MUST use `SKILL.md` (case-sensitive)
- **Hooks Format:** Must use `hooks.json` (JSON, not YAML)
- **Path Variables:** All paths must use `${CLAUDE_PLUGIN_ROOT}`
- **Isolation:** All local-memory operations must use `session_filter_mode: "session_only"`
- **MCP Integration:** Must gracefully degrade if MCP servers unavailable

**Sources:**
- [Claude Code Plugins Reference](https://code.claude.com/docs/en/plugins-reference)
- [Claude Code Hooks Documentation](https://code.claude.com/docs/en/hooks)
- [Anthropic Plugin Development Toolkit](https://github.com/anthropics/claude-code/blob/main/plugins/plugin-dev/README.md)

---

## Decision

### Chosen Architecture: Multi-Component Plugin with Strict Conventions

We adopt a **multi-component plugin architecture** with mandatory naming conventions, strict isolation enforcement, and progressive disclosure patterns.

### Core Structure

```
project-catalyst/
├── plugin.json                      # Manifest (MANDATORY fields)
├── README.md                        # User documentation
├── MASTER-PLAN.md                   # Implementation plan
├── CONTRIBUTING.md                  # Contribution guidelines
├── LICENSE                          # MIT License
│
├── skills/                          # AI Skills (intelligence layer)
│   ├── project-analyzer/
│   │   ├── SKILL.md                # ⚠️ MANDATORY filename
│   │   ├── reference.md            # Optional detailed docs
│   │   ├── assets/                 # Detection patterns, rules
│   │   └── scripts/                # Python/bash utilities
│   └── utility-generator/
│       ├── SKILL.md                # ⚠️ MANDATORY filename
│       └── scripts/
│
├── templates/                       # Pre-built templates (phased)
│   ├── git/
│   ├── documentation/
│   ├── ci-cd/
│   ├── setup/
│   └── quality/
│
├── commands/                        # Slash commands
│   ├── analyze-project.md
│   ├── apply-template.md
│   ├── optimize-setup.md
│   ├── health-check.md
│   └── onboard.md
│
├── hooks/
│   └── hooks.json                  # ⚠️ MUST be JSON (not YAML)
│
├── scripts/                         # Utilities and validators
│   ├── lib/
│   │   └── session-utils.js       # Isolation helpers
│   ├── check-analyzed.sh
│   ├── validate-template.sh
│   ├── validate-isolation.sh       # 100% coverage enforcer
│   └── validate-plugin.sh          # CI/CD integration
│
├── tests/                           # Comprehensive test suite
│   ├── unit/                       # 75 tests
│   ├── integration/                # 20 tests
│   └── e2e/                        # 5 tests
│
└── docs/                            # Development documentation
    ├── adr/                        # Architecture Decision Records
    ├── sdd/                        # Software Design Documents
    ├── guides/                     # User guides
    └── api/                        # API documentation
```

### Key Architectural Principles

**1. Convention Over Configuration**
- Mandatory file names (`SKILL.md`, `hooks.json`) ensure predictability
- Standard directory structure enables tooling and automation
- Consistent patterns reduce cognitive load

**2. Progressive Disclosure**
- Skills load in 3 levels: metadata → SKILL.md → supporting files
- Templates load on-demand, not all at once
- Token usage scales with actual need

**3. Strict Isolation Enforcement**
- All local-memory operations verified at runtime
- `validate-isolation.sh` runs pre-commit (100% coverage)
- Helper functions (`createIsolatedParams()`) prevent violations

**4. Graceful Degradation**
- MCP server failures don't break core functionality
- Fallback to local file storage when needed
- Clear error messages guide recovery

**5. Path Portability**
- `${CLAUDE_PLUGIN_ROOT}` ensures plugin works anywhere
- No hardcoded paths
- Cross-platform compatibility (Windows, macOS, Linux)

---

## Considered Alternatives

### Alternative 1: Monolithic Single-Skill Plugin

**Pros:**
- Simpler structure
- Faster initial development
- Less cognitive overhead

**Cons:**
- Poor scalability (40+ templates in one Skill)
- Token inefficiency (loads everything always)
- Hard to maintain as complexity grows
- Violates progressive disclosure principle

**Why Not Chosen:**
Progressive disclosure requires componentization. A 40+ template plugin cannot efficiently load all context at once without hitting token limits.

### Alternative 2: YAML Configuration for Hooks

**Pros:**
- More human-readable than JSON
- Common in other systems
- Easier to write manually

**Cons:**
- **Violates Anthropic specification** (hooks MUST be JSON)
- Inconsistent with Claude Code ecosystem
- Would fail plugin validation

**Why Not Chosen:**
Anthropic Documentation explicitly requires `hooks.json` format. Using YAML would cause validation failures and ecosystem incompatibility.

**Source:** [Claude Code Hooks Documentation](https://code.claude.com/docs/en/hooks)

### Alternative 3: Flexible Skill Naming (skill.md, analyzer.md, etc.)

**Pros:**
- More expressive file names
- Easier to identify Skill purpose
- Common in other systems

**Cons:**
- **Violates Anthropic specification** (MUST be `SKILL.md`)
- Claude Code won't recognize Skills
- Breaks plugin loader

**Why Not Chosen:**
Claude Code's Skill loader specifically searches for `SKILL.md` (case-sensitive). Alternative names would cause Skills to be ignored.

**Source:** [Claude Code Plugins Documentation](https://code.claude.com/docs/en/plugins#next-steps)

---

## Consequences

### Positive

1. **Anthropic Compliance:** 100% adherence to official specifications
2. **Predictable Structure:** Standard conventions enable tooling and automation
3. **Token Efficiency:** Progressive disclosure reduces token usage by 87%
4. **Isolation Guarantee:** Runtime verification prevents contamination
5. **Maintainability:** Clear separation of concerns across components
6. **Extensibility:** Easy to add new Skills, templates, commands
7. **Testability:** Each component can be tested independently

### Negative

1. **Learning Curve:** Contributors must learn conventions (mitigated by clear docs)
2. **Strictness:** Less flexibility in naming/structure (mitigated by rationale in ADRs)
3. **Boilerplate:** More files required than monolithic approach (mitigated by templates)
4. **Validation Overhead:** Must run validators pre-commit (mitigated by automation)

### Risks

**Risk 1: Breaking Changes in Claude Code**
- **Impact:** Plugin conventions could change
- **Probability:** Low (stable API)
- **Mitigation:** Version pinning, integration tests, monitoring release notes

**Risk 2: Isolation Enforcement Gaps**
- **Impact:** Context contamination between projects
- **Probability:** Medium (human error in new code)
- **Mitigation:** 100% test coverage, pre-commit validation, runtime checks

**Risk 3: Complexity Creep**
- **Impact:** Structure becomes unwieldy as plugin grows
- **Probability:** Medium (40+ templates + features)
- **Mitigation:** Modular design, clear boundaries, periodic refactoring

---

## Implementation Notes

### Phase 1 (Weeks 1-2): Foundation

**Critical Files:**
1. `plugin.json` - Manifest with MANDATORY fields
2. `hooks/hooks.json` - Event hooks (JSON format)
3. `scripts/lib/session-utils.js` - Isolation helpers
4. `scripts/validate-isolation.sh` - 100% coverage enforcer

**Validation:**
- All paths use `${CLAUDE_PLUGIN_ROOT}`
- All Skills named `SKILL.md`
- Hooks in JSON format
- Isolation verified at runtime

### Phase 2 (Weeks 3-4): Templates & Commands

**Focus:**
- 15 MVP templates in phased structure
- 5 slash commands
- Template validator

### Phase 3-6 (Weeks 5-12): Skills, Testing, Launch

**Focus:**
- Analyzer Skill with local-memory integration
- Utility-generator Skill
- Comprehensive test suite
- Documentation and launch

---

## References

### Official Documentation

1. [Claude Code Plugins Reference](https://code.claude.com/docs/en/plugins-reference#plugin-components-reference)
2. [Claude Code Hooks Documentation](https://code.claude.com/docs/en/hooks)
3. [Claude Code Plugins Documentation](https://code.claude.com/docs/en/plugins#next-steps)
4. [Plugin Development Toolkit](https://github.com/anthropics/claude-code/blob/main/plugins/plugin-dev/README.md)

### Research & Patterns

5. [Anthropic Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
6. [Anthropic Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval)

### Project Documentation

7. [MASTER-PLAN.md](../../MASTER-PLAN.md) - Complete implementation plan
8. [README.md](../../README.md) - Project overview
9. [PROJECT-ISOLATION-SETUP.md](C:\localmemory\PROJECT-ISOLATION-SETUP.md) - Isolation patterns

### Related Plugins (Reference Implementations)

10. Multi-Agent Command Pattern: `C:\Users\jcmei\.claude\plugins\marketplaces\claude-code-workflows\plugins\git-pr-workflows\`
11. Multi-File Skill Structure: `C:\Users\jcmei\.claude\plugins\marketplaces\claude-code-workflows\plugins\shell-scripting\`
12. Token Optimization: `C:\Users\jcmei\.claude\skills\context-optimizer.md`

---

## Validation

### Success Criteria

**Plugin Validation:**
- ✅ Passes `npx @anthropic-ai/plugin-validator ./`
- ✅ All Skills recognized by Claude Code
- ✅ Hooks trigger correctly
- ✅ Commands appear in slash command menu

**Isolation Verification:**
- ✅ 100% of local-memory operations use `session_filter_mode: "session_only"`
- ✅ `validate-isolation.sh` passes on every commit
- ✅ No cross-project context contamination in testing

**Token Optimization:**
- ✅ First analysis: < 1,500 tokens
- ✅ Cached operations: < 200 tokens
- ✅ 87% reduction achieved vs naive approach

**Integration:**
- ✅ Plugin installs via `claude plugin add gh:jcmrs/project-catalyst`
- ✅ Works on Windows, macOS, Linux
- ✅ Graceful degradation without MCP servers

### Metrics

**Code Quality:**
- Test coverage: 80%+ overall, 100% for isolation logic
- Lint errors: 0
- Security vulnerabilities: 0

**Performance:**
- Analyzer execution: < 5 seconds
- Template application: < 2 seconds
- Memory footprint: < 50MB

**Documentation:**
- All ADRs complete
- User guides complete (4)
- API documentation complete

---

**Last Updated:** 2025-11-27
**Related ADRs:**
- [ADR-002: Analyzer Design](./002-analyzer-design.md)
- [ADR-003: Template System](./003-template-system.md)
- [ADR-004: Isolation Enforcement](./004-isolation-enforcement.md)
- [ADR-005: Token Optimization](./005-token-optimization.md)
- [ADR-006: Distribution Strategy](./006-distribution-strategy.md)
