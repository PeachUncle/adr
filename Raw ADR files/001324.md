# ADR-026: State Management

## Status

Accepted

## Context

The project requires a scalable and predictable state management solution that
supports complex UI interactions, asynchronous operations, and global state
sharing across components. The solution must integrate well with React and
TypeScript, minimize boilerplate, and encourage maintainable state architecture.

Several state management solutions were evaluated, including React Context API,
Zustand, MobX, and Redux Toolkit.

## Decision

We decided to use **Redux Toolkit (RTK)** from `@reduxjs/toolkit` as the primary
state management solution.

## Reasons

1. **Standardized Redux Patterns**:
   - Redux Toolkit provides a recommended and modernized approach to using
     Redux, enforcing best practices by default and reducing boilerplate.

2. **Powerful DevTools Integration**:
   - Out-of-the-box support for Redux DevTools enables time-travel debugging and
     insight into state transitions.

3. **TypeScript Support**:
   - Built-in TypeScript support simplifies typing for actions, reducers,
     thunks, and selectors, improving maintainability and DX.

4. **Built-in Async Support**:
   - `createAsyncThunk` makes it easy to handle async logic and loading/error
     states in a consistent, scalable way.

5. **Scalability**:
   - RTK scales well for both small components and large applications with
     complex, shared, or nested state.

6. **Community and Ecosystem**:
   - Redux remains one of the most widely adopted and well-supported state
     management libraries in the React ecosystem.

7. **Integration with React**:
   - RTK works seamlessly with `react-redux`, and hooks-based APIs like
     `useSelector` and `useDispatch` align with modern React patterns.

8. **Tooling and Middleware**:
   - Middleware like `redux-thunk` is included by default, and it’s easy to add
     logging, persistence, or API middleware (e.g. RTK Query).

## Consequences

1. **Learning Curve**:
   - Developers unfamiliar with Redux concepts (e.g., reducers, actions,
     normalization) may need time to ramp up, despite RTK’s simplifications.

2. **Boilerplate vs Simpler Alternatives**:
   - Even with RTK, there is still more structure and boilerplate than
     alternatives like Zustand or useReducer for smaller apps.

3. **Initial Setup Overhead**:
   - Requires setting up slices, a store, provider configuration, and
     potentially RTK Query if used.

## Alternatives Considered

### Zustand:

- **Pros**: Minimalistic, hooks-based, very easy to set up and use.
- **Cons**: Less structure and tooling; can lead to inconsistency in large
  codebases.

### React Context + useReducer:

- **Pros**: Native to React, no additional dependencies.
- **Cons**: Not optimized for large-scale or deeply nested state; poor
  devtools support.

### MobX:

- **Pros**: Reactive paradigm with minimal boilerplate.
- **Cons**: Less predictable, harder to debug, and diverges from mainstream
  patterns.
