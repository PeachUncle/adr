---
title: "Storage Solution: Longhorn"
date: "2025-03-18"
---


| status: | date: | decision-makers: |
| --- | --- | --- |
| approved | 2025-03-18 | Sofus Albertsen |

## Context and Problem Statement

### Do i need it?

Even though Kubernetes (and their Container Storage Interface) is production ready for persistency and statefull workloads, keeping your cluster stateless have several advantages:

* Dead simple disaster recovery (and duplication) of your cluster: everything is defined as code, so (re)creating a cluster is as easy as running your setupscripts once more and wait for everything to come up.
* Backup and restore has never been simple, and Kubernetes is not solving this for you.

At it's core, we want stateless [cloud native applications](https://kodekloud.com/blog/cloud-native-principles-explained/).
Remember the distinction between the need for persistency and ephemeral storage; your chaching service needs ephemeral storage, but does not need backup/restore of said data. Those are perfectly fitting for Kubernetes.

Often time your Database is sitting on some special hardware, and is catered to by specialized competences.
Keep it that way, and connect to the database from your cluster.

### What are the criterias for choosing this?

* **Performance Requirements:** What are the expected Input/Output Operations Per Second (IOPS) that your applications will demand? What about throughput?
* **Scalability Needs:** Are you able to add storage seamlessly after the initial creation?
* **Data Availability and Durability:** What are you requrements to replica's, time to recover etc.
* **Team Expertise and Comfort Level:** What is your team's existing knowledge and experience with the specific storage solutions you are considering?

### What are our weights for making a choice?

While all criterias are important, choosing one persistency tool over the other can have vastly different requirements to the expertise of the team.

Therefore, the primary weight is; if you have a storage solution that already supports Kubernetes with a CSI driver, evaluate that one before anything else.

Secondary, it is the complexity introduced that we will focus on.

## Considered Options

* **Longhorn:**  A lightweight, reliable, and easy-to-use distributed block storage system for Kubernetes.  It's built by Rancher (now SUSE). Key features include built-in snapshots, backups, replication, and a user-friendly GUI.  It's designed specifically *for* Kubernetes and integrates deeply.

* **Rook Ceph:** Rook is a storage *operator* for Kubernetes, and Ceph is a highly scalable, distributed storage system offering object, block, and file storage.  Rook automates deployment, management, and scaling of Ceph within Kubernetes. This combination is powerful but complex.

* **OpenEBS:**  A containerized storage solution that provides persistent block storage for Kubernetes applications.  It offers several different "storage engines" (cStor, Jiva, Local PV, Mayastor), each with different performance and feature characteristics.  Offers flexibility but can require careful selection of the right engine.

* **Portworx:** A commercial (paid) storage platform designed for Kubernetes.  It offers high performance, high availability, and advanced features like data encryption, storage-level snapshots, and automated scaling.  It's a mature and feature-rich solution, but comes with licensing costs.

## Decision Outcome

Chosen option: **Longhorn**, because it provides a good balance of features, ease of use, and integration with Kubernetes, while minimizing the complexity overhead for our team.

It's a strong, open-source option that aligns well with our focus on simplicity.
It meets our needs for persistent storage within the cluster without introducing the operational overhead of a more complex solution like Rook/Ceph.

Based on different scenarios, the following general recommendations can be made:

* For organizations that require massive scalability, support for block, object, and file storage within a unified system, and have a team with the necessary expertise to manage a complex distributed storage platform, Ceph/Rook is a powerful option.
* For users who are looking for a straightforward and reliable distributed block storage solution that is easy to deploy and manage within Kubernetes, especially for smaller to medium-sized environments, Longhorn is an excellent choice.
* If you lack the required skillset all together, and need a high-performance, feature-rich, and commercially supported solution, and where the licensing costs are justified then Portworx is our recommendation.

### Consequences

* Good, because it's relatively easy to deploy and manage, leading to lower operational overhead and faster time to value. It has good community support and active development.
* Good, because Longhorn's performance is generally good for typical workloads, meeting our initial performance requirements.

* Bad, because Longhorn is primarily focused on block storage. If we need robust support for shared filesystems (ReadWriteMany access mode with full POSIX compliance) *within* the cluster, we might need to wait untill newer versions of the tools supports this (see their [roadmap for more information](https://github.com/longhorn/longhorn/wiki/Roadmap#longhorn-v111-january-2026))
* Bad, because, although Longhorn has a growing community, it's not as mature as Ceph. While this is less of a direct "consequence" and more of a relative comparison, it's worth keeping in mind for long-term planning.
