# Use Next.js 15 with React 18 for User Facing Frontend

* **Status**: Accepted
* **Date**: 2025-08-25

## Context

We are starting a new project that is expected to have a long-term impact (multi-year lifecycle). The latest stable release of Next.js is **v15**, which officially supports both **React 18** and **React 19 RC**.

However:

* **React 19** is still in release-candidate stage and not fully supported across the ecosystem.
* Popular libraries such as **shadcn/ui**, **NextAuth**, **MUI**, and others have unresolved peer dependency issues when used with React 19, causing installation errors or runtime instability.
* React 18 is stable, widely adopted, and remains a fully supported option in Next.js 15.
* We want to balance long-term maintainability with developer productivity and ecosystem stability.

## Decision

We will adopt **Next.js 15 with React 18** as our baseline technology stack.

* This ensures stability and broad compatibility with commonly used libraries.
* We will monitor ecosystem progress on React 19 adoption and plan for a future migration when the ecosystem has matured (likely around Next.js 16).
* Deprecation warnings introduced in Next.js 15 will be addressed during development to keep our codebase forward-compatible.

## Consequences

**Positive**:

* Immediate compatibility with shadcn/ui, NextAuth, MUI, and other popular libraries.
* Stable developer experience with minimal peer dependency conflicts.
* Reduced risk of breaking changes from experimental React 19 features.
* Easier onboarding for contributors, as React 18 is the current mainstream version.

**Negative**:

* We will not benefit from React 19 features (e.g., improved Actions API, useOptimistic enhancements, ref-as-prop).
* A migration to React 19 will be required in the future, once libraries catch up.
* Slightly less “future proof” in the very short term.

## Alternatives Considered

1. **Use Next.js 15 with React 19 RC**

   * Pros: Access to latest React features early, technically future-proof.
   * Cons: Multiple compatibility issues with key libraries, risk of instability, reliance on `--legacy-peer-deps` or overrides.

2. **Use Next.js 14 with React 18**

   * Pros: Very stable, wide library support.
   * Cons: Already superseded by Next.js 15, would require near-term upgrade; less aligned with long-term roadmap.

3. **Wait for Next.js 16 + React 19 GA**

   * Pros: Maximum stability with the newest stack.
   * Cons: Delays project start, not viable given current timelines.
