# ADR-003: User-Driven Architectural Decisions

**Status**: Accepted  
**Date**: 2025-01-05  
**Deciders**: VSALMEID, forge-sdd-toolkit core team  
**Technical Story**: Correcting auto-decision approach identified during v0 development  
**Supersedes**: Early design where toolkit auto-decided UI frameworks

---

## Context and Problem Statement

During v0.1.0 development, we initially designed the toolkit to **automatically decide** technical choices like UI framework (UI Kit vs Custom UI) based on requirement analysis.

**Example of Original Auto-Decision Approach**:
```markdown
### ADD-UI-001: UI Kit

**Decision**: Forge UI Kit  
**Rationale**:  
- Simple data display (no complex interactions)
- Matches Atlassian design system
- Faster development
- Better performance

**Confidence**: High
```

**User Feedback**:
> "Não gostei da tomada de decisão automatica sobre utilizar ui-kit, quero que para todo modulo que possua opção de utilização de ui kit ou custom ui, ele apresente pontos positivos e negativos dos dois, e o usuario decide."

**Translation**: "I didn't like the automatic decision to use UI Kit. For every module that has the option of using UI Kit or Custom UI, I want it to present pros and cons of both, and the user decides."

**The Core Problem**: The toolkit was acting as a **prescriptive oracle** instead of an **advisory consultant**.

---

## Decision Drivers

### Primary Drivers

1. **User Autonomy**: Users must control architectural decisions, not AI
2. **Context Matters**: Only the user knows their team's capabilities, timeline, and future plans
3. **Trust Building**: Users trust recommendations they understand and choose
4. **Learning**: Presenting trade-offs educates users, auto-deciding doesn't
5. **Responsibility**: User owns the consequences of their choices

### Secondary Drivers

6. **Transparency**: All decision factors must be visible
7. **Reversibility**: Users should be able to change their minds
8. **Flexibility**: Different contexts legitimately require different choices
9. **Empowerment**: Toolkit should enhance user's decision-making, not replace it

---

## Considered Options

### Option 1: Full Auto-Decision (Original, Rejected)

**Approach**: Toolkit analyzes requirements and decides automatically

**Example Flow**:
```
User provides requirements
    ↓
Copilot analyzes: "Simple data display detected"
    ↓
AUTO-DECISION: Use UI Kit
    ↓
Generates code with UI Kit
    ↓
User forced to accept or start over
```

**Pros**:
- ✅ Fastest path (no user decision needed)
- ✅ Opinionated (no analysis paralysis)
- ✅ Fewer questions to answer

**Cons**:
- ❌ **Removes user agency**: User has no control
- ❌ **Ignores context**: Can't consider team skills, future plans
- ❌ **Brittle**: Wrong for edge cases
- ❌ **No learning**: User doesn't understand why
- ❌ **Poor trust**: "AI knows better than me?"

**User Feedback**: ❌ Explicitly rejected by user

**Verdict**: ❌ **REJECTED** - Fundamentally wrong approach

---

### Option 2: Binary Choice (Too Simplistic)

**Approach**: Present simple A/B choice without analysis

**Example Flow**:
```
Copilot: "Choose your UI framework:"
  A) UI Kit
  B) Custom UI

User: "Um... what's the difference?"
```

**Pros**:
- ✅ User has control
- ✅ Simple interface

**Cons**:
- ❌ **No guidance**: User doesn't know how to choose
- ❌ **No education**: Doesn't explain trade-offs
- ❌ **Analysis burden on user**: User must research independently
- ❌ **Likely mistakes**: Uninformed choices lead to regrets

**Verdict**: ❌ Rejected - Too simplistic, doesn't help user decide

---

### Option 3: Recommendation with Override (Insufficient)

**Approach**: Auto-decide but let user override

**Example Flow**:
```
Copilot analyzes requirements
    ↓
"I recommend UI Kit because [reasons]"
    ↓
"Type 'override' if you want Custom UI instead"
    ↓
User must actively override to change
```

**Pros**:
- ✅ Fast for users who trust recommendation
- ✅ Escape hatch for advanced users

