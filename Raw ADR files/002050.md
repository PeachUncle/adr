# Studio Package Design Document

## Context

HAI3 needs a modern, extensible developer tooling solution that:
1. Provides more space than the current Footer implementation
2. Can be completely excluded from production builds
3. Offers modern UX with drag/resize/collapse capabilities
4. Follows HAI3's clean architecture principles (package isolation, dependency inversion)
5. Allows future expansion (state inspector, console, performance monitoring)

### Stakeholders
- **Developers**: Need quick access to dev tools while building with HAI3
- **Platform Builders**: Want zero production bundle impact
- **HAI3 Core Team**: Need extensible architecture for future dev features

### Constraints
- Must follow HAI3 package dependency rules (no circular dependencies)
- Must use event-driven pattern (emit events, not direct dispatch)
- Must be tree-shakeable via conditional imports
- Must work cross-browser (no browser extension for now)
- Must persist state across page reloads

## Goals / Non-Goals

### Goals
✅ Create standalone `@hai3/studio` package
✅ Implement floating, draggable, resizable panel with glassmorphic design
✅ Migrate existing dev tools (theme, screenset, language, API mode) from Footer
✅ Zero production bundle impact via conditional imports
✅ Keyboard shortcut for power users (`Ctrl+Shift+D`)
✅ Persistent state (position, size, collapsed) in localStorage
✅ Extensible architecture for future dev tool sections

### Non-Goals
❌ Browser extension (future consideration if deep debugging needed)
❌ Redux time-travel or state tree inspection (future feature)
❌ Built-in console or network panel (use browser Studio for now)
❌ Multi-language translation for dev tools UI (English only)
❌ Mobile/responsive support (dev tools for desktop development only)

## Decisions

### 0. UIKit Contracts: Keep Unified for Now, Split If Needed Later

**Decision**: Keep `@hai3/uikit-contracts` as a single package for now. If studio requires contracts not used by uicore, consider splitting in the future.

**Rationale**:
- **Contracts are types only**: No runtime code, minimal bundle impact (few KB)
- **YAGNI principle**: Don't split until we have concrete need
- **Simpler architecture**: Fewer packages to manage
- **Easy to split later**: If studio needs 50+ studio-only type definitions, we can create `@hai3/uikit-contracts-studio` or use subpath exports

**Future Split Strategy** (if needed):
```
Option 1: Separate package
  @hai3/uikit-contracts (core types)
  @hai3/uikit-contracts-studio (studio-only types)

Option 2: Subpath exports
  @hai3/uikit-contracts/core
  @hai3/uikit-contracts/studio
```

**For now**: All contracts in `@hai3/uikit-contracts`, both uicore and studio import from it.

### 1. Package Architecture: Standalone Workspace Package

**Decision**: Create `@hai3/studio` as a new workspace package with direct dependency on `@hai3/uikit`.

**Rationale**:
- **Clean separation**: Dev tools are conceptually separate from production layout code
- **No production bloat**: Studio can import directly from `@hai3/uikit` without platforms needing to register studio-specific components
- **Tree-shaking**: Entire package (including its uikit dependencies) eliminated when conditionally imported
- **Simplified platform code**: Platforms don't register components only used by studio
- **Independent versioning**: Can evolve dev tools separately from core packages

**Alternatives Considered**:
- **Alt 1: Keep in `uicore`** - Rejected because it mixes dev and production concerns
- **Alt 2: Use `uikitRegistry` for all components** - Rejected because platforms would need to register studio-specific components, bloating production bundles
- **Alt 3: Separate npm package** - Overkill for monorepo; adds publishing overhead
- **Alt 4: Browser extension** - Rejected for v1 due to installation friction and cross-browser complexity

**Why Direct `@hai3/uikit` Dependency Is Safe**:
- Studio is conditionally imported with `if (import.meta.env.DEV)`
- Vite/Rollup tree-shakes the entire branch in production builds
- Both `@hai3/studio` AND its dependency `@hai3/uikit` components are eliminated
- Zero production bundle impact

**Implementation**:
```
packages/studio/
├── package.json          # Workspace package config
├── tsconfig.json         # Extends root tsconfig
├── tsup.config.ts        # ESM build with sideEffects: false
└── src/
    ├── StudioOverlay.tsx      # Top-level component
    ├── StudioPanel.tsx        # Main panel UI
    ├── StudioProvider.tsx     # Context for state
    ├── hooks/
    │   ├── useDraggable.ts
    │   ├── useResizable.ts
    │   └── useKeyboardShortcut.ts
    ├── sections/
    │   ├── ThemeSelector.tsx    # Migrated from uicore
    │   ├── ScreensetSelector.tsx
    │   ├── LanguageSelector.tsx
    │   └── ApiModeToggle.tsx
    └── utils/
        └── persistence.ts       # localStorage helpers
```

### 2. UI Pattern: Floating Glassmorphic Overlay

**Decision**: Use a floating div with glassmorphism design (backdrop blur, semi-transparent background), draggable/resizable, collapsible to small button.

**Rationale**:
- **Modern UX**: Glassmorphism is a 2025 design trend (see research: macOS, Fluent UI)
- **Flexibility**: User controls position and size, unlike docked panels
- **Non-intrusive**: Collapses to tiny 40px button when not needed
- **No layout impact**: Floating overlay doesn't push content aside
- **Visual appeal**: Backdrop blur creates professional, polished look

**Alternatives Considered**:
- **Alt 1: Docked panel (Storybook-style)** - Rejected because it reduces viewport space and requires layout integration
- **Alt 2: Chrome extension** - Rejected for v1 (see Decision #1)
- **Alt 3: Modal dialog** - Rejected because modals block interaction with the app

**Implementation Details**:
- **Positioning**: CSS `position: fixed`, default bottom-right (adjustable)
- **Z-index**: 10000 (above all app content)
- **Glassmorphism CSS**:
  ```css
  background: rgba(255, 255, 255, 0.1); /* Light theme */
  background: rgba(0, 0, 0, 0.4);       /* Dark theme */
  backdrop-filter: blur(16px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  ```

### 3. Drag Implementation: Custom Mouse Event Handler

**Decision**: Implement drag-and-drop using custom `useDraggable` hook with mouse events (no external library).

**Rationale**:
- **Simplicity**: Drag logic is straightforward (track mouse down/move/up)
- **Zero dependencies**: No need for react-draggable or similar libraries
- **Custom constraints**: Easy to enforce viewport boundaries
- **Learning opportunity**: Demonstrates React hook patterns for HAI3 users

**Implementation**:
```typescript
// packages/studio/src/hooks/useDraggable.ts
export const useDraggable = (initialPosition: Position) => {
  const [position, setPosition] = useState(initialPosition);
  const [isDragging, setIsDragging] = useState(false);
  const dragStartPos = useRef<Position>({ x: 0, y: 0 });

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    dragStartPos.current = { x: e.clientX - position.x, y: e.clientY - position.y };
  };

  useEffect(() => {
    if (!isDragging) return;

    const handleMouseMove = (e: MouseEvent) => {
      const newX = clamp(e.clientX - dragStartPos.current.x, 0, window.innerWidth - panelWidth);
      const newY = clamp(e.clientY - dragStartPos.current.y, 0, window.innerHeight - panelHeight);
      setPosition({ x: newX, y: newY });
      saveToLocalStorage('hai3:studio:position', { x: newX, y: newY });
    };

    const handleMouseUp = () => setIsDragging(false);

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging]);

  return { position, handleMouseDown, isDragging };
};
```

**Viewport Boundary Enforcement**: Clamp x/y to `[0, window.innerWidth - panelWidth]` and `[0, window.innerHeight - panelHeight]`.

### 4. Resize Implementation: Corner Handle with Mouse Events

**Decision**: Implement resize with a visible corner handle (bottom-right) using `useResizable` hook.

**Rationale**:
- **Discoverability**: Corner grip icon signals resizability
- **Simplicity**: Only bottom-right corner needed (most common UX)
- **Min/Max constraints**: Easy to enforce bounds (320x400 min, 600x800 max)
- **No library**: Custom hook keeps bundle small

**Implementation**:
```typescript
// packages/studio/src/hooks/useResizable.ts
export const useResizable = (initialSize: Size) => {
  const [size, setSize] = useState(initialSize);
  const [isResizing, setIsResizing] = useState(false);

  const handleMouseDown = (e: React.MouseEvent) => {
    e.stopPropagation(); // Don't trigger drag
    setIsResizing(true);
  };

  useEffect(() => {
    if (!isResizing) return;

    const handleMouseMove = (e: MouseEvent) => {
      const newWidth = clamp(e.clientX - panelX, MIN_WIDTH, MAX_WIDTH);
      const newHeight = clamp(e.clientY - panelY, MIN_HEIGHT, MAX_HEIGHT);
      setSize({ width: newWidth, height: newHeight });
      saveToLocalStorage('hai3:studio:size', { width: newWidth, height: newHeight });
    };

    const handleMouseUp = () => setIsResizing(false);

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing]);

  return { size, handleMouseDown, isResizing };
};
```

**Constraints**:
- Min: 320px × 400px (enough for controls)
- Max: 600px × 800px (prevents obscuring too much app content)

### 5. State Persistence: localStorage with Defensive Defaults

**Decision**: Persist panel state (position, size, collapsed) to localStorage with defensive error handling.

**Rationale**:
- **User convenience**: State survives page reloads
- **Privacy**: localStorage is client-side only (no server tracking)
- **Resilience**: Defensive coding handles localStorage errors (quota exceeded, disabled, etc.)

**Keys**:
- `hai3:studio:position` - `{ x: number, y: number }`
- `hai3:studio:size` - `{ width: number, height: number }`
- `hai3:studio:collapsed` - `boolean`

**Implementation**:
```typescript
// packages/studio/src/utils/persistence.ts
export const saveStudioState = <T>(key: string, value: T): void => {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (e) {
    console.warn(`[Studio] Failed to save state for ${key}:`, e);
  }
};

export const loadStudioState = <T>(key: string, defaultValue: T): T => {
  try {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : defaultValue;
  } catch (e) {
    console.warn(`[Studio] Failed to load state for ${key}:`, e);
    return defaultValue;
  }
};
```

**Default Values** (when localStorage is empty or fails):
- Position: `{ x: window.innerWidth - 420, y: window.innerHeight - 520 }` (bottom-right with 20px margin)
- Size: `{ width: 400, height: 500 }`
- Collapsed: `false`

### 6. Conditional Import: Dynamic import() with import.meta.env.DEV

**Decision**: Use dynamic `import()` wrapped in `if (import.meta.env.DEV)` to conditionally load studio.

**Rationale**:
- **Tree-shaking**: Vite's Rollup will eliminate the entire branch in production builds
- **Code-splitting**: Dynamic import creates separate chunk even in dev mode
- **Type-safety**: TypeScript understands conditional imports
- **No runtime check**: `import.meta.env.DEV` is replaced at build time (zero production overhead)

**Implementation**:
```typescript
// src/main.tsx
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { HAI3Provider } from '@hai3/uicore';
import { App } from './App';
import '@/uikit/uikitRegistry';
import '@/screensets/screensetRegistry';
import '@/themes/themeRegistry';
import './index.css';

const rootElement = document.getElementById('root')!;
const root = createRoot(rootElement);

// Conditionally load and render Studio in development
(async () => {
  let StudioOverlay: React.ComponentType | null = null;

  if (import.meta.env.DEV) {
    const studio = await import('@hai3/studio');
    StudioOverlay = studio.StudioOverlay;
  }

  root.render(
    <StrictMode>
      <HAI3Provider>
        <App />
      </HAI3Provider>
      {StudioOverlay && <StudioOverlay />}
    </StrictMode>
  );
})();
```

**Build Verification**: Run `npm run build` and inspect `dist/` bundle to confirm:
1. No `@hai3/studio` imports in production JS
2. No studio-related strings in bundle
3. Bundle size doesn't increase

**Alternatives Considered**:
- **Alt 1: Runtime environment check** (`if (process.env.NODE_ENV === 'development')`) - Rejected because code still ships in bundle
- **Alt 2: Separate entry point** - Rejected because it complicates build config

### 7. Component Hierarchy: Context Provider Pattern

**Decision**: Use React Context API via `StudioProvider` to share state across panel components.

**Rationale**:
- **Clean prop-drilling avoidance**: Position, size, collapsed state accessible anywhere
- **Separation of concerns**: Provider handles state logic, components handle UI
- **Testability**: Can test provider and components independently
- **React best practice**: Standard pattern for shared state

**Component Tree**:
```
<StudioOverlay>                      # Top-level, handles keyboard shortcuts
  <StudioProvider>                   # Context provider for state
    {collapsed ? (
      <FloatingButton />               # 40px button (uses UIKit Button)
    ) : (
      <StudioPanel>                  # Main panel (uses UIKit Card)
        <PanelHeader />                # Title, collapse button (UIKit Button), drag handle
        <ControlPanel>                 # Scrollable content (UIKit ScrollArea)
          <ThemeSelector />            # Uses UIKit DropdownMenu
          <ScreensetSelector />        # Uses UIKit DropdownMenu
          <LanguageSelector />         # Uses UIKit DropdownMenu
          <ApiModeToggle />            # Uses UIKit Switch/Toggle
        </ControlPanel>
        <ResizeHandle />               # Bottom-right corner grip (custom div)
      </StudioPanel>
    )}
  </StudioProvider>
</StudioOverlay>
```

**UIKit Component Usage** (direct imports):
```typescript
// In StudioPanel.tsx - Direct imports from @hai3/uikit
import { Card } from '@hai3/uikit';
import { Button } from '@hai3/uikit';
import { ScrollArea } from '@hai3/uikit';

// In control selectors - Direct imports (no registry needed)
import { DropdownMenu, DropdownButton, DropdownMenuItem } from '@hai3/uikit';
```

**Why not `uikitRegistry`?**
- Registry pattern is for runtime swappability (platforms customizing components)
- Studio components are internal implementation details, not meant to be customized
- Direct imports simpler and tree-shake better
- Platforms don't waste bundle space on studio-only components

**Context Shape**:
```typescript
interface StudioContextValue {
  position: Position;
  size: Size;
  collapsed: boolean;
  setPosition: (pos: Position) => void;
  setSize: (size: Size) => void;
  toggleCollapsed: () => void;
  toggleVisibility: () => void;
}
```

### 8. Keyboard Shortcuts: Global Event Listener with Cleanup

**Decision**: Use `useKeyboardShortcut` hook that attaches window-level keydown listener.

**Rationale**:
- **Global access**: Works regardless of focus (unless input/textarea has focus)
- **Platform-aware**: Detects macOS (`metaKey`) vs Windows/Linux (`ctrlKey`)
- **Proper cleanup**: Removes listener on unmount

**Implementation**:
```typescript
// packages/studio/src/hooks/useKeyboardShortcut.ts
export const useKeyboardShortcut = (handler: () => void) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
      const modifierKey = isMac ? e.metaKey : e.ctrlKey;

      if (modifierKey && e.shiftKey && e.key === 'D') {
        e.preventDefault(); // Prevent browser bookmark dialog
        handler();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handler]);
};
```

**Edge Case Handling**:
- **Prevent default**: Stop browser's native `Ctrl+Shift+D` (bookmark all tabs)
- **Input focus**: Consider adding check to ignore if `document.activeElement` is input/textarea
- **Restore focus**: After toggling visibility, focus should return to previous element (future enhancement)

## Risks / Trade-offs

### Risk 1: Floating Panel Obscures Content

**Risk**: Users might accidentally position panel over important UI during development.

**Mitigation**:
- Draggable and collapsible - user can move or hide instantly
- Persistent position - once positioned well, stays there
- Keyboard shortcut for quick toggle
- Semi-transparent glassmorphism allows some visibility through panel

**Trade-off**: Accepted. Docked panels (Storybook-style) avoid this but reduce viewport space permanently. Floating overlay is more flexible.

### Risk 2: Tree-Shaking Failure

**Risk**: Conditional import might not be eliminated in production if build config is incorrect.

**Mitigation**:
- **Test in CI**: Add build step that inspects bundle for studio strings
- **Documentation**: Clear instructions in README about verifying tree-shaking
- **Package config**: Set `"sideEffects": false` in `@hai3/studio/package.json`

**Trade-off**: Accepted. If tree-shaking fails, production bundle includes ~50KB of dev tools code (minor). CI tests will catch this.

### Risk 3: localStorage Quota or Disabled

**Risk**: State persistence fails if localStorage is full or disabled (privacy mode).

**Mitigation**:
- Defensive try/catch in persistence utilities
- Fallback to in-memory defaults if localStorage unavailable
- Log warnings to console (not user-facing errors)

**Trade-off**: Accepted. Worst case: panel resets to default position/size on reload. Non-critical for dev tools.

### Risk 4: Glassmorphism Performance

**Risk**: `backdrop-filter: blur()` can be GPU-intensive, especially on low-end devices.

**Mitigation**:
- Panel is dev-only (not production concern)
- Panel is typically small (400x500px), not full-screen
- Can add option to disable glassmorphism in future if needed

**Trade-off**: Accepted. Dev environments typically run on powerful machines. If performance issue arises, add toggle for "simple mode" (solid background, no blur).

## Migration Plan

### Step 1: Create Package (Day 1)
1. Scaffold `packages/studio` directory
2. Create package.json, tsconfig, tsup config
3. Add to root workspace
4. Verify builds successfully

### Step 2: Implement Core Components (Day 2)
1. Build StudioPanel, StudioProvider, StudioOverlay
2. Implement drag/resize hooks
3. Add keyboard shortcuts
4. Add state persistence

### Step 3: Migrate Controls (Day 2-3)
1. Copy ThemeSelector, ScreensetSelector, LanguageSelector, ApiModeToggle from uicore to studio
2. Update imports to use `@hai3/uicore` for hooks/actions
3. Create ControlPanel container
4. Test all controls work correctly

### Step 4: Integrate and Clean Up (Day 3)
1. Add conditional import to `src/main.tsx`
2. Remove dev tools from Footer in uicore
3. Test dev mode: studio loads and works
4. Test production build: studio excluded

### Step 5: Validation (Day 4)
1. Run architecture checks (`npm run arch:check`, `npm run arch:deps`)
2. Manual testing: drag, resize, collapse, keyboard, state persistence
3. Production bundle verification
4. Update documentation

### Rollback Plan
If critical issues arise:
1. Keep Footer with dev tools as fallback (behind feature flag)
2. Disable studio conditional import in main.tsx
3. Fix issues in studio package
4. Re-enable when stable

No user-facing breaking changes - rollback is seamless.

## Open Questions

1. **Future Features**: Should we add state inspector (Redux tree) in v2?
   - **Answer**: Yes, but defer to future. Focus on v1 = controls only.

2. **Multi-Panel Support**: Should panel support tabs for future sections (Console, Network, etc.)?
   - **Answer**: Yes, add tab structure to ControlPanel now (even if only 1 tab initially). Makes future expansion easier.

3. **Themes**: Should studio respect app theme or have independent theme?
   - **Answer**: Respect app theme. Glassmorphism adapts to light/dark automatically.

4. **Mobile**: Should we support mobile responsive layout?
   - **Answer**: No. Studio are for desktop development only. Saves complexity.
