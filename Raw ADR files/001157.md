# 2. Add lerna to Monorepo

Date: 2024-08-13

## Status

Accepted

## Context

The current project structure consists of a monorepo that contains a frontend and a backend application at the time of writing, both using Node.js and Typescript. As the complexity and scale of the project is projected to grow over time, I face a challenge in managing dependecnies, building and deploying the project. I will need a solutioon to streamline the development process, ensure the consistency across projects and improve the ability to manage shared dependencies.

### Key Issues

1. **Dependency Management**: The current project structure does not provide a clear way to manage dependencies across the frontend and backend applications. This can lead to inconsistencies in the versions of shared dependencies and make it difficult to manage the dependencies effectively.
2. **Build and Run scripts**: There is no centralkized way to build and run the projects leading to potential duplication of scripts and risk of discrepancies in the build and run process.
3. **Project Interdependencies**: The frontend and backend applications are closely related and share some dependencies. Managing these interdependencies can be challenging without a clear structure in place.

## Decision

I will introduce Lerna to manage our monorepo. Lerna is a tool that optimizes the workflow around managing multi-package repositories by providing powerful features for linking, versioning, and publishing packages. It will help me address the key issues identified above by enabling me to:

Centralize Dependency Management: Lerna will allow me to manage shared dependencies more effectively by linking local packages and reducing duplication.
Streamline Build and Run Processes: I can use Lerna to execute scripts across all projects simultaneously, ensuring consistency in builds and reducing the overhead of maintaining multiple scripts.
Improve Project Organization: By using Lerna, I can better organize our projects within the monorepo, making it easier to manage interdependencies and scale the repository as needed

## Consequences

### Positive

1. **Simplified Dependency Management**: Lerna will help me manage dependencies more effectively, reducing the risk of version conflicts and inconsistencies.
2. **Consistent builds**: By centralizing build scripts, I can ensure that all projects are built consistently, reducing the risk of errors and discrepancies.
3. **Improved Scalability**: Lerna will provide a scalable structure for managing multiple projects within the monorepo, making it easier to add new projects in the future.
4. **Enhanced Collaboration**: Lerna will enable better collaboration between frontend and backend teams by providing a shared structure for managing projects.

### Negative

1. **Learning Curve**: Introducing Lerna may require some time to learn and adapt to the new workflow, which could slow down development initially.
2. **Configuration Overhead**: Setting up Lerna and configuring the monorepo structure may require additional effort upfront, which could delay immediate development tasks.
3. **Tool Maintenance**: Lerna will introduce a new tool into the development workflow, which may require additional maintenance and updates over time.

### Implementation Plan

1. **Install Lerna**: I will install Lerna to the root as a dev dependency and initialize it.
2. **Organize Projects**: I will reorganize the projects within the monorepo to align with Lerna's structure, moving shared code into separate packages where necessary.
3. **Configure Lerna**: I will configure Lerna to manage dependencies, build scripts, and other project-specific configurations.
4. **Update Scripts**: I will update the build and run scripts to use Lerna commands where applicable, ensuring consistency across projects.
