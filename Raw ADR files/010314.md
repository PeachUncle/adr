# ADR-005: Frontend Architecture

## Status

Accepted

## Context

The Learning Platform requires a modern, maintainable, and scalable frontend architecture that enables efficient development, testing, and user experience. This ADR documents the key architectural decisions for the frontend implementation.

## Decision: Technologies and Structure

### 1. **Build Tool**: Vite

- Vite is used as the build tool and development server to enable faster builds and Hot Module Replacement (HMR).
- Optimized for React and TypeScript with minimal configuration.
- Leverages native ES modules for faster development feedback loops.

### 2. **Frontend Framework**: React 18

- React is used for the user interface to enable a component-based architecture with high reusability.
- Utilizes functional components with hooks for state management and lifecycle events.
- Takes advantage of React 18 features like automatic batching and concurrent rendering capabilities.

### 3. **UI Library**: Material UI (MUI)

- Material UI is used as the design system to provide consistent and appealing UI components.
- Centralized theme configuration for consistent styling across the application.
- Custom component extensions maintain visual consistency while meeting specific requirements.

### 4. **State Management**: Zustand & React Query

- Zustand is used for centralized application state management to provide a lean and performant state management solution.
- React Query is used for server state management, providing automatic caching, background updates, and optimistic UI updates.
- Clear separation between client state (Zustand) and server state (React Query).

### 5. **Test Framework**: Vitest & Playwright

- End-to-end tests are conducted with Playwright to ensure UI and API stability.
- Vitest for unit and component testing with a focus on testing behavior rather than implementation.
- Global test mocks and utilities defined in setupTests.ts for consistency across tests.

### 6. **Programming Language**: TypeScript

- TypeScript is used to ensure type safety and better maintainability of the code.
- Strict type checking enabled to catch potential errors during development.
- Interfaces prefixed with 'I' (e.g., IUserProps) for clarity and consistency.

### 7. **Linting**: ESLint

- ESLint is used to ensure code quality and consistency within the project.
- Custom rule configuration aligned with project requirements and best practices.
- Integration with TypeScript for enhanced static analysis.

### 8. **Project Structure**

```plaintext
frontend/
│── src/
│   ├── assets/                # Global assets (images, fonts, global styles)
│   ├── components/            # Reusable UI components
│   │   ├── common/            # Shared components (e.g., DataTable, StatusChip)
│   │   └── layout/            # Layout components (Header, Footer, etc.)
│   │
│   ├── features/              # Feature-specific components and logic
│   │   ├── auth/              # Authentication-related components and hooks
│   │   ├── courses/           # Course management components
│   │   ├── dashboard/         # Dashboard and analytics components
│   │   └── learningTasks/     # Learning task-related components
│   │
│   ├── hooks/                 # Custom React hooks
│   │
│   ├── services/              # API service layer
│   │   ├── api/               # Centralized API logic
│   │   └── auth/              # Authentication services
│   │
│   ├── store/                 # Zustand state management stores
│   │
│   ├── theme/                 # Material UI theme configuration
│   │
│   ├── types/                 # TypeScript type definitions
│   │
│   ├── utils/                 # Shared utility functions
│   │
│   ├── routes/                # Application routing configuration
│   │
│   ├── tests/                 # Test utilities and setup
│   │   └── setupTests.ts      # Global test configuration
│   │
│   ├── App.tsx                # Root application component
│   ├── main.tsx               # Application entry point
│   └── vite-env.d.ts          # Vite environment types
```

- **Feature-based Organization**: Code is primarily organized by features/domains rather than by technical types.
- **Shared Components**: Common UI components are extracted to a shared folder to promote reuse.
- **Path Aliases**: Use of path aliases (e.g., `@components/*`, `@features/*`) for cleaner imports.

### 9. **API Layer (Isolated Communication with Backend)**

API services are organized within each domain. Each domain has its own set of API services responsible for interacting with the backend. For example, the `courses` domain has `coursesApi.ts` for managing courses, and the `tasks` domain has `tasksApi.ts` for managing tasks.

- **Centralized API Service Layer**:
  - Base `ApiService` class provides core functionality for API requests.
  - Resource-specific services extend or use the base service.
  - Standardized error handling and response normalization.
  - Automatic token inclusion via Axios interceptors.

- **API Endpoints Structure**:
  - `authApi.ts` → Authentication endpoints (`/auth/login/`, `/auth/logout/`, `/auth/register/`)
  - `usersApi.ts` → User profile and management (`/users/profile/`)
  - `coursesApi.ts` → Course management (`/courses/`)
  - `learningTasksApi.ts` → Learning task management (`/learning-tasks/`)
  - `quizApi.ts` → Quiz-related endpoints (`/quizzes/`, `/quiz-attempts/`)

### 10. **Authentication Architecture**

- **JWT-based Authentication**:
  - Token management via dedicated `AuthService`.
  - Tokens stored in localStorage with appropriate security measures.
  - Automatic token refresh when expired.
  - Auth state globally available through `useAuth` hook.

- **Access Control**:
  - Role-based route protection using `ProtectedRoute` and `RoleBasedRoute` components.
  - Component-level access control through conditional rendering.
  - Permission checks embedded in API service calls.

### 11. **State Management with Zustand & React Query**

- **Client State Management** (Zustand):
  - Separate stores for different domains:
    - `authStore.ts` - Authentication state
    - `uiStore.ts` - UI state (modals, themes, etc.)
    - `settingsStore.ts` - User preferences

- **Server State Management** (React Query):
  - Consistent query and mutation hooks:
    - `useQuery` for data fetching
    - `useMutation` for data updates
    - `useQueryClient` for cache manipulation
  - Optimistic updates for better user experience
  - Automatic retries and background refetching

