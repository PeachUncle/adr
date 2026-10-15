---
status: accepted
date: 2025-10-03
decision-makers: [development team]
consulted: [product owner]
informed: [all team members]
---

# Use Functional Layout Testing Instead of Visual Regression Testing

## Context and Problem Statement

The current testing approach using element visibility checks (`.toBeVisible()`) failed to detect critical layout failures including 3D cube positioning conflicts and mobile typography overflow. Visual regression testing was considered but creates fundamental conflicts with incremental development by treating visual changes as test failures, severely inhibiting design iteration and creating false positives.

We need a testing approach that catches functional layout failures (content overflow, positioning conflicts, interaction blocking) without preventing visual design evolution or requiring baseline image maintenance.

## Decision Drivers

- Critical layout failures reached production despite comprehensive test coverage
- Visual regression testing inhibits incremental development by treating visual changes as failures
- Need fast execution for development workflow integration (pre-commit < 5 seconds)
- Must catch functional layout issues without false positives from visual design changes
- Support continuous design iteration without test maintenance overhead
- Provide actionable failure information for layout debugging

## Considered Options

- **Option 1**: Implement visual regression testing with baseline screenshot comparison
- **Option 2**: Enhanced element visibility testing with better assertions
- **Option 3**: Functional layout testing validating user experience behavior
- **Option 4**: Hybrid approach combining visual regression with functional testing

## Decision Outcome

Chosen option: "**Option 3: Functional layout testing validating user experience behavior**", because it catches the actual problems users experience (content overflow, invisible elements, interaction blocking) without creating false positives from visual design changes, supports rapid development iteration, and provides clear actionable feedback for layout issues.

### Consequences

- Good, because catches functional layout failures that affect user experience
- Good, because supports continuous visual design iteration without test maintenance
- Good, because provides fast execution suitable for pre-commit workflow integration
- Good, because eliminates false positives from intentional visual design changes
- Good, because offers clear, actionable failure information for debugging
- Bad, because requires developing new testing patterns and validation approaches
- Bad, because may miss purely aesthetic issues that don't affect functionality

### Confirmation

Implementation compliance will be confirmed through:

- Functional layout test suite execution speed (pre-commit checks < 5 seconds)
- Test coverage of critical layout scenarios (viewport boundaries, element positioning, responsive behavior)
- Zero false positives from visual design changes during development iterations
- Successful detection of layout failures through synthetic test scenarios
- Developer workflow integration metrics showing no development friction

## Pros and Cons of the Options

### Option 1: Visual Regression Testing

**Implementation**: Screenshot comparison against baseline images with diff analysis

- Good, because catches all visual changes including subtle layout shifts
- Good, because provides visual evidence of changes through image diffs
- Good, because well-established testing pattern with mature tooling
- Bad, because treats intentional visual changes as test failures
- Bad, because requires baseline image maintenance as design evolves
- Bad, because creates false positives that inhibit incremental development
- Bad, because slow execution time incompatible with pre-commit workflow
- Bad, because provides unclear feedback for functional vs. aesthetic changes

### Option 2: Enhanced Element Visibility Testing

**Implementation**: Improved `.toBeVisible()` assertions with additional element state validation

- Good, because builds on existing testing infrastructure with minimal changes
- Good, because fast execution suitable for all development workflow stages
- Good, because no baseline maintenance overhead
- Neutral, because limited scope may still miss critical layout issues
- Bad, because element visibility doesn't validate positioning correctness
- Bad, because doesn't detect content overflow or responsive behavior failures
- Bad, because provides limited actionable information for layout debugging

### Option 3: Functional Layout Testing (Selected)

**Implementation**: Viewport boundary validation, CSS property testing, interaction validation, responsive behavior testing

- Good, because validates user experience behavior rather than visual sameness
- Good, because catches critical layout failures affecting user interaction
- Good, because supports continuous visual design iteration without test friction
- Good, because provides specific, actionable failure information
- Good, because fast execution suitable for pre-commit integration
- Good, because eliminates false positives from intentional visual changes
- Neutral, because requires developing new testing patterns and assertions
- Bad, because may not catch purely aesthetic issues that don't affect functionality

### Option 4: Hybrid Approach

**Implementation**: Combination of functional testing for development workflow and visual regression for release validation

- Good, because combines benefits of functional testing with visual validation coverage
- Good, because allows different testing strategies for different development stages
- Neutral, because maintains some visual regression benefits while reducing development friction
- Bad, because increases testing complexity and maintenance overhead
- Bad, because still requires baseline image maintenance for visual regression component
- Bad, because mixed approach may create confusion about when tests should pass/fail

## More Information

This decision implements the testing strategy defined in story BIZ-FUNCTIONAL-LAYOUT-TESTING (025.6), focusing on functional validation that supports incremental development while preventing critical layout failures.

The approach prioritizes user experience validation over visual consistency checking, enabling continuous design iteration while maintaining layout quality assurance. Implementation will build on existing Playwright testing infrastructure (ADR-0002) with enhanced functional validation patterns.

Review criteria: This decision should be reassessed if functional testing fails to catch critical layout issues in production, or if development team reports significant friction from the testing approach.
