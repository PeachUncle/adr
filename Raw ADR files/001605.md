# ADR-006: Sprint 1 Technology Stack Selection

**Status**: Accepted  
**Date**: 2025-11-06  
**Deciders**: Software Architect, Technical Lead, Development Team

## Context

Sprint 1 focuses on establishing the project foundation and core infrastructure for the Eucharist Understanding Platform. We need to make specific technology choices for:

1. **Backend Foundation**: Server framework, middleware, logging, validation, and security
2. **Frontend Foundation**: Build tool, routing, styling, HTTP client, and state management
3. **Development Tools**: Linting, formatting, testing, and local development environment
4. **Database Clients**: ORM/ODM choices for PostgreSQL and MongoDB

These choices must:

- Align with our architectural decisions (ADR-001 through ADR-005)
- Enable rapid development and iteration
- Support TypeScript throughout the stack
- Provide excellent developer experience
- Be production-ready and well-maintained
- Have strong community support and documentation

## Decision

We will use the following technology stack for Sprint 1 implementation:

### Backend Technology Stack

#### Core Framework & Runtime

- **Node.js 20.x LTS**: Latest long-term support version for stability and modern features
- **Express.js 4.19.x**: Lightweight, flexible web framework with extensive middleware ecosystem
- **TypeScript 5.3.x**: Type safety, better IDE support, and improved code quality

#### Security & Middleware

- **Helmet 7.x**: Secure Express apps by setting various HTTP headers
- **CORS 2.x**: Enable Cross-Origin Resource Sharing with configurable options
- **bcryptjs 2.x**: Password hashing with salt rounds (12+ rounds for security)
- **express-rate-limit 7.x**: Rate limiting to prevent abuse

#### Validation & Error Handling

- **Zod 3.x**: TypeScript-first schema validation for runtime type checking
- **express-validator 7.x**: Additional validation middleware for Express routes

#### Logging & Monitoring

- **Winston 3.x**: Flexible logging library with multiple transports
  - Console transport for development
  - File transport for production logs
  - JSON format for structured logging
- **Morgan 1.x**: HTTP request logger middleware
  - 'dev' format for development
  - 'combined' format for production

#### Database Access

- **Sequelize 6.x**: Promise-based ORM for PostgreSQL
  - TypeScript support
  - Migration and seeding tools
  - Connection pooling
- **Mongoose 8.x**: MongoDB object modeling for Node.js
  - Schema validation
  - Middleware (pre/post hooks)
  - TypeScript support
- **ioredis 5.x**: Redis client with full TypeScript support
  - Connection pooling
  - Cluster support
  - Promise-based API

#### Testing

- **Jest 29.x**: Testing framework for unit and integration tests
  - TypeScript support via ts-jest
  - Code coverage reporting
  - Mocking capabilities
- **Supertest 6.x**: HTTP assertion library for API testing
- **@types/jest**: TypeScript definitions for Jest

#### Development Tools

- **tsx 4.x**: TypeScript execution for development
- **nodemon 3.x**: Auto-restart on file changes
- **dotenv 16.x**: Environment variable management

### Frontend Technology Stack

#### Core Framework & Build Tool

- **React 18.2.x**: Component-based UI library with concurrent features
- **Vite 5.x**: Fast build tool optimized for modern web development
  - Lightning-fast HMR (Hot Module Replacement)
  - Optimized production builds
  - Built-in TypeScript support
- **TypeScript 5.3.x**: Consistent type safety across frontend

#### Routing & Navigation

- **React Router 6.x**: Declarative routing for React applications
  - Nested routes
  - Data loading
  - Error boundaries
  - TypeScript support

#### Styling

- **Tailwind CSS 3.x**: Utility-first CSS framework
  - Rapid UI development
  - Consistent design system
  - Purging for small bundle sizes
- **PostCSS 8.x**: CSS transformations for Tailwind
- **Autoprefixer**: Vendor prefix automation

#### HTTP Client & State Management

- **Axios 1.x**: Promise-based HTTP client
  - Request/response interceptors
  - Automatic JSON transformation
  - Timeout support
  - Error handling
- **Zustand 4.x**: Lightweight state management
  - Simple API
  - TypeScript support
  - No boilerplate
  - Devtools support

#### Testing

- **Jest 29.x**: Testing framework
- **@testing-library/react 14.x**: React component testing utilities
- **@testing-library/jest-dom**: Custom Jest matchers for DOM
- **@testing-library/user-event**: User interaction simulation
- **vitest**: Vite-native test runner (alternative to Jest for faster tests)

