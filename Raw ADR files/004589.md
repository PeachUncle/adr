# ADR-0002: Database Versioning Strategy

- **Date**: 2025-12-10
- **Status**: Accepted

## Context

The WeighToGo Android application uses SQLite for local data persistence. As the application evolves, the database schema will need to change to support new features, fix bugs, or improve performance.

**Current State (v1.0):**
- Database version: 1
- Tables: users, weight_entries, goal_weights
- `onUpgrade()` implementation: DROP and recreate all tables (data loss)
- Acceptable for development (no production users yet)
- NOT acceptable for production (would delete all user data)

**Requirements:**
- Support incremental schema changes without data loss
- Maintain backward compatibility where possible
- Clear upgrade path for each version increment
- Testable migration logic
- Rollback strategy for failed migrations

## Decision

We will adopt a **hybrid migration strategy** that combines manual SQL migrations for production with consideration for future Room Persistence Library adoption:

### Phase 1: Manual SQL Migrations (Current - v1.x)
**For immediate production releases:**

1. **Version-Specific Migration Logic**
   - Implement switch statement in `onUpgrade()` for incremental migrations
   - Each case handles migration from one version to the next
   - Migrations are cumulative (v1→v2→v3, not direct v1→v3)

```java
@Override
public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
    Log.w(TAG, "Upgrading database from version " + oldVersion + " to " + newVersion);

    // Incremental migrations - each case falls through to next
    switch (oldVersion) {
        case 1:
            // Upgrade from v1 to v2
            upgradeToVersion2(db);
            // Fall through
        case 2:
            // Upgrade from v2 to v3
            upgradeToVersion3(db);
            // Fall through
        // ... additional versions
    }

    Log.i(TAG, "Database upgrade completed successfully");
}

private void upgradeToVersion2(SQLiteDatabase db) {
    // Example: Add new column
    db.execSQL("ALTER TABLE users ADD COLUMN profile_image TEXT");
    Log.d(TAG, "Upgraded to version 2: Added profile_image column");
}
```

2. **Migration Types Supported**
   - **Add column**: `ALTER TABLE table_name ADD COLUMN column_name TYPE`
   - **Add table**: `CREATE TABLE IF NOT EXISTS new_table (...)`
   - **Add index**: `CREATE INDEX IF NOT EXISTS idx_name ON table(column)`
   - **Data migration**: `UPDATE table SET new_col = old_col WHERE ...`

3. **SQLite Limitations (Workarounds Required)**
   - Cannot drop column directly → Create new table, copy data, rename
   - Cannot modify column type → Use same workaround
   - Cannot rename column easily → ALTER TABLE RENAME COLUMN (SQLite 3.25+)

### Phase 2: Room Persistence Library (Future - v2.0+)
**For long-term maintainability:**

When migrating to Room (estimated Phase 2.0+):
- Leverage Room's automatic migration generation
- Use `@Database(version = X, exportSchema = true)` for schema tracking
- Implement Room Migration objects for manual migrations
- Keep existing manual migrations for users upgrading from v1.x

```java
// Example Room migration (future)
static final Migration MIGRATION_1_2 = new Migration(1, 2) {
    @Override
    public void migrate(SupportSQLiteDatabase database) {
        database.execSQL("ALTER TABLE users ADD COLUMN profile_image TEXT");
    }
};
```

### Testing Strategy

1. **Unit Tests for Each Migration**
   - Create database at old version
   - Insert test data
   - Run migration
   - Verify data preserved and schema updated

2. **Integration Tests**
   - Test cumulative migrations (v1→v3 should work)
   - Test data integrity after migration
   - Test rollback scenarios

3. **Manual QA Checklist**
   - Test on physical devices (various Android versions)
   - Test with large datasets (performance)
   - Test edge cases (empty tables, null values)

### Rollback Strategy

**If Migration Fails:**
1. Catch exception in `onUpgrade()`
2. Log error with details (old version, new version, SQL statement)
3. Attempt to restore from backup (if implemented)
4. Throw exception to prevent app from continuing with corrupt database
5. User can reinstall app (loses data, but prevents crashes)

**Future Enhancement:**
- Implement database backup before upgrade
- Store backup in external storage
- Restore from backup if migration fails

## Rationale

**Why Manual SQL Migrations (Phase 1)?**
- ✅ Full control over migration logic
- ✅ No additional dependencies (Room adds complexity)
- ✅ Easier to understand for SQLite-familiar developers
- ✅ Sufficient for simple schema changes (v1.0 → v1.5)
- ✅ Testable with Robolectric

**Why Consider Room (Phase 2)?**
- ✅ Compile-time verification of SQL queries
- ✅ Automatic migration generation for simple changes
- ✅ Better integration with Jetpack components (LiveData, Coroutines)
- ✅ Reduced boilerplate for DAO implementations
- ✅ Industry standard for modern Android apps

