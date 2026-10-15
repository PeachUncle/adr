# ADR 001: Modular Crate-Based Architecture with MVC Pattern and Askama HTML Rendering

## Status
Accepted

## Context

We are developing a backend system that will serve a hypermedia-based frontend composed of full HTML documents and fragments. The system has the following characteristics:

- A small team is developing and maintaining the entire application.
- The frontend is composed of multiple integrated application areas (discovery, presentation, editing) served from the backend.
- Views are rendered server-side using [Askama](https://github.com/djc/askama), a compile-time HTML templating engine.
- Clients receive real-time updates via **Server-Sent Events (SSE)**.
- The system will offer both an HTTP API (via [Axum](https://github.com/tokio-rs/axum)) and a CLI interface for project metadata editing.

The system is expected to grow in size and complexity over time, so modularity, scalability, and clear separation of concerns are critical.

## Decision

We will organize the codebase as a **modular Cargo workspace** with **one crate per functional or architectural concern**. The architectural style will follow an adapted **Model-View-Controller (MVC)** pattern, with the following responsibilities distributed across crates:

### Architecture Layers and Crates

| Layer       | Crates                          | Responsibilities                                 |
|-------------|----------------------------------|--------------------------------------------------|
| Controller  | `http/`, `cli/`                 | Route handling, orchestration, I/O               |
| View        | `documents/`, `sse/`            | Rendering full HTML views or fragments           |
| Model       | `users/`, `auth/`, `storage/`, `types/` | Business logic, persistence, domain types         |
| Infra       | `events/`, `config/`            | Event broadcasting, configuration management     |

### Frontend Application Areas in `documents/`

The `documents` crate will be organized as a **monorepo-style module**, reflecting different frontend environments:

- `discovery/` — Views for browsing and searching all projects.
- `presentation/` — Views for presenting individual project data.
- `rdu_tools/` — Views used by the CLI for metadata editing.
- `shared/` — Common layouts, components, and template utilities.

Each module will contain:
- A `templates/` folder with Askama templates
- A `views.rs` with rendering functions
- A `mod.rs` to structure the public API

### Cargo Workspace Structure

```
myapp/
├── cli/                    # CLI entrypoint
├── http/                   # Axum-based HTTP API
├── documents/              # Askama HTML rendering
├── users/                  # User lifecycle logic
├── auth/                   # Authentication and sessions
├── storage/                # Data access layer
├── types/                  # Shared domain types and traits
├── config/                 # App configuration
├── events/                 # Domain event bus (tokio broadcast)
├── sse/                    # SSE integration (HTML fragment delivery)
├── Cargo.toml              # Workspace definition
```

### Routing and Rendering

- Axum route handlers in `http/` will invoke rendering logic from `documents/`.
- SSE streams in `sse/` will push rendered HTML fragments via `Event::data`.
- The CLI will reuse rendering logic from `documents::rdu_tools`.

### Testing Strategy

- Each crate can be tested independently using `cargo test -p <crate>`.
- Rendering logic in `documents/` will be unit tested by asserting on rendered HTML.
- Domain logic (`users/`, `auth/`) will be tested independently of transport concerns.

## Consequences

- ✅ High modularity and separation of concerns.
- ✅ Fast incremental compilation and clear dependency management.
- ✅ Easy testing and future scaling into services if necessary.
- ✅ MVC-like clarity with idiomatic Rust constructs (traits, crates, modules).
- ✅ Shared rendering logic between HTTP and CLI interfaces.
- ⚠ Slightly higher complexity in initial project setup.
- ⚠ Developers need to understand inter-crate dependencies and workspace tooling.

## Alternatives Considered

- **Flat module structure within a single crate**: Rejected due to lack of compile-time boundaries and poor scalability.
- **Microservice-based architecture**: Overkill for current team size and scope.
- **WebSocket-based updates**: More complex for uni-directional updates than SSE, not justified at this stage.
