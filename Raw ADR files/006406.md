# ADR-027: Adoption of React as Default Frontend Framework

## Status
Proposed

## Date
2025-03-02

## Context
The Aronim Bookstore application is implementing a micro-frontend architecture (ADR-025) and Backend-for-Frontend pattern (ADR-026). As we establish our frontend development approach, we need to select a default frontend framework that:

- Aligns with our micro-frontend architecture
- Supports efficient component development and reuse
- Provides good performance and user experience
- Has robust ecosystem and community support
- Enables efficient development workflows
- Facilitates testing and quality assurance
- Supports our design system and component library needs
- Integrates well with our BFF implementation using GraphQL
- Offers good developer experience and productivity
- Has long-term viability and support

While our micro-frontend architecture allows for technology flexibility, establishing a default framework will promote consistency, reduce cognitive overhead, and streamline development across teams.

## Decision
We will adopt **React** as the default frontend framework for the Aronim Bookstore application with the following implementation approach:

### 1. Core Technology Stack
- **React** as the primary UI library
- **TypeScript** for type safety and developer experience
- **React Router** for client-side routing
- **React Query** for data fetching and state management
- **Styled Components** for component styling
- **Jest** and **React Testing Library** for testing

### 2. Architecture Approach
- Implement component-based architecture following atomic design principles
- Create a shared component library based on our design system
- Use custom hooks for reusable logic
- Implement state management appropriate to the complexity level
- Enforce consistent patterns for data fetching and mutations

### 3. Development Standards
- Establish coding conventions and best practices
- Create templates for new components and micro-frontends
- Define standard folder structure and organization
- Implement consistent error handling patterns
- Establish accessibility standards and testing procedures

### 4. Integration with Micro-Frontend Architecture
- Configure React for module federation
- Implement shared runtime dependencies
- Create patterns for cross-micro-frontend communication
- Establish consistent mounting/unmounting patterns

### 5. Performance Optimization
- Implement code splitting and lazy loading
- Use React's performance optimization features
- Configure appropriate bundling and caching strategies
- Implement monitoring for React-specific metrics

## Implementation Approach

1. **Setup and Configuration**
   - Create standardized React project template
   - Configure TypeScript with appropriate settings
   - Set up linting and code formatting rules
   - Configure testing framework and utilities
   - Implement build and deployment pipeline

2. **Component Library Development**
   - Create foundational UI components
   - Implement design system tokens and themes
   - Develop layout and structural components
   - Create documentation and usage examples
   - Implement Storybook for component development

3. **Micro-Frontend Integration**
   - Configure React for module federation
   - Implement shared dependency management
   - Create patterns for micro-frontend communication
   - Establish root component patterns for micro-frontend mounting

4. **Developer Tooling**
   - Create development environment setup
   - Implement hot module replacement
   - Configure developer tools and extensions
   - Create documentation and onboarding materials
   - Implement code generators for common patterns

## Consequences

### Positive
- Strong ecosystem with extensive libraries and community support
- Well-established patterns for component development
- Good performance characteristics with virtual DOM
- Excellent developer tooling and debugging capabilities
- Declarative programming model that improves code readability
- Strong TypeScript integration for type safety
- Robust testing ecosystem
- Good integration with modern build tools
- Flexibility to adapt to different state management approaches
- Aligns with industry trends and hiring pool

### Negative
- Learning curve for developers new to React
- Need for careful performance optimization in complex applications
- Potential for inconsistent patterns without proper governance
- Risk of dependency on third-party libraries for common functionality
- Requires disciplined approach to prevent component bloat
- Need for careful state management in complex applications
- Requires additional tooling for complete application functionality

## Alternatives Considered

1. **Vue.js**
   - More approachable learning curve
   - Built-in template system
   - Good performance characteristics
   - Smaller ecosystem compared to React
   - Less TypeScript integration maturity
   - Less adoption in enterprise applications
   - Potentially smaller hiring pool

2. **Angular**
   - Comprehensive framework with built-in functionality
   - Strong TypeScript integration
   - Built-in dependency injection
   - More opinionated structure
   - Steeper learning curve
   - Heavier bundle size
   - Less flexibility for micro-frontend architecture

