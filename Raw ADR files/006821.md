# Technology Stack Selection

## Purpose
This document records the decisions regarding the core technology stack for Bartleby's implementation.

## Classification
- **Domain:** Technology
- **Stability:** Semi-stable
- **Abstraction:** Structural
- **Confidence:** Established

## Content

### Context

Bartleby requires:
- Backend API server (event processing, data persistence)
- Frontend SPA (card editing, network visualization)
- Database (event log + materialized views)
- Markdown editor (wiki link support)
- Build tooling (TypeScript compilation, bundling)
- Deployment (containerization)

The project prioritizes:
1. TypeScript throughout for type safety
2. Modern, well-maintained libraries
3. Single-user, local-first deployment
4. Fast development iteration
5. API-first architecture

### Decision

**Adopted Stack:**

**Backend:**
- **Runtime:** Node.js 20+
- **Framework:** Hono
- **Database:** SQLite (better-sqlite3)

**Frontend:**
- **Framework:** React 18+
- **Build Tool:** Vite
- **Routing:** TanStack Router
- **Server State:** TanStack Query
- **UI State:** Zustand
- **Markdown Editor:** Milkdown
- **Visualization:** D3.js

**Development:**
- **Language:** TypeScript 5+
- **Package Manager:** npm
- **Containerization:** Docker

### Status

Accepted

### Consequences

**Positive:**
- TypeScript end-to-end ensures type safety
- Modern tooling with excellent DX
- Battle-tested libraries reduce risk
- Active ecosystems for support and plugins
- Zero-config deployment (SQLite + Docker)

**Negative:**
- Learning curve for TanStack Router (newer library)
- Milkdown less mature than some alternatives
- D3.js complexity for network visualization
- Node.js overhead vs lightweight alternatives

**Risks:**
- Milkdown maintenance/stability unknown
- TanStack ecosystem relatively new
- SQLite limitations for future collaboration features

**Trade-offs:**
- Modern tooling vs. stability (accepted some newer libraries)
- TypeScript safety vs. runtime overhead
- Rich features vs. bundle size

### Alternatives Considered

#### Backend Framework

**Alternative: Express**
- **Pros:** Most popular, huge ecosystem, many examples
- **Cons:** Not TypeScript-native, middleware bloat, slower than Hono
- **Decision:** Hono chosen for TypeScript-first design and performance

**Alternative: Fastify**
- **Pros:** Fast, good TypeScript support, schema validation
- **Cons:** More complex than needed, overkill for single-user
- **Decision:** Hono simpler and sufficient

#### Database

**Alternative: PostgreSQL**
- **Pros:** Full-featured, better for multi-user, JSON support
- **Cons:** Requires separate process, overkill for single-user, complex setup
- **Decision:** SQLite perfect for embedded, file-based, single-user use case

**Alternative: JSON Files**
- **Pros:** Ultra-simple, easy to inspect, no dependencies
- **Cons:** No ACID, poor query performance, no indexes, manual locking
- **Decision:** SQLite provides database features with file-based simplicity

#### Frontend Framework

**Alternative: Vue**
- **Pros:** Simpler than React, good TypeScript, smaller bundle
- **Cons:** Smaller ecosystem for specialized needs (D3 integration, rich editors)
- **Decision:** React chosen for larger ecosystem and D3 integration experience

**Alternative: Svelte**
- **Pros:** Excellent DX, smallest bundles, reactive by default
- **Cons:** Smaller ecosystem, less enterprise adoption, fewer libraries
- **Decision:** React ecosystem more mature for markdown editing and visualization

#### Router

**Alternative: React Router**
- **Pros:** Industry standard, huge community, stable
- **Cons:** Not type-safe, manual type management, verbose
- **Decision:** TanStack Router chosen for TypeScript-first approach

#### Server State

**Alternative: SWR**
- **Pros:** Simple API, from Vercel, good documentation
- **Cons:** Less feature-rich than TanStack Query, smaller ecosystem
- **Decision:** TanStack Query more powerful, better TypeScript

**Alternative: Redux + RTK Query**
- **Pros:** Industry standard, very mature, excellent devtools
- **Cons:** Verbose, complex setup, overkill for this use case
- **Decision:** TanStack Query simpler, more focused on server state

#### Markdown Editor

**Alternative: CodeMirror 6**
- **Pros:** Very mature, highly customizable, excellent performance
- **Cons:** Lower-level, requires building WYSIWYG layer, steeper learning curve
- **Decision:** Milkdown provides WYSIWYG out of box with plugins

**Alternative: TipTap**
- **Pros:** WYSIWYG, ProseMirror-based, good docs, active development
- **Cons:** Vue-first (React support added later), larger bundle
- **Decision:** Milkdown more framework-agnostic, cleaner API

**Alternative: Slate**
- **Pros:** React-native, fully customizable, good TypeScript
- **Cons:** Requires building everything from scratch, complex to master
- **Decision:** Milkdown provides more out-of-box features

### Implementation Notes

**Backend (Hono + SQLite):**
```typescript
import { Hono } from 'hono';
import Database from 'better-sqlite3';

const app = new Hono();
const db = new Database('bartleby.db');

app.get('/api/cards', (c) => {
  const cards = db.prepare('SELECT * FROM cards').all();
  return c.json({ success: true, data: cards });
});
```

**Frontend (React + TanStack):**
```typescript
import { useQuery } from '@tanstack/react-query';
import { createRouter } from '@tanstack/react-router';

const { data: cards } = useQuery({
  queryKey: ['cards'],
  queryFn: () => fetch('/api/cards').then(r => r.json())
});
```

**Build (Vite):**
```typescript
// vite.config.ts
export default defineConfig({
  plugins: [react()],
  server: { proxy: { '/api': 'http://localhost:3000' } }
});
```

**Docker:**
```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY dist ./dist
COPY server ./server
EXPOSE 3000
CMD ["node", "server/index.js"]
```

## Relationships
- **Parent Nodes:** [foundation/principles.md], [foundation/structure.md]
- **Child Nodes:** None
- **Related Nodes:**
  - [api-server/overview.md] - implements - Uses Hono and SQLite
  - [frontend-app/overview.md] - implements - Uses React and TanStack
  - [data-model/overview.md] - implements - Stored in SQLite

## Navigation Guidance
- **Access Context:** Reference when setting up development environment or evaluating library choices
- **Common Next Steps:** Review implementation patterns, library documentation
- **Related Tasks:** Project setup, dependency management, build configuration
- **Update Patterns:** Revisit if major security issues or maintenance concerns with chosen libraries

## Metadata
- **Decision Number:** 003
- **Created:** 2025-11-14
- **Last Updated:** 2025-11-14
- **Updated By:** AI Agent (Claude)
- **Deciders:** Development team based on project requirements and constraints

## Change History
- 2025-11-14: Initial decision record created
