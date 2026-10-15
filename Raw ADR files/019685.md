---
id: ADR-0008
created: 2025-04-02
decision_date: 2025-04-02
last_updated: 2025-04-02
status: Accepted
summary: Adopt Redux Toolkit as the sole state management system with cascade-aware persistence support
---

# ADR-0008: Adopt Redux Toolkit as the sole state management system with cascade-aware persistence support

## Context

- Our frontend application currently uses a mix of **React Context** and **local state** to manage user session, chat
  messages, UI selections, and other features.
- This approach has led to **difficulty synchronizing state** across different parts of the app, **stale reads**, and \*
  \*complex debugging\*\*.
- As the application grows in complexity and team size, we need a **single, consistent, scalable, and debuggable** way
  to manage application state.

## Problem Framing (Clarified)

- State transitions (e.g., updating profile, sending a chat message) require **synchronous and predictable updates**.
- **React Context** is not designed for dynamic, cross-feature, deeply nested or async-updated state.
- Mixing Context and Redux adds **cognitive load** and reduces maintainability.
- The application will require **persistent state** across sessions and possibly across devices (e.g. inventory,
  preferences).
- A **migration path** is needed to move from `local` to `global` (backend) storage without losing local user data.

## Decision Drivers

- **Consistency** – Single mental model and source of truth
- **Predictability** – State changes are traceable and auditable
- **Scalability** – Suitable for increasingly complex and asynchronous workflows
- **Debuggability** – Built-in support for Redux DevTools
- **Developer Velocity** – Easier for backend-oriented developers to reason about
- **Persistence Support** – Enables local and remote data durability across sessions and users
- **Migration Resilience** – Graceful evolution of persisted formats and storage targets

## Mental Models & Techniques Used

- **KISS** – Avoid two overlapping state systems
- **Cognitive Load Theory** – Reduce complexity by eliminating dual paradigms
- **Second-Order Thinking** – Design for scale now to avoid painful refactors later
- **Opportunity Cost** – Avoid wasting time rewriting context logic later
- **Heuristic Audit** – Identify state areas with highest coupling and persistence needs

## Alternatives Considered

1. **React Context + Redux (Mixed)**

   - **Pros**: Optimized for simple UI-local state
   - **Cons**: Inconsistent architecture, harder to debug, higher switching cost later
   - **Rejected**: Adds complexity and technical debt

2. **React Context Only**

   - **Pros**: Lightweight for very small apps
   - **Cons**: Not suitable for shared, async, or derived state; no tooling
   - **Rejected**: Breaks under real-world complexity

3. **Redux Toolkit Only**
   - **Pros**: Consistent, well-documented, scalable, devtools-ready
   - **Cons**: Slightly more boilerplate upfront (solved by Redux Toolkit)
   - **✅ Chosen**

## Decision

We will use **Redux Toolkit** as the **sole state management solution** across the application, replacing all existing
React Contexts (except theme providers if needed). In addition, we will design a **Persistence Layer** to persist
specific Redux slices to **LocalStorage** initially, and to a **backend API** later, with a mechanism to cascade and
migrate between storage layers without losing local state.

## Trade-offs & Consequences

### Positive Outcomes

- Single paradigm for all developers
- Scalable architecture from day one
- DevTools support
- Simplified testing and debugging
- Better action-based event modeling
- Persistence layer supports cross-session UX improvements
- Cascade strategy ensures backward-compatible upgrade paths

### Negative Outcomes

- Slight learning curve for Redux newcomers
- Small UI-only state becomes slightly verbose
- Requires version/migration handling to ensure schema compatibility

### Unresolved Questions

- May revisit lightweight solutions like Zustand for micro-apps, but not for current architecture

## Implementation Plan

1. **Install Redux Toolkit & React-Redux**

   \`\`\`bash
   npm install @reduxjs/toolkit react-redux
   \`\`\`

2. **Create Global Store**

   \`\`\`ts
   // app/store.ts
   import { configureStore } from '@reduxjs/toolkit';
   import userProfileReducer from '../features/userProfile/userProfileSlice';
   import chatReducer from '../features/chat/chatSlice';

   export const store = configureStore({
     reducer: {
       userProfile: userProfileReducer,
       chat: chatReducer,
     },
   });

   export type RootState = ReturnType<typeof store.getState>;
   export type AppDispatch = typeof store.dispatch;
   \`\`\`

3. **Provide Store to App**

   \`\`\`tsx
   import { Provider } from 'react-redux';
   import { store } from './app/store';

   <Provider store={store}>
     <App />
   </Provider>;
   \`\`\`

4. **Slice Example: userProfileSlice.ts**

   \`\`\`ts
   import { createSlice, PayloadAction } from '@reduxjs/toolkit';

   interface UserProfileState {
     name: string;
     preferredLanguage: string;
   }

   const initialState: UserProfileState = {
     name: '',
     preferredLanguage: 'en',
   };

   const userProfileSlice = createSlice({
     name: 'userProfile',
     initialState,
     reducers: {
       setProfile(state, action: PayloadAction<UserProfileState>) {
         return action.payload;
       },
       updateLanguage(state, action: PayloadAction<string>) {
         state.preferredLanguage = action.payload;
       },
     },
   });

   export const { setProfile, updateLanguage } = userProfileSlice.actions;
   export default userProfileSlice.reducer;
   \`\`\`

5. **Use in Component**

   \`\`\`tsx
   const dispatch = useDispatch<AppDispatch>();
   const userProfile = useSelector((state: RootState) => state.userProfile);

   useEffect(() => {
     dispatch(updateLanguage('pl'));
   }, []);
   \`\`\`

6. **Design Persistence Layer**
   - Create a `StorageAdapter` interface to support both local and backend storage.
   - Tag slices with persistence level: `none`, `local`, `global`
   - Middleware inspects actions and triggers read/write to correct storage layer
   - Store version alongside persisted data
   - Add migration logic per slice for version upgrades
   - Example:
   \`\`\`ts
   interface StorageAdapter {
     save: (key: string, data: unknown, version: number) => void;
     load: (key: string) => { version: number; data: unknown } | null;
   }
   \`\`\`

## Verification Criteria

- All application state lives in Redux slices
- DevTools inspection is possible for all state changes
- No logic remains in React Context except theme/localization wrappers (if needed)
- Verified by migrating userProfile and chat states first, then progressively others
- Persistence layer supports saving/loading selective state with version support and migration fallback

## Confidence Rating

**High** – Based on industry best practices, strong internal experience, and future maintainability

## Lessons Learned (Retrospective)

To be added after full migration and first feature iteration

## Examples & Usage (Optional)

See implementation plan for concrete examples of `createSlice`, `configureStore`, and persistence layer abstraction

## References

- https://redux-toolkit.js.org/
- https://react-redux.js.org/
- https://github.com/rt2zz/redux-persist
- Previous internal decisions: N/A
