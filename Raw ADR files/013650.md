# V2 Strategic Reset: Minimal to Sophisticated Architecture

## Purpose
Document the strategic pivot from sophisticated-first to minimal-first architecture, enabling immediate usability while preserving the path to enterprise features.

## Classification
- **Domain:** Project Governance
- **Stability:** Static
- **Abstraction:** Policy
- **Confidence:** Absolute

## Decision

**APPROVED**: Strategic reset to layered architecture
**Date**: October 12, 2025
**Authorized By**: Project lead
**Status**: ACTIVE - V2 implementation begins now

## The Problem

### V1 Approach (Sophisticated-First)
Patinox v1 aimed directly at the enterprise tier:
- 8-crate workspace with MAPE-K monitoring
- Tower middleware validation from day one
- TypeState patterns and compile-time guarantees
- Git-based evolution and meta-layer analysis

**Result**: Too complex to use during development, blocking validation of core concepts.

### Core Issue Identified
"Framework trap" - built for sophistication that doesn't exist yet:
- ❌ Can't validate design because too complex to use
- ❌ Can't get feedback because no simple entry point
- ❌ Implementation stalls (gap between nothing and everything is too large)
- ❌ No working agents despite months of planning

## The Solution

### V2 Approach (Minimal-First with Progressive Enhancement)

**Layered Architecture:**
```
Layer 1: Minimal Agent (~150 lines)
├─> Agent + Tool + CLI generation
├─> Simple ReACT loop
└─> Working agent in Week 1

Layer 2: Plugin Enhancements
├─> Memory, Discovery, Resources
├─> Opt-in complexity
└─> Based on real usage needs

Layer 3: Reasoning Patterns
├─> Plan-Execute, Reflexion
├─> Multi-step orchestration
└─> When simple agents prove insufficient

Layer 4: Enterprise Features (V1 Work)
├─> MAPE-K monitoring
├─> Tower validation
├─> Git-based evolution
└─> Import from V1 when validated
```

## What Changes

### Architecture Philosophy
- **Was**: Build comprehensive framework for future needs
- **Now**: Build minimal framework, add sophistication from real needs

### Development Sequence
- **Was**: Define all abstractions → Implement foundation → Build features
- **Now**: Working example → Use it → Feel pain → Add features

### Validation Strategy
- **Was**: Comprehensive test suite before first use
- **Now**: Working agent validates core, tests grow with features

### Success Metric
- **Was**: Architecture completeness
- **Now**: Time to first working agent (target: Day 1)

## What Doesn't Change

### Core Vision
Patinox still aims to be the most reliable, observable AI agent framework in Rust. The layered approach is a better path to that goal.

### Target Users
- Individual developers (now accessible at Layer 1-2)
- Production systems (Layer 4 when ready)
- Progressive enhancement serves both

### Technology Foundation
- Rust for safety and performance
- Async with Tokio
- Multi-provider support
- Type-safe abstractions (introduced progressively)

## V1 Work Status

### Not Wasted - Repositioned as Research
V1 development validated:
- ✅ Problem space understanding
- ✅ Provider abstraction design
- ✅ Validation logic patterns
- ✅ Memory management approaches
- ✅ What enterprise tier should look like

### Preserved for Salvage
All V1 code preserved in:
- Git branch: `archive/patinox-v1-sophisticated-first`
- Git tag: `v1-research-phase`
- Directory: `src-v1-enterprise/` (in V2 repository)
- Context network: `context-network/archive/v1-research/`

### Import Strategy
V2 will import proven V1 components when validated:
- Provider implementations (already solid)
- Validation logic (as Layer 3-4 plugins)
- Memory management (as Layer 2 plugins)
- Test utilities and patterns

## V2 Implementation Plan

### Week 1: Minimal Core
**Goal**: Working agent you can actually use

```rust
use patinox::*;

fn main() {
    create_agent("hello")
        .tool_fn("greet", "Say hello", |name| {
            Ok(format!("Hello, {}!", name))
        })
        .run_cli()
}
```

**Success Criteria:**
- [ ] Example compiles
- [ ] Example runs with real LLM
- [ ] Can add custom tools
- [ ] Used for something real

### Week 2-3: Plugin Layer
**Goal**: Add sophistication only where needed

Based on Week 1 usage discoveries:
- Memory if needed
- Discovery if needed
- Resource management if needed

**Success Criteria:**
- [ ] 2-3 useful agents built
- [ ] Pain points identified and addressed
- [ ] Plugin architecture proven

### Week 4+: Import V1 Gems
**Goal**: Bring in sophisticated features when validated

- Import provider code
- Add validation as plugins
- Introduce monitoring when needed
- Build enterprise tier incrementally

## Risk Mitigation

### Risk: Lose V1 Investment
**Mitigation**: Everything archived, tagged, documented. Nothing lost, just repositioned.

### Risk: Repeat V1 Mistakes
**Mitigation**: CLAUDE.md updated to prevent AI agents from being pulled back to sophisticated-first approach.

### Risk: Stay Too Simple
**Mitigation**: V1 code ready to import. Enterprise features are the validated destination, not abandoned.

### Risk: Context Confusion
**Mitigation**: Clear archival structure, updated project definition, V2-specific planning docs.

## Success Criteria

### Immediate (Week 1)
- [ ] First working agent deployed
- [ ] Actually used for real task
- [ ] Core concepts validated

### Short-term (Month 1)
- [ ] 5+ working agents in use
- [ ] Plugin architecture proven
- [ ] Clear path to sophistication

### Long-term (Quarter 1)
- [ ] V1 enterprise features imported as validated plugins
- [ ] Both simple and sophisticated use cases supported
- [ ] Clear progression path documented

## Documentation Impact

### CLAUDE.md Updates
Added V2 strategy section:
- Explains layered approach
- References V1 as research/enterprise target
- Prevents sophisticated-first pull
- Sets incremental complexity expectation

### README.md Updates
- Remove enterprise features (roadmap only)
- Show simple examples first
- Progressive enhancement narrative
- V1 mentioned as future enterprise tier

### Context Network Reorganization
- V1 planning → `archive/v1-research/`
- V2 planning in active `planning/`
- Clear separation of concerns
- Archive documented with README

## Authorization

**Project Lead**: ✓ APPROVED
- Strategic reset validated
- Layered approach authorized
- V1 preservation confirmed
- V2 implementation begins

**AI Collaborator**: ✓ ACKNOWLEDGED
- V2 strategy understood
- Will prevent sophisticated-first drift
- Will build incrementally from minimal
- Will import V1 gems when validated

## Relationships
- **Supersedes:** [decisions/begin_coding_decision.md] (V1 approach)
- **Archives:** [decisions/architectural_decisions_resolved.md] (preserved for Layer 4)
- **Preserves:** All V1 work as research and import source
- **Enables:** Immediate usability with clear sophistication path

## Metadata
- **Created:** October 12, 2025
- **Last Updated:** October 12, 2025
- **Updated By:** Development Team
- **Priority:** CRITICAL - Strategic Direction
- **Status:** ACTIVE - V2 Implementation Authorized
- **Restored:** October 13, 2025 (file was accidentally deleted in commit bc6820a)

## Change History
- October 12, 2025: Created V2 strategic reset decision with full archival plan
- October 13, 2025: Restored from commit fabaac0 after accidental deletion
