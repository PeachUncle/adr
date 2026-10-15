# Branching Strategy

## Status

Accepted

## Context

The number of production and soon-to-be production projects contained with this monorepo is growing. At the time of writing, the TES National Explorer and TESAs are both being developed and pushed to production, without a concrete branching strategy.

TESAs are rolled out in stages, with the first stage being a beta application that should be available at a public link for stakeholders. The link for a TESA beta shouldn't be available on the production treeequityscore.org site until that TESA is released for production.

At the moment, the production TES application is deployed automatically from `main` and the staging app is deployed automatically from `tes/staging`. The TESA betas created thus far have been developed in `tes/staging` and released to staging via the `staging-tes-app` heroku application. This caused the `main` and `tes/staging` branches to diverge and cause some headaches when merging later.

We need a branching strategy that enables us to maintain unified code and release code to both production and staging environments.

## Decision

We will implement a [feature branch workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow).

All development will take place in a dedicated branch instead of the `main` branch.

Feature branches should have a clear, highly focused purpose and thus create an easily reviewable pull request (PR).

Feature branches should be branched off of the most recent version of `main`. If a feature branch requires code that is still under review in a PR and hasn't yet been merged into main, then that feature branch can be branched off of the one that contains the necessary context. It should be noted in the PR for the new feature branch that it was merged off another feature branch and that the older one should be reviewed and merged into `main` first. Then `main` should be merged back into the new feature branch to update it with the most recent changes.

Since we're working in a monorepo, changes that are specific to a single app should try to be isolated from changes that impact the entire monorepo in order to make reviewing PRs easier.

Feature branches should be named according to the following conventions:

- Feature branches should have a descriptive name (`help-widget`).
- If there is an issue associated with a feature branch, in most cases there should be, the issue number should be prefixed (`102-help-widget`).
- If the branch is associated with changes in a specific app in the monorepo, the app name should be prefixed followed by a forward slash (`tes-uk/102-help-widget`).
- If the branch is associated with repo-wide changes, the branch name should be prefixed by `monorepo` (`monorepo/update-setup-docs`).

All new code for all apps contained with in this monorepo should be pulled into `main` through a feature branch and subsequent PR.

A PR needs to be reviewed by at least one other developer before being merged into `main`. The only exception might be merging critical bug fix when other developers aren't around to review. Still, the author of the PR should notify the other developers that there is a critical PR that requires their review and confirm that they will be unable to review it within a reasonable time frame before merging the bug fix.

We will deploy new changes to the production and staging environments through Github releases.

## Consequences

Feature branching will help keep the monorepo and the projects it supports maintainable both in the short and long term. It should help reduce the number of bugs that make their way to the production application. However, it may also mean that implementing features takes slightly longer, especially because we want to strictly enforce code reviews.

This branching strategy will likely necessitate semantic versioning of the repository since we will be using releases to deploy code to production and staging environments. That will be discussed in a future architecture decision record (ADR).
