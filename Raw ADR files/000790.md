---
docid: ADR-080
title: ADR 037 Lifecycle Stages Framework
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

﻿---
docid: ADR-037
title: Lifecycle Stages Framework
status: Accepted
date: 2026-01-05
accepted-date: 2026-01-05
decision-makers: "@SARAH, @Architect, @TechLead"
consulted: "@DevOps, @ProductOwner"
informed: "All agents"
supersedes: null
related: "GL-014, GL-013"
---

# ADR-037: Lifecycle Stages Framework

## Status

**Accepted** - Approved by @Architect, @TechLead on 2026-01-05

## Context

B2X is currently in pre-release development (version 0.x), governed by [GL-014]. As the project matures toward v1.0 and beyond, we need a comprehensive lifecycle management framework that:

1. **Defines clear stages** from experimental to end-of-life
2. **Sets expectations** for stability, breaking changes, and support
3. **Enables component-level tracking** (different components may be at different stages)
4. **Automates enforcement** via CI/CD and tooling
5. **Communicates status** to developers and stakeholders

### Current Limitation

GL-014 only covers the pre-release phase. We lack:
- Formal definition of other stages (Alpha, RC, Stable, LTS, Maintenance, EOL)
- Stage transition criteria
- Component-level stage tracking
- Tooling integration

## Decision

We will implement a **7-stage lifecycle framework** with both project-level and component-level tracking.

### Lifecycle Stages

```
┌─────────────────────────────────────────────────────────────────┐
│                    B2X Lifecycle Stages                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐    ┌─────────────┐    ┌────────────────┐         │
│  │  ALPHA   │───▶│ PRE-RELEASE │───▶│ RELEASE        │         │
│  │  0.0.x   │    │   0.x.x     │    │ CANDIDATE      │         │
│  └──────────┘    └─────────────┘    │ 1.0.0-rc.x     │         │
│       │                              └───────┬────────┘         │
│       │                                      │                  │
│       │ (experimental                        ▼                  │
│       │  abandoned)              ┌───────────────────┐          │
│       │                          │     STABLE        │          │
│       ▼                          │     1.x.x         │          │
│  ┌──────────┐                    └─────────┬─────────┘          │
│  │DEPRECATED│◀─────────────────────────────┤                    │
│  │  (EOL)   │                              │                    │
│  └──────────┘                              ▼                    │
│       ▲                          ┌───────────────────┐          │
│       │                          │   MAINTENANCE     │          │
│       │                          │   (security only) │          │
│       │                          └─────────┬─────────┘          │
│       │                                    │                    │
│       │         ┌───────────────┐          │                    │
│       └─────────│      LTS      │◀─────────┘                    │
│                 │  (long-term)  │                               │
│                 └───────────────┘                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Stage Definitions

| Stage | Version Pattern | Stability | Breaking Changes | Deprecation | Support Duration |
|-------|-----------------|-----------|------------------|-------------|------------------|
| **Alpha** | `0.0.x` | 🔴 Experimental | Anytime, no notice | Not required | None |
| **Pre-Release** | `0.x.x` | 🟠 Unstable | Minor version bump | Not required | Best-effort |
| **Release Candidate** | `x.y.z-rc.n` | 🟡 Feature-complete | Blocked (bugs only) | N/A | Until stable |
| **Stable** | `x.y.z` | 🟢 Production | Major version only | Required (1 minor) | Until next major |
| **LTS** | `x.y.z` (tagged) | 🟢 Long-term | Security patches only | Extended (3 minor) | 18-24 months |
| **Maintenance** | `x.y.z` (tagged) | 🔵 Security-only | Critical security only | N/A | 6 months |
| **Deprecated** | N/A | ⚫ End-of-Life | None | N/A | None |

### Stage Policies

#### 1. Alpha (`0.0.x`)

**Purpose**: Proof-of-concept, experimentation, feasibility studies.

| Policy | Value |
|--------|-------|
| API stability | None |
| Documentation | Optional |
| Test coverage | Optional |
| Breaking changes | Anytime |
| Deprecation notice | None |
| Production use | ❌ Prohibited |

**Transition to Pre-Release**: When feature concept is proven and worth developing.

#### 2. Pre-Release (`0.x.x`) — *Current B2X Stage*

**Purpose**: Active feature development, API design iteration.

| Policy | Value |
|--------|-------|
| API stability | None guaranteed |
| Documentation | Encouraged |
| Test coverage | >60% target |
| Breaking changes | Allowed (minor bump) |
| Deprecation notice | Not required |
| Production use | ⚠️ At own risk |

**Governed by**: [GL-014]

**Transition to RC**: All features complete, API freeze declared.

#### 3. Release Candidate (`x.y.z-rc.n`)

**Purpose**: Final testing, documentation polish, performance tuning.

| Policy | Value |
|--------|-------|
| API stability | Frozen |
| Documentation | Required (complete) |
| Test coverage | >80% required |
| Breaking changes | ❌ Blocked |
| Bug fixes | Allowed (rc.n bump) |
| Production use | ⚠️ Early adopters only |

**Duration**: 2-4 weeks typical

**Transition to Stable**: @QA sign-off, @Security audit passed, docs complete.

#### 4. Stable (`x.y.z`)

**Purpose**: Production-ready, fully supported release.

| Policy | Value |
|--------|-------|
| API stability | Guaranteed within major |
| Documentation | Required |
| Test coverage | >80% maintained |
| Breaking changes | Major version only |
| Deprecation notice | Minimum 1 minor version |
| Production use | ✅ Recommended |

**Semantic Versioning Enforced**:
- MAJOR: Breaking changes
- MINOR: New features (backwards compatible)
- PATCH: Bug fixes

#### 5. LTS (Long-Term Support)

**Purpose**: Extended support for enterprise deployments.

| Policy | Value |
|--------|-------|
| API stability | Frozen |
| New features | ❌ None |
| Bug fixes | Critical only |
| Security patches | ✅ Yes |
| Deprecation notice | 3 minor versions or 6 months |
| Support duration | 18-24 months |

**Designation**: Specific stable versions tagged as LTS (e.g., `v1.4.0-lts`).

#### 6. Maintenance

**Purpose**: Security-only support for older stable versions.

| Policy | Value |
|--------|-------|
| New features | ❌ None |
| Bug fixes | Critical security only |
| Support duration | 6 months |
| Upgrade path | Documented |

**Entry**: When superseded by new major version or LTS ends.

#### 7. Deprecated (End-of-Life)

**Purpose**: Archived, no longer supported.

| Policy | Value |
|--------|-------|
| Updates | ❌ None |
| Support | ❌ None |
| Documentation | Archived |
| Migration guide | Required |

### Component-Level Stages

Different components can be at different lifecycle stages:

```yaml
# .ai/config/lifecycle.yml (proposed)
project:
  name: B2X
  default-stage: pre-release
  version: 0.8.0

