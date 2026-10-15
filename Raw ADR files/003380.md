# ADR-004: Scene-First Routing

**Status**: Accepted and Implemented  
**Date**: 2025  
**Decision Makers**: Development Team  
**Related Documents**: 
- `docs/active-development/SCENE_FIRST_ROUTING.md`
- `docs/active-development/NAVIGATOR_SYSTEMS_ARCHITECTURE.md`

---

## Context

Protogen required a navigation architecture for the portal interface that could handle both traditional page-like navigation and the unique requirements of a scene-based content platform.

### Traditional Routing Challenges

1. **Page-Centric Model**: Standard React routing is page-based, not scene-based
2. **Limited Context**: URL alone insufficient for complex navigation state
3. **Auxiliary Interactions**: Modals, drawers, and dialogs not well integrated
4. **Scene Discovery**: No clear pattern for loading admin-authored scenes
5. **Navigation State**: Difficult to maintain navigation history and context
6. **URL Sync**: Complex bi-directional sync between URL and app state

### Requirements

- Full-screen scene-oriented interface
- System scenes (built-in) and custom scenes (admin-authored)
- Context-based navigation with history tracking
- Dialog system for auxiliary interactions
- URL synchronization with browser history
- Flexible routing patterns (exact, glob, regex)
- Default scene handling
- Integration with Navigator system

---

## Decision

**We will implement Scene-First Routing where scenes are the primary UI paradigm**, with all navigation driven by the Navigator system and contexts mapped to scenes via the SceneRouter.

### Scene-First Architecture

```
User Navigation
    ↓
Navigator System (context changes)
    ↓
SceneRouter (context → scene mapping)
    ↓
SceneContainer (dynamic scene rendering)
    ↓
Scene Component (system or custom)
```

### Key Components

1. **Navigator System**: Central navigation state management
2. **SceneRouter**: Maps contexts to scene IDs with pattern matching
3. **SceneContainer**: Dynamically renders appropriate scene
4. **URL Sync Service**: Bi-directional URL ↔ context synchronization
5. **System Scenes**: Built-in scenes (Home, Explore, Profile, Settings)
6. **Dialog System**: Handles all non-scene interactions

---

## Design Principles

### 1. Scenes as Primary UI

The entire application is scene-driven:
- User loads portal → Default scene renders
- User navigates → Context changes → New scene renders
- Auxiliary interactions → Dialog system handles

### 2. Context-Based Navigation

Navigation uses contexts, not URLs:

```typescript
// Navigate by context
navigatorSystem.navigateTo('/explore');

// Navigate to specific scene
navigatorSystem.navigateToScene('system-profile');

// Navigate to scene in deck
navigatorSystem.navigateToDeck('my-deck', 0);
```

### 3. Flexible Routing Patterns

SceneRouter supports multiple pattern types:

```typescript
// Exact match
sceneRouter.setSceneOverride('/explore', 'system-explore');

// Glob pattern
sceneRouter.setSceneOverride('/profile/*', 'system-profile');

// Regex pattern
sceneRouter.setSceneOverride('^/admin/.*', 'admin-dashboard');

// Priority-based resolution
sceneRouter.setSceneOverride('/special', 'special-scene', 100);
```

### 4. Dialog Integration

All auxiliary interactions use the Dialog System:

```typescript
// Non-scene interactions in dialogs
dialogSystem.openModal({
    title: 'Settings',
    content: <SettingsPanel />
});

// Comments, bookmarks, etc. in drawers
dialogSystem.openDrawer({
    position: 'right',
    content: <CommentsPanel />
});
```

---

## Consequences

### Positive

✅ **Unified Experience**: Consistent full-screen scene interface  
✅ **Flexible Routing**: Pattern matching supports complex routing rules  
✅ **Admin Control**: Admins can override routing for custom scenes  
✅ **History Tracking**: Full navigation history with back/forward  
✅ **URL Sync**: Browser URLs stay in sync with navigation state  
✅ **System Extensibility**: Easy to add new system scenes  
✅ **Custom Scenes**: Admin-authored scenes load dynamically  
✅ **Clean Separation**: Dialogs for auxiliary, scenes for primary content

### Negative

⚠️ **Learning Curve**: Different from traditional page-based routing  
⚠️ **Context Complexity**: Context paths can become complex  
⚠️ **Pattern Conflicts**: Possible routing pattern conflicts (mitigated by priority)

### Neutral

ℹ️ **No React Router**: Custom navigation instead of react-router-dom  
ℹ️ **Event-Driven**: Navigation uses event system for coordination  
ℹ️ **State Management**: Navigator system maintains navigation state

---

## Implementation Details

### Scene Router

