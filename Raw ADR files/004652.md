# ADR-002: SQLite for Local Database

Status: Accepted
Date: 2025-12-18
Owner: User
Related Features: All features
Supersedes: N/A
Superseded by: N/A

---

## Context

We need a local database to track:
- Device photo metadata and upload status
- Remote photo references (file_id, message_id)
- Folder organization
- Bot configurations
- Upload queue for background processing
- Full-text search for OCR data

Requirements:
- Works offline (local-first architecture)
- Fast queries for large photo libraries (10,000+ photos)
- Full-text search capability
- ACID compliance for upload tracking
- Cross-platform (Android, iOS)

---

## Decision

Use **SQLite via expo-sqlite** as the local database.

Key points:
- Single database file: `wyvern-photos.db`
- Full schema defined in CREATE_TABLES_SQL
- FTS5 virtual table for OCR text search
- Triggers to keep FTS index in sync
- Foreign key constraints enabled
- Singleton settings table

---

## Alternatives considered

### Realm

- Pros: Object-oriented API, reactive queries, sync built-in
- Cons: Larger bundle size, sync not needed (we have Telegram), learning curve
- Rejected because: Overkill for simple relational data

### WatermelonDB

- Pros: Optimized for React Native, observable queries
- Cons: Another abstraction layer, less mature
- Rejected because: SQLite is simpler and more predictable

### AsyncStorage + JSON

- Pros: Simple API, built into React Native
- Cons: No relational queries, no indexes, scales poorly
- Rejected because: Cannot handle large photo libraries efficiently

---

## Consequences

### Positive

- Direct SQL queries for flexibility
- Proven stability and performance
- FTS5 provides powerful text search
- expo-sqlite is well-maintained and stable
- Standard SQL skills transfer
- Small bundle size

### Negative / risks

- Raw SQL requires manual schema management
- No built-in migrations (need to implement manually)
- No ORM benefits (type safety on queries)
- Mitigation: Keep schema in schema.ts, use TypeScript interfaces for type safety

---

## Impact

### Code

- Affected modules: `lib/database/`, all hooks, all features
- Schema: `lib/database/schema.ts` — single source of truth
-DAO pattern: `lib/database/dao.ts` — typed query functions

### Data / configuration

- Database file: `wyvern-photos.db` in app documents directory
- Singleton settings: id always equals 1
- Indexes: Created on common query patterns (uploaded status, dates, folders)
- FTS: Auto-synced via triggers

### Documentation

- Schema documented in schema.ts with TypeScript interfaces
- Each table has clear purpose comments

---

## Verification

### Test environment

- Environment: Android emulator, iOS simulator
- Database: Fresh database created on first launch

### Test flows

| ID | Scenario | Level | Expected result | Notes |
| --- | --- | --- | --- | --- |
| TST-001 | Fresh install | Device | Database created with all tables | Check PRAGMA table_list |
| TST-002 | Insert 10,000 photos | Device | Query returns in < 100ms | Use dateAdded DESC index |
| TST-003 | FTS search for "receipt" | Device | Relevant photos returned | Requires OCR data |
| TST-004 | Foreign key violation | Unit | Error thrown | Try invalid botId |

---

## References

- expo-sqlite docs: https://docs.expo.dev/versions/latest/sdk/sqlite/
- SQLite FTS5: https://www.sqlite.org/fts5.html
- Database schema: lib/database/schema.ts
