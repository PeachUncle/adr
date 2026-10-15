# ADR-006: XPath Expression Generation Engine

Date: 2025-07-24
Status: Accepted
Deciders: LocateFlow Development Team

## Context

The LocateFlow Chrome Extension requires an XPath expression generation system that can create optimized, reliable XPath expressions for DOM elements. The system must leverage native browser XPath evaluation capabilities and provide comprehensive confidence scoring for different XPath strategies.

## Decision

We have implemented a priority-based XPath generation engine with native browser integration:

### Priority Strategy:
1. **ID-based XPath** (highest reliability) - `//button[@id="submit"]`
2. **Attribute-based XPath** (name, type, data-* attributes) - `//input[@name="username"]`
3. **Class-based XPath** (with contains() functions) - `//div[contains(@class, "container")]`
4. **Text content-based XPath** - `//button[text()="Click Me"]`
5. **Position-based XPath** (parent/child relationships) - `//div[@class="parent"]/button[2]`
6. **Absolute XPath** (fallback) - `//span`

### Core Components:
- `XPathGenerator` class with comprehensive XPath expression generation
- Native browser XPath evaluation using `document.evaluate()`
- XPath-specific stability scoring algorithm (0-100 scale)
- Multi-factor confidence assessment with XPath-specific warnings

### Key Features:
- Multi-class combination with `and` operators for efficiency
- Sibling position calculation for hierarchy-based expressions
- Absolute path detection with fragility warnings
- Position-based selector penalties in confidence scoring

## Consequences

### Positive:
- Native browser XPath evaluation ensures maximum compatibility
- Comprehensive XPath strategy coverage for diverse DOM structures
- Optimized expressions with performance considerations
- Detailed confidence scoring with XPath-specific factors
- High test coverage (96.09%) ensures reliability

### Negative:
- XPath evaluation may be slower than CSS selector validation
- Position-based XPath expressions are inherently fragile
- Complex multi-class XPath expressions may be harder to debug
- Browser XPath support variations across different environments

### Mitigation:
- Implement performance monitoring for XPath evaluation
- Provide clear warnings for fragile position-based expressions
- Document XPath expression patterns for debugging support
- Test across multiple browser versions for compatibility
- Fallback to simpler expressions when complex ones fail

## Implementation Notes

### Technical Details:
- Uses `XPathResult.ORDERED_NODE_SNAPSHOT_TYPE` for reliable evaluation
- Follows TDD methodology with 26 comprehensive test cases
- Implements clean architecture with separation of concerns
- Provides extensive JSDoc documentation with examples

### XPath Optimization Features:
- Shorter expressions preferred when equally reliable
- Efficient multi-class combination: `[contains(@class, "a") and contains(@class, "b")]`
- Smart sibling position detection for hierarchy building
- Comprehensive error handling for XPath evaluation failures

### Integration Points:
- Integrates with shared data models (`LocatorStrategy`, `ConfidenceScore`)
- Compatible with Chrome extension content script environment
- Supports aggregation with other locator generation strategies

### Quality Gates:
- Minimum 90% test coverage requirement exceeded (96.09% achieved)
- ESLint compliance for code quality standards
- Comprehensive error handling for production environments
- Native browser API integration for maximum reliability