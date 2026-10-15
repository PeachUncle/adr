# ADR-010: Technology for Git Operations (Library vs CLI)

Status: Accepted
Date: 2025-08-22
Owners: Archon Core

## Context

Archon must perform clone/fetch/pull/push, tagging, diffs, and merges, plus LFS and credential helper integration. Options:

1) **Shell out** to the system `git` CLI
2) Use a **pure Go library** (go-git)
3) Use **libgit2** via Go bindings (git2go)

## Decision

Adopt a **hybrid** approach:

- **Default: system `git` CLI** for porcelain operations (clone, fetch, pull, push, tag, LFS, credentials). This guarantees parity with Git behavior and leverages OS credential helpers and LFS filters.  [oai_citation:19‡Git SCM](https://git-scm.com/doc/credential-helpers?utm_source=chatgpt.com) [oai_citation:20‡Git Large File Storage](https://git-lfs.com/?utm_source=chatgpt.com)
- **In-process (selective): `go-git`** for fast, read-mostly operations where it shines (e.g., opening a repo, reading objects, enumerating commits/trees, lightweight diffs when we don’t need filters). Keep an internal abstraction so we can route operations.  [oai_citation:21‡GitHub](https://github.com/go-git/go-git?utm_source=chatgpt.com) [oai_citation:22‡Go Packages](https://pkg.go.dev/github.com/go-git/go-git/v5?utm_source=chatgpt.com)
- **No libgit2 (v1)**: Avoid CGO and cross-platform native library packaging; revisit only if a specific feature/perf gap requires it.  [oai_citation:23‡GitHub](https://github.com/libgit2/libgit2?utm_source=chatgpt.com)

## Rationale

- The **CLI** is the reference implementation and integrates best with **credential helpers** and **LFS**, which are crucial for our attachments and enterprise auth.  [oai_citation:24‡Git SCM](https://git-scm.com/doc/credential-helpers?utm_source=chatgpt.com) [oai_citation:25‡GitHub Docs](https://docs.github.com/repositories/working-with-files/managing-large-files/about-git-large-file-storage?utm_source=chatgpt.com)
- **go-git** is pure Go, widely used, and avoids external deps; however, parity with the CLI for every edge case (e.g., all merge strategies, filters) is difficult. Using it for read-mostly paths keeps the UX snappy without correctness risk.  [oai_citation:26‡GitHub](https://github.com/go-git/go-git?utm_source=chatgpt.com) [oai_citation:27‡Go Packages](https://pkg.go.dev/github.com/go-git/go-git/v5?utm_source=chatgpt.com)
- **libgit2/git2go** is powerful but adds CGO and native packaging complexity; several projects weigh go-git vs git2go based on environment constraints—keeping an abstraction lets us pivot later if needed.  [oai_citation:28‡GitHub](https://github.com/fluxcd/flux2/discussions/426?utm_source=chatgpt.com)

## Alternatives Considered

- **CLI-only**: Simplest; but certain in-app operations benefit from in-process speed and finer control.
- **go-git only**: Cleaner distribution; but LFS/credentials parity and edge-case merges are harder.
- **libgit2 only**: Feature-rich; but increases build/signing burden and support matrix.

## Consequences

- Positive: Correctness for sync operations; performance for local reads; flexible future swap.
- Negative: Requires shipping with a Git dependency; must manage process execution & error parsing.
- Follow-ups: Clear detection/help if Git is missing; telemetry (opt-in) for slow ops to tune hybrid thresholds.

## Implementation Notes

- Define `internal/git/iface.go` with verbs: Clone, Fetch, Pull, Push, Tag, Diff, Merge, LFSInit.
- CLI adapter: `internal/git/cli/*` (exec + JSON parsers).
- Library adapter: `internal/git/gogit/*` for read paths and simple diffs.  [oai_citation:29‡Go Packages](https://pkg.go.dev/github.com/go-git/go-git/v5?utm_source=chatgpt.com)

## Review / Revisit

- Revisit if users demand full offline bootstrap without system Git, or if we need libgit2 features/perf not matched by go-git.
