# 0005. Wait to Use vitest-dom

## Date

2023-03-11

## Approved By

@danascheider

## Decision

We will wait to adopt the [vitest-dom](https://github.com/chaance/vitest-dom) package, even though doing so prevents automated DOM testing.

## Glossary

- **Document Object Model (DOM):** The data representation of objects, such as HTML elements, that appear on a web page, constructed by browsers in order to display the elements
- **DOM Testing:** Testing focussed on making expectations on DOM elements, such as checking whether an HTML element is visible on the page or has a particular attribute
- **Expectation:** An alternative to assertions in a testing context, invoked using the `expect` function
- **Matcher:** A function that can be used in test expectations to indicate what the expected behaviour is, for example, `.toBeTruthy()` or `.toHaveBeenCalled()`
- **Testing Library:** A library that can be used with a JavaScript testing framework, providing, among other things, a variety of matchers that can be used in expectations
- **Vitest:** A testing framework used with Vite, competing with [Jest](https://jestjs.io) and [Jasmine](https://jasmine.github.io), that is currently used for the SIM front end

## Context

When we started using Vite, due to a lack of familiarity with tooling, we made the implicit decision to use Vitest with React Testing Library for automated testing. Unfortunately, it turns out Vitest is a limited and immature tool that has no built-in DOM testing capabilities. This means we can't test, on an automated basis or in CI, whether elements are visible to users, which CSS properties are set on them, which attributes are set on HTML elements, and more.

We have recently become aware of a package, [vitest-dom](https://github.com/chaance/vitest-dom), that would introduce certain matchers for DOM testing into Testing Library for Vitest. This package is a fork of `@testing-library/js-dom`, which integrates well with Jest but not with Vitest. This package is currently on version 0.0.4, with the most recent commit to `main` in June of 2022.

## Considerations

Vitest is a very young tool, with the latest version at this writing being 0.29.2. As such, any ecosystem tools catering to it specifically, will also be quite immature. However, 0.0.4 is a very early version that comes with considerable risk of the package not being maintained or documented. The project only has 20 commits on `main`, the only branch, with the most recent being 8 months ago. It appears that the package was forked last year and modified to work with Vitest at that point. This commit history is much to recent for us to consider depending on at this time.

It is worth noting that `vitest-dom`'s sole maintainer [has confirmed](https://github.com/chaance/vitest-dom/issues/1#issuecomment-1437611057) three weeks ago that they are still maintaining the package despite the lack of recent commit history.

Another issue is that `vitest-dom`'s peer dependency on Vitest is on version `"^0.16.0"` - i.e., any versions greater than or equal to 0.16.0 but less than 0.17. This is so many minor versions behind Vitest's current version that it is questionable whether it would even work with the Vitest version we are using. There is currently an [open issue](https://github.com/chaance/vitest-dom/issues/2) about bumping the peer dependency.

## Summary

Although `vitest-dom` is a promising tool that would significantly bolster our capability to perform automated DOM testing in CI, the package is currently too immature to be considered reliable and its peer dependency requirement doesn't match the version of Vitest we are using. For this reason, we will hold off on adopting the package, but will watch the repo and see how future activity plays out.