#### Development Tools

- **@vitejs/plugin-react**: Official React plugin for Vite
- **vite-tsconfig-paths**: TypeScript path mapping in Vite

### Code Quality Tools

#### Linting

- **ESLint 8.x**: JavaScript/TypeScript linter
  - @typescript-eslint/parser
  - @typescript-eslint/eslint-plugin
  - eslint-plugin-react
  - eslint-plugin-react-hooks
  - eslint-plugin-jsx-a11y (accessibility)

#### Formatting

- **Prettier 3.x**: Opinionated code formatter
  - Consistent code style
  - Integration with ESLint
  - Auto-formatting on save

#### Git Hooks

- **husky 8.x**: Git hooks made easy
- **lint-staged 15.x**: Run linters on staged files

### Local Development Environment

#### Containerization

- **Docker 24.x**: Container platform
- **Docker Compose 2.x**: Multi-container orchestration

#### Database Services (Docker Compose)

```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: eucharist_dev
      POSTGRES_USER: eucharist_user
      POSTGRES_PASSWORD: dev_password
    ports:
      - '5432:5432'
    volumes:
      - postgres_data:/var/lib/postgresql/data

  mongodb:
    image: mongo:7.0
    environment:
      MONGO_INITDB_ROOT_USERNAME: mongo_user
      MONGO_INITDB_ROOT_PASSWORD: dev_password
      MONGO_INITDB_DATABASE: eucharist_content
    ports:
      - '27017:27017'
    volumes:
      - mongodb_data:/data/db

  redis:
    image: redis:7-alpine
    ports:
      - '6379:6379'
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
```

## Rationale

### Backend Choices

**Express.js over alternatives (Fastify, Koa, NestJS)**:

- ✅ Largest ecosystem of middleware
- ✅ Team familiarity and extensive documentation
- ✅ Flexibility without framework lock-in
- ✅ Proven production track record
- ⚠️ NestJS considered but deemed too heavy for Sprint 1

**Zod over Joi for validation**:

- ✅ TypeScript-first design
- ✅ Excellent type inference
- ✅ Smaller bundle size
- ✅ Better error messages
- ✅ Can derive TypeScript types from schemas

**Winston + Morgan for logging**:

- ✅ Winston: Production-grade with multiple transports
- ✅ Morgan: Simple HTTP request logging
- ✅ Complementary tools, not overlapping
- ✅ Industry standard combination

**Sequelize + Mongoose (not Prisma or TypeORM)**:

- ✅ Mature ecosystems with excellent documentation
- ✅ Separate tools for separate databases (single responsibility)
- ✅ Migration tools built-in
- ✅ Team familiarity
- ⚠️ Prisma considered but requires more learning time

### Frontend Choices

**Vite over Create React App or Webpack**:

- ✅ 10-100x faster HMR than CRA
- ✅ Built-in TypeScript support
- ✅ Optimized production builds
- ✅ Modern tooling with ESM
- ✅ CRA is no longer maintained

**React Router v6 over alternatives**:

- ✅ Official routing solution
- ✅ Data loading patterns
- ✅ Nested routes support
- ✅ Excellent TypeScript support

**Tailwind CSS over CSS-in-JS or plain CSS**:

- ✅ Rapid prototyping and development
- ✅ Consistent design system
- ✅ No runtime overhead (unlike styled-components)
- ✅ Small production bundle with purging
- ✅ Excellent documentation and community

**Zustand over Redux or Context API**:

- ✅ Minimal boilerplate (vs Redux)
- ✅ Better performance than Context API
- ✅ TypeScript support
- ✅ Simpler mental model for Sprint 1
- ⚠️ Can migrate to Redux later if needed

**Axios over Fetch API**:

- ✅ Request/response interceptors
- ✅ Automatic JSON transformation
- ✅ Better error handling
- ✅ Timeout support
- ✅ Cancellation support

### Development Tools

**Jest + Testing Library**:

- ✅ Industry standard for React testing
- ✅ Excellent documentation
- ✅ Good TypeScript support
- ✅ Built-in code coverage

**ESLint + Prettier**:

- ✅ Catches bugs and enforces style
- ✅ Prevents common mistakes
- ✅ Consistent code across team
- ✅ IDE integration

**Docker Compose for local dev**:

