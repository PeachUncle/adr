# Architecture Pattern

* Status: Proposed
* Deciders: Casey Cheung, Habib Ullah, Rami Kotaiche
* Date: 2024-11-14

Technical Story: The chosen architecture needs to ensure separation of concerns, maintainability, and scalability for the library management system.

## Context and Problem Statement

We need a system architecture that enables a clear separation of responsibilities, supports scalability, and simplifies collaboration between development teams. It should also cater to multi-channel access (web, phone, and in-branch) while allowing easy updates and extensions to the system.

## Decision Drivers

* Scalability: The need for the system to handle a growing number of users and data across multiple platforms.
- Real-time Data Updates: Required for dynamic and interactive interfaces.
- Team Collaboration: A structure that supports modular development and independent work by the team.

## Considered Options

* Model-View-Controller (MVC)
* Three-Tier Architecture

## Decision Outcome

Chosen option: "Model-View-Controller", because The team selected MVC due to its flexibility and suitability for an interactive library management system. The clear separation of responsibilities between the Model, View, and Controller layers allows for easier maintenance and scaling, particularly as the system integrates multi-channel access points.

While the three-tier architecture is a strong contender for its reliability and simplicity, it lacks the flexibility and real-time capabilities that MVC provides, making it less ideal for this project.

### Positive Consequences

* Clear separation of concerns: Models handle data, Views manage the UI, and Controllers process user input.
* Enhances maintainability and testability, as individual components can be modified or tested independently.
* Scales well for web-based systems and multi-channel applications.

### Negative Consequences

* Requires disciplined implementation to avoid tightly coupling components.
* Complexity can increase with larger projects or highly interactive UIs.

## Pros and Cons of the Options

### Model-View-Controller

An architectural pattern that separates the application into three interconnected components:

Model: Manages the data and business logic.
View: Handles the user interface and displays data.
Controller: Manages user input and updates Models and Views accordingly.

* Good, because - Ideal for applications with dynamic user interfaces.
- Supports asynchronous data updates, suitable for real-time features.
- Clear modularity simplifies debugging and any enhancements.
* Bad, because - Requires proper planning to avoid tightly coupling Controller logic with Views.
- Can lead to overcomplication in simple use cases.

### Three-Tier Architecture

A traditional architecture pattern that separates an application into three layers:

Presentation Tier: The user interface (frontend).
Logic Tier: Business logic and data processing.
Data Tier: Database and data storage.

* Good, because - Strong focus on scalability and reliability.
- Clear separation between user-facing and backend logic.
* Bad, because - Less flexible for interactive and dynamic UIs.
- The rigid tier structure can make cross-layer communication inefficient.
- Not as optimized for real-time data updates as MVC.

## Links

* MVC Design Pattern Overview. (n.d.). Retrieved from https://www.mvc.com
- Three-Tier Architecture. (n.d.). System Design Handbook. Retrieved from https://www.systemdesignhandbook.com
