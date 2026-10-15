# 06. WebSocket Server API for Multiplayer Tetris

Date: 2025-05-28

## Status

Accepted

## Context

To enable real-time multiplayer gameplay across multiple devices, the architecture must support efficient, low-latency communication between clients and a central server. The server is authoritative for game state, while clients are responsible for input and rendering. The user flow (see ADR#5) includes joining/creating games, waiting in a lobby, playing, and seeing results. The client code is structured around a Renderer interface, which provides methods for updating the visual state. The WebSocket API must support incremental, renderer-driven updates rather than sending the full game state on every change.

## Decision

- **Protocol:** Use WebSockets for bidirectional, real-time communication between clients and server.
- **Message Format:** All messages are JSON objects with a `type` field. Additional fields depend on the message type.
- **Client-to-Server Messages:**
  - `join`: Sent when a client connects. Includes player info (name, color).
  - `ready`: Sent when a player is ready to start the game from the lobby.
  - `action`: Sent when a player performs an in-game action (move, rotate, drop, etc.).
  - `leave`: Sent when a player leaves the game or disconnects.
- **Server-to-Client Messages:**
  - `player_joined`: Notifies clients when a new player joins the lobby.
  - `player_left`: Notifies clients when a player leaves or disconnects.
  - `game_started`: Sent when all players are ready; instructs clients to navigate to the game screen and begin play.
  - **Renderer-based incremental updates:**
    - `insert_shape`, `update_shape`, `remove_shape`, `update_points`, `clear_lines`, etc. (maps directly to Renderer interface methods; only changes are sent, not the full state)
  - `game_over`: Notifies clients that the game has ended and provides results.
  - `error`: Communicates errors (e.g., invalid action, room not found).

### Message Schemas

#### Client → Server

- **join**
  ```json
  { "type": "join", "player": { "name": "string", "color": "number" } }
  ```
- **ready**
  ```json
  { "type": "ready", "playerId": "string" }
  ```
- **action**
  ```json
  { "type": "action", "playerId": "string", "action": "MOVE_LEFT" | "MOVE_RIGHT" | "MOVE_DOWN" | "ROTATE" | "DROP" }
  ```
- **leave**
  ```json
  { "type": "leave", "playerId": "string" }
  ```

#### Server → Client

- **player_joined**
  ```json
  { "type": "player_joined", "player": { "id": "string", "name": "string", "color": "number" } }
  ```
- **player_left**
  ```json
  { "type": "player_left", "playerId": "string" }
  ```
- **game_started**
  ```json
  { "type": "game_started", "players": [ ... ] }
  ```
- **Renderer-based updates**
  - `insert_shape`
    ```json
    { "type": "insert_shape", "shape": { ... } }
    ```
  - `update_shape`
    ```json
    { "type": "update_shape", "shape": { ... } }
    ```
  - `remove_shape`
    ```json
    { "type": "remove_shape", "shapeId": "number" }
    ```
  - `update_points`
    ```json
    { "type": "update_points", "playerId": "string", "points": "number" }
    ```
  - `clear_lines`
    ```json
    { "type": "clear_lines", "playerId": "string", "lines": [number] }
    ```
- **game_over**
  ```json
  { "type": "game_over", "results": { ... } }
  ```
- **error**
  ```json
  { "type": "error", "message": "string" }
  ```

### Example Flow

1. Client connects and sends a `join` message.
2. Server responds with `player_joined` and updates the lobby for all clients.
3. Each client sends a `ready` message when ready.
4. When all players are ready, server sends `game_started` to all clients.
5. During gameplay, clients send `action` messages; server processes and sends incremental renderer-based updates.
6. When a player leaves, server sends `player_left`.
7. When the game ends, server sends `game_over`.

## Consequences

- Enables efficient, real-time multiplayer gameplay with minimal network overhead.
- Renderer-based incremental updates reduce bandwidth and improve responsiveness.
- The protocol is extensible for future features (e.g., chat, spectators).
- Requires careful handling of message ordering, error cases, and reconnection logic.

---

_See also: [04-client-server-components.md](./04-client-server-components.md), [05-user-experience-flow.md](./05-user-experience-flow.md)_
