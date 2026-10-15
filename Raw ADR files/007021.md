# ADR 005: Adopt the Atomic Design Principles for building UI components

- **Date created**: 04/02/2025
- **Driver**: Alex Foxleigh (Foxy)

## Status

![rejected]

## Context

In order to build a consistent, scalable and maintainable UI, we need to adopt a set of principles which will help us to build our components in a way that will allow us to do this.

## Advice

I would recommend using Brad Frost's [Atomic Design Principles](https://atomicdesign.bradfrost.com/table-of-contents/). These principles are a set of guidelines that will help us to build our components in a way that will allow us to build a consistent, scalable and maintainable UI.

It breaks down the UI into 5 different levels:

- Atoms
- Molecules
- Organisms
- Templates
- Pages

Each level is built on top of the previous level. Rather than going into detail
about each level, I would recommend reading the article linked above. It is a
very good read and will give you a much better understanding of the principles.
However, in a nutshell, the principles are as follows:

- Atoms are the smallest components that make up the UI. They are the building blocks of the UI.
- Molecules are groups of atoms that work together to form a more complex component.
- Organisms are groups of molecules that work together to form a more complex component.
- Templates are a set of components that are used to build a page and are reused across multiple pages.
- Pages are groups of molecules that work together to form a more complex component.

Atoms, Molecules and Organisms are built in isolation and are not aware of the
data layer. This means that they can be used in any project or microservice and
still work as expected. That can use their own internal state but should not be
aware of any external data other than that which is passed to them as props.

I would also recommend the use of an additional level, which is the 'Partial' level.
This level is used to build components that are smaller than a page but requires
access to the data layer. This is useful when building complex pages such as
multi-step forms. It keeps your compoenents small and pure and allows you to build
complex pages without having to build a single, unwieldy page component.

In addition to the above, I'd recommend also splitting out input components into
their own level. This is because input components can be various different types
and splitting them into their own level will make it easier for a developer to
find the component they are looking for.

I recommend using Storybook to build and document the components. Storybook is a
tool that allows you to build and document your components in isolation. It allows
you to see how the component looks and behaves in isolation and also allows you
to see how the component looks and behaves when it is used in a page. It also
allows you to see how the component looks and behaves when it is used in a template.
There is an ADR for Storybook which you can read [here](./adr-007-storybook.md).

## Discussions

- Alex Foxleigh - This is the place to discuss the ADR. Please keep the discussion
  on topic and try to avoid repeating the same points. Please put your name next to
  any points you make.

## Decision

Utilise the principles of Atomic Design but categorise input components based on
their functionality, e.g. 'inputs', 'layout', 'navigation', etc. rather than
their atomic level.

## Consequences

- We will be able to build a consistent, scalable and maintainable UI.
- We will be able to build components in isolation and reuse them across multiple projects.
- We will be able to build complex pages by combining smaller components.
- Application code will be easier to maintain and understand.
- As only pages, partials and templates will be aware of the data layer, the
  application will be easier to test and develop. It also ensures that the
  components are pure and can be used in any project.

[proposed]: https://img.shields.io/badge/Proposed-yellow?style=for-the-badge
[accepted]: https://img.shields.io/badge/Accepted-green?style=for-the-badge
[superceded]: https://img.shields.io/badge/Superceded-orange?style=for-the-badge
[rejected]: https://img.shields.io/badge/Rejected-red?style=for-the-badge
[deprecated]: https://img.shields.io/badge/Deprecated-grey?style=for-the-badge
