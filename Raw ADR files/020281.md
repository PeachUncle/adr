# Keep the Eligibility Screener and the Participant Recertification Portal separate

* Status: accepted
* Deciders: @rocketnova, @microwavenby, @aplybeah
* Date: 2022-01-06

Technical Story: https://wicmtdp.atlassian.net/browse/PRP-52

## Context and Problem Statement

Now that the [Eligibility Screener](https://github.com/navapbc/wic-mt-demo-project-eligibility-screener) is being re-written in Remix, the framework that we chose in [ADR-0005](0005-use-remix-for-project-architecture.md) to use for the Participant Recertification Portal,

## Decision Drivers

* Is there an easy way to keep the eligibility screener's dependencies up to date?
* Is there an easy way to port improvements made in PRP to the eligibility screener?
* Will it be easier or harder for WIC agencies to use or adopt these tools if they are combined into the same codebase?

## Considered Options

* Option 1 - Combine the eligibility screener and the recertification portal into the same codebase
* Option 2 - Keep the eligibility screener and the recertification portal as two separate codebases
* Option 3 - Keep the eligibility screener and the recertification portal as two codebases, but create a shared library for their components
* Option 4 - Create a "parent repo" that has both the Eligibility Screener and Recert Portal as git submodules. Manage dependencies collectively from the parent repo (keeping package.json in sync in both)

## Decision Outcome

Option 2 - Keep the eligibility screener and the recertification portal as two separate codebases

## Pros and Cons of the Options

### Option 1 - Combine the eligibility screener and the recertification portal into the same codebase

* Good, because it will be easy to keep the eligibility screener's dependencies up to date
* Good, because we can more easily create and manage shared React components
* Good, because we have fewer code repos to manage
* Bad, because it may be hard for an interested party to try out one tool without the code and documentation for the other
* Bad, because we might need to build a setup script / wizard to help someone navigate deployment options
* Bad, because pull requests that impact one tool may impact the other

### Option 2 - Keep the eligibility screener and the recertification portal as two separate codebases

* Good, because it will make deploying and using either tool less complicated for us and for any other state agencies
* Good, because we can make architectural decisions for the PRP without worrying about how it might impact the eligibility screener code
* Good, because they are actually distinct standalone tools with distinct use cases
* Good, because pull requests can be reviewed without considering the impact to the other tool
* Good, because we can always merge them later
* Bad, because it means over time the two codebases may diverge in foundational or underlying tooling (e.g. tests, linting, package management)
* Bad, because we maintain two separate stacks and terraform code, two separate CI pipelines and GitHub actions, etc

### Option 3 - Keep the eligibility screener and the recertification portal as two codebases, but create a shared library for their components

Same pros and cons as option 2 plus:

* Good, because shared react components can be pulled out into a separate reusable react component library
* Bad, because we need to manage a separate reusable react component library

### Option 4 - Create a "parent repo" that has both the Eligibility Screener and Recert Portal as git submodules. Manage dependencies collectively from the parent repo (keeping package.json in sync in both)

Same pros and cons as option 2 plus:

* Good, because dependencies are kept in sync between the eligibity screener and the recertification portal
* Bad, because git submodules are finicky, add an extra git step to keep the repo updated, and add friction for developer experience
* Bad, because dependencies are not visible within the individual eligibity screener and the recertification portal repos
