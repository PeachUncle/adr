# ADR-004: Use React.js with Vite for Frontend

## Status
Accepted

## Date
2025-12-19

## Context

We need to build a modern, responsive frontend for Smart Health Synchronizer that can:
- Provide separate interfaces for doctors and patients
- Display health data and visualizations
- Handle real-time updates
- Integrate with backend REST API
- Provide excellent user experience
- Support mobile and desktop devices

### Requirements
- Component-based architecture
- Fast development and build times
- Active community and ecosystem
- Good state management
- Easy API integration
- Modern tooling

### Options Considered

**Option 1: React.js with Vite**
- Most popular library (used by Facebook, Netflix, Airbnb)
- Component-based architecture
- Large ecosystem
- Vite for fast builds
- Virtual DOM for performance

**Option 2: Vue.js**
- Easier learning curve
- Good documentation
- Smaller ecosystem than React
- Less industry demand

**Option 3: Angular**
- Full framework (opinionated)
- TypeScript by default
- Steeper learning curve
- Enterprise-focused

**Option 4: Next.js (React framework)**
- Built on React
- Server-side rendering
- More complex than needed
- Overkill for our SPA

## Decision

We will use **React.js 18+ with Vite** for the frontend.

## Rationale

### Why React.js?

1. **Industry Standard**
   - Most popular frontend library
   - Used by 40% of developers worldwide
   - High job market demand
   - Extensive learning resources

2. **Component-Based Architecture**
   - Reusable UI components
   - Easy to maintain and test
   - Clear separation of concerns
   - Modular development

3. **Rich Ecosystem**
   - React Router for navigation
   - React Query for API state
   - Material-UI / Tailwind CSS for styling
   - React Hook Form for forms
   - Extensive third-party libraries

4. **Performance**
   - Virtual DOM for efficient updates
   - React 18 concurrent features
   - Code splitting and lazy loading
   - Optimized rendering

5. **Developer Experience**
   - React DevTools for debugging
   - Hot Module Replacement (HMR)
   - Excellent documentation
   - Strong community support

### Why Vite?

1. **Lightning Fast**
   - Instant server start
   - Fast Hot Module Replacement
   - Optimized production builds
   - ESBuild for bundling

2. **Modern Tooling**
   - Native ES modules
   - Built-in TypeScript support
   - Out-of-the-box JSX support
   - Environment variables

3. **Better than Create React App**
   - 10-100x faster build times
   - Smaller bundle sizes
   - Modern by default
   - Better developer experience

4. **Production Ready**
   - Used by Vue, Svelte communities
   - Rollup for production builds
   - Tree shaking
   - Asset optimization

## Consequences

### Positive

✅ **Rapid Development**
- Component reusability
- Large component libraries available
- Fast build times with Vite
- Hot reload for instant feedback

✅ **Performance**
- Virtual DOM efficiency
- Code splitting support
- Lazy loading components
- Small bundle sizes with Vite

✅ **Developer Experience**
- Excellent debugging tools
- Strong typing with PropTypes/TypeScript
- Large community for help
- Abundant learning resources

✅ **Ecosystem**
- React Router for routing
- React Query for server state
- Material-UI / Tailwind for UI
- React Hook Form for forms
- Chart libraries for visualizations

✅ **Career Value**
- Most in-demand frontend skill
- Transferable knowledge
- Industry standard
- High job market value

✅ **Mobile Support**
- Responsive design support
- React Native for future mobile apps
- Progressive Web App capabilities

### Negative

❌ **Learning Curve**
- Hooks concept takes time to master
- State management can be complex
- Mitigation: We have learning roadmap

❌ **Decision Fatigue**
- Many ways to do the same thing
- Need to choose libraries carefully
- Mitigation: We define our stack clearly

❌ **Frequent Updates**
- React ecosystem evolves quickly
- Need to keep up with changes
- Mitigation: Stick to stable versions

❌ **SEO Challenges**
- Client-side rendering affects SEO
- Mitigation: Not critical for our app (authenticated users)

## Implementation Details

### Project Structure
```
frontend/
├── src/
│   ├── components/      # Reusable components
│   │   ├── common/      # Buttons, inputs, etc.
│   │   ├── layout/      # Header, sidebar, footer
│   │   └── forms/       # Form components
│   ├── pages/           # Page components
│   │   ├── auth/        # Login, register
│   │   ├── doctor/      # Doctor dashboard
│   │   ├── patient/     # Patient dashboard
│   │   └── blogs/       # Blog pages
│   ├── hooks/           # Custom React hooks
│   ├── contexts/        # React Context providers
│   ├── services/        # API service layer
│   ├── utils/           # Utility functions
│   └── styles/          # Global styles
```

### Key Dependencies
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "@tanstack/react-query": "^5.0.0",
    "axios": "^1.6.0",
    "react-hook-form": "^7.48.0",
    "tailwindcss": "^3.3.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.0",
    "vite": "^5.0.0",
    "eslint": "^8.55.0",
    "prettier": "^3.1.0"
  }
}
```

### Technology Stack

**Build Tool:**
- Vite 5.x - Fast, modern build tool

**Routing:**
- React Router v6 - Client-side routing

**State Management:**
- React Query - Server state
- Context API - Global state
- Local state with useState/useReducer

**Styling:**
- Tailwind CSS - Utility-first CSS framework
- CSS Modules - Component-scoped styles

**Forms:**
- React Hook Form - Performant form handling
- Yup/Zod - Validation schemas

**HTTP Client:**
- Axios - Promise-based HTTP client
- Interceptors for auth tokens

**Testing:**
- Vitest - Fast unit testing
- React Testing Library - Component testing

## Architecture Patterns

### Component Pattern
```jsx
// Functional components with hooks
function UserProfile({ user }) {
  const [isEditing, setIsEditing] = useState(false);
  
  return (
    <div className="user-profile">
      <h2>{user.name}</h2>
      {/* Component JSX */}
    </div>
  );
}
```

### API Integration Pattern
```javascript
// services/authService.js
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL;

export const authService = {
  login: async (credentials) => {
    const response = await axios.post(`${API_URL}/auth/login/`, credentials);
    return response.data;
  }
};
```

### State Management
- **Local State**: useState, useReducer
- **Global State**: Context API for auth, theme
- **Server State**: React Query for API data
- **Form State**: React Hook Form

## Alternatives for Specific Features

- **UI Framework**: Tailwind CSS (utility-first)
- **State Management**: React Query + Context API
- **Forms**: React Hook Form (performance)
- **Routing**: React Router v6 (standard)
- **HTTP**: Axios (interceptors for auth)

## Review Date

This decision will be reviewed at the end of Sprint 3 (6 weeks) to ensure it meets our needs.

## References

- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [React Router](https://reactrouter.com/)
- [React Query](https://tanstack.com/query/)
- [Tailwind CSS](https://tailwindcss.com/)

## Notes

- React + Vite provides the best developer experience
- Tailwind CSS for rapid UI development
- React Query simplifies API state management
- Perfect for learning modern frontend development
- Industry-standard stack with high job market value
- Vite makes development enjoyable with instant feedback
