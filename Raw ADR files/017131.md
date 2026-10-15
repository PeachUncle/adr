# ADR-0004: Separation of Application-Level and Phase-Specific Prompts

**Status:** Accepted  
**Date:** 2025-05-15

## Context

In the ChatGPT-driven skill assessment experience, two types of prompts are used:

1. **Application-Level Prompts**  
   These define how ChatGPT should behave globally—tone, guardrails, behavior constraints, etc.

2. **Phase-Specific Prompts**  
   These support specific interactions during phases such as intro, roleplay, and reflection.

Previously, these prompts were partially intermixed in mode-specific setup files (e.g., `README_chat_default.md`). However, clearer separation improves maintainability and responsibility boundaries.

## Decision

### 1. Application-level behavior is defined in `shared/facilitator_prompt.md`

This file describes the assistant’s tone, behavioral constraints, and how it should facilitate the experience overall. It references:

- [`shared/roleplay_safety.md`](../roleplay_safety.md): Describes constraints and prohibited behaviors during roleplay (e.g., no mid-phase restart)

### 2. Phase-specific behavior remains modular

Prompts such as:

- [`prompt_intro.md`](../prompt_intro.md)
- [`prompt_reflection.md`](../prompt_reflection.md)

will remain separate and describe behavior only for their respective phases. These are listed in mode setup files like `README_chat_default.md`.

### 3. Mode router files do not define behavior

Files such as `README_chat_default.md` will **only point to the correct prompts and assets**, and not duplicate or enforce behavior definitions. They simply declare:

- What assets to load
- Which prompts to use
- How to organize the session flow

## Consequences

- Centralizes the ChatGPT’s behavioral identity into a single file (`facilitator_prompt.md`)
- Simplifies `README_chat_*.md` files by focusing them on structure and assets, not behavior
- Enables easier future changes to ChatGPT personality or tone
- Ensures that guardrails (`roleplay_safety.md`) are respected across all modes and roles

## Future Considerations

- Application-level prompts may be versioned or extended (e.g., facilitator_prompt_v2.md)
- Phase prompts can be role-customized if needed using naming like `prompt_intro_po.md`
