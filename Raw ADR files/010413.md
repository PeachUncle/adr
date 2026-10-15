## ADR 007: Next.js for frontend

## Context
We need to select a framework for developing the frontend of NeuroLingo, a cross-platform language learning application. The framework must support several requirements. These include search engine optimization for improved discoverability, server-side rendering (SSR) and static site generation (SSG) to enhance performance, scalability to handle potential future growth, a rich ecosystem and compatibility with modern tools and libraries, cross-platform support for web and mobile users, and ease of developer onboarding and productivity. The framework must also be compatible with TypeScript, as this is our chosen language for the frontend. 

### Options

Next.js offers built-in support for SSR and SSG, excellent search engine optimization capabilities, and a robust developer experience with TypeScript and CSS-in-JS. It also provides a rich plugin ecosystem, including strong support for tools like Tailwind CSS and i18n, a large community, extensive documentation, and easy integration with backend APIs. However, it requires server hosting for SSR functionality and has a learning curve for developers unfamiliar with React. Even for those familiar with React, latest versions of Next.js introduce a new routing system that may be unfamiliar.

React without Next.js is lightweight and flexible. It operates fully client-side, eliminating the need for server hosting, and is familiar to most frontend developers. However, it lacks native SSR and SSG support, requiring additional tools like Gatsby or custom solutions, and offers poor SEO out of the box. It is also less suited for large-scale applications compared to Next.js.

Vue.js, with options like Nuxt.js, provides SSR and SSG capabilities similar to Next.js. It has good community support, documentation, and is relatively flexible. However, its ecosystem is much smaller compared to React/Next.js, and adopting it would add additional overhead in the form of training time as most of our team primarily has experience with Next or React.

## Decision

We will use Next.js to build the frontend for NeuroLingo. This decision aligns with our need for SSR/SSG capabilities, search engine optimization, scalability, and developer productivity. Next.js is also widely adopted, ensuring access to community support and open source extensions.

## Status

Accepted

## Consequences

The adoption of Next.js will lead to several consequences. On the positive side, it will improve user experience due to fast-loading pages and optimized performance. The enhanced SEO will lead to better discoverability. Development will be streamlined through built-in tools and plugins, and it will simplify integration with APIs and back-end services. On the negative side, the requirement for server hosting will increase costs. However, we believe the benefits outweigh the drawbacks, making Next.js the most suitable framework for this project.
