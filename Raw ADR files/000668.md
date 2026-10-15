# 008_package_update_frequency

## Context

Waiting too long with updating dependencies can lead to many errors in your code.

Updating too frequently can lead to too many PRs.

It is apparently possible to let a pipeline automatically update dependencies, create PRs for them, and even auto merge if tests pass.
See: https://snyk.io/blog/continuous-dependency-updates-improving-processes-front-loading-pain/
But I'm (MtP) not sure if it's a good idea to go that far with a 2 person team. I'm also not sure if someone is going to manually keep updating dependencies every month once this project is in production.

Beyond that, seems:

- updating to a new minor version usually is fine. Low chance of breaking code
- updating to a new major version has higher risk to break code

Opinions online vary wildly on best update frequency:

- Daily
- Weekly
- Every sprint
- Twice a year
- Once a year
- Never
- Only update when you have to, for example to fix a bug. But carries the risk on missing out on important security updates.
- Only update when you have time to deal with the potential errors that pop up. Most commonly chosen time is at the start of a new sprint or after a big release.
- Update more often if not doing so causes too many issues.
- Only update to stable versions, not experimental ones.
- If you update packages in a pipeline, you rely very much on your unit and integration testing to verify that there are no breaking changes.
- If you update manually, you run the risk of there being undocumented changes in the package(s).

I couldn't find a best update frequency. Opinions vary wildly. Wubbo prefers updating packages once a month (as we don't work in sprints), and that is good enough for me.

It's recommended to update the packages on a new branch, so that you don't end up with a master branch that doesn't work, when you are in production.

## Decision

Update packages once a month

## Status [Proposed, Accepted, Deprecated, Superseded]

Accepted

## Consequences

There might be bugs popping up due to an updated package. So it's probably best to make a new branch for this process.
