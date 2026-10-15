---
status: 'accepted'
date: 2024-07-01
decision-makers: voder.ai website team
---

# ADR 0003: Cache Playwright Browser Binaries in GitHub Actions

## Context and Problem Statement

Our CI workflow runs Playwright end-to-end tests on every push. Each run re-downloads Playwright’s browser binaries (~600 MB), adding 2–3 minutes and consuming significant network bandwidth.

## Decision Drivers

- Reduce CI runtime for Playwright setup
- Minimize external downloads and bandwidth usage
- Keep CI configuration simple and maintainable

## Considered Options

- Do nothing (always download on each run)
- Use a self-hosted runner with pre-installed browsers
- Cache Playwright browser binaries with GitHub Actions

## Decision Outcome

Chosen option: "Cache Playwright browser binaries with GitHub Actions", because it integrates seamlessly into our CI workflow, requires minimal maintenance, and significantly reduces test setup time.

### Consequences

- Good, because CI jobs restore browser binaries from cache when available, speeding up Playwright setup.
- Bad, because caches must be invalidated when the Playwright version (in package-lock.json) changes.
- Good, because network bandwidth usage and external downloads decrease.

### Confirmation

- Verify the "Cache Playwright browsers" step in CI reports a cache hit on subsequent runs.
- Observe that the Playwright install step skips downloading binaries on cache hits.
- Measure CI build times before and after implementation to confirm a 2–3 minute reduction.

## Pros and Cons of the Options

### Do nothing (always download)

- Good, because no change required.
- Bad, because CI is slower and uses unnecessary bandwidth.

### Use a self-hosted runner with pre-installed browsers

- Good, because browsers are always available.
- Bad, because it introduces maintenance overhead and potential costs.

### Cache Playwright browser binaries with GitHub Actions

- Good, because it leverages `actions/cache@v3`, integrates easily, and dramatically speeds up CI.
- Bad, because cached binaries need invalidation when versions update.

## More Information

- GitHub Actions cache docs: <https://docs.github.com/actions/using-workflows/caching-dependencies>
- Playwright installation guide: <https://playwright.dev/docs/installation>
