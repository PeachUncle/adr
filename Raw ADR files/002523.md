# ADR-004: Storage Manager Architecture

Date: 2025-07-24
Status: Accepted
Deciders: LocateFlow Development Team

## Context

The LocateFlow Chrome extension requires persistent storage for user preferences and locator history. Chrome extensions have specific storage APIs and limitations that need to be handled gracefully. The system must support:

- User preference persistence across browser sessions
- Automatic locator history management with capacity limits
- Storage quota management and cleanup
- Error handling for storage failures
- Data validation and integrity

## Decision

Implement a centralized StorageManager class that wraps Chrome's storage API with the following architecture:

### Core Components:
1. **StorageManager Class**: Main interface for all storage operations
2. **Automatic History Management**: Separate method for copy-triggered history entries
3. **Quota Management**: Proactive cleanup when storage limits are approached
4. **Data Validation**: Integration with data models for type safety

### Key Methods:
- `savePreferences()` / `loadPreferences()`: User settings management
- `saveToHistory()` / `loadHistory()`: Manual history operations
- `addToHistoryOnCopy()`: Automatic history entry creation (Task 3.2)
- `cleanupStorage()`: Quota management and old entry removal
- `getStorageStats()`: Usage monitoring and health checks

### Storage Strategy:
- **Chrome Local Storage**: Primary storage for all data
- **Newest-First Ordering**: History maintained with most recent entries first
- **Capacity Management**: Automatic removal of oldest entries when limits exceeded
- **Unique ID Generation**: History entries get unique IDs with timestamp components

## Consequences

### Positive:
- **Centralized Storage Logic**: All storage operations go through single interface
- **Automatic History Management**: Seamless user experience with copy-triggered history
- **Quota Safety**: Proactive cleanup prevents storage quota errors
- **Type Safety**: Integration with data models ensures data integrity
- **Error Resilience**: Graceful handling of storage failures with fallbacks
- **Testability**: Comprehensive test coverage with Chrome API mocking

### Negative:
- **Additional Complexity**: Separate methods for different history use cases
- **Memory Overhead**: In-memory operations for history management
- **Chrome Dependency**: Tightly coupled to Chrome storage API

### Mitigation:
- **Clear Method Separation**: `saveToHistory()` for manual saves, `addToHistoryOnCopy()` for automatic
- **Efficient Operations**: Minimal memory usage with array slicing for capacity management
- **Mock Strategy**: Comprehensive Chrome API mocking for testing independence

## Implementation Notes

### TDD Implementation:
- **RED Phase**: 9 comprehensive failing tests for history management
- **GREEN Phase**: Minimal implementation with `addToHistoryOnCopy()` method
- **REFACTOR Phase**: Extracted helper methods for ID generation and entry creation

### History Management Features:
- **Automatic Entry Creation**: `addToHistoryOnCopy()` creates entries when locators are copied
- **Unique ID Generation**: `generateHistoryId()` creates timestamp-based unique identifiers
- **Capacity Enforcement**: Oldest-first removal when history exceeds user-defined limits
- **Data Preservation**: Complete element info and strategies maintained in history

### Error Handling Integration:
- **Storage Error Handling**: Uses centralized error handler for consistent failure management
- **Data Validation**: Validates all data before storage operations
- **Graceful Degradation**: Returns defaults when storage operations fail

### Quality Metrics:
- **Test Coverage**: 35/35 tests passing with comprehensive edge case coverage
- **Code Quality**: Private helper methods for clean separation of concerns
- **Performance**: Efficient array operations for history management
- **Reliability**: Robust error handling and data validation

### Integration Points:
- **Data Models**: Uses validation functions from shared data models
- **Error Handler**: Integrates with centralized error handling system
- **User Preferences**: Respects user-defined history limits and settings
- **Chrome APIs**: Wraps chrome.storage.local with error handling and validation

This architecture provides a solid foundation for all storage needs while maintaining data integrity and user experience quality.