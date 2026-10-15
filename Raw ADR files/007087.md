# ADR-004: Use Gherkin for Acceptance Test Specifications

## Status
Accepted

## Context

The BlueZone application follows the "Ports and Adapters" architecture pattern and embraces the Set-Based Engineering (SBE) approach. In this context, acceptance tests are not only used to validate behavior, but also to define expected system functionality in a **technology-neutral**, **actor-driven** form.

To support multiple competing implementations (e.g., Python, TypeScript), we need a common, human-readable language for specifying use case behavior that:

- Can be understood by both technical and non-technical stakeholders
- Is easily portable across programming languages and frameworks
- Can serve as a contract for validating conformance regardless of implementation details

## Decision

We will use **Gherkin** to write acceptance test specifications for all BlueZone use cases.

Each use case will be expressed using Gherkin-style **Given–When–Then** scenarios.

To improve readability and navigation within GitHub, these scenarios will be stored in `.feature.md` files—Markdown documents that preserve standard Gherkin syntax but render better in the GitHub UI than plain `.feature` files. These files may include supplementary Markdown elements such as links or section headers.

The `.feature.md` files will:

- Capture the intended behavior from the perspective of external actors (e.g., Car Driver, Parking Inspector, Administrator)
- Serve as shared artifacts across all implementation repositories via Git subtree (`common/features/`)
- Drive the definition of internal ports and test harness logic in each language-specific implementation

### Language-Specific Integration

Each language-specific repository will:

- Reuse the common `.feature.md` files directly
- Implement a language-specific test runner and step definitions
- Optionally preprocess `.feature.md` files into raw `.feature` files for use with standard Gherkin test tools
- Integrate the acceptance tests into CI pipelines to verify conformance

## Benefits

- **Language-neutral** specification of expected behavior
- **Readable by both domain experts and developers**
- **Reusable across implementations**, supporting parallel evolution
- **Aligned with use cases and actors**, not tied to internal architecture
- **Improved GitHub rendering** compared to raw `.feature` files

## Consequences

- Requires tooling or conventions to extract `.feature` content from `.feature.md` files for test runners
- Enforcing consistency and completeness across `.feature.md` files becomes a documentation responsibility
- Not ideal for very low-level or infrastructure-specific testing (but that’s out of scope for Gherkin)

## Out of Scope

- Mapping Gherkin scenarios to internal port definitions is deferred to a separate ADR.
- Naming conventions and folder structure for `.feature.md` files are documented elsewhere.

## References

- [Cucumber documentation](https://cucumber.io/docs/gherkin/)
- [Set-Based Engineering in Software](https://medium.com/@asher-sterkin/focus-on-core-value-and-keep-cloud-infrastructure-flexible-with-ports-adapters-af79c5fa1e56)
