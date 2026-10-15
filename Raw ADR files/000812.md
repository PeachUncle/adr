# 003 - Architecture Selection

**Reporter:** Rafał Karaś

## Context

The decision revolves around selecting the architecture for the project. The optimal project structure is crucial for the efficient development and maintenance of the system.

## Considered Options

- **Option #1** - Use of a modular monolith.
- **Option #2** - Use of microservices.

## Decision

After thorough analysis of the available options and considering the specific needs of the team, the decision has been made to go with Option #1, which is the use of a modular monolith.

This decision is based on the following reasons:
1. **Team Collaboration:** It is easier for the team to collaborate when all the code is in one project. Accessibility and communication between modules are simpler.
2. **Simpler Management:** In the case of a single, cohesive project, managing code, builds, testing, and deployment is more transparent.
3. **Quick Start:** A monolithic project allows for a faster start and easier understanding for new team members.
4. **Shared Codebase:** Modules can more easily share code and libraries, facilitating the maintenance of a consistent style and standards.

Potential scalability issues will be monitored, and the project can be adjusted if necessary.

## Expected result

Adopting a modular monolith will enable effective team collaboration, faster development, and easier project management.

Impact on:
- **Organization:** It will enable a consistent project structure and easier team workflow organization.
- **Standardization:** It will safeguard the project from issues related to maintaining consistency in the code.
- **Concrete Solution:** It will provide a uniform codebase, facilitating the maintenance and development of the system.

Potential negative consequences:
- In the case of significant project growth, the need for a reevaluation of the architecture.

## Benefits for the Team

In the context of the team, using a modular monolith has additional benefits:
1. **Quick Communication:** Easier communication and collaboration among team members who have access to everything in one place.
2. **Easier Problem Diagnosis:** Consolidated code in one project makes it easier for the team to diagnose and resolve issues.
3. **Shared Solutions:** The team can more easily share ideas, solutions, and knowledge, speeding up project processes.

## Links

None
