# Docker Container Per Book Deployment

## Purpose
This document records the decision to deploy each book project as a separate, self-contained Docker container.

## Classification
- **Domain:** Deployment Architecture
- **Stability:** Static
- **Abstraction:** Structural
- **Confidence:** Established

## Content

### Context

Bartleby is designed for authors writing books. Key considerations:

1. **Isolation:** Each book is independent (different content, metadata, state)
2. **Simplicity:** Authors want "one command" to start working
3. **Multi-project:** Authors may work on multiple books simultaneously
4. **Local-first:** v1 targets local development, not cloud SaaS
5. **No shared state:** Books don't interact or share data

The question was how to handle multiple book projects:
- Single application instance with multi-tenancy?
- Separate database per book, shared application?
- Completely separate containers per book?

### Decision

**One Docker container per book project:**

- Each container includes: frontend (static files), API server, SQLite database
- Each container runs on different port (3001, 3002, etc.)
- Volume mount for database persistence: `-v ./my-novel-data:/app/data`
- No shared state between containers
- Authors can run multiple containers concurrently

### Status

Accepted

### Consequences

**Positive:**
- **Perfect isolation:** No risk of cross-book data corruption
- **Simple deployment:** `docker run -p 3001:3000 -v ./data:/app/data bartleby`
- **Easy multi-project:** Run N containers for N books
- **Independent versions:** Different books can use different Bartleby versions
- **Resource control:** Can limit resources per book
- **Easy backup:** Just copy the volume directory
- **No auth needed:** Each container is isolated to localhost
- **Migration simple:** Move volume folder to migrate book

**Negative:**
- **Resource overhead:** Duplication of application code in memory per container
- **No cross-book features:** Can't search across all books, link between books
- **Port management:** User must track which port is which book
- **More containers to manage:** Could get unwieldy with many books

**Risks:**
- Port conflicts if not managed
- Memory usage with many concurrent books
- Complexity in switching between books (different ports)

**Trade-offs:**
- Simplicity and isolation over resource efficiency
- Local-first over cloud-native architecture
- Single-user convenience over multi-user features

### Alternatives Considered

#### Alternative 1: Single Instance with Project Switching

One application, users create/switch between projects via UI.

**Pros:**
- Single port, single container
- Lower resource usage
- Easier to switch between books
- Could add cross-book search

**Cons:**
- Requires multi-tenancy logic
- Database schema more complex (project_id everywhere)
- All books must use same Bartleby version
- Single point of failure affects all books
- More complex backup/restore
- Requires authentication or project selection UI

#### Alternative 2: Shared Backend, Separate Databases

One API server, multiple SQLite files, route by subdomain or path.

**Pros:**
- Some resource sharing (one Node process)
- Still good isolation of data
- Single container

**Cons:**
- Complex routing logic
- Concurrent access to multiple DBs from one process
- Still need project selection mechanism
- Less portable (can't move single book easily)

#### Alternative 3: Separate Processes, Shared Machine

Multiple instances of app, different ports, no containerization.

**Pros:**
- Very simple (just run server multiple times)
- No Docker dependency
- Familiar pattern

**Cons:**
- No environment isolation
- Dependency version conflicts possible
- Less portable across machines
- Manual process management
- Harder to distribute/deploy

### Implementation Notes

1. **Container Start Command:**
   ```bash
   docker run -d \
     --name my-novel \
     -p 3001:3000 \
     -v ./my-novel-data:/app/data \
     bartleby:latest
   ```

2. **Multi-stage Dockerfile:**
   ```dockerfile
   # Build frontend
   FROM node:20-alpine AS frontend-build
   WORKDIR /app/frontend
   COPY frontend/package*.json ./
   RUN npm ci
   COPY frontend/ ./
   RUN npm run build

   # Build backend
   FROM node:20-alpine AS backend-build
   WORKDIR /app/backend
   COPY backend/package*.json ./
   RUN npm ci
   COPY backend/ ./
   RUN npm run build

   # Final image
   FROM node:20-alpine
   WORKDIR /app
   COPY --from=backend-build /app/backend/dist ./server
   COPY --from=backend-build /app/backend/node_modules ./node_modules
   COPY --from=frontend-build /app/frontend/dist ./public
   VOLUME /app/data
   EXPOSE 3000
   CMD ["node", "server/index.js"]
   ```

3. **Database Path:**
   - SQLite file: `/app/data/bartleby.db`
   - Exports: `/app/data/exports/`
   - Volume-mounted for persistence

4. **Port Convention:**
   - Container internal: Always 3000
   - Host external: User choice (e.g., -p 3001:3000, -p 3002:3000)

5. **Book Organization:**
   ```
   ~/writing/
     my-novel/
       data/              # Volume mount
         bartleby.db
         exports/
       docker-compose.yml # Optional: defines container
     cookbook/
       data/
       docker-compose.yml
   ```

6. **Docker Compose (Optional):**
   ```yaml
   version: '3.8'
   services:
     bartleby:
       image: bartleby:latest
       container_name: my-novel
       ports:
         - "3001:3000"
       volumes:
         - ./data:/app/data
       restart: unless-stopped
   ```

## Relationships
- **Parent Nodes:** [foundation/principles.md]
- **Child Nodes:** None
- **Related Nodes:**
  - [foundation/structure.md] - implements - Deployment model part of overall structure
  - [data-model/overview.md] - isolates - Each container has independent database

## Navigation Guidance
- **Access Context:** Reference when setting up deployments, planning book organization, or troubleshooting container issues
- **Common Next Steps:** Review Dockerfile, volume mount configuration, multi-book workflows
- **Related Tasks:** Docker image building, container deployment, data backup/migration
- **Update Patterns:** Revisit if cloud deployment or multi-user features become priorities

## Metadata
- **Decision Number:** 004
- **Created:** 2025-11-14
- **Last Updated:** 2025-11-14
- **Updated By:** AI Agent (Claude)
- **Deciders:** Development team based on deployment requirements

## Change History
- 2025-11-14: Initial decision record created
