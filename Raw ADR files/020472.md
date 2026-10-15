# DEC-2025-05-29-bootstrap-design.md

## Title
Unified Cross-Platform Bootstrap Script

## Status
Accepted

## Context
The `workstation-setup` project must support bootstrapping from a freshly installed system—macOS, Linux, or Windows—without requiring the user to know which setup script to run. We needed an entrypoint that automatically detects the OS and dispatches to the correct platform-specific script. Solutions such as `setup.sh` or `setup.ps1` alone are insufficient since they only work in one shell context.

## Decision
We will use a **single polyglot file named `bootstrap`** (no extension) at the root of the repository. This file will be executable and compatible with both Unix-style shells and PowerShell on Windows.

The file uses a dual-mode trick:

- The first line is a Bash comment but interpreted by PowerShell to re-invoke the same file using `pwsh`.
- Inside the file, Bash handles macOS/Linux dispatch, while PowerShell handles Windows.

```bash
#!/usr/bin/env bash
# 2>/dev/null; exec pwsh -File "$0" "$@"

# ===========================
# Bash Branch (macOS/Linux)
# ===========================
echo "Detected Bash environment..."
bash ./scripts/setup.sh
exit 0

<#
# ===========================
# PowerShell Branch (Windows)
# ===========================
Write-Host "Detected PowerShell environment..."
.\\scripts\\setup.ps1
exit
#>
```

## Rationale
- One entrypoint for all platforms reduces friction and improves usability.
- Compatible with command line usage, scripts, CI runners, and VMs.
- No need for separate `bootstrap.ps1` and `bootstrap.sh` files.
- Easy to document and explain in the `README`.

## Consequences
- Requires PowerShell Core (`pwsh`) to be installed and available in `$PATH` on Windows.
- Cannot use `bash -c` syntax directly on Windows-only systems without WSL or Git Bash.
- Unix systems must mark the file executable: `chmod +x bootstrap`.

## Alternatives Considered
- Multiple bootstrap files per OS (rejected: adds complexity)
- Using Makefile or wrapper scripts (rejected: not native on all platforms)
- Relying solely on users to choose the correct script (rejected: poor UX)

## References
- Žižka, O. (2013, July 7). *Single script to run in both Windows batch and Linux Bash?* Stack Overflow. https://stackoverflow.com/q/17510688
- Rohner, A. (2015, September 28). *Polymorphic file valid in Batch, Bash, and PowerShell.* https://andreasrohner.at/posts/Scripting/Polymorphic-file-that-is-a-valid-Windows-Batch-Bourne-Shell-and-Powershell-script/
