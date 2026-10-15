# ADR-00004: Frontend Architecture and Technology Stack

## Status
**Accepted** - 2024-09-28

## Context
The AGoat Publisher system needs a modern, maintainable frontend that supports both content management and business-specific functionality (Thorne health products). The frontend must be responsive, accessible, and provide excellent user experience across different user types (content creators, readers, administrators, patients).

## Decision
Implement a unified React.js frontend using:
- **React 18** with TypeScript for type safety
- **Vite** as the build tool for fast development and optimized builds
- **Radix UI** for accessible, unstyled components
- **Tailwind CSS 4.1.12** for utility-first styling
- **React Router** for client-side routing
- **Axios** for HTTP client with interceptors
- **Wysimark** for rich text editing
- **DOMPurify** for content sanitization
- **Marked** for markdown processing

## Rationale
1. **Modern React**: React 18 provides latest features and performance improvements
2. **Type Safety**: TypeScript reduces runtime errors and improves developer experience
3. **Build Performance**: Vite provides fast development server and optimized builds
4. **Accessibility**: Radix UI components are built with accessibility in mind
5. **Design System**: Tailwind CSS provides consistent, maintainable styling
6. **Rich Content**: Wysimark provides modern rich text editing capabilities
7. **Security**: DOMPurify prevents XSS attacks in user-generated content
8. **Unified Architecture**: Single React app eliminates Module Federation complexity

## Consequences

### Positive
- **Developer Experience**: Fast development with Vite and TypeScript
- **User Experience**: Modern, responsive, accessible interface
- **Maintainability**: Single codebase with consistent patterns
- **Performance**: Optimized builds and fast loading times
- **Accessibility**: Built-in accessibility features from Radix UI
- **Security**: Content sanitization and type safety
- **Scalability**: Component-based architecture supports growth

### Negative
- **Bundle Size**: Single app may have larger initial bundle
- **Learning Curve**: Team needs expertise in multiple technologies
- **Dependencies**: Many dependencies to manage and update
- **Complexity**: Rich text editing and content management complexity

## Implementation Details

### Technology Stack
```json
{
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "@radix-ui/themes": "^2.0.0",
    "@radix-ui/react-*": "^1.x.x",
    "@tailwindcss/postcss": "^4.1.12",
    "@wysimark/react": "^3.0.20",
    "axios": "^1.11.0",
    "dompurify": "^3.2.6",
    "marked": "^16.2.0",
    "react-router-dom": "^6.x.x"
  }
}
```

### Architecture Patterns
1. **Component-Based**: Reusable components with clear interfaces
2. **Context API**: Global state management for authentication and themes
3. **Custom Hooks**: Reusable logic for API calls and state management
4. **Error Boundaries**: Graceful error handling and recovery
5. **Lazy Loading**: Code splitting for better performance

### Key Features
1. **Responsive Design**: Mobile-first approach with Tailwind CSS
2. **Accessibility**: WCAG 2.1 AA compliance through Radix UI
3. **Rich Text Editing**: Modern WYSIWYG editor with markdown support
4. **Content Sanitization**: XSS protection with DOMPurify
5. **Authentication**: OIDC-compliant authentication flows
6. **State Management**: Context-based state with React hooks

### Development Workflow
1. **Hot Reload**: Vite provides instant feedback during development
2. **Type Checking**: TypeScript provides compile-time error checking
3. **Linting**: ESLint and Prettier for code quality
4. **Testing**: Jest and React Testing Library for unit tests
5. **Build Optimization**: Vite optimizes for production builds

### Security Measures
- Content sanitization with DOMPurify
- TypeScript for type safety
- Secure HTTP client with Axios interceptors
- XSS protection in rich text content
- CSRF protection through authentication flows

## References
- [React 18 Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Radix UI Documentation](https://www.radix-ui.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [Wysimark Documentation](https://wysimark.com/)
- [DOMPurify Documentation](https://github.com/cure53/DOMPurify)
- [Frontend Requirements](../../requirements-and-user-stories/final-functional/authentication-requirements.md)
- [Performance Requirements](../../requirements-and-user-stories/final-nonfunctional/performance-requirements.md)