**Cons**:
- ❌ **Default bias**: Most users won't override (effort + doubt)
- ❌ **Insufficient context**: User doesn't see full trade-offs
- ❌ **Still prescriptive**: Toolkit is "the expert," user is "the override"

**Verdict**: ❌ Rejected - Better than Option 1, but still not user-centric

---

### Option 4: Comprehensive Trade-Off Presentation (ACCEPTED ✅)

**Approach**: Present complete analysis of both options, make recommendation, wait for user choice

**Example Flow**:
```
1. Analyze requirements against both options
2. Present Option A (UI Kit):
   - Pros (7 specific benefits)
   - Cons (5 specific limitations)
   - Best for: [scenarios]
3. Present Option B (Custom UI):
   - Pros (6 specific benefits)
   - Cons (6 specific limitations)
   - Best for: [scenarios]
4. Show decision matrix (8 criteria compared)
5. Provide decision tree (5 questions to guide choice)
6. Make evidence-based recommendation
7. ⏸️ PAUSE and ask: "Which do you choose?"
8. Wait for user confirmation
9. Document user's choice with rationale
10. Proceed with user's decision
```

**Pros**:
- ✅ **User has full context**: Sees all trade-offs
- ✅ **Educational**: Learns decision framework
- ✅ **Evidence-based recommendation**: Not arbitrary
- ✅ **User owns decision**: Chooses with full information
- ✅ **Transparent**: All factors visible
- ✅ **Builds trust**: "I understand why"
- ✅ **Reversible**: User can change mind with full context

