# ADR 002: Offline-First Strategy with UUID-based IDs

**Date**: 2024-12-11  
**Status**: Accepted  
**Deciders**: Project Team  
**Context Tags**: #offline #sync #architecture

---

## Context

### The Requirement

> "I can login once and then go offline for months and use the accounting system and come online and then sync using UUID's"

Users need to:
1. Work offline for extended periods (weeks/months)
2. Record transactions without internet
3. Sync seamlessly when back online
4. Avoid data loss or conflicts

### The Challenge

Traditional approaches:
- **Server-assigned IDs**: Can't create records offline (no server to assign ID)
- **Auto-increment IDs**: Collisions when multiple devices offline
- **Temporary IDs**: Complex remapping when syncing

---

## Decision

**We will implement a true offline-first architecture using client-generated UUIDs.**

### Core Principles

1. **Client-Generated IDs**: All record IDs are UUIDs generated on device
2. **Local-First Operations**: All CRUD operations work offline
3. **Automatic Sync**: Firestore handles sync when connection returns
4. **Append-Only for Transactions**: Financial records never deleted, only corrected
5. **Last-Write-Wins for Most Data**: Acceptable for our use case

---

## Technical Implementation

### 1. UUID Generation

```typescript
import { v4 as uuid } from 'uuid';

// Create transaction offline
const transaction: Transaction = {
  id: uuid(), // Globally unique, no server needed
  household_id: householdId,
  amount: 12500,
  date: Timestamp.now(),
  account_id: accountId,
  // ...rest of fields
  created_by_device: deviceUUID,
  created_at: Timestamp.now(),
};

// Write to Firestore
await setDoc(
  doc(db, `households/${householdId}/transactions/${transaction.id}`),
  transaction
);
// ↑ Works offline, queued for sync
```

### 2. Offline Persistence

```typescript
// Enable Firestore offline persistence
import { enableIndexedDbPersistence } from 'firebase/firestore';

await enableIndexedDbPersistence(db, {
  synchronizeTabs: true
});

// Now all operations work offline
```

### 3. Sync Detection

```typescript
// Listen to network status
import NetInfo from '@react-native-community/netinfo';

const unsubscribe = NetInfo.addEventListener(state => {
  console.log('Is connected?', state.isConnected);
  console.log('Connection type', state.type);
  
  if (state.isConnected) {
    showSyncIndicator('Syncing...');
  }
});

// Listen to Firestore sync status
const query = collection(db, `households/${householdId}/transactions`);
onSnapshot(query, (snapshot) => {
  snapshot.metadata.fromCache; // true if from cache (offline)
  snapshot.metadata.hasPendingWrites; // true if queued for sync
  
  if (snapshot.metadata.hasPendingWrites) {
    showSyncIndicator('Changes pending...');
  } else if (!snapshot.metadata.fromCache) {
    showSyncIndicator('Synced ✓');
  }
});
```

### 4. Conflict Resolution

**Our approach**: Last-write-wins (Firestore default)

**Why it works**:
- Single user most of the time
- Couples rarely edit same record simultaneously
- Conflicts very rare in practice

**For the rare conflict**:
```typescript
// Firestore handles this automatically
// Last update (by server timestamp) wins

// If conflict matters (e.g., budget closed), we can detect:
await runTransaction(db, async (transaction) => {
  const budgetRef = doc(db, `households/${householdId}/budgets/${budgetId}`);
  const budget = await transaction.get(budgetRef);
  
  if (budget.data().status === 'closed') {
    throw new Error('Budget already closed');
  }
  
  transaction.update(budgetRef, { status: 'closed' });
});
```

---

## Offline Capabilities

### What Works Offline

✅ **Full CRUD Operations**:
- Create transactions
- Edit transactions
- Delete transactions (soft delete)
- Create budgets
- Edit budget categories
- Add debts
- Record debt payments
- Create goals
- Update goal progress

✅ **Reads**:
- View all transactions
- View budgets
- View reports (calculated from local data)
- View debts
- View household data

✅ **Calculations**:
- Budget totals
- Category balances
- Debt snowball order
- Baby Step progress
- Financial reports

### What Doesn't Work Offline

❌ **Auth Changes**:
- Password reset (requires server)
- Email change (requires server)
- Token refresh (requires server)
- But: Existing session persists offline

❌ **Initial Login**:
- First-time login requires internet
- But: After login once, offline indefinitely

❌ **Receipt Photo Upload**:
- Photos stored locally offline
- Uploaded to Firebase Storage when online
- But: Can attach and view photos offline

❌ **Household Invitations**:
- Adding new members requires internet
- But: Existing members work offline

---

## Data Flow

### Offline Write Flow

