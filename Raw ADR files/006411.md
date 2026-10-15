# ADR-032: Adoption of ESM Module Format for Frontend

## Status
Proposed

## Date
2025-03-03

## Context
The Aronim Bookstore application is implementing a micro-frontend architecture (ADR-025) with React as the default frontend framework (ADR-027). As we establish our frontend development approach, we need to decide on the JavaScript module format that:

- Aligns with modern web development standards
- Provides optimal performance for browser loading
- Supports efficient tree-shaking and code-splitting
- Ensures compatibility with our micro-frontend architecture
- Enables future-proof development practices
- Maintains compatibility with our toolchain and dependencies
- Supports modern JavaScript features

Currently, there are several module formats used in JavaScript ecosystems:
1. CommonJS (CJS) - The traditional Node.js module format using `require()` and `module.exports`
2. ECMAScript Modules (ESM) - The standard JavaScript module format using `import` and `export` statements
3. Universal Module Definition (UMD) - A pattern that works in multiple environments
4. AMD (Asynchronous Module Definition) - Primarily used with older tools like RequireJS

As browser support for ESM has matured and the JavaScript ecosystem has evolved, we need to determine the most appropriate module format for our frontend architecture.

## Decision
We will adopt **ECMAScript Modules (ESM)** as the standard module format for all frontend JavaScript/TypeScript code in the Aronim Bookstore application with the following implementation approach:

### 1. Core Implementation Strategy
- Use native ESM syntax (`import`/`export`) in all frontend code
- Configure TypeScript to target ESM output (`"module": "ESNext"` in tsconfig)
- Set `"type": "module"` in package.json for all frontend packages
- Update build tools to properly handle ESM
- Use `.mjs` extension for JavaScript files when needed for clarity
- Configure bundlers to output ESM format for production builds

### 2. Build and Development Tooling
- Configure webpack/Rollup to properly handle ESM input and output
- Update module federation configuration to work with ESM
- Set up development server with ESM support
- Configure Jest and testing tools to handle ESM modules
- Update ESLint and other tools to support ESM syntax
- Implement proper source map generation for ESM modules

### 3. Dependency Management
- Prefer dependencies that provide ESM builds
- For CJS-only dependencies, use appropriate interoperability solutions
- Document any dependencies requiring special handling
- Update dependency management strategy to prioritize ESM packages
- Implement version constraints to ensure ESM compatibility

### 4. Migration Strategy
- Create ESM transition plan for existing code (if applicable)
- Update import/export statements throughout the codebase
- Fix any circular dependency issues exposed by ESM's static analysis
- Implement comprehensive testing to ensure functionality after migration
- Create documentation for ESM best practices

### 5. Browser Compatibility
- Configure appropriate build outputs for different browser targets
- Implement differential loading for modern vs. legacy browsers
- Use appropriate polyfills only when necessary
- Configure proper MIME types on the server (`Content-Type: text/javascript`)
- Add appropriate `<script type="module">` tags in HTML

## Implementation Approach

1. **Package Configuration Updates**
   - Update all package.json files to include `"type": "module"`
   - Configure TypeScript for ESM output
   - Update module resolution settings
   - Configure appropriate browser and Node.js targets

   ```json
   // package.json
   {
     "name": "@aronim/frontend-package",
     "type": "module",
     "exports": {
       ".": {
         "import": "./dist/index.js",
         "require": "./dist/index.cjs"
       }
     },
     "sideEffects": false
   }
   ```

   ```json
   // tsconfig.json
   {
     "compilerOptions": {
       "target": "ES2020",
       "module": "ESNext",
       "moduleResolution": "bundler",
       "esModuleInterop": true
     }
   }
   ```

2. **Webpack Configuration Updates**
   - Update webpack configuration to handle ESM properly
   - Configure module federation for ESM compatibility
   - Implement optimization settings for ESM

   ```js
   // webpack.config.js
   export default {
     experiments: {
       outputModule: true
     },
     output: {
       module: true,
       libraryTarget: 'module'
     },
     plugins: [
       new ModuleFederationPlugin({
         name: 'catalog',
         filename: 'remoteEntry.js',
         exposes: {
           './CatalogApp': './src/CatalogMicroFrontend',
         },
         shared: {
           // Shared dependencies configuration
         },
         library: { type: 'module' }
       })
     ]
   };
   ```

3. **Code Updates for ESM Syntax**
   - Use proper ESM import/export syntax
   - Update dynamic imports to use ESM format
   - Handle browser-specific ESM patterns

   ```js
   // ESM import syntax
   import React from 'react';
   import { useState, useEffect } from 'react';
   import ProductCard from './components/ProductCard.js';
   
   // Named exports
   export const ProductList = ({ products }) => {
     // Component implementation
   };
   
   // Default export
   export default ProductList;
   
   // Dynamic import (ESM)
   const DynamicComponent = await import('./DynamicComponent.js')
     .then(module => module.default);
   ```

4. **HTML Template Updates**
   - Update script tags to use `type="module"`
   - Configure proper loading attributes
   - Handle fallbacks if needed

   ```html
   <!DOCTYPE html>
   <html>
   <head>
     <meta charset="UTF-8">
     <title>Aronim Bookstore</title>
   </head>
   <body>
     <div id="root"></div>
     <script type="module" src="/dist/main.js"></script>
   </body>
   </html>
   ```

5. **Testing Configuration Updates**
   - Configure Jest to handle ESM
   - Update test files to use ESM syntax
   - Configure coverage reporting for ESM files

   ```js
   // jest.config.js
   export default {
     transform: {
       '^.+\\.(ts|tsx|js|jsx)$': ['babel-jest', { configFile: './babel.config.js' }]
     },
     extensionsToTreatAsEsm: ['.ts', '.tsx', '.mjs'],
     moduleNameMapper: {
       '^(\\.{1,2}/.*)\\.js$': '$1'
     },
     testEnvironment: 'jsdom'
   };
   ```

## Consequences

### Positive
- Improved tree-shaking and dead code elimination
- Native browser support without transpilation for modern browsers
- Static analysis benefits from ESM's static structure
- Better performance through more efficient loading patterns
- Future-proof approach aligned with JavaScript standards
- Better developer experience with consistent import/export syntax
- Top-level await support in modern environments
- Improved code-splitting capabilities
- Better alignment with modern framework practices
- Simplified build configuration over time

### Negative
- Potential compatibility issues with older libraries using CommonJS
- Need for interoperability solutions for some dependencies
- Additional configuration required during transition period
- Potential learning curve for developers used to CommonJS
- Stricter handling of circular dependencies
- Potential issues with some testing frameworks
- May require updates to CI/CD pipelines
- Requires careful handling of browser compatibility

## Alternatives Considered

1. **Continue using CommonJS**
   - More established in Node.js ecosystem
   - Better compatibility with existing libraries
   - No transition required
   - Less efficient tree-shaking
   - Not aligned with browser standards
   - Requires more transpilation for browsers
   - Technical debt over time

2. **Dual Format (ESM + CommonJS)**
   - Provides maximum compatibility
   - Increases build complexity
   - Requires maintaining two output formats
   - Potential for inconsistencies between formats
   - Higher maintenance overhead

3. **UMD Format**
   - Works in multiple environments
   - More complex syntax and larger output
   - Less efficient than ESM for browsers
   - Not aligned with modern development practices
   - Poorer tree-shaking capabilities

## Implementation Notes

### ESM Best Practices

```js
// Prefer named imports for better tree-shaking
import { Button, Card } from '@aronim/design-system';

// Avoid namespace imports which may hinder tree-shaking
// Not recommended:
// import * as DesignSystem from '@aronim/design-system';

// Use file extensions in imports for better tooling compatibility
import ProductCard from './ProductCard.js';
import { formatPrice } from '../utils/formatters.js';

// For TypeScript, configure to add extensions automatically
// tsconfig.json: "moduleResolution": "bundler"

// Dynamic imports for code splitting
const OrderHistory = () => {
  const [OrderDetails, setOrderDetails] = useState(null);
  
  useEffect(() => {
    import('./OrderDetails.js')
      .then(module => {
        setOrderDetails(() => module.default);
      });
  }, []);
  
  return OrderDetails ? <OrderDetails /> : <Loading />;
};

// Top-level await (in modules where supported)
const userData = await fetchUserData();
export const userDefaults = processUserData(userData);
```

### Module Federation with ESM

```js
// webpack.config.js for host application
export default {
  experiments: {
    outputModule: true,
  },
  output: {
    publicPath: 'auto',
    module: true,
    libraryTarget: 'module'
  },
  plugins: [
    new ModuleFederationPlugin({
      name: 'host',
      filename: 'remoteEntry.js',
      remotes: {
        catalog: 'catalog@http://localhost:3001/remoteEntry.js',
        checkout: 'checkout@http://localhost:3002/remoteEntry.js',
      },
      shared: {
        react: { 
          singleton: true, 
          requiredVersion: deps.react,
          eager: true
        },
        'react-dom': { 
          singleton: true, 
          requiredVersion: deps['react-dom'],
          eager: true
        }
      },
      library: { type: 'module' }
    }),
  ],
};

// Dynamic remote loading with ESM
const loadRemote = async (remoteName, moduleName) => {
  const remoteUrl = remoteRegistry[remoteName];
  
  // Dynamic import the remote entry
  const remoteContainer = await import(/* @vite-ignore */ remoteUrl);
  
  // Initialize the remote
  await remoteContainer.init(__webpack_share_scopes__.default);
  
  // Get the module factory
  const factory = await remoteContainer.get(moduleName);
  
  // Create the module
  return factory();
};

// Usage
const CatalogApp = React.lazy(() => loadRemote('catalog', './CatalogApp'));
```

## Compliance Verification
- Audit of all import/export statements for ESM compatibility
- Verification of build output format
- Browser compatibility testing across target browsers
- Performance benchmarking before and after migration
- Bundle size analysis to verify tree-shaking benefits
- Testing of all dynamic import code paths
- Verification of module federation functionality
- CI pipeline validation for ESM modules

## References
- ECMAScript Modules Specification: https://tc39.es/ecma262/#sec-modules
- MDN Web Docs on JavaScript modules: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules
- Node.js ECMAScript Modules documentation: https://nodejs.org/api/esm.html
- Webpack Module Federation with ESM: https://webpack.js.org/concepts/module-federation/
- TypeScript ESM Support: https://www.typescriptlang.org/docs/handbook/esm-node.html
- Jest ESM Support: https://jestjs.io/docs/ecmascript-modules
- Package.json exports field: https://nodejs.org/api/packages.html#exports
- Browser compatibility: https://caniuse.com/es6-module