- Stores are organized by domain with clear boundaries between functionality.

### 12. **Component Design Philosophy**

- **Separation of Concerns**:
  - UI components focus on presentation only
  - Business logic extracted to custom hooks and services
  - Container components connect UI to data sources

- **Reusable Component Patterns**:
  - `DataTable` - For displaying tabular data with sorting, filtering
  - `StatusChip` - For displaying status indicators
  - `ProgressIndicator` - For showing progress/completion
  - Form components with built-in validation

- **UI Components are Stateless**:
  - Data flows through props
  - Event handlers defined at container level
  - Material UI theming applied consistently

### 13. **Form Handling & Validation**

- React Hook Form for form state management
- Yup/Zod schema validation
- Consistent error display patterns
- Custom form field components with built-in validation support

### 14. **Routing Strategy**

- React Router v7 with `v7_startTransition` future flag enabled
- Centralized route configuration in `routes` directory
- Route-based code splitting for performance optimization
- ProtectedRoute component for authentication checks
- RoleBasedRoute for authorization control

### 15. **Error Handling Strategy**

- Global error boundary catches unhandled exceptions
- API error handling standardized across services
- User-friendly error messages through notification system
- Fallback UI for failed component rendering
- Consistent loading state presentation

### 16. **Testing Architecture**

- **Unit Testing** (Vitest):
  - Components tested for behavior not implementation
  - Hooks tested with custom render utilities
  - Services tested with mocked API responses
  - Store/state management tested for correctness

- **End-to-End Testing** (Playwright):
  - Critical user flows tested across browsers
  - Authentication flows thoroughly covered
  - Course and task interactions tested
  - API mocking when needed for stable tests

- **Test Utilities**:
  - Global mocks in `setupTests.ts`
  - Reusable test helpers
  - Consistent mock data aligned with API schema
  - LocalStorage mocking for authentication tests

### 17. **Performance Optimization**

- **Code Splitting**:
  - Route-based splitting using React.lazy and Suspense
  - Feature-based splitting for large feature sets
  - Dynamic imports for conditional functionality

- **Rendering Optimization**:
  - React.memo for expensive components
  - useMemo and useCallback for referential stability
  - Virtualization for long lists (react-window)

- **Data Loading**:
  - React Query for efficient caching
  - Optimistic updates for immediate feedback
  - Pagination and infinite scrolling where appropriate

### 18. **Accessibility**

- ARIA attributes applied consistently
- Semantic HTML structure
- Keyboard navigation support
- Screen reader compatibility
- Color contrast compliance
- Focus management for modal dialogs

## **Conceptual Ideas & Best Practices**

### **1. Separation of State and UI Logic**

- React components should be as **stateless** as possible and contain no business logic.
- API communication and data processing takes place in **hooks or services** (`hooks/`, `store/`).
- Custom hooks encapsulate complex logic and provide simple interfaces to components.

### **2. Error Handling & Resilience**

- **Axios interceptors** for global error handling and automatic token renewal in `axiosClient.ts`.
- UI feedback through **Snackbar notifications (Material UI)**.
- Fallback components and error boundaries catch and display errors gracefully.
- Comprehensive logging for debugging and monitoring.

### **3. Scalability through Code Splitting**

- **React Lazy Loading & Suspense** for loading modules.
- **Dynamic loading of routes** with `React Router`.
- Feature flags for progressive feature rollout.
- Microfrontend architecture considerations for future growth.

### **4. Performance Optimization**

- Memoization with `React.memo()` and `useMemo()` to avoid unnecessary re-renders.
- Optimization of API calls with **React Query**.
- **Code splitting and lazy loading for routes** implementation.
- **Strategy for caching API responses** with React Query's caching capabilities.
- Bundle analysis and optimization for production builds.

### **5. Security & Authentication**

- **JWT handling** with local storage and secure practices.
- Access restrictions with **React Context for Auth** and middleware in routes.
- CSRF protection measures.
- Content Security Policy implementation.
- Regular security audits and dependency updates.

### **6. Testing Strategy**

- **Unit tests for components and hooks** using Vitest and Testing Library.
- **Integration tests** for component interaction.
- **End-to-end tests** with Playwright for critical user journeys.
- Mock service worker for API mocking in tests.
- Test coverage monitoring and thresholds.

### **7. Comprehensive Error Handling**

- **Global error handling** for API requests.
- **User-friendly error messages** and fallback UI.
- Contextual errors with actionable feedback.
- Offline support and connection recovery.
- Error tracking and reporting to monitoring systems.

### **8. Build and Deployment**

- **CI/CD pipeline** for automated testing and deployment.
- **Environment-specific builds** with environment variables.
- Progressive deployment strategy.
- Feature flags for controlled feature rollout.
- Performance monitoring in production.

### **9. Documentation**

- **Component documentation** with Props interfaces.
- **API usage guidelines** and examples.
- **State management patterns** documented.
- **Development workflows** documented in README.
- **Architecture diagrams** for visual representation of system design.

## Consequences

- The feature-based organization allows for easier feature development and maintenance.
- Strict typing with TypeScript improves code quality and developer experience.
- The separation of client state (Zustand) and server state (React Query) leads to clearer state management.
- The centralized API layer provides consistency and simplifies error handling.
- Material UI enables a consistent design system but may require customization for specific needs.
- Testing architecture ensures both component correctness and end-to-end functionality.
- The comprehensive approach to error handling enhances user experience and system resilience.

These architectural decisions aim to create a maintainable, performant, and scalable frontend application for the Learning Platform.
