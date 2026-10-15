# Decision Record: Migrate to Tailwind CSS

## Context
The application originally used a mix of custom CSS, Bootstrap components (b-container, b-row, b-col), and inline styles across Vue components. This led to:
- Inconsistent styling approaches
- Large CSS files with scoped styles in each component
- Difficulty maintaining visual consistency
- Bootstrap Vue components referenced but not installed as dependencies
- CSS specificity conflicts and naming issues

## Problem
The main issues were:
1. **Maintainability**: Each component had its own scoped CSS, making global changes difficult
2. **Consistency**: Mix of custom styles, Bootstrap classes, and inline styles created visual inconsistencies
3. **Bundle size**: Custom CSS was not optimized, leading to larger bundle sizes
4. **Developer experience**: Writing and maintaining custom CSS for each component was time-consuming
5. **Missing dependencies**: Bootstrap Vue components used but not properly installed

## Decision
We have decided to migrate the entire application to Tailwind CSS v3.4. This involves:
- Installing Tailwind CSS, PostCSS, and Autoprefixer
- Creating a centralized Tailwind configuration with custom utilities
- Replacing all custom CSS with Tailwind utility classes
- Converting Bootstrap grid layouts to Tailwind's flexbox and grid utilities
- Keeping only library-specific styles (Leaflet, Video.js) in scoped CSS

## Implementation Details
1. **Configuration**: Created `postcss.config.js` and `tailwind.config.js` with ES6 module syntax
2. **Custom components**: Defined reusable component classes (`.btn-primary`, `.select-field`, `.input-field`) using `@layer components`
3. **Migration scope**: 
   - All Vue components (HeaderAsso, SearchLocation, Autocomplete, Com2coQuickAccess)
   - All views (AppCarte, AppStatistics, AppInformation, AppMethodo, AppVideoAdmin)
   - Main App.vue layout
4. **Preserved styles**: Only Leaflet-specific (`.dataDetail`, `.legend`) and Video.js player styles

## Consequences

### Positive
- **Consistency**: Unified design system across all components
- **Performance**: Smaller production bundle through PurgeCSS (only used classes included)
- **Developer productivity**: Faster development with utility-first approach
- **Responsive design**: Built-in responsive utilities (sm:, md:, lg:, xl:)
- **Maintainability**: Changes in templates instead of separate CSS files
- **No naming conflicts**: Utility classes eliminate CSS specificity issues

### Negative
- **Learning curve**: Team needs to learn Tailwind's utility classes
- **Verbose templates**: More classes in HTML, though organized logically
- **Initial migration time**: Required refactoring all components

## Alternatives Considered
1. **Keep custom CSS with better organization**: Would not solve consistency and bundle size issues
2. **Install and use Bootstrap Vue properly**: Adds heavy framework dependency, not aligned with Vue 3 best practices
3. **Use CSS-in-JS solution**: Adds runtime overhead and complexity
4. **Tailwind v4**: Rejected due to breaking changes and different plugin architecture; v3 is more stable

## Expected Impact
The migration to Tailwind CSS is expected to:
- Reduce CSS bundle size by ~70% in production
- Improve development speed by 30-40%
- Eliminate CSS-related bugs from specificity conflicts
- Provide better mobile responsiveness out of the box
- Simplify onboarding for new developers with standard utility classes
- Enable rapid prototyping and design iterations