components:
  core-api:
    stage: pre-release
    version: 0.8.0
    
  admin-frontend:
    stage: pre-release
    version: 0.8.0
    
  store-frontend:
    stage: pre-release
    version: 0.8.0
    
  cli:
    stage: alpha
    version: 0.0.3
    note: "Experimental features under development"
    
  erp-connectors:
    stage: alpha
    version: 0.0.1
    note: "Plugin architecture being designed"
    
  search-service:
    stage: pre-release
    version: 0.7.0
```

### Transition Criteria

#### Alpha → Pre-Release
- [ ] Proof-of-concept validated
- [ ] Basic architecture defined
- [ ] Development commitment made
- [ ] @Architect approval

#### Pre-Release → Release Candidate
- [ ] All planned features implemented
- [ ] API freeze declared
- [ ] Database schema frozen
- [ ] >80% test coverage achieved
- [ ] Security audit scheduled
- [ ] @ProductOwner feature sign-off
- [ ] @Architect architecture sign-off

#### Release Candidate → Stable
- [ ] All RC bugs resolved
- [ ] @QA comprehensive testing passed
- [ ] @Security audit passed
- [ ] Documentation complete
- [ ] Performance benchmarks met
- [ ] @TechLead final review
- [ ] @ProductOwner release approval

#### Stable → LTS
- [ ] Version stability proven (3+ months)
- [ ] Enterprise customer demand
- [ ] Support capacity confirmed
- [ ] @ProductOwner LTS designation

#### Stable/LTS → Maintenance
- [ ] Superseded by new major/LTS version
- [ ] Support transition plan documented
- [ ] Migration guide published

#### Maintenance → Deprecated
- [ ] Maintenance period elapsed
- [ ] No critical security issues pending
- [ ] Archive documentation complete

### Tooling Integration

#### 1. CI/CD Stage Enforcement

```yaml
# Proposed CI behavior
stages:
  alpha:
    - Skip backwards compatibility tests
    - Minimal documentation check
    - Allow experimental dependencies
    
  pre-release:
    - Skip backwards compatibility tests
    - Basic documentation check
    - Dependency audit (warning only)
    
  release-candidate:
    - Full test suite required
    - Documentation completeness check
    - Security scan required
    - No new features allowed
    
  stable:
    - Full test suite required
    - Backwards compatibility tests
    - Breaking change detection
    - Deprecation validation