3. **Svelte**
   - Excellent performance with compile-time approach
   - Less boilerplate code
   - Smaller bundle sizes
   - Less mature ecosystem
   - Smaller community and hiring pool
   - Less established patterns for large applications
   - Limited tooling compared to React

4. **Web Components**
   - Framework-agnostic approach
   - Native browser support
   - Strong encapsulation
   - Limited ecosystem for complex application needs
   - More complex state management
   - Less developer tooling
   - More verbose for complex component development

## Implementation Notes

### Basic Component Structure

```tsx
// src/components/Button/Button.tsx
import React from 'react';
import styled from 'styled-components';
import { theme } from '../../styles/theme';

export type ButtonVariant = 'primary' | 'secondary' | 'tertiary';
export type ButtonSize = 'small' | 'medium' | 'large';

export interface ButtonProps {
  /** The content to display inside the button */
  children: React.ReactNode;
  /** The button's visual style */
  variant?: ButtonVariant;
  /** The button's size */
  size?: ButtonSize;
  /** Whether the button should take up the full width of its container */
  fullWidth?: boolean;
  /** Whether the button is disabled */
  disabled?: boolean;
  /** Click handler */
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  /** Additional class name */
  className?: string;
  /** Type of button */
  type?: 'button' | 'submit' | 'reset';
}

const StyledButton = styled.button<{
  variant: ButtonVariant;
  size: ButtonSize;
  fullWidth: boolean;
}>`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: ${theme.radii.md};
  font-family: ${theme.fonts.body};
  font-weight: ${theme.fontWeights.medium};
  cursor: pointer;
  transition: all 0.2s ease;
  
  /* Variant styles */
  ${props => {
    switch (props.variant) {
      case 'primary':
        return `
          background-color: ${theme.colors.primary};
          color: ${theme.colors.white};
          border: none;
          
          &:hover:not(:disabled) {
            background-color: ${theme.colors.primaryDark};
          }
        `;
      case 'secondary':
        return `
          background-color: ${theme.colors.white};
          color: ${theme.colors.primary};
          border: 1px solid ${theme.colors.primary};
          
          &:hover:not(:disabled) {
            background-color: ${theme.colors.gray100};
          }
        `;
      case 'tertiary':
        return `
          background-color: transparent;
          color: ${theme.colors.primary};
          border: none;
          
          &:hover:not(:disabled) {
            background-color: ${theme.colors.gray50};
          }
        `;
      default:
        return '';
    }
  }}
  
  /* Size styles */
  ${props => {
    switch (props.size) {
      case 'small':
        return `
          font-size: ${theme.fontSizes.xs};
          padding: ${theme.space[1]} ${theme.space[2]};
          height: 32px;
        `;
      case 'medium':
        return `
          font-size: ${theme.fontSizes.sm};
          padding: ${theme.space[2]} ${theme.space[3]};
          height: 40px;
        `;
      case 'large':
        return `
          font-size: ${theme.fontSizes.md};
          padding: ${theme.space[2]} ${theme.space[4]};
          height: 48px;
        `;
      default:
        return '';
    }
  }}
  
  /* Full width style */
  ${props => props.fullWidth && `
    width: 100%;
  `}
  
  /* Disabled state */
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'medium',
  fullWidth = false,
  disabled = false,
  onClick,
  className,
  type = 'button',
  ...props
}) => {
  return (
    <StyledButton
      type={type}
      variant={variant}
      size={size}
      fullWidth={fullWidth}
      disabled={disabled}
      onClick={onClick}
      className={className}
      {...props}
    >
      {children}
    </StyledButton>
  );
};
```

### Custom Hook Example

```tsx
// src/hooks/useGraphQLQuery.ts
import { useQuery, UseQueryOptions } from 'react-query';
import { GraphQLClient } from 'graphql-request';

// Initialize the GraphQL client
const graphqlClient = new GraphQLClient('/graphql', {
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
  },
});

