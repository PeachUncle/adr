# ADR-0002: Test, Provisioning, and Release Pipeline

## Status

Accepted

Date of decision: 2024-08-21

## Context and Problem Statement

Continuous integration and continuous delivery (CI/CD) is the practice of integrating code changes early and often,
running automated tests on the resulting code, provisioning infrastructure for a target environment, and releasing to
that environment. This provides rapid feedback to developers, leading to increased technical quality.

We expect to follow CI/CD practices (or a close derivative) in the development of the Private Rented Sector Database
(PRSDB). What tool will we use to run our CI/CD pipelines?

## Considered Options

* GitHub Actions
* Concourse
* Jenkins

## Decision Outcome

GitHub Actions, because it is a simple, managed service that is commonly used within MHCLG.

## Pros and Cons of the Options

### GitHub Actions

GitHub Actions is a CI/CD platform built into GitHub.
* Good, because it is integrated into GitHub, the code repository that PRSDB will use.
* Good, because it is used by several other MHCLG projects (including more modern codebases).
* Good, because it offers both managed runners (reducing operational burden for MHCLG) and the option to self-host
  runners (if that ever becomes necessary); it is also possible to use a mix of managed and self-hosted runners.
* Good, because it offers out-of-the-box integrations with AWS features (e.g. ECR/ECS, and OIDC security).

### Concourse

Concourse describes itself as “an open-source continuous thing-doer" - i.e. a generic CI/CD pipeline platform.
* Bad, because it is not widely used within MHCLG (although it is used by some older projects related to individual
  electoral registration).
* Bad, because it is not particularly widely used beyond MHCLG.
* Bad, because it does not offer any managed solution.
* Bad, because it offers limited out-of-the-box integrations with GitHub or AWS.

### Jenkins

Jenkins describes itself as “the leading open source automation server”. It been a popular choice in the domain for many
years (although, anecdotally, has been less popular in recent years).
* Bad, because it is not widely used within MHCLG.
* Good, because it is popular in the wider community.
* Bad, because it does not offer any managed solution.
* Neutral, because although it offers limited out-of-the-box integrations with GitHub and AWS, it is commonly enough
* used that examples and patterns should be available.

## More Information

* Review of the MHCLG technical landscape: [DLUHC Tech Landscape Review.docx](https://mhclg.sharepoint.com/:w:/s/PrivateRentedSector/EZp45cVALmBDl-MmTf5gd9cBajXyR87tPoGDom_OZFiMgg?e=GgSSh6) 