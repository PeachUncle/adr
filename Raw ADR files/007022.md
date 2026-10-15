# ADR 006: Use Storybook to build and document the application UI

- **Date created**: 04/02/2025
- **Driver**: Alex Foxleigh (Foxy)

## Status

![accepted]

## Context

Making sure an application is robust, performant and accessible can be a challenge.
It also needs to be easily maintainable, this requires clear, concise and up-to-date
documentation, which is often a problem in development teams.

## Advice

I would recommend using [Storybook](https://storybook.js.org/).
In their own words "Storybook is a frontend workshop for building UI components
and pages in isolation." The 'in isolation' part is key here, as if the element
we have just built works in isolation, we can be confident that it's likely to
work everywhere.

There are some distinct benefits to using Storybook:

- It has a vast plugin library which can allow we to add some really useful testing
  features (e.g. unit tests and accessibility tests) with ease.
- We could have a shared component library which we can use across all of our
  projects. This would hugely reduce the amount of time developrs spend building
  new components and pages.
- It has a 'smoke test' feature which allows we to quickly check that all our
  stories are working without having to spin up a full instance of the application.
- It makes keeping documentation up to date much simpler.
- It makes onboarding a breeze as all a new developer needs to do to learn how muuch
  of the app works AND see it's documentation side-by-side is run the storybook instance.
  We can even host a copy of it separately so we can just give a new developer a
  link to visit.
- Similar to the above, it makes UAT (User Acceptance Testing) much more granualar.
  We can give the user a link to the storybook site pointing at the element we
  want them to review and they won't be distracted by anything else as they will
  only see that element.

The one main caveat of this though is that it HAS to become a part of the development
process. Developers should be building new components, partials, pages and templates
IN Storybook, ensuring that they are designed to work in isolation and ensure that
they make individual stories for every distinct feature and/or variation that the
element has. This does add a bit of an overhead, however it saves time elsewhere
as if the Storybook instance is configured correctly and has the right plugins,
it will be able to run unit tests, accessibility tests and even visual regression
tests on the stories without any extra work.

It also minimises technical debt as the documentation is always up to date and the
stories are always working, we could easily add a storybook smoke test to our
CI/CD pipeline to ensure that all stories are working before a new version is deployed,
dramatically reducing the risk of deploying a broken version of the app.

## Discussions

- Alex Foxleigh - This is the place to discuss the ADR. Please keep the discussion
  on topic and try to avoid repeating the same points. Please put our name next to
  any points we make.

## Decision

Implement Storybook into the application.

## Consequences

- All new components, partials, pages and templates would be built in Storybook
  and have their own, detailed stories.
- All new components, partials, pages and templates would be built with
  accessibility in mind.
- All new components, partials, pages and templates would be built with unit
  tests in mind.
- All new components, partials, pages and templates would be built with visual
  regression tests in mind.
- All new components, partials, pages and templates would be built with performance
  in mind.
- All new components, partials, pages and templates would be built in isolation.
  This means that they should be able to be used in any project and still work
  as expected.
- All new components, partials, pages and templates would be built with documentation
  in mind. This means that the documentation for the element should be kept up
  to date and should be easily accessible.
- Onboarding new developers should be much easier as they will be able to see how
  the application works and how the look and feel is achieved.
- UAT will be much easier as we can give the user a direct link to the individual
  story for the element we want them to review.
- Application robustness will be improved significantly.
- There will be an extra overhead when building new elements, however this will
  be offset by the benefits listed above.
- There will be a small learning curve for new developers to get used to building elements
  in Storybook if they are not already familiar with it. (Storybook is already used in our
  projects, although not as extensively as I would like.)

[proposed]: https://img.shields.io/badge/Proposed-yellow?style=for-the-badge
[accepted]: https://img.shields.io/badge/Accepted-green?style=for-the-badge
[superceded]: https://img.shields.io/badge/Superceded-orange?style=for-the-badge
[rejected]: https://img.shields.io/badge/Rejected-red?style=for-the-badge
[deprecated]: https://img.shields.io/badge/Deprecated-grey?style=for-the-badge
