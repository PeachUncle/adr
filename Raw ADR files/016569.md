# Architecture Decision Record (ADR)

ADR-0030: Framework-Agnostic Frontend Development with Thin UI ADR

We will adopt a **framework-agnostic frontend core architecture**, where all business logic and application behavior are
implemented outside Angular and UI frameworks act only as adapters.

## 1. Status

**Draft** | **Accepted**

## 2. Context

**Problem / Need**

The frontend application is built using Angular (currently Angular 21). The application is expected to be long-lived,
evolve over time, and undergo framework upgrades (Angular major versions) and potentially framework changes (e.g.,
React, Vite-based UI) with minimal risk and cost.
Key challenges identified:

* Angular upgrades frequently introduce breaking changes **affecting components**, lifecycle, DI, and testing.
* UI-driven development **tightly couples** business logic to the framework, making **testing** slow and brittle.
    * End-to-end and UI tests based on CSS/XPath selectors are **fragile** and expensive to maintain.
* Developers lack a **fast feedback** loop to develop and validate frontend behavior without building UI first.

To address these challenges, the team wants a frontend architecture that:

* **Separates business logic** from the UI framework
* Enables **UI-independent development** and **testing**
* Reduces **upgrade and migration costs**
* Improves developer **productivity** and **confidence**

## Context

The frontend application is built using Angular (currently Angular 21). The application is expected to be long-lived,
evolve over time, and undergo framework upgrades (Angular major versions) and potentially framework changes (e.g.,
React, Vite-based UI) with minimal risk and cost.

Key challenges identified:

* Angular upgrades frequently introduce breaking changes affecting components, lifecycle, DI, and testing.
* UI-driven development tightly couples business logic to the framework, making testing slow and brittle.
* End-to-end and UI tests based on CSS/XPath selectors are fragile and expensive to maintain.
* Developers lack a fast feedback loop to develop and validate frontend behavior without building UI first.

To address these challenges, the team wants a frontend architecture that:

* Separates business logic from the UI framework
* Enables UI-independent development and testing
* Reduces upgrade and migration costs
* Improves developer productivity and confidence

## 3. Decision

We will adopt a framework-agnostic frontend core architecture, where all business logic and application behavior are
implemented outside Angular and UI frameworks. These act only as **data visualizers**.

Name it as: **Service For Component (SFC)** (like Backend For Frontend: BFF).

Key decisions:

1. Framework-Agnostic
2. Layered Responsibility Model
3. Thin UI Components
4. Service per Component aka SFC
5. UI-Independent Executability
6. Developer Console Accessibility
7. Testing Strategy
8. Angular as an data visualizer

### Key decisions:

1. **Framework-Agnostic Core**

    * Business logic, workflows, validation, and state transitions are implemented in service layers.
    * The core must not import or depend on Angular or any UI framework.

2. **Layered Responsibility Model**

   ```
   UI Presenter (Components in frameworks like Angular / React / VueJS / Other)
           ↓
   Application Services (Domain Logic, non or less depending from framework)
           ↓
   Resource Adapters (HTTP, storage, browser APIs)
   ```

    * (Angular) components are thin and UI-only.
    * Application services coordinate use cases and expose behavior to the UI. Service layer prepare data for
      visualization.
    * Domain logic contains pure business rules and is implemented in service layer.
    * Resource access are data sources.

3. **Thin UI Components**

    * UI components must not contain business logic.
    * Components delegate all behavior to application services.
    * Components are responsible only for rendering, event binding, and user interaction.

4. **Service per Feature / Component (Facade Pattern)**

    * Feature-level or complex components must have a corresponding application service (facade).
    * Simple presentational components may omit a facade when no behavior exists.

5. **UI-Independent Executability**

    * Application services must be executable without Angular or any UI framework.
    * Services can be instantiated and invoked directly using JavaScript or TypeScript.

6. **Developer Console Accessibility (Development Only)**

    * In development environments, selected application services may be explicitly exposed on the browser `window`
      object for interactive testing and exploration.
    * No Angular services or framework internals may be exposed.
    * This exposure must be disabled in production builds.

7. **Testing Strategy**

    * The primary test target is the application service and domain layers.
    * Tests must not require DOM, Angular TestBed, or browser automation.
    * UI tests are limited to wiring, smoke tests, and critical user journeys.

8. **Angular as an data visualizer**

    * Angular is treated as an implementation detail of the UI layer.
    * Angular dependency injection may wrap or adapt application services but must not own business logic.

## 4. Rationale (Justification)

Explain **why** this decision was made.

### 4.1. Advantages

* ...
* ...
* ...

### 4.2. Known drawbacks / accepted risks

* ...
* ...
* ...

## 5. Alternatives Considered / Considered Options

1. **Traditional Angular Architecture**
    * Rejected due to tight coupling, challenging upgrades, and heavy UI-based testing.
2. **UI-First Development with E2E Testing**
    * Rejected due to brittle tests, slow feedback, and high maintenance cost.
3. **Micro-Frontends**
    * Does not solve core testability and coupling issues by itself.

## 6. Consequences, Impacts & Follow-up Actions

Describe the consequences of this decision.

* Technical impact
* Organizational / process impact
* Cost or operational impact
* Required follow-up actions (tasks, reviews, migrations, documentation updates)

## Consequences

### Positive

* Business logic is fully testable without UI, DOM, or Selenium-style tools.
* Angular upgrades affect only UI adapters, reducing risk and effort.
* Developers can develop and debug frontend behavior using the browser console or Node.js.
* Migration to other UI frameworks becomes feasible with minimal refactoring.
* Faster feedback loops improve developer productivity and code quality.

### Negative / Trade-offs

* Additional upfront architectural discipline is required.
* Slightly more boilerplate due to explicit layering and adapters.
* Team members must understand and follow dependency direction rules.

## Enforcement and Guardrails

To ensure the architecture is consistently applied:

* No Angular imports are allowed outside the UI adapter layer.
* Dependency direction must always point inward (UI → Application → Domain).
* Linting and CI checks should be used to enforce module boundaries.
* Production builds must not expose application services on the global scope.

## Notes

This ADR intentionally prioritizes long-term maintainability, upgradeability, and developer experience over short-term
simplicity. The architecture is particularly suitable for large, long-lived frontend applications with complex business
logic.
