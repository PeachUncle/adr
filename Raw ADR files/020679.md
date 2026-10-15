# ADR 0009: UUID-Based Deployment and Image Tagging Strategy

## Status

**Accepted**

## Context

We operate a `Development → Staging → Production` promotion model:

1. **Staging** automatically tracks the latest changes from the `main` branch.
2. **Production** is updated only through explicitly versioned releases (`v*` tags).

Earlier attempts to trigger Coolify deployments using both `uuid` and `tag` parameters in webhook URLs were unsuccessful due to API constraints—Coolify does not support combining these parameters. As a result, we require a deployment mechanism that is reliable, API-compliant, and still supports multiple Docker image tags (`main`, `staging`, `prod`, `latest`) to enable safe rollbacks and controlled promotions.

## Decision

### 1. Deployment Triggers (Service UUID Only)

All deployments will be triggered exclusively via the **Coolify Service UUID**.

* The CI pipeline builds and pushes Docker images.
* Upon completion, it sends a webhook request to Coolify using `?uuid=<service-uuid>` only.
* Coolify pulls the Docker image tag configured in the service settings; no tag is specified in the webhook.

This approach ensures deterministic and API-compliant deployments.

### 2. Docker Image Tagging Strategy

The CI pipeline (using `docker/metadata-action`) maintains both mutable and immutable tags to support promotion and rollback workflows.

**On push to `main` (Staging):**

* `:staging` — mutable pointer used by the Staging environment
* `:main` — branch-aligned tag for traceability
* `:sha-<commit>` — immutable tag for precise version reference

**On push of `v*` tags (Production):**

* `:prod` — mutable pointer used by the Production environment
* `:latest` — convenience alias for the current production release
* `:vX.Y.Z` — immutable, versioned release tag

### 3. Coolify Service Configuration

Environment-to-tag mapping is handled entirely within Coolify:

* **Staging services** pull
  `ghcr.io/zouari-org/zouari-rs-backend:staging`
* **Production services** pull
  `ghcr.io/zouari-org/zouari-rs-backend:prod`

Changing the deployed version is achieved by updating the configured image tag in Coolify, not by altering webhook parameters.

## Consequences

* **Predictable Deployments:**
  Staging consistently reflects the latest state of `main`, while Production tracks the current `prod` release.
* **Operational Rollbacks:**
  In case of a faulty release, Production can be rolled back by reconfiguring Coolify to pull a prior immutable tag (e.g., `:v1.2.2`).
* **API Compliance and Stability:**
  Eliminating the `tag` parameter from deployment webhooks prevents `400 Bad Request` errors and aligns with Coolify’s supported API behavior.
