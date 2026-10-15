# ADR 003: Append-Only Transactions with Late Entry Tracking

**Date**: 2024-12-11  
**Status**: Accepted  
**Deciders**: Project Team  
**Context Tags**: #transactions #audit #data-integrity

---

## Context

### The Requirement

> "Reports should be generated from live data but we should capture late entries so we can identify if I don't capture as it happens it's a bad habit."

Two competing needs:
1. **Financial Integrity**: Need accurate historical records
2. **Behavior Tracking**: Need to know when entries are captured late

### The Problem

Traditional approaches:
- **Full Edit**: Allow changing any field anytime → Audit trail lost
- **Read-Only**: Never allow edits → Users frustrated by typos
- **Version History**: Complex to implement and query

---

## Decision

**We will use an append-only pattern for transactions with correction entries, and track late entry behavior separately.**

### Core Principles

1. **Original Transaction Immutable**: Once created, core fields locked
2. **Corrections via New Entries**: Fixes create new correction transactions
3. **Late Entry Tracking**: Separate fields track capture behavior
4. **Live Data for Reports**: Always use latest corrected data
5. **Full Audit Trail**: Can reconstruct any point in time

---

## Data Model

### Transaction Fields

```typescript
interface Transaction {
  // Identity
  id: string;  // UUID
  
  // Core Fields (Immutable after creation)
  date: Timestamp;           // When transaction occurred
  amount: number;            // Amount in cents
  account_id: string;        // Which account
  type: 'EXPENSE' | 'INCOME' | 'TRANSFER';
  
  // Mutable Fields (Can be edited)
  payee?: string;            // Can fix typos
  notes?: string;            // Can add details
  
  // Late Entry Tracking (Set once at creation)
  captured_at: Timestamp;    // When entered in app
  capture_delay_days: number; // date - captured_at
  
  // Corrections
  corrects_transaction_id?: string;  // If this corrects another tx
  corrected_by_transaction_id?: string;  // If this was corrected
  is_correction: boolean;     // True if this is a correction entry
  
  // Soft Delete
  status: 'active' | 'deleted' | 'corrected';
  
  // Audit
  created_at: Timestamp;
  updated_at: Timestamp;
  created_by: string;
  created_by_device: string;
}
```

---

## Implementation

### 1. Create Transaction (Immediate Entry)

```typescript
async function createTransaction(data: CreateTransactionInput): Promise<Transaction> {
  const now = Timestamp.now();
  
  const transaction: Transaction = {
    id: uuid(),
    date: data.date,
    amount: data.amount,
    account_id: data.account_id,
    type: data.type,
    payee: data.payee,
    notes: data.notes,
    
    // Late entry tracking
    captured_at: now,  // Captured now
    capture_delay_days: 0,  // Same day = 0 delay
    
    // Not a correction
    is_correction: false,
    corrects_transaction_id: null,
    corrected_by_transaction_id: null,
    
    status: 'active',
    created_at: now,
    updated_at: now,
    created_by: getCurrentUserId(),
    created_by_device: getDeviceId(),
  };
  
  await saveTransaction(transaction);
  return transaction;
}
```

### 2. Create Late Entry

```typescript
async function createLateEntry(data: CreateTransactionInput): Promise<Transaction> {
  const now = Timestamp.now();
  const transactionDate = data.date;
  
  // Calculate delay
  const delayDays = differenceInDays(now.toDate(), transactionDate.toDate());
  
  const transaction: Transaction = {
    id: uuid(),
    date: transactionDate,  // When it actually happened
    amount: data.amount,
    // ... other fields
    
    // Late entry tracking
    captured_at: now,  // Captured today
    capture_delay_days: delayDays,  // e.g., 14 days late
    
    is_correction: false,
    status: 'active',
    created_at: now,
    updated_at: now,
    created_by: getCurrentUserId(),
    created_by_device: getDeviceId(),
  };
  
  // Warn if very late
  if (delayDays > 7) {
    showWarning(`This transaction is ${delayDays} days late. Try to capture expenses same-day!`);
  }
  
  await saveTransaction(transaction);
  return transaction;
}
```

