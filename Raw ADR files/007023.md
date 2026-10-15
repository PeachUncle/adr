# ADR 007: Use Redux Toolkit Query for global state management

- **Date created**: 04/02/2025
- **Driver**: Alex Foxleigh (Foxy)

## Status

![accepted]

## Context

We need a way to manage global state in the application. We have a few options:

- [Redux](https://redux.js.org/)
- [Redux Toolkit](https://redux-toolkit.js.org/)
- [Redux Toolkit Query](https://redux-toolkit.js.org/rtk-query/overview)
- [MobX](https://mobx.js.org/README.html)
- React's own built-in Context

I have used Redux Toolkit Query in the past and it has worked well. It is a wrapper
around Redux Toolkit which provides a way to manage global state and also provides
a way to manage API calls. It also has a built in cache which can be used to store
data from API calls, which can then be used to reduce the number of API calls made.
That will improve the performance of the application as well as reducing the amount
of data that needs to be sent over the network.

Redux itself is a very powerful tool, but it can be a bit of a pain to set up and
can be confusing to use, espeically in larger applications. Redux Toolkit makes
it much easier to set up and use but still has quite a steep learning curve. Redux
Toolkit Query is a wrapper around Redux Toolkit which makes it even easier to use.
The learning curve is certaintly not zero but it is much lower than Redux Toolkit
and leaps and bounds lower than Redux itself.

I have never used MobX personally. However, from what I have read, is a much easier
to use tool than Redux. I can't recommend it simply because it does not have the
same level of community support as Redux.

React context is the primary competition here as it can do much of what Redux can do
without the additional overhead, however RTKQuery provides us with automatic cache 
invalidation as well as built-in WebSocket support and a persistent mode. This
would be of use in later phases of the application.

## Advice

I would recommend using Redux Toolkit Query. It is relatively new (it was released
in 2020) but it is already being used in a number of large applications. It is
also being developed by the same people who created Redux Toolkit, so it is very
well supported. The learning curve is much lower than other state management tools
and still comes with all of the power and flexibility of Redux. The cache
management is also very powerful and can be used to improve the performance of
the application.

It also makes a lot of sense from a future-proofing perspective, we will eventually
want to allow offline access (until we build the React Native app, this will be the
only way to use it on mobile and offline support is essential) and we'll certainly
want to add WebSockets support so that multiple users can work on the same location
or even box at the same time.

## Discussions

- Alex Foxleigh - This is the place to discuss the ADR. Please keep the discussion
  on topic and try to avoid repeating the same points. Please put your name next to
  any points you make.

## Decision

Implement Redux Toolkit Query into the application.

## Consequences

- The application will be easier to maintain and develop.
- The application will be easier to test.
- The application will be more performant.
- The application will be more scalable.
- There will be a small learning curve for new developers.
- Developers who are already used to Redux may find the paradigm shift confusing
  at first.

[proposed]: https://img.shields.io/badge/Proposed-yellow?style=for-the-badge
[accepted]: https://img.shields.io/badge/Accepted-green?style=for-the-badge
[superceded]: https://img.shields.io/badge/Superceded-orange?style=for-the-badge
[rejected]: https://img.shields.io/badge/Rejected-red?style=for-the-badge
[deprecated]: https://img.shields.io/badge/Deprecated-grey?style=for-the-badge
