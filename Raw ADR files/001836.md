# ADR-003: React Native with Expo for Mobile Apps

## Status

Accepted

## Date

2025-10-01 (Pre-M1 Planning)

## Context

Need to support mobile applications (iOS and Android) after web app is complete.

Constraints:

- Solo developer with React/TypeScript experience
- Limited budget (personal project)
- Want to maximize code reuse from web app
- Need to deliver both iOS and Android
- Timeline: Mobile app should follow web app within reasonable time

Requirements:

- Cross-platform (iOS + Android from one codebase)
- Type safety (TypeScript)
- Can reuse backend API and shared types
- Good developer experience (hot reload, debugging)
- Mature ecosystem and community support

## Decision

Use **React Native with Expo** for mobile development.

**Why Expo specifically:**

- Managed workflow (no Xcode/Android Studio needed for most development)
- Over-the-air updates
- Easy native module integration with Expo SDK
- Simplified build and deployment (EAS Build)
- Can eject to bare React Native if needed

## Alternatives Considered

### Alternative 1: Flutter

- **Pros**:
  - Excellent performance (compiles to native code)
  - Beautiful UI components out of the box (Material + Cupertino)
  - Hot reload
  - Single codebase for iOS/Android/Web
  - Great for complex animations
  - Growing community
- **Cons**:
  - **New language**: Dart (not TypeScript)
  - **Zero code reuse**: Can't use React components, hooks, or TypeScript types
  - **Rewrite validation**: Can't use Zod schemas, need to rewrite in Dart
  - **Smaller ecosystem**: Fewer packages than React Native
  - **Learning curve**: 1-2 months to become proficient
- **Why rejected**: Can't leverage existing React knowledge. Would need to rewrite all validation logic, API client, and learn a new language. For a solo developer, this adds 2-3 months to timeline.

### Alternative 2: Native (Swift for iOS + Kotlin for Android)

- **Pros**:
  - Best performance (truly native)
  - Full access to platform APIs (day-one access to new features)
  - Best UX (platform-native look and feel)
  - Largest communities (iOS and Android)
- **Cons**:
  - **Build everything twice**: Separate codebases for iOS and Android
  - **Learn two languages**: Swift + Kotlin
  - **2x development time**: Every feature implemented twice
  - **2x maintenance**: Fix bugs in both codebases
  - **Zero UI code reuse**: Different UI frameworks (SwiftUI vs Jetpack Compose)
- **Why rejected**: Not feasible for solo developer. Would take 6+ months to build what React Native can do in 2 months. Can't reuse any web code.

### Alternative 3: Progressive Web App (PWA)

- **Pros**:
  - **100% code reuse**: Just use the web app
  - Works on all platforms
  - No app store approval needed
  - Easy updates (just deploy)
- **Cons**:
  - Limited native features (notifications less reliable, no home screen by default)
  - Slower than native apps
  - No App Store/Play Store presence (less discoverable)
  - Can't use native UI components
  - iOS PWA support is limited
- **Why rejected**: Not a true mobile app. Push notifications are unreliable, no offline support for core features, and lacks native feel. For a resume project, "built a PWA" is less impressive than "built native mobile apps."

### Alternative 4: Ionic (Web technologies in WebView)

- **Pros**:
  - Use web technologies (HTML/CSS/JS)
  - Can reuse some React components
  - Cross-platform
- **Cons**:
  - Performance issues (WebView overhead)
  - Doesn't feel native
  - Ionic-React is less popular than React Native
  - Hybrid approach has worst of both worlds
- **Why rejected**: Performance and UX inferior to React Native. If using JavaScript anyway, React Native is better choice.

## Consequences

### Positive

- ✅ **40% code reuse**: Shared types, schemas, API client, validation logic
- ✅ **Same language**: TypeScript across backend, web, and mobile
- ✅ **React knowledge transfers**: Hooks, component patterns, state management
- ✅ **Fast development**: 2-3 months for mobile vs 6+ months for native
- ✅ **Hot reload**: Fast iteration during development
- ✅ **Large ecosystem**: 1000+ libraries, most problems already solved
- ✅ **React Query works**: Can use same data-fetching strategy as web
- ✅ **One developer**: Solo developer can handle web + mobile
- ✅ **Over-the-air updates**: Fix bugs without App Store review (with Expo)

### Negative

- ❌ **Can't reuse React components**: Web components don't work on mobile (DOM vs native views)
- ❌ **Different styling**: Can't use TailwindCSS directly (need NativeWind or RN stylesheets)
- ❌ **Performance gap**: Not as fast as native Swift/Kotlin
- ❌ **Platform-specific code**: Some features need separate iOS/Android implementations
- ❌ **Larger app size**: ~30-50MB vs ~5-10MB for native
- ❌ **Bridge overhead**: JavaScript-native communication has slight latency

### Neutral

- ℹ️ **Expo limitations**: Some native modules require ejecting (rare in practice)
- ℹ️ **Update frequency**: React Native updates can sometimes break things

