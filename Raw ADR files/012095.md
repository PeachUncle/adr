# Component Directory Structure

- **Status:** Accepted
- **Date:** 2024-11-18

## Context

A clear and professional component directory structure is essential for the Spotify client application, which is built using React and TypeScript. The structure should support scalability, maintainability, and modularity, ensuring the application is easy to extend and navigate.

Key considerations:

1. Components should be modular and reusable.
2. Separation of concerns should be maintained between pages, shared components, and specific features.
3. The structure should align with industry best practices and support growth as the app evolves.

## Decision

The project will adopt the following directory structure for components:

```
src/
├── components/          # Reusable components
│   ├── common/          # General-purpose UI components
│   │   ├── Button/
│   │   │   ├── Button.tsx
│   │   │   ├── Button.test.tsx
│   │   │   └── Button.module.css
│   │   ├── Modal/
│   │   │   ├── Modal.tsx
│   │   │   ├── Modal.test.tsx
│   │   │   └── Modal.module.css
│   ├── layout/          # Layout components (e.g., Header, Footer)
│   │   ├── Header/
│   │   │   ├── Header.tsx
│   │   │   ├── Header.test.tsx
│   │   │   └── Header.module.css
│   │   └── Footer/
│   │       ├── Footer.tsx
│   │       ├── Footer.test.tsx
│   │       └── Footer.module.css
│   ├── spotify/         # Spotify-specific components
│   │   ├── PlaylistCard/
│   │   │   ├── PlaylistCard.tsx
│   │   │   ├── PlaylistCard.test.tsx
│   │   │   └── PlaylistCard.module.css
│   │   ├── TrackRow/
│   │   │   ├── TrackRow.tsx
│   │   │   ├── TrackRow.test.tsx
│   │   │   └── TrackRow.module.css
├── features/            # Redux slices and feature-specific logic
│   ├── auth/            # Authentication state management
│   │   ├── authSlice.ts
│   │   ├── authActions.ts
│   │   ├── authSelectors.ts
│   │   └── authTypes.ts
│   ├── playlist/        # Playlist-specific logic
│   │   ├── playlistSlice.ts
│   │   ├── playlistActions.ts
│   │   ├── playlistSelectors.ts
│   │   └── playlistTypes.ts
├── hooks/               # Custom hooks
│   ├── useAuth.ts       # Authentication hooks
│   ├── useSpotifyAPI.ts # React Query hooks for Spotify API
│   └── useRedux.ts      # Typed hooks for Redux (e.g., `useAppDispatch`, `useAppSelector`)
├── pages/               # Application pages mapped to routes
│   ├── Home/
│   │   ├── Home.tsx
│   │   ├── Home.test.tsx
│   │   └── Home.module.css
│   ├── Login/
│   │   ├── Login.tsx
│   │   ├── Login.test.tsx
│   │   └── Login.module.css
│   ├── Playlist/
│   │   ├── Playlist.tsx
│   │   ├── Playlist.test.tsx
│   │   └── Playlist.module.css
├── services/            # API services
│   ├── spotifyAPI.ts    # API calls encapsulated (e.g., fetchPlaylist, fetchUser)
│   └── authAPI.ts       # API calls for authentication
├── store/               # Redux store configuration
│   ├── store.ts         # Redux store setup
│   ├── rootReducer.ts   # Combined reducers
│   └── middleware.ts    # Custom middleware (if any)
├── types/               # TypeScript interfaces and types
│   ├── spotify.d.ts     # Spotify-specific types (e.g., Playlist, Track)
│   └── auth.d.ts        # Authentication-specific types
├── App.tsx              # Root component
└── main.tsx             # Entry point (bootstrapped by Vite)
```

---

### **Key Directories**

1. **`components/`**

   - Organized into **common**, **layout**, and **spotify** directories.
   - Promotes reusability and clarity by grouping components based on functionality.

2. **`features/`**

   - Redux-related logic is grouped by feature (e.g., `auth`, `playlist`).
   - Each feature folder includes slices, actions, selectors, and types.

3. **`hooks/`**

   - Houses custom hooks, including **React Query hooks** (`useSpotifyAPI`) and **typed Redux hooks** (`useAppDispatch`, `useAppSelector`).

4. **`pages/`**

   - Maps to application routes, ensuring a clean separation of concerns for page-level logic.

5. **`services/`**

   - Encapsulates API calls, keeping data-fetching logic separate from components.

6. **`store/`**

   - Centralizes Redux store configuration and middleware.

---

## Consequences

### **Positive**

- **Scalability:** The structure accommodates growth by cleanly separating shared and specific components.
- **Reusability:** Encourages the creation of modular, reusable components.
- **Maintainability:** Improves code organization and readability for future updates.

### **Negative**

- May involve slightly more boilerplate (e.g., directories and files for each component), but this is offset by the benefits of a modular structure.

## Alternatives Considered

1. **Flat Structure:** Placing all components in a single folder.
   - **Pros:** Simplicity for very small projects.
   - **Cons:** Becomes unmanageable as the app grows.
2. **Feature-Based Structure:** Organizing by features instead of shared/common.
   - **Pros:** Works well for feature-heavy applications.
   - **Cons:** Reduces reusability across unrelated features.

---

## Status and Next Steps

This directory structure will be implemented immediately. All existing and new components will conform to this organization.
