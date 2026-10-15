# ADR 01: Continuous Integration and Continuous Delivery

[<- Back](../README.md)

## Context

We want to ensure the quality of our software with each commit, and we need to
be able to release new versions of software quickly and reliably.

## Decision

We will use continuous integration and continuous delivery (CI/CD).

Continuous Integration (CI) is a key practice in modern software development
where code changes are integrated into a shared code base as soon as they are
complete, which aids in swift and efficient deployment. It revolves around
isolating and testing new code in the local development environment before
performing final tests and moving the code to the staging environment
Historically, software engineers would compile and build code manually,
bundling multiple changes before deploying to production. This approach,
however, proved time-consuming and less efficient. With the advent of DevOps,
it's now recognized that continuous, incremental integration, testing, and
deployment of changes are more efficient, reliable, and speed up the overall
software build process. The practice of CI has been facilitated by the use of
automated tools, which enable engineers to incorporate new code changes
continuously into the production code base.

Continuous Delivery (CD) is a software development practice that automates the
delivery of code changes, enabling them to be released to production without
human intervention. CD naturally complements Continuous Integration (CI), an
approach where code changes are automatically built and tested upon being
committed to the source code. The CI/CD pipeline collectively enhances the
quality of code, diminishes deployment risks, and expedites the development
process by ensuring that every change made to the software is production-ready,
thoroughly tested, and deployable at any time, thus fostering a streamlined and
efficient software delivery lifecycle.

The sub-decisions associated with this ADR include:

- Our developer platform is GitHub.
- CI/CD pipelines via GitHub Actions.
- Development workflow based on GitFlow.

## Consequences

- We will have early detection of integration bugs.
- Releases will be less risky and easier to do.
- Need to invest time in setting up and maintaining CI/CD pipelines.

## References

- [GitHub Actions](https://github.com/features/actions)
- [GitHub Flow](https://docs.github.com/en/get-started/quickstart/github-flow)
- [GitHub CICD](https://resources.github.com/ci-cd)