## Implementation Notes

**Code Reuse Breakdown:**

```
✅ Backend API (100% reuse)
   - Same REST endpoints
   - Same JSON responses
   - Same authentication flow

✅ Shared Package (100% reuse)
   - TypeScript types
   - Zod validation schemas
   - Currency enums, constants

✅ API Client Logic (90% reuse)
   - Axios setup
   - Request/response interceptors
   - Error handling
   - Only difference: token storage (AsyncStorage vs localStorage)

✅ Business Logic (80% reuse)
   - Form validation
   - Data transformations
   - Utility functions

❌ UI Components (0% reuse)
   - Web: React + TailwindCSS
   - Mobile: React Native components + NativeWind/StyleSheet

❌ Navigation (0% reuse)
   - Web: React Router
   - Mobile: React Navigation

❌ Storage (0% reuse, but same API)
   - Web: localStorage
   - Mobile: AsyncStorage (same interface)
```

**Future Monorepo Structure:**

```
forex-watch/
├── apps/
│   ├── backend/
│   ├── web/           (renamed from frontend)
│   └── mobile/        (React Native + Expo)
├── packages/
│   ├── shared/        (types + schemas - ALL platforms)
│   ├── api-client/    (web + mobile reuse)
│   └── utils/         (pure TypeScript functions)
```

**Tech Stack for Mobile:**

- React Native + Expo
- TypeScript
- React Navigation (routing)
- React Query (data fetching)
- NativeWind (Tailwind for React Native) OR StyleSheet
- react-native-keychain (secure token storage)
- Expo Notifications (push notifications)

**Native Features Needed:**

- Push notifications (replace email alerts)
- Secure storage (tokens)
- Biometric auth (optional enhancement)
- Deep linking (from email to app)

## Interview Talking Points

1. **"Why React Native over Flutter?"**
   - Answer: Time and code reuse. I already had a React web app with TypeScript types and Zod validation schemas. React Native lets me reuse ~40% of that code - all my domain logic, API client, and type definitions. Flutter would mean rewriting everything in Dart. For a solo developer, React Native cuts mobile development time from 6 months to 2 months while leveraging my existing React knowledge.

2. **"What code did you actually reuse?"**
   - Answer: The entire `@forex-watch/shared` package - TypeScript types, Zod schemas, currency enums. My API client logic - Axios setup, interceptors, error handling. All business logic - validation functions, data transformations. What I couldn't reuse: UI components (DOM vs native views) and styling (Tailwind doesn't work on mobile). I used NativeWind to get a similar experience.

3. **"What about performance?"**
   - Answer: React Native isn't as fast as native Swift/Kotlin, but it's more than sufficient for my use case. Forex Watch is CRUD-heavy, not compute-intensive. No 60fps animations, no real-time video processing. The performance bottleneck is network requests, not the framework. If this were a game or video editor, I'd choose native. But for a form-based app, React Native's performance is excellent and the development speed gain is worth it.

4. **"Why Expo instead of bare React Native?"**
   - Answer: Expo provides a managed workflow that eliminates most native build complexity. I get push notifications, secure storage, camera access, etc. without opening Xcode/Android Studio. EAS Build handles builds in the cloud. Over-the-air updates let me fix bugs without App Store review. I can eject to bare React Native if needed, but Expo's limitations rarely affect typical apps. The DX improvement is massive.

5. **"What was challenging about React Native?"**
   - Answer: Styling is different from web. No CSS box model, flexbox works slightly differently, and layout can be tricky. Also, debugging native crashes requires understanding the bridge between JavaScript and native code. I used Reactotron and Flipper for debugging. Another challenge: managing different screen sizes on Android (web has this too, but Android fragmentation is worse).

6. **"Would you choose differently for a different project?"**
   - Answer: Depends on the project. For this CRUD app with existing React codebase, React Native is perfect. If performance was critical (game, AR app, heavy animations), I'd choose native or Flutter. If the team had no JavaScript experience, Flutter would be easier to learn from scratch. If it was a simple content app, might just do a PWA. Architecture decisions should match project constraints.

7. **"How does this look on a resume?"**
   - Answer: Shows full-stack capability (backend + web + mobile), code reuse strategy, TypeScript across platforms, and understanding of cross-platform trade-offs. React Native is used by Facebook, Instagram, Discord - it's production-grade. Building mobile apps demonstrates I can work across the entire stack.

8. **Demonstrates:**
   - Practical decision-making (code reuse over purity)
   - Understanding of cross-platform frameworks
   - Resource awareness (solo developer constraints)
   - Knowledge of React ecosystem
   - Ability to quantify trade-offs (40% code reuse, 2 months vs 6 months)

## References

- [React Native Documentation](https://reactnative.dev/)
- [Expo Documentation](https://docs.expo.dev/)
- [React Native vs Flutter comparison](https://ionic.io/resources/articles/react-native-vs-flutter)
- [Companies using React Native](https://reactnative.dev/showcase)
