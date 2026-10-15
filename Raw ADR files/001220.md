# Adoption of Gradle as Build System

- Status: Accepted
- Deciders: Daniel
- Date: 2023-06-11
- Technical Story: Project Setup

## Context and Problem Statement

The build system is an important component of any software project. It helps automate and manage the project's dependencies, compilation process, packaging, and deployment. The
question is: "Which build system should be used for our Kotlin project?"

## Considered Options:

- Gradle
- Maven

## Decision Drivers:

- **Suitability for Kotlin**: Compatibility and support for Kotlin-based projects.
- **Learning Curve**: Ease of learning and adapting for the team.
- **Build Performance**: Speed and efficiency of building the project.
- **Dependency Management**: Capability of efficient dependency management.
- **Community Support**: Availability of robust community support.

## Decision Outcome:

Chosen option: "Gradle", due to its compatibility with Kotlin, familiarity within the team, efficient handling of project dependencies, and the presence of a strong community
support. Specifically:

- Gradle supports Kotlin DSL which provides a type-safe way to configure builds which results in better tooling support.
- The team is familiar with Gradle build system leading to lower learning curve.
- Gradle’s incrementality feature helps in faster builds.
- Excellent dependency management capabilities (transitive dependency management, conflict resolution, and caching).
- Active and vast community support means more resources and quick resolutions to potential issues.

## Consequences:

Assuming that Gradle will be adopted as the primary build system, there will be consequences to anticipate:

**Positive Consequences**

- Speedy and efficient building of project due to Gradle's streaming and incrementality feature.
- More readable and maintainable build scripts due to Gradle's domain-specific language (DSL) based on Kotlin.
- Mature dependency management system.

**Negative Consequences**

- Gradle's build scripts can become complex and unwieldy for large builds.
- Need for potential upskilling or training for team members not familiar with Gradle.
