# ADR 002 – Handling Cloud Image Updates in Proxmox VM Bootstrap

**Status:** Accepted

**Date:** 2025-02-01

## Context

In this setup, Terraform provisions VMs in Proxmox using a downloaded **Ubuntu cloud image** attached as the primary disk (`scsi0`).

When the upstream Ubuntu cloud image is updated, Terraform detects a change in the image’s `file_id`. By default, this would trigger a **recreation of all dependent VMs**.

In a homelab setup, VMs are currently treated as **“pets”** rather than disposable **“cattle”**, because this environment is a PoC learning space. The focus is on experimenting with Terraform, Kubernetes (K3s), and automation workflows, not on building full production-grade pipelines.

Unnecessary VM recreation would cause:

* Downtime
* Potential data/state loss
* Disruption to Kubernetes clusters (e.g. having to reinstall K3s and rejoin nodes)
* Loss of manual configurations made during experiments

## Options Considered

### Option 1 – Ignore `disk[0].file_id` changes in Terraform (current approach)

* **Pros:**

    * Prevents unnecessary VM recreation when cloud image updates.
    * Keeps homelab VMs stable while experimenting.
    * Simple, low-effort approach.
* **Cons:**

    * VMs will **not automatically receive base image updates**.
    * Requires a separate **patching policy** (manual or automated within the VM).

---

### Option 2 – Implement an automated rebuild pipeline for VMs

* **Pros:**

    * Aligns with production best practices (treating VMs as “cattle, not pets”).
    * Ensures VMs are always provisioned from the latest cloud image.
* **Cons:**

    * High complexity — would require automation for:

        * K3s installation
        * Rejoining cluster nodes
        * Handling rolling upgrades safely
        * Reapplying any additional config/state
    * Significant upfront investment in automation.
    * Detracts from homelab’s primary goal as a **learning and PoC environment**.

---

### Option 3 – Hybrid approach

* **Pros:**

    * Allow Terraform recreation only in controlled scenarios (e.g. major upgrades).
    * Combine with lightweight patching inside existing VMs.
    * Balances learning between immutable infrastructure and pet-like stateful VMs.
* **Cons:**

    * Still requires manual decision-making and discipline.
    * Complexity sits between options 1 and 2.

---

## Decision

For now, adopt **Option 1**:
Configure Terraform to **ignore changes to `disk[0].file_id`** in VM resources.

This avoids disruptive and unnecessary VM recreation while maintaining a stable learning environment.

---

## Consequences

* VMs will **not auto-upgrade base images** → must rely on in-VM patching.
* A **patching policy** (manual or automated) will be introduced to ensure VMs remain updated.
* Future improvement: an **automated rebuild + K3s rejoin pipeline** may be added when the homelab evolves to explore production-grade patterns.
