# 0007. Don't Use Testing Library Jest-DOM

## Date

2023-03-14

## Approved By

@danascheider

## Decision

We will not use `@testing-library/jest-dom`.

## Glossary

- **Document Object Model (DOM):** The data representation of objects, such as HTML elements, that appear on a web page, constructed by browsers in order to display the elements
- **DOM Testing:** Testing focussed on making expectations on DOM elements, such as checking whether an HTML element is visible on the page or has a particular attribute
- **Expectation:** An alternative to assertions in a testing context, invoked using the `expect` function
- **Matcher:** A function that can be used in test expectations to indicate what the expected behaviour is, for example, `.toBeTruthy()` or `.toHaveBeenCalled()`
- **Testing Library:** A library that can be used with a JavaScript testing framework, providing, among other things, a variety of matchers that can be used in expectations
- **Testing Library Jest-DOM:** A library meant to be used with [Jest](https://jestjs.io) that adds DOM-testing matchers to Testing Library's base set of matchers
- **Vitest:** A testing framework used with Vite, competing with [Jest](https://jestjs.io) and [Jasmine](https://jasmine.github.io), that is currently used for the SIM front end

## Context

We would like to have automated DOM testing for the SIM front end to reduce the need for extensive manual testing of every release. Unfortunately, there are no tools made to work with Vitest that add matchers or other utilities for DOM testing. Testing Library's main DOM-testing extension, [Testing Library Jest-DOM](https://testing-library.com/docs/ecosystem-jest-dom/), is made to work with competing test framework [Jest](https://jestjs.io).

## Considerations

There is prior art indicating it [is possible](https://markus.oberlehner.net/blog/using-testing-library-jest-dom-with-vitest/) to use Testing Library Jest-DOM with Vitest. However, using tools that aren't really meant to work together feels like a hack. It seems likely that, as Vitest and its ecosystem continue to develop, compatibility between the framework and Testing Library Jest-DOM will get shakier. There is a [competing library](https://github.com/chaance/vitest-dom), `vitest-dom`, that provides the same utilities (and, indeed, is a fork of Testing Library Jest-DOM) but tailored for Vitest. This will be a good option to consider in the future, but in the short term we have decided [not to use it](/docs/adrs/0005-wait-to-use-vitest-dom.md) on account of its immaturity and outdated peer dependency on a considerably older version of Vitest.

## Summary

As much as possible, we want to stick to using tools that are built to work well together. Testing Library Jest-DOM was not built with Vitest in mind, so we will wait for a DOM testing library that is more suited to Vitest.
