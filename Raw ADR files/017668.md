---
type: DRR
winner_id: lightweight-canvas-stripchart-with-vanilla-javascript
created: 2025-12-23T19:21:21-08:00
content_hash: d63f7cd464e3a4a1efb3d90086e0f1cf
---

# Lightweight Canvas Stripchart with Vanilla JavaScript for SpeedData v0.3

## Context
SpeedData v0.3 stripchart frontend requires real-time scrolling time-series visualization:

**Requirements:**
- Display live data from WebSocket stream (existing server.js broadcasts AVRO-decoded JSON)
- Scrolling chart: newest data on right (time=0), oldest scrolls left and falls off
- Fixed time window (configurable duration, e.g., 30 seconds)
- FIFO queue behavior (circular buffer)
- Multiple charts per HTML page
- Signal selector: channel.signal notation (e.g., "example.voltage")
- CSS theming: dark mode (black bg, yellow lines), light mode (white bg, blue lines)
- Standard HTML/CSS conventions (no custom syntax like `<span signals=[...]>`)
- CSS-based positioning (flexbox, grid, etc.)
- No server changes (client-side signal filtering)

**User Constraints:**
- **Independence prioritized:** "I'd like to be as independent as possible"
- **Avoid libraries:** "I might want more LOC to avoid libraries. node/js libraries seem to bring in fragility"
- **No import-by-default:** "let's not go import by default"

**Current State:**
- Simple text display (index.html with `<span id="field">` elements)
- WebSocket client (frontend.js) updates spans with latest values
- No charting capability yet

## Decision
**Selected Option:** lightweight-canvas-stripchart-with-vanilla-javascript

**Adopt Lightweight Canvas Stripchart with Vanilla JavaScript**

**Implementation:**
```html
<canvas class="stripchart"
        data-signals="example.voltage,example.current"
        data-window="30"
        data-height="300"
        data-theme="auto">
</canvas>
```

**Core Components:**
1. **Stripchart Class** (~5 KB vanilla JavaScript)
   - Canvas 2D rendering with requestAnimationFrame loop
   - Circular buffer for FIFO time-windowed data
   - Auto-scaling Y axis based on data range
   - Theme detection (prefers-color-scheme media query)
   - Grid and axes rendering

2. **Data Management:**
   - Map<signalName, Array<{time, value}>> for multi-signal buffering
   - FIFO eviction: push new data, shift old data outside time window
   - Performance: Array methods (push/shift) with periodic cleanup

3. **Rendering:**
   - Canvas clearRect() + full redraw each frame
   - X-axis: right edge = now, left edge = now - window_duration
   - Y-axis: auto-scale based on min/max of all buffered values
   - requestAnimationFrame for smooth 60fps updates

4. **WebSocket Integration:**
   - Global listener parses JSON, routes to chart instances by signal name
   - Each chart filters for configured signals (data-signals attribute)
   - Signal mapping: "channel.signal" split on dot

5. **Theming:**
   - getThemeColors() checks data-theme attribute or prefers-color-scheme
   - Dark: #000 background, #FFFF00 lines, #333 grid, #CCC text
   - Light: #FFF background, #0000FF lines, #DDD grid, #333 text

**Dependencies:**
- Zero npm packages
- Native browser APIs only: Canvas 2D, requestAnimationFrame, Array, MediaQueryList

## Rationale
**Why Vanilla JS won:**

1. **Perfect User Alignment (Primary Factor):**
   - User explicitly stated: "I'd like to be as independent as possible"
   - "I might want more LOC to avoid libraries. node/js libraries seem to bring in fragility"
   - "let's not go import by default"
   - Vanilla JS achieves **zero npm dependencies** with **simplest architecture**

2. **Minimal Code Size:**
   - ~5 KB implementation vs ~10-15 KB Web Components
   - Smallest possible solution meeting all requirements
   - No framework overhead, no abstraction layers

3. **Simplicity:**
   - Direct Canvas API calls (no Shadow DOM complexity)
   - No custom element lifecycle (constructor, connectedCallback, etc.)
   - Easier to understand, debug, and maintain
   - Lower learning curve for contributors

4. **Performance Validated:**
   - Canvas 2D proven for real-time rendering (MDN official docs, 2025)
   - requestAnimationFrame syncs with display refresh (60 Hz, auto-pauses when inactive)
   - CanvasJS benchmark: 100,000 datapoints in milliseconds
   - Handles target workload (100+ Hz decimated data)

5. **Browser Compatibility:**
   - Canvas API universal in modern browsers
   - No polyfill needed (vs Web Components Chrome 54+, Firefox 63+, Safari 10.1+)
   - MediaQueryList (prefers-color-scheme) widely supported

6. **Proven Pattern:**
   - MDN official documentation validates approach
   - StreamingDataManager working example (Medium, July 2025)
   - Circular buffer FIFO implementations on GitHub
   - Industry standard: requestAnimationFrame over setInterval

