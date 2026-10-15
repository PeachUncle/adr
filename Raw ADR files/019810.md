---
title: "ADR 015: Automated Ecosystem Configuration Rollout"
type: "architecture"
audience: "operator"
status: "accepted"
priority: "medium"
version: "1.0.0"
created: "2025-12-30"
updated: "2025-12-30"
reviewers: ["@quievreux"]
tags: ["automation", "governance", "ci-cd", "scripting"]
---

# ADR 015: Automated Ecosystem Configuration Rollout

## Status
Accepted

## Date
2025-12-30

## Context
With the introduction of private packages (ADR 014) and standardized workflows (ADR 010), manually updating configuration files across dozens of repositories is becoming a bottleneck and a source of risk.
Key configuration files that need synchronization include:
- `.npmrc` (for registry authentication)
- `.github/workflows/*.yml` (for CI permissions and tokens)
- `tsconfig.json` (for standardized compiler options)

Manually editing these in 20+ repositories is error-prone, boring, and slow.

## Decision
We implemented an **Automated Rollout Strategy** using script-based orchestration (`scripts/rollout-ui.ts` and `scripts/rollout-standards.ts`).

### Mechanism
1.  **Central Script:** A TypeScript script residing in the `vibecoder-architect-reviewer` (Architect) repository acts as the source of truth.
2.  **FileSystem Traversal:** The script accepts a root directory path (e.g., `c:\CODE\GIT`), identifies all valid repositories, and iterates through them.
3.  **Idempotent Updates:**
    - **Injection:** It parses existing files (like YAML workflows) and injects *only* the missing pieces (e.g., `permissions: packages: read`) without destroying custom configurations.
    - **Creation:** If missing files (like `.npmrc`) don't exist, they are created from a standard template.
4.  **Verification:** The script attempts to run validation commands (like `npm install`) to ensure the applied configuration actually works.

## Consequences

### Positive
- **Scalability:** We can roll out a new security requirement or infrastructure change to 50+ repos in minutes.
- **Consistency:** Eliminated "drift" where some repos have slightly different settings than others.
- **Speed:** Drastically reduced the time required to adopt `quievreux/ui`.

### Negative
- **Risk of Mass-Breaking:** A bug in the rollout script could potentially corrupt configuration in all repositories simultaneously.
- **Local Context:** The script runs locally on the Architect's machine; it is not yet a fully autonomous CI agent that opens Pull Requests (though that is the long-term vision).

## Mitigations
- **Dry Runs:** Can implement flags to verify changes before writing.
- **Git Safety:** Always run rollout scripts against repositories that have clean git states, allowing for easy `git checkout .` revert if something goes wrong.
- **Review:** The script logic is part of the Architect repo and subject to code review.
