# ADR-002: Source Control System

## Status

Accepted

## Context

The project requires a version control system to manage source code effectively.
The chosen system should support scalability for future needs while being
efficient and reliable for individual use.

## Decision

We decided to use Git as the source control system for this project.

## Reasons

1. **Distributed Version Control**:
   Git’s distributed nature ensures the repository can be cloned and backed up
   easily, reducing dependency on a single system.

2. **Future Scalability**:
   Git is well-suited for potential future team expansion, offering features
   like branching and merging that can support collaborative workflows.

3. **Industry Standard**:
   Git is the most widely used version control system, ensuring compatibility
   with a variety of tools and services, which can streamline future
   integrations and transitions.

4. **Performance**:
   Git handles small and large projects efficiently, making it an ideal choice
   for a wide range of use cases.

5. **Ecosystem and Tooling**:
   Git has an extensive ecosystem with integrations for hosting platforms (e.g.,
   GitHub, GitLab, Bitbucket) and development tools, which can simplify
   repository management.

## Consequences

1. Initial setup and familiarization with Git workflows may take time for a new
   user, but this is a one-time effort with long-term benefits.

2. The choice of Git may require using or setting up a hosting service (e.g.,
   GitHub or GitLab), which could introduce minor additional steps for
   repository management.

## Alternatives Considered

### Subversion (SVN):

- **Pros**: Centralized system, simpler to understand for newcomers.
- **Cons**: Less flexible and future-proof compared to Git.

### Mercurial:

- **Pros**: Similar to Git in terms of functionality.
- **Cons**: Smaller ecosystem and less adoption, which could limit future
  options.

### Perforce:

- **Pros**: Strong for managing large files and enterprise-scale projects.
- **Cons**: Overkill for a single developer and more complex to set up.
