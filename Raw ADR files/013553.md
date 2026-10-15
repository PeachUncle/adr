# 1. Build Container Images Using Buildpacks

## Status
Accepted

## Context
Writing Docker files by hand is cumbersome and inefficient. There are better ways.

## Decision
We will use  [Buildpacks](https://buildpacks.io/) to assemble container images for the services to be deployed to Kubernetes.

## Consequences
No more debugging Dockerfiles or large images. Cloud Native Buildpacks does much of the heavy lifting, generating optimized images that can be used with any container runtime.