# ADR-025: Adoption of Micro-Frontend Architecture

## Status
Proposed

## Date
2025-03-02

## Context
Our Aronim Bookstore application requires a frontend architecture that aligns with our modular backend design (Modulith) while providing a cohesive user experience. We need a frontend architecture that:

- Enables independent development and deployment of frontend components
- Supports team autonomy and parallel development
- Aligns with our domain-driven design approach
- Scales with growing application complexity and team size
- Provides consistent user experience across the application
- Integrates well with our existing backend architecture
- Supports gradual migration and incremental adoption
- Enables technology flexibility where appropriate
- Maintains good performance and user experience
- Facilitates testing and quality assurance

The traditional monolithic frontend approach may lead to development bottlenecks, complex merges, and challenges in maintaining clear boundaries between different parts of the application as it grows.

## Decision
We will implement a **Micro-Frontend Architecture** with the following characteristics:

### 1. Architectural Approach
- Adopt a **runtime integration** approach using module federation
- Implement vertical slicing based on business domains
- Align micro-frontend boundaries with backend module boundaries
- Create a thin application shell for orchestration and shared functionality
- Use Web Components for technology-agnostic integration where needed

### 2. Technology Stack
- Use **React** as the primary framework for micro-frontends
- Implement **Webpack Module Federation** for runtime integration
- Utilize **Single-SPA** for application shell and micro-frontend orchestration
- Apply **Styled Components** with a shared design system for UI consistency
- Implement shared state management using **Redux Toolkit** for cross-micro-frontend communication

### 3. Development Approach
- Create a centralized design system and component library
- Implement clear contracts between micro-frontends
- Establish independent CI/CD pipelines for each micro-frontend
- Define standards for cross-cutting concerns (auth, logging, etc.)
- Create development tooling for local micro-frontend development

### 4. Deployment Strategy
- Deploy micro-frontends independently to CDN/static hosting
- Implement versioning strategy for micro-frontend releases
- Configure application shell to load appropriate micro-frontend versions
- Support canary releases and A/B testing at the micro-frontend level
- Implement shared dependency management

### 5. Performance Optimization
- Implement shared dependencies to avoid duplication
- Configure appropriate caching strategies
- Implement lazy loading of micro-frontends
- Optimize initial loading performance
- Monitor and optimize runtime performance

## Implementation Approach

1. **Application Shell Development**
   - Create a minimal application shell
   - Implement routing and micro-frontend loading logic
   - Set up authentication and global state management
   - Create global error handling and fallback mechanisms

2. **Shared Infrastructure**
   - Develop shared component library and design system
   - Implement build tooling and templates
   - Create development environment for micro-frontend testing
   - Set up monitoring and observability

3. **First Micro-Frontend Implementation**
   - Start with the product catalog domain as the first micro-frontend
   - Establish patterns and best practices
   - Document integration approach
   - Create template for future micro-frontends

4. **Incremental Adoption**
   - Gradually implement additional micro-frontends
   - Migrate existing functionality incrementally
   - Refine integration patterns based on feedback
   - Expand shared component library as needed

## Consequences

### Positive
- Independent development and deployment of frontend features
- Better alignment with backend domain boundaries
- Improved team autonomy and development velocity
- Flexibility to use different technologies when appropriate
- Better scalability for large applications and teams
- Reduced merge conflicts and coordination overhead
- More focused and maintainable codebases
- Easier onboarding for new team members to specific domains
- Support for incremental upgrades and migrations
- Better isolation for testing and quality assurance

### Negative
- Increased complexity in build and deployment infrastructure
- Potential performance overhead from multiple applications
- Need for strong governance and standards
- Challenges in maintaining consistent user experience
- Duplication risk without proper shared component strategy
- Steeper learning curve for developers
- Debugging complexity across micro-frontend boundaries
- Potential versioning and compatibility issues
- Additional operational overhead
- Risk of inconsistent implementation without proper standards

## Alternatives Considered

1. **Monolithic Frontend**
   - Simpler architecture and tooling
   - Better initial development velocity
   - Easier sharing of code and state
   - Challenges with scaling development across teams
   - Potential bottlenecks in CI/CD as application grows
   - Less alignment with backend modularity

2. **Server-Side Composition**
   - Simpler client-side architecture
   - Better initial page load performance
   - Less JavaScript overhead
   - More complex server infrastructure
   - Potentially higher latency for user interactions
   - Less flexibility for rich client-side interactions

3. **iFrame-Based Integration**
   - Stronger isolation between micro-frontends
   - Simpler integration model
   - Poor user experience and performance
   - Challenges with responsive design
   - Difficult cross-frame communication
   - SEO challenges

4. **Web Components Only**
   - More standardized approach
   - Framework-agnostic integration
   - Less mature ecosystem
   - More complex implementation for rich applications
   - Potential performance challenges
   - Limited browser support for advanced features

