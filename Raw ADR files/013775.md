# 3. UI patterns showcase

Date: 2017-08-01

## Status

Accepted

## Context

We need a tool to showcase all the UI patterns and we can use as a development environment.

- Human friendly _live_ patterns showcase.
- Documentation
- Test runner

Lots of different options:

- [Storybook](https://storybook.js.org/): UI dev environment you'll love to use
- [react-cosmos](https://github.com/react-cosmos/react-cosmos): DX tool for designing reusable React components
- [reactcards](https://github.com/steos/reactcards): devcards for react
- [React Styleguidist](https://react-styleguidist.js.org/): isolated React component development environment with a living style guide
- [Atellier](http://scup.github.io/atellier/) is a React component that gives you an accessible way to interact with your components library.
- [carte-blanche](https://github.com/carteb/carte-blanche): An isolated development space with integrated fuzz testing for your components. See them individually, explore them in different states and quickly and confidently develop them.
- [Catalog](https://interactivethings.github.io/catalog). Create living style guides using Markdown or React
- [React BlueKit](http://bluekit.blueberry.io/): Render React components with editable source and live preview
- [react-styleguide-generator](https://github.com/pocotan001/react-styleguide-generator): Easily generate a good-looking styleguide by adding some documentation to your React project.
- [react-demo](https://github.com/rpominov/react-demo): A React-component for creating demos of other components
- [patternplate](https://github.com/sinnerschrader/patternplate): 📘 Create, present and deliver component libraries

Non-React specific:

- [Source](https://sourcejs.com/): tool for documenting, testing and managing UI components achieving productive team work.
  - with [sourcejs-react-styleguidist](https://github.com/sourcejs/sourcejs-react-styleguidist): React Styleguidist Integration Plugin for SourceJS
- [Fractal](http://fractal.build/): Build. Document. Integrate.
Powerful component libraries & styleguides that fit the way you work.
- [Nucleus](https://holidaypirates.github.io/nucleus/): Living style guide generator


## Decision

We use [Storybook](https://storybook.js.org/) to showcase UI patterns.

Main reasons for this decision are:

- **maturity**   
  It had already a couple of iterations, current version is 3 and it has over 700 issues resolved.
- **community**   
  Kadira, original creators, handed over the project to the community: [The Storybook Story](https://medium.com/storybookjs/the-storybook-story-dd3c1ab0d2ce).   
  It is easy to find blog post describing different use cases for Storybook.
- **flexibility**   
  [Addons](https://storybook.js.org/addons/introduction/) are a powerful feature to customise your Storybook to your needs.   
  And they are opening to more UI libraries than React: [Introducing: Storybook for Vue 🎉](https://medium.com/storybookjs/introducing-storybook-for-vue-940f222541c5)

## Consequences

Every UI pattern must have at least one [Story](https://storybook.js.org/basics/writing-stories/).

**Stories** will be written in a file finished with `.stories.js` in the folder for the UI pattern.

**Stories** describe the different states/variations of the component that will be shown in the Storybook.
