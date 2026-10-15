# ADR-0002: Frontend Architecture

## Status
Accepted

## Context
We need to choose a frontend architecture that supports:
- Modern React patterns
- Type safety
- Component reusability
- State management
- Form handling with validation

## Decision
We will use the following frontend architecture:

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI Library**: Radix UI primitives with shadcn/ui components
- **State Management**: 
  - Context API for global UI state (auth, theme, notifications)
  - TanStack Query (React Query) for server state
  - React Hook Form for form state
- **Validation**: Zod schemas from shared package
- **Routing**: Client-side routing with custom AppLayout component

### Component Organization

```
apps/web/src/
├── components/
│   ├── a11y/          # Accessibility components
│   ├── auth/          # Authentication components
│   ├── chatbot/       # Chat-related components
│   ├── dashboard/     # Dashboard components
│   ├── feed/          # Feed optimizer components
│   ├── layout/        # Layout components
│   ├── theme/         # Theme components
│   └── ui/            # Reusable UI primitives (shadcn/ui)
├── contexts/          # React contexts
├── hooks/             # Custom React hooks
├── lib/               # Utilities and helpers
└── pages/             # Page components
```

### Rationale

1. **React 18**: Latest features, concurrent rendering, and broad ecosystem support
2. **TypeScript**: Type safety catches errors at compile time
3. **Vite**: Fast development server and optimized builds
4. **Radix UI**: Accessible, unstyled components with full customization
5. **Context API**: Sufficient for global UI state without Redux overhead
6. **TanStack Query**: Excellent for server state, caching, and synchronization
7. **React Hook Form**: Performant form handling with Zod validation

## Consequences

### Positive
- Type-safe components and props
- Accessible components out of the box (Radix UI)
- Excellent developer experience with Vite
- Efficient form handling with React Hook Form
- Clear separation of concerns

### Negative
- Learning curve for React Hook Form and TanStack Query
- Multiple state management approaches (though each has clear purpose)
- Need to maintain consistency across component patterns

## Alternatives Considered

1. **Redux/Zustand**: Rejected - Context API sufficient for current needs
2. **Next.js**: Rejected - Not needed for SPA, adds complexity
3. **Styled Components**: Rejected - Tailwind CSS more suitable for this project
4. **Material UI**: Rejected - Radix UI provides better customization

