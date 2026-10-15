# Decision: Networking & Entity Identity

**Status:** Resolved

**Choice:** Lightyear for networking, SQLite for persistence identity

---

## Context

The workbench supports multiplayer (friends playing together). This requires:

- Networked entity replication
- Client prediction for responsive gameplay
- Server authority for consistency
- Entity identity that works across network and persistence

## Options Considered

### Networking

| Option | Pros | Cons |
|--------|------|------|
| **Lightyear** | Bevy-native, handles prediction/reconciliation | Relatively new |
| **bevy_replicon** | Simpler API | Less built-in prediction |
| **Custom** | Full control | Massive effort, error-prone |

### Entity Identity

| Option | Pros | Cons |
|--------|------|------|
| **Unified ID** | One ID everywhere | Complexity, ID collision concerns |
| **Separate IDs** | Each system handles its own | Must map between systems |

## Decision

**Lightyear for networking. Separate identity schemes for network and persistence.**

### Networking: Lightyear

Lightyear provides:
- Client-side prediction
- Server reconciliation
- Entity replication
- Input replication

### Identity: Separate Schemes

- **Network identity:** Lightyear handles this. Entities get network IDs during replication.
- **Persistence identity:** SQLite handles this. Templates/prefabs have stable IDs.
- **Runtime mapping:** When spawning from a template, store the template ID as a component.

## Implementation Notes

### Template vs Instance

```rust
// Template ID: stable, from SQLite
#[derive(Component)]
pub struct TemplateId(pub String);  // e.g., "enemy:grunt"

// Instance: spawned entity in the world
// Network ID: assigned by Lightyear during replication
// Bevy Entity: local to each client/server
```

### Spawning from Templates

```rust
fn spawn_enemy(
    commands: &mut Commands,
    registry: &EnemyRegistry,
    template_id: &str,
    position: Vec2,
) {
    let template = registry.get(template_id).unwrap();

    commands.spawn((
        TemplateId(template_id.to_string()),
        Health(template.health),
        Position(position),
        // Lightyear adds network components automatically
    ));
}
```

### Persistence

When saving:
```rust
struct SavedEntity {
    template_id: String,      // Which template this came from
    instance_state: Value,    // Delta from template (modified health, position, etc.)
}
```

When loading:
```rust
// 1. Look up template by ID
// 2. Spawn from template
// 3. Apply instance state delta
```

### Network Replication

Lightyear handles which components replicate:

```rust
app.add_plugins(ReplicationPlugin)
   .replicate::<Health>()
   .replicate::<Position>()
   .replicate::<TemplateId>();
```

## Consequences

- Lightyear handles all network complexity
- Template IDs are stable across sessions and networks
- Instance state (health, position) is the delta from template
- No need to invent entity identity—use each system's native scheme
- Mapping between schemes happens at spawn/save boundaries
