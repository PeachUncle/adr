# ADR 008: Multi-layered testing strategy

## Status

Accepted

## Context

The portfolio website combines complex 3D graphics, interactive features, and accessibility requirements. We need a comprehensive testing strategy that covers all aspects while maintaining development velocity.

Testing challenges:

- 3D rendering is difficult to test in traditional unit tests
- Accessibility testing requires specialized tools
- Performance testing needs real device metrics
- Cross-browser compatibility for WebGL features

## Decision

We will implement a multi-layered testing strategy with different tools and approaches for different types of testing.

## Consequences

### Positive

- **Quality Assurance** - Comprehensive coverage of all features
- **Regression Prevention** - Automated detection of breaking changes
- **Accessibility Compliance** - Automated accessibility testing
- **Performance Monitoring** - Continuous performance validation
- **Developer Confidence** - Safe refactoring and feature development
- **Documentation** - Tests serve as living documentation

### Negative

- **Development Overhead** - Additional time for writing and maintaining tests
- **CI/CD Complexity** - Longer build times and more complex pipelines
- **Tool Maintenance** - Multiple testing tools to keep updated
- **False Positives** - Flaky tests can block development

### Testing Layers

#### 1. Unit Tests (Vitest + React Testing Library)

- **Component Logic** - React component behavior and props
- **Utility Functions** - Pure functions and data transformations
- **Hooks** - Custom React hooks with renderHook
- **State Management** - Zustand store behavior
- **Validation** - Form validation and data schemas

#### 2. Integration Tests

- **API Routes** - Next.js API endpoint testing
- **Data Loading** - Content loading and error handling
- **3D Component Integration** - Mocked Three.js interactions
- **State Persistence** - localStorage and session storage

#### 3. End-to-End Tests (Playwright)

- **Critical User Journeys** - Home → Project → Contact flow
- **3D Interactions** - Click, hover, and keyboard navigation
- **Accessibility** - Screen reader and keyboard testing
- **Cross-browser** - Chrome, Firefox, Safari, Edge
- **Mobile Testing** - Touch interactions and responsive design

#### 4. Visual Regression Tests

- **3D Scene Rendering** - Screenshot comparison for consistency
- **UI Components** - Visual state testing across themes
- **Responsive Design** - Layout testing at different breakpoints
- **Animation States** - Motion and transition testing

#### 5. Performance Tests

- **Lighthouse CI** - Core Web Vitals and performance scores
- **Bundle Analysis** - JavaScript bundle size monitoring
- **3D Performance** - FPS and memory usage testing
- **Load Testing** - Server performance under load

#### 6. Accessibility Tests

- **Automated Testing** - axe-core integration in unit and E2E tests
- **Manual Testing** - Screen reader and keyboard navigation
- **Color Contrast** - Automated contrast ratio checking
- **Focus Management** - Tab order and focus indicator testing

### Test Organization

- **Test Co-location** - Tests near the code they test
- **Shared Utilities** - Common test helpers and mocks
- **Test Data** - Fixtures and mock data management
- **CI/CD Integration** - Parallel test execution and reporting
