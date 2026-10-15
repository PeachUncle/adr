# ADR 0004: qml-singleton-vs-named-element

- **Status**: Accepted
- **Date**: 2025-09-06
- **Owners**: Tasqly Team
- **Related**: Phase0 — Slice3 (Navigation, Loader & Fallback)
- **Tags**: qml, singleton, navigation, conflict, autogen

---

## Context
During implementation of **Phase 0 / Slice 3** (Navigation, Loader & Fallback), we introduced a `NavigateTo` use case class:
- Declared in C++ as `QObject` with `QML_NAMED_ELEMENT(NavigateTo)`.
- Also registered manually as a **singleton instance** via `qmlRegisterSingletonInstance<NavigateTo>(...)` inside `QmlSingletonProvider`.

This created a conflict:
- **Autogen issue:** Qt's `qmltyperegistrations.cpp` attempted to generate a call:
  ```cpp
  qmlRegisterTypesAndRevisions<NavigateTo>("Tasqly_V1", 1);
  ```
  but failed with:
  ```
  error: 'NavigateTo' was not declared in this scope
  ```
- **QML runtime issue:** In QML, code such as:
  ```qml
  Connections {
      target: NavigateTo
      onPageStateChanged: loader.pageState = state
  }
  ```
  raised errors. `NavigateTo` was ambiguously both a **type** and a **singleton instance**.

---

## Decision
- **Removed `QML_NAMED_ELEMENT(NavigateTo)`** from `NavigateTo.h`.  
- Kept only the explicit **singleton registration** inside `QmlSingletonProvider`:
  ```cpp
  auto* navigateTo = new NavigateTo(navService, log);
  qmlRegisterSingletonInstance<NavigateTo>("Tasqly_V1", 1, 0, "NavigateTo", navigateTo);
  ```
- This ensures QML only knows `NavigateTo` as a **singleton instance**, not as a creatable type.  
- Connections in QML now bind correctly:
  ```qml
  Connections {
      target: NavigateTo
      onPageStateChanged: loader.pageState = state
  }
  ```
- Autogen no longer generates invalid `qmlRegisterTypesAndRevisions` calls.

---

## Consequences
- `NavigateTo` cannot be instantiated directly in QML (e.g., `NavigateTo { }`). This is consistent with its role as a **use case service**, not a UI component.  
- Autogen errors (`NavigateTo not declared in this scope`) are resolved.  
- Cleaner separation: **Singleton services** are registered explicitly, while **UI components** continue to use `QML_ELEMENT`.  

---

## References
- Build failure logs showing `NavigateTo` undeclared inside `apptasqly_v1_qmltyperegistrations.cpp`.  
- QML error when binding `target: NavigateTo` prior to fix.  
- Patch removing `QML_NAMED_ELEMENT(NavigateTo)` from `NavigateTo.h`.  