### 3. Correct Transaction (Wrong Amount)

```typescript
async function correctTransaction(
  originalId: string,
  newAmount: number,
  reason: string
): Promise<Transaction> {
  // 1. Get original transaction
  const original = await getTransaction(originalId);
  
  // 2. Mark original as corrected
  await updateTransaction(originalId, {
    status: 'corrected',
    updated_at: Timestamp.now(),
  });
  
  // 3. Create correction transaction
  const correction: Transaction = {
    id: uuid(),
    date: original.date,  // Same date as original
    amount: newAmount,    // Corrected amount
    account_id: original.account_id,
    type: original.type,
    payee: original.payee,
    notes: `Correction: ${reason}. Original amount: ${formatMoney(original.amount)}`,
    
    // Late entry tracking (from ORIGINAL)
    captured_at: original.captured_at,  // Keep original capture time
    capture_delay_days: original.capture_delay_days,
    
    // Mark as correction
    is_correction: true,
    corrects_transaction_id: originalId,
    
    status: 'active',
    created_at: Timestamp.now(),
    updated_at: Timestamp.now(),
    created_by: getCurrentUserId(),
    created_by_device: getDeviceId(),
  };
  
  await saveTransaction(correction);
  
  // 4. Link back to original
  await updateTransaction(originalId, {
    corrected_by_transaction_id: correction.id,
  });
  
  return correction;
}
```

### 4. Soft Delete Transaction

```typescript
async function deleteTransaction(id: string): Promise<void> {
  // Never hard delete financial data
  await updateTransaction(id, {
    status: 'deleted',
    updated_at: Timestamp.now(),
  });
  
  // If this corrected another transaction, restore original
  const tx = await getTransaction(id);
  if (tx.corrects_transaction_id) {
    await updateTransaction(tx.corrects_transaction_id, {
      status: 'active',  // Restore
      corrected_by_transaction_id: null,
    });
  }
}
```

---

## Querying

### Get Active Transactions

```typescript
async function getActiveTransactions(
  householdId: string
): Promise<Transaction[]> {
  const q = query(
    collection(db, `households/${householdId}/transactions`),
    where('status', '==', 'active'),
    orderBy('date', 'desc')
  );
  
  const snapshot = await getDocs(q);
  return snapshot.docs.map(doc => mapToTransaction(doc));
}
```

### Get All Transactions (Including History)

```typescript
async function getAllTransactions(
  householdId: string
): Promise<Transaction[]> {
  // Include corrected and deleted for audit
  const q = query(
    collection(db, `households/${householdId}/transactions`),
    orderBy('date', 'desc')
  );
  
  const snapshot = await getDocs(q);
  return snapshot.docs.map(doc => mapToTransaction(doc));
}
```

### Get Correction History

```typescript
async function getCorrectionHistory(
  transactionId: string
): Promise<Transaction[]> {
  // Get original + all corrections
  const original = await getTransaction(transactionId);
  const corrections: Transaction[] = [];
  
  let current: Transaction | null = original;
  while (current?.corrected_by_transaction_id) {
    const correction = await getTransaction(current.corrected_by_transaction_id);
    corrections.push(correction);
    current = correction;
  }
  
  return [original, ...corrections];
}
```

---

## Reports Use Live Data

### Budget Report

```typescript
async function generateBudgetReport(
  budgetId: string
): Promise<BudgetReport> {
  const budget = await getBudget(budgetId);
  
  // Only count ACTIVE transactions (latest corrections)
  const transactions = await query(
    collection(db, 'transactions'),
    where('status', '==', 'active'),  // Excludes corrected/deleted
    where('date', '>=', budget.period_start),
    where('date', '<=', budget.period_end)
  );
  
  // Calculate from live data
  const categoryTotals = calculateCategoryTotals(transactions);
  
  return {
    budget_id: budgetId,
    categories: categoryTotals,
    // ... rest of report
  };
}
```

**Result**: Reports always show current truth, not historical mistakes.