```

#### 2. Stage Badges

```markdown
![Stage: Pre-Release](https://img.shields.io/badge/stage-pre--release-orange)
![Stage: Stable](https://img.shields.io/badge/stage-stable-green)
![Stage: LTS](https://img.shields.io/badge/stage-LTS-blue)
```

#### 3. PR Templates

Stage-aware PR templates with appropriate checklists.

### Documentation Updates

| Document | Action |
|----------|--------|
| [GL-014] | Rename to "Lifecycle Stages Framework" or archive |
| [GL-015] | Create "Stable Release Policy" (activated at v1.0) |
| README.md | Add lifecycle stage badge |
| CONTRIBUTING.md | Document stage-appropriate contribution guidelines |
| PROJECT_DASHBOARD.md | Add component stage tracking |

## Consequences

### Positive

1. **Clear Expectations**: Developers and stakeholders understand stability guarantees
2. **Flexible Development**: Alpha/pre-release components can iterate rapidly
3. **Enterprise Ready**: LTS track supports enterprise deployment needs
4. **Automated Enforcement**: CI/CD validates stage-appropriate behavior
5. **Component Independence**: Different components can evolve at different paces

### Negative

1. **Complexity**: More stages to manage and communicate
2. **Tooling Investment**: CI/CD and documentation tooling required
3. **Cognitive Load**: Team must understand stage implications

### Risks

| Risk | Mitigation |
|------|------------|
| Stage confusion | Clear documentation, badges, automated checks |
| Premature stable declaration | Strict transition criteria, sign-offs |
| LTS support burden | Capacity planning before LTS designation |
| Component stage drift | Regular lifecycle reviews |

## Implementation Plan

### Phase 1: Documentation (Week 1)
- [ ] Finalize this ADR
- [ ] Update GL-014 or create new lifecycle guideline
- [ ] Update DOCUMENT_REGISTRY.md

### Phase 2: Configuration (Week 2)
- [ ] Create `.ai/config/lifecycle.yml`
- [ ] Document current component stages
- [ ] Add stage badges to README

### Phase 3: Tooling (Week 3-4)
- [ ] Create stage-aware PR templates
- [ ] Implement CI stage validation (basic)
- [ ] Add PROJECT_DASHBOARD component tracking

### Phase 4: Automation (Future)
- [x] Basic CI/CD stage validation (`.github/workflows/lifecycle-validation.yml`)
- [ ] Full breaking change detection
- [ ] Automated transition checks
- [ ] Stage change notifications

## Alternatives Considered

### A. Keep Simple (GL-014 only)
- **Pros**: Simpler, less overhead
- **Cons**: No framework for post-v1.0, no component-level tracking
- **Decision**: Rejected — need long-term lifecycle management

### B. Full Semantic Versioning from Start
- **Pros**: Industry standard
- **Cons**: Pre-release overhead, blocks rapid iteration
- **Decision**: Rejected — current GL-014 approach better for 0.x

### C. Stage-per-Guideline
- **Pros**: Clear separation
- **Cons**: Document sprawl, harder to maintain
- **Decision**: Partially adopted — GL-014 becomes lifecycle doc, GL-015 for stable

## References

- [Semantic Versioning 2.0.0](https://semver.org/)
- [GL-014] Pre-Release Development Phase
- [GL-013] Dependency Management Policy
- [Node.js LTS Schedule](https://nodejs.org/en/about/releases/) (inspiration)
- [Ubuntu Release Cycle](https://ubuntu.com/about/release-cycle) (inspiration)

---

**Proposed by**: @SARAH  
**Accepted by**: @Architect, @TechLead  
**Decision date**: 2026-01-05
