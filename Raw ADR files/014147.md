# ADR-0001: Project Layout and Workspace Management

## Status
Accepted

## Date
2026-01-07

## Context
The `platform-iac-cli` project is designed as a high-performance orchestration tool for Senior DevSecOps. It requires a directory structure that:
1. Facilitates separation between the entry point and core business logic.
2. Ensures internal packages are not accessible by external projects (security encapsulation).
3. Supports rapid context switching between different feature sets (e.g., IaC logic vs. MCP server).
4. Complies with industry standards for Go projects to ensure maintainability.

## Decision
We will adopt the **Standard Go Project Layout** combined with a **Git Worktree-based development workflow**.

### Directory Layout
- `/cmd/platform-cli/`: The main entry point. Minimal logic; responsible for CLI initialization and command routing.
- `/internal/`: All core logic (orchestration, security checks, config management). Using `internal` prevents external Go programs from importing these packages.
- `/docs/adr/`: Architectural Decision Records in Markdown format.
- `/docs/features/`: Feature-specific documentation and specifications.
- `/pkg/`: (Optional) Library code that is safe to be exported and used by other projects.

### Workspace Management
We will use **Git Worktree** in a "Bare Repository" configuration. The root directory will house the `.bare/` repository, while active branches (`main`, `feat/mcp`, etc.) will reside in separate, co-located directories.



## Rationale
- **Encapsulation:** By using `/internal`, we enforce strict boundaries, ensuring that the CLI's logic remains private and manageable.
- **Operational Efficiency:** Git Worktree allows us to avoid the overhead of `git checkout` when switching between long-running tasks (e.g., debugging a Terragrunt provider vs. implementing VPC Lattice logic).
- **Scalability:** The Standard Go Layout is the most recognized structure in the Go ecosystem, making it easier for other Senior Engineers to contribute.

## Consequences
- **Build Complexity:** Binary builds must be executed from the specific worktree directory (e.g., `main/`).
- **Standardization:** All developers must adhere to the defined structure; placing logic directly in `/cmd` or the root directory is prohibited.
- **Learning Curve:** Contributors unfamiliar with `git worktree` will require onboarding on the bare-repo setup.
