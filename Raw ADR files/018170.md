# ADR-003: Component Architecture Patterns

## Status
Accepted

## Context
The S&W Foundation Contractors Next.js application requires a consistent component architecture that supports reusability, maintainability, and the Tailwind CSS design system. Current components show inconsistent patterns and need standardization.

## Decision
Implement a layered component architecture with clear patterns for layout, UI components, and page-specific components following atomic design principles.

## Architecture

### Component Hierarchy
```
Components Architecture (Atomic Design)
├── Atoms (Basic UI Elements)
│   ├── Button
│   ├── Input
│   ├── Text
│   └── Icon
├── Molecules (Simple Combinations)
│   ├── FormField
│   ├── SearchBox
│   ├── NavItem
│   └── Card
├── Organisms (Complex Components)
│   ├── Header
│   ├── Footer
│   ├── NavigationBar
│   ├── ContactForm
│   └── InfoSection
├── Templates (Layout Structures)
│   ├── TWLayout
│   ├── AdminLayout
│   └── BlogLayout
└── Pages (Complete Views)
    ├── AboutPage
    ├── ServicesPage
    └── ContactPage
```

### Layout Pattern
```jsx
// Standard layout pattern with getLayout
function PageComponent() {
  return <PageContent />;
}

PageComponent.getLayout = function getLayout(page) {
  return <TWLayout>{page}</TWLayout>;
};

export default PageComponent;
```

### Animation Pattern
```jsx
// Consistent animation pattern using FadeIn components
import { FadeIn, FadeInStagger } from '@/components/animations';

function AnimatedSection() {
  return (
    <FadeInStagger>
      <FadeIn>
        <Component1 />
      </FadeIn>
      <FadeIn>
        <Component2 />
      </FadeIn>
    </FadeInStagger>
  );
}
```

### Full-Width Section Pattern
```jsx
// Standard pattern for full viewport width sections
function FullWidthSection({ children, className = "" }) {
  return (
    <section className={`relative w-screen -ml-[50vw] -mr-[50vw] left-1/2 right-1/2 ${className}`}>
      <div className="relative mx-auto w-full max-w-[1600px] px-6 md:px-10">
        {children}
      </div>
    </section>
  );
}
```

## Component Standards

### File Structure
```
src/components/ComponentName/
├── ComponentName.jsx          # Main component
├── ComponentName.test.jsx     # Tests
├── ComponentName.stories.jsx  # Storybook stories (optional)
├── hooks/                     # Component-specific hooks
│   └── useComponentName.js
├── utils/                     # Component utilities
│   └── componentHelpers.js
└── index.js                  # Export file
```

### Component Template
```jsx
// ComponentName.jsx
import { forwardRef } from 'react';
import PropTypes from 'prop-types';
import { cn } from '@/utils/classNames';

const ComponentName = forwardRef(({
  variant = 'default',
  size = 'medium',
  className,
  children,
  ...props
}, ref) => {
  const baseClasses = 'base-styling-classes';
  const variantClasses = {
    default: 'default-variant-classes',
    primary: 'primary-variant-classes',
    secondary: 'secondary-variant-classes'
  };
  const sizeClasses = {
    small: 'small-size-classes',
    medium: 'medium-size-classes',
    large: 'large-size-classes'
  };

  return (
    <div
      ref={ref}
      className={cn(
        baseClasses,
        variantClasses[variant],
        sizeClasses[size],
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
});

ComponentName.displayName = 'ComponentName';

ComponentName.propTypes = {
  variant: PropTypes.oneOf(['default', 'primary', 'secondary']),
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  className: PropTypes.string,
  children: PropTypes.node
};

export default ComponentName;
```

