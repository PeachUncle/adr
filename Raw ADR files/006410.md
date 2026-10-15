# ADR-031: Adoption of Lerna for Frontend Monorepo Management

## Status
Accepted

## Date
2025-03-03

## Context
The Aronim Bookstore application has adopted a micro-frontend architecture (ADR-025) with React as the default frontend framework (ADR-027). As our frontend codebase grows with multiple micro-frontends and shared libraries, we need an effective solution to manage this complexity. We need a tool that:

- Facilitates managing multiple packages within a single repository (monorepo)
- Streamlines dependency management across packages
- Enables sharing code between micro-frontends
- Simplifies the build, test, and release processes
- Supports our module federation approach
- Reduces duplication and promotes code reuse
- Provides consistent versioning and publishing workflows
- Integrates well with our existing CI/CD pipeline

A monorepo approach for frontend code would help us maintain consistency across micro-frontends while still allowing independent deployment as required by our architecture.

## Decision
We will adopt **Lerna** as our frontend monorepo management tool with the following implementation approach:

### 1. Repository Structure
- Implement a Lerna-managed monorepo for all frontend packages
- Organize packages into the following categories:
  - `applications/`: Individual micro-frontend applications
  - `libraries/`: Shared libraries and components
  - `tools/`: Build tools, generators, and utilities

### 2. Workspace Management
- Use Yarn workspaces in conjunction with Lerna for dependency management
- Implement a consistent package structure across all packages
- Define clear package boundaries and dependencies
- Manage shared dependencies at the root level

### 3. Build and Development Workflow
- Configure parallel build processes for improved performance
- Implement shared configurations for TypeScript, ESLint, Prettier, and Jest
- Create standardized scripts for common operations
- Configure hot module reloading for local development
- Implement watch mode for dependent packages during development

### 4. Version Management
- Use independent versioning mode to allow packages to version independently
- Implement conventional commits for automated version determination
- Configure automated changelog generation
- Establish versioning policies for different package types

### 5. CI/CD Integration
- Configure caching strategies for faster CI builds
- Implement affected-based testing and builds
- Create deployment pipelines for individual micro-frontends
- Establish artifact publishing workflows for shared libraries

## Implementation Approach

1. **Initial Setup**
   - Install and configure Lerna in the frontend repository
   - Set up Yarn workspaces
   - Create the basic folder structure
   - Configure root-level tooling and configurations

```json
// lerna.json
{
  "version": "independent",
  "npmClient": "yarn",
  "useWorkspaces": true,
  "packages": ["applications/*", "libraries/*", "tools/*"],
  "command": {
    "publish": {
      "conventionalCommits": true,
      "message": "chore(release): publish",
      "registry": "https://npm.pkg.github.com",
      "yes": true
    },
    "version": {
      "allowBranch": "main",
      "conventionalCommits": true,
      "createRelease": "github",
      "message": "chore(release): publish [skip ci]"
    },
    "bootstrap": {
      "hoist": true
    }
  },
  "ignoreChanges": [
    "**/*.md",
    "**/*.test.ts",
    "**/*.test.tsx",
    "**/*.spec.ts",
    "**/*.spec.tsx",
    "**/*.stories.tsx"
  ]
}
```

```json
// package.json (root)
{
  "name": "aronim-bookstore-frontend",
  "private": true,
  "workspaces": [
    "applications/*",
    "libraries/*",
    "tools/*"
  ],
  "scripts": {
    "start": "lerna run start --stream --parallel",
    "build": "lerna run build --stream",
    "test": "lerna run test --stream",
    "lint": "lerna run lint --stream --parallel",
    "clean": "lerna clean",
    "bootstrap": "lerna bootstrap",
    "version": "lerna version",
    "publish": "lerna publish",
    "affected:build": "lerna run build --stream --since=origin/main",
    "affected:test": "lerna run test --stream --since=origin/main",
    "new:app": "node ./tools/generators/app",
    "new:lib": "node ./tools/generators/lib"
  },
  "devDependencies": {
    "@typescript-eslint/eslint-plugin": "^5.59.0",
    "@typescript-eslint/parser": "^5.59.0",
    "eslint": "^8.38.0",
    "eslint-config-prettier": "^8.8.0",
    "eslint-plugin-import": "^2.27.5",
    "eslint-plugin-jsx-a11y": "^6.7.1",
    "eslint-plugin-react": "^7.32.2",
    "eslint-plugin-react-hooks": "^4.6.0",
    "husky": "^8.0.3",
    "jest": "^29.5.0",
    "lerna": "^6.6.1",
    "lint-staged": "^13.2.1",
    "prettier": "^2.8.7",
    "typescript": "^5.0.4"
  }
}
```

2. **Package Templates**
   - Create standardized templates for micro-frontend applications
   - Create standardized templates for shared libraries
   - Implement generators for creating new packages

```typescript
// tools/generators/lib/index.js
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const libName = process.argv[2];
if (!libName) {
  console.error('Please provide a library name');
  process.exit(1);
}

const libPath = path.join(__dirname, '../../../libraries', libName);

// Create directory structure
fs.mkdirSync(libPath, { recursive: true });
fs.mkdirSync(`${libPath}/src`, { recursive: true });
fs.mkdirSync(`${libPath}/src/components`, { recursive: true });
fs.mkdirSync(`${libPath}/src/hooks`, { recursive: true });
fs.mkdirSync(`${libPath}/src/utils`, { recursive: true });
fs.mkdirSync(`${libPath}/src/types`, { recursive: true });
fs.mkdirSync(`${libPath}/__tests__`, { recursive: true });

// Create package.json
const packageJson = {
  name: `@aronim/${libName}`,
  version: '0.1.0',
  main: 'dist/index.js',
  types: 'dist/index.d.ts',
  files: ['dist'],
  scripts: {
    build: 'tsc',
    test: 'jest',
    lint: 'eslint src --ext .ts,.tsx',
    clean: 'rimraf dist'
  },
  peerDependencies: {
    react: '>=17.0.0',
    'react-dom': '>=17.0.0',
    'styled-components': '>=5.0.0'
  },
  devDependencies: {
    '@types/react': '^18.0.0',
    '@types/react-dom': '^18.0.0',
    '@types/styled-components': '^5.1.26',
    typescript: '^5.0.4',
    rimraf: '^5.0.0'
  }
};

fs.writeFileSync(
  `${libPath}/package.json`,
  JSON.stringify(packageJson, null, 2)
);

// Create tsconfig.json
const tsConfig = {
  extends: '../../tsconfig.base.json',
  compilerOptions: {
    outDir: './dist',
    rootDir: './src',
    declaration: true,
    declarationMap: true
  },
  include: ['src/**/*'],
  exclude: ['node_modules', '**/*.test.ts', '**/*.test.tsx']
};

fs.writeFileSync(
  `${libPath}/tsconfig.json`,
  JSON.stringify(tsConfig, null, 2)
);

// Create aronim-application-books.tsx
fs.writeFileSync(
  `${libPath}/src/aronim-application-books.tsx`,
  `// Export all public API from this file\n`
);

// Create README.md
fs.writeFileSync(
  `${libPath}/README.md`,
  `# ${libName}\n\nA shared library for the Aronim Bookstore frontend.\n`
);

// Create a sample component
const sampleComponentName = 'Sample';
fs.writeFileSync(
  `${libPath}/src/components/${sampleComponentName}.tsx`,
  `import React from 'react';
import styled from 'styled-components';

export interface ${sampleComponentName}Props {
  /** The label to display */
  label: string;
}

const StyledDiv = styled.div\`
  padding: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
\`;

export const ${sampleComponentName}: React.FC<${sampleComponentName}Props> = ({ label }) => {
  return <StyledDiv>{label}</StyledDiv>;
};
`
);

// Create a sample test
fs.writeFileSync(
  `${libPath}/__tests__/${sampleComponentName}.test.tsx`,
  `import React from 'react';
import { render, screen } from '@testing-library/react';
import { ${sampleComponentName} } from '../src/components/${sampleComponentName}';

describe('${sampleComponentName}', () => {
  test('renders correctly', () => {
    render(<${sampleComponentName} label="Test Label" />);
    expect(screen.getByText('Test Label')).toBeInTheDocument();
  });
});
`
);

// Export the component in aronim-application-books.tsx
fs.appendFileSync(
  `${libPath}/src/aronim-application-books.tsx`,
  `export * from './components/${sampleComponentName}';\n`
);

console.log(`Library ${libName} created successfully!`);

// Install dependencies
console.log('Installing dependencies...');
execSync('yarn', { cwd: process.cwd(), stdio: 'inherit' });
```

3. **Shared Configuration**
   - Create shared TypeScript configuration
   - Create shared ESLint and Prettier configurations
   - Create shared Jest configuration

```json
// tsconfig.base.json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "node",
    "jsx": "react-jsx",
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "strict": true,
    "skipLibCheck": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": false,
    "declaration": true,
    "sourceMap": true,
    "lib": ["DOM", "DOM.Iterable", "ESNext"],
    "allowSyntheticDefaultImports": true,
    "noFallthroughCasesInSwitch": true
  },
  "exclude": ["node_modules", "dist", "build"]
}
```

4. **CI/CD Integration**
   - Configure GitHub Actions workflow for the monorepo

```yaml
# .github/workflows/frontend.yml
name: Frontend CI/CD

on:
  push:
    branches: [main]
    paths:
      - 'applications/**'
      - 'libraries/**'
      - 'tools/**'
      - 'package.json'
      - 'yarn.lock'
      - 'lerna.json'
      - '.github/workflows/frontend.yml'
  pull_request:
    branches: [main]
    paths:
      - 'applications/**'
      - 'libraries/**'
      - 'tools/**'
      - 'package.json'
      - 'yarn.lock'
      - 'lerna.json'
      - '.github/workflows/frontend.yml'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'yarn'

      - name: Install dependencies
        run: yarn install --frozen-lockfile

      - name: Lint
        run: yarn affected:lint

      - name: Test
        run: yarn affected:test

      - name: Build
        run: yarn affected:build

      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: build-artifacts
          path: |
            applications/*/dist
            libraries/*/dist

  deploy:
    needs: build
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'yarn'
          registry-url: 'https://npm.pkg.github.com'
          scope: '@aronim'

      - name: Download build artifacts
        uses: actions/download-artifact@v3
        with:
          name: build-artifacts

      - name: Publish packages
        run: yarn lerna publish from-package --yes
        env:
          NODE_AUTH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Deploy micro-frontends
        run: yarn lerna run deploy --scope="@aronim/{catalog,checkout,account}"
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

## Consequences

### Positive
- Streamlined management of multiple frontend packages in a single repository
- Simplified dependency management across packages
- Improved code sharing and reuse between micro-frontends
- Reduced duplication of configuration and tooling
- More consistent development experience across teams
- Simplified versioning and publishing workflows
- Better integration with CI/CD processes
- Optimized build performance through caching and selective builds
- Easier onboarding of new developers with standardized structure
- Support for independent versioning and deployment of packages

### Negative
- Learning curve for developers not familiar with monorepo concepts
- Increased complexity in build and CI configuration
- Potential performance issues with very large repositories
- Risk of tight coupling between packages if boundaries aren't well-defined
- Increased risk of breaking changes affecting multiple packages
- More complex release coordination for interdependent packages
- Additional tooling overhead compared to separate repositories
- Potential challenges with access control at the package level

## Alternatives Considered

1. **Separate Repositories**
   - Each micro-frontend and library in its own repository
   - Simpler repository structure
   - Clear ownership boundaries
   - Independent CI/CD pipelines
   - More complex dependency management
   - Harder to maintain consistency across projects
   - Difficult to coordinate changes across multiple repositories
   - Higher overhead for shared code changes

2. **Nx**
   - More advanced monorepo tooling
   - Better visualization of dependency graph
   - More sophisticated affected commands
   - Built-in generators and schematics
   - Steeper learning curve
   - More opinionated structure
   - Potentially more complex configuration
   - Better suited for Angular ecosystem (though works well with React)

3. **Turborepo**
   - Faster build performance with intelligent caching
   - Simpler configuration than Nx
   - Growing ecosystem and adoption
   - Less mature than Lerna
   - Fewer features for versioning and publishing
   - Less established patterns and best practices
   - Limited remote caching options

4. **PNPM Workspaces**
   - Efficient package management with content-addressable storage
   - Built-in workspace support
   - Stricter dependency management
   - Limited features for versioning and publishing
   - Less mature ecosystem for monorepo management
   - Fewer integrations with other tools
   - Limited support for affected-based commands

## Implementation Notes

### Package Structure Example

```
aronim-bookstore-frontend/
├── applications/
│   ├── catalog/
│   │   ├── src/
│   │   ├── package.json
│   │   └── tsconfig.json
│   ├── checkout/
│   │   ├── src/
│   │   ├── package.json
│   │   └── tsconfig.json
│   └── shell/
│       ├── src/
│       ├── package.json
│       └── tsconfig.json
├── libraries/
│   ├── ui-components/
│   │   ├── src/
│   │   ├── package.json
│   │   └── tsconfig.json
│   ├── hooks/
│   │   ├── src/
│   │   ├── package.json
│   │   └── tsconfig.json
│   └── utils/
│       ├── src/
│       ├── package.json
│       └── tsconfig.json
├── tools/
│   ├── generators/
│   │   ├── app/
│   │   └── lib/
│   └── eslint-config/
├── lerna.json
├── package.json
├── tsconfig.base.json
└── yarn.lock
```

### Dependency Management Example

```json
// applications/catalog/package.json
{
  "name": "@aronim/catalog",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "start": "webpack serve --mode development",
    "build": "webpack --mode production",
    "test": "jest",
    "lint": "eslint src --ext .ts,.tsx"
  },
  "dependencies": {
    "@aronim/ui-components": "^0.1.0",
    "@aronim/hooks": "^0.1.0",
    "@aronim/utils": "^0.1.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.10.0"
  },
  "devDependencies": {
    "@types/react": "^18.0.35",
    "@types/react-dom": "^18.0.11",
    "typescript": "^5.0.4",
    "webpack": "^5.80.0",
    "webpack-cli": "^5.0.1",
    "webpack-dev-server": "^4.13.3"
  }
}
```

### Versioning Strategy

For our versioning strategy, we will:

1. Use conventional commits to automatically determine version bumps
2. Apply independent versioning to allow packages to evolve at different rates
3. Publish shared libraries to our private package registry
4. Deploy micro-frontends to their respective hosting environments
5. Use git tags to mark releases
6. Generate changelogs automatically from commit messages

### Migration Plan

1. **Phase 1: Initial Setup (Week 1-2)**
   - Set up the monorepo structure with Lerna and Yarn workspaces
   - Create shared configurations and tooling
   - Develop package templates and generators

2. **Phase 2: Migrate Shared Code (Week 3-4)**
   - Identify and extract common components and utilities
   - Create shared libraries for UI components, hooks, and utilities
   - Implement testing and documentation

3. **Phase 3: Migrate Applications (Week 5-8)**
   - Move existing micro-frontends into the monorepo structure
   - Update dependencies to use shared libraries
   - Ensure all applications build and run correctly

4. **Phase 4: CI/CD Integration (Week 9-10)**
   - Configure GitHub Actions workflows
   - Set up artifact publishing
   - Implement deployment pipelines

5. **Phase 5: Developer Onboarding (Week 11-12)**
   - Create documentation and guidelines
   - Conduct training sessions
   - Establish code review and contribution processes

## Compliance Verification
- Regular dependency audits using yarn audit
- Bundle size monitoring
- Performance benchmarking
- Code quality verification through ESLint
- Type checking with TypeScript
- Comprehensive test coverage
- Documentation quality checks

## References
- Lerna Documentation: https://lerna.js.org/
- Yarn Workspaces: https://classic.yarnpkg.com/en/docs/workspaces/
- Monorepo Best Practices: https://nx.dev/concepts/more-concepts/monorepo-nx-enterprise
- Module Federation: https://webpack.js.org/concepts/module-federation/
- Conventional Commits: https://www.conventionalcommits.org/
- GitHub Actions: https://docs.github.com/en/actions
