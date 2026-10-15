# ADR-003: Client-Side Storage Strategy

## Status

**Accepted** - 2026-01-07

## Context

Luminote needs to store various types of data on the client side for offline
access, performance, and user experience:

1. **Configuration Data**: Provider, model, target language (NOT API keys by
   default)
1. **Visit History**: URLs, titles, timestamps, cached content
1. **Translation Versions**: Multiple versions of translations for comparison
1. **Notes & Highlights**: User annotations and saved AI explanations
1. **Termbase**: Custom terminology dictionaries
1. **Draft Content**: Unsaved work, paste-text translations

Key requirements:

- Fast read/write for frequent operations
- Sufficient storage capacity (100+ MB for cached content)
- Structured data with indexing for queries
- Optional encryption for sensitive data
- User control over data persistence
- Easy to export/import for backup

We need to choose storage technologies that:

- Work reliably across browsers
- Support complex queries (history search, filtering)
- Handle large objects (cached HTML content)
- Are well-documented for GitHub Copilot
- Provide clear migration paths

## Decision

We will use a **layered storage strategy** with different technologies for
different data types:

### Storage Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
├─────────────────────────────────────────────────────────────┤
│                    Storage Abstraction                      │
│  (Unified API for all storage operations)                  │
├────────────┬──────────────┬──────────────┬─────────────────┤
│ localStorage│  IndexedDB   │ SessionStorage│  Memory Store  │
│  (Config)  │  (History,   │  (Temp API   │  (UI State)    │
│            │   Notes,     │   Keys)      │                 │
│            │   Versions)  │              │                 │
└────────────┴──────────────┴──────────────┴─────────────────┘
```

### Storage Allocation by Data Type

| Data Type               | Storage         | Size Limit | Persistence  | Reason                         |
| ----------------------- | --------------- | ---------- | ------------ | ------------------------------ |
| Configuration (no keys) | localStorage    | ~10 KB     | Persistent   | Simple, fast, survives reload  |
| API Keys (optional)     | sessionStorage  | ~1 KB      | Session-only | Security: cleared on tab close |
| Visit History           | IndexedDB       | ~50 MB     | Persistent   | Large objects, needs queries   |
| Translation Versions    | IndexedDB       | ~50 MB     | Persistent   | Large objects, versioning      |
| Notes & Highlights      | IndexedDB       | ~20 MB     | Persistent   | Structured data, searchable    |
| Termbase                | IndexedDB       | ~10 MB     | Persistent   | Structured data, relations     |
| Temporary Data          | Memory (stores) | ~10 MB     | Volatile     | No persistence needed          |
| Cached Extractions      | IndexedDB       | ~100 MB    | 24h TTL      | Large HTML, expire old         |

### Implementation Structure

```typescript
// src/lib/storage/index.ts

export interface StorageAdapter {
  get<T>(key: string): Promise<T | null>;
  set<T>(key: string, value: T): Promise<void>;
  delete(key: string): Promise<void>;
  clear(): Promise<void>;
}

// localStorage adapter
export class LocalStorageAdapter implements StorageAdapter {
  async get<T>(key: string): Promise<T | null> {
    const value = localStorage.getItem(key);
    return value ? JSON.parse(value) : null;
  }

  async set<T>(key: string, value: T): Promise<void> {
    localStorage.setItem(key, JSON.stringify(value));
  }

  async delete(key: string): Promise<void> {
    localStorage.removeItem(key);
  }

  async clear(): Promise<void> {
    localStorage.clear();
  }
}

// IndexedDB adapter
export class IndexedDBAdapter implements StorageAdapter {
  private dbName: string;
  private storeName: string;

  constructor(dbName: string, storeName: string) {
    this.dbName = dbName;
    this.storeName = storeName;
  }

