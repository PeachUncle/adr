# ADR-001: Technology Stack Selection

## Status
Accepted

## Context
The Recipe Keeper application requires a modern, scalable technology stack that can support:
- AI-powered recipe extraction from photos and URLs
- Real-time search and filtering capabilities
- Responsive web interface for desktop and mobile
- Containerized deployment for easy scaling
- High performance and good developer experience

We needed to choose technologies for frontend, backend, database, and deployment that work well together and align with our goals.

## Considered Options

### Frontend Options
- **Option 1**: React with TypeScript
  - Pros: Large ecosystem, excellent TypeScript support, great tooling
  - Cons: Steeper learning curve, more boilerplate

- **Option 2**: Vue.js with TypeScript
  - Pros: Gentle learning curve, good documentation, smaller bundle size
  - Cons: Smaller ecosystem, less TypeScript maturity

- **Option 3**: Next.js (React framework)
  - Pros: Full-stack capabilities, excellent performance, SSR/SSG
  - Cons: More complex for simple SPA, vendor lock-in

### Backend Options
- **Option 1**: Node.js with Express
  - Pros: JavaScript everywhere, huge ecosystem, excellent JSON handling
  - Cons: Single-threaded, callback complexity

- **Option 2**: Python with FastAPI
  - Pros: Excellent AI library support, automatic API docs, type hints
  - Cons: Different language from frontend, slower for I/O

- **Option 3**: Go with Gin/Echo
  - Pros: Excellent performance, compiled binary, good concurrency
  - Cons: Different language, smaller ecosystem for AI

### Database Options
- **Option 1**: PostgreSQL
  - Pros: Excellent JSON support, full-text search, ACID compliance
  - Cons: More complex setup than NoSQL

- **Option 2**: MongoDB
  - Pros: Schema flexibility, JSON-native
  - Cons: No ACID guarantees, less mature full-text search

- **Option 3**: SQLite
  - Pros: Simple setup, serverless
  - Cons: Limited concurrency, no built-in replication

## Decision

We chose:
- **Frontend**: React 18 with TypeScript, Vite, Tailwind CSS
- **Backend**: Node.js with Express and TypeScript
- **Database**: PostgreSQL with Prisma ORM
- **Deployment**: Docker containers with Docker Compose
- **AI Integration**: Google Gemini API via official SDK

### Rationale

1. **React + TypeScript**: Provides excellent developer experience, large ecosystem, and strong typing
2. **Node.js + Express**: Allows full-stack JavaScript, great for JSON APIs, huge ecosystem
3. **PostgreSQL**: Excellent JSON support for recipe data, robust full-text search, ACID compliance
4. **Prisma**: Type-safe database access, excellent migrations, good TypeScript integration
5. **Docker**: Consistent deployment, easy local development, scalable architecture
6. **Vite**: Fast development server, excellent TypeScript support, modern bundling
7. **Tailwind CSS**: Utility-first CSS, excellent for responsive design, great DX

## Consequences

### Positive
- **Unified Language**: JavaScript/TypeScript across frontend and backend reduces context switching
- **Type Safety**: TypeScript provides excellent type safety and IDE support
- **Performance**: Vite provides fast development builds, PostgreSQL excellent query performance
- **Scalability**: Docker containers can be easily scaled horizontally
- **Developer Experience**: Excellent tooling, debugging, and hot reloading
- **JSON Support**: PostgreSQL's JSON support perfect for recipe data structure
- **AI Integration**: Google Gemini API provides cutting-edge AI capabilities

### Negative
- **Learning Curve**: TypeScript and React require more initial learning
- **Complexity**: More moving parts than a simple stack
- **Single-threaded**: Node.js limitation for CPU-intensive tasks
- **Bundle Size**: React applications can be larger than alternatives
- **Database Complexity**: PostgreSQL requires more operational knowledge than simpler databases

### Neutral
- **Ecosystem Lock-in**: Heavy investment in JavaScript/TypeScript ecosystem
- **Tooling Complexity**: Multiple build tools and configurations to manage
- **Docker Dependency**: Requires Docker for local development

## Implementation Details

### Frontend Dependencies
- React 18 with hooks and concurrent features
- TypeScript 5.x with strict mode
- Vite 5.x for build tooling
- Tailwind CSS 3.x for styling
- Shadcn/ui for component library
- Zustand for state management
- React Router for navigation

### Backend Dependencies
- Node.js 20 LTS
- Express 4.x with TypeScript
- Prisma 5.x for database access
- JWT for authentication
- Winston for logging
- Jest for testing

### Database Schema
- PostgreSQL 15.x
- JSONB columns for ingredients, directions, nutrition
- Full-text search indices
- UUID primary keys

### Development Tools
- ESLint + Prettier for code quality
- Docker Compose for local development
- GitHub Actions for CI/CD
- Postman for API testing

## Related ADRs
- [ADR-002: Database Schema Design](./002-database-schema.md)
- [ADR-003: AI Service Integration](./003-ai-integration.md)

## Review Date
This decision should be reviewed if:
- Performance requirements significantly change
- Team expertise shifts to other technologies
- Major security vulnerabilities are discovered
- Better alternatives emerge in the ecosystem