# Use FlatBuffers over TCP for Pose Data Serialization and Transport

![](https://img.shields.io/badge/status-accepted-brightgreen)

## Date

📅 2024-06-01

To support real-time pose tracking for a camera-controlled game, we need an efficient and portable
mechanism for sending structured pose data from the capture device (client) to the game engine
(server). The system should be:

* Lightweight and fast enough for real-time applications
* Able to encode structured pose frames with nested fields
* Language-agnostic and easily portable between Python, Rust, C++, and others
* Flexible for future integrations (e.g., mobile, embedded, or web clients)

## Alternatives Considered

### 1. JSON over HTTP/WebSockets

* **Pros**:

  * Human-readable
  * Extremely common and well-supported in browsers and most platforms
* **Cons**:

  * Too verbose for real-time, high-frequency pose data
  * Requires more CPU time to parse/serialize
  * Lacks schema enforcement unless paired with external validation

### 2. Protocol Buffers (gRPC)

* **Pros**:

  * Strong schema, mature ecosystem
  * Works with HTTP/2 and has browser adapters
* **Cons**:

  * More complex to integrate across all environments
  * Limited native support in Rust compared to FlatBuffers
  * gRPC may be heavyweight for simple streaming pose data

### 3. FlatBuffers over TCP (Chosen)

* **Pros**:

  * Compact binary format with zero-copy deserialization
  * Schema-defined messages and strong type safety
  * Native support in Rust, Python, C++, and other target languages
  * TCP is simple and available across all major operating systems
* **Cons**:

  * No built-in transport protocol or compression
  * Direct TCP not ideal for browser clients (e.g., WebAssembly)

## Decision

We chose to use **FlatBuffers** to define and serialize pose data, and to transmit that data over
a **TCP socket** between the client and game server.

This approach is currently a strong fit for local development and early prototyping. It enables fast
communication, precise data control, and clean schema definitions shared across Python and Rust.

## Consequences

* A `.fbs` schema is defined and compiled to both Python and Rust via `flatc`.
* The game server listens on a local TCP socket; the Python-based client connects and streams
  serialized pose frames.
* FlatBuffers types are generated and stored in the `generated/` folder, and kept in sync via `make`.

## Future Considerations

* **Browser/WASM support**: WebAssembly targets cannot open raw TCP sockets; a shift to WebSockets
  or HTTP-based communication would be required to support browser clients.
* **Mobile / Embedded devices**: May require a transport abstraction layer (e.g., TCP vs. WebSocket)
  and possibly alternative serialization like CBOR or MessagePack for environments where FlatBuffers
  is not ideal.
* **Pluggable backends**: If the system must support heterogeneous input sources (e.g., iPhone camera,
  MediaPipe running on a Jetson Nano, etc.), a unified gateway or API layer might be needed.

For now, the current setup is sufficient for development and prototyping, but it may evolve toward a
more browser- or mobile-friendly communication protocol in later stages.

