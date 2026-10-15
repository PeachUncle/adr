# 2. Custom dev container image

Date: 2024-06-04

## Status

Accepted

## Context

We originally had a single dev container environment with a generic Docker image. We want to build on this to provide a more "habitable" environment for researchers in which to write code. This includes providing R and RStudio, as the majority of researchers using OpenSAFELY write R code.

## Decision

We will use a custom Docker image, defined and managed in the research-template-docker repo and specified within the research-template [dev container configuration](https://github.com/opensafely/research-template/blob/main/.devcontainer/devcontainer.json), to provide a customised development environment for researchers to use within Codespaces. We will use this to provide the same versions of Python and R as used in the action images and to provide RStudio.

We will use rocker/rstudio:4.0.5 as the base image, at least initially.

## Consequences

We chose to base this custom Docker image on the rocker/rstudio:4.0.5 image, as this would provide us with the same version of R as the action image and provide RStudio in a way that works with dev containers "out of the box". Rocker is well-known and well-maintained within the community, and it provides us with a potential upgrade path for the future.

As we're using an older version of R to be compatible with the R action image, installing it on recent operating systems is tricky, so it was felt that using an "official" image would be easier. If a newer version of the R action image becomes available and uses a more up to date version of R it may make sense to explore using a new base image.

There is a small risk that Rocker might remove their Docker image and we would then need to recreate it in order to release new versions of the dev container image. The Rocker Dockerfile isn't publicly available which makes this slightly harder.

Maintaining a custom dev container Docker image will create some additional work for the tech teams and we intend to look for ways to minimise that burden. In particular, we will need to consider how we'll respond to updates to the action images. We expect to receive support requests and bug reports from researchers about the environment we provide. We'll also need to consider how we rollout updates to the environment to researchers. However, we believe that the benefits to researchers will be worth the small amount of extra work we expect from the tech teams as a result of this change.