### Hook Pattern
```jsx
// Custom hook template
import { useState, useEffect, useCallback } from 'react';

export function useCustomHook(initialValue) {
  const [state, setState] = useState(initialValue);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAction = useCallback(async (params) => {
    try {
      setLoading(true);
      setError(null);
      // Logic here
      setState(newState);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // Side effects
    return () => {
      // Cleanup
    };
  }, []);

  return {
    state,
    loading,
    error,
    handleAction
  };
}
```

## Tailwind CSS Patterns

### Design Tokens
```jsx
// Consistent design token usage
const designTokens = {
  colors: {
    primary: 'bg-red-600 hover:bg-red-700',
    secondary: 'bg-[#0b2a5a] hover:bg-[#0a2551]',
    surface: 'bg-white',
    text: 'text-neutral-900'
  },
  spacing: {
    section: 'py-8 md:py-12',
    container: 'px-6 md:px-10',
    content: 'max-w-[1600px] mx-auto'
  },
  typography: {
    heading: 'text-3xl md:text-5xl font-extrabold',
    body: 'text-base leading-relaxed',
    caption: 'text-sm text-neutral-600'
  }
};
```

### Responsive Design Pattern
```jsx
// Mobile-first responsive design
function ResponsiveComponent() {
  return (
    <div className="
      grid grid-cols-1 gap-4
      md:grid-cols-2 md:gap-6
      lg:grid-cols-3 lg:gap-8
      xl:grid-cols-4
    ">
      {/* Content */}
    </div>
  );
}
```

## Testing Patterns

### Component Testing
```jsx
// ComponentName.test.jsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ComponentName from './ComponentName';

describe('ComponentName', () => {
  it('renders with default props', () => {
    render(<ComponentName>Test Content</ComponentName>);
    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('handles user interaction', async () => {
    const user = userEvent.setup();
    const handleClick = jest.fn();
    
    render(<ComponentName onClick={handleClick}>Button</ComponentName>);
    
    await user.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('applies custom className', () => {
    const customClass = 'custom-class';
    render(<ComponentName className={customClass}>Content</ComponentName>);
    
    expect(screen.getByText('Content')).toHaveClass(customClass);
  });
});
```

## Performance Patterns

### Code Splitting
```jsx
// Lazy loading for large components
import { lazy, Suspense } from 'react';

const HeavyComponent = lazy(() => import('./HeavyComponent'));

function ParentComponent() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <HeavyComponent />
    </Suspense>
  );
}
```

### Image Optimization
```jsx
// Next.js Image optimization pattern
import Image from 'next/image';

function OptimizedImage({ src, alt, ...props }) {
  return (
    <Image
      src={src}
      alt={alt}
      fill
      sizes="(min-width: 768px) 50vw, 100vw"
      className="object-cover"
      unoptimized={process.env.NODE_ENV === 'development'}
      loader={({ src }) => src}
      {...props}
    />
  );
}
```

## Rationale

### Benefits
1. **Consistency**: Standardized patterns across all components
2. **Reusability**: Atomic design promotes component reuse
3. **Maintainability**: Clear structure makes updates easier
4. **Performance**: Built-in optimization patterns
5. **Testing**: Consistent testing approaches

### Trade-offs
- **Initial Complexity**: More structure upfront
- **Learning Curve**: Team needs to learn patterns
- **File Overhead**: More files per component

## Implementation Guidelines

### Migration Strategy
1. **New Components**: Use new patterns immediately
2. **Legacy Components**: Refactor gradually following patterns
3. **Documentation**: Update as components are refactored

### Code Review Checklist
- [ ] Follows component template structure
- [ ] Uses consistent naming conventions
- [ ] Includes proper PropTypes/TypeScript
- [ ] Has appropriate tests
- [ ] Follows Tailwind patterns
- [ ] Implements performance optimizations

## Related Decisions
- ADR-002: File Organization Structure
- ADR-004: Testing Strategy
- ADR-006: Tailwind CSS Architecture

## References
- Atomic Design Methodology
- React Component Patterns
- Tailwind CSS Best Practices
- Next.js Performance Patterns