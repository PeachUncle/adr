# ADR-0003: Single File vs Multiple Files for Memory Storage

**Status**: Accepted
**Date**: 2025-08-05
**Context**: Travel Memory Journal needs to organize JSON storage efficiently for 1000+ travel memories while maintaining simplicity and performance.

## Problem Statement
How should we organize memory storage in JSON format - single file containing all memories or multiple files organized by date/location/category?

## Decision Drivers
- **Business Requirements**: Simple backup and restore, data portability, user data control
- **Technical Constraints**: 1000+ memories (~1MB total), atomic operations, data consistency
- **Team Constraints**: MVP timeline, minimal file system complexity
- **Non-Functional Requirements**: App launch <3s, search <2s, reliable data integrity

## Options Considered

### Option 1: Single JSON File (Recommended)
**Pros**:
- Atomic read/write operations ensure data consistency
- Simple backup and restore (single file copy)
- Faster app startup - load once, cache in memory
- No file fragmentation or missing file issues
- Easier data validation and integrity checks
- Perfect for MVP scope and timeline

**Cons**:
- Entire file must be rewritten on each update
- Memory usage grows with dataset size
- Potential for data loss if file corruption occurs

**Implementation Effort**: S (Small)
**Operational Complexity**: Low

### Option 2: Multiple Files by Date (Year/Month)
**Pros**:
- Smaller individual files reduce memory usage
- Partial data loss risk (only one month affected)
- Could enable date-range optimizations

**Cons**:
- Complex file management and organization logic
- Race conditions between multiple file operations
- Harder to maintain data consistency across files
- More complex backup strategy (multiple files)
- Increased app startup time (scan multiple files)

**Why Not Chosen**: Adds significant complexity without proportional benefits for 1MB dataset

### Option 3: One File Per Memory
**Pros**:
- Maximum granular control and isolation
- Easy to add/remove individual memories

**Cons**:
- File system overhead with 1000+ small files
- Complex indexing and search across files
- Potential file system performance issues
- Much more complex implementation
- Backup becomes directory sync operation

**Why Not Chosen**: Massive complexity increase with poor performance characteristics

## Decision
We will use a **Single JSON File** (`memories.json`) containing all user memories.

**Rationale**: Single file storage provides the optimal balance of simplicity, performance, and reliability for our use case. With only 1MB of total data, the benefits of file splitting don't justify the complexity costs.

## Consequences
**Positive**:
- Atomic operations prevent data corruption during writes
- Simple and reliable backup strategy
- Fast in-memory operations after initial load
- Easy data validation and integrity verification
- Minimal file system complexity
- Clear data ownership and location

**Negative**:
- Full file rewrite on each memory addition/update
- Complete data loss risk if single file corrupts
- Memory usage proportional to total dataset size

**Implementation Notes**:
- Implement atomic writes using temporary files and rename operations
- Create timestamped backup files before each write operation
- Use file locking to prevent concurrent access issues
- Implement data validation on load to detect corruption
- Consider lazy loading strategies if memory usage becomes an issue

## File Structure
```
~/.travel-memory-journal/
├── memories.json           # Primary data file
├── backups/
│   ├── memories-2025-08-05-14-30-00.json
│   ├── memories-2025-08-05-15-45-12.json
│   └── memories-2025-08-05-16-22-35.json
└── config.json            # Application configuration
```

## Data Format
```json
{
  "metadata": {
    "version": "1.0",
    "created_at": "2025-08-05T12:00:00Z",
    "updated_at": "2025-08-05T16:22:35Z",
    "total_memories": 157
  },
  "memories": [
    {
      "id": "uuid-here",
      "location": "Paris, France",
      "date": "2024-07-15",
      "description": "Amazing day exploring the Louvre...",
      "tags": ["museum", "art", "culture", "paris"],
      "created_at": "2025-08-05T12:15:00Z",
      "updated_at": "2025-08-05T12:15:00Z"
    }
  ]
}
```

## Migration Strategy
If single file approach becomes problematic:
1. Implement file splitting by year while maintaining same API
2. Add index file for cross-file operations
3. Migrate existing single file to new structure
4. Maintain backward compatibility for data imports