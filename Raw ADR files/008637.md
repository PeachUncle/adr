# 0003 - Adopt Architecture Decision Records

**Status:** Accepted

**Date:** 2025-11-26

**Deciders:** Marcelo Almeida (repository owner)

## Context

DevMagic has made several significant architectural decisions (migrating to Dev Container Features, implementing automatic dotfiles installation, choosing Homebrew over Conda, etc.). These decisions were well-thought-out with clear rationale, but the reasoning was scattered across:

- Git commit messages
- Code comments
- Ad-hoc documentation in `docs/blog-devmagic-refactoring-learnings.md`
- Chat logs in `docs/ai-chats/`

**Problems with this approach:**

1. **Discoverability** - Hard to find "why" a decision was made
2. **Context loss** - Alternatives considered are forgotten over time
3. **Onboarding difficulty** - New contributors (or future self) must piece together history
4. **Decision justification** - When questioned, rationale isn't easily referenced
5. **Pattern repetition** - Can't easily see if similar decisions were made before

As a solo-maintained project that may grow, capturing architectural decisions systematically will help maintain long-term clarity.

## Decision

Adopt **Architecture Decision Records (ADRs)** using Michael Nygard's template:

- Store ADRs in `docs/adr/` directory
- Use sequential numbering: `0001-title.md`, `0002-title.md`, etc.
- Follow simple template: Status, Context, Decision, Alternatives, Consequences
- Keep ADRs immutable - supersede with new ADRs rather than editing
- Index all ADRs in `docs/adr/README.md`

**Initial ADRs created:**

- 0001 - Use Dev Container Features
- 0002 - Automatic Dotfiles Installation
- 0003 - Adopt Architecture Decision Records (this document)

## Alternatives Considered

### Option 1: Continue with current documentation approach

**Rejected** because:
- Information remains scattered
- No systematic way to capture decisions
- Difficult to reference specific decisions
- Onboarding friction remains high

### Option 2: Use RFCs (Request for Comments)

**Rejected** because:
- Heavier weight process
- Implies multi-person review/approval
- ADRs are simpler for solo-maintained projects
- Can adopt RFCs later if project grows

### Option 3: Use decision log in single document

**Rejected** because:
- Single file becomes unwieldy over time
- Hard to link to specific decisions
- No clear lifecycle per decision
- Merge conflicts if multiple decisions in progress

### Option 4: Use GitHub Issues/Discussions for decisions

**Rejected** because:
- Not co-located with code
- Can be closed/deleted
- Harder to maintain index
- Less discoverable in repository

## Consequences

### Positive

- **Clearer decision history** - Easy to see what was decided and why
- **Better onboarding** - New contributors understand architectural choices
- **Reduced repetition** - Can reference existing ADRs for similar decisions
- **Improved communication** - Clear format for discussing architectural changes
- **Living documentation** - ADRs live alongside code, not separate wiki
- **Industry standard** - Used by AWS, Azure, Kubernetes, many open-source projects
- **Lightweight** - Simple markdown, no special tooling required

### Negative

- **Initial overhead** - Need to write ADRs for past decisions (one-time cost)
- **Discipline required** - Must remember to create ADR for significant decisions
- **Potential staleness** - ADRs can become outdated if not superseded properly

### Neutral

- ADRs are immutable by convention (append or supersede, don't edit)
- "Significant" is subjective - will learn over time what warrants ADR
- Can be referenced in commit messages: "Implements ADR-0002"

## Notes

**What warrants an ADR?**

- Changes to core architecture or infrastructure
- Technology/framework choices (languages, libraries, tools)
- Significant trade-offs between alternatives
- Decisions that affect multiple components/users
- Patterns that should be followed consistently

**What doesn't need an ADR?**

- Bug fixes
- Refactoring with no architectural impact
- Documentation improvements
- Minor configuration changes
- Single-file changes with no broader implications

**Template location:** `docs/adr/template.md`

**Related Documentation:**
- `.github/copilot-instructions.md` - Single source of truth for AI assistant context (see [ADR-0004](0004-consolidate-ai-context-files.md))
- `docs/ARCHITECTURE.md` - High-level architecture overview

**References:**
- [Michael Nygard's ADR template](http://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions)
- [GitHub ADR organization](https://adr.github.io/)
- [ADR examples repository](https://github.com/joelparkerhenderson/architecture-decision-record)
- [AWS ADR guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/welcome.html)
