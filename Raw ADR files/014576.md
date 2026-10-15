# ADR 002: Replace Traefik with ingress-nginx as API Gateway

**Status**: Accepted

**Date**: 2025-08-04

## Context

The initial architecture planned to use Traefik as the API Gateway and HashiCorp Consul for service discovery and service mesh. During the initial setup (Task 1.3), the `helm install consul` command failed repeatedly.

The root cause was a persistent conflict over the ownership of Kubernetes Gateway API Custom Resource Definitions (CRDs) like `gatewayclasses.gateway.networking.k8s.io`. The Traefik Helm chart installed these CRDs, and the Consul Helm chart also attempted to install or manage them, causing a validation error in Helm due to missing ownership labels.

Multiple attempts to resolve this failed, including:
* Disabling the Gateway API component in the Consul chart (`--set gatewayAPIs.enabled=false`).
* Skipping CRD installation in the Consul chart (`--skip-crds`).
* Manually adding the required Helm ownership labels to the existing CRDs.

The final error indicated a deep API version incompatibility between the CRDs as installed by Traefik and as expected by the Consul chart (`status.storedVersions[0]: Invalid value: "v1": missing from spec.versions`). This showed that the two charts, in their chosen versions, were fundamentally incompatible in their management of the Gateway API.

## Decision

We will **replace Traefik with `ingress-nginx`** as the project's API Gateway / Ingress Controller.

This architectural pivot is designed to completely eliminate the source of the conflict. `ingress-nginx` is the community-standard Ingress controller, is extremely stable, and does not use the conflicting Gateway API CRDs by default.

## Consequences

* **Positive**:
    * The installation of both `ingress-nginx` and Consul is now successful and conflict-free, allowing the project to proceed on a stable foundation.
    * The project's goal of using a dedicated Ingress Controller is still met.
    * The critical goal of using Consul for its service mesh capabilities in Milestone 3 is preserved.
    * Demonstrates proficiency with `ingress-nginx`, the most widely used Ingress controller in the Kubernetes ecosystem.

* **Negative**:
    * The project will use the standard Kubernetes `Ingress` resource for routing instead of the newer `Gateway` and `HTTPRoute` resources. This is a minor trade-off for a significantly more stable and compatible setup.