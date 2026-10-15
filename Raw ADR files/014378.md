# Reverse Client-Server Roles and Use WebSockets

![Status: Proposed](https://img.shields.io/badge/status-proposed-yellow)

## Date

📅 2024-06-01

## Context
The current architecture assumes that the **game (Bevy app)** acts as a server and the **camera
controller** (initially Python, later C++ or mobile) acts as a client, connecting via TCP. This setup
has worked well for local development but presents limitations when considering platform
flexibility:

- **Browsers (WebAssembly) cannot act as servers** due to sandboxing constraints.
- **Mobile devices** or embedded controllers are better suited to act as always-on, accessible
  servers or streaming endpoints.
- A **server-based controller** simplifies discovery and connectivity for clients (games).

Additionally, the chosen protocol — TCP with FlatBuffers — while performant, is not compatible with
web environments and may not be supported as widely across mobile platforms.

## Decision

### 1. **Reverse the Client-Server Roles**
- The **controller becomes the server** (exposing an API or socket for real-time pose streaming).
- The **game becomes the client**, connecting to the controller to receive motion data.

This change supports more diverse deployment options:
- Browser-based games (WASM) can initiate outgoing connections.
- Games running on various platforms (native, web, mobile) can interact with the controller
  uniformly.

### 2. **Adopt WebSockets as Communication Protocol**
- Replace raw TCP with **WebSockets**, which are:
  - Fully supported in **browsers**
  - Lightweight and **real-time capable**
  - Supported by **Rust (e.g. tokio-tungstenite)** and **Python (e.g. websockets, aiohttp)**

This shift allows the system to maintain efficient low-latency communication without sacrificing
platform compatibility.

## Consequences
- The controller implementation must be modified to run a WebSocket server.
- The Bevy game must connect to this WebSocket server as a client.
- Protocol payloads (e.g. FlatBuffers) may need to be adapted or wrapped for WebSocket frames.
- Deployment models (especially on mobile or embedded) will need to expose the controller endpoint
  securely.

## Alternatives Considered
| Approach     | Pros                             | Cons                                       |
|--------------|----------------------------------|--------------------------------------------|
| Keep TCP     | Simple, fast, already working    | Not browser-compatible, harder to scale    |
| Use gRPC     | Typed, structured                | gRPC-web complexity, heavier toolchain     |
| Use HTTP     | Universal                        | Too slow for pose streaming                |
| Use WebRTC   | Low latency, P2P                 | Complex setup, ICE/NAT traversal issues    |

## Future Work
- Evaluate if a message broker (e.g. NATS, MQTT) might be a better fit for multiple
  controllers/players.
- Ensure controller APIs can be extended (e.g. for authentication, metadata streaming).
- Abstract protocol handling for possible future backends (QUIC, gRPC).

## Related
- ADR 0003: [Use FlatBuffers over TCP for Pose Data Serialization and Transport](003-use-flatbuffers.md0)