```typescript
export class SceneRouter {
  private routes: Map<string, RouteConfig> = new Map();
  private defaultSceneId: string = 'system-home';
  
  // Get scene for current context
  getSceneForContext(context: CurrentContext): string {
    // 1. Exact match
    const exact = this.routes.get(context.path);
    if (exact) return exact.sceneId;
    
    // 2. Pattern matching (by priority)
    const patterns = Array.from(this.routes.values())
      .filter(r => r.pattern)
      .sort((a, b) => (b.priority || 0) - (a.priority || 0));
    
    for (const route of patterns) {
      if (this.matchesPattern(context.path, route.pattern)) {
        return route.sceneId;
      }
    }
    
    // 3. Context-specified scene
    if (context.sceneId) return context.sceneId;
    
    // 4. Default scene
    return this.defaultSceneId;
  }
  
  setSceneOverride(pattern: string, sceneId: string, priority = 0) {
    this.routes.set(pattern, { pattern, sceneId, priority });
  }
}
```

### System Scenes

Four built-in system scenes:

1. **SystemHomeScene** (`system-home`)
   - Default landing scene
   - Welcome message and quick actions
   - Route: `/`

2. **SystemExploreScene** (`system-explore`)
   - Content discovery and browsing
   - Search and filtering
   - Route: `/explore`

3. **SystemProfileScene** (`system-profile`)
   - User profile and settings
   - Activity history
   - Route: `/profile/*`

4. **SystemSettingsScene** (`system-settings`)
   - App configuration
   - Preferences management
   - Route: `/settings`

### URL Synchronization

```typescript
export class URLSyncService {
  // Sync context → URL
  syncContextToURL(context: CurrentContext) {
    const url = this.contextToURL(context);
    window.history.pushState({ context }, '', url);
  }
  
  // Sync URL → context
  syncURLToContext(url: string): CurrentContext {
    return this.urlToContext(url);
  }
  
  // Bi-directional sync
  initialize() {
    // Listen to Navigator changes
    navigatorSystem.on('navigate', (context) => {
      this.syncContextToURL(context);
    });
    
    // Listen to browser back/forward
    window.addEventListener('popstate', (event) => {
      if (event.state?.context) {
        navigatorSystem.navigateTo(event.state.context.path);
      }
    });
  }
}
```

---

## Implementation Status

### Completed

- ✅ SceneRouter with pattern matching
- ✅ Four default system scenes (Home, Explore, Profile, Settings)
- ✅ SceneContainer component with dynamic rendering
- ✅ URL synchronization service
- ✅ Integration with Navigator system
- ✅ Dialog system integration
- ✅ Scene override configuration
- ✅ History tracking with back/forward
- ✅ Breadcrumb navigation

### Future Enhancements

- ⏳ Admin UI for route configuration
- ⏳ Scene loading indicators
- ⏳ Scene transition animations
- ⏳ Advanced caching strategies
- ⏳ Prefetching for common paths

---

## Alternatives Considered

### Alternative 1: React Router with Custom Integration

**Approach**: Use react-router-dom with custom scene components

**Rejected Because**:
- Forced page-centric mental model
- URL-first instead of context-first
- Dialog integration awkward
- Less control over navigation flow
- Harder to implement scene overrides

### Alternative 2: URL-Only Navigation

**Approach**: Use URL as sole source of truth for navigation

**Rejected Because**:
- URLs insufficient for complex navigation state
- Difficult to maintain deep context
- History tracking more complex
- Admin scene overrides harder to implement

### Alternative 3: Mixed Routing (Pages + Scenes)

**Approach**: Some routes as pages, some as scenes

**Rejected Because**:
- Inconsistent user experience
- Confusing mental model
- Harder to maintain two systems
- Unclear boundary between pages and scenes

---

## Success Metrics

### Achieved

✅ Smooth scene transitions  
✅ Working back/forward navigation  
✅ URL synchronization functional  
✅ Admin scene overrides working  
✅ All system scenes operational  
✅ Dialog integration seamless  

### User Experience

✅ Intuitive navigation patterns  
✅ Fast scene loading  
✅ Consistent full-screen experience  
✅ Clear navigation state (breadcrumbs)  

---

## References

- **Documentation**: `docs/active-development/SCENE_FIRST_ROUTING.md`
- **Navigator System**: `docs/active-development/NAVIGATOR_SYSTEMS_ARCHITECTURE.md`
- **Implementation**: `shared/src/systems/scene/SceneRouter.ts`
- **System Scenes**: `shared/src/systems/scene/default-scenes/`
- **URL Sync**: `shared/src/systems/navigator/URLSyncService.ts`

---

## Notes

Scene-First Routing has proven to be the right architectural choice for Protogen. The clear separation between scenes (primary content) and dialogs (auxiliary interactions) creates a consistent and intuitive user experience.

The flexibility of pattern-based routing enables admin control over navigation while maintaining system defaults. The context-first approach (rather than URL-first) better matches the mental model of scene-based navigation.

**Key Insight**: Embracing scene-first architecture fully (rather than trying to fit scenes into page-based routing) led to a cleaner, more maintainable system.

