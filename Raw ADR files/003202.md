# ADR-006: Choice of UI Component Library

**Date:** 2025-09-02

**Status:** Decided & Implemented

## Context

To achieve a professional, consistent, and feature-rich user interface within a rapid development timeline, a pre-built component library is necessary. The application requires complex components for both the customer-facing portal and the data-intensive admin dashboard, including modals, data grids, and forms.

## Decision

We will use **Material UI (MUI)** as the primary UI component library for the React frontend. This includes the core `@mui/material` library and the `@mui/x-data-grid` for the admin dashboard.

## Consequences

*   **Pros:**
    *   **Comprehensive Component Set:** MUI provides a vast array of well-documented, accessible components out-of-the-box, significantly accelerating the development of complex UIs like `RequestDetailModal.tsx` and `Dashboard.tsx`.
    *   **Professional Aesthetic:** The Material Design system offers a clean, professional, and widely recognized look-and-feel, which builds trust for a business-focused application.
    *   **Data-Grid Functionality:** The `@mui/x-data-grid` component is extremely powerful, providing sorting, filtering, and pagination with minimal setup, which is a massive time-saver for the admin command center.

*   **Cons:**
    *   **Bundle Size:** Full-featured component libraries like MUI can be heavy and may increase the initial page load time if not carefully managed with code-splitting.
    *   **Styling System:** MUI uses its own styling solution (`@emotion/styled`). This can introduce a learning curve and make it more complex to override styles compared to a utility-first framework like Tailwind CSS.
    *   **Opinionated Design:** The components are strongly styled, which can make achieving a highly unique, custom brand aesthetic more work.

*   **Alternatives Considered:**
    *   **Tailwind CSS:** A utility-first CSS framework that provides maximum flexibility. It was not chosen as the primary library because it would have required building complex components like modals and data grids from scratch, slowing down the initial prototyping.
    *   **Shadcn/ui:** A popular library that provides unstyled, composable components. It's an excellent middle ground but requires more setup and composition for each component, making it slightly slower for a rapid POC compared to MUI's ready-to-use components.
