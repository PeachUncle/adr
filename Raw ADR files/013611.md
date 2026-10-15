# ADR-002: Game State Management Pattern

## Status
Accepted

## Context
We need to decide how to manage the state of individual Parchís games in our umbrella architecture. Each game needs to track:

- **Game state**: Player positions, current turn, dice rolls, game phase
- **Concurrency**: Multiple games running in parallel (not within a single game)
- **Fault tolerance**: Recovery from process crashes or network issues
- **Scalability**: Supporting multiple concurrent games
- **State consistency**: Ensuring all players see the same game state
- **Reconnection support**: Players should be able to recover game state after connection issues

The decision impacts performance, reliability, and complexity of the `parchis_game` application within our umbrella project.

## Options Considered

**Option A: GenServer per Game**
- Each game instance runs as a dedicated GenServer process
- State stored in GenServer's internal state
- Registry for game discovery and process management
- Built-in serialization and message handling

**Option B: ETS-based State Storage**
- Game state stored in ETS tables
- Lightweight processes for game logic coordination
- Shared state accessible by multiple processes
- Manual state persistence management

**Option C: Agent per Game**
- Each game uses an Agent for state management
- Simpler than GenServer but less control over lifecycle
- Registry-based discovery
- Limited message handling capabilities

**Option D: Distributed Process Architecture**
- Games can run across multiple nodes
- Process groups for fault tolerance
- More complex but highly scalable
- Overkill for current requirements

## Learning Resources for Decision
- **GenServer Patterns**: "Elixir in Action" Chapter 7 - Generic server processes (Saša Jurić)
- **OTP Design Principles**: [OTP Design Principles - Erlang Documentation](https://www.erlang.org/doc/design_principles/gen_server_concepts.html)
- **Registry Usage**: "Programming Elixir ≥ 1.6" Chapter 18 - Tasks and Agents (Dave Thomas)
- **ETS Performance**: "Learn You Some Erlang" - ETS chapter (Fred Hébert)
- **Process Supervision**: "The Little Elixir & OTP Guidebook" Chapter 6 (Benjamin Tan Wei Hao)
- **State Recovery**: "Designing for Scalability with Erlang/OTP" Chapter 4 - Process Architecture (Francesco Cesarini)

## Decision
**Choose Option A: GenServer per Game**

## Rationale
1. **Current State Only**: No need for event sourcing or history - GenServer state is perfect for current game snapshot
2. **Turn-based Nature**: GenServer's synchronous message handling fits turn-based gameplay perfectly
3. **Automatic Cleanup**: GenServer lifecycle management handles cleanup when all players disconnect
4. **Connection Recovery**: Process state survives individual player disconnections
5. **Process Isolation**: Each game is completely isolated from others
6. **Built-in Supervision**: OTP supervision trees provide robust fault tolerance

## Architecture Pattern

```
DynamicSupervisor (GameSupervisor)
├── GameServer (game_id: "abc123")
├── GameServer (game_id: "def456")
└── GameServer (game_id: "xyz789")

Registry: game_id -> GameServer PID
Timeout: Auto-terminate when all players disconnected
```

## State Management Strategy
- **Current state snapshot**: No event history storage
- **In-memory state**: Stored in GenServer state
- **Cleanup trigger**: All players disconnected
- **Recovery method**: Process state available for reconnecting players

## Consequences

**Positive:**
- Simple state model - current game state only
- Natural process lifecycle management
- Built-in fault tolerance via OTP
- Turn-based synchronization handled automatically
- Clear process boundaries for AI development

**Negative:**
- State lost on process crash (requires supervision strategy)
- Memory usage scales with number of active games
- No audit trail of game moves

**Mitigation:**
- Implement robust supervision strategy
- Add timeout-based cleanup for inactive games
- Monitor memory usage patterns

## Compliance
This decision supports Modern Software Engineering principles:
- **Fast Feedback**: Simple state model enables quick testing
- **Build Quality In**: OTP patterns provide built-in reliability
- **Focus on Outcomes**: Serves reconnection and multi-game requirements