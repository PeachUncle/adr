---
title: "Network Plugin: Cilium"
---

| status: | date: | decision-makers: |
| --- | --- | --- |
| proposed | 2025-02-18 | Alexandra Aldershaab, Steffen Petersen |

## Context and Problem Statement

A CNI plugin is required to implement the Kubernetes network model by assigning IP addresses from preallocated CIDR ranges to pods and nodes. The CNI plugin is also responsible for enforcing network policies that control how traffic flows between namespaces as well as between the cluster and the internet.

## Considered Options

* Flannel
* Cilium
* Calico

## Decision Outcome

Chosen option: **Cilium**, because it is a fully conformant CNI plugin that works in both cloud and on-premises environments while also providing support for network policies as well as more advanced networking features. Cilium has also gained rapid adoption in the Kubernetes community and is considered the future standard of CNI plugins.

Flannel was considered, but it does not support network policies which is considered a hard requirement.

Calico, while supporting Network policies, falls short compared to Cilium in terms of advanced networking features.

### Consequences

* Good, because Cilium provides support for network policies on L7 as well as the usual L3/L4.
* Good, because Cilium provides support for BGP controlplane integration, allowing for seamless integration with existing networking infrastructure.
* Good, because Cilium provides a feature called Egress Gateway which allows for traffic exiting the cluster to be routed through specific nodes, facilitating smooth integration with existing security infrastructure such as IP-based firewalls.
* Good, because Cilium comes with a utility called Hubble which provides deep observability into the network traffic, allowing for easy debugging and troubleshooting of network issues.

* Bad, because Cilium requires you to understand both Kubernetes networking and tradition networking concepts to fully utilize its advanced features.
* Bad, because Cilium does not come installed by default on any flavor of Kubernetes, requiring additional steps to install it and provide necessary custom configuration.
