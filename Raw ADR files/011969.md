# ADR-0004: Split Multi-Entry Packages into Stand-Alone Modules

Date: 2025-06-10 Status: **Accepted**

## Context

The original `@outfitter/contracts` package exposed a secondary export path `@outfitter/contracts/zod` to keep the core dependency-free while offering optional Zod utilities. During our build-system investigation we learned that multi-entry packages conflict with TypeScript **project references** and complicate declaration generation with **tsup**. The additional indirection also confused consumers and hindered tree-shaking.

Relevant analysis: [202506101749-monorepo-build-system-analysis](../handoffs/202506101749-monorepo-build-system-analysis.md) (§Multi-Entry Point Complexity) and the [Comprehensive Repository Review](../notes/202506101807-comprehensive-review.md).

## Decision

We **split each secondary entry into its own first-class package**.

- `@outfitter/contracts` → zero-dependency core (Result, AppError, types).
- `@outfitter/contracts-zod` → Zod helpers that depend on the core.

Future optional extensions (e.g., io-ts helpers) will use the same pattern: **one responsibility per npm package**.

## Consequences

### Positive

1. **Simpler builds** – TypeScript project references no longer need to model multi-entry output; `tsup` stays trivial.
2. **Clear dependencies** – Consumers explicitly opt into Zod by installing `@outfitter/contracts-zod`.
3. **Better tree-shaking** – No accidental inclusion of Zod in core bundles.
4. **Peer-dependency confusion eliminated** – Core remains zero-dep; extension owns its deps.

### Negative / Mitigations

| Impact                                       | Mitigation                                                                                                  |
| -------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Extra packages to publish & version          | Changesets automates versioning; CI handles publish matrix.                                                 |
| Breaking change for consumers using sub-path | Provide deprecation notice, update READMEs, ship `exports` fallback for one minor version (❓ TODO decide). |

## Option Matrix Considered (excerpt)

| Option                                 | Effort | Risk     | Build Simplicity | DX               |
| -------------------------------------- | ------ | -------- | ---------------- | ---------------- |
| A. Fix project refs + keep multi-entry | High   | Med-High | 😬               | Same as today    |
| **B. Split packages (chosen)**         | Med    | Low      | 😀               | Clear & explicit |
| C. Replace with modern monorepo tool   | High   | High     | 🙂               | Unknown          |

## Follow-Up Tasks

1. ✅ Create `@outfitter/contracts-zod` package (done in PR #TBD).
2. ✅ Remove `./zod` sub-export from core.
3. ✅ Update docs & READMEs (`contracts`, CLAUDE, etc.).
4. 🚧 Add CI matrix build for new package.
5. 🚧 Announce deprecation of sub-path in release notes.
