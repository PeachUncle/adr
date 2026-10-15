# ADR-005: Extract UI Components

**Status:** ✅ Accepted and Implemented  
**Date:** 2025-10-09  
**Phase:** Phase 5 - Extract UI Components

---

## Context

After extracting hooks in Phase 4, the DrawingCanvas.tsx component still contained 971 lines with all UI rendering logic in a single monolithic component. The component rendered:

- Canvas element with event handlers
- Width HUD for editing selected lines
- Floating action button for draw mode
- Sidebar with line summary
- Bottom bar with zoom controls

All of this rendering logic was mixed together, making the component difficult to understand, test, and maintain.

### Problems Identified

1. **Monolithic Component:** 971 lines of rendering logic in one file
2. **Poor Testability:** UI elements couldn't be tested in isolation
3. **No Reusability:** UI elements couldn't be reused in other contexts
4. **Difficult Maintenance:** Changes to one UI element required navigating the entire file
5. **Mixed Concerns:** Canvas rendering, HUD, sidebar, and controls all in one component

---

## Decision

We decided to extract UI rendering into focused, single-responsibility components:

### Component Organization (`src/components/DrawingCanvas/`)

**UI Components:**
- `WidthHUD.tsx` - Floating HUD for editing line width
- `DrawButton.tsx` - Floating action button for draw mode toggle
- `Sidebar.tsx` - Collapsible sidebar with line summary
- `BottomBar.tsx` - Bottom bar with zoom controls
- `CanvasRenderer.tsx` - Canvas element with all event handlers
- `index.ts` - Barrel export

**Component Principles:**
- **Single Responsibility:** Each component handles one UI concern
- **Props Over State:** Components receive data via props, not internal state
- **Composition:** Main component composes child components
- **Type Safety:** All props are strongly typed with TypeScript interfaces
- **Testability:** Components can be tested with React Testing Library

---

## Consequences

### Positive

✅ **Improved Testability:** Components tested in isolation (41 tests, ~95% coverage)  
✅ **Better Reusability:** Components can be reused in other contexts  
✅ **Clearer Structure:** Each component has a clear, focused purpose  
✅ **Easier Maintenance:** Changes to UI elements are localized  
✅ **Reduced Complexity:** Main component reduced by 69 lines  
✅ **Better Composition:** Main component is now primarily composition

### Negative

🟡 **More Files:** Created 8 new files (5 component files, 3 test files initially, +4 in Phase 6)  
🟡 **Prop Drilling:** Some props need to be passed through multiple levels  
🟡 **Component Overhead:** More components means more files to navigate

### Neutral

- **Minimal Runtime Impact:** Component extraction has negligible performance impact
- **No Behavior Change:** Functionality remains identical
- **Medium-High Risk:** UI changes are more visible, requiring careful testing

---

## Alternatives Considered

### 1. Keep Monolithic Component
**Rejected:** Would maintain high complexity and poor testability

### 2. Extract Fewer, Larger Components
**Rejected:** Single-responsibility components are easier to test and maintain

### 3. Use Component Libraries (Material-UI, etc.)
**Rejected:** Custom components provide better control and smaller bundle size

### 4. Create Separate Pages/Routes
**Rejected:** Application is single-page; routing not needed

---

## Implementation Details

### WidthHUD Component

**Before (inline in DrawingCanvas):**
```typescript
{selectedLine && hudPosition && (
  <div
    style={{
      position: 'absolute',
      left: hudPosition.x,
      top: hudPosition.y,
      // ... styles
    }}
  >
    <div>Width</div>
    <input
      type="range"
      min="1"
      max="60"
      value={selectedLine.width}
      onChange={(e) => handleWidthChange(Number(e.target.value))}
    />
    <div>{selectedLine.width}px</div>
  </div>
)}
```

