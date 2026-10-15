# ADR-0002: React Frontend Architecture

**Status:** Accepted  
**Date:** 2025-11-26 (Updated 2025-12-01)  
**Supersedes:** None  
**Superseded By:** N/A

---

## Context

We needed to establish a modern, maintainable React frontend architecture for the work productivity tracking application. Key requirements included:

- Web-based interface (user preference from questionnaire)
- Integration with Flask REST API
- Support for 7 core features with distinct views
- State management across components
- Fast development iteration (January MVP deadline)
- Excellent developer experience
- Modern React 18+ patterns

Considerations:
- Build tool choice (performance, DX)
- State management complexity
- Project organization strategy
- Routing for multi-page experience
- API communication patterns

## Decision

We will use **Vite + React 18** with **Zustand for state management**, **Feature-based project structure**, and **React Router v6** for navigation.

### Core Stack Components:

1. **Build Tool: Vite**
   - Lightning-fast hot module replacement (HMR)
   - Optimized production builds with esbuild
   - Native ES modules
   - Superior developer experience vs Create React App

2. **State Management: Zustand**
   - Minimal boilerplate (simpler than Redux)
   - Hook-based API (modern React pattern)
   - Small bundle size (~1KB)
   - Perfect balance of simplicity and power
   - Easy to learn and use

3. **Project Structure: Feature-Based**
   ```
   src/
   ├── features/           # Feature modules
   │   ├── projects/       # Project organization (Priority #1)
   │   ├── dailyFocus/
   │   ├── learningJournal/
   │   ├── skills/
   │   ├── meetings/
   │   ├── goals/
   │   ├── feedback/
   │   └── energy/
   ├── components/         # Shared components
   ├── services/           # API calls
   ├── hooks/              # Custom hooks
   └── utils/              # Utilities
   ```

4. **Navigation: React Router v6**
   - Standard React routing solution
   - Declarative route definitions
   - Nested routes support
   - URL-based navigation

5. **API Communication: Axios with Service Layer**
   - Centralized API configuration
   - Request/response interceptors
   - Service modules per feature
   - Custom hooks for API calls

### Key Patterns:

- **Functional Components + Hooks** (no class components)
- **Small, Focused Components** (single responsibility)
- **Custom Hooks** for reusable logic
- **Service Layer** for API calls (parallel to backend)
- **Co-location** (component, styles, tests together)

## Consequences

### Positive

- **Performance**: Vite provides fastest development experience; instant HMR
- **Developer Experience**: Modern tooling, minimal configuration, fast feedback loop
- **Maintainability**: Feature-based structure maps directly to 7 core features; easy to navigate
- **Scalability**: Clean separation allows adding features without touching existing code
- **Simplicity**: Zustand requires minimal boilerplate; easier to learn than Redux
- **Consistency**: Service layer matches backend architecture pattern
- **Modern Stack**: Using 2024 best practices and actively maintained tools
- **Bundle Size**: Vite optimization + Zustand's small size = lean production builds

### Negative

- **Ecosystem Maturity**: Zustand newer than Redux (smaller community, fewer plugins)
- **Migration Path**: Less established patterns for migration if Zustand proves insufficient
- **Learning Curve**: Team needs to learn Vite (if coming from CRA) and Zustand
- **Tooling Differences**: Vite config differs from Webpack/CRA

**Mitigation:**
- Zustand's simplicity means less to learn than Redux
- Can migrate to Redux later if needed (service layer makes this easier)
- Vite's excellent documentation eases transition
- Zustand sufficient for our use case (single-user local app)

## Alternatives Considered

### Alternative 1: Create React App (CRA) + Context API

**Description:** Official React bootstrapping tool with built-in Context API for state

**Pros:**
- Most widely known/documented
- Zero configuration
- Context API built into React
- Mature tooling

**Cons:**
- Slower build times and HMR than Vite
- Webpack-based (older technology)
- Context API can cause performance issues with frequent updates
- CRA less actively maintained
- Larger bundle sizes

**Why Not Chosen:** Vite offers significantly better developer experience. Context API's re-render issues problematic for frequently updated data (task lists, time tracking). Performance matters for MVP timeline.

### Alternative 2: Next.js

**Description:** React framework with server-side rendering and file-based routing

**Pros:**
- Production-ready out of the box
- SEO benefits (SSR)
- Built-in API routes
- Excellent documentation

**Cons:**
- Overkill for local single-user app
- SSR unnecessary (not a web app accessed via browsers)
- More complex than needed
- Framework lock-in
- Heavier than simple React + Vite

**Why Not Chosen:** We don't need SSR, SEO, or framework features. Local desktop app doesn't benefit from Next.js's strengths. Adds unnecessary complexity.

### Alternative 3: Redux for State Management

**Description:** Battle-tested state management library with large ecosystem

**Pros:**
- Industry standard
- Excellent devtools
- Large community and resources
- Proven scalability
- Middleware ecosystem

**Cons:**
- Significant boilerplate (actions, reducers, types)
- Steeper learning curve
- More complex setup
- Overkill for our use case
- Slower development velocity

**Why Not Chosen:** Redux is overkill for single-user local app. Boilerplate slows MVP development. Zustand provides 80% of benefits with 20% of complexity.

### Alternative 4: Type-Based Project Structure

**Description:** Organize by file type (components/, containers/, services/)

**Pros:**
- Traditional approach
- Clear file type separation
- Familiar to many developers

**Cons:**
- Feature code spread across multiple directories
- Difficult to find related files
- Doesn't scale well with feature count
- Coupling between unrelated features harder to spot

**Why Not Chosen:** Feature-based structure maps better to our 7 core features. Easier to navigate and maintain. Industry moving toward feature-based organization.

## Implementation Notes

1. **Setup:**
   ```bash
   npm create vite@latest frontend -- --template react
   npm install zustand axios react-router-dom
   ```

2. **Feature Structure Template:**
   ```
   features/[featureName]/
   ├── [FeatureName]View.jsx    # Main view component
   ├── components/               # Feature-specific components
   ├── use[FeatureName].js       # Custom hook
   └── [featureName]Service.js   # API calls (optional, or in services/)
   ```

3. **Zustand Store Pattern:**
   ```javascript
   // stores/useTaskStore.js
   import create from 'zustand'
   
   export const useTaskStore = create((set) => ({
     tasks: [],
     addTask: (task) => set((state) => ({ 
       tasks: [...state.tasks, task] 
     }))
   }))
   ```

4. **Service Layer:**
   ```javascript
   // services/tasksService.js
   import api from './api'
   
   export const tasksService = {
     getAll: () => api.get('/tasks'),
     create: (data) => api.post('/tasks', data)
   }
   ```

5. **Vite Proxy Configuration:**
   ```javascript
   // vite.config.js
   export default defineConfig({
     server: {
       proxy: {
         '/api': 'http://localhost:5000'
       }
     }
   })
   ```

## References

- [React Frontend Architecture Research](../research/tech-stack/react-frontend-architecture.md) - Comprehensive analysis (500+ lines)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Zustand Documentation](https://docs.pmnd.rs/zustand)
- [React Router Documentation](https://reactrouter.com/)

## Related ADRs

- **ADR-0001:** Flask Backend Architecture - Backend counterpart to this frontend architecture
- **ADR-0003:** SQLite Database Design - Database layer for this frontend
- **ADR-0004:** Flask-React Integration Strategy - Integration approach between this frontend and Flask
- **ADR-0005:** Projects as Foundation Architecture - Feature priority decision that added `projects/` feature module

---

**Last Updated:** 2025-11-26  
**Status:** ✅ Accepted and Active





