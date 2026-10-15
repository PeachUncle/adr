# ADR 0003: Route-as-Value-and-Guard-Policy

- **Status**: Accepted
- **Date**: 2025-09-06
- **Owners**: Tasqly Team
- **Related**: Phase0 — Slice3 (Navigation, Loader & Fallback)
- **Tags**: navigation, route, guard, policy

---

## Context
In Slice 3, we introduced a **Route** struct (`src/domain/core/Route.h`) as a value object.  
The purpose is to treat navigation targets as **immutable validated values** instead of raw strings.

The `NavigationService` depends on `Route` for **route guarding** and stack management.  
This ADR formalizes the policy for how routes are validated, logged, and guarded at runtime.

---

## Problem
- Without a central abstraction, navigation could use arbitrary strings (e.g., `"settings"`, `"dashboard"`), leading to inconsistencies and runtime errors.  
- Missing validation could cause navigation to invalid pages, breaking the stack and user experience.  
- Lack of policy would allow UI code to bypass guards.

---

## Decision
We adopt the following policies:

### 1. Route as Value Object
- `Route` is defined with:
  - `QString id`  
  - `QDateTime timestamp`  
- Includes `isValid()` and `toString()` helpers.  
- Must be passed by **value or const-ref** across app layers.

### 2. Guard Policy
- **All navigation requests** go through `NavigationService::navigateTo(Route)`.  
- If `route.isValid() == false`:  
  - Reject navigation.  
  - Log at `Error` level under category `"navigation"`.  
  - Emit `navigationFailed(reason)` → UI shows toast.  
- If valid:  
  - Push route to stack.  
  - Log at `Info` level.  
  - Emit `navigated(route)`.

### 3. Integration with Use Cases
- The `NavigateTo` use case wraps `NavigationService`:
  - Emits `PageState::Loading` before calling navigate.  
  - Switches to `PageState::Ready` or `PageState::Error` depending on result.  
- Ensures UI loaders (SmartPageLoader/SmartFallback) follow the same lifecycle.

---

## Consequences
- Routes are now **type-safe and validated**.  
- Prevents invalid navigation at compile-time (through enforced struct usage).  
- Provides consistent logging and error handling.  
- UI code cannot bypass guard policies.

---

## Future Extensions
- Extend `Route` with extra metadata (e.g., params, auth token).  
- Persist last successful route in `AppSettingsManager`.  
- Support route replacement (`replaceTop`) with guard.

---

## References
- `src/domain/core/Route.h`  
- `src/app/navigation/NavigationService.{h,cpp}`  
- `src/app/usecases/NavigateTo.{h,cpp}`  
