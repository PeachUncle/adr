# 0002. Use React

## Date

2023-02-20

## Approved By

@danascheider

## Decision

We will use React as our JavaScript library for the new front end.

## Glossary

- **Create React App (CRA):** A lightweight, React-based [framework](https://create-react-app.dev/) enabling React apps to be created quickly and easily
- **CSS modules:** A [CSS preprocessing solution](https://github.com/css-modules/css-modules) enabling CSS rules to be scoped to an individual component or element, all but eliminating the need to manage cascades
- **Preact:** A lighter-weight [library](https://preactjs.com) with very similar features and API to React
- **React:** A fully-featured [front-end JavaScript library](https://reactjs.org) enabling the use of an HTML-like syntax to create page components in isolation
- **Storybook:** A [developer tool](https://storybook.js.org/) enabling components in React or other component-based frameworks to be viewed and interacted with in isolation from the rest of the page
- **Svelte:** A [front-end JavaScript library](https://svelte.dev) that competes with React
- **TypeScript:** A JavaScript-based [language](https://typescriptlang.org) that incorporates strong typing (see TypeScript ADR for details)
- **Vue.js:** A [front-end JavaScript library](https://vuejs.org) that competes with React; Vue is currently the most popular frontend library/framework

## Context

Several challenges have recently converged, pushing us to implement a full rewrite of the SIM front end. The new Google identity API proved very difficult to integrate with, prompting us to consider a move to [Firebase](/docs/adrs/0001-use-firebase.md). We'd been wanting to port the app to [TypeScript](https://typescriptlang.org) for some time, and it would be easier to achieve this during a rewrite. The discovery that [Create React App](https://create-react-app.dev/) may no longer be maintained was the last straw pushing us to move to a new framework, necessitating a rewrite.

Since we were contemplating a rewrite anyway, it made sense to revisit the question of whether React was the best tool for the job.

## Considerations

We considered React as well as three other, competing libraries:

- [Preact](https://preactjs.com)
- [Vue.js](https://vuejs.org)
- [Svelte](https://svelte.dev)

In considering these libraries, we considered the following factors:

- **Similarity to React:** Much of our tech stack is changing significantly for this rewrite, and as such, we want to ensure that the learning curve for a new library is minimal, unless there are truly compelling reasons to accept a steeper one.
- **Application state management:** We're using React contexts to handle application state. These have worked so far, however, they are a bit cumbersome. We were interested to know if any of the other libraries offered more elegant solutions to this problem.
- **Compatibility with Firebase:** Since we'd already decided to use [Firebase](https://firebase.google.com), any solution we chose needed to be interoperable with Firebase.
- **TypeScript support:** We needed to be sure that we would be able to use TypeScript to its fullest advantage in whichever library we chose.
- **Testing options:** Front-end testing is always a pain point, and we need any solution we use to be at least as testable as React.
- **Accessibility features:** One of our priorities is accessibility, which is an afterthought in many cases in frontend development. Out-of-the-box accessibility features would be a big bonus.
- **Security features:** Security is another priority, and one that can be difficult to get right. Sensible default settings around security are important.
- **Available documentation and resources:** Documentation determines whether an implementation will go smoothly or be very painful. We were looking for well-documented solutions with enough adoption to have resources available on blogs, StackOverflow, and more.
- **CSS module support:** In the legacy front end, we used CSS modules, and they worked great. If possible, we'd like to use them again. If they are not supported, we would need to investigate the best styling alternatives for whatever library we chose.
- **Storybook support:** Storybook is an exceptional development tool. Support for Storybook is all but a hard-and-fast requirement.
- **Additional or missing features:** We also wanted to consider any outstanding features a library offered that differentiated it from its competitors, even if it didn't fit neatly into the criteria we were prioritising. Likewise, we needed to consider any features we're using that were missing from a given solution.

These are a lot of factors to cover in a single ADR, however, there is a [Google doc](https://docs.google.com/document/d/1w0BbmBMs_55QBtHEndTHq7tPYHQObrq3R2_qwbnKbgw/edit?usp=sharing) summarising the comparisons between the libraries we considered.

## Summary

Preact was clearly inadequate for our use case since it was simply meant for projects of more limited scope. Vue and Svelte had some compelling points and met most of our criteria, however, they are dissimilar to React to such an extent that we would need to invest significant time in learning. Their advantages over React were insufficient to justify putting in that effort.
