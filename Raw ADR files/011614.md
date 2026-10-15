# 4. Frontend Framework: Vue

Date: 2024-06-01

## Status

Accepted

## Context

The frontend of the project doesn't necessarily require a framework but for someone without a web development background they seem to offer a nice solution. The framework should facilitate building interactive and dynamic user interfaces with minimal complexity. Considering my limited experience, I need a tool that allows me to leverage my existing knowledge while reducing the effort required to handle vanilla JavaScript complexities. Additionally, choosing between TypeScript and JavaScript within the framework is crucial to mitigate potential errors and improve code maintainability.

## Considered Options

* Vue with JavaScript
* Vue with TypeScript
* React
* Angular
* Vanilla JavaScript

## Decision

I have chosen Vue as the frontend framework with TypeScript for the following reasons:

- **Familiarity**: Vue is the only framework I have used in a project so far, which reduces the learning curve and allows me to build upon my existing knowledge.
- **Ease of Use**: Vue's simplicity and ease of integration make it suitable for someone without a strong web development background.
- **TypeScript**: Using TypeScript within Vue helps mitigate errors before runtime, provides better tooling, and enhances code maintainability.

## Consequences

### Vue with JavaScript

**Pros:**

- Simplicity and ease of use for beginners.
- A large community and extensive documentation available for support.
- Fast to set up and start developing.

**Cons:**

- Lack of type safety can lead to runtime errors that are harder to debug.
- As projects grow, JavaScript codebases can become harder to maintain and refactor.

### Vue with TypeScript

**Pros:**

- Type safety reduces the likelihood of runtime errors and enhances code reliability.
- Improved tooling and editor support for autocompletion and type checking.
- Facilitates better code organization and maintainability, especially in larger projects.

**Cons:**

- Initial setup and configuration can be more complex than plain JavaScript.
- Learning curve associated with understanding TypeScript's type system.

### React

**Pros:**

- Large community and ecosystem with extensive libraries and tools.
- Flexibility in building complex applications with a component-based architecture.

**Cons:**

- Steeper learning curve for someone without a web development background.
- Requires more boilerplate code compared to Vue.

### Angular

**Pros:**

- Comprehensive framework with built-in tools for large-scale applications.
- Strong support for TypeScript out of the box.

**Cons:**

- Very steep learning curve, particularly challenging for beginners.
- More opinionated and complex than Vue, potentially overwhelming for small to medium projects.

### Vanilla JavaScript

**Pros:**

- No additional libraries or frameworks required.
- Full control over the code without any abstractions.
- Provides knowledge about what's happening "under the hood" of frameworks for future web projects.

**Cons:**

- Tedious and time-consuming to build complex applications.
- Lack of structure can lead to unmanageable and error-prone codebases.
- No built-in tools for state management, component structure, or reactive data binding.

## Conclusion

I have chosen Vue as the frontend framework due to its ease of use, familiarity, and ability to build upon my existing knowledge. To further enhance code reliability and maintainability, I am using TypeScript within Vue. This decision aligns with my current skills and helps me improve my web development proficiency while mitigating common JavaScript pitfalls.