```
User Action (Offline)
         ↓
  Generate UUID
         ↓
  Create Document
         ↓
  Write to Local Firestore Cache
         ↓
  Add to Pending Queue
         ↓
  Return Success to User
         ↓
  (User continues working)
         ↓
  Device Comes Online
         ↓
  Firestore Auto-Syncs Pending Writes
         ↓
  Server Receives Documents
         ↓
  Server Timestamp Applied
         ↓
  Real-time Listeners Notified
         ↓
  Other Devices Receive Updates
```

### Offline Read Flow

```
User Requests Data (Offline)
         ↓
  Query Local Firestore Cache
         ↓
  Return Cached Data
         ↓
  UI Updates Instantly
         ↓
  (No network call needed)
```

### Online Sync Flow

```
Device Comes Online
         ↓
  Firestore Detects Connection
         ↓
  Flush Pending Writes
         ↓
  Download Remote Changes
         ↓
  Merge with Local Cache
         ↓
  Trigger Snapshot Listeners
         ↓
  UI Updates with New Data
         ↓
  Show "Synced ✓" Indicator
```

---

## Edge Cases & Solutions

### Edge Case 1: Months Offline, Phone Lost

**Problem**: User offline for 3 months, drops phone in lake

**Solution**: 
```
❌ We accept data loss
✅ We warn users proactively

Implementation:
- Show warning after 7 days offline: "Please sync soon"
- Show urgent warning after 30 days: "SYNC NOW to back up data"
- Option to export backup locally (future feature)
```

**User decision**: Offline-first means accepting this risk

### Edge Case 2: Both Devices Edit Same Transaction Offline

**Problem**: 
- Device A offline: Edit transaction amount to $100
- Device B offline: Edit same transaction amount to $120
- Both come online

**Result**: Last write wins (one overwrites the other)

**Solution**: Acceptable for our use case
- Rare occurrence (single user most of the time)
- User can fix manually if noticed
- Alternative would add massive complexity

### Edge Case 3: Security Rules Change While Offline

**Problem**:
- User offline for 2 months
- Admin changes security rules
- User comes online, writes fail

**Solution**: 
```typescript
// Listen for write failures
onSnapshot(query, 
  (snapshot) => { /* success */ },
  (error) => {
    if (error.code === 'permission-denied') {
      showAlert('Some changes could not sync. Please contact support.');
      logFailedWrites(error);
    }
  }
);

// Log failed writes for manual recovery
async function logFailedWrites(error: FirebaseError) {
  await setDoc(doc(db, 'sync_errors', uuid()), {
    user_id: currentUserId,
    error: error.message,
    timestamp: Timestamp.now(),
    device_id: deviceUUID,
  });
}
```

### Edge Case 4: Firestore Cache Limit Exceeded

**Problem**: Too much data to cache locally

**Solution**:
- Firestore cache: 40 MB by default
- For our use case: 100,000 transactions = ~10 MB
- Should never hit limit for typical user
- If hit: Firestore auto-evicts old data (LRU)

```typescript
// Can increase cache size if needed
enableIndexedDbPersistence(db, {
  cacheSizeBytes: 100 * 1024 * 1024, // 100 MB
});
```

---

## Advantages

### 1. True Offline Operation

✅ **No "Offline Errors"**:
```typescript
// Traditional approach:
try {
  await createTransaction(data);
} catch (err) {
  if (err === NetworkError) {
    showError('No internet connection'); // ❌ Bad UX
  }
}

// Our approach:
await createTransaction(data); // Always succeeds
// Syncs automatically later ✅
```

### 2. Instant UI Feedback

✅ **Optimistic Updates**:
```typescript
// Write appears instantly
await setDoc(doc(db, 'transactions', txId), transaction);
// ↑ Returns immediately, user sees update

// Sync happens in background
// No spinner, no waiting
```

### 3. Reliability

✅ **No Sync Engine to Build**:
- Firestore handles queue
- Firestore handles retries
- Firestore handles ordering
- Firestore handles conflicts

### 4. Simplicity

✅ **Same Code for Online/Offline**:
```typescript
// One code path for both
async function createTransaction(data: Transaction) {
  await setDoc(
    doc(db, `households/${data.household_id}/transactions/${data.id}`),
    data
  );
  // Works offline AND online
}
```

---

## Disadvantages

### 1. NoSQL Limitations

❌ **No Transactions Across Documents** (in SQL sense):
```typescript
// Can't do atomic multi-doc updates reliably offline
// Must use Firestore batch writes (online only)

// Solution: Design data to avoid needing this
// Use subcollections to keep related data together
```

### 2. Limited Query Capabilities

❌ **Must Design for Firestore Queries**:
```typescript
// Can't do:
// SELECT * FROM transactions WHERE amount > 100 AND date < '2024-01-01'
// (Multiple inequalities on different fields)

// Must use composite indexes:
// Index: household_id + amount + date
```

