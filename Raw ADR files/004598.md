# ADR 003: How Vote Tracking Works (votedBy Array)

**Date**: 2025-11-21
**Status**: Accepted
**Deciders**: Development Team

## Context

**Feature**: Secret tasks reveal after 2 unique users vote.

**Original Bug** (from brief):
```typescript
task: {
  revealVotes: number  // ❌ WRONG: Can't track WHO voted
}
```

**Problem**: Same user could click "Reveal" twice and trigger reveal.

## Decision

Track **who voted** using an array of user IDs:

```typescript
task: {
  votedBy: string[]  // ✅ Array of user UUIDs
}
```

## Rationale

### Why Array of User IDs

**Scenario WITHOUT votedBy**:
```
User A creates secret task { revealVotes: 0 }
User A clicks Reveal       { revealVotes: 1 }
User A clicks again        { revealVotes: 2 }  ← ❌ REVEALED!
```

**Scenario WITH votedBy**:
```
User A creates secret task { votedBy: [] }
User A clicks Reveal       { votedBy: ['user-a-uuid'] }
User A clicks again        { votedBy: ['user-a-uuid'] }  ← ✅ DUPLICATE IGNORED
User B clicks Reveal       { votedBy: ['user-a-uuid', 'user-b-uuid'] }  ← ✅ REVEALED!
```

### Implementation

**Contract** (`task.contract.ts`):
```typescript
votedBy: z.array(z.string().uuid()).max(10)
```

**Helper** (computed property):
```typescript
export const taskIsRevealed = (task: Task): boolean =>
  task.votedBy.length >= 2;
```

**Service Logic** (`task.service.ts`):
```typescript
async voteReveal(taskId: string): Promise<void> {
  const user = await this.authProvider.currentUser();
  const task = this.tasks().find(t => t.id === taskId);

  // Prevent duplicate votes
  if (!task.votedBy.includes(user.id)) {
    task.votedBy.push(user.id);
    await this.updateTask(task);
  }
}
```

**Sync Message**:
```typescript
{
  type: 'VOTE_REVEAL',
  payload: {
    taskId: 'task-uuid',
    userId: 'user-uuid'  // ← Who voted
  }
}
```

## Consequences

### Positive
- ✅ **Prevents cheating**: Same user can't reveal alone
- ✅ **Auditable**: Know exactly who voted
- ✅ **Future-proof**: Can add "Voted by: Alice, Bob" UI
- ✅ **Max limit**: Array capped at 10 (prevents abuse)

### Negative
- ⚠️  Slightly more storage (array vs number)
- ⚠️  Must dedupe votes (check `includes()` before adding)

## Sync Behavior

**User A votes**:
1. User A clicks "Reveal"
2. TaskService adds A's UUID to `votedBy`
3. TaskService publishes VOTE_REVEAL sync message
4. User B receives sync message
5. User B's TaskService adds A's UUID (if not present)
6. Both see "1/2 votes"

**User B votes** (reveal threshold reached):
1. User B clicks "Reveal"
2. TaskService adds B's UUID to `votedBy`
3. `votedBy.length === 2` → `taskIsRevealed() === true`
4. TaskService publishes VOTE_REVEAL sync message
5. User A receives sync message, adds B's UUID
6. Both see revealed content with fade-in animation

**User C joins later** (after reveal):
1. User C opens `/s/ABC123`
2. TaskService loads tasks from TaskStore
3. Task has `{ votedBy: ['a-uuid', 'b-uuid'] }`
4. `taskIsRevealed()` returns `true` immediately
5. User C sees content (no mask icon)

## Edge Cases Handled

### Same User, Multiple Tabs
```
User A Tab 1: Clicks reveal → votedBy: ['a-uuid']
User A Tab 2: Clicks reveal → votedBy: ['a-uuid']  ← Duplicate ignored
```

### Late Voter (Already Revealed)
```
Task: { votedBy: ['a', 'b'] }  ← Already revealed
User C: Clicks reveal → votedBy: ['a', 'b', 'c']
No change in UI (already visible)
```

### Deleted User Vote
```
Future enhancement: Remove deleted user IDs from votedBy
For now: Voting continues to work (dead votes don't prevent reveal)
```

## Alternatives Considered

### 1. Track Vote Count Only
```typescript
revealVotes: number
```
**Rejected**: Can't prevent duplicate votes from same user.

### 2. Separate Votes Table
```typescript
votes: { taskId, userId, timestamp }[]
```
**Rejected**: Overkill for simple feature, adds complexity.

### 3. Set<string> Instead of Array
```typescript
votedBy: Set<string>
```
**Rejected**: Zod doesn't have native Set schema, arrays work fine.

### 4. Map of Votes with Timestamps
```typescript
votes: { [userId: string]: timestamp }
```
**Rejected**: Don't need timestamps (yet), YAGNI principle.

## Testing

**Contract Test**:
```typescript
it('validates votedBy array', () => {
  const task = { ...mockTask, votedBy: ['uuid-1', 'uuid-2'] };
  expect(() => TaskSchemaV1.parse(task)).not.toThrow();
});
```

**Service Test**:
```typescript
it('prevents duplicate votes', async () => {
  await service.voteReveal('task-1');
  await service.voteReveal('task-1');  // ← Same user
  const task = service.tasks().find(t => t.id === 'task-1');
  expect(task.votedBy).toEqual(['user-uuid']);  // ← Only once
});
```

**E2E Test**:
```typescript
it('requires 2 unique votes', async () => {
  await page1.click('[data-testid="reveal-btn"]');  // User 1
  await expect(page1.locator('text=1/2')).toBeVisible();

  await page1.click('[data-testid="reveal-btn"]');  // User 1 again
  await expect(page1.locator('text=1/2')).toBeVisible();  // ← Still 1

  await page2.click('[data-testid="reveal-btn"]');  // User 2
  await expect(page1.locator('text=Secret content')).toBeVisible();  // ← Revealed!
});
```

## References

- [Array.prototype.includes()](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/includes)
- [Zod array schema](https://zod.dev/?id=arrays)