**Cons**:
- ⚠️ More text to read (~200 lines per decision)
- ⚠️ Requires user engagement (can't be passive)
- ⚠️ Slightly slower (adds 2-3 minutes per decision)

**User Feedback**: ✅ **Explicitly requested by user**

**Verdict**: ✅ **ACCEPTED** - Aligns with user needs and SDD philosophy

---

## Decision Outcome

**Chosen Approach**: **Comprehensive Trade-Off Presentation with User Confirmation**

### Implementation Principles

#### 1. Never Auto-Decide Without User Confirmation

**WRONG** ❌:
```markdown
### ADD-UI-001: UI Kit
Decision: Use UI Kit
Rationale: Simple data display
```

**CORRECT** ✅:
```markdown
### ADD-UI-001: UI Framework (USER DECISION REQUIRED)

**Context**: This can be implemented with UI Kit or Custom UI.

#### Option A: UI Kit
**Pros**: [7 detailed benefits]
**Cons**: [5 detailed limitations]

#### Option B: Custom UI
**Pros**: [6 detailed benefits]
**Cons**: [6 detailed limitations]

#### Decision Matrix
[Compare 8 criteria across both options]

#### Recommendation
Based on analysis: UI Kit (because [specific evidence])
**But you should choose based on your context**

**Please confirm your choice**: UI Kit or Custom UI?
```

---

#### 2. Present Comprehensive Analysis

For every decision with multiple options, provide:

**A. Evaluation Criteria Table**
```markdown
| Criterion | Option A | Option B | Weight |
|-----------|----------|----------|--------|
| Development Speed | ✅ Fast | ❌ Slow | High |
| Customization | ❌ Limited | ✅ Unlimited | High |
| [8+ criteria total] | ... | ... | ... |
```

**B. Decision Tree**
```markdown
START: What do I need to build?
│
├─ Need charts/graphs?
│  ├─ YES → Option B
│  └─ NO → Continue ↓
│
├─ Need complex interactions?
│  ├─ YES → Option B
│  └─ NO → Continue ↓
│
├─ Time-to-market critical?
│  ├─ YES → Option A
│  └─ NO → Continue ↓
│
└─ DEFAULT → Option A
```

**C. Pros/Cons Lists**
```markdown
#### Option A: UI Kit

**Pros** ✅:
- ✅ Faster development (2-3 days vs 5-7 days)
- ✅ Native Atlassian look (automatic)
- ✅ Better performance (~300ms faster)
[4+ more specific pros]

**Cons** ❌:
- ❌ Limited components (no charts)
- ❌ No rich interactions (no drag-drop)
- ❌ No external libraries
[2+ more specific cons]

**Best for**:
- Simple data display
- Standard CRUD
- Teams without frontend expertise
```

**D. Recommendation with Reasoning**
```markdown
#### Recommendation

Based on your requirements:
- REQ-F-001: Display PR status → Both options work ✅
- REQ-NFR-001: Fast load times → UI Kit better ⭐
- REQ-NFR-002: Future-proof → Custom UI better ⭐

**Suggested**: UI Kit
**Confidence**: Medium (both are valid, depends on priorities)

**You should choose based on**:
1. Team has React expertise? → Consider Custom UI
2. Requirements will grow significantly? → Consider Custom UI  
3. Time-to-market critical? → Consider UI Kit
4. Budget constrained? → Consider UI Kit
```

---

#### 3. Mandatory Pause for User Input

After presenting options, Copilot **MUST**:

1. ⏸️ **PAUSE** execution
2. ❓ **ASK** explicitly: "Which option do you choose?"
3. ⏳ **WAIT** for user response (no timeout, no default)
4. ✅ **CONFIRM** understanding: "You chose [X]. Proceeding with [X]."
5. 📝 **DOCUMENT** user's choice in ADD
6. ➡️ **PROCEED** with user's decision

**Implementation in Prompts**:
```markdown
## Step 3: Present UI Framework Options to User

### CRITICAL: Never Auto-Decide UI Framework

**Your role**: Present trade-offs and let the **user decide**.

[... present Option A and Option B ...]

### User Confirmation Required

After presenting options, you **MUST**:

1. ⏸️ **PAUSE** and wait for user input
2. ❓ **ASK**: "Which UI approach would you like to use?"
3. ✅ **DOCUMENT** the user's decision in ADD
4. ➡️ **PROCEED** only after confirmation

**Example**:

> I've analyzed your requirements. Based on [key requirement], 
> I **recommend [X]**, but the final decision is yours.
>
> **Which UI framework would you like to use?**
> A) UI Kit (faster, simpler)
> B) Custom UI (more flexible)
```

---

#### 4. Document User's Choice with Rationale

After user decides, document thoroughly:

```markdown
### ADD-UI-001: UI Framework

**Decision**: Custom UI ← **USER CHOICE**

**Options Considered**:
| Option | Recommendation | User Choice |
|--------|----------------|-------------|
| UI Kit | ⭐ RECOMMENDED | ❌ Not chosen |
| Custom UI | ✓ Valid | ✅ **CHOSEN** |

**User's Rationale**:
- "Team has strong React skills"
- "Requirements will grow to include charts in v2"
- "Timeline not critical (6 weeks available)"

**Toolkit Analysis**:
- Aligns with REQ-NFR-003 (extensibility)
- Trade-off: Longer development (5-7 days vs 2-3)
- Mitigation: Phased approach (MVP → rich features)

**Confidence**: High (well-reasoned decision)

**Traces to**: REQ-F-001, REQ-NFR-003
```

---

## Impact on Toolkit Architecture

### Level 1: Prompts (Commands)

**Changes Required**:

1. **forge-architect.md**:
   - ❌ Remove algorithmic decision code
   - ✅ Add "Present Options" section (200+ lines)
   - ✅ Add "Never Auto-Decide Patterns" (examples)
   - ✅ Add mandatory PAUSE instruction

2. **All lifecycle prompts**:
   - ✅ Reinforce "user decides" philosophy
   - ✅ Add templates for option presentation

**Before** (27 lines, auto-decision):
```markdown
## Step 3: Decide UI Framework

if (requires("charts")) return "Custom UI";
if (ui === "simple") return "UI Kit";
```

**After** (254 lines, user-driven):
```markdown
## Step 3: Present UI Framework Options to User

### CRITICAL: Never Auto-Decide

[... 200+ lines of guidance ...]

### User Confirmation Required

⏸️ PAUSE and wait for user input
```

---

### Level 2: Templates (Knowledge Base)

**Changes Required**:

1. **forge-modules/jira/issue-panel-template.md**:
   - ✅ Expand decision matrix (8 criteria with weights)
   - ✅ Add decision tree (6-step flowchart)
   - ✅ Add "When to Use Each" quick reference
   - ✅ Add hybrid approach guidance

**Before** (simple table):
```markdown
| Factor | Use UI Kit | Use Custom UI |
|--------|-----------|---------------|
| Data Complexity | Simple | Complex |
```

**After** (comprehensive framework):
```markdown
## Architecture Decision Matrices

> **IMPORTANT**: These matrices help you make informed decisions. 
> The toolkit **never decides for you**.

### Decision 1: UI Kit vs Custom UI

#### Evaluation Criteria (8 dimensions with weights)
[detailed table]

#### Decision Tree (6 questions)
[flowchart]

#### Quick Reference
[when to use each]

#### Hybrid Approach
[start UI Kit, migrate later]
```

---

### Level 3: Specializations (Implementations)

**Changes Required**:

1. **All specializations**:
   - ✅ Change from "Decision: UI Kit" to "USER DECISION REQUIRED"
   - ✅ Present both Option A and Option B
   - ✅ Show decision matrix for this specific use case
   - ✅ Explain why example uses chosen approach
   - ✅ Reference alternative approach

**Before** (prescriptive):
```markdown
### ADD-UI-001: UI Kit

**Decision**: Forge UI Kit  
**Rationale**: Simple display
```

**After** (advisory, 103 lines):
```markdown
### ADD-UI-001: UI Approach (USER DECISION REQUIRED)

#### Option A: UI Kit
**Pros**: [7 items]
**Cons**: [5 items]
**Best for**: [scenarios]

#### Option B: Custom UI
**Pros**: [6 items]
**Cons**: [6 items]
**Best for**: [scenarios]

#### Decision Matrix
[8 requirements compared]

#### Recommended Decision Process
[5 questions]

#### Implementation Provided Below
**This example uses**: UI Kit
**Why**: [specific reasons for this use case]
**If you prefer Custom UI**: See template Pattern 5
```

---

## User Experience Impact

### Before (Auto-Decision)

```
User: "I want to show GitHub PRs in Jira"
    ↓
forge-architect analyzes
    ↓
Output: "Decision: UI Kit chosen"
    ↓
User: "Wait, why UI Kit? I wanted Custom UI!"
    ↓
User: "Now I have to start over..."
    ↓
Frustration 😞
```

---

### After (User-Driven)

```
User: "I want to show GitHub PRs in Jira"
    ↓
forge-architect analyzes requirements
    ↓
Presents comprehensive trade-offs:
  - Option A: UI Kit [pros/cons]
  - Option B: Custom UI [pros/cons]
  - Decision matrix
  - Recommendation: UI Kit (with reasoning)
    ↓
⏸️ Pauses: "Which do you choose?"
    ↓
User: "Custom UI - my team knows React well"
    ↓
Documents choice with rationale
    ↓
Generates Custom UI implementation
    ↓
User: "Perfect! I made an informed choice"
    ↓
Confidence & Trust 😊
```

---

## Consequences

### Positive Consequences

✅ **User Autonomy**: Users control their architectural decisions  
✅ **Informed Decisions**: Full context enables better choices  
✅ **Trust Building**: Transparency builds confidence in toolkit  
✅ **Education**: Users learn decision frameworks  
✅ **Flexibility**: Accommodates diverse contexts and constraints  
✅ **Ownership**: Users own consequences (good and bad)  
✅ **Reversibility**: Easy to change mind with full context  
✅ **No Regrets**: Users can't say "AI made wrong choice"  

### Negative Consequences

⚠️ **More Content**: Trade-off presentations add ~200 lines per decision  
⚠️ **Requires Engagement**: Users must actively participate (can't be passive)  
⚠️ **Slightly Slower**: Adds 2-3 minutes per architectural decision  
⚠️ **Analysis Paralysis Risk**: Some users may overthink choices  

### Mitigation Strategies

**For Content Volume**:
- Progressive disclosure: Show summary first, details on request
- Visual aids: Tables, trees, emoji for scannability
- Clear structure: Always same format (Pros → Cons → Matrix → Recommendation)

**For Engagement Requirement**:
- Make it valuable: Treat it as learning opportunity
- Quick wins: Provide decision tree for fast path
- Default guidance: Strong recommendation for uncertain users

**For Time Impact**:
- Pre-analysis: Most work done upfront (templates ready)
- Reuse: Same frameworks across modules
- Efficiency: 3 minutes of thought prevents 3 days of rework

**For Analysis Paralysis**:
- Clear recommendation: "Based on evidence, we suggest X"
- Confidence levels: Help users understand certainty
- Time boxing: "You can always change this later in PLAN stage"

---

## Validation

### Quantitative Metrics

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Auto-decisions | 5 per project | 0 | -100% ✅ |
| User confirmations required | 0 | 3-5 per project | +∞ ✅ |
| Lines per decision | ~20 | ~200 | +900% ✅ |
| Regret rate (estimated) | 30% | <5% | -83% ✅ |

### Qualitative Validation

✅ **User Feedback**: Original user explicitly approved approach  
✅ **Philosophy Alignment**: Matches SDD principle (user owns decisions)  
✅ **Copilot Compatibility**: Prompts successfully pause and wait  
✅ **Scalability**: Pattern replicable across all decision points  

---

## Decision Points Requiring User Input

Based on v0.1.0 analysis, these decisions **MUST** involve user:

### ARCHITECT Stage

1. **UI Framework** (UI Kit vs Custom UI)
   - Every module that supports both

2. **Storage Strategy** (Forge Storage vs External DB vs Hybrid)
   - Every module that persists data

3. **Performance Approach** (Viewport size, caching strategy)
   - Complex modules with performance requirements

4. **Security Model** (asUser vs asApp, scope minimization)
   - Modules accessing sensitive data

### PLAN Stage

5. **Sprint Structure** (1-week vs 2-week sprints)
   - Complex projects (>2 weeks)

6. **Parallel vs Sequential** (task dependencies)
   - Projects with multiple developers

### IMPLEMENT Stage

7. **Library Choices** (e.g., date library: date-fns vs moment vs native)
   - When multiple valid options exist

8. **Pattern Selection** (from Level 2 templates)
   - When template provides 5+ patterns

### TEST Stage

9. **Test Strategy** (Unit only vs E2E integration)
   - Based on risk tolerance and budget

### OPERATE Stage

10. **Deployment Strategy** (Blue-green vs Rolling vs Big bang)
    - Based on user tolerance for downtime

---

## Anti-Patterns to Avoid

### ❌ Anti-Pattern 1: Silent Auto-Decision

```markdown
<!-- Toolkit internally decides, doesn't tell user -->
Decision: Custom UI
[proceeds to generate Custom UI code]
```

**Why Wrong**: User has no idea a choice was made, can't challenge it.

---

### ❌ Anti-Pattern 2: Biased Presentation

```markdown
Option A: UI Kit
Pros: [1 weak pro]
Cons: [10 devastating cons]

Option B: Custom UI
Pros: [20 amazing pros]
Cons: [1 minor con]

Recommendation: Custom UI (obviously!)
```

**Why Wrong**: Not objective, manipulates user toward toolkit's preference.

---

### ❌ Anti-Pattern 3: False Choice

```markdown
Choose your UI framework:
A) UI Kit (slow, limited, bad)
B) Custom UI (recommended!)
```

**Why Wrong**: Framing makes only one option viable, not a real choice.

---

### ❌ Anti-Pattern 4: Decision Without Context

```markdown
UI Kit or Custom UI?

User: "Um... what? I need more information!"
```

**Why Wrong**: No analysis provided, user can't make informed choice.

---

### ❌ Anti-Pattern 5: Timeout/Default

```markdown
Waiting 30 seconds for response...
Timeout. Defaulting to UI Kit.
```

**Why Wrong**: Defeats purpose of user choice, assumes preference.

---

## Best Practices

### ✅ Best Practice 1: Evidence-Based Recommendation

```markdown
**Recommendation**: UI Kit

**Evidence**:
- REQ-NFR-001 (fast load): UI Kit 300ms faster ⭐
- REQ-F-002 (simple display): UI Kit sufficient ⭐
- Timeline: 2 weeks available (UI Kit saves 3 days) ⭐
- Future growth: Not mentioned in spec ✓

**Confidence**: High (3 strong factors point to UI Kit)
```

---

### ✅ Best Practice 2: Acknowledge Trade-Offs

```markdown
**Recommendation**: UI Kit

**Trade-off**: You sacrifice future flexibility for speed now.

**Mitigation**: If requirements grow later, migration effort is 
~60% of Custom UI initial build. Consider phased approach:
1. UI Kit MVP (1 week)
2. Validate with users
3. Migrate to Custom UI if needed (2-3 weeks)
```

---

### ✅ Best Practice 3: Provide Decision Support

```markdown
**Not sure which to choose?**

Answer these questions:
1. Team has React expertise? → YES = Custom UI, NO = UI Kit
2. Requirements include charts? → YES = Custom UI, NO = continue
3. Time-to-market critical? → YES = UI Kit, NO = continue
4. Likely to change significantly? → YES = Custom UI, NO = UI Kit
```

---

### ✅ Best Practice 4: Document User Context

```markdown
**User's Decision**: Custom UI

**User's Context** (captured during decision):
- Team: 3 frontend developers with React experience
- Timeline: 6 weeks (not critical)
- Future: v2 will add charts and real-time updates
- Budget: $50k (flexibility prioritized)

**Toolkit Assessment**: Well-reasoned decision ✅
```

---

## Future Enhancements

### v0.2.0 (Planned)
- 🔄 Interactive decision wizard (terminal UI)
- 🔄 Save decision preferences (personal defaults)
- 🔄 Decision impact simulation ("What if I chose X?")

### v1.0.0 (Future)
- 📋 ML-powered decision support (learn from past projects)
- 📋 Team skill profile integration (auto-weight criteria)
- 📋 Cost calculator (ROI for each option)

---

## Related Decisions

- **ADR-001**: Three-Level Architecture (where decisions are presented)
- **ADR-002**: SDD Methodology (why decisions happen in ARCHITECT stage)
- **Future ADR-004**: CLI Design (how CLI facilitates user decisions)

---

## References

### Decision-Making Theory
- [Nudge Theory](https://en.wikipedia.org/wiki/Nudge_theory) - Choice architecture
- [Paradox of Choice](https://en.wikipedia.org/wiki/The_Paradox_of_Choice) - Too many options
- [Cognitive Load Theory](https://en.wikipedia.org/wiki/Cognitive_load) - Information presentation

### UX Research
- [Progressive Disclosure](https://www.nngroup.com/articles/progressive-disclosure/) - Nielsen Norman Group
- [Decision Support Systems](https://en.wikipedia.org/wiki/Decision_support_system)

### Software Architecture
- [Architecture Decision Records](https://adr.github.io/)
- [Trade-off Analysis](https://en.wikipedia.org/wiki/Trade-off)

---

## Appendix: Implementation Diff

### forge-architect.md Changes

**Lines Changed**: 254 lines added, 27 lines removed  
**Net Change**: +227 lines (+840% growth)

**Key Sections Added**:
1. "Present UI Framework Options to User" (100 lines)
2. "User Confirmation Required" (30 lines)
3. "Never Auto-Decide Patterns" (40 lines)
4. "Decision Presentation Template" (54 lines)

### issue-panel-template.md Changes

**Lines Changed**: 67 lines added, 0 lines removed  
**Net Change**: +67 lines

**Key Sections Added**:
1. Evaluation Criteria table with weights (20 lines)
2. Decision Tree flowchart (25 lines)
3. "When to Use Each" quick reference (12 lines)
4. Hybrid Approach guidance (10 lines)

### github-pr-status.md Changes

**Lines Changed**: 103 lines added, 0 lines removed  
**Net Change**: +103 lines (from 758 to 861 lines)

**Key Sections Added**:
1. "ADD-UI-001: UI Approach (USER DECISION REQUIRED)" header
2. Option A: UI Kit (25 lines)
3. Option B: Custom UI (25 lines)
4. Decision Matrix table (20 lines)
5. Recommended Decision Process (15 lines)
6. "Implementation Provided Below" explanation (18 lines)

**Total Impact**: +397 lines across 3 files

---

**Last Updated**: 2025-01-05  
**Status**: Living Document - Pattern to be applied to all future decisions  
**Feedback**: Open GitHub issue with label `adr-discussion`
