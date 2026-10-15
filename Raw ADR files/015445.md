# ADR-2 Use Clojure for Backend Development

## Context
The Rehearser MVP requires a backend that is robust, maintainable, and
cost-effective. The project has constraints around simplicity, ease of
development, and operational efficiency. But really, the team has an
existing experience and preference for Clojure, so the above does not
matter all that much.

## Decision
Adopt Clojure as the primary language for backend development.

## Expected Consequences

**Productivity**: Adopting Clojure is expected to support productivity
due to its concise syntax and functional programming model. The
dynamic nature and good support for interactive programming in the
REPL is expected to help here as well.

**Maintainability**: The emphasis on immutability and pure functions
may simplify testing and debugging processes.

**Performance**: The volumes of data and users are
expected to be low enough, that almost any platform will generally
reach the required response times.

**Startup time**: Clojure applications are in some situations somewhat
slow to start, often requiring at least several seconds of startup
time before being ready to serve requests. This may need consideration
in some deployment strategies, but for an MVP this is probably not a
severe issue.

**Interoperability and Tooling**: Clojure’s seamless integration with
Java libraries expands the available tools and resources, benefiting
from the JVM ecosystem. The maturity of Clojure tooling is generally
sufficient, although some tools might not be as polished as those
available for more widely used languages. This aspect necessitates
occasional workarounds or custom solutions for certain tasks.

**Ecosystem and Deployment**: The Clojure ecosystem, although rich,
may not be as extensive as Node.js or Python, requiring occasional
custom solutions or workarounds. Deployment will involve packaging the
application as a standalone JAR or using containerization (e.g.,
Docker) and deploying on a low-cost VM in an EU-based data center,
aligning with GDPR and budget constraints.

## Candidate comparison

1. **Clojure**:
   - **Pros**:
     - Concise syntax and functional programming model enhance
       productivity and maintainability.
     - Strong support for concurrency and immutability.
     - Excellent interoperability with Java and the JVM ecosystem.
   - **Cons**:
     - Startup time can be slower compared to other languages.
     - The ecosystem, while rich, is smaller compared to mainstream
       languages like Node.js or Python, potentially requiring custom
       solutions.
     - Learning curve for developers unfamiliar with functional
       programming or the JVM ecosystem.
     - Absence of static typing, which might help with avoiding some
       classes of defects.
2. **Anything else**:
   - **Pros**:
     - (Not really checked)
   - **Cons**:
     - Not Clojure
