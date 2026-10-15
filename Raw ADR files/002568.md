# ADR 0001: Choice of Database Library (Whisper)

## Context and Problem Statement

Graphite needs a database library to store time-series data efficiently and allow quick retrieval for graph rendering.

## Decision Drivers

* High write and read performance for time-series data
* Simple integration with the rest of the Graphite system
* Scalability to handle high data volumes

## Considered Options

* Custom time-series database (Whisper)
* Using an existing time-series database like RRDtool
* Relational databases like MySQL or PostgreSQL

## Decision Outcome

Chosen option: "Custom time-series database (Whisper)", because
it is specifically designed for Graphite's needs, providing high performance for time-series data with a simple API, and allows direct manipulation of data stored in specially formatted files, making it efficient and scalable for the intended use.

### Consequences

* Good, because high performance and scalability tailored to Graphite's requirements.
* Bad, because development and maintenance overhead of a custom solution.

## Validation

The choice was validated through performance testing and real-world usage in a high-volume e-commerce environment.

## Pros and Cons of the Options

### Custom time-series database (Whisper)

* Good, because high performance tailored to specific needs.
* Good, because simple API for integration.
* Bad, because requires development and maintenance effort.

### Using an existing time-series database like RRDtool

* Good, because mature and well-tested.
* Good, because no development effort needed.
* Bad, because may not meet performance requirements.
* Bad, because less control over custom features.

### Relational databases like MySQL or PostgreSQL

* Good, because widely used and supported.
* Good, because robust and feature-rich.
* Bad, because not optimized for time-series data.
* Bad, because potential performance bottlenecks.

## More Information

For more details on the decision process, see the Graphite project documentation and performance benchmarks.