**Trade-offs Accepted:**

1. **Manual Implementation:** Grid, axes, scaling all custom code (vs Web Components built-in features). User explicitly accepts "more LOC to avoid libraries."

2. **Weaker Encapsulation:** Global scope vs Shadow DOM isolation. Acceptable for single-page stripchart app. Can use module pattern if needed.

3. **No Component Reusability:** Each page includes Stripchart class. Acceptable for v0.3 scope.

4. **Limited Features:** No built-in zoom/pan/legends. Can add incrementally as needed.

**Why Web Components rejected:**

- More complexity (Shadow DOM API, custom element lifecycle)
- Larger code size (~10-15 KB vs ~5 KB)
- Browser compatibility concerns (polyfill adds dependency)
- User didn't request component encapsulation
- Simplicity preferred over component architecture for v0.3

### Characteristic Space (C.16)
- Vanilla JavaScript implementation (zero frameworks)
- Canvas 2D API for rendering
- requestAnimationFrame for 60fps animation loop
- Circular buffer FIFO for time-windowed data
- Auto-scaling Y axis based on data range
- CSS theming via data attributes and prefers-color-scheme
- Standard HTML canvas elements with data attributes
- WebSocket integration with existing server
- Zero npm dependencies (native browser APIs only)
- ~5 KB implementation size
- Multi-chart support (multiple canvas elements per page)
- Signal selector: channel.signal dot notation
- Performance: 100-1000 Hz data rates supported

## Consequences
**Immediate Implementation Actions:**

1. **Create stripchart.js module:**
   - Stripchart class with constructor, data buffer, rendering methods
   - Canvas setup, theme detection, auto-scaling
   - WebSocket integration via global listener
   - Export: DOMContentLoaded listener initializes all `canvas.stripchart` elements

2. **Update index.html:**
   - Replace `<span>` text displays with `<canvas class="stripchart">` elements
   - Add data attributes: data-signals, data-window, data-height, data-theme
   - Include `<script src="stripchart.js"></script>`

3. **Update frontend.js:**
   - Keep existing WebSocket connection
   - Add chart routing: parse data, call chart.addDataPoint(signal, value)
   - Charts array: global registry of Stripchart instances

4. **Add CSS theming:**
   - Base styles for `canvas.stripchart` (display: block, width, border)
   - Optional: dark/light mode overrides (if not using data-theme="auto")

5. **Testing:**
   - Verify multi-signal plotting (voltage + current on same chart)
   - Verify FIFO window (data older than 30s falls off)
   - Verify scrolling (newest on right, oldest on left)
   - Verify theme switching (dark/light via data-theme or prefers-color-scheme)
   - Verify multi-chart pages (multiple canvas elements work independently)

**Code Structure:**

```
stripchart/
├── frontend/
│   ├── index.html         # Updated with <canvas> elements
│   ├── frontend.js        # Updated with chart routing
│   ├── stripchart.js      # NEW: Stripchart class (~5 KB)
│   └── style.css          # Optional: canvas theming
└── server/
    └── server.js          # No changes needed
```

**Architectural Impact:**

- Frontend becomes pure vanilla JS (no frameworks, no libraries)
- All code under direct control (no external dependencies)
- Maintenance burden: all bugs are ours, but full understanding and control
- Future extensibility: can add zoom/pan/legends incrementally as needed

**Performance Expectations:**

- 60fps smooth scrolling (requestAnimationFrame sync)
- Handles 100+ Hz decimated data (Canvas 2D validated)
- Memory stable (circular buffer FIFO prevents growth)
- CPU auto-pauses when tab inactive (requestAnimationFrame feature)

**Future Evolution (v0.4+):**

- **If component reusability needed:** Migrate to Web Components (already researched)
- **If advanced features needed:** Add zoom (mouse wheel), pan (drag), crosshairs (mouse move)
- **If performance insufficient:** Optimize rendering (dirty rect tracking, off-screen canvas)
- **If bundle size critical:** Already minimal (~5 KB)

**Technical Debt Incurred:**

- Manual grid/axes rendering (not using library helpers)
- No plugin ecosystem (each feature is custom development)
- Weaker encapsulation than Web Components (global scope)
- Must document CSS theming approach for users

**Constraints Accepted:**

- v0.3 scope: basic stripcharts (time-series line plots)
- No advanced features (zoom, pan, annotations, multiple Y-axes)
- Single time axis per chart (no dual-axis support)
- CSS positioning (user responsible for layout)

**Success Criteria:**

- Canvas elements render live data from WebSocket
- Scrolling behavior: newest right, oldest left, FIFO window
- Dark/light theme switching works
- Multiple independent charts on single page
- Zero npm dependencies maintained
- Performance handles ~100 Hz decimated data with multiple signals
