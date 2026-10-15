# ADR-PY-002: Define Project Folder Structure

## Status

Accepted

## Context

This project adopts the ["Ports and Adapters" architecture pattern](../../common/docs/adrs/adr-002-apply-ports-and-adapters-architecture-pattern), which calls for strict separation of concerns between application core, interfaces, and infrastructure-specific components.

It also follows the [mono-repository strategy](./adr-py-001-use-mono-repository.md), which centralizes all components, adapters, and configurations in a single repository for easier management and testing. Within such a structure, a clear and consistent folder layout is essential to:

- Enforce architectural boundaries across layers.
- Support modular development and substitution of adapters.
- Maintain infrastructure-agnostic workflow implementations.
- Organize acceptance tests based on the [shared specifications subtree](../../common/docs/README.md).
- Enable consistent documentation and automation practices.

This structure must also align with Pythonic conventions while remaining faithful to the goals of modularity and separation expressed in previous decisions—namely, [ADR-PY-000: Use Python as Implementation Language](./adr-py-000-use-python-as-implementation-language.md) and [ADR-PY-001: Use Mono-Repository](./adr-py-001-use-mono-repository.md).

## Decision

The Python implementation of the BlueZone project will use the following top-level folder structure:

bz-taew-py/
├── adapters/
│   ├── aws/ - adapters per cloud platform vendor
│   ├── gcp/
│   ├── postgresql/ - adapters for a 3rd party Open Source technology
│   ├── textual/ - Text UI adapter
│   └── <web>/ - Web UI adapter - TBD
├── domain/ - data structures common for ports and adapters
├── docs/ - Python-specific project documentation
│   ├── adrs/
│   ├── installation.md
│   ├── deployment.md
│   └── README.md
├── ports/ - a plain list of port definitions to keep import statements shorter
├── scripts/ - automation
├── test/ - acceptance tests (unit tests are TBD)
└── workflows/ - use case event flow realizations


This structure reflects Python idioms while preserving alignment with the architecture's intent. It avoids premature categorization or over-nesting while allowing space for adapter diversity and infrastructure specialization.

## Consequences

- The project avoids deep or redundant hierarchies, improving clarity and modularity.
- Each layer—domain, port, workflow, adapter—is physically separated to maintain architectural boundaries.
- Multiple adapters for the same port can coexist in an organized way, enabling flexible runtime configuration and substitution.
- The structure supports cross-cutting testing strategies and can evolve with minimal disruption.
- Common automation tasks can be centralized and reused through the `scripts` folder.
- The `docs` folder becomes the anchor for project-specific ADRs, configuration documentation, and usage instructions.

## References

- [ADR-002: Apply "Ports and Adapters" Architecture Pattern](../../common/docs/adrs/adr-002-apply-ports-and-adapters-architecture-pattern)
- [ADR-003: Use Separate Repositories with Git Subtree](../../common/docs/adrs/adr-003-use-separate-repositories-with-git-subtree)
- [ADR-PY-000: Use Python as Implementation Language](./adr-py-000-use-python-as-implementation-language.md)
- [ADR-PY-001: Use Mono-Repository](./adr-py-001-use-mono-repository.md)