---

## Late Entry Behavior Tracking

### Calculate Late Entry Stats

```typescript
interface LateEntryStats {
  total_transactions: number;
  same_day: number;           // capture_delay_days === 0
  within_week: number;        // capture_delay_days <= 7
  late: number;               // capture_delay_days > 7
  very_late: number;          // capture_delay_days > 30
  avg_delay_days: number;
  worst_delay_days: number;
}

async function calculateLateEntryStats(
  householdId: string,
  periodStart: Date,
  periodEnd: Date
): Promise<LateEntryStats> {
  const transactions = await getTransactionsInPeriod(
    householdId,
    periodStart,
    periodEnd
  );
  
  const stats: LateEntryStats = {
    total_transactions: transactions.length,
    same_day: 0,
    within_week: 0,
    late: 0,
    very_late: 0,
    avg_delay_days: 0,
    worst_delay_days: 0,
  };
  
  let totalDelay = 0;
  
  for (const tx of transactions) {
    totalDelay += tx.capture_delay_days;
    
    if (tx.capture_delay_days === 0) {
      stats.same_day++;
    } else if (tx.capture_delay_days <= 7) {
      stats.within_week++;
    } else if (tx.capture_delay_days <= 30) {
      stats.late++;
    } else {
      stats.very_late++;
    }
    
    if (tx.capture_delay_days > stats.worst_delay_days) {
      stats.worst_delay_days = tx.capture_delay_days;
    }
  }
  
  stats.avg_delay_days = totalDelay / transactions.length;
  
  return stats;
}
```

### UI: Late Entry Warning

```typescript
function TransactionListItem({ transaction }: Props) {
  const showWarning = transaction.capture_delay_days > 3;
  
  return (
    <View style={styles.container}>
      <Text>{transaction.payee}</Text>
      <Text>{formatMoney(transaction.amount)}</Text>
      
      {showWarning && (
        <View style={styles.warning}>
          <Icon name="alert" color="orange" />
          <Text>
            Captured {transaction.capture_delay_days} days late
          </Text>
        </View>
      )}
    </View>
  );
}
```

### UI: Late Entry Report

```
┌────────────────────────────────────┐
│ Capture Habits (March 2024)       │
├────────────────────────────────────┤
│                                    │
│ Same Day:      45 (75%)   ███████  │
│ Within Week:   12 (20%)   ██       │
│ Late (>7d):     3  (5%)   █        │
│                                    │
│ Average Delay: 1.2 days            │
│ Worst Delay:   14 days             │
│                                    │
│ 💡 Tip: Capture expenses same-day  │
│    for best budget accuracy!       │
└────────────────────────────────────┘
```

---

## Advantages

### 1. Financial Integrity ✅

```
Original:  2024-03-05  $100.00  Groceries
          ↓ (Oops, was $120!)
Correction: 2024-03-05  $120.00  Groceries (Corrects original)

Reports show: $120 (correct)
Audit trail: Can see original $100 + correction
```

### 2. Behavior Tracking ✅

```
User captures expenses:
- Mar 1:  Same day     ✓
- Mar 5:  Same day     ✓
- Mar 12: 7 days late  ⚠️
- Mar 20: 14 days late ⚠️⚠️

App shows: "You're capturing 20% of expenses late. Try recording same-day!"
```

### 3. Audit Trail ✅

```typescript
// Can always reconstruct history
const history = await getCorrectionHistory(txId);
console.log(history);
// [
//   { amount: 10000, status: 'corrected', date: '2024-03-05' },
//   { amount: 12000, status: 'active', date: '2024-03-05', corrects: txId }
// ]
```

### 4. Compliance ✅

For business expenses or tax audits:
- Full history available
- Can prove original entry + corrections
- Timestamps on everything
- Device tracking for security

---

## Edge Cases

### Edge Case 1: Multiple Corrections

```typescript
Original:  $100  (corrected)
Correction 1: $120  (corrected)
Correction 2: $125  (active)  ← This is current

// Query returns only $125 (active)
// But audit trail has all three
```