- ✅ Consistent environment across team
- ✅ Easy database setup
- ✅ No need to install databases locally
- ✅ Environment parity with production

## Consequences

### Positive

✅ **Rapid Development**: Modern tooling enables fast iteration  
✅ **Type Safety**: TypeScript throughout reduces runtime errors  
✅ **Developer Experience**: Excellent IDE support and documentation  
✅ **Production Ready**: All tools proven in production environments  
✅ **Community Support**: Active communities for all major dependencies  
✅ **Maintainability**: Well-documented, stable libraries  
✅ **Testing**: Comprehensive testing tools from day one  
✅ **Security**: Built-in security best practices (Helmet, bcrypt, rate limiting)

### Negative

⚠️ **Learning Curve**: Team needs to learn multiple tools simultaneously  
⚠️ **Dependency Count**: Many dependencies to maintain and update  
⚠️ **Version Management**: Need to keep all packages updated  
⚠️ **Initial Setup Time**: Takes time to configure all tools properly  
⚠️ **Bundle Size**: Frontend dependencies add to bundle size  
⚠️ **Testing Setup**: Jest + Testing Library configuration can be complex

### Neutral

➖ **Alternative Paths**: Most choices have viable alternatives if needed  
➖ **Migration Risk**: Some tools (like Zustand) might need replacement at scale  
➖ **Docker Requirement**: Team needs Docker installed for local development

## Implementation Plan

### Phase 1: Backend Foundation (Days 1-2)

**Package Installation**:

```bash
# Backend core
npm install express cors helmet morgan bcryptjs
npm install winston express-rate-limit zod express-validator
npm install sequelize pg pg-hstore mongoose ioredis
npm install dotenv

# TypeScript & Types
npm install -D typescript @types/node @types/express
npm install -D @types/cors @types/morgan @types/bcryptjs
npm install -D tsx nodemon ts-node

# Testing
npm install -D jest @types/jest ts-jest supertest @types/supertest
```

**Configuration**:

- [ ] Initialize TypeScript (tsconfig.json)
- [ ] Configure ESLint and Prettier
- [ ] Set up Winston logger
- [ ] Configure Sequelize connection
- [ ] Configure Mongoose connection
- [ ] Configure Redis client
- [ ] Create Express app with middleware

### Phase 2: Frontend Foundation (Days 3-4)

**Project Initialization**:

```bash
npm create vite@latest web -- --template react-ts
cd web
npm install
```

**Additional Dependencies**:

```bash
# Routing & HTTP
npm install react-router-dom axios zustand

# Styling
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Testing
npm install -D @testing-library/react @testing-library/jest-dom
npm install -D @testing-library/user-event vitest

# Types
npm install -D @types/react @types/react-dom
```

**Configuration**:

- [ ] Configure Tailwind CSS
- [ ] Set up React Router
- [ ] Configure Axios instance
- [ ] Create Zustand stores
- [ ] Set up testing environment

### Phase 3: Development Environment (Day 5)

**Docker Setup**:

```bash
# Create docker-compose.yml
# Start services
docker-compose up -d

# Verify connections
docker-compose ps
```

**Git Hooks**:

```bash
npm install -D husky lint-staged
npx husky install
npx husky add .husky/pre-commit "npx lint-staged"
```

**Lint-staged Configuration**:

```json
{
  "lint-staged": {
    "*.{js,jsx,ts,tsx}": ["eslint --fix", "prettier --write"],
    "*.{json,md,yml}": ["prettier --write"]
  }
}
```

### Phase 4: Documentation (Day 5)

- [ ] Update README with setup instructions
- [ ] Document environment variables
- [ ] Create contribution guidelines
- [ ] Document testing strategy
- [ ] Add code examples

## Version Pinning Strategy

### Approach

- **Major versions**: Pinned (e.g., "^4.19.0" for Express 4.x)
- **Minor updates**: Allowed via ^ (security patches and bug fixes)
- **Lock file**: Commit package-lock.json for reproducible builds
- **Updates**: Regular dependency audits (weekly)

### Update Schedule

- **Security patches**: Immediate
- **Minor updates**: Weekly review
- **Major updates**: Quarterly evaluation with testing

## Testing Strategy

### Backend Testing

```typescript
// Unit tests with Jest
describe('AuthService', () => {
  it('should hash password correctly', async () => {
    const password = 'Test123!';
    const hash = await hashPassword(password);
    expect(hash).not.toBe(password);
  });
});

// Integration tests with Supertest
describe('POST /api/auth/register', () => {
  it('should create new user', async () => {
    const response = await request(app)
      .post('/api/auth/register')
      .send({ email: 'test@example.com', password: 'Test123!' });
    expect(response.status).toBe(201);
  });
});
```

### Frontend Testing

```typescript
// Component tests with Testing Library
describe('LoginForm', () => {
  it('should render form fields', () => {
    render(<LoginForm />);
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  });
});
```

### Coverage Requirements

- **Unit tests**: Minimum 80% coverage
- **Integration tests**: All API endpoints covered
- **E2E tests**: Critical user flows (planned for Sprint 2)

## Success Criteria

### Development Environment

- [ ] Backend server starts without errors
- [ ] Frontend app loads in browser
- [ ] Database connections successful
- [ ] Hot reload works on both frontend and backend
- [ ] All linting and formatting rules pass
- [ ] Test suites run successfully

### Code Quality

- [ ] TypeScript compilation with no errors
- [ ] ESLint passes with 0 warnings
- [ ] Prettier formatting consistent
- [ ] Test coverage >80%
- [ ] All tests passing in CI

### Team Readiness

- [ ] All team members can run project locally
- [ ] Documentation clear and complete
- [ ] Setup time <30 minutes for new developers
- [ ] Team comfortable with tooling

## Security Considerations

### Dependency Security

- **npm audit**: Run on every install
- **Automated scanning**: GitHub Dependabot enabled
- **Version pinning**: Prevent unexpected updates
- **Regular updates**: Weekly security patch review

### Runtime Security

- **Helmet**: Sets security headers automatically
- **CORS**: Whitelist allowed origins
- **Rate limiting**: Prevent brute force attacks
- **Input validation**: Zod schemas for all inputs
- **Password hashing**: bcrypt with 12+ salt rounds

## Monitoring & Observability

### Logging Levels

```typescript
// Development
logger.level = 'debug';

// Production
logger.level = 'info';

// Logging structure
logger.info('User registered', {
  userId: user.id,
  email: user.email,
  timestamp: new Date().toISOString(),
});
```

### Performance Metrics

- **Response times**: Track with Morgan
- **Database queries**: Log slow queries (>100ms)
- **Error rates**: Track via Winston error logs
- **Memory usage**: Monitor Node.js heap

## Migration & Rollback

### Upgrade Path

- Tools can be upgraded incrementally
- Most major version changes don't require code rewrites
- TypeScript provides safety net for breaking changes

### Alternative Tools

If any tool proves inadequate:

- **Express → Fastify**: Similar API, straightforward migration
- **Zustand → Redux**: State management migration is well-documented
- **Sequelize → Prisma**: ORM migration tools available
- **Vite → Webpack**: Fallback if Vite issues arise

## Cost Analysis

### All Tools

- **Cost**: $0 (all open-source)
- **License**: MIT or similar permissive licenses
- **Support**: Community support via GitHub/Stack Overflow
- **Enterprise**: Optional paid support available for most tools

### Infrastructure Costs

- **Development**: $0 (Docker locally)
- **CI/CD**: Covered by ADR-005 (GitHub Actions)
- **Hosting**: TBD in deployment ADR

## References

- [Express.js Documentation](https://expressjs.com/)
- [Vite Documentation](https://vitejs.dev/)
- [React Router Documentation](https://reactrouter.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [Zod Documentation](https://zod.dev/)
- [Zustand Documentation](https://docs.pmnd.rs/zustand/)
- [Sequelize Documentation](https://sequelize.org/)
- [Mongoose Documentation](https://mongoosejs.com/)
- [Winston Documentation](https://github.com/winstonjs/winston)
- [Jest Documentation](https://jestjs.io/)
- [Testing Library Documentation](https://testing-library.com/)

## Related ADRs

- **ADR-001**: React + Next.js for Web Frontend (defines React choice)
- **ADR-003**: PostgreSQL + MongoDB Hybrid (defines database choices)
- **ADR-004**: JWT Authentication (defines auth strategy)
- **ADR-005**: CI/CD with GitHub Actions (defines deployment pipeline)

## Revision History

- **2025-11-06**: Initial version - Accepted for Sprint 1 implementation

---

**Next Review**: 2026-02-06 (3 months)  
**Owner**: Software Architect  
**Status**: Active
