# ADR 002: Use React and NextJS as the primary frontend stack

- **Date created**: 04/02/2025
- **Driver**: Alex Foxleigh (Foxy)

## Status

![accepted]

## Context

Choosing a primary frontend stack to use for the project.

## Advice

[NextJS](https://nextjs.org/) is a JavaScript framework that sits on top of
React. It is an 'opinionated' framework that is still incredibly flexible and can
be customised to your needs.

It has a robust ecosystem of plugins and libraries that make it easy to
build applications as well as a large following of developers, making
onboarding and maintenance much easier. As it is just React under the
hood, it is very future-proof and if a developer is familiar with React they can
easily pick-up NextJS. It also has a large community of developers who are willing
to help with any issues you may have.

## Alternatives

- [Create React App](https://create-react-app.dev/)

I would recommend against using Create React App as it is less configurable as NextJS.
The benefit of using Create React App is lost as soon as you need to customise the
configuration. This is because you will have to eject from Create React App and
then you will have to maintain the configuration yourself\*. This is not a problem
with NextJS as it is very configurable out of the box.

\*As soon as you eject a Create React App project, you are no longer actually using
Create React App. This means you are now responsible for keeping all of the
dependencies up to date yourself. This is not a problem with NextJS as it is very
well maintained and is constantly being updated.

## Discussions

- Alex Foxleigh - This is the place to discuss the ADR. Please keep the discussion
  on topic and try to avoid repeating the same points. Please put your name next to
  any points you make.

## Decision

Implement NextJS as the primary frontend stack.

## Consequences

- We will have a simple file-based routing system
- We will have a well defined project folder structure which is easy to
  understand
- Many react-essentials packages will be available out of the box (e.g.
  TypeScript, Jest, Sass, etc.) and usable with minimal configuration.
- We will have a large community of developers who are willing to help
  with any issues we may have.
- Hiring and onboarding new developers will be easier as there is a large
  community of developers who are familiar with NextJS and React.
- NextJS is an opinionated framework, so we will have to be careful not
  to stray too far from the conventions that it provides.

[proposed]: https://img.shields.io/badge/Proposed-yellow?style=for-the-badge
[accepted]: https://img.shields.io/badge/Accepted-green?style=for-the-badge
[superceded]: https://img.shields.io/badge/Superceded-orange?style=for-the-badge
[rejected]: https://img.shields.io/badge/Rejected-red?style=for-the-badge
[deprecated]: https://img.shields.io/badge/Deprecated-grey?style=for-the-badge
