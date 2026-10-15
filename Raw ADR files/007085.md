# ADR-001: Use PlantUML for Architecture Diagrams

## Status
Accepted

## Context

As established in [ADR-000: Use Architecture Decision Records (ADRs)](./adr-000-use-adrs-to-document-all-architecturally-significant-decisions.md), architecturally significant choices must be made explicit, version-controlled, and maintainable over time.

To support this, we require a consistent approach to visualizing architecture, system behavior, and design artifacts. These diagrams must be:

- **Readable** and consistent across languages and technology stacks
- **Maintained as plain text** to support version control, diffing, and peer review
- **Integrated into CI pipelines** and documentation workflows
- **Flexible enough** to represent various system views, including static structure and dynamic interactions

Traditional GUI-based tools fall short in collaborative, Git-based environments due to binary formats and lack of automation. Instead, we seek a lightweight, text-based solution that aligns with our engineering practices.

PlantUML is a widely adopted tool that satisfies these requirements. This ADR formalizes its adoption as the standard for all architecture and design diagrams in the project.

## Decision

We will use **PlantUML** as the standard tool for generating all architecture, design, and interaction diagrams in the **BlueZone** project.

PlantUML offers:

- Text-based syntax compatible with version control
- Support for multiple diagram types: class, component, sequence, activity, etc.
- Simple automation through CLI tools and `Makefile`-based workflows
- Wide adoption and integration into many IDEs, CI pipelines, and Markdown renderers

### Integration

- All `.puml` source files will be stored under the `./docs/puml` folder.
- All resulting `.png` diagram files produced by PluntUML will be stored under the `./docs/diagrams` folder.
- A standard `Makefile` will support rendering `.puml` files to `.png` and `.svg` targets using the shared `plantuml.jar` binary.
- The `scripts/install.sh` script will install Java and download the correct version of PlantUML for local and CI use.

Generated diagrams will be committed alongside their `.puml` source unless project policy changes.

## Benefits

- **Consistent, portable diagrams** across all implementations and documentation
- **Version-controlled text format** allows code review, diffing, and collaboration
- **Low-overhead tooling** for developers in any environment
- **Reusable in Markdown-based documentation** with image embedding

## Consequences

- Requires Java to be installed or provisioned in CI environments
- May be unfamiliar to contributors who prefer GUI-based diagramming tools
- Requires shared conventions for organizing diagram files and naming

## Out of Scope

- Tooling for editing diagrams in WYSIWYG or graphical mode (contributors may use IDE plugins at their discretion)
- Styling standards (e.g., fonts, layout) will evolve incrementally and are not mandated in this ADR

## References

- [PlantUML Language Reference Guide](https://plantuml.com/guide)
- [PlantUML CLI Usage](https://plantuml.com/command-line)