## Implementation Notes

### Application Shell Structure

```javascript
// app-shell/src/index.js
import { registerApplication, start } from 'single-spa';
import { constructRoutes, constructApplications } from 'single-spa-layout';

// Load layout from HTML or define in JS
const routes = constructRoutes(`
  <single-spa-router>
    <nav class="topnav">
      <application name="@aronim/nav"></application>
    </nav>
    <main>
      <route path="/">
        <application name="@aronim/home"></application>
      </route>
      <route path="/books">
        <application name="@aronim/catalog"></application>
      </route>
      <route path="/cart">
        <application name="@aronim/cart"></application>
      </route>
      <route path="/checkout">
        <application name="@aronim/checkout"></application>
      </route>
      <route path="/account">
        <application name="@aronim/account"></application>
      </route>
    </main>
    <footer>
      <application name="@aronim/footer"></application>
    </footer>
  </single-spa-router>
`);

const applications = constructApplications({
  routes,
  loadApp({ name }) {
    return System.import(name);
  },
});

applications.forEach(registerApplication);

// Start the application
start();
```

### Webpack Module Federation Configuration

```javascript
// webpack.config.js for a micro-frontend
const { ModuleFederationPlugin } = require('webpack').container;
const deps = require('./package.json').dependencies;

module.exports = {
  // ... other webpack configuration
  plugins: [
    new ModuleFederationPlugin({
      name: 'catalog',
      filename: 'remoteEntry.js',
      exposes: {
        './CatalogApp': './src/CatalogApp',
        './ProductList': './src/components/ProductList',
        './ProductDetail': './src/components/ProductDetail',
      },
      shared: {
        ...deps,
        react: {
          singleton: true,
          requiredVersion: deps.react,
        },
        'react-dom': {
          singleton: true,
          requiredVersion: deps['react-dom'],
        },
        '@aronim/design-system': {
          singleton: true,
        },
      },
    }),
  ],
};
```

### Micro-Frontend Component Example

```jsx
// catalog/src/CatalogApp.jsx
import React from 'react';
import { BrowserRouter, Route, Switch } from 'react-router-dom';
import { ErrorBoundary } from '@aronim/shared-components';
import { ThemeProvider } from '@aronim/design-system';
import ProductList from './components/ProductList';
import ProductDetail from './components/ProductDetail';

export default function CatalogApp({ basePath }) {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <BrowserRouter basename={basePath}>
          <Switch>
            <Route exact path="/" component={ProductList} />
            <Route path="/:productId" component={ProductDetail} />
          </Switch>
        </BrowserRouter>
      </ThemeProvider>
    </ErrorBoundary>
  );
}
```

### Shared Component Library

```jsx
// design-system/src/components/Button/Button.jsx
import React from 'react';
import styled from 'styled-components';
import PropTypes from 'prop-types';

const StyledButton = styled.button`
  padding: 8px 16px;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  
  ${props => props.variant === 'primary' && `
    background-color: var(--color-primary);
    color: white;
    border: none;
    
    &:hover {
      background-color: var(--color-primary-dark);
    }
  `}
  
  ${props => props.variant === 'secondary' && `
    background-color: white;
    color: var(--color-primary);
    border: 1px solid var(--color-primary);
    
    &:hover {
      background-color: var(--color-gray-light);
    }
  `}
  
  ${props => props.size === 'small' && `
    font-size: 14px;
    padding: 4px 8px;
  `}
  
  ${props => props.size === 'large' && `
    font-size: 18px;
    padding: 12px 24px;
  `}
  
  ${props => props.fullWidth && `
    width: 100%;
  `}
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

function Button({ children, variant, size, fullWidth, ...props }) {
  return (
    <StyledButton 
      variant={variant} 
      size={size} 
      fullWidth={fullWidth} 
      {...props}
    >
      {children}
    </StyledButton>
  );
}

Button.propTypes = {
  variant: PropTypes.oneOf(['primary', 'secondary']),
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  fullWidth: PropTypes.bool,
  children: PropTypes.node.isRequired,
};

Button.defaultProps = {
  variant: 'primary',
  size: 'medium',
  fullWidth: false,
};

export default Button;
```

### Cross-Micro-Frontend Communication

```javascript
// shared-state/src/store.js
import { configureStore } from '@reduxjs/toolkit';
import { combineReducers } from 'redux';

// Create a store factory to ensure we have only one store instance
let store;