### Edge Case 2: Delete Correction

```typescript
// User corrects, then deletes correction
Original:  $100  (corrected)
Correction: $120  (deleted)

// Result: Original restored to active
Original:  $100  (active)  ← Back to this
```

### Edge Case 3: Back-Dated Entry in Closed Month

```typescript
// April 15: User adds transaction from March 10
// March budget already closed

const transaction = {
  date: Timestamp.fromDate(new Date('2024-03-10')),
  captured_at: Timestamp.fromDate(new Date('2024-04-15')),
  capture_delay_days: 36,  // Very late!
};

// Check if affects closed budget
const budget = await getBudgetForDate(transaction.date);
if (budget.status === 'closed') {
  showWarning(
    'This transaction is in a closed month. ' +
    'Adding it will change historical reports. Continue?'
  );
}
```

---

## Disadvantages

### 1. More Complex Queries ⚠️

```typescript
// Must always filter by status
const transactions = await query(
  collection(db, 'transactions'),
  where('status', '==', 'active')  // Don't forget this!
);

// Mitigation: Use helper functions that include filter
```

### 2. More Storage ⚠️

```typescript
// Keep all corrections + originals
// Storage grows faster

// Typical transaction: ~500 bytes
// 10,000 transactions/year = 5 MB
// With 10% corrections = 5.5 MB
// Negligible cost

// Mitigation: Archive old data after 5+ years
```

### 3. UI Complexity ⚠️

```typescript
// Must handle correction history in UI
// "Show original" link
// "View correction history"

// Mitigation: Hide by default, show on request
```

---

## Alternatives Considered

### Alternative 1: Full Edit (Rejected) ❌

Allow editing any field anytime.

**Pros**:
- Simple UI
- Simple code
- Users can fix mistakes easily

**Cons**:
- ❌ No audit trail
- ❌ Can't track late entries
- ❌ Can't prove compliance
- ❌ Reports can be retroactively changed

**Verdict**: Unacceptable for financial app

---

### Alternative 2: Immutable Forever (Rejected) ❌

Never allow any edits.

**Pros**:
- Perfect audit trail
- Simple to implement
- No correction logic

**Cons**:
- ❌ Terrible UX (can't fix typos)
- ❌ Forces workarounds (delete + recreate)
- ❌ Users frustrated

**Verdict**: Too rigid

---

### Alternative 3: Version History (Rejected) ⚠️

Keep version history in subcollection.

```typescript
// Main transaction (current version)
transactions/{txId}

// Version history
transactions/{txId}/versions/{versionId}
```

**Pros**:
- Full history
- Clean main collection

**Cons**:
- ⚠️ More complex queries (need to join)
- ⚠️ Must query subcollection for history
- ⚠️ Firestore limitations on subcollection queries

**Verdict**: More complex than append-only, no benefit

---

## Success Metrics

We will know this approach works if:

1. ✅ Users can correct mistakes easily
2. ✅ Full audit trail maintained
3. ✅ Late entry behavior tracked accurately
4. ✅ Reports always show current data
5. ✅ No data integrity issues
6. ✅ Compliance requirements met
7. ✅ <1% of transactions have corrections

---

## References

- [Event Sourcing Pattern](https://martinfowler.com/eaaDev/EventSourcing.html)
- [Append-Only Data Structures](https://en.wikipedia.org/wiki/Append-only)
- [Financial Data Integrity](https://www.pcisecuritystandards.org/)

---

## Decision Log

- **2024-12-11**: Decided on append-only with corrections
- **2024-12-11**: Decided to track late entries via capture_delay_days
- **2024-12-11**: Decided on soft deletes (never hard delete)

---

## Notes

This approach balances:
- **User needs**: Can fix mistakes
- **Business needs**: Audit trail for compliance
- **Product needs**: Track behavior to improve habits

The key insight: **Separation of concerns**
- Transaction data (amount, date, account) = append-only
- Capture behavior (when entered) = separate tracking
- Display data (mutable fields like notes) = can edit

This gives us the best of both worlds: integrity + usability.