**Why NOT Room Immediately?**
- ❌ Learning curve for team unfamiliar with Room
- ❌ Requires significant refactoring of existing DAOs
- ❌ Adds build dependency and complexity
- ❌ Overkill for simple CRUD operations in v1.0
- ❌ Manual migrations still needed for complex transformations

**Why Incremental Switch-Based Migrations?**
- ✅ Handles any upgrade path (v1→v2, v1→v3, v2→v3)
- ✅ Clear, linear migration history
- ✅ Easy to test each migration step
- ✅ Fall-through allows cumulative migrations
- ✅ Standard Android pattern (used by Google samples)

## Consequences

### Positive
- ✅ **Data Preservation**: Users won't lose data during upgrades
- ✅ **Flexibility**: Can handle any schema change (add, modify, delete)
- ✅ **Testability**: Each migration can be unit tested
- ✅ **Clarity**: Each version change is explicitly documented in code
- ✅ **Future-Proof**: Room migration path is clear

### Negative
- ❌ **Manual Effort**: Every schema change requires manual SQL + tests
- ❌ **Complexity**: Switch statement grows with each version
- ❌ **No Automatic Generation**: Unlike Room, no tooling support
- ❌ **SQLite Limitations**: Some operations require workarounds

### Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Migration fails on some devices | Comprehensive testing on multiple Android versions |
| Data corruption during migration | Wrap migrations in transaction, rollback on error |
| Performance issues with large datasets | Test migrations with realistic data volumes |
| Forgotten migration step | PR checklist: "Did you increment DATABASE_VERSION?" |
| Complex column type changes | Document workaround pattern in this ADR |

## Implementation Checklist

When incrementing database version:
- [ ] Update `DATABASE_VERSION` constant
- [ ] Add new `case` in `onUpgrade()` switch statement
- [ ] Implement `upgradeToVersionX()` method with migration SQL
- [ ] Write unit test for migration (old version → new version)
- [ ] Test data preservation with realistic dataset
- [ ] Document breaking changes in CHANGELOG.md
- [ ] Update database architecture documentation

## Examples

### Example 1: Add Column (Simple)
```java
// DATABASE_VERSION = 2
private void upgradeToVersion2(SQLiteDatabase db) {
    db.execSQL("ALTER TABLE users ADD COLUMN profile_image TEXT");
}
```

### Example 2: Add Table
```java
// DATABASE_VERSION = 3
private void upgradeToVersion3(SQLiteDatabase db) {
    db.execSQL("CREATE TABLE IF NOT EXISTS achievements (" +
        "id INTEGER PRIMARY KEY AUTOINCREMENT, " +
        "user_id INTEGER NOT NULL, " +
        "achievement_type TEXT NOT NULL, " +
        "achieved_date TEXT NOT NULL, " +
        "FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE)");

    // Add index for foreign key
    db.execSQL("CREATE INDEX idx_achievements_user_id ON achievements(user_id)");
}
```

### Example 3: Rename Column (Workaround)
```java
// DATABASE_VERSION = 4
private void upgradeToVersion4(SQLiteDatabase db) {
    // SQLite doesn't support RENAME COLUMN directly (before 3.25)
    // Workaround: Create new table, copy data, drop old table, rename new table

    // 1. Create new table with correct column name
    db.execSQL("CREATE TABLE users_new (" +
        "id INTEGER PRIMARY KEY AUTOINCREMENT, " +
        "username TEXT NOT NULL UNIQUE, " +
        "email_address TEXT, " +  // Renamed from 'email'
        "created_at TEXT NOT NULL)");

    // 2. Copy data from old table
    db.execSQL("INSERT INTO users_new (id, username, email_address, created_at) " +
               "SELECT id, username, email, created_at FROM users");

    // 3. Drop old table
    db.execSQL("DROP TABLE users");

    // 4. Rename new table
    db.execSQL("ALTER TABLE users_new RENAME TO users");

    Log.d(TAG, "Upgraded to version 4: Renamed email column to email_address");
}
```

## References

- [SQLite ALTER TABLE documentation](https://www.sqlite.org/lang_altertable.html)
- [Android SQLiteOpenHelper documentation](https://developer.android.com/reference/android/database/sqlite/SQLiteOpenHelper)
- [Room Persistence Library](https://developer.android.com/training/data-storage/room)
- [Google I/O 2019: Room Migration Best Practices](https://www.youtube.com/watch?v=X7KjEe04MZk)

## Related ADRs

- ADR-0001: Initial Database Architecture (to be created)
- ADR-0003: Room Migration Strategy (future, when implemented)

## Supersedes

None - this is the first formal database versioning strategy for the project.

## Superseded By

None currently. Will be superseded by ADR-0003 when migrating to Room Persistence Library.
