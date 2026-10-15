# ADR-3 Use Clojure CLI tools and deps.edn

## Context
Clojure offers multiple build tools (Leiningen, Boot,
CLI+deps.edn). The project needs lightweight tooling that aligns with
modern Clojure practices while avoiding unnecessary complexity.

## Decision
Use **Clojure CLI tools** (`clj`/`clojure`) with **deps.edn** for
dependency management and task execution.

## Expected Consequences

**Simplicity**: The CLI tools provide a minimal, scriptable interface
without project-specific wrappers or plugins. This reduces cognitive
overhead for developers familiar with Clojure’s core tooling.

**Flexibility**: `deps.edn` allows fine-grained dependency management
(e.g., per-task aliases, override-free merging).

**Reproducibility**: Dependency resolution is deterministic, and the
toolchain encourages explicit configuration, reducing "works on my
machine" issues.

**Tooling Ecosystem**: While younger than Leiningen, the CLI tools
ecosystem is growing (e.g., `clj-kondo` for linting, `kaocha` for
testing). Some tasks may require manual setup (e.g., uberjar creation
via `tools.build`).

**Learning Curve**: Developers new to Clojure’s CLI tools may need
time to adapt, though the concepts (e.g., `deps.edn` aliases) are
simpler than Leiningen’s project.clj or Boot’s build.boot.

## Candidate comparison

1. **Clojure CLI + deps.edn (chosen)**
   - **Pros**:
     - Lightweight, no wrapper tool required.
     - Aligns with Clojure’s future direction (official tooling).
     - Easy to script and integrate with shell tools.
     - Most familiar to the team at the moment of choice
   - **Cons**:
     - Less "batteries-included" than Leiningen (e.g., no built-in `uberjar` task).
     - Smaller plugin ecosystem for niche tasks.

2. **Leiningen**
   - **Pros**:
     - Mature, extensive plugin ecosystem.
     - Familiar to many Clojure developers.
   - **Cons**:
     - Slower (JVM startup per task).
     - Plugin-based model can introduce complexity.

3. **Boot**
   - **Pros**:
     - Flexible, composable build pipeline.
   - **Cons**:
     - Steeper learning curve.
     - Less actively maintained.
     - Unfamiliar