  async get<T>(key: string): Promise<T | null> {
    const db = await this.openDB();
    const transaction = db.transaction(this.storeName, 'readonly');
    const store = transaction.objectStore(this.storeName);
    return new Promise((resolve, reject) => {
      const request = store.get(key);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  // ... other methods
}

// Unified storage manager
export class StorageManager {
  private config: LocalStorageAdapter;
  private history: IndexedDBAdapter;
  private notes: IndexedDBAdapter;

  constructor() {
    this.config = new LocalStorageAdapter();
    this.history = new IndexedDBAdapter('luminote', 'history');
    this.notes = new IndexedDBAdapter('luminote', 'notes');
  }

  // High-level methods
  async saveConfig(config: ConfigState): Promise<void> {
    await this.config.set('config', config);
  }

  async getHistory(limit: number = 50): Promise<HistoryEntry[]> {
    // Query IndexedDB with limit
  }
}

export const storage = new StorageManager();
```

### IndexedDB Schema

```typescript
// Database: luminote
// Version: 1

// Object Store: history
interface HistoryEntry {
  id: string;           // UUID
  url: string;          // Indexed
  title: string;
  visited_at: number;   // Indexed (timestamp)
  language_pair: string; // e.g., "zh-CN|en"
  content: string;      // Compressed JSON
  metadata: object;
}

// Object Store: versions
interface TranslationVersion {
  id: string;           // UUID
  history_id: string;   // Foreign key to history
  block_id: string;
  version_number: number;
  translated_text: string;
  prompt: string;
  model: string;
  created_at: number;
}

// Object Store: notes
interface Note {
  id: string;           // UUID
  history_id: string;   // Foreign key
  block_id: string;
  type: 'explanation' | 'definition' | 'summary' | 'highlight';
  content: string;
  created_at: number;   // Indexed
  tags: string[];       // Indexed
}

// Object Store: termbase
interface TermEntry {
  id: string;           // UUID
  source_term: string;  // Indexed
  target_term: string;
  context: string;
  category: string;     // Indexed
  created_at: number;
}
```

### Data Lifecycle

**Visit History:**

- Save on successful translation
- TTL: Keep last 100 entries or 30 days (configurable)
- Cleanup: Weekly background task
- Export: JSON file download

**Translation Versions:**

- Save on re-translation
- Keep: Last 3 versions per block
- Automatic pruning of old versions
- Linked to history entry (cascade delete)

**Notes:**

- Save immediately on creation
- Never auto-delete (user must delete)
- Full-text search enabled
- Export: Markdown file

**Configuration:**

- Save on change
- No TTL
- Export/import support

## Consequences

### Positive

- **Appropriate Technology**: Right tool for each data type
- **Performance**: Fast reads/writes with IndexedDB indexes
- **Capacity**: Sufficient for thousands of history entries
- **Offline-First**: Works without network connection
- **User Control**: Clear data management and export options
- **Security**: API keys in sessionStorage or memory only
- **Queries**: IndexedDB supports complex searches

### Negative

- **Complexity**: Multiple storage systems to manage
- **Browser Support**: IndexedDB API is verbose
- **Debugging**: Harder to inspect than localStorage
- **Migration**: Schema changes require migration logic
- **Quota**: Browser storage limits vary

### Trade-offs

- Chose IndexedDB over localStorage for large data despite complexity
- Chose sessionStorage over localStorage for API keys for security
- Chose not to encrypt by default (optional) for simplicity
- Chose TTL approach over unlimited storage to prevent quota issues

## Alternatives Considered

### 1. localStorage Only

**Pros:**

- Simple API
- Easy to debug
- Synchronous
- Good browser support

**Cons:**

- 5-10 MB limit (too small)
- No indexing/querying
- String-only values
- Synchronous blocks UI

**Verdict:** Rejected - Insufficient capacity and query capability

### 2. IndexedDB Only

**Pros:**

- Large capacity
- Complex queries
- Transactions
- Structured data

**Cons:**

- Verbose API
- Asynchronous complexity
- Overkill for simple config
- Harder for Copilot to generate

**Verdict:** Rejected - Too complex for simple data like config

### 3. Server-Side Storage

**Pros:**

- No client limits
- Sync across devices
- Better backup

**Cons:**

- Requires backend database
- Privacy concerns
- Network dependency
- Against BYOK philosophy

**Verdict:** Rejected - Contradicts local-first approach

### 4. WebSQL

**Pros:**

- SQL queries
- Familiar syntax

**Cons:**

- Deprecated standard
- No longer maintained
- Browser support declining

**Verdict:** Rejected - Deprecated technology

### 5. Cache API

**Pros:**

- Designed for offline
- Good for HTTP responses

**Cons:**

- Limited to HTTP responses
- Not for arbitrary data
- Different mental model

**Verdict:** Rejected - Not suitable for structured data

## Implementation Notes

### For GitHub Copilot

When implementing storage operations:

1. **Always use abstraction layer:**

```typescript
import { storage } from '$lib/storage';

// Don't access localStorage directly
const config = await storage.getConfig();
```

1. **Handle quota errors:**

```typescript
try {
  await storage.saveHistory(entry);
} catch (e) {
  if (e.name === 'QuotaExceededError') {
    await storage.cleanup();
    // Retry or notify user
  }
}
```

1. **Use transactions for related writes:**

```typescript
await storage.transaction(async (tx) => {
  await tx.saveHistory(entry);
  await tx.saveVersions(versions);
});
```

### Storage Abstraction Pattern

```typescript
// src/lib/storage/config-storage.ts

export class ConfigStorage {
  private adapter: StorageAdapter;

  constructor(adapter: StorageAdapter) {
    this.adapter = adapter;
  }

  async getConfig(): Promise<ConfigState> {
    const config = await this.adapter.get<ConfigState>('config');
    return config ?? DEFAULT_CONFIG;
  }

  async setProvider(provider: string): Promise<void> {
    const config = await this.getConfig();
    config.provider = provider;
    await this.adapter.set('config', config);
  }

  // ... other config methods
}
```

### Migration Strategy

```typescript
// src/lib/storage/migrations.ts

export const migrations = [
  {
    version: 1,
    up: async (db: IDBDatabase) => {
      db.createObjectStore('history', { keyPath: 'id' });
      const historyStore = db.transaction('history').objectStore('history');
      historyStore.createIndex('url', 'url', { unique: false });
      historyStore.createIndex('visited_at', 'visited_at', { unique: false });
    }
  },
  {
    version: 2,
    up: async (db: IDBDatabase) => {
      db.createObjectStore('notes', { keyPath: 'id' });
      // Add indexes...
    }
  }
];
```

### Cleanup Logic

```typescript
// src/lib/storage/cleanup.ts

export async function cleanupHistory(
  maxEntries: number = 100,
  maxAge: number = 30 * 24 * 60 * 60 * 1000 // 30 days
): Promise<void> {
  const history = await storage.getAllHistory();

  // Sort by date
  history.sort((a, b) => b.visited_at - a.visited_at);

  // Delete old entries
  const now = Date.now();
  const toDelete = history.filter(
    (entry, index) =>
      index >= maxEntries || (now - entry.visited_at) > maxAge
  );

  for (const entry of toDelete) {
    await storage.deleteHistory(entry.id);
  }
}
```

## Security Considerations

### API Key Handling

**Default (Session-Only):**

```typescript
// API key in memory only
const apiKeyStore = writable<string>('');

// Or sessionStorage (cleared on tab close)
sessionStorage.setItem('api_key', key);
```

**Optional Persistence (User Opt-In):**

```typescript
if (userConsentsToStorage) {
  // Encrypt before storing
  const encrypted = await encryptAPIKey(key, userPassword);
  await storage.set('encrypted_api_key', encrypted);
}
```

### Data Export

All data should be exportable:

```typescript
export async function exportAllData(): Promise<Blob> {
  const data = {
    config: await storage.getConfig(),
    history: await storage.getAllHistory(),
    notes: await storage.getAllNotes(),
    termbase: await storage.getAllTerms(),
    exported_at: new Date().toISOString()
  };

  return new Blob([JSON.stringify(data, null, 2)], {
    type: 'application/json'
  });
}
```

## References

- [MDN: IndexedDB API](https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API)
- [MDN: Web Storage API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Storage_API)
- [Feature Specifications - Local Storage](../feature-specifications.md#2-local-visit-history-and-quick-paste-text-translation)
- [BYOK Configuration](../feature-specifications.md#3-byok-bring-your-own-key-configuration)

## Changelog

- 2026-01-07: Initial version accepted
