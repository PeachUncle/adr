# Decision: Content Storage

**Status:** Resolved

**Choice:** SQLite as the source of truth

---

## Context

The workbench needs to store authored content (items, enemies, rooms, scripts). The storage solution must:

- Support the editor writing content
- Support the runtime reading content
- Enable hot reload (detect changes)
- Be simple to set up and use
- Work offline (no server required for solo use)

## Options Considered

| Option | Pros | Cons |
|--------|------|------|
| **SQLite** | Single file, queryable, ACID, great Rust support | Not as human-readable as text files |
| **RON files** | Human-readable, git-friendly | No queries, manual file watching, merge conflicts |
| **JSON files** | Universal format, human-readable | Same issues as RON |
| **SpacetimeDB** | Built for games, multiplayer-ready | More complex, newer technology |

## Decision

**SQLite as the source of truth.**

Content lives in a SQLite database. The editor writes directly to SQLite. The runtime reads from SQLite. Hot reload watches for database changes.

## Implementation Notes

### Schema Pattern

Each content type gets a table:

```sql
CREATE TABLE enemies (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    data TEXT NOT NULL,  -- JSON blob with full definition
    created_at INTEGER DEFAULT (unixepoch()),
    updated_at INTEGER DEFAULT (unixepoch())
);
```

The `data` column stores the full definition as JSON, allowing schema evolution without migrations for every field change.

### Rust Integration

Using `rusqlite` with `refinery` for migrations:

```rust
pub struct Database {
    conn: Connection,
}

impl Database {
    pub fn get_enemy(&self, id: &str) -> Result<EnemyDefinition, DatabaseError> {
        let data: String = self.conn.query_row(
            "SELECT data FROM enemies WHERE id = ?1",
            params![id],
            |row| row.get(0),
        )?;
        Ok(serde_json::from_str(&data)?)
    }
}
```

### ContentType Trait

Generic loading via trait:

```rust
pub trait ContentType: Sized {
    type Id;
    fn id(&self) -> &Self::Id;
    fn load_all(db: &Database) -> Result<Vec<Self>, LoadError>;
    fn type_name() -> &'static str;
}
```

### Hot Reload

- ContentWatcher monitors database for changes
- On change, affected ContentRegistry reloads
- Bevy event notifies systems of updated content

### Editor Integration

Editor (web UI via axum) writes directly to SQLite:

```
Browser form → POST /api/enemies → Database.upsert_enemy() → SQLite
                                                          ↓
                                            ContentWatcher detects change
                                                          ↓
                                            EnemyRegistry reloads
                                                          ↓
                                            Game uses new definition
```

## Consequences

- All content stored in single `.db` file
- Queries available for content management (find all enemies with health > 100)
- Can store binary blobs (sprites, audio) if needed
- Not human-editable (but editor UI is the interface)
- Git tracks the database file (or we export to SQL dumps for versioning)
