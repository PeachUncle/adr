# ADR-007: Repository Hosting

## Status

Accepted

## Context

The project requires a reliable hosting platform for the Git repository. As the
project currently has a single developer, the chosen platform should be simple
to set up and use, while also providing features that support future scalability
and potential team collaboration.

## Decision

We decided to use GitHub as the hosting platform for the project repository.

## Reasons

1. **Ease of Use**:
   GitHub provides a user-friendly interface and intuitive workflows, making it
   easy to manage repositories and perform tasks such as pull requests and issue
   tracking.

2. **Popularity and Community**:
   GitHub is the most widely used Git hosting platform, ensuring familiarity for
   future collaborators and access to extensive community support and
   documentation.

3. **Free Tier for Public and Private Repositories**:
   GitHub offers a robust free tier, which includes unlimited private
   repositories, making it a cost-effective solution for the project.

4. **Integration Ecosystem**:
   GitHub integrates seamlessly with a wide range of tools, including CI/CD
   services, project management tools, and IDEs, streamlining development
   workflows.

5. **Scalability for Team Collaboration**:
   While the project currently has one developer, GitHub’s features (e.g., pull
   requests, code reviews, and team management) will support collaboration if
   the team grows.

6. **Availability and Reliability**:
   GitHub’s globally distributed infrastructure ensures high availability and
   reliability, minimizing the risk of downtime.

## Consequences

1. GitHub requires creating an account and setting up SSH keys or personal
   access tokens for secure access, which introduces a minor initial
   configuration effort.

2. The project will rely on an external platform for repository hosting, meaning
   it is subject to GitHub’s terms of service and any potential service
   disruptions.

## Alternatives Considered

### GitLab:

- **Pros**: Strong CI/CD integration and robust free tier for private
  repositories.
- **Cons**: Slightly less user-friendly for newcomers and smaller
  community compared to GitHub.

### Bitbucket:

- **Pros**: Good integration with Atlassian tools (e.g., Jira).
- **Cons**: Free tier limits the number of users for private repositories.

### Self-hosted Git Server:

- **Pros**: Complete control over the repository and data.
- **Cons**: Requires significant setup and maintenance effort, overkill for a
  single-developer project.
