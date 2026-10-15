# 001: IaC Language and Tooling Selection

- **Status:** Accepted
- **Date:** 2025-07-01

## Context and Problem Statement

The AgentForge project requires a robust, scalable, and maintainable Infrastructure as Code (IaC) solution using the AWS CDK. The chosen language must provide strong type safety to minimize configuration errors, be expressive enough to model complex systems, and have a mature ecosystem to reduce development friction. We need to select a primary language that offers the lowest total cost of ownership and the fewest development headaches over the project's lifetime.

## Considered Options

1.  **TypeScript:** The "native" language of the CDK with the largest ecosystem. However, its structural typing can be overly flexible, requiring external libraries like Zod for strict data validation.
2.  **Python:** Highly expressive and popular, with first-class CDK and AWS SDK support. Its dynamic typing necessitates an external library like Pydantic for runtime data validation and type safety.
3.  **F#:** Possesses a superior type system (Algebraic Data Types, Discriminated Unions) that is theoretically perfect for modeling infrastructure. However, it has the smallest CDK community, leading to high risk from lack of examples and support.
4.  **Architectural Diagramming (C4 Model with Mermaid):** A language-agnostic approach to define the system architecture before implementation. This decouples the high-level design from the specific implementation language.

## Decision

We have decided to adopt a hybrid approach:

1.  **Primary Language: Python.** We will use Python for all AWS CDK development.
2.  **Data Validation: Pydantic.** We will integrate Pydantic for defining and validating all data structures and contracts between system components (e.g., Lambda event bodies, API payloads). We view Pydantic not as an add-on, but as a standard part of our Python stack for this project.
3.  **Architectural Specification: C4 Model with Mermaid.** Before implementing any new major component, we will create or update a C4 diagram in a Markdown file. This will serve as the language-independent source of truth for the system's architecture.

## Rationale

This decision provides the best balance of competing concerns:

- **Developer Velocity & Support:** Python has a mature, first-class ecosystem for CDK and general AWS development, minimizing friction from tooling and lack of documentation.
- **Type Safety & Correctness:** Pydantic provides robust, runtime-enforced type safety exactly where it's needed most—at the boundaries between components. This addresses the primary weakness of using a dynamically typed language for IaC.
- **Architectural Rigor:** The mandatory use of C4 diagrams ensures that we maintain a clear, high-level vision of the system, preventing architectural drift and facilitating communication.
- **Long-Term Maintainability:** This stack is common, well-understood, and avoids locking us into a niche ecosystem (like F# for CDK), which would pose a long-term risk.

By combining these three elements, we achieve a development process that is architecturally sound, implementation-safe, and highly productive.
