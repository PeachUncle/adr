# ADR-004: UI Framework Selection - Mantine

## Status
Accepted - 2025-08-17

## Context

During the React migration planning phase, we need to select a comprehensive UI framework that will serve as the foundation for all WitchCityRope user interfaces. The choice will significantly impact development velocity, accessibility compliance, maintenance overhead, and user experience quality.

### Key Requirements
- **TypeScript Support**: First-class TypeScript integration for type safety
- **Accessibility**: WCAG 2.1 AA compliance for inclusive community platform
- **Form Components**: Comprehensive form handling for registration, profiles, event creation
- **Mobile Responsiveness**: Mobile-first design for community accessibility
- **Theming**: Flexible theming to match WitchCityRope brand identity
- **Performance**: Reasonable bundle size and runtime performance
- **Community Support**: Active maintenance and documentation quality

### Evaluation Process
Comprehensive research conducted evaluating four leading React UI frameworks:
- Mantine v7
- Chakra UI
- Material-UI (MUI)
- Ant Design

**Research Document**: `/docs/architecture/react-migration/ui-framework-research.md`

## Decision

**Selected: Mantine v7** (Score: 89/100)

Mantine provides the optimal balance of features for the WitchCityRope platform migration.

### Decision Matrix Summary

| Framework | TypeScript | Accessibility | Mobile | Forms | Theming | Documentation | Community | Performance | **Total** |
|-----------|------------|---------------|---------|-------|---------|---------------|-----------|-------------|-----------|
| **Mantine** | 10 | 9 | 9 | 10 | 9 | 10 | 8 | 8 | **89** |
| Chakra UI | 9 | 10 | 9 | 8 | 9 | 9 | 8 | 8 | 86 |
| Material-UI | 9 | 8 | 9 | 9 | 9 | 8 | 10 | 6 | 82 |
| Ant Design | 10 | 6 | 8 | 9 | 8 | 8 | 9 | 6 | 75 |

### Key Differentiators

#### Why Mantine Won
1. **TypeScript-First Architecture**: Built with TypeScript from the ground up with precise type definitions
2. **Comprehensive Form System**: Advanced form handling with `@mantine/form` and built-in validation
3. **Component Completeness**: 120+ components and 70+ hooks covering all use cases
4. **Performance Optimized**: v7 removed CSS-in-JS dependencies for better performance
5. **Excellent Documentation**: Exceptional documentation quality with interactive examples
6. **Accessibility Built-in**: WCAG-compliant components with ARIA attributes out of the box

#### Community Platform Fit
- **Form-Heavy Application**: Registration, profiles, event creation, vetting applications
- **Professional Yet Approachable**: Suitable for community platform aesthetic
- **Accessibility Critical**: Built-in WCAG compliance for inclusive community
- **Mobile-First**: Strong responsive design support for community accessibility

## Consequences

### Positive Impacts
1. **Development Velocity**: TypeScript-first approach will accelerate development
2. **Form Implementation**: Comprehensive form system reduces custom validation work
3. **Accessibility Compliance**: Built-in WCAG support ensures inclusive platform
4. **Performance**: v7 performance improvements benefit user experience
5. **Maintenance**: Well-documented, consistent API reduces maintenance overhead
6. **Future-Proofing**: Active development and modern architecture

### Potential Challenges
1. **Learning Curve**: Team will need to learn Mantine patterns and conventions
2. **Community Size**: Smaller community than MUI, potentially fewer third-party resources
3. **Enterprise Maturity**: Less battle-tested in large enterprise environments

### Risk Mitigation
- **Fallback Plan**: Chakra UI (Score: 86) provides excellent alternative with larger community
- **Training**: Dedicated time for team to learn Mantine patterns during setup phase
- **Documentation**: Comprehensive internal documentation of patterns and usage

## Implementation Strategy

### Phase 1: Foundation Setup (Week 1-2)
```bash
# Core Mantine installation
npm install @mantine/core @mantine/hooks @mantine/form @mantine/notifications
```

### Theme Configuration
```typescript
import { MantineProvider, createTheme } from '@mantine/core';

const wcrTheme = createTheme({
  colors: {
    wcr: [
      '#f8f4e6', // ivory (lightest)
      '#e8ddd4',
      '#d4a5a5', // dustyRose  
      '#c48b8b',
      '#b47171',
      '#a45757',
      '#9b4a75', // plum
      '#880124', // burgundy
      '#6b0119', // darker
      '#2c2c2c'  // charcoal (darkest)
    ]
  },
  primaryColor: 'wcr',
  fontFamily: 'Source Sans 3, sans-serif',
  headings: {
    fontFamily: 'Bodoni Moda, serif'
  }
});
```

### Component Migration Priority
1. **Authentication Components**: Login, registration, password reset
2. **Form Components**: Event creation, profile management, vetting applications  
3. **Layout Components**: Navigation, headers, footers
4. **Event Management**: Event lists, details, registration
5. **Admin Interfaces**: User management, event management

## Success Metrics

### Technical Metrics
- **Bundle Size**: Target < 500KB gzipped total bundle
- **Performance**: Lighthouse score > 90
- **Accessibility**: WCAG 2.1 AA compliance (95%+ automated tests)
- **Development Velocity**: 30% faster component development vs current Blazor

### Quality Metrics
- **Component Test Coverage**: > 80%
- **Type Safety**: Zero TypeScript errors in production builds
- **Mobile Responsiveness**: 100% components mobile-optimized
- **Documentation Coverage**: All custom components documented

## References

- [Mantine Official Documentation](https://mantine.dev/)
- [UI Framework Research Document](/docs/architecture/react-migration/ui-framework-research.md)
- [React Migration Plan](/docs/architecture/react-migration/migration-plan.md)
- [WitchCityRope Design System Requirements](/docs/design/style-guide/WEBSITE_STYLE_GUIDE.md)

## Related Decisions

- **ADR-001**: Pure Blazor Server Architecture (superseded by React migration)
- **ADR-002**: Authentication API Pattern (will be preserved in React implementation)
- **ADR-003**: Playwright E2E Testing (will test Mantine components)

## Notes

- **Customization Planned**: WitchCityRope branding and colors will be applied through Mantine's theming system
- **Gradual Migration**: Mantine components will be introduced incrementally during React migration phases
- **Team Training**: Dedicated time allocated for Mantine pattern learning in migration timeline