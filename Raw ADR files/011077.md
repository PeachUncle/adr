# No Python Policy for TypeScript Development Environment

## Purpose
This document records the decision to explicitly exclude Python from the development environment to keep AI agents focused on TypeScript solutions.

## Classification
- **Domain:** Architecture
- **Stability:** Static
- **Abstraction:** Conceptual
- **Confidence:** Established

## Content

### Context

When building a TypeScript development environment optimized for AI agents, we observed that LLMs have strong training data biases toward Python for data analysis, scripting, and database operations. This creates a problem:

**The Problem:**
- AI agents naturally gravitate toward Python solutions due to training data
- Python scripts proliferate even in TypeScript-focused projects
- This creates a fragmented codebase (TypeScript + Python)
- Developers must context-switch between languages
- TypeScript expertise doesn't transfer to Python scripts
- Python introduces another runtime and dependency management system

**Key Observations:**
- Most Python usage in dev environments is for "helper scripts"
- Deno + TypeScript can handle everything Python does in this context
- AI agents will use Python reflexively unless explicitly prevented
- The availability of Python in PATH triggers AI agent Python suggestions

### Decision

**We will maintain a strict no-Python policy in this development environment:**

1. **No Python interpreter** in the DevContainer or production images
2. **No pip or Python package managers** installed
3. **No Python scripts** in the repository
4. **All tooling and scripting** will be TypeScript via Deno
5. **AI agents will be instructed** that Python is not available

This is enforced at the infrastructure level: Python simply doesn't exist in the environment.

### Status
Accepted (2025-09-28)

### Consequences

**Positive Consequences:**
- Forces AI agents to produce TypeScript solutions
- Single-language codebase for all tooling
- Developers only need TypeScript expertise
- Faster context switching (no mental language switching)
- Deno's TypeScript support provides excellent scripting capabilities
- Eliminates Python dependency management issues
- Smaller container images (no Python installation)
- Clear constraints improve AI agent decision quality

**Negative Consequences:**
- Cannot leverage Python-specific libraries or tools
- Some AI agents may initially struggle or suggest installing Python
- Must find TypeScript alternatives for traditionally Python tasks
- Some data science workflows may be more complex without Python
- Team members with Python expertise cannot leverage it here

**Risks Introduced:**
- May encounter tasks where Python would have been easier
- TypeScript ecosystem may lack direct equivalents for some Python tools
- AI agents might produce suboptimal solutions without Python option
- Future tools we want to integrate might require Python

**Trade-offs Made:**
- Language flexibility vs. codebase consistency
- Python's data science ecosystem vs. TypeScript-native solutions
- Short-term convenience vs. long-term maintainability

### Alternatives Considered

#### Alternative 1: Python Available, AI Agents Discouraged
Install Python but instruct AI agents to prefer TypeScript.

**Pros:**
- Flexibility when Python is truly the best tool
- Can leverage Python libraries if needed
- Less restrictive for edge cases
- Easier to integrate Python-based tools

**Cons:**
- AI agents will still suggest Python frequently
- Instructions alone won't overcome training data bias
- Requires constant vigilance to prevent Python creep
- Eventually results in a mixed codebase anyway

#### Alternative 2: Python for Data Analysis Only
Allow Python specifically for data analysis and ML tasks.

**Pros:**
- Leverages Python's strengths in data science
- More pragmatic approach
- Easier integration with ML workflows
- Can use Jupyter notebooks for exploration

**Cons:**
- Creates an exception that AI agents will exploit
- "Data analysis" boundary becomes fuzzy
- Still requires Python in the environment
- Doesn't prevent the fragmentation we're trying to avoid

#### Alternative 3: Allow Python but Enforce Strict Boundaries
Use linting and CI checks to limit Python to specific directories.

**Pros:**
- Compromise between flexibility and consistency
- Clear boundaries enforced by tooling
- Can use Python where it genuinely makes sense

**Cons:**
- Requires additional tooling and enforcement
- AI agents may still suggest Python inappropriately
- Doesn't address the root cause (training data bias)
- More complex mental model for developers

### Implementation Notes

**DevContainer Configuration:**
```dockerfile
# Explicitly DO NOT install Python
# No pip, no python3, no conda
# Only Deno and Node.js
```

**AI Agent Instructions:**
Clear statements in CLAUDE.md and system prompts:
- "Python is not available in this environment"
- "Use TypeScript via Deno for all scripting"
- "Do not suggest Python solutions"

**Validation:**
The `scripts/doctor.ts` health check explicitly verifies that Python is NOT installed:
```typescript
// Check that Python is NOT in the environment
const noPython = await checkCommandNotExists("python");
const noPython3 = await checkCommandNotExists("python3");
```

**What We Use Instead:**
- **Deno scripts** for all automation and tooling
- **TypeScript** for data transformations
- **Kuzu (via Deno)** for graph database operations
- **DuckDB (via Deno)** for analytics and data queries
- **ts-morph** for AST analysis (instead of Python's ast module)
- **Deno's standard library** for file operations and utilities

## Relationships
- **Parent Nodes:**
  - [foundation/principles.md] - implements - Simplicity and consistency principles
  - [foundation/project_definition.md] - supports - TypeScript-focused development goals
- **Child Nodes:** None
- **Related Nodes:**
  - [adr_002_deno_node_runtime_split.md] - complements - Both create clear boundaries
  - [architecture/tooling_architecture.md] - influences - Shapes tooling choices
  - [cross_cutting/ai_agent_guidelines.md] - enforces - AI agents respect this policy

## Navigation Guidance
- **Access Context:** Reference when AI agents suggest Python or when considering new tools
- **Common Next Steps:** Review TypeScript alternatives for traditionally Python tasks
- **Related Tasks:** Tool selection, script development, AI agent prompting
- **Update Patterns:** Only revisit if TypeScript ecosystem proves insufficient

## Metadata
- **Decision Number:** ADR-003
- **Created:** 2025-09-30
- **Last Updated:** 2025-09-30
- **Updated By:** Claude (AI Agent)
- **Deciders:** Development team, based on AI agent behavior observations

## Change History
- 2025-09-30: Initial creation based on implementation guide documentation