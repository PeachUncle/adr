# Choosing Remix and Epic Stack

Date: 2024-08-27

Status: Accepted

## Context and Problem Statement

When building a modern web application, choosing the right framework and starter kit is crucial for productivity, performance, and maintainability. This decision addresses the selection of Remix as the web framework and the Epic Stack as the starter kit for our project, considering alternatives and the specific benefits of Remix.

### Decision Drivers

* Need for a modern, performant web framework
* Desire for a full-stack TypeScript solution
* Importance of developer productivity and good developer experience
* Requirement for a solid foundation with essential tools and setups
* Preference for a framework that aligns with web standards and reduces developer frustration

## Decision Outcome

Adopt Remix as the web framework and use the Epic Stack as the starter kit for our project.

### Positive Consequences

* Improved performance with server-side rendering and efficient client-side updates
* Streamlined development process with a well-structured starter kit
* Access to a growing ecosystem and community support
* Ability to leverage modern web standards and best practices
* Reduced developer frustration compared to some alternatives

### Negative Consequences

* Learning curve for developers new to Remix
* Potential limitations in customization if heavily relying on Epic Stack defaults

## Consequences

### Choosing Remix

* Good, because it provides a modern, full-stack web framework built on web standards
* Good, because it offers excellent performance through server-side rendering and efficient client-side updates
* Good, because it simplifies data loading and mutation with a clear separation of concerns
* Good, because it supports nested routing, which aligns well with complex application structures
* Good, because it has built-in error handling and progressive enhancement
* Good, because it focuses on web standards, making it easier to understand and work with compared to more abstracted frameworks

### Adopting the Epic Stack

* Good, because it provides a comprehensive starter kit with essential tools and setups
* Good, because it includes best practices for deployment, testing, and development workflows
* Good, because it offers a solid foundation that can be customized to fit specific project needs
* Good, because it includes pre-configured tools like Prisma for database access, Tailwind for styling, and testing utilities
* Bad, because it may include some opinionated choices that might not fit all project requirements

## Comparison with Alternatives

### Next.js

* While Next.js is popular, it has been known to cause frustration among developers due to frequent changes and complexity in certain areas
* Remix offers a more straightforward approach to server-side rendering and data fetching
* Remix's focus on web standards makes it easier to reason about compared to Next.js's abstractions

### SvelteKit

* SvelteKit is a powerful framework, but my own experience is primarily with React
* Choosing Remix allows us to leverage our existing React knowledge while gaining the benefits of a full-stack framework

### Simple HTML/JS/CSS Stack

* While a simple HTML/JS/CSS stack offers flexibility, it lacks the built-in structure and tooling for scalable applications
* Remix provides a modern, scalable structure out of the box, which is crucial for larger projects
* The full-stack TypeScript approach in Remix offers better type safety and developer experience compared to a simple stack

## Remix as a Meta Framework

Remix is considered a meta framework because it builds upon React, extending its capabilities to create a full-stack web development solution. According to [Bejamas](https://bejamas.io/hub/web-frameworks/remix):

* Remix is a full-stack web framework built on top of React
* It embraces web standards and leverages them to provide better user and developer experiences
* Remix focuses solely on SSR with both Node.js and Edge runtimes, making it ideal for applications with many pages that rely heavily on dynamic data
* It supports nested routes, which other frameworks adopted later
* Remix emphasizes progressive enhancement, allowing the data layer of an app to function with or without JavaScript on the page

These features make Remix a powerful choice for building modern, performant web applications while maintaining a focus on web standards and developer productivity.

## Links

* [Remix Documentation](https://remix.run/)
* [Epic Stack Repository](https://github.com/epicweb-dev/epic-stack)
* [Bejamas Remix Overview](https://bejamas.io/hub/web-frameworks/remix)