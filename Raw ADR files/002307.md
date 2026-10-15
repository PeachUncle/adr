# ADR 0001: Repository Structure (Monorepo)

- Status: Accepted
- Date: 2025-12-08
- Title: Repository Structure (Monorepo)
- Context: Interview & Job Copilot

———

## Context

The platform comprises multiple Spring Boot microservices, a Next.js frontend, an nginx API gateway, shared JWT/auth libraries, and Docker
Compose-based local infrastructure. A single developer maintains the codebase and needs fast, synchronized changes across services, consistent
tooling, and straightforward dependency/version management. A decision is required between a single monorepo and multiple per-service
repositories.

## Decision

Adopt a monorepo with a single Gradle wrapper at the root, one Gradle project per backend service, colocated frontend and gateway configs,
shared libraries under libs/, and local infra under infra/. All services own their data and remain independently buildable and deployable.

———

## Status

Accepted.

## Alternatives Considered

- Monorepo (chosen): One repo for backend services, frontend, gateway, shared libs, and infra; single build orchestration via Gradle.
- Polyrepo: Separate repos per service/frontend/gateway/lib with independent pipelines.

## Rationale

- Single developer benefits from atomic, cross-cutting changes (API + client + gateway) without multi-repo coordination.
- Shared tooling (Gradle wrapper, linting, testing) stays consistent and versioned together.
- Simplifies dependency updates and interface evolution (e.g., DTOs, shared auth libs).
- Easier local orchestration and onboarding: one clone, one set of scripts.
- Reduces CI/CD duplication across services.

## Consequences

- Positive: Faster iteration for cross-service changes; unified conventions; simpler local dev with Docker Compose; reduced CI complexity.
- Negative: Larger repository size over time; requires discipline to avoid unintended coupling; CI runs may need selective builds to keep
  feedback fast.
- Mitigations: Keep services owning their data and APIs; use per-project Gradle tasks and selective CI triggers; enforce boundaries via gateway
  contracts and shared lib versioning.

———

## Notes on Implementation

- Root Gradle wrapper orchestrates all service builds; each service remains independently deployable.
- Gateway decouples clients from service topology; shared libs limited to cross-cutting concerns (auth/JWT).
- LLM usage remains optional and isolated; core flows stay rule/template-driven.
