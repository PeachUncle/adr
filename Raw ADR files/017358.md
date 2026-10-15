# ADR-010: Express.js for API Server

**Date**: 2025-10-27
**Status**: Accepted
**Epic**: Epic 005 - Backend Service Refactoring
**Related ADRs**: [ADR-001 (Inversify DI)](./ADR-001-inversify-dependency-injection.md), [ADR-011 (OpenAPI)](./ADR-011-openapi-documentation.md)

## Context

We needed a web framework for our Node.js backend API server with:
- RESTful API routing
- Middleware support (auth, logging, validation)
- TypeScript compatibility
- Large ecosystem and community
- Production-ready performance

## Decision

We will use **Express.js 4.x** as our web application framework.

**Implementation**:
```typescript
import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import { container } from './infrastructure/container';

const app = express();

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Routes
app.use('/api/payments', paymentRoutes);
app.use('/api/users', userRoutes);
app.use('/api/content', contentRoutes);

// Error handling
app.use(errorHandler);

app.listen(3001, () => {
  console.log('API server running on port 3001');
});
```

## Consequences

### Positive

1. **Mature Ecosystem**: Thousands of middleware packages available
2. **Easy Learning Curve**: Simple, intuitive API
3. **TypeScript Support**: Excellent type definitions
4. **Community**: Large community and extensive documentation
5. **Production Proven**: Used by millions of applications

### Negative

1. **Not the Fastest**: Fastify is faster (~2x performance)
2. **Callback-Based**: Older async pattern (vs native async/await)
3. **Minimal Features**: Need to add middleware for most features

**Why Worth It**: Maturity and ecosystem outweigh performance difference for our use case.

## Alternatives Considered

- **Fastify**: Faster but smaller ecosystem - Considered for future
- **Koa**: More modern but less mature - Rejected
- **NestJS**: Too opinionated, complete rewrite - Rejected
- **Hapi**: Less popular, smaller community - Rejected

## Middleware Stack

```typescript
// Security
app.use(helmet());
app.use(cors({ origin: ALLOWED_ORIGINS }));
app.use(rateLimit({ windowMs: 15 * 60 * 1000, max: 100 }));

// Parsing
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Logging
app.use(morgan('combined'));

// Authentication
app.use(authMiddleware);

// Validation
app.use(validationMiddleware);
```

## Related Documentation

- [Express.js Documentation](https://expressjs.com)
- [API Architecture](/docs/architecture/diagrams/epic-005-api-architecture.mmd)
- [Backend Developer Guide](/docs/development/backend-developer-guide.md)

## Revision History

- **2025-10-27**: Initial decision documented for Epic 005
