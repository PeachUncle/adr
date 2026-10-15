# ADR-006: Content Script Injection Retry Mechanism

Date: 2025-07-28
Status: Accepted
Deciders: LocateFlow Development Team

## Context

The Chrome extension needs to inject content scripts into web pages to enable element inspection functionality. However, content script injection can fail due to various reasons:

1. **Network issues**: Temporary connectivity problems
2. **Tab state issues**: Page not fully loaded or in transition
3. **Permission issues**: Restricted page types (chrome://, file://, extension pages)
4. **Resource contention**: Browser busy with other operations

The original implementation had basic error handling but lacked:
- Retry logic for transient failures
- Exponential backoff to avoid overwhelming the browser
- Fallback mechanisms for unsupported page types
- Proper error categorization and user feedback

## Decision

Implement an enhanced content script injection system with:

### 1. Exponential Backoff Retry Logic
- Maximum 3 retry attempts for failed injections
- Exponential backoff delays: 1000ms, 2000ms, 4000ms
- Immediate failure for unsupported page types (no retries)

### 2. Page Type Detection and Fallback
- Pre-injection validation of page URL compatibility
- Explicit rejection of unsupported page types:
  - `chrome://` pages (browser internal pages)
  - `chrome-extension://` pages (extension pages)
  - `file://` pages (local file system)
  - `moz-extension://` and `edge-extension://` (other browser extensions)
- Clear error messages for unsupported page types

### 3. Enhanced Error Handling
- Categorized error messages for different failure types
- Context preservation for debugging purposes
- Graceful degradation without crashing the extension

### 4. Test-Driven Implementation
- Comprehensive test coverage for all retry scenarios
- Mock-based testing to avoid actual delays in test execution
- Edge case coverage for various failure modes

## Consequences

### Positive:
- **Improved Reliability**: Transient failures are automatically retried
- **Better User Experience**: Clear error messages for unsupported pages
- **Reduced Support Burden**: Fewer user reports of injection failures
- **Maintainable Code**: Well-tested retry logic with clear separation of concerns
- **Performance Optimization**: Exponential backoff prevents browser overload

### Negative:
- **Increased Complexity**: More code paths and error handling logic
- **Potential Delays**: Users may experience slight delays during retry attempts
- **Resource Usage**: Additional memory for retry state management

### Mitigation:
- **Comprehensive Testing**: TDD approach ensures all edge cases are covered
- **Timeout Limits**: Maximum retry attempts prevent infinite retry loops
- **Clear Documentation**: ADR and inline comments explain retry behavior
- **Performance Monitoring**: Logging enables tracking of retry frequency

## Implementation Notes

### Core Components:

1. **`isPageSupported(tabId: number)`**: Validates page URL compatibility
2. **`injectContentScriptWithRetry(tabId: number, maxRetries: number)`**: Implements retry logic
3. **`delay(ms: number)`**: Utility for creating async delays

### Retry Algorithm:
```typescript
for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
        await chrome.scripting.executeScript({...});
        return; // Success
    } catch (error) {
        if (attempt < maxRetries) {
            const delay = 1000 * Math.pow(2, attempt - 1);
            await this.delay(delay);
        }
    }
}
throw new Error(`Failed after ${maxRetries} attempts`);
```

### Error Message Format:
- Page compatibility: "Content script injection not supported on this page type"
- Tab query failures: "Failed to query tab information: [specific error]"
- Injection failures: "Failed to inject content script after [N] attempts: [specific error]"

### Testing Strategy:
- Mock `chrome.scripting.executeScript` for different failure scenarios
- Mock `chrome.tabs.query` for page type testing
- Mock `setTimeout` to avoid actual delays in tests
- Verify exact retry counts and delay timings
- Test all supported and unsupported page types

This implementation ensures robust content script injection while maintaining clear error handling and user feedback for unsupported scenarios.