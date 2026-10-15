# Migration to Own Server Infrastructure Instead of AICON Server

**Date:** 2025-07-23

## Status

Accepted

## Context

Previously, we decided to use the AICON server provided by DHBW Heidenheim as our hosting infrastructure (see ADR-5). While this solution offered cost savings and university IT support, several limitations have impacted our development and operational efficiency:

- **Limited External Access:** The AICON server is only accessible from within the university network or via VPN, complicating remote development, monitoring, and collaboration.
- **Restricted Configuration:** We have limited control over server configuration, which hinders optimization, troubleshooting, and the ability to install or update required software.
- **Resource Constraints:** The server resources are shared among multiple student projects, leading to potential performance issues and resource contention.
- **Reliability Issues:** The shared nature and limited oversight have resulted in increased error rates and downtime, affecting the stability of our application.

## Decision

We will migrate our project from the AICON server to our own dedicated server infrastructure.

- The new infrastructure will be fully under our control, allowing unrestricted configuration and optimization.
- We will ensure reliable external access for all team members, regardless of location.
- Dedicated resources will improve performance and scalability.
- We will be able to implement robust monitoring, backup, and security measures tailored to our needs.

## Consequences

* **Increased Costs:** We will incur expenses for server rental, maintenance, and administration.
* **Full Control:** We gain complete control over hardware, software, and network configuration.
* **Improved Accessibility:** Team members can access the infrastructure from anywhere without VPN restrictions.
* **Enhanced Reliability:** Dedicated resources and oversight will reduce downtime and error rates.
* **Operational Responsibility:** We are responsible for server maintenance, updates, and security.

---

**Summary:**  
Migrating to our own server infrastructure addresses the limitations of the AICON server, providing greater flexibility, reliability, and accessibility for our project, at the cost of increased operational responsibility and expenses.