export function useGraphQLQuery<TData, TVariables>(
  query: string,
  variables?: TVariables,
  options?: UseQueryOptions<TData>
) {
  return useQuery<TData>(
    [query, variables],
    async () => {
      return graphqlClient.request<TData>(query, variables);
    },
    {
      ...options,
      retry: (failureCount, error: any) => {
        // Don't retry on 4xx errors
        if (error.response?.status >= 400 && error.response?.status < 500) {
          return false;
        }
        return failureCount < 3;
      },
    }
  );
}
```

### Micro-Frontend Root Component

```tsx
// src/CatalogMicroFrontend.tsx
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ReactQueryDevtools } from 'react-query/devtools';
import { ThemeProvider } from 'styled-components';
import { ErrorBoundary } from '../components/ErrorBoundary';
import { theme } from '../styles/theme';
import ProductListPage from './pages/ProductListPage';
import ProductDetailPage from './pages/ProductDetailPage';
import CategoryPage from './pages/CategoryPage';
import NotFoundPage from './pages/NotFoundPage';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60000, // 1 minute
      cacheTime: 300000, // 5 minutes
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

export interface CatalogMicroFrontendProps {
  basePath?: string;
}

export default function CatalogMicroFrontend({ basePath = '' }: CatalogMicroFrontendProps) {
  return (
    <ErrorBoundary fallback={<div>Something went wrong in the Catalog application.</div>}>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <BrowserRouter basename={basePath}>
            <Routes>
              <Route path="/" element={<ProductListPage />} />
              <Route path="/product/:productId" element={<ProductDetailPage />} />
              <Route path="/category/:categoryId" element={<CategoryPage />} />
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </BrowserRouter>
        </ThemeProvider>
        {process.env.NODE_ENV !== 'production' && <ReactQueryDevtools />}
      </QueryClientProvider>
    </ErrorBoundary>
  );
}
```

### Module Federation Configuration

```js
// webpack.config.js
const { ModuleFederationPlugin } = require('webpack').container;
const deps = require('./package.json').dependencies;

module.exports = {
  // ... other webpack config
  plugins: [
    new ModuleFederationPlugin({
      name: 'catalog',
      filename: 'remoteEntry.js',
      exposes: {
        './CatalogApp': './src/CatalogMicroFrontend',
        './ProductCard': './src/components/ProductCard',
        './FeaturedProducts': './src/components/FeaturedProducts',
      },
      shared: {
        react: {
          singleton: true,
          requiredVersion: deps.react,
        },
        'react-dom': {
          singleton: true,
          requiredVersion: deps['react-dom'],
        },
        'react-router-dom': {
          singleton: true,
          requiredVersion: deps['react-router-dom'],
        },
        'react-query': {
          singleton: true,
          requiredVersion: deps['react-query'],
        },
        'styled-components': {
          singleton: true,
          requiredVersion: deps['styled-components'],
        },
        '@aronim/design-system': {
          singleton: true,
        },
      },
    }),
  ],
};
```

### Data Fetching with React Query and GraphQL

```tsx
// src/pages/ProductDetailPage.tsx
import React from 'react';
import { useParams } from 'react-router-dom';
import { gql } from 'graphql-request';
import { useGraphQLQuery } from '../hooks/useGraphQLQuery';
import { PageLayout } from '../components/layout/PageLayout';
import { ProductDetail } from '../components/product/ProductDetail';
import { RelatedProducts } from '../components/product/RelatedProducts';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { ErrorMessage } from '../components/ui/ErrorMessage';

const GET_PRODUCT = gql`
  query GetProduct($id: ID!) {
    bookById(id: $id) {
      id
      title
      author {
        id
        name
      }
      price {
        amount
        currency
      }
      coverImage
      rating
      description
      categories {
        id
        name
      }
      availability
      relatedBooks {
        id
        title
        coverImage
        price {
          amount
          currency
        }
      }
    }
  }
`;

