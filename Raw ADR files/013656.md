# Tailwind Component Factory for Layouts

Date: 2023-04-15

Status: Accepted

## Context and Problem Statement

We needed a flexible and reusable way to create layout components that leverage Tailwind CSS classes. The goal was to reduce code duplication, improve maintainability, and ensure consistency across the application's layout components.

### Decision Drivers

* Reduce code duplication in layout components
* Improve maintainability of layout-related code
* Ensure consistency in applying Tailwind CSS classes
* Provide flexibility for creating various layout components with different default settings

### Considered Options

* Create individual layout components manually
* Use a higher-order component (HOC) approach
* Implement a component factory function

## Decision Outcome

We chose to implement a component factory function called `createLayoutComponent`. This function generates React components with predefined Tailwind CSS classes and customizable options.

### Positive Consequences

* Significantly reduces code duplication for layout components
* Improves maintainability by centralizing layout component creation logic
* Ensures consistency in applying Tailwind CSS classes across layout components
* Provides flexibility to create various layout components with different default settings
* Allows for easy customization of generated components through props

### Negative Consequences

* Adds a layer of abstraction that may require developers to understand the factory pattern
* Potential for overuse, leading to the creation of too many specialized components

## Consequences

### Component Factory Approach

* Good, because it promotes code reuse and consistency
* Good, because it allows for easy creation of new layout components with predefined styles
* Good, because it provides flexibility through customizable options and prop overrides
* Bad, because it introduces an additional layer of abstraction
* Bad, because it may lead to overuse if not carefully managed

### Manual Component Creation

* Good, because it's straightforward and doesn't require understanding of factory patterns
* Bad, because it leads to code duplication and potential inconsistencies
* Bad, because it's less maintainable as the number of layout components grows

## Links

* [Utils Implementation](../../app/components/layouts/utils.tsx)
* [Page Layout Components](../../app/components/layouts/page.tsx)
* [Usage in Index Route](../../app/routes/_marketing+/index.tsx)
* [Usage in About Route](../../app/routes/_marketing+/about.tsx)
