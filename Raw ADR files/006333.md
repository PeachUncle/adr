# ADR-008: Git Workflow & Credentials

Status: Accepted
Date: 2025-08-22
Owners: Archon Core

## Context

Archon uses Git for versioned configuration snapshots and collaboration. We need a simple, predictable user workflow and a secure way to authenticate to remotes across Windows, macOS, and Linux.

## Decision

- **UI workflow**: Present a linear history with "Snapshot" (commit+tag), "Sync" (pull/push), and "History". Advanced branching is allowed outside the app; Archon will respect branches but does not force users into branch management screens. (Keeps UX approachable.)  
- **LFS**: Projects use Git LFS for large binaries in `/attachments/`. Archon initializes LFS on repo creation and on enabling attachments.  [oai_citation:0‡Git Large File Storage](https://git-lfs.com/?utm_source=chatgpt.com) [oai_citation:1‡GitHub Docs](https://docs.github.com/repositories/working-with-files/managing-large-files/about-git-large-file-storage?utm_source=chatgpt.com) [oai_citation:2‡GitLab Docs](https://docs.gitlab.com/topics/git/lfs/?utm_source=chatgpt.com)
- **Credentials**: Prefer platform credential helpers:
  - macOS: `git-credential-osxkeychain`
  - Windows: `wincred` (Credential Manager)
  - Linux: `libsecret` (GNOME Keyring/KWallet)  
  
  Archon shells out to `git credential` so the OS manages secrets.  [oai_citation:3‡Git SCM](https://git-scm.com/doc/credential-helpers?utm_source=chatgpt.com)
- **SSH**: Default to **ed25519** keypairs and standard SSH agents. (Archon can help generate keys and copy the public key.)  
- **Offline safety**: All key operations (edit, snapshot) work offline; "Sync" clearly shows pending pushes/pulls.

## Rationale

- Keeping the in-app model linear matches our non-Git-expert personas and the spec’s snapshot mental model, while staying compatible with normal Git workflows. LFS is the standard way to store large binaries without bloating repos. Native credential helpers provide secure, per-OS storage.  [oai_citation:4‡Git Large File Storage](https://git-lfs.com/?utm_source=chatgpt.com) [oai_citation:5‡GitHub Docs](https://docs.github.com/repositories/working-with-files/managing-large-files/about-git-large-file-storage?utm_source=chatgpt.com) [oai_citation:6‡Git SCM](https://git-scm.com/doc/credential-helpers?utm_source=chatgpt.com)

## Alternatives Considered

- **Custom credential store**: More control, but reinvents well-hardened OS facilities.
- **No LFS**: Simpler, but repositories grow unmanageably and clones become slow.

## Consequences

- Positive: Trustworthy sync with minimal UX; secure credentials; scalable binary handling.
- Risks: Users must have Git+LFS installed (see ADR-010 for the tech choice).
- Follow-ups: Clear diagnostics for remote auth failures; helper docs for PAT/SSH.

## Implementation Notes

- Invoke `git credential` plumbing so helpers handle prompts/secrets.  [oai_citation:7‡Git SCM](https://git-scm.com/docs/gitcredentials?utm_source=chatgpt.com)
- Initialize LFS (`git lfs install` + track rules) on first attachment usage.  [oai_citation:8‡Git Large File Storage](https://git-lfs.com/?utm_source=chatgpt.com)

## Review / Revisit

- Revisit when enabling automated background sync or organization SSO.
