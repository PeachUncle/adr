# ADR-0015: Smart Strict Mode and Resource-Level Load Policies

## Status

Accepted

## Context

In the skill assessment system, we observed that ChatGPT's completion mechanism can lead to undesired behaviors when file content is not explicitly fetched from specified URLs. This affects reproducibility and control over key prompts, especially in scenarios where strict fidelity to source material (e.g., evaluation criteria) is required.

Strict Mode was introduced to mitigate this by requiring all resources to be fetched from remote sources (e.g., GitHub raw links) before processing. However, a fully strict approach negatively impacts performance and hinders beneficial variation (e.g., character personality drift). Therefore, we propose a hybrid strategy: Smart Strict Mode.

## Decision

We define a new session-level configuration mode: **SMART\_STRICT**. This mode allows each file or resource to specify its own load policy, optimizing both accuracy and performance.

### Smart Strict Mode Declaration

```markdown
<!--
SESSION_MODE: SMART_STRICT

RESOURCE_POLICIES:
  - path: shared/evaluation_criteria.md
    download: always
  - path: roles/po/prompts/prompt_intro.md
    download: always
  - path: roles/po/characters/collaborative_team.md
    download: if_missing
  - path: product_briefs/calendar_dashboard.md
    download: if_missing
  - path: shared/router/role_router.md
    download: prefer_cache
-->
```

### Policy Semantics

| Policy         | Behavior                                                                 |
| -------------- | ------------------------------------------------------------------------ |
| `always`       | File must be freshly fetched via HTTP (status 200 OK required).          |
| `if_missing`   | Fallback to memory is allowed if the file was already seen this session. |
| `prefer_cache` | Prefer completion from memory or training data to avoid re-fetch delays. |

### Application

The facilitator prompt or prompt header will instruct ChatGPT to:

* Fetch all `always` files before beginning execution
* Attempt `if_missing` fetches only if no cached version is available
* Skip downloading `prefer_cache` files unless explicitly forced

This structure ensures reproducibility where required (evaluation logic), while enabling flexibility and performance in less critical assets (characters, product briefs).

## Consequences

* Enables fine-grained control over load behavior per resource
* Supports reuse of stable system files via caching, speeding up execution
* Encourages variability where it adds learning value (e.g., replayable character scenarios)
* Requires updates to facilitator and prompt header templates to respect these declarations
* Future CLI or scripting tools could parse `RESOURCE_POLICIES` blocks to generate fetch instructions

---

Created: 2025-05-17
Authors: Sachiko Kijima, AssistA
