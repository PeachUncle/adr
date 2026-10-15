## ADR 002: Typescript for frontend language

## Context
Choosing the right language for frontend development is critical to ensuring a smooth development experience, maintainability, and performance. The frontend of a web application requires interactivity, responsiveness, and integration with back-end services, making the choice of language an important architectural decision.

### Options
Javascript is the native language of web browsers and by far has the most extensive ecosystem for frontend development. Frameworks like React, Vue.js, and Angular enable the creation of modern, dynamic user interfaces. JavaScript is highly optimized for frontend performance, with extensive browser support and a vast number of third-party libraries. JS can sometimes become difficult to manage in larger applications due to its loosely typed nature, but using TypeScript (a superset of JavaScript with additional key features) mitigates this issue.

Python is primarily a back-end language but can be used for frontend development through frameworks like Brython or Transcrypt, which transpile Python code into JavaScript. There are also other options like Django templates and Streamlit, offering a simple solution to add a UI to a backend. While Python offers readability and a strong developer experience, it lacks the deep browser integration and performance optimizations of JavaScript. Python is not natively supported in browsers, which makes it a less practical choice for frontend development.

Ruby on Rails is a full-stack framework primarily used for back-end development, but it includes some frontend capabilities through ERB (Embedded Ruby) templates and JavaScript integration. While Rails makes it easy to generate HTML and integrate JavaScript, it is not a standalone frontend solution. Most modern Rails applications still rely on JavaScript frameworks for rich frontend experiences.

PHP is traditionally used for back-end development, but it can be used to generate frontend HTML dynamically. While PHP excels at server-side rendering, it is not designed for interactive frontend development in the same way JavaScript is. Modern frontend frameworks rely heavily on JavaScript, making PHP less relevant for handling frontend interactivity.


## Decision

We will use **TypeScript** as the primary language for frontend development. TypeScript’s static typing and improved tooling will help catch errors earlier in the development process, improving overall code quality and maintainability. The structured nature of TypeScript makes it easier to work on large applications and onboard new developers. In addition, it is fully compatible with JavaScript’s ecosystem, including frameworks like React, Vue.js, and Next.js, providing the flexibility and power we need to build modern, dynamic user interfaces. Its deep integration with browsers ensures smooth performance and compatibility, making it the best choice for our frontend stack.

While Python, Ruby on Rails, and PHP have their strengths, they are primarily suited for back-end development. Using these languages for frontend work would introduce unnecessary complexity and limit our ability to leverage modern frontend technologies. By adopting TypeScript, we ensure that our frontend remains performant, maintainable, and aligned with industry best practices.

## Status

Accepted

## Consequences

Using TypeScript will improve the maintainability of our codebase by catching type-related errors at compile time, reducing the likelihood of production bugs. This will lead to fewer runtime issues and a more stable frontend application. Additionally, TypeScript’s type annotations and interfaces will enhance code readability, making it easier for new developers to understand and contribute to the project.

However, as a consequence of this, we are foregoing the simplicity and readability of Python, the convention-driven development style of Ruby on Rails, and the built-in server-side rendering strengths of PHP. While these languages excel in back-end development, they do not offer the same level of interactivity and browser compatibility that JavaScript (and subsequently TypeScript) provide.
