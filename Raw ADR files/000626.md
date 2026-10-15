# Use React for Frontend Web Development

## Context and Problem Statement

In the context of developing the front end for our web application, we need to choose a JavaScript library or framework that facilitates efficient and maintainable development. The problem at hand is to select the most suitable technology that aligns with our project requirements and development goals. The decision should be based on factors such as developer community support, ease of integration, and long-term maintainability.

## Decision Drivers

* **Community Support:** The availability of a robust and active developer community.
* **Type Safety:** The ability to use static typing for enhanced code quality.
* **Ecosystem Compatibility:** Integration capabilities with third-party libraries and tools.

## Considered Options

* ReactJS
* React + Typescript
* VueJS
* Angular

## Decision Outcome

Chosen option: **ReactJS + Typescript**, because it combines the flexibility and popularity of React with the added benefits of static typing offered by Typescript. This choice ensures a scalable and maintainable codebase.

### Positive Consequences

* **Community Backing:** React is widely adopted, and combining it with Typescript ensures a strong and supportive community.
* **Type Safety:** Typescript adds static typing, reducing runtime errors and improving code quality.
* **Ecosystem Integration:** React's extensive ecosystem and compatibility with Typescript provide a wide range of tools and libraries for development.

### Negative Consequences

* **Learning Curve:** Developers might need some time to adapt to the syntax and concepts of Typescript.
* **Build Complexity:** Introducing Typescript may increase build complexity, but the benefits outweigh the drawbacks.

## Pros and Cons of the Options

### ReactJS

* Good, because it is the most popular according to [Stackoverflow 2022 Developer Survey](https://survey.stackoverflow.co/2022/#technology-most-popular-technologies).
* Good, for its component-based architecture, enabling modular and reusable code.
* Neutral, as it lacks built-in support for static typing.
* Bad, because potential for runtime errors due to lack of type checking.

### React + Typescript

* Good, because it is the most popular according to [Stackoverflow 2022 Developer Survey](https://survey.stackoverflow.co/2022/#technology-most-popular-technologies).
* Good, for combining the benefits of React with static typing for improved code quality.
* Neutral, as there is a learning curve associated with Typescript.
* Bad, because of potential build complexity.

### VueJS

* Good, for its simplicity and ease of integration.
* Good, for its flexible and approachable design.
* Neutral, as it may lack the same level of community and third-party support as React.
* Bad, because it may not be as widely adopted in the industry.

### Angular

* Good, because it uses Typescript by default instead of Javascript.
* Bad, because it has a steeper learning curve compared to the other options.
* Bad, for its heavier framework that may lead to increased development time.
* Neutral, as it may be overkill for smaller projects.

## Links
- [Mi Classrooms ADR-0002](https://github.com/mi-classroom/mi-web-technologien-beiboot-ss2022-Moosgloeckchen/blob/be96353229bb0514241963bb8b1d32fe4bd153f8/docs/decisions/0002-react-frontend.md)
