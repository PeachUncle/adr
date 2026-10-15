# ADR-005: On-Page Popup Architecture

Date: 2025-07-24
Status: Accepted
Deciders: LocateFlow Development Team

## Context

The LocateFlow Chrome Extension requires an on-page popup UI that appears when users hover over elements during inspection mode. This popup must provide a tabbed interface for locators and ARIA information, with keyboard hotkey support for efficient navigation.

### Requirements
- 2.3: Tabbed interface to organize different views (Locators, ARIA)
- 2.4: Keyboard hotkey support for tab switching (1, 2, 3...)
- 4.1: Dedicated ARIA tab in on-page popup

### Constraints
- Must work within Chrome extension content script environment
- Should not interfere with page functionality
- Must be positioned intelligently to avoid screen edges
- Should provide copy functionality for locators

## Decision

We will implement an OnPagePopup class with the following architecture:

### Core Components
1. **Popup Container Management**: Creates and positions popup elements
2. **Tabbed Interface**: Provides organized views for different content types
3. **Keyboard Handler**: Manages hotkey support for tab switching
4. **Copy Functionality**: Enables locator copying with callback system

### Key Design Decisions

#### 1. Smart Positioning System
- Default positioning with 10px offset from cursor
- Edge detection to prevent popup from going off-screen
- Fixed positioning with maximum z-index for visibility

#### 2. Tabbed Interface Architecture
- Separate tab container and content container
- Active tab state management
- Click handlers for tab switching
- Keyboard hotkey integration (1, 2, 3...)

#### 3. Event-Driven Architecture
- Callback system for copy operations
- Document-level keyboard event handling
- Proper cleanup of event listeners

#### 4. DOM Integration Strategy
- Direct DOM manipulation for performance
- HTML string generation for complex content
- Event delegation for copy button handling

## Implementation Details

### Class Structure
```typescript
export class OnPagePopup {
  private keydownHandler: ((event: KeyboardEvent) => void) | null = null;
  private copyCallback: CopyCallback | null = null;

  public show(position: PopupPosition, strategies: LocatorStrategy[]): void
  public hide(): void
  public onCopy(callback: CopyCallback): void
}
```

### Positioning Algorithm
1. Calculate default position (cursor + 10px offset)
2. Check if popup would exceed screen boundaries
3. Adjust position to keep popup visible
4. Apply fixed positioning with maximum z-index

### Tab Management
- Locators tab (hotkey: 1) - displays generated locators with copy buttons
- ARIA tab (hotkey: 2) - provides ARIA snapshot functionality
- Active state management through CSS classes

### Keyboard Hotkey System
- Document-level keydown event listener
- Number key detection (1-9)
- Tab switching through programmatic click events
- Event prevention for handled keys

## Consequences

### Positive
- **User Experience**: Intuitive tabbed interface with keyboard shortcuts
- **Performance**: Direct DOM manipulation for fast rendering
- **Flexibility**: Callback system allows easy integration with other components
- **Accessibility**: ARIA-focused tab for accessibility testing
- **Reliability**: Smart positioning prevents UI issues

### Negative
- **DOM Pollution**: Adds elements to page DOM (mitigated by cleanup)
- **Event Conflicts**: Global keyboard handler could conflict with page events
- **Maintenance**: Complex positioning logic requires careful testing

### Mitigation
- Comprehensive cleanup in hide() method
- Unique CSS classes and IDs to avoid conflicts
- Thorough testing of positioning edge cases
- Event handler cleanup to prevent memory leaks

## Implementation Notes

### CSS Classes Used
- `locateflow-popup`: Main popup container
- `locateflow-tabs`: Tab button container
- `locateflow-content`: Tab content container
- `locateflow-tab`: Individual tab button
- `locateflow-tab active`: Active tab state
- `locateflow-locators`: Locators list container
- `locateflow-aria-content`: ARIA tab content

### Integration Points
- ElementHighlighter: Provides element selection events
- ElementSelector: Supplies locator strategies
- StorageManager: Handles copy operation persistence
- Content Script: Manages popup lifecycle

### Testing Strategy
- TDD approach with comprehensive test coverage
- Mock DOM methods for isolated testing
- Event simulation for keyboard and click interactions
- Edge case testing for positioning logic

This architecture provides a robust, user-friendly on-page popup system that meets all requirements while maintaining good separation of concerns and testability.