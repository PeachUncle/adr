## Context
The application presently fetches 100% of history on startup. With NIP-59 (Gift Wrap) encryption, this involves heavy cryptographic work for every message. Doing this in one large blocking operation degrades user experience.

## Goals
- **Immediate Interactivity**: The user should see recent messages and be able to type immediately on startup.
- **Efficient Sync**: Only download what is missing.
- **Smooth Scrolling**: UI should handle thousands of messages without DOM lag.

## Decisions

### Pipeline Processing
Instead of `Fetch All -> Decrypt All -> Save All`, we will use a pipeline:
`Fetch Batch (N=50) -> Decrypt/Filter -> Save -> Update UI -> Fetch Next Batch`.
This ensures that if the app is closed or crashes, partial progress is saved.

### Checkpointing Strategy
We will use a "Gap Detection" strategy.
- We fetch backwards from `now`.
- If a fetched batch contains 100% known messages (already in DB), we assume we have reached the locally stored history and stop fetching.
- **Risk**: If there is a "hole" in the local history (e.g., failed write in the past), we might stop early.
- **Mitigation**: We can allow a "tolerance" (e.g., stop only after 2 consecutive batches of duplicates) or provide a "Full Resync" button in settings for repair. For this iteration, a simple "stop on full batch duplicate" is sufficient.

### Pagination vs LiveQuery
`Dexie.js` `liveQuery` is excellent for reactivity but tricky with infinite scroll (loading *more* data into the same reactive array).
- **Decision**: We will keep `liveQuery` for the *recent* window (e.g., last 50 messages) to handle incoming real-time messages.
- For *older* history (scrolled into view), we will perform one-off `db.toArray()` queries and prepend them to the UI list.
- This creates a hybrid model: "Live Tail" + "Static Head".

## Risks
- **Scroll Jumps**: Prepending items to a scrolled container often causes the scrollbar to jump.
- **Mitigation**: We must capture `scrollHeight` before prepend and adjust `scrollTop` immediately after render to maintain visual position.
