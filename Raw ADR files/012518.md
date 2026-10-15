# Choosing the Frontend Framework for the Nordic Bank Core System
- Status: accepted
- Deciders: @hansen1904
- Date: 2024-12-08

## Context and Problem Statement
We need to select the most appropriate frontend framework for developing the user interface of Nordic Bank's core banking system. The framework must meet our requirements for performance, maintainability, scalability, and developer productivity. This decision will impact the development process and user experience.

## Decision Drivers
- Performance: The framework must offer high performance to ensure a smooth user experience.
- Maintainability: The framework should be easy to maintain and have strong community support.
- Scalability: The framework must support scalable architecture to accommodate future growth.
- Developer Productivity: The framework should enhance developer productivity and provide robust tools and features.
- Team Expertise: The framework should align with the current skills and expertise of our development team.

## Considered Options
- React
- Angular
- Vue.js

## Decision Outcome
Chosen option: "React", because it offers high performance, a strong community, and a rich ecosystem of tools and libraries. Additionally, our development team has significant experience with React, ensuring a smooth development process.

### Positive Consequences
- High performance, leading to a smooth and responsive user experience.
- Strong community support and a rich ecosystem of tools and libraries.
- Alignment with the team's existing expertise, reducing the learning curve.
- Flexibility in building reusable components.

### Negative Consequences
- Requires additional configuration and setup compared to some other frameworks.
- The large ecosystem can sometimes lead to decision fatigue due to the number of available options.

## Pros and Cons of the Options

### React
- **Pros**:
    - Offers high performance and flexibility.
    - Has strong community support and a rich ecosystem.
    - Aligns with the team's expertise.
- **Cons**:
    - Requires additional configuration and setup.
    - The large ecosystem can lead to decision fatigue.

### Angular
- **Pros**:
    - Provides a comprehensive framework with built-in features.
    - Has strong community support and documentation.
- **Cons**:
    - Has a steeper learning curve.
    - It can be overkill for simpler applications.

### Vue.js
- **Pros**:
    - Easy to learn and integrate.
    - Offers a flexible and performant framework.
- **Cons**:
    - Has a smaller community compared to React and Angular.
    - May lack some advanced features found in other frameworks.