export default function ProductDetailPage() {
  const { productId } = useParams<{ productId: string }>();
  
  const { data, isLoading, error } = useGraphQLQuery(
    GET_PRODUCT,
    { id: productId },
    {
      enabled: !!productId,
    }
  );
  
  if (isLoading) {
    return (
      <PageLayout>
        <LoadingSpinner size="large" />
      </PageLayout>
    );
  }
  
  if (error) {
    return (
      <PageLayout>
        <ErrorMessage 
          title="Unable to load product details" 
          message="Please try again later or contact support if the problem persists."
        />
      </PageLayout>
    );
  }
  
  const { bookById: product } = data || {};
  
  if (!product) {
    return (
      <PageLayout>
        <ErrorMessage 
          title="Product not found" 
          message="The product you're looking for doesn't exist or has been removed."
        />
      </PageLayout>
    );
  }
  
  return (
    <PageLayout>
      <ProductDetail product={product} />
      {product.relatedBooks?.length > 0 && (
        <RelatedProducts products={product.relatedBooks} />
      )}
    </PageLayout>
  );
}
```

### Testing Example

```tsx
// src/components/Button/Button.test.tsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider } from 'styled-components';
import { Button } from './Button';
import { theme } from '../../styles/theme';

// Helper to render with theme
const renderWithTheme = (ui: React.ReactElement) => {
  return render(<ThemeProvider theme={theme}>{ui}</ThemeProvider>);
};

