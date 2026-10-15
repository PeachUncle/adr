# ADR-0008: Prompt Structure Design for Skill Assessment

**Status:** Accepted  
**Date:** 2025-05-16

Accepted

## Context

In the skill assessment system using ChatGPT ("AssistA") as a facilitator, prompts such as `facilitator_prompt.md` and `prompt_intro.md` define the assistant’s behavior for each phase and mode. In previous iterations, prompt files varied in structure, which led to:

* Inconsistent behavior across modes and phases
* Difficulty in debugging or updating logic
* Reduced clarity for contributors and maintainers

Inspired by escalation report structures and API architecture principles, a more modular, readable, and enforceable prompt structure is required.

## Decision

We will adopt a standard prompt structure for all role/mode/phase-specific prompts using the following sections:

```
# 📝 Summary
A short description of the purpose and context of this prompt.

# 🎯 Expected End State
Goals that the assistant should aim to achieve by the end of the session or phase.

# 🧑 Your Role
Description of the assistant's expected behavior and stance in this scenario.

# ⚙️ Business Logic / Behavior
List of key logical rules, constraints, or step-based behaviors to follow.

# 📂 Assets & Components
Table of external files to be loaded, with their purpose and paths.

# ❌ Guardrails / NG Behaviors
Behavioral boundaries or restrictions (e.g., no multi-participant handling).
```

### Layered Responsibility Mapping (API Architecture Metaphor)

To enhance clarity and maintenance, we define each file group by its architectural role:

| Layer                      | Responsibility                         | Examples                                                |
| -------------------------- | -------------------------------------- | ------------------------------------------------------- |
| API Gateway                | Entry point & routing control          | `shared/chat_mode/readme_chat.md`                       |
| BFF (Backend for Frontend) | Mode-level control & config resolution | `readme_chat_default.md`, `readme_chat_debug.md`        |
| Application Logic          | Behavioral rules & state control       | `facilitator_prompt.md`, `prompt_intro.md`              |
| Data Layer                 | Scenario assets, briefs, team profiles | `characters/`, `product_briefs/`, `config/lang/jp.yaml` |

This layered abstraction enables future extension to new roles, languages, or modes with minimal cross-impact.

## Consequences

* All existing prompts such as `facilitator_prompt.md` will be refactored to this format.
* A shared template file (`shared/templates/prompt_structure.md`) will be introduced for future reuse.
* A `format` key (e.g., `format: standard-v1`) may be optionally added to prompt metadata in `config/*.yaml` to track adoption.
* Contributors will follow this format when adding new roles, phases, or modes.

---

Created: 2025-05-16
Authors: Sachiko Kijima, AssistA
