# 5. Support of most recent action images (inc Python v2)

Date: 2024-06-07

## Status

Accepted

## Context

We want to provide a Codespaces environment that's intuitive for researchers to understand and that provides a "habitable" environment for them in which to write code. We also want to keep the maintenance burden for developers low.

We would also like to encourage researchers to use the newest action images available, so that they are using the latest language features and libraries, and taking advantage of any other improvements (such as performance enhancements) that may be available. We believe that providing a development environment that supports that aim will help with this.

Note: support of action images only refers to the files we pull in from those images to provide syntax highlighting, help pages/documentation, and autocomplete. It does not affect the use of the `opensafely run` or `opensafely exec` where all versions of action images will be available as they are locally.

## Decision

We will provide a development environment for the most recent version of the Python Action image, which is V2.

We will not provide a development environment for V1 of the Python Action image.

More generally, we will aim to support the most recent versions of action images only. We will not provide support for multiple versions of an action image.

## Consequences

We did a soft rollout of the Python v2 action image earlier this year. At present only one or two researchers are using it, although we expect that number to increase over time. So it's possible that we're making a decision that means the Codespaces experience won't be as good for some older projects. However, we believe those numbers are very low and that the impact of not supporting Python v1 is also low. We already recommend that users run their code regularly using `opensafely run` or `opensafely exec` and those commands do still support Python v1.

In future, researchers using older action images could edit their dev container config to point to a version of the Docker image that uses the older action images. To do this, they would [change the tag, or hash, of the image name](https://github.com/opensafely/research-template/blob/5bd648f567b52c46a82979dc072d7355b22b2fff/.devcontainer/devcontainer.json#L5) to point to an older version. In this example they would alter the `v0` tag:

```
"image": "ghcr.io/opensafely-core/research-template:v0",
```

However, we could potentially make other changes that means this doesn't work as expected. Over time, we may find that the Codespaces environment doesn't meet the needs of developers of older research projects. We intend to monitor the usage of Codespaces to pick up if researchers are using it on older projects. If it becomes a problem, we could change our approach.
