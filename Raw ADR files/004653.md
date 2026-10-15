# ADR-003: Expo Router for Navigation

Status: Accepted
Date: 2025-12-18
Owner: User
Related Features: All screens
Supersedes: N/A
Superseded by: N/A

---

## Context

We need a navigation solution for a mobile photo gallery app with:
- Tab-based navigation for main sections (Photos, Cloud, Settings)
- Stack navigation for photo viewer
- Deep linking support (future: share links to photos)
- Type-safe routing
- Web compatibility (optional but nice-to-have)

---

## Decision

Use **Expo Router** with file-based routing.

Route structure:
```
app/
├── (tabs)/
│   ├── _layout.tsx     # Tab navigator
│   ├── index.tsx       # Device Photos (default tab)
│   ├── cloud.tsx       # Cloud Photos
│   └── settings.tsx    # Settings
├── viewer.tsx          # Photo viewer (modal/stack)
├── _layout.tsx         # Root layout
└── +not-found.tsx      # 404 page
```

Key points:
- File-based routing (Next.js-style)
- Type-safe with auto-generated types
- Built on React Navigation under the hood
- Shared layouts for common UI

---

## Alternatives considered

### React Navigation (direct)

- Pros: Most popular, full control, well-documented
- Cons: Manual route configuration, no auto-generated types, more boilerplate
- Rejected because: Expo Router builds on it with better DX

### React Native Navigation (Wix)

- Pros: Native navigation performance
- Cons: Complex setup, not compatible with Expo Go, overkill for this app
- Rejected because: Complexity not justified for photo gallery

### Custom navigation

- Pros: Full control, minimal dependencies
- Cons: Reinventing the wheel, no deep linking, no type safety
- Rejected because: Not worth the effort

---

## Consequences

### Positive

- File-based routing is intuitive (folder = route)
- Type-safe navigation with auto-generated types
- Deep linking works out of the box
- Web support available if needed
- Expo ecosystem integration
- Less boilerplate than React Navigation

### Negative / risks

- Locked into Expo ecosystem
- Younger than React Navigation (less battle-tested)
- File structure determines routes (less flexible)
- Mitigation: Expo Router is built on React Navigation, fallback is possible

---

## Impact

### Code

- Route structure: `app/` folder defines all routes
- Navigation: Use `router.push()` and `Link` components
- Layouts: Shared UI defined in `_layout.tsx` files
- Params: Type-safe with `useLocalSearchParams<T>()`

### Data / configuration

- Route types: Auto-generated in `.expo-router/` (gitignored)
- Deep links: Configured in `app.json` under `scheme`

### Documentation

- Route map: Self-documenting via file structure
- Navigation patterns: Use router.push for programmatic, Link for declarative

---

## Verification

### Test environment

- Environment: Android emulator, iOS simulator
- Routes: All routes accessible via file system

### Test flows

| ID | Scenario | Level | Expected result | Notes |
| --- | --- | --- | --- | --- |
| TST-001 | Navigate between tabs | Device | Tabs switch instantly | Bottom tab bar |
| TST-002 | Open photo viewer | Device | Photo displays full-screen | Modal transition |
| TST-003 | Back navigation | Device | Returns to previous screen | Hardware back button |
| TST-004 | Deep link to viewer | Device | Opens specific photo | Test with custom URI |

---

## References

- Expo Router docs: https://docs.expo.dev/router/introduction/
- React Navigation: https://reactnavigation.org/
- Route structure: app/ directory
