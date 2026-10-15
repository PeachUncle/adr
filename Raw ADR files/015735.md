# Decision: Scripting Language

**Status:** Resolved

**Choice:** mlua with Luau dialect

---

## Context

The workbench needs a scripting layer so non-programmers can create custom behaviors without writing Rust. The scripting language must be:

- Sandboxed (users can't break the system)
- Simple enough for beginners
- Powerful enough for real behaviors
- Hot-reloadable

## Options Considered

| Option | Pros | Cons |
|--------|------|------|
| **Lua (mlua)** | Battle-tested, simple syntax, great Rust interop | No built-in typing |
| **Rhai** | Rust-native, good sandbox | Less ecosystem, unfamiliar syntax |
| **WASM** | Any language compiles to it | Complex toolchain, harder for beginners |

## Decision

**mlua with Luau dialect.**

Luau (Roblox's Lua variant) adds:
- Optional type annotations
- Better sandbox defaults
- Familiar to anyone who's modded games

## Implementation Notes

### Module-First Design

Scripts export module objects with hook handlers:

```lua
local module = {}

function module.on_spawn(entity)
    print("Entity spawned: " .. entity.name)
end

function module.on_update(entity, dt)
    -- Called each frame
end

return module
```

### UserData Pattern

Rust types exposed to Lua via `UserData` trait:

```rust
impl UserData for LuaEntity {
    fn add_methods<M: UserDataMethods<Self>>(methods: &mut M) {
        methods.add_method("name", |_, this, ()| Ok(this.name.clone()));
        methods.add_method("health", |_, this, ()| Ok(this.health));
    }
}
```

### Global Namespaces

Globals organized by purpose:

```lua
-- Accessing player inventory
local inv = inventory:player(player_id)
inv:add_item("health_potion")

-- Spawning entities
spawner:enemy("grunt", position)
```

### Hot Reload

- File watcher detects script changes
- ScriptLoader reloads affected modules
- Existing entities get new behavior immediately

## Consequences

- All behavior authoring uses Lua
- Rust code provides the API surface (UserData implementations)
- Scripts can't access arbitrary Rust internals (sandbox)
- Non-programmers can copy/modify example scripts
