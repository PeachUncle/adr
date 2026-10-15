# ADR-0001: Chat Mode Structure and Prompt Organization

**Status:** Accepted  
**Date:** 2025-05-15

## Context

This repository provides a skill assessment experience using ChatGPT as a virtual facilitator.  
To support various usage scenarios such as standard assessment, debugging, and post-assessment reflection, multiple **chat modes** need to be supported.

In the initial version, only a single `README_chat.md` was used for instructions. However, with the addition of more modes and roles, the structure required better organization and clarity.

## Decision

The following structure has been adopted:

### 1. Use `README_chat.md` as a router

- `shared/chat_mode/README_chat.md` serves as the **entry point** for ChatGPT to choose a role (e.g., PO, EA) and a mode (e.g., default, debug, reflection).
- This file links to `README_chat_default.md`, `README_chat_debug.md`, and other mode-specific instruction sets.

### 2. Separate mode-specific instructions by purpose

- Each mode (e.g., default, debug) has its own dedicated file under `shared/chat_mode/`:
  - `README_chat_default.md`: Normal assessment mode
  - `README_chat_debug.md`: For user testing, error reproduction, or relaxed output
- These files describe:
  - The facilitator prompt to use (e.g., `shared/facilitator_prompt.md`)
  - Necessary assets per phase (intro, roleplay, reflection)

### 3. Role-independent introductory and reflection prompts are placed in `shared/`

- Files such as:
  - `prompt_intro.md`
  - `prompt_reflection.md`
- These are used across roles (PO, EA, etc.), so they are placed in `shared/` to avoid duplication and clarify their cross-role scope.

## Consequences

- New modes can be added by simply creating new `README_chat_*.md` files and linking them from the router.
- The repository maintains a clear separation of concerns:
  - `shared/` for reusable prompts and mode controllers
  - `roles/` for role-specific content like scenarios and evaluation criteria
- ChatGPT can operate autonomously based on clearly defined instructions per mode.

## Future Considerations

- Further structure may be applied if reflection or intro prompts require role-specific variations.
- Mode-specific facilitator prompts (e.g., `facilitator_prompt_debug.md`) may be standardized further as more roles are added.