describe('Button component', () => {
  test('renders correctly with default props', () => {
    renderWithTheme(<Button>Click me</Button>);
    
    const button = screen.getByRole('button', { name: /click me/i });
    expect(button).toBeInTheDocument();
    expect(button).toHaveAttribute('type', 'button');
    expect(button).not.toBeDisabled();
  });
  
  test('applies different variants correctly', () => {
    const { rerender } = renderWithTheme(<Button variant="primary">Primary</Button>);
    let button = screen.getByRole('button', { name: /primary/i });
    expect(button).toHaveStyle(`background-color: ${theme.colors.primary}`);
    
    rerender(<ThemeProvider theme={theme}><Button variant="secondary">Secondary</Button></ThemeProvider>);
    button = screen.getByRole('button', { name: /secondary/i });
    expect(button).toHaveStyle(`background-color: ${theme.colors.white}`);
    
    rerender(<ThemeProvider theme={theme}><Button variant="tertiary">Tertiary</Button></ThemeProvider>);
    button = screen.getByRole('button', { name: /tertiary/i });
    expect(button).toHaveStyle('background-color: transparent');
  });
  
  test('applies different sizes correctly', () => {
    const { rerender } = renderWithTheme(<Button size="small">Small</Button>);
    let button = screen.getByRole('button', { name: /small/i });
    expect(button).toHaveStyle('height: 32px');
    
    rerender(<ThemeProvider theme={theme}><Button size="medium">Medium</Button></ThemeProvider>);
    button = screen.getByRole('button', { name: /medium/i });
    expect(button).toHaveStyle('height: 40px');
    
    rerender(<ThemeProvider theme={theme}><Button size="large">Large</Button></ThemeProvider>);
    button = screen.getByRole('button', { name: /large/i });
    expect(button).toHaveStyle('height: 48px');
  });
  
  test('handles fullWidth prop correctly', () => {
    renderWithTheme(<Button fullWidth>Full Width</Button>);
    const button = screen.getByRole('button', { name: /full width/i });
    expect(button).toHaveStyle('width: 100%');
  });
  
  test('handles disabled state correctly', () => {
    renderWithTheme(<Button disabled>Disabled</Button>);
    const button = screen.getByRole('button', { name: /disabled/i });
    expect(button).toBeDisabled();
    expect(button).toHaveStyle('opacity: 0.6');
    expect(button).toHaveStyle('cursor: not-allowed');
  });
  
  test('calls onClick handler when clicked', () => {
    const handleClick = jest.fn();
    renderWithTheme(<Button onClick={handleClick}>Click me</Button>);
    
    const button = screen.getByRole('button', { name: /click me/i });
    fireEvent.click(button);
    
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
  
  test('does not call onClick when disabled', () => {
    const handleClick = jest.fn();
    renderWithTheme(<Button onClick={handleClick} disabled>Click me</Button>);
    
    const button = screen.getByRole('button', { name: /click me/i });
    fireEvent.click(button);
    
    expect(handleClick).not.toHaveBeenCalled();
  });
});
```

## Performance Optimization

### Code Splitting and Lazy Loading

```tsx
// src/App.tsx
import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { LoadingSpinner } from './components/ui/LoadingSpinner';

// Lazy load pages
const HomePage = lazy(() => import('./pages/HomePage'));
const ProductListPage = lazy(() => import('./pages/ProductListPage'));
const ProductDetailPage = lazy(() => import('./pages/ProductDetailPage'));
const CartPage = lazy(() => import('./pages/CartPage'));
const CheckoutPage = lazy(() => import('./pages/CheckoutPage'));
const AccountPage = lazy(() => import('./pages/AccountPage'));
const NotFoundPage = lazy(() => import('./pages/NotFoundPage'));

export default function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<LoadingSpinner size="large" centered />}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/products" element={<ProductListPage />} />
          <Route path="/product/:productId" element={<ProductDetailPage />} />
          <Route path="/cart" element={<CartPage />} />
          <Route path="/checkout" element={<CheckoutPage />} />
          <Route path="/account/*" element={<AccountPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
```

### React.memo for Performance Optimization

```tsx
// src/components/product/ProductCard.tsx
import React from 'react';
import styled from 'styled-components';
import { Link } from 'react-router-dom';
import { formatCurrency } from '../../utils/formatters';

interface ProductCardProps {
  id: string;
  title: string;
  author: string;
  price: {
    amount: number;
    currency: string;
  };
  coverImage: string;
  rating?: number;
}

const Card = styled.div`
  display: flex;
  flex-direction: column;
  border-radius: ${props => props.theme.radii.md};
  box-shadow: ${props => props.theme.shadows.sm};
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: ${props => props.theme.shadows.md};
  }
`;

const ImageContainer = styled.div`
  position: relative;
  padding-top: 150%; /* 2:3 aspect ratio for book covers */
  overflow: hidden;
`;

const Image = styled.img`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
`;

const Content = styled.div`
  padding: ${props => props.theme.space[3]};
  display: flex;
  flex-direction: column;
  flex: 1;
`;

const Title = styled.h3`
  margin: 0 0 ${props => props.theme.space[1]};
  font-size: ${props => props.theme.fontSizes.md};
  font-weight: ${props => props.theme.fontWeights.semibold};
`;

const Author = styled.p`
  margin: 0 0 ${props => props.theme.space[2]};
  font-size: ${props => props.theme.fontSizes.sm};
  color: ${props => props.theme.colors.gray600};
`;

const Price = styled.p`
  margin: ${props => props.theme.space[2]} 0 0;
  font-size: ${props => props.theme.fontSizes.md};
  font-weight: ${props => props.theme.fontWeights.bold};
  color: ${props => props.theme.colors.primary};
`;

const ProductCard = React.memo(({ id, title, author, price, coverImage, rating }: ProductCardProps) => {
  return (
    <Link to={`/product/${id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
      <Card>
        <ImageContainer>
          <Image src={coverImage} alt={title} loading="lazy" />
        </ImageContainer>
        <Content>
          <Title>{title}</Title>
          <Author>by {author}</Author>
          <Price>{formatCurrency(price.amount, price.currency)}</Price>
        </Content>
      </Card>
    </Link>
  );
});

ProductCard.displayName = 'ProductCard';

export default ProductCard;
```

## Compliance Verification
- Regular performance audits using React DevTools
- Accessibility testing with tools like axe-react
- Unit and integration testing coverage
- Bundle size monitoring
- Component API documentation review
- Code quality verification through static analysis
- Cross-browser compatibility testing
- Responsive design verification

## References
- React Documentation: https://reactjs.org/docs
- TypeScript React: https://www.typescriptlang.org/docs/handbook/react.html
- React Query: https://react-query.tanstack.com/
- Styled Components: https://styled-components.com/
- React Testing Library: https://testing-library.com/docs/react-testing-library/intro/
- React Performance Optimization: https://reactjs.org/docs/optimizing-performance.html
- Module Federation: https://webpack.js.org/concepts/module-federation/
- Atomic Design Principles: https://bradfrost.com/blog/post/atomic-web-design/