**After (extracted component):**
```typescript
// src/components/DrawingCanvas/WidthHUD.tsx
export interface WidthHUDProps {
  selectedLine: Line | null;
  position: { x: number; y: number } | null;
  onWidthChange: (newWidth: number) => void;
  hudRef?: React.RefObject<HTMLDivElement>;
}

export function WidthHUD(props: WidthHUDProps): JSX.Element | null {
  const { selectedLine, position, onWidthChange, hudRef } = props;
  
  if (!selectedLine || !position) return null;
  
  return (
    <div
      ref={hudRef}
      role="dialog"
      aria-label="Line width editor"
      style={{ position: 'absolute', left: position.x, top: position.y }}
      className="bg-white border-2 border-blue-500 rounded-lg shadow-lg p-4"
    >
      <div className="text-sm font-semibold text-gray-700 mb-2">Width</div>
      <input
        type="range"
        min="1"
        max="60"
        value={selectedLine.width}
        onChange={(e) => onWidthChange(Number(e.target.value))}
        aria-label="Selected line width"
        className="w-full"
      />
      <div className="text-center text-sm font-mono mt-2">
        {selectedLine.width}px
      </div>
    </div>
  );
}

// src/components/DrawingCanvas/__tests__/WidthHUD.test.tsx
describe('WidthHUD', () => {
  it('should not render when no line selected', () => {
    const { container } = render(
      <WidthHUD selectedLine={null} position={{x: 0, y: 0}} onWidthChange={vi.fn()} />
    );
    expect(container.firstChild).toBeNull();
  });
  
  it('should call onWidthChange when slider changes', () => {
    const onWidthChange = vi.fn();
    render(<WidthHUD selectedLine={mockLine} position={{x: 0, y: 0}} onWidthChange={onWidthChange} />);
    const slider = screen.getByRole('slider');
    fireEvent.change(slider, { target: { value: '15' } });
    expect(onWidthChange).toHaveBeenCalledWith(15);
  });
});
```

### Sidebar Component

```typescript
// src/components/DrawingCanvas/Sidebar.tsx
export interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
  lineSummary: LineSummaryRow[];
  currentScale: Scale;
  width?: number;
}

export function Sidebar(props: SidebarProps): JSX.Element {
  const { collapsed, onToggle, lineSummary, currentScale, width = 320 } = props;
  const sidebarWidth = collapsed ? 0 : width;
  
  return (
    <>
      {/* Toggle button */}
      <button
        onClick={onToggle}
        style={{ right: `${sidebarWidth}px` }}
        className="fixed top-1/2 transform -translate-y-1/2 z-50"
        aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        {collapsed ? <ChevronLeft /> : <ChevronRight />}
      </button>
      
      {/* Sidebar content */}
      {!collapsed && (
        <div style={{ width: `${width}px` }} className="fixed right-0 top-0 h-full">
          <div className="p-4">
            <h2>Line Summary</h2>
            <p>Scale: {currentScale.displayName}</p>
            {lineSummary.length === 0 ? (
              <p>No lines drawn yet</p>
            ) : (
              <table>
                {/* Table content */}
              </table>
            )}
          </div>
        </div>
      )}
    </>
  );
}

// Tests cover: collapsed/expanded states, line summary rendering, empty state
```

### CanvasRenderer Component

```typescript
// src/components/DrawingCanvas/CanvasRenderer.tsx
export interface CanvasRendererProps {
  canvasRef: React.RefObject<HTMLCanvasElement>;
  containerRef: React.RefObject<HTMLDivElement>;
  isDrawActive: boolean;
  onPointerDown: (e: React.PointerEvent<HTMLCanvasElement>) => void;
  onPointerMove: (e: React.PointerEvent<HTMLCanvasElement>) => void;
  onPointerUp: (e: React.PointerEvent<HTMLCanvasElement>) => void;
  onWheel: (e: React.WheelEvent<HTMLCanvasElement>) => void;
  onContextMenu: (e: React.MouseEvent<HTMLCanvasElement>) => void;
  onTouchStart: (e: React.TouchEvent<HTMLCanvasElement>) => void;
  onTouchMove: (e: React.TouchEvent<HTMLCanvasElement>) => void;
  onTouchEnd: (e: React.TouchEvent<HTMLCanvasElement>) => void;
  sidebarWidth: number;
  children?: React.ReactNode;
}

export function CanvasRenderer(props: CanvasRendererProps): JSX.Element {
  const { canvasRef, containerRef, isDrawActive, sidebarWidth, children, ...handlers } = props;
  
  return (
    <div
      ref={containerRef}
      style={{
        width: `calc(100% - ${sidebarWidth}px)`,
        height: 'calc(100vh - 60px)',
      }}
      className="relative overflow-hidden"
    >
      <canvas
        ref={canvasRef}
        role="img"
        aria-label="Drawing canvas"
        className={isDrawActive ? 'cursor-crosshair' : 'cursor-default'}
        style={{ touchAction: 'none' }}
        {...handlers}
      />
      {children}
    </div>
  );
}

// Tests verify: canvas rendering, event handlers, cursor states, children rendering
```

