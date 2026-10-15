# ADR-002: OpenAPI processing pipeline in `@diplodoc/openapi-extension`

## Status

Accepted

## Context

The `@diplodoc/openapi-extension` package is responsible for rendering OpenAPI descriptions and the JSON Schemas contained inside them into Yandex Flavored Markdown (YFM) and UI components.

Over time, several concerns started to mix:

- Parsing and normalizing raw OpenAPI specifications (including different versions and vendor extensions).
- Rendering high-level OpenAPI structures (endpoints, operations, tags, security, etc.).
- Rendering JSON Schemas used in request/response bodies, parameters, and components.
- UI-specific concerns (React components, layout, interactivity).

Without clear boundaries, it becomes easy to:

- duplicate transformation logic in multiple places,
- introduce inconsistent behavior between “OpenAPI view” and “JSON Schema view”,
- leak normalization logic into UI components and tests.

## Decision

We explicitly separate processing into **independent stages** and **independent modules**:

1. **Specification loading & parsing**

   - Responsibility: read raw OpenAPI documents (YAML/JSON), resolve includes/refs on the file level where applicable.
   - Output: an in-memory representation close to the original spec (including version info and vendor extensions).

2. **Normalization layer**

   - Responsibility: convert raw OpenAPI data into internal, normalized structures that are:
     - version-agnostic where possible (OpenAPI 3.x vs 2.0),
     - consistent in how operations, parameters, request/response bodies, and components are represented,
     - safe and convenient for rendering (no surprising `undefined`/`null` shapes where we can provide defaults).
   - This layer **does not render** anything. It prepares data for both OpenAPI and JSON Schema renderers.

3. **OpenAPI rendering**

   - Responsibility: render high-level OpenAPI concepts:
     - operations/endpoints (method + path),
     - tags and groups,
     - servers,
     - security,
     - summaries and descriptions.
   - Rendering uses normalized data from step 2 and is **independent** from the JSON Schema rendering module.

4. **JSON Schema rendering**

   - Responsibility: render JSON Schemas referenced from the OpenAPI document:
     - request/response bodies,
     - parameters with schema,
     - reusable components.
   - This module is shared, self-contained and **does not know** about the surrounding OpenAPI context beyond what is passed explicitly via its API.

5. **UI composition**
   - Responsibility: compose React components / YFM blocks using the outputs from OpenAPI and JSON Schema renderers.
   - UI layers should not contain business logic for normalization or schema traversal beyond what is necessary for presentation.

### Key invariants

- **Normalization happens before rendering.**  
  Rendering functions and React components may assume that data has already been normalized according to this ADR.

- **OpenAPI renderer and JSON Schema renderer are independent modules.**

  - JSON Schema rendering must stay reusable outside of OpenAPI context.
  - OpenAPI rendering should treat JSON Schema rendering as a black box with a clear interface.

- **UI components do not perform structural normalization.**
  - They may handle view-specific defaults (e.g., “show empty state instead of an empty list”),
  - but they must not encode business rules about how an OpenAPI document or JSON Schema is interpreted.

## Consequences

### Positive

- Clear separation of responsibilities between parsing, normalization, rendering, and UI.
- Easier reuse of JSON Schema rendering in other contexts.
- Less duplication of transformation logic and fewer subtle inconsistencies.
- Tests can target each layer independently (normalization tests, rendering tests, UI tests).

### Negative

- Some refactors may be required to move logic from UI/components into the normalization layer.
- Developers and AI agents must be aware of the pipeline and choose the right layer for changes.

## Guidelines for future changes

- When fixing a bug related to how data is interpreted, **first check the normalization layer**.  
  Do not patch inconsistent shapes in UI components or individual renderers if the real problem is in normalization.

- When adding new features that depend on OpenAPI structure (e.g., new way to group endpoints),  
  prefer **extending normalized models** and reuse them in OpenAPI rendering.

- When changing how JSON Schemas are displayed, make changes in the **JSON Schema renderer module**,  
  not in OpenAPI-specific code, unless the change is truly OpenAPI-specific (e.g., different context labels).
