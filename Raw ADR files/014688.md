# Separation of Printed View and Form View, and Avoidance of Bootstrap

* Status: Done
* Deciders: Fuensanta Sansano Montoya and Tomás Raigal López
* Date: 2023-04-10

## Context and Problem Statement

In our project, we have a requirement to allow users to generate printable documents based on the information they provide through a form. However, we have identified that combining the form view and the printed view within the same page can introduce unnecessary complexity and dependencies. Additionally, using Bootstrap for these views might result in an overly complex implementation.

We need to decide whether to separate the printed view from the form view and avoid using Bootstrap, in order to simplify responsibilities and streamline the development process.

## Decision Drivers

* Simplification of responsibilities
* Minimization of complexity
* Development efficiency
* Maintainability

## Considered Options

1. Combine the form view and the printed view within the same page using Bootstrap.
2. Separate the printed view from the form view.
3. Separate the printed view from the form view and avoid using Bootstrap.

## Decision Outcome

Chosen option: Option 3 - Separate the printed view from the form view and avoid using Bootstrap. This option best aligns with our decision drivers and provides the most straightforward and efficient solution.

### Positive Consequences

* **Simplification of Responsibilities**: By separating the printed view from the form view, we can assign clear responsibilities to each view. The form view focuses on data input and validation, while the printed view is responsible for generating the printable document based on the provided data. This separation improves the overall clarity and maintainability of the codebase.
* **Minimization of Complexity**: Combining the form view and the printed view within the same page can introduce unnecessary complexity, as the requirements for each view might differ. By separating them, we can eliminate any potential conflicts and make the code easier to understand and maintain.
* **Development Efficiency**: Separating the views allows developers to focus on implementing specific functionality for each view independently. This division of work enables parallel development and faster iteration cycles, ultimately improving development efficiency.
* **Maintainability**: The separation of views simplifies future updates and modifications. Changes to one view are less likely to impact the other, reducing the risk of introducing unintended side effects. It also facilitates easier bug tracking and troubleshooting.

### Negative Consequences

* **Increased Development Effort**: Separating the views may require additional development effort initially, as it involves creating and maintaining separate view files. However, the long-term benefits of improved maintainability and reduced complexity outweigh the initial investment.

## Alternatives Considered

### Option 1: Combine the form view and the printed view within the same page using Bootstrap

This option would involve utilizing Bootstrap to create a single page that includes both the form view and the printed view. However, combining the views within the same page could introduce unnecessary complexity and dependencies. Additionally, using Bootstrap might result in an overly complex implementation, as the requirements for the form view and the printed view might differ significantly.

### Option 2: Separate the printed view from the form view

Under this option, we would separate the printed view and the form view into separate pages or components. This would simplify the responsibilities of each view, but it would not address the concern about using Bootstrap and its potential complexity.

## Rationale

We chose option 3, which involves separating the printed view from the form view and avoiding the use of Bootstrap, to simplify responsibilities and minimize complexity. By separating the views, we can assign clear responsibilities to each view and ensure a more maintainable codebase. Additionally, avoiding the use of Bootstrap for these views eliminates unnecessary dependencies and reduces the risk of introducing unnecessary complexity. This decision enables faster development iterations and improved long-term maintainability.

## Related to

* [ADR pdf library](./adr-1-pdf-library.md)
