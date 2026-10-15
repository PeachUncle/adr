# Use AICON Server of DHBW Heidenheim as Hosting Infrastructure

**Date:** 2025-07-15

## Status

expired

## Context

For hosting our application, we require a reliable server infrastructure that supports Docker Compose and is accessible to our development team. Renting and maintaining a dedicated server would incur costs and administrative overhead. As students of DHBW Heidenheim, we have access to the AICON server, which is provided by the university for student projects.

The AICON server is available free of charge and is already equipped with the necessary resources and network configuration for our project. However, it is a shared resource, used by multiple student teams, which may lead to resource contention or configuration conflicts. Additionally, the server is only accessible from within the university network; external access requires a VPN connection.

## Decision

We will use the AICON server provided by DHBW Heidenheim as the hosting infrastructure for our project.

- The server is cost-free and maintained by the university IT department.
- It supports Docker and Docker Compose, meeting our technical requirements.
- The infrastructure is shared with other student projects, so we must be mindful of resource usage and potential conflicts.
- Access to the server is restricted to the university network; remote access from outside requires a VPN connection.

## Consequences

* **No Hosting Costs:** We avoid expenses and administrative effort associated with renting and maintaining a private server.
* **Shared Resources:** Resource contention or accidental interference with other student projects is possible. Coordination and communication with other teams may be necessary.
* **Limited Accessibility:** The server is only reachable from the university network or via VPN, which may complicate remote development and monitoring.
* **University IT Support:** The server is maintained by the university, reducing our operational burden but also limiting our control over hardware and base configuration.
* **Security & Privacy:** Data and services are hosted in a controlled, academic environment, but privacy and security depend on the shared nature of the infrastructure.

---

**Summary:**  
Using the AICON server is a pragmatic and cost-effective solution for our project, leveraging university resources while accepting the limitations of shared infrastructure and restricted access.