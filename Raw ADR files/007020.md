# ADR 004: Use SASS as our Theming engine (with SCSS Modules)

- **Date created**: 04/02/2025
- **Driver**: Alex Foxleigh (Foxy)

## Status

![accepted]

## Context

Choosing a suitable CSS stack for our theming engine.

## Advice

I recommend using [SASS](https://sass-lang.com/). SASS is a mature and powerful
CSS preprocessor and when combined with (S)CSS-modules, it can be used to create
a modular CSS system, ensuring that our CSS is as modular and reusable as possible.

SASS also has a lot of powerful features, such as mixins, nesting and functions,
which can be used to create a robust and comprehensive theming engine.

We would be specifically using the 'SCSS' syntax for SASS as this is more closely
aligned with the CSS specification.

## Alternatives

Another contender for this decision was [TailwindCSS](https://tailwindcss.com/). 
Tailwind is a popular utility-first CSS framework that allows for rapid development 
by applying styles directly to elements through utility classes.

Tailwind has a growing ecosystem and is widely used, particularly in the React 
and Next.js communities. It enforces consistency through a central configuration 
file (tailwind.config.js) where developers can define theme variables, spacing, 
typography, and other design tokens. Teams can also use the @apply directive to 
create reusable styles, reducing some of the concerns around utility class bloat.
This is not an ideal solution though and is even discouraged by Adam Wathan 
(The creator of Tailwind).

However, there are some trade-offs to consider. Tailwind introduces a learning 
curve for developers unfamiliar with its utility-first approach. The heavy use of
classes in the markup can make the HTML harder to read, and enforcing a strict 
design system requires additional effort through custom configurations. While 
Tailwind’s Just-in-Time (JIT) compiler helps keep the final CSS size minimal, 
it can still lead to verbose class structures, especially in larger applications.

Ultimately, while Tailwind offers a fast development workflow, we believe SCSS 
provides better long-term maintainability, particularly in terms of structuring 
styles in a modular way and keeping concerns separate from the component markup.

## Discussions

- Alex Foxleigh - This is the place to discuss the ADR. Please keep the discussion
  on topic and try to avoid repeating the same points. Please put your name next 
  to any points you make.

## Decision

Implement SCSS as our Theming engine.

## Consequences

- All components will be modular and reusable with standalone SCSS-modules
  whilst still having access to the variables, mixins and functions from the main theme.
- We will be adopting a robust and well supported CSS framework with a huge
  ecosystem of plugins and extensions. As well as a solid number of developers who
  will be able to work with this technology for years to come.
- Encourages separation of concerns and modularity.
- We will have a large community of developers who are willing to help with
  any issues we may have.
- Hiring and onboarding new developers will be easier as there is a large
  community of developers who are familiar with SASS.
- All of our current projects already use SASS and therefore migration will
  be easy and there will be no learning curve for developers.

[proposed]: https://img.shields.io/badge/Proposed-yellow?style=for-the-badge
[accepted]: https://img.shields.io/badge/Accepted-green?style=for-the-badge
[superceded]: https://img.shields.io/badge/Superceded-orange?style=for-the-badge
[rejected]: https://img.shields.io/badge/Rejected-red?style=for-the-badge
[deprecated]: https://img.shields.io/badge/Deprecated-grey?style=for-the-badge