### 3. Potential Conflicts

❌ **Last-Write-Wins Can Lose Data**:
- Rare but possible
- Acceptable trade-off for simplicity
- Can add conflict detection if needed later

---

## Monitoring & Debugging

### Track Sync Health

```typescript
interface SyncHealth {
  last_sync_at: Date;
  pending_writes: number;
  failed_writes: number;
  offline_duration_minutes: number;
}

async function checkSyncHealth(): Promise<SyncHealth> {
  // Check if writes pending
  const snapshot = await getDocs(query);
  const pending = snapshot.docs.filter(
    d => d.metadata.hasPendingWrites
  ).length;
  
  // Check network
  const networkState = await NetInfo.fetch();
  
  return {
    last_sync_at: getLastSyncTimestamp(),
    pending_writes: pending,
    failed_writes: await getFailedWriteCount(),
    offline_duration_minutes: calculateOfflineDuration(),
  };
}

// Show in settings/debug screen
function SyncHealthScreen() {
  const health = useSyncHealth();
  
  return (
    <View>
      <Text>Last Sync: {health.last_sync_at.toLocaleString()}</Text>
      <Text>Pending: {health.pending_writes}</Text>
      <Text>Failed: {health.failed_writes}</Text>
      <Text>Offline: {health.offline_duration_minutes} minutes</Text>
    </View>
  );
}
```

### Device ID for Debugging

```typescript
// Store device UUID for sync debugging
import DeviceInfo from 'react-native-device-info';

const DEVICE_ID = await DeviceInfo.getUniqueId();

// Include in all writes
const transaction = {
  // ... fields
  created_by_device: DEVICE_ID,
  created_at: Timestamp.now(),
};

// Can track which device created what
// Useful for debugging conflicts
```

---

## Testing Strategy

### Manual Testing Checklist

- [ ] Create transaction while airplane mode on
- [ ] Verify transaction appears in UI
- [ ] Turn airplane mode off
- [ ] Verify transaction syncs to Firestore
- [ ] Verify transaction appears on other device
- [ ] Edit transaction offline
- [ ] Delete transaction offline
- [ ] Create 100 transactions offline
- [ ] Sync all 100 successfully
- [ ] Stay offline for 7 days
- [ ] Verify all features still work
- [ ] Sync after 7 days

### Automated Tests

```typescript
describe('Offline-first functionality', () => {
  it('should create transaction offline', async () => {
    // Disconnect
    await db.disableNetwork();
    
    // Create transaction
    const tx = createTransaction({ amount: 100 });
    await saveTransaction(tx);
    
    // Verify in local cache
    const result = await getTransaction(tx.id);
    expect(result).toBeDefined();
    expect(result.metadata.hasPendingWrites).toBe(true);
    
    // Reconnect
    await db.enableNetwork();
    
    // Wait for sync
    await waitFor(() => {
      const synced = await getTransaction(tx.id);
      return !synced.metadata.hasPendingWrites;
    });
    
    expect(syncedResult.metadata.fromCache).toBe(false);
  });
});
```

---

## Migration Path

### If We Need to Change Approach

**Scenario**: Firestore offline not working as expected

**Alternative 1: SQLite + Sync**
- Estimated effort: 6-8 weeks
- Add SQLite database
- Build sync engine
- Migrate data

**Alternative 2: Realm**
- Estimated effort: 4-6 weeks
- Add Realm database
- Use Realm Sync
- Migrate data

**Cost**: $60k-100k in developer time

---

## Success Metrics

We will know this approach works if:

1. ✅ 0 data loss incidents
2. ✅ >99% sync success rate
3. ✅ <5s sync time for 100 pending writes
4. ✅ Works after 30+ days offline
5. ✅ No UUID collisions
6. ✅ Conflict rate <0.1%
7. ✅ Users never see "offline error" messages

---

## References

- [Firestore Offline Persistence](https://firebase.google.com/docs/firestore/manage-data/enable-offline)
- [UUID RFC 4122](https://tools.ietf.org/html/rfc4122)
- [Offline-First Design Patterns](https://offlinefirst.org/)
- [Local-First Software](https://www.inkandswitch.com/local-first/)

---

## Decision Log

- **2024-12-11**: Decided on offline-first with UUIDs
- **2024-12-11**: Accepted last-write-wins for conflicts
- **2024-12-11**: Accepted data loss risk if device lost while offline

---

## Notes

This decision is core to the app's value proposition. The ability to work offline for extended periods differentiates us from competitors.

The UUID approach is simple and proven. The trade-offs (last-write-wins, NoSQL limitations) are acceptable for our use case.

Key insight: **Most users are single-user OR mostly online**. Conflicts are theoretical concerns, not practical problems.

