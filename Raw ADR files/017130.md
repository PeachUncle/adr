# ADR-0003: Placement of Phase-Specific Prompts (Intro and Reflection)

**Status:** Accepted  
**Date:** 2025-05-15

## Context

In the skill assessment experience facilitated by ChatGPT, the flow is structured around distinct phases:
- Introduction (onboarding and scenario explanation)
- Roleplay
- Reflection (evaluation and feedback)

Prompts such as `prompt_intro.md` and `prompt_reflection.md` are used to guide ChatGPT's behavior during these phases.  
Initially, these prompts were considered for placement inside role-specific folders (e.g., `roles/po/`), but a clearer separation of concerns became necessary as multiple roles and modes were introduced.

## Decision

### Phase-specific prompts like `prompt_intro.md` and `prompt_reflection.md` will be stored in `shared/`

These prompts:

- Are **not dependent on the specific role** (e.g., PO, EA)
- Represent **common process instructions** for ChatGPT across all roles
- Belong to the same category as `facilitator_prompt.md` in terms of function and audience

This organization aligns with the role of `shared/` as the location for cross-role, ChatGPT-facing instruction assets.

### Updated Placement:

```
shared/
├── facilitator_prompt.md
├── prompt_intro.md
├── prompt_reflection.md
└── ...
```

### Role-specific folders (`roles/{role}/`) will only contain:

- Role-specific scenarios and evaluation materials
- Team/character profiles used in roleplay

## Consequences

- Promotes reusability: The same prompts can be used across different roles
- Clarifies responsibilities: `shared/` contains behavior-control instructions for ChatGPT, `roles/` contains domain-specific knowledge
- Simplifies maintenance: Prompts need only be updated in one place

## Future Considerations

- If role-specific variations of intro or reflection prompts become necessary, they can be named as `prompt_intro_{role}.md` and placed in `shared/`
- Additional phase prompts (e.g., emergency handling, help prompts) can follow the same placement rule
