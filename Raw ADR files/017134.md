# ADR-0016: Scale Down to MVP and Branch Off Extended Architecture

## Status
Accepted

## Date
2025-05-17

## Context

The initial implementation included an advanced architectural structure for running skill assessments within ChatGPT. This design featured:

- Prompt modularization by phase (intro, roleplay, reflection, etc.)
- A router mechanism (`role_router.md`) to dispatch prompts based on trigger words
- State-reset logic to re-inject facilitator behavior (`facilitator_prompt.md`) at each phase
- Centralized configuration files with defined prompt paths and language variants
- Internet-based prompt loading (from GitHub) using raw file access

However, the following **technical difficulties and platform constraints** were observed:

- **Unreliable Internet fetch behavior** from ChatGPT to GitHub (timeouts, fetch failures)
- **Caching and completion bias** of ChatGPT leading to unexpected prompt interpretations
- **Session drift**, especially in long conversations, reducing the effect of earlier prompt injections
- Prompt routing and dynamic control logic increased the complexity beyond what’s practical for ChatGPT-native apps

Therefore, we decided to **scale down to a simpler MVP** that embraces the **fuzzy, flexible nature of ChatGPT** as a feature—not a bug.

## Decision

- The full-featured version is preserved in the `extended-architecture` branch as an exploratory prototype
- The `main` branch will follow a simplified architecture:

  - **Prompt files will be manually injected by users** (e.g., `prompt_intro.md`, `prompt_roleplay.md`)
  - No automatic routing; each phase shift is explicitly triggered by reading a specific file
  - The system favors **predictability through simplicity**, not internal routing logic
  - The fuzzy nature of ChatGPT's responses will be **leveraged for immersive roleplay and reflective learning**

## Consequences

- The system becomes more robust for real-time use, even if internet fetch fails
- Less deterministic behavior is acceptable and even desirable for learner engagement
- Prompt modularity remains available and reusable in future versions (e.g., for EA scenarios)
- Advanced routing logic is deferred but not discarded, allowing future reintegration if needed