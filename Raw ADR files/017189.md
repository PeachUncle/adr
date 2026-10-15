# 0006. Wait to Use vitest-dom

## Date

2023-03-13

## Approved By

@danascheider

## Decision

We will use [MSW](https://mswjs.io/) instead of [vitest-fetch-mock](https://www.npmjs.com/package/vitest-fetch-mock) for our Vitest tests because of its much more robust API mocking capabilities. We will continue using `storybook-addon-mock` for Storybook despite its limitations.

## Glossary

- **Mock:** A function that emulates behaviour of a certain application or component for the purpose of testing a particular state
- **Mock Service Worker (MSW):** A [library](https://mswjs.io/) for mocking API calls in a Node environemnt
- **vitest-fetch-mock:** An [alternative](https://www.npmjs.com/package/vitest-fetch-mock) to MSW integrating more seamlessly with Vitest but offering more limited functionality
- **Vitest:** A testing framework used with Vite, competing with [Jest](https://jestjs.io) and [Jasmine](https://jasmine.github.io), that is currently used for the SIM front end

## Context

When we initially started our rewrite, we adopted the `vitest-fetch-mock` tool for mocking API calls. `vitest-fetch-mock` is lightweight and easy to integrate with Vitest, so it seemed like a good choice at the time. However, as time went on, we began to discover severe limitations. In particular, `vitest-fetch-mock` doesn't allow you to mock API calls based on request characteristics like URI or HTTP method. You can only set up handlers in the order the API calls are received (e.g., first external API call generates response A, second external API call generates response B, regardless of what the requests were). This can be problematic in an application where data is continually updated using hooks and contexts, which can make it difficult to predict which API calls will be made when - nor is there any particular benefit to the mental exercise of figuring this out under ordinary circumstances.

In the legacy front end, we used MSW for mocking API calls in both Jest and Storybook. The tool definitely gives us enough rope to hang ourselves: it enables extremely advanced use cases that can result in byzantine handlers and extensive mocking. That was part of the reason we started with `vitest-fetch-mock` on the rewrite: we hoped it would encourage us to stick to simpler use-cases. Unfortunately, the real result was that it prevented us from testing nuanced functionality.

## Considerations

The Vitest ecosystem is young and fast growing. It's likely that, in a few years, a tool like `vitest-fetch-mock` will have the functionality we need. However, until then, it makes more sense to use MSW since we've used it before, know it works, and have experience to avoid pitfalls with some of the more complicated use cases.

Although [`storybook-addon-mock`](https://storybook-addon-mock.vercel.app/?path=/story/docs-introduction--page) has similar limitations to those of `vitest-fetch-mock`, in its case it makes more sense because it keeps code quality reasonable and Storybook functionality realistic. Still, the fact that MSW could be used for Storybook in the future if necessary is also a good selling point for adding it to our toolset.

## Summary

Although it would be nice to utilise tools native to the Vitest ecosystem, it makes more sense to use the more mature, more fully featured MSW to mock API calls in our Vitest tests. The fact that we can potentially also use it for Storybook is another reason to adopt this tool.