export const createStore = (reducers = {}) => {
  const staticReducers = {
    auth: authReducer,
    // Other shared reducers
  };

  // Combine static reducers with dynamically injected ones
  const combinedReducers = combineReducers({
    ...staticReducers,
    ...reducers,
  });

  // Create or reuse the store
  if (!store) {
    store = configureStore({
      reducer: combinedReducers,
      middleware: (getDefaultMiddleware) => 
        getDefaultMiddleware().concat(logger),
      devTools: process.env.NODE_ENV !== 'production',
    });
    
    // Store the static reducers
    store.staticReducers = staticReducers;
  } else {
    // If store exists, just replace the reducers with the new combined ones
    store.replaceReducer(combinedReducers);
  }

  // Add a function to inject reducers dynamically when micro-frontends load
  store.injectReducer = (key, reducer) => {
    if (!key || store.staticReducers[key]) return;
    
    store.replaceReducer(
      combineReducers({
        ...store.staticReducers,
        ...store.asyncReducers,
        [key]: reducer,
      })
    );
  };

  return store;
};

export const getStore = () => store;
```

### CI/CD Pipeline for Micro-Frontend

```yaml
# .github/workflows/catalog-micro-frontend.yml
name: Catalog Micro-Frontend CI/CD

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'micro-frontends/catalog/**'
  pull_request:
    branches: [ main, develop ]
    paths:
      - 'micro-frontends/catalog/**'

jobs:
  build:
    name: Build and Test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: '**/package-lock.json'
      
      - name: Install dependencies
        working-directory: micro-frontends/catalog
        run: npm ci
      
      - name: Lint
        working-directory: micro-frontends/catalog
        run: npm run lint
      
      - name: Test
        working-directory: micro-frontends/catalog
        run: npm test
      
      - name: Build
        working-directory: micro-frontends/catalog
        run: npm run build
      
      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: catalog-build
          path: micro-frontends/catalog/dist
  
  deploy:
    name: Deploy
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Download build artifacts
        uses: actions/download-artifact@v3
        with:
          name: catalog-build
          path: dist
      
      - name: Deploy to CDN
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Upload to S3
        run: |
          aws s3 sync dist s3://aronim-bookstore-micro-frontends/catalog/latest/
          aws s3 sync dist s3://aronim-bookstore-micro-frontends/catalog/v${{ github.sha }}/
      
      - name: Invalidate CloudFront cache
        run: |
          aws cloudfront create-invalidation \
            --distribution-id ${{ secrets.CLOUDFRONT_DISTRIBUTION_ID }} \
            --paths "/catalog/latest/*"
```

### Local Development Setup

```javascript
// micro-frontend-dev-server.js
const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 9000;

// Enable CORS
app.use(cors());

// Serve the app shell locally
app.use('/', express.static('app-shell/dist'));

// Proxy requests to micro-frontends running locally
app.use('/catalog', createProxyMiddleware({ 
  target: 'http://localhost:9001',
  changeOrigin: true,
  pathRewrite: {'^/catalog' : ''}
}));

app.use('/cart', createProxyMiddleware({ 
  target: 'http://localhost:9002',
  changeOrigin: true,
  pathRewrite: {'^/cart' : ''}
}));

app.use('/checkout', createProxyMiddleware({ 
  target: 'http://localhost:9003',
  changeOrigin: true,
  pathRewrite: {'^/checkout' : ''}
}));

// Fallback to app shell for SPA routing
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'app-shell/dist/index.html'));
});

app.listen(PORT, () => {
  console.log(`Micro-frontend dev server running at http://localhost:${PORT}`);
});
```

## Performance Optimization

### Lazy Loading Configuration

```javascript
// app-shell/src/index.js
import { registerApplication, start } from 'single-spa';

// Lazy load micro-frontends
registerApplication({
  name: '@aronim/catalog',
  app: () => System.import('@aronim/catalog'),
  activeWhen: ['/books'],
  customProps: { domElement: document.getElementById('catalog-container') }
});

registerApplication({
  name: '@aronim/cart',
  app: () => System.import('@aronim/cart'),
  activeWhen: ['/cart'],
  customProps: { domElement: document.getElementById('cart-container') }
});

// Pre-load critical micro-frontends
System.import('@aronim/nav');
System.import('@aronim/footer');

start();
```

## Compliance Verification
- Regular audits of frontend performance metrics
- Verification of accessibility compliance across micro-frontends
- Testing of cross-micro-frontend interactions
- Validation of consistent UI/UX across the application
- Security review of micro-frontend integration points
- Dependency analysis to identify duplication
- Documentation review for micro-frontend standards

## References
- Micro-Frontends Architecture: https://micro-frontends.org/
- Module Federation: https://webpack.js.org/concepts/module-federation/
- Single-SPA Framework: https://single-spa.js.org/
- Web Components Standard: https://developer.mozilla.org/en-US/docs/Web/Web_Components
- React Documentation: https://reactjs.org/docs/getting-started.html
- Design Systems: https://www.invisionapp.com/inside-design/guide-to-design-systems/
- Frontend Performance Optimization: https://web.dev/fast/
- Micro-Frontend Testing Strategies: https://martinfowler.com/articles/micro-frontends.html