---

## Metrics

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| DrawingCanvas.tsx Lines | 971 | 902 | -69 (-7%) |
| Total Files | 48 | 56 | +8 |
| UI Components | 1 | 6 | +5 |
| Component Tests | 0 | 41 | +41 (5 initial + 36 in Phase 6) |
| Test Coverage (Components) | 0% | ~95% | +95% |
| Bundle Size | 160.01 KB | 161.02 KB | +1.01 KB |

---

## Component Architecture

### Composition Pattern

```typescript
// DrawingCanvas.tsx (simplified)
export function DrawingCanvas() {
  // Hooks for state management
  const drawingState = useDrawingState();
  const viewportTransform = useViewportTransform();
  
  // Event handlers
  const handlePointerDown = (e) => { /* ... */ };
  const handleWidthChange = (width) => { /* ... */ };
  
  return (
    <div className="fixed inset-0">
      <CanvasRenderer
        canvasRef={canvasRef}
        isDrawActive={isDrawActive}
        onPointerDown={handlePointerDown}
        sidebarWidth={sidebarWidth}
      >
        <WidthHUD
          selectedLine={selectedLine}
          position={hudPosition}
          onWidthChange={handleWidthChange}
        />
        <DrawButton
          isActive={isDrawActive}
          onToggle={toggleDrawMode}
          sidebarWidth={sidebarWidth}
        />
      </CanvasRenderer>
      
      <Sidebar
        collapsed={sidebarCollapsed}
        onToggle={toggleSidebar}
        lineSummary={lineSummary}
        currentScale={currentScale}
      />
      
      <BottomBar
        zoom={viewportScale}
        canZoomIn={canZoomIn}
        canZoomOut={canZoomOut}
        onZoomIn={handleZoomIn}
        onZoomOut={handleZoomOut}
        onResetZoom={handleResetZoom}
      />
    </div>
  );
}
```

---

## Testing Strategy

### Test Organization (Phase 5 + 6)
```
src/components/DrawingCanvas/__tests__/
├── DrawButton.test.tsx (5 tests)
├── Sidebar.test.tsx (8 tests)
├── BottomBar.test.tsx (9 tests)
├── WidthHUD.test.tsx (10 tests)
└── CanvasRenderer.test.tsx (9 tests)
```

### Testing Approach
- **React Testing Library:** Component rendering and interaction testing
- **User Events:** Simulate user interactions (clicks, input changes)
- **Accessibility:** Verify ARIA labels and roles
- **Props Testing:** Verify components respond correctly to prop changes
- **Edge Cases:** Null values, empty states, disabled states

---

## Lessons Learned

1. **Component Composition:** Small, focused components are easier to test and maintain
2. **Props Interface:** Well-defined prop interfaces improve type safety
3. **Children Pattern:** CanvasRenderer accepting children enables flexible composition
4. **Accessibility:** Adding ARIA labels during extraction improves accessibility
5. **Test Coverage:** Component tests catch UI regressions early

---

## Related ADRs

- **ADR-004:** Extract Custom Hooks (components use hooks for state)
- **ADR-006:** Optimization & Polish (comprehensive component testing)

---

## References

- Phase 5 Summary: `docs/phases/PHASE_5_SUMMARY.md`
- UI Components: `src/components/DrawingCanvas/`
- Component Tests: `src/components/DrawingCanvas/__tests__/`
- Refactor Scorecard: `docs/REFACTOR_SCORECARD.md`

