# ADR 001: Framework Selection - Next.js

## Status
Accepted

## Context
We need to choose a web framework for the Rate Your Day application. The requirements are:
- Responsive design (mobile and desktop)
- Simple CRUD operations for mood ratings
- Calendar view with monthly data
- Fast development timeline
- Azure deployment

The two candidates considered were:
1. **Next.js** (React-based full-stack framework)
2. **Flask** (Python micro-framework)

## Decision
We will use **Next.js 14+** with the App Router.

## Rationale

### Why Next.js over Flask

| Factor | Next.js | Flask |
|--------|---------|-------|
| Frontend + Backend | Single codebase | Separate frontend needed |
| TypeScript | Native support | Requires setup |
| Responsive UI | React ecosystem | Manual or separate framework |
| Calendar components | Many React libraries | Fewer options |
| API routes | Built-in | Built-in |
| Development speed | Faster for this use case | More setup required |
| Azure deployment | Container Apps / Static Web Apps | Container Apps |

### Key Advantages

1. **Single Codebase**: Next.js API routes eliminate the need for a separate backend service, reducing complexity.

2. **React Ecosystem**: Rich component libraries for calendars (react-calendar, date-fns) and responsive design (Tailwind CSS).

3. **TypeScript First**: Native TypeScript support ensures type safety across frontend and backend.

4. **Developer Experience**: Hot reload, built-in routing, and excellent documentation accelerate development.

5. **Deployment Flexibility**: Can deploy as a container to Azure Container Apps or as a static site with serverless functions.

### Trade-offs Accepted

- Slightly larger bundle size than a minimal Flask + vanilla JS solution
- Node.js runtime instead of Python (team familiarity may vary)
- React learning curve for developers new to the ecosystem

## Consequences

### Positive
- Faster time to MVP
- Single deployment artifact
- Type safety across the stack
- Rich UI component ecosystem

### Negative
- Requires Node.js knowledge
- React-specific patterns to learn
- Slightly more complex than a static HTML + API approach

## Alternatives Considered

### Flask + React SPA
- Pro: Python backend, React frontend flexibility
- Con: Two separate applications to maintain, deploy, and coordinate

### Flask + HTMX
- Pro: Simple, minimal JavaScript
- Con: Fewer calendar UI options, less polished mobile experience

### Remix
- Pro: Similar benefits to Next.js
- Con: Smaller ecosystem, less Azure deployment documentation

## References
- [Next.js Documentation](https://nextjs.org/docs)
- [Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/)
