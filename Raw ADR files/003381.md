# ADR-005: SSR Architecture with Shared Library

**Status**: Accepted (Design Complete, Implementation Pending)  
**Date**: October 2025  
**Decision Makers**: Development Team  
**Related Documents**: 
- `docs/active-development/SSR_ARCHITECTURE.md`
- `docs/DEVELOPMENT.md`

---

## Context

Protogen's shared library architecture provides a comprehensive foundation for UI components and system modules used across web, and potentially mobile platforms. However, the initial architecture relied on client-side rendering (CSR) exclusively, which has several limitations:

### Client-Side Rendering Limitations

1. **Slow Initial Load**: Large JavaScript bundles must download before content appears
2. **SEO Challenges**: Search engines struggle with CSR applications
3. **Poor Performance Metrics**: High Time-to-Interactive (TTI) and First Contentful Paint (FCP)
4. **No Progressive Enhancement**: Requires JavaScript to function
5. **Mobile Performance**: Slower devices experience significant delays

### Requirements

- Faster initial page loads with pre-rendered HTML
- SEO-friendly content for search engine indexing
- Progressive enhancement (works without JavaScript)
- Reduced Time-to-Interactive (TTI)
- Consistent rendering between server and client
- Support for all shared library systems
- Integration with existing API backend
- Mobile-optimized bundle delivery

---

## Decision

**We will implement Server-Side Rendering (SSR) where the Laravel API can pre-render shared library system modules and deliver optimized bundles to clients.**

### SSR Architecture

```
Client Request
    ↓
API Server (FastAPI/Laravel)
    ↓
SSR Rendering Service
    ├── Import @protogen/shared modules
    ├── Render React components server-side
    ├── Serialize state for hydration
    └── Generate optimized bundles
    ↓
Pre-rendered HTML + Hydration Data
    ↓
Client (Fast Initial Display)
    ↓
Hydration (Interactive React App)
```

### Key Components

1. **SSR Rendering Service**: Server-side React rendering in API
2. **Shared Library Exports**: System modules exposed for SSR
3. **State Serialization**: Serialize app state for client hydration
4. **Bundle Optimization**: Tree-shaking and code-splitting
5. **Hydration Strategy**: Progressive hydration on client
6. **Cache Layer**: CDN-friendly caching for rendered content

---

## Design Principles

### 1. Shared Library as Foundation

The shared library serves both client and server:

```json
// shared/package.json
{
  "exports": {
    "./systems/navigator": "./dist/src/systems/navigator/index.js",
    "./systems/scene": "./dist/src/systems/scene/index.js",
    "./systems/dialog": "./dist/src/systems/dialog/index.js",
    "./components": "./dist/src/components/index.js"
  }
}
```

### 2. Dual Execution Context

Components must work in both environments:

```typescript
export class NavigatorSystem {
  private static isServer = typeof window === 'undefined';
  
  async loadData() {
    if (NavigatorSystem.isServer) {
      // Server: Direct database access
      return await db.query(...);
    } else {
      // Client: API fetch
      return await fetch('/api/...');
    }
  }
}
```

### 3. Progressive Hydration

Client hydrates server-rendered content progressively:

```typescript
// Server renders initial HTML
const html = renderToString(<App initialState={serverState} />);

// Client hydrates with same state
hydrateRoot(
  document.getElementById('root'),
  <App initialState={serverState} />
);
```

### 4. API as SSR Server

The Laravel API serves dual roles:

- REST API for client operations
- SSR server for initial page loads

```php
// Laravel route for SSR
Route::get('/{path}', function ($path) {
    return $ssrService->renderPage($path);
})->where('path', '.*');
```

---

## Consequences

### Positive

✅ **Fast Initial Load**: Pre-rendered HTML displays immediately  
✅ **SEO-Friendly**: Search engines index server-rendered content  
✅ **Progressive Enhancement**: Basic functionality without JavaScript  
✅ **Better Performance**: Improved TTI and FCP metrics  
✅ **Mobile Optimized**: Faster load on slower devices  
✅ **Consistent Rendering**: Same code renders on server and client  
✅ **CDN-Friendly**: Static HTML cacheable on CDN  
✅ **Future-Proof**: Ready for mobile app SSR

### Negative

⚠️ **Complexity**: Additional server rendering infrastructure  
⚠️ **Build Process**: More complex build and deployment  
⚠️ **State Management**: Careful serialization/deserialization required  
⚠️ **Debugging**: Harder to debug SSR vs CSR issues  
⚠️ **Resource Usage**: Server CPU for rendering  

### Neutral

ℹ️ **Dual Context**: Components must handle both server and client  
ℹ️ **API Changes**: New SSR endpoints in API  
ℹ️ **Bundle Strategy**: Need separate server and client bundles

---

## Implementation Strategy

### Phase 1: Foundation (Not Started)

1. Set up Node.js rendering service in API
2. Configure shared library for SSR
3. Implement basic server-side rendering
4. Add state serialization
5. Create hydration strategy

### Phase 2: System Integration (Not Started)

1. Make Navigator system SSR-compatible
2. Update Scene system for dual execution
3. Ensure Dialog system works with SSR
4. Test all shared components

### Phase 3: Optimization (Not Started)

1. Implement code splitting
2. Add progressive hydration
3. Configure CDN caching
4. Optimize bundle sizes
5. Add performance monitoring

### Phase 4: Production (Not Started)

1. Deploy SSR service
2. Configure reverse proxy
3. Set up CDN
4. Monitor performance
5. Gradual rollout

---

## Technical Details

### Server-Side Rendering Service

```typescript
// SSR service in API
export class SSRService {
  async renderPage(path: string): Promise<string> {
    // 1. Resolve route to scene
    const scene = await this.resolveScene(path);
    
    // 2. Load data for scene
    const data = await this.loadSceneData(scene);
    
    // 3. Render React component
    const html = renderToString(
      <SceneContainer scene={scene} initialData={data} />
    );
    
    // 4. Serialize state for hydration
    const state = this.serializeState(data);
    
    // 5. Generate HTML with hydration script
    return this.wrapHTML(html, state);
  }
}
```

### Component Compatibility

```typescript
// Example SSR-compatible component
export function SceneView({ sceneId }: SceneViewProps) {
  const [scene, setScene] = useState<Scene | null>(null);
  
  useEffect(() => {
    // Only runs on client
    if (typeof window !== 'undefined') {
      // Client-only initialization
      setupClientFeatures();
    }
  }, []);
  
  // Render works on both server and client
  return (
    <div className="scene-view">
      {scene ? <SceneContent scene={scene} /> : <Loading />}
    </div>
  );
}
```

### State Serialization

```typescript
// Serialize state for client hydration
function serializeState(state: AppState): string {
  return JSON.stringify({
    scene: state.currentScene,
    context: state.navigationContext,
    user: state.user,
    // ... other state
  });
}

// Deserialize on client
function deserializeState(stateScript: HTMLScriptElement): AppState {
  return JSON.parse(stateScript.textContent);
}
```

---

## Alternatives Considered

### Alternative 1: Client-Side Rendering Only

**Approach**: Continue with CSR, optimize bundle size

**Rejected Because**:
- Doesn't solve fundamental SEO and initial load problems
- Limited performance improvements possible
- Mobile devices still slow
- Missed opportunity for better UX

### Alternative 2: Static Site Generation (SSG)

**Approach**: Pre-render all pages at build time

**Rejected Because**:
- Not suitable for dynamic, user-specific content
- Admin-authored scenes can't be pre-rendered
- Real-time updates not possible
- Doesn't fit Protogen's dynamic nature

### Alternative 3: Third-Party SSR Framework (Next.js)

**Approach**: Migrate to Next.js for built-in SSR

**Rejected Because**:
- Major architectural change
- Loss of Laravel API benefits
- Doesn't integrate well with existing systems
- More complex deployment
- Vendor lock-in

### Alternative 4: Server Components (RSC)

**Approach**: Use React Server Components

**Rejected Because**:
- Still experimental/bleeding edge
- Requires Next.js or similar framework
- Not compatible with existing architecture
- Too early for production use

---

## Implementation Status

### Completed

- ✅ Shared library architecture (SSR-ready)
- ✅ System modules as separate exports
- ✅ TypeScript types for all modules
- ✅ Component isolation and organization

### Pending

- ⏳ SSR rendering service in API
- ⏳ State serialization/deserialization
- ⏳ Hydration strategy implementation
- ⏳ Component SSR compatibility updates
- ⏳ CDN configuration for cached content
- ⏳ Performance monitoring and optimization

---

## Success Metrics

### Performance Targets

- Time to First Byte (TTFB): < 200ms
- First Contentful Paint (FCP): < 1s
- Time to Interactive (TTI): < 3s
- Lighthouse Score: > 90

### Implementation Metrics

- All system components SSR-compatible
- No SSR-specific bugs in production
- Consistent rendering server/client
- CDN cache hit rate > 80%

---

## References

- **Architecture Doc**: `docs/active-development/SSR_ARCHITECTURE.md`
- **Shared Library**: `shared/package.json` exports
- **Development Guide**: `docs/DEVELOPMENT.md`

---

## Notes

SSR Architecture represents a future enhancement to Protogen's already strong shared library foundation. The decision to design for SSR from the beginning (separable system modules, dual execution context) means implementation will be straightforward when the time comes.

The choice to use the existing API as the SSR server (rather than a separate Node.js server) maintains architectural simplicity and leverages existing infrastructure.

**Status**: Foundation is ready, implementation awaiting prioritization. The shared library architecture was designed from the start to support SSR, making future implementation low-risk.

**Next Step**: When implementing, start with a single system scene (e.g., SystemHomeScene) as proof of concept before rolling out to all scenes.

