# ADR 0002: Cross-Platform clang-format Detection

- **Status**: Accepted
- **Date**: 2025-09-30
- **Owners**: Tasqly Team
- **Related**: Phase01 — CI/CD Setup
- **Tags**: tooling, linting, ci, cross-platform

---

## Context
During development we use `clang-format` to enforce C++ code style. A problem appeared:
- On **Windows (MSYS2)** the binary is named `clang-format`.
- On **Linux (Ubuntu CI)** the installed binary is named `clang-format-20`.

Our original script hardcoded `/usr/bin/clang-format-20`, which caused local developers on Windows to fail running the formatter. Conversely, relying only on `clang-format` would break CI where only `clang-format-20` exists.

This mismatch created friction:
- Developers could not use the same `scripts/check-format.sh` locally and in CI.
- CI consistency checks risked using a different version than local.

## Decision
We adopted a **cross-platform detection strategy** in `scripts/check-format.sh`:
- The script tries multiple candidate names: `clang-format-20` (Linux) and `clang-format` (Windows/MSYS2).
- It uses the first binary found in `$PATH`.
- The script then prints the resolved binary and version to avoid ambiguity.

Implementation snippet:
```bash
for candidate in clang-format-20 clang-format; do
  if command -v "$candidate" &> /dev/null; then
    CLANGFMT=$(command -v "$candidate")
    break
  fi
done

echo "Using clang-format binary: $CLANGFMT"
"$CLANGFMT" --version
```

## Consequences
- ✅ **Consistency**: Both Windows devs and Linux CI use the same script.
- ✅ **Transparency**: Binary path and version are logged each run.
- ✅ **Robustness**: If neither binary is found, the script exits with error.
- ⚠️ **Risk**: Different versions (e.g., 20.1.8 locally vs 20.1.9 on CI) could still diverge slightly, but pinned CI setup minimizes this.
- 🔄 **Trade-off**: We maintain a simple detection loop instead of forcing symlinks or platform-specific scripts.

## References
- `scripts/check-format.sh`
- GitHub Actions workflow (`.github/workflows/ci.yml`)
- [Project_Quality_Policy.md]
- [FilePolicy.md]