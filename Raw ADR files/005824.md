# GitHub Actions with Self-Hosted Runner for Automated Deployment Workflow

Date: 2025-07-22

## Status

Expired

## Context

Our application (comprising backend, frontend, database) is orchestrated using Docker Compose. To ensure an automated, reliable, and consistent deployment of the application to our local, internal university server whenever code changes are pushed to the main branch, we require a robust CI/CD process. Manual deployment steps are prone to errors and time-consuming.

We use GitHub as our primary platform for code development and version control. The team prefers an integrated CI/CD solution that offers direct control over the deployment environment and minimizes external dependencies, especially given the internal nature of the target server (the university server, as decided in [ADR 0003: Utilizing University Infrastruktur with Docker for Project Deployment]).

### Alternatives Considered
We considered several options for automating deployment:

* **Manual Deployment:** This approach is highly error-prone, inefficient, and inconsistent. It was rejected due to its high maintenance overhead and unreliability.
* **GitHub-hosted Runners with SSH/SCP:** This alternative would require complex SSH connections, secure key management, and file transfers from an external GitHub-hosted runner to the internal target server. This would significantly increase complexity compared to direct execution on the server and expand the attack surface. It was rejected.
* **Other CI/CD Tools (e.g., Jenkins, GitLab CI):** While capable, these tools would introduce an additional, separate system outside of our GitHub-centric workflow. This would increase overhead and complexity. They were rejected as GitHub Actions offers sufficient functionality for this use case and integrates well with our existing development environment.

## Decision

We will use GitHub Actions in conjunction with a self-hosted runner installed directly on the internal university server (the General Informatics server) to automatically deploy our Docker Compose setup.

The workflow will be triggered on every push to the main branch and on every pull request targeting main. It will include steps to check out the repository, gracefully stop and remove existing Docker Compose services, pull the latest Docker images, and start the services in detached mode (docker compose up -d --build).

## Consequences

* **Automated & Consistent Deployments:** This ensures reliable and repeatable deployments, significantly reducing manual effort and potential errors.

* **Direct Server Control:** The self-hosted runner provides direct access to Docker commands and the host's file system, enabling efficient and precise deployment actions without complex remote access layers. This is particularly advantageous for an internal server setup.

* **Adaptation to Internal Infrastructure:** This solution integrates seamlessly with the characteristics of an internal server, avoiding the need for external services to have direct access to our internal network.

* **Dependency on Server Health:** The deployment process directly depends on the availability and health of the self-hosted runner and the target server.

* **Permissions Management:** The runner user must have appropriate permissions for Docker operations and file system access. Resolving issues like "permission denied" (e.g., from root-owned Docker volume remnants) may require administrative intervention if sudo privileges are unavailable to the runner user.

* **Runner Maintenance:** The self-hosted runner software will need to be maintained and kept running (e.g., as a systemd service) on the target server.