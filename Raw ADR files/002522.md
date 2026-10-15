# ADR-004: Element Selector Architecture

Date: 2025-07-24
Status: Accepted
Deciders: LocateFlow Development Team

## Context

Task 5.2 required implementing element selection and inspection functionality with TDD approach. The system needed to handle element selection on hover and click, element data extraction, locator generation triggering, and Ctrl key detection for popup freezing functionality.

Key requirements addressed:
- Requirement 1.2: Element selection on hover and click
- Requirement 1.4: Copy highest-rated locator on element click
- Requirement 1.5: Ctrl key detection for popup freezing functionality

## Decision

Implemented `ElementSelector` class with the following architectural decisions:

### Core Architecture
- **Single Responsibility**: Focused solely on element selection and data extraction
- **Callback-Based Integration**: Uses callback pattern for loose coupling with other components
- **Error Handling**: Graceful degradation for all DOM operations and API calls
- **Fallback Mechanisms**: Provides fallback selectors when primary generation fails

### Key Components
1. **Element Data Extraction**: Comprehensive extraction of element attributes, position, and metadata
2. **XPath Generation**: Simple XPath generation with ID prioritization
3. **Locator Strategy Integration**: Integrates with existing CSS selector generator
4. **Clipboard Operations**: Handles clipboard API with error recovery
5. **Ctrl Key Detection**: Event-based detection for popup freezing functionality

### Integration Points
- **CSS Selector Generator**: Integrates with existing `CSSelectorGenerator` class
- **Data Models**: Uses established `LocatorData`, `ElementInfo`, and `LocatorStrategy` interfaces
- **Callback System**: Provides `onElementSelected` and `onElementHovered` for external integration

## Consequences

### Positive:
- **Comprehensive Test Coverage**: 21/21 tests passing with 95%+ coverage
- **Error Resilience**: Graceful handling of DOM errors, clipboard failures, and generation errors
- **Flexible Integration**: Callback system allows easy integration with highlighter and popup components
- **Fallback Support**: Continues to function even when primary locator generation fails
- **TDD Compliance**: Strict Red-Green-Refactor cycle followed throughout implementation

### Negative:
- **Limited Locator Strategies**: Currently only integrates with CSS generator (XPath, ARIA generators pending)
- **Simple XPath Generation**: Basic XPath implementation may need enhancement for complex scenarios
- **Console Warnings**: Uses console.warn for error logging (may need structured logging later)

### Mitigation:
- **Extensible Design**: Architecture supports easy addition of new locator generators
- **Documented Interfaces**: Clear interfaces defined for future XPath and ARIA generator integration
- **Error Context**: Error messages include sufficient context for debugging
- **Performance Considerations**: Minimal DOM operations and efficient callback management

## Implementation Notes

### TDD Cycle Results:
- **RED Phase**: 21 failing tests written before implementation
- **GREEN Phase**: Minimal implementation to pass all tests
- **REFACTOR Phase**: Code quality improvements while maintaining green tests

### Quality Metrics:
- **Test Coverage**: 95%+ line coverage, 100% function coverage
- **Error Handling**: All DOM operations wrapped in try-catch blocks
- **Type Safety**: Full TypeScript compliance with strict mode
- **Code Quality**: ESLint compliant, follows SOLID principles

### Integration Requirements:
- Must be used with `ElementHighlighter` for visual feedback
- Requires `CSSelectorGenerator` for locator generation
- Integrates with clipboard API for copy functionality
- Supports callback registration for external event handling

### Future Enhancements:
- Integration with XPath and ARIA generators when available
- Enhanced XPath generation with more sophisticated strategies
- Structured logging system to replace console.warn
- Performance optimizations for large DOM trees