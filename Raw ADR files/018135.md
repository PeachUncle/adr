# ADR-001: Module-Based Architecture

## Status

Accepted

## Context

We need to establish a clear, scalable architecture for the Astro project that:
- Promotes code organization and maintainability
- Enables feature-based development with clear boundaries
- Separates routing concerns from component implementation
- Provides a shared foundation for reusable components and utilities
- Supports team collaboration with well-defined module boundaries

The project will grow to include multiple features (blog, projects, introduction pages, etc.), and we need a structure that scales without becoming unwieldy.

## Decision

We will adopt a **module-based architecture** with the following conventions:

### Core Module

The `core` module serves as the shared foundation containing:
- Shared UI components (buttons, cards, layouts, sections)
- Shared utility functions
- Shared hooks (if using React/Vue)
- Third-party integrations
- Shared type definitions and constants

**Structure:**
```
src/modules/core/
  ├── components/    # Shared UI components
  │   ├── base/      # Base/primitives components
  │   ├── layouts/   # Layout components
  │   └── sections/  # Reusable section components
  ├── utils/         # Shared utility functions
  ├── hooks/         # Shared hooks
  ├── libs/          # Third-party integrations
  ├── types.ts       # Shared type definitions
  └── constants.ts   # Shared constants
```

### Feature Modules

Each feature module is **self-contained** and follows this structure:

```
src/modules/{module-name}/
  ├── components/     # Module-specific components
  ├── pages/         # Page components (loaded by routes)
  ├── services/      # Data fetching and business logic
  ├── utils/         # Module-specific utilities
  ├── hooks/         # Custom hooks (if using React/Vue)
  ├── libs/          # Module-specific third-party integrations
  ├── styles/        # Module-specific styles
  ├── types.ts       # Module type definitions
  └── constants.ts   # Module constants
```

### Routing Pattern

The `src/pages/` directory is **only for routing purposes**. Route files should:
- Import page components from modules
- Handle routing-specific concerns (metadata, params, query strings)
- Delegate actual page rendering to module components

**Example:**
```astro
// src/pages/about.astro
---
import AboutPage from '../modules/introduction/pages/AboutPage.astro';
---

<AboutPage />
```

## Consequences

### Positive

- **Clear boundaries**: Each module is self-contained, making it easier to understand and maintain
- **Scalability**: New features can be added as new modules without affecting existing code
- **Reusability**: Core module provides shared components and utilities used across modules
- **Separation of concerns**: Routing logic is separated from page component implementation
- **Team collaboration**: Different developers can work on different modules with minimal conflicts
- **Testability**: Modules can be tested in isolation
- **Code organization**: Related code (components, services, types) is grouped together

### Negative

- **Initial setup overhead**: Requires creating directory structure for each module
- **Import paths**: Module imports may be slightly longer (e.g., `../modules/core/components/Button.astro`)
- **Learning curve**: Team members need to understand and follow the module structure conventions
- **Potential duplication**: Risk of duplicating code if not properly using the core module

### Mitigation

- Use TypeScript path aliases in `tsconfig.json` to shorten import paths
- Establish clear guidelines on what belongs in core vs. feature modules
- Regular code reviews to ensure adherence to the architecture
- Document module creation process and conventions

