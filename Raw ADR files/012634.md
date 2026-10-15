# ADR-0009: Vue.js Admin Dashboard Architecture

## Status
**Accepted**

## Context
The Nucleus project needed a modern, responsive admin dashboard to provide observability and management capabilities for AI workflow evaluations. The requirements included:

- Real-time data visualization and metrics
- Responsive design for mobile and desktop
- Modern UI/UX with intuitive navigation
- Integration with existing ASP.NET Core API
- Export functionality for data analysis
- Comprehensive settings management

The team needed to choose a frontend technology stack that would provide excellent developer experience, modern tooling, and seamless integration with the existing backend architecture.

## Decision
We chose Vue.js 3 with the following technology stack:

- **Vue.js 3** with Composition API for modern reactive components
- **Tailwind CSS** for utility-first styling and responsive design
- **Pinia** for state management with reactive stores
- **Vue Router** for client-side navigation
- **Chart.js** for data visualization
- **Vite** for fast development and building
- **Axios** for HTTP client communication

The dashboard architecture follows a modular component design with:
- Layout components (AppLayout, Sidebar, Header)
- Feature components (Dashboard, Evaluations, Settings)
- Reusable UI components (charts, tables, forms)
- Pinia stores for reactive state management
- Vite proxy configuration for seamless API integration

## Consequences

### Positive
- **Modern Development Experience**: Vue.js 3 with Composition API provides excellent developer experience
- **Responsive Design**: Tailwind CSS enables rapid development of mobile-friendly interfaces
- **Reactive State Management**: Pinia provides clean, reactive state management
- **Fast Development**: Vite offers hot module replacement and fast builds
- **Seamless Integration**: Vite proxy handles API communication without CORS issues
- **Component Reusability**: Modular architecture enables code reuse and maintainability
- **Type Safety**: TypeScript support for better development experience

### Negative
- **Learning Curve**: Team needs Vue.js 3 knowledge (mitigated by modern documentation)
- **Bundle Size**: Additional frontend dependencies increase overall application size
- **Complexity**: Frontend adds another layer to the application stack

### Neutral
- **Technology Diversity**: Introduces JavaScript/TypeScript alongside C# backend
- **Deployment Complexity**: Requires separate frontend build and deployment process

## Rationale
Vue.js 3 was chosen over alternatives (React, Angular, Svelte) for several reasons:

1. **Gentle Learning Curve**: Vue.js provides excellent documentation and gradual adoption
2. **Composition API**: Modern reactive programming model aligns with current best practices
3. **Ecosystem**: Rich ecosystem with Tailwind CSS, Pinia, and Chart.js integration
4. **Performance**: Excellent runtime performance and small bundle sizes
5. **Developer Experience**: Vite provides fast development server and build times

The decision to use Tailwind CSS was driven by:
- Rapid development capabilities
- Consistent design system
- Excellent responsive design support
- Strong community and documentation

Pinia was chosen over Vuex for:
- Better TypeScript support
- Simpler API and less boilerplate
- Composition API integration
- Official Vue.js recommendation

## Related Decisions
- [ADR-0001: Clean Architecture](../adr/ADR-0001-clean-architecture.md)
- [ADR-0002: ASP.NET Core](../adr/ADR-0002-aspnet-core.md)
- [ADR-0008: Entity Framework](../adr/ADR-0008-entity-framework.md)

## References
- [Vue.js 3 Documentation](https://vuejs.org/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [Pinia Documentation](https://pinia.vuejs.org/)
- [Vite Documentation](https://vitejs.dev/) 