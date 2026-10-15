---
status: proposed
date: 2024-12-11
decision-makers: Michael Ogunrinde, James Bateman, Cory-Newman
---

# Local Development and Collaboration Strategy for AML System

## Context and Problem Statement

The AML system needs a reliable local development environment while enabling effective team collaboration. We need to determine the best approach for local hosting of our Next.js frontend and MySQL database, while ensuring smooth team collaboration through version control. The solution must support consistent development environments across team members while maintaining code quality and version control.

## Decision Drivers

* Must provide consistent development environment
* Need to ensure reliable database access
* Must support effective team collaboration
* Should enable code version control
* Must facilitate code review process
* Should support parallel development
* Must maintain code quality
* Should be easily maintainable

## Considered Options

### Version Control and Collaboration

* GitHub with branch strategy
* GitLab self-hosted
* BitBucket
* Local Git server
* Direct file sharing

### Development Environment

* Local development server with Git
* Docker with Git integration
* Virtual machine with shared repositories
* XAMPP/WAMP/MAMP with Git
* Cloud development environment

## Decision Outcome

Chosen approach: "Local development with GitHub collaboration", because:

1. Enables individual development environments
2. Provides robust version control
3. Facilitates team collaboration
4. Supports code review process
5. Maintains project history
6. Enables parallel development
7. Free for small teams

### Planned Implementation Approach

1. GitHub Setup:
   * Repository organisation
   * Branch strategy
   * Pull request workflow
   * Code review process
   * Issue tracking

2. Local Environment:
   * Development server setup
   * Database configuration
   * Environment variables
   * Git integration

3. Collaboration Workflow:
   * Feature branch workflow
   * Code review guidelines
   * Merge procedures
   * Conflict resolution
   * Documentation practices

### Consequences

* Good, because it enables team collaboration
* Good, because it maintains code version history
* Good, because it supports code review
* Bad, because it requires Git knowledge
* Bad, because it needs careful branch management

### Confirmation

We will validate this decision through:

1. Team workflow testing
2. Code review process validation
3. Conflict resolution testing
4. Documentation review
5. Team feedback collection

## Pros and Cons of the Options

### GitHub with Branch Strategy

* Good, because of robust collaboration features
* Good, because of familiar interface
* Good, because of integrated tools
* Bad, because of potential merge conflicts
* Bad, because of learning curve for Git

### Local Git Server

* Good, because of complete control
* Good, because of data privacy
* Bad, because of maintenance overhead
* Bad, because of setup complexity
* Bad, because of limited tools

### Direct File Sharing

* Good, because of simplicity
* Good, because of easy setup
* Bad, because of no version control
* Bad, because of conflict management
* Bad, because of no code review support

## More Information

Implementation requirements:

1. GitHub Setup:
   * Repository structure
   * Branch naming conventions
   * Commit message standards
   * Pull request templates
   * Issue templates

2. Development Guidelines:
   * Git workflow
   * Code review checklist
   * Conflict resolution procedures
   * Documentation requirements
   * Testing standards

3. Team Requirements:
   * Git training needs
   * Access management
   * Communication protocols
   * Review assignments
   * Merge permissions

4. Security Considerations:
   * Repository access control
   * Environment variable management
   * Sensitive data handling
   * Backup procedures

Next steps:

1. Set up GitHub repository
2. Document branch strategy
3. Create workflow guidelines
4. Train team on Git
5. Establish review process
