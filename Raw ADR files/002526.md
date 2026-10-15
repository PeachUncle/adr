# ADR-005: Service Worker Architecture

Date: 2025-07-28
Status: Accepted
Deciders: LocateFlow Development Team

## Context

The LocateFlow Chrome Extension requires a background service worker to manage extension lifecycle, coordinate cross-tab communication, and handle UI state management. With Chrome's Manifest V3 requirements, we need to implement a service worker that can:

1. Manage inspection mode activation/deactivation across tabs
2. Handle content script injection and communication
3. Update extension icon and badge based on state
4. Coordinate state between popup UI and content scripts
5. Provide error handling and logging capabilities

## Decision

We have implemented a centralized `ServiceWorker` class that follows these architectural principles:

### Core Architecture
- **Single Responsibility**: Each method handles a specific aspect of service worker functionality
- **Event-Driven Communication**: Uses Chrome's message passing API for cross-component communication
- **State Management**: Maintains per-tab inspection state using a Map data structure
- **Error Handling**: Comprehensive error handling with logging for debugging

### Key Components
1. **Lifecycle Management**: Handles extension installation and initialization
2. **Message Routing**: Central message handler that routes actions to appropriate methods
3. **State Coordination**: Per-tab state tracking with cross-tab broadcasting
4. **UI Updates**: Badge and icon updates based on inspection state
5. **Content Script Management**: Injection and communication with content scripts

### Communication Protocol
```typescript
interface ExtensionMessage {
  action: 'activateInspection' | 'deactivateInspection' | 'getInspectionState';
  tabId?: number;
  [key: string]: any;
}
```

### State Management Strategy
- Per-tab inspection state stored in `Map<number, boolean>`
- State changes broadcast to all tabs for UI consistency
- Automatic cleanup when tabs are closed or navigated

## Consequences

### Positive:
- **Centralized Control**: Single point of control for all background operations
- **Scalable Architecture**: Easy to add new message types and functionality
- **Robust Error Handling**: Comprehensive error handling prevents extension crashes
- **Cross-Tab Consistency**: State synchronization ensures consistent UI across tabs
- **Testable Design**: Clear interfaces and dependency injection enable comprehensive testing

### Negative:
- **Memory Usage**: Per-tab state storage increases memory footprint
- **Complexity**: Central message routing adds complexity for simple operations
- **Chrome API Dependency**: Tightly coupled to Chrome extension APIs

### Mitigation:
- **Memory Management**: Automatic cleanup of tab state on tab removal
- **Documentation**: Comprehensive JSDoc and ADR documentation
- **Testing**: Extensive test coverage with mocked Chrome APIs
- **Error Boundaries**: Graceful degradation when Chrome APIs fail

## Implementation Notes

### TDD Implementation
The service worker was implemented using strict Test-Driven Development:
1. **RED Phase**: 17 failing tests written first to define expected behavior
2. **GREEN Phase**: Minimal implementation to pass all tests
3. **REFACTOR Phase**: Code organization and documentation improvements

### Chrome API Integration
- Uses Manifest V3 service worker patterns
- Implements proper async message handling with response callbacks
- Handles Chrome API failures gracefully with try-catch blocks
- Maintains compatibility with Chrome extension security policies

### Testing Strategy
- Comprehensive Chrome API mocking for isolated unit testing
- 17 test cases covering all functionality and error scenarios
- Mock-based testing enables fast, reliable test execution
- Test coverage includes edge cases and error conditions

### Future Extensibility
The architecture supports easy extension for:
- Additional message types and actions
- New UI state management requirements
- Enhanced error reporting and analytics
- Cross-extension communication capabilities