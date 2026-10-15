# ADR 03: Infrastructure-as-Code with Policy-as-Code

[<- Back](../README.md)

## Context

We want to automate our infrastructure setup and enforce policies across the
entire stack.

## Decision

We will manage infrastructure and policy using code.

Infrastructure-as-Code (IaC) is a key DevOps practice that involves the use of
scripts or code to automate the provisioning and management of IT
infrastructure. This includes physical devices, virtual machines, networks, and
other resources. The code is treated in the same way as application code: it's
stored in version control repositories, tested, and deployed through continuous
integration/continuous delivery (CI/CD) pipelines. Tools such as Terraform,
Ansible, Chef, Puppet, and Kubernetes are commonly used in implementing IaC.
This approach helps achieve consistency across different environments, reduces
the potential for human error, and speeds up deployment processes, since the
infrastructure can be created and managed programmatically. Furthermore, it
promotes transparency and auditability since the configuration and changes to
the infrastructure are trackable in the codebase. It also fits perfectly within
the paradigm of the cloud computing era, where services and resources can be
rapidly provisioned and decommissioned in response to changing business needs.

Policy-as-Code (PaC) is an approach to defining and managing organizational
rules and standards in software development through codified policies. It's an
extension of the Infrastructure-as-Code concept and is a part of the broader
DevOps and DevSecOps practices. PaC entails encoding policies related to
security, compliance, operational best practices, or any other rules into a
format that can be version-controlled, audited, and applied automatically.
Tools like Open Policy Agent, HashiCorp's Sentinel, and Chef InSpec are
commonly used for implementing PaC. It aims to automate the enforcement of
these policies in the software development lifecycle, reducing manual review
processes and promoting consistency and compliance with regulations. By using
PaC, companies can continuously and automatically verify that their practices
align with their defined policies at all stages of the CI/CD pipeline, thus
enabling proactive detection and mitigation of risks, reducing the time spent
on remediation, and improving overall system compliance and security.

The sub-decisions associated with this ADR include:

- We will use Terraform for our infrastructure-as-code.
- We will use Open Policy Agent (OPA) for our policy-as-code.

## Consequences

- Changes to the infrastructure will be easier to manage and track.
- Policies can be applied uniformly and automatically.
- Learning curve for developers unfamiliar with infrastructure and policy as code concepts.
