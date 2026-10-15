# 🧠 Architectural Decision Record

**Title:** Use `dev_env.yml` as a Single Source of Truth for Setup Logic
**Status:** Accepted
**Date:** 2025-05-29
**Deciders:** PazzTech
**Context:** PT: Workstation Setup

---

## 🎯 Decision

We will use a single YAML file (`dev_env.yml`) to declare the full configuration of a development environment. This file defines:

* Which tools to install
* On which operating systems
* Whether they are installed automatically or require manual steps
* What versions or managers to use

The setup scripts (`setup.sh`, `setup.ps1`, and future `bootstrap`) will parse this file and dynamically drive installation logic based on its contents.

---

## 🤔 Rationale

### Problems With Prior Approach

* Logic was hardcoded in OS-specific shell scripts
* Manual installs had no visibility or tracking
* Adding a new tool required touching multiple files and scripts
* There was no central point of audit or control

### Benefits of YAML-Driven Approach

* ✅ Declarative: clear and human-readable
* 🧠 Unified: one place to manage all tools across all platforms
* 💡 Extensible: supports flags like `enabled`, `manual`, `version`, `manager`, `extensions`
* 📋 Traceable: enables output of uninstalled tools into `logs/manual-install.md`
* 🔄 Re-runnable: promotes idempotency and version pinning

---

## ✍️ Structure Summary

```yaml
languages:
  python:
    macos:
      enabled: true
      version: "3.11.4"
      manager: pyenv
    windows:
      enabled: true
      version: "3.11.4"
      manager: pyenv-win
editors:
  vscode:
    all:
      enabled: true
      extensions:
        - ms-python.python
```

Script logic will branch based on `$(get_os)` and handle per-key installs accordingly.

---

## 🔄 Alternatives Considered

* JSON: Less readable, harder to comment, no multiline-friendly config blocks
* Multiple `*-config.yml` files: Higher surface area, loss of global view
* Sticking with script-only logic: Higher coupling and long-term complexity

---

## 🔧 Implications

* Setup scripts must include a YAML parser (`yq`, PowerShell native YAML, or Python fallback)
* All future installs must be defined through this file to ensure consistency
* Requires strict versioning hygiene for tools defined with `version:`

---

## 🔜 Next Steps

*
