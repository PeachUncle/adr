# ADR: Developer Documentation Platform Selection

**Status:** Accepted  
**Date:** 2025-10-15  
**Decision Drivers:**  
- Unified developer experience  
- Integration with CI/CD pipelines  
- Alignment with internal platform engineering standards  
- Support for Architecture Decision Records (ADRs)  
- Maintainability and adoption scalability  

---

## Context

Modern engineering organizations require a centralized documentation system that goes beyond static pages. Documentation today must integrate tightly with:

- **Source control** (to remain versioned with code)  
- **Continuous delivery pipelines** (to ensure automation visibility)  
- **Service discovery and metadata management** (to provide context on ownership, lifecycle, and dependencies)

The desired solution should therefore:

1. Support **multi-source documentation** (e.g., markdown in repos, generated API docs, runbooks)  
2. Include **structured metadata** (e.g., ownership, lifecycle, dependency graph)  
3. Facilitate **Architecture Decision Records (ADRs)**  
4. Integrate with existing DevOps tools (e.g., GitHub, Azure DevOps, ArgoCD, and Kubernetes)  

---

## Considered Options

| Tool / Pattern | Description | Pros | Cons |
|----------------|-------------|------|------|
| **MkDocs** | Static site generator for Markdown docs, commonly used with `mkdocs-material`. | Simple setup, Git-based workflow, extensible with plugins (TechDocs foundation). | No native service catalog or ADR visualization; lacks organizational metadata. |
| **Docusaurus** | React-based static site generator by Meta. | Excellent UI, versioning, Markdown+MDX support, good developer experience. | Not oriented toward service catalogs; heavy for operational documentation. |
| **ReadTheDocs** | Hosted documentation platform for open source and private projects. | Mature platform, integrated with Sphinx, autodoc for Python. | Poor integration with CI/CD and service metadata; minimal extensibility for platform teams. |
| **Confluence** | Atlassian’s enterprise wiki. | Rich WYSIWYG editor, permissions model, enterprise adoption. | Content drift risk; disconnected from codebase; limited automation. |
| **GitBook** | SaaS documentation with Git integration. | Clean UX, easy for non-technical contributors. | Lacks service catalog or structured metadata; not self-hosted or deeply automatable. |
| **Spotify Backstage** | Open-source developer portal with Software Catalog, TechDocs, and ADR plugins. | Unified catalog for services, auto-generated TechDocs (MkDocs-based), ADR integration, extensible plugin system, metadata API, supports CI/CD and cloud integrations. | Requires initial setup and maintenance; more complex deployment than static sites. |

---

## Decision

**Chosen Option: Spotify Backstage**

Backstage was selected for its **unified documentation and metadata ecosystem**, combining:

- **Software Catalog**: Provides discoverability, ownership, and dependency mapping for internal services, components, and APIs.  
- **TechDocs**: Automatically generates and serves MkDocs-based documentation directly from code repositories.  
- **ADR Support**: Integrates with repository-based ADR patterns (e.g., `adr-tools` or `adr-log`), exposing architectural decisions through Backstage’s UI, contextualized by component ownership.  

These features together create a **single pane of glass for developers**—linking documentation, ownership, and architectural reasoning with live system metadata.  

---

## Consequences

**Positive:**
- Strong alignment with **platform-as-a-product** principles  
- Standardized approach to documentation across teams  
- Integration with GitOps workflows (TechDocs builds via CI)  
- Extensible to other developer-experience features (Scorecards, Catalog Imports, System Diagrams)  

**Negative:**
- Requires **initial infrastructure investment** (hosting, catalog setup)  
- Ongoing **plugin maintenance and security reviews**  
- Some non-engineering stakeholders may prefer simpler UIs like Confluence  

---

## Recommendation

Adopt **Spotify Backstage** as the centralized documentation and developer portal solution.  
Integrate **TechDocs** for Markdown-based documentation, **ADR plugins** for architectural traceability, and maintain the **Software Catalog** as the authoritative inventory of internal systems and components.  

---

## References

- [Backstage.io – Official Documentation](https://backstage.io/docs/)  
- [TechDocs Overview](https://backstage.io/docs/features/techdocs/techdocs-overview)  
- [ADR Plugin for Backstage](https://github.com/backstage/backstage/tree/master/plugins/adr)  
- [Spotify Engineering Blog – Backstage Developer Portal](https://engineering.atspotify.com/2020/03/introducing-backstage/)  
- [CNCF Project: Backstage](https://landscape.cncf.io/?selected=backstage)

