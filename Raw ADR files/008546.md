# ADR-006: Frontend Technology Stack and Framework Selection

**Date**: 2025-12-31  
**Status**: Proposed  
**Decision Makers**: Architecture Team, Frontend Team  
**Technical Story**: CV Checker Phase 2 - Web Frontend Implementation  
**Supersedes**: None  
**Related Documents**: [Frontend FRD](../features/frontend-ag-ui.md), [Technical Review](../reviews/technical-review-2025-12-31.md), [Backend ADR-005](./ADR-005-fastapi-backend-architecture.md)

---

## Context

CV Checker Phase 2 requires a web-based frontend to enable user interaction with the backend analysis service built in Phase 1. The frontend must support:

### Business Requirements
- **User Workflow**: Upload CV (Markdown) + paste job description → analyze → view results and recommendations
- **Analysis History**: View and retrieve past analyses (stored in browser localStorage)
- **Responsive Design**: Mobile (320px+), tablet (768px+), and desktop (1024px+) support
- **Accessibility**: WCAG 2.1 AA compliance for keyboard navigation, screen readers, and color contrast
- **Performance**: First Contentful Paint <1.5s, Time to Interactive <3s
- **Deployment**: Azure Static Web Apps (free tier, automatic HTTPS, global CDN)

### Technical Requirements
- **API Integration**: Single RESTful endpoint `POST /api/v1/analyze` (FastAPI backend)
- **Type Safety**: Auto-generate TypeScript types from OpenAPI specification
- **State Management**: CV content, job description, analysis results, and history (localStorage-backed)
- **File Handling**: Client-side validation for Markdown files (2MB max)
- **Error Handling**: User-friendly messages for network/API/validation errors
- **Security**: Input sanitization, CSP headers, no XSS vulnerabilities
- **Monitoring**: Application Insights integration for telemetry and errors

### Critical Blocker from Technical Review
The PRD originally specified **AG-UI framework** for the frontend, but the Developer Lead raised this as a **BLOCKER** with the following concerns:

> **⚠️ CRITICAL:** AG-UI framework availability and documentation must be verified before Phase 2 kickoff.
> - **If AG-UI not available:** Fall back to **Fluent UI 2** (Microsoft design system) or **React + Radix UI**
> - **Action Item:** Product/Engineering to confirm AG-UI readiness by Week 6

This ADR resolves that blocker by researching AG-UI and evaluating alternative technology stacks.

---

## Decision Options Evaluated

### Option 1: AG-UI Protocol + CopilotKit (React)

#### Overview
AG-UI is a **protocol**, not a UI component library. It defines a standardized event-driven communication pattern between AI agents and frontend applications.

**Key Findings from Research:**
- **AG-UI Documentation**: Official Microsoft Learn documentation exists ([AG-UI Integration with Agent Framework](https://learn.microsoft.com/en-us/agent-framework/integrations/ag-ui/))
- **What AG-UI Provides**:
  - Server-Sent Events (SSE) for real-time streaming
  - Thread management for conversation context
  - Human-in-the-loop approval workflows
  - State synchronization between client and server
  - Generative UI capabilities
- **What AG-UI Does NOT Provide**:
  - UI component library (buttons, forms, cards)
  - State management library
  - Build tooling or scaffolding
  - File upload components
  - Visualization libraries (charts, gauges)

**CopilotKit Integration:**
- [CopilotKit](https://copilotkit.ai/) provides React UI components that implement the AG-UI protocol
- Components: Streaming chat interface, tool rendering, approval dialogs, state management
- Example: [AG-UI Dojo](https://dojo.ag-ui.com/microsoft-agent-framework-dotnet) demo application

#### Assessment for CV Checker

**Pros:**
- ✅ Official Microsoft protocol with active development and documentation
- ✅ Excellent fit for **agentic, conversational UIs** with streaming responses
- ✅ CopilotKit provides React components that work out-of-the-box
- ✅ Future-proof: If CV Checker adds conversational features (Phase 3+), AG-UI is ideal
- ✅ Supports backend streaming (Phase 1 backend is synchronous, but could evolve)

**Cons:**
- ❌ **Overkill for CV Checker MVP**: CV Checker uses a **single stateless API call**, not streaming chat
- ❌ **No form/upload components**: Need to build or integrate separate UI library for CV upload, job textarea, results visualization
- ❌ **Learning curve**: Team must learn AG-UI protocol + CopilotKit API + separate UI library
- ❌ **Additional complexity**: AG-UI server endpoint required (FastAPI integration exists, but adds setup time)
- ❌ **Unnecessary features**: Thread management, approval workflows, generative UI not needed for Phase 2

**Recommendation:**
- **Not recommended for Phase 2 MVP**
- **Reconsider for Phase 3** if conversational/streaming features are added (e.g., "Chat with your CV results", "Ask questions about recommendations")

---

### Option 2: Fluent UI 2 (React) - @fluentui/react-components

#### Overview
Fluent UI 2 (v9) is Microsoft's official design system and React component library, successor to Office UI Fabric React.

**Key Features:**
- **Component Library**: 80+ production-ready components (Button, Input, Card, Dialog, Spinner, Tooltip, etc.)
- **Design System**: Consistent theming, spacing, typography aligned with Microsoft 365
- **Accessibility**: WCAG 2.1 AAA built-in (keyboard nav, ARIA labels, screen reader support)
- **Performance**: Tree-shakable, lightweight bundles (v9 is ~40% smaller than v8)
- **TypeScript First**: Full type safety and IntelliSense support
- **Customization**: CSS-in-JS styling, design tokens for theming
- **React 18+**: Modern React features (Hooks, Suspense, Concurrent Rendering)

**Documentation:**
- Official docs: [https://react.fluentui.dev/](https://react.fluentui.dev/)
- Storybook: [https://storybooks.fluentui.dev/react/](https://storybooks.fluentui.dev/react/)
- GitHub: [microsoft/fluentui](https://github.com/microsoft/fluentui)
- 6,048 code snippets available (Context7 high reputation)

#### Assessment for CV Checker

**Pros:**
- ✅ **Microsoft ecosystem alignment**: Perfect fit for Azure-hosted application using Microsoft Agent Framework backend
- ✅ **Component coverage**: All UI needs covered (forms, buttons, cards, spinners, tooltips, progress bars)
- ✅ **Accessibility built-in**: WCAG 2.1 AA/AAA compliance out-of-the-box
- ✅ **Performance**: Optimized for production, meets <1.5s FCP target
- ✅ **Mature and stable**: Used in Microsoft 365, Teams, SharePoint (proven at scale)
- ✅ **Excellent documentation**: Comprehensive guides, Storybook examples, active community
- ✅ **TypeScript native**: Full type safety reduces runtime errors
- ✅ **Responsive design**: Components support mobile, tablet, desktop out-of-the-box
- ✅ **Low learning curve**: Standard React patterns, familiar to most React developers
- ✅ **Future-proof**: Active development, long-term Microsoft support

**Cons:**
- ⚠️ **No chart/visualization library**: Need to integrate separate library for score gauge/progress bars (e.g., Recharts, Victory, or custom SVG)
- ⚠️ **Less opinionated**: No built-in state management or routing (developer choice)
- ⚠️ **Large bundle**: ~300KB minified (acceptable with code splitting)

**Recommended Stack:**
```
Frontend Framework: React 18
UI Components:      @fluentui/react-components (Fluent UI v9)
Build Tool:         Vite (fast HMR, optimized builds)
State Management:   Zustand or React Context API (lightweight)
Routing:            None (single-page application)
API Client:         openapi-typescript-codegen (auto-generated from backend)
Visualization:      Recharts (charts) + custom SVG (score gauge)
Testing:            Vitest + Testing Library + Playwright
Deployment:         Azure Static Web Apps
```

**Recommendation:**
- **RECOMMENDED for Phase 2 MVP**
- Best balance of functionality, performance, and Microsoft ecosystem alignment
- Fastest path to production (4-week timeline achievable)

---

### Option 3: Next.js + Fluent UI 2

#### Overview
Next.js is a React meta-framework with SSR, SSG, routing, and build optimizations. Combined with Fluent UI 2 for components.

**Key Features:**
- **File-based Routing**: Automatic route generation from folder structure
- **Performance**: Image optimization, automatic code splitting, bundle analysis
- **SEO**: Server-side rendering (SSR) and static site generation (SSG)
- **Developer Experience**: Fast Refresh, TypeScript support, ESLint integration
- **Deployment**: First-class Vercel support, Azure Static Web Apps compatible

#### Assessment for CV Checker

**Pros:**
- ✅ **Future-proof**: If CV Checker adds multi-page features (user dashboard, settings, documentation)
- ✅ **SEO-friendly**: If marketing/landing pages needed
- ✅ **Performance**: Superior initial load times with SSR/SSG
- ✅ **Developer experience**: Hot reload, built-in routing, optimized builds

**Cons:**
- ❌ **Overkill for MVP**: CV Checker is a **single-page application** (no routing needed)
- ❌ **Complexity overhead**: SSR/SSG configuration, API routes (not needed)
- ❌ **Longer setup time**: ~1-2 extra days vs. Vite for equivalent features
- ❌ **Azure Static Web Apps caveats**: Next.js SSR requires Azure Functions backend (added complexity)

**Recommendation:**
- **Not recommended for Phase 2 MVP**
- **Reconsider for Phase 3** if multi-page features are added (user accounts, dashboard, documentation pages)

---

### Option 4: React + Radix UI + Tailwind CSS

#### Overview
Radix UI provides unstyled, accessible React primitives. Tailwind CSS for utility-first styling.

**Key Features:**
- **Radix UI**: Headless components (Dialog, Dropdown, Tooltip, etc.) with full accessibility
- **Tailwind CSS**: Utility-first CSS framework for rapid styling
- **Flexibility**: Complete control over design system
- **Bundle Size**: Minimal JavaScript (Radix is headless, Tailwind is CSS-only)

#### Assessment for CV Checker

**Pros:**
- ✅ **Lightweight**: Smallest bundle size of all options
- ✅ **Accessibility**: Radix UI has excellent WCAG 2.1 support
- ✅ **Customization**: Full design control (if custom brand needed)

**Cons:**
- ❌ **More work**: Must style every component from scratch
- ❌ **Inconsistent with Microsoft ecosystem**: Doesn't match Azure/Microsoft 365 design
- ❌ **No pre-built forms**: Must build CV upload, job textarea, results cards manually
- ❌ **Longer timeline**: ~1-2 extra weeks to build and style components
- ❌ **Less polished**: Harder to achieve Microsoft-quality UX without design expertise

**Recommendation:**
- **Not recommended for Phase 2 MVP**
- **Consider for Phase 3** if custom branding/white-labeling is required

---

## Decision

**We will use Fluent UI 2 (@fluentui/react-components) with React and Vite for the Phase 2 frontend.**

### Rationale

1. **Microsoft Ecosystem Alignment**: Fluent UI 2 is Microsoft's official design system, providing a cohesive experience across Azure and Microsoft 365 products.

2. **Component Coverage**: All required UI elements are available out-of-the-box:
   - Forms: `Input`, `Textarea`, `Button`, `Label`
   - Uploads: `Button` + `input[type="file"]` with custom styling
   - Results: `Card`, `ProgressBar`, `Badge`, `Tooltip`
   - Feedback: `Spinner`, `MessageBar`, `Dialog`
   - Layout: `Stack`, `Grid` (via CSS Grid)

3. **Accessibility Built-In**: WCAG 2.1 AA/AAA compliance is automatic, reducing accessibility testing burden.

4. **Performance**: Meets all performance requirements (<1.5s FCP, <3s TTI) with proper code splitting.

5. **Timeline Achievable**: 4-week Phase 2 timeline is realistic with pre-built, documented components.

6. **Developer Experience**: Familiar React patterns, excellent TypeScript support, comprehensive Storybook documentation.

7. **Future-Proof**: Active development by Microsoft, long-term support guaranteed, easy migration path if features expand.

8. **AG-UI Compatibility**: If streaming/conversational features are added in Phase 3, Fluent UI 2 components can be used alongside AG-UI protocol (not mutually exclusive).

---

## Additional Architectural Decisions

### State Management: Zustand

**Decision**: Use [Zustand](https://github.com/pmndrs/zustand) for global state management.

**Rationale:**
- Lightweight (~1KB minified)
- TypeScript-first with full type inference
- No boilerplate (simpler than Redux or Context API)
- Perfect for CV Checker's state needs:
  - Current CV (file, content)
  - Current job description
  - Current analysis (loading, result, error)
  - Analysis history (array of past results)
- Easy localStorage persistence with `persist` middleware

**Alternative Considered:** React Context API (acceptable, but Zustand provides better DevTools and performance)

---

### Routing: None (Single-Page Application)

**Decision**: No routing library for Phase 2. Use conditional rendering for views.

**Rationale:**
- CV Checker MVP is a single-page workflow: Upload → Analyze → Results
- Analysis history is a modal or slide-out panel (not a separate page)
- Adding React Router or Next.js routing is unnecessary complexity
- If multi-page navigation is needed in Phase 3, add React Router at that time

---

### Build Tool: Vite

**Decision**: Use [Vite](https://vitejs.dev/) for development and production builds.

**Rationale:**
- **Fast HMR**: <50ms hot module replacement (vs. 1-2s with Webpack)
- **Optimized Production Builds**: Rollup-based bundling with tree-shaking
- **TypeScript Native**: No additional configuration needed
- **React 18 Support**: Fast Refresh, Suspense, Concurrent Rendering
- **Azure Static Web Apps Compatible**: Standard static file output (`dist/`)
- **Developer Experience**: Minimal configuration, fast startup (<1s)

**Alternative Considered:** Create React App (deprecated, slower builds)

---

### API Client Generation: openapi-typescript-codegen

**Decision**: Auto-generate TypeScript API client from backend OpenAPI spec using `openapi-typescript-codegen`.

**Rationale:**
- **Type Safety**: Frontend and backend schemas stay in sync automatically
- **Reduced Errors**: Compile-time errors if API changes
- **Developer Experience**: IntelliSense for API calls
- **Maintenance**: No manual typing of request/response models
- **CI/CD Integration**: Regenerate client when backend OpenAPI spec changes

**Generation Command:**
```bash
npx openapi-typescript-codegen \
  --input http://localhost:8000/api/v1/openapi.json \
  --output ./src/api/generated \
  --client axios
```

**Alternative Considered:** Manual Axios calls (error-prone, no type safety)

---

### Visualization Library: Recharts + Custom SVG

**Decision**: Use [Recharts](https://recharts.org/) for bar charts and custom SVG for the score gauge.

**Rationale:**
- **Recharts**:
  - React-native (declarative API)
  - Accessible (ARIA labels, keyboard nav)
  - Responsive and themeable
  - Small bundle (~50KB minified)
  - Perfect for subscores breakdown (horizontal bar charts)
- **Custom SVG Gauge**:
  - Full design control for overall score (circle gauge)
  - Lightweight (<1KB)
  - Animatable with CSS/JS
  - Accessible with `<title>` and `role="img"`

**Alternatives Considered:**
- Victory (larger bundle, less React-like API)
- Chart.js (imperative, not React-native)
- D3.js (steep learning curve, overkill)

---

### Deployment Target: Azure Static Web Apps

**Decision**: Deploy to [Azure Static Web Apps](https://learn.microsoft.com/azure/static-web-apps/).

**Rationale:**
- **Free Tier**: 100GB bandwidth/month, custom domain, automatic HTTPS
- **Global CDN**: Low latency worldwide
- **CI/CD**: GitHub Actions integration out-of-the-box
- **Configuration**: Simple `staticwebapp.config.json` for routing, headers, CORS
- **Preview Deployments**: Automatic staging environments on PRs
- **Integration with Backend**: Can be deployed alongside backend API (future)

**Configuration Example:**
```json
{
  "navigationFallback": {
    "rewrite": "/index.html",
    "exclude": ["/assets/*", "/api/*"]
  },
  "responseOverrides": {
    "404": {
      "rewrite": "/index.html"
    }
  },
  "globalHeaders": {
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline' https://js.monitor.azure.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://<backend-api>.azurewebsites.net https://dc.services.visualstudio.com;"
  }
}
```

---

## Implementation Plan

### Week 7: Project Setup & Core UI
1. **Day 1-2: Scaffolding**
   - Initialize Vite + React + TypeScript project
   - Install Fluent UI 2 (`@fluentui/react-components`)
   - Configure Zustand for state management
   - Set up ESLint + Prettier + Husky pre-commit hooks
   - Generate TypeScript API client from backend OpenAPI spec

2. **Day 3-5: CV Upload & Job Input**
   - Build CV upload component (file picker + drag-and-drop with `Input` + `Button`)
   - Build job description textarea (with character counter)
   - Implement client-side validation (file type, size, content length)
   - Wire up Zustand store for CV and job state
   - Persist state to localStorage

### Week 8: Analysis & Results Visualization
3. **Day 1-2: Analysis Workflow**
   - Build "Analyze Match" button with loading states (`Spinner`)
   - Implement API call with error handling
   - Add timeout handling (60s max)
   - Display success/error messages (`MessageBar`)

4. **Day 3-5: Results Display**
   - Build overall score gauge (custom SVG circle)
   - Build subscores breakdown (Recharts horizontal bars)
   - Build recommendations list (expandable `Card` components with `Badge` for priority)
   - Add tooltips (`Tooltip`) for score explanations
   - Implement filtering/sorting for recommendations

### Week 9: History & Responsive Design
5. **Day 1-2: Analysis History**
   - Build history list view (paginated `Card` list)
   - Implement "View Details" navigation to past analysis
   - Add sort by date/score functionality
   - Persist history to localStorage (max 10 results, 7-day TTL)

6. **Day 3-5: Responsive Design**
   - Test and fix mobile layout (320px-767px)
   - Test and fix tablet layout (768px-1023px)
   - Test and fix desktop layout (1024px+)
   - Ensure touch targets meet 44x44px minimum
   - Test with Chrome DevTools device emulation

### Week 10: Testing, Polish & Deployment
7. **Day 1-2: Testing**
   - Write unit tests (Vitest + Testing Library) for utilities, state, API client
   - Write integration tests for full workflows
   - Run accessibility tests (axe-core) and fix violations
   - Write E2E tests (Playwright) for critical paths

8. **Day 3-4: Polish & Performance**
   - Run Lighthouse CI and optimize (target: Performance >90, A11y >95)
   - Add Application Insights integration
   - Implement error logging and telemetry
   - Test error scenarios (network failure, API timeout, invalid input)
   - Fix any visual bugs or UX issues

9. **Day 5: Deployment**
   - Set up Azure Static Web Apps
   - Configure GitHub Actions CI/CD pipeline
   - Deploy to staging environment
   - Manual QA and smoke testing
   - Deploy to production
   - Monitor error rates and performance

---

## Technology Stack Summary

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Framework** | React 18 | Industry standard, excellent ecosystem, team expertise |
| **UI Library** | Fluent UI 2 (v9) | Microsoft design system, accessibility built-in, component coverage |
| **Build Tool** | Vite | Fast HMR, optimized production builds, TypeScript native |
| **State Management** | Zustand | Lightweight, TypeScript-first, localStorage persistence |
| **Routing** | None (Phase 2) | Single-page app, add React Router in Phase 3 if needed |
| **API Client** | openapi-typescript-codegen | Auto-generated from backend OpenAPI spec, type-safe |
| **Visualization** | Recharts + Custom SVG | Accessible charts, lightweight, React-native API |
| **Testing** | Vitest + Testing Library + Playwright + axe-core | Fast unit tests, component tests, E2E tests, accessibility |
| **Deployment** | Azure Static Web Apps | Free tier, global CDN, GitHub Actions CI/CD |
| **Monitoring** | Azure Application Insights | Telemetry, error tracking, performance monitoring |
| **Styling** | Fluent UI Tokens + CSS Modules | Consistent theming, scoped styles, design tokens |

---

## Consequences

### Positive

1. **Microsoft Ecosystem Consistency**: Fluent UI 2 provides a native Microsoft experience that aligns with Azure portal, Microsoft 365, and Microsoft Agent Framework branding.

2. **Rapid Development**: Pre-built components accelerate development, making the 4-week Phase 2 timeline achievable.

3. **Accessibility Compliance**: WCAG 2.1 AA/AAA compliance is automatic, reducing manual testing and remediation work.

4. **Type Safety**: TypeScript + auto-generated API client + Fluent UI's typed components eliminate entire classes of runtime errors.

5. **Performance**: Vite's fast builds + Fluent UI's tree-shakable components + code splitting meet all performance targets.

6. **Developer Experience**: Excellent documentation, Storybook examples, and active community reduce onboarding time.

7. **Future Flexibility**: If AG-UI is needed in Phase 3 for conversational features, Fluent UI 2 components can coexist with AG-UI protocol.

8. **Long-Term Support**: Microsoft's ongoing investment in Fluent UI ensures long-term viability and updates.

### Negative

1. **Vendor Lock-In (Moderate)**: Fluent UI 2 is Microsoft-specific. Switching to another design system (e.g., Material UI) would require component refactoring.
   - **Mitigation**: Fluent UI is open-source and well-maintained. Microsoft's track record with React libraries is strong. Lock-in risk is acceptable.

2. **No Built-In Charts**: Recharts is a separate dependency for visualizations.
   - **Mitigation**: Recharts is lightweight, well-maintained, and Fluent UI compatible. Total added bundle size: ~50KB.

3. **Learning Curve (Minimal)**: Team must learn Fluent UI 2 API and design tokens.
   - **Mitigation**: Documentation is excellent. Fluent UI 2 follows standard React patterns. Learning curve is <1 day for experienced React developers.

4. **Bundle Size**: Fluent UI 2 adds ~300KB minified to the bundle.
   - **Mitigation**: Code splitting, tree-shaking, and lazy loading reduce initial load. Only components used are bundled. Performance targets are still achievable.

### Risks

1. **Risk: Fluent UI v9 Stability**
   - **Description**: Fluent UI v9 is the latest major version. Some edge cases may have bugs.
   - **Likelihood**: Low (v9 has been stable since 2022, used in production by Microsoft)
   - **Impact**: Medium (workarounds may be needed for edge cases)
   - **Mitigation**: Extensive Storybook testing, GitHub issues for bug reports, fallback to custom components if needed.

2. **Risk: Team Unfamiliarity with Fluent UI**
   - **Description**: Team may not have experience with Fluent UI 2 API.
   - **Likelihood**: Medium (depends on team background)
   - **Impact**: Low (documentation and examples are excellent)
   - **Mitigation**: Allocate 1 day for Fluent UI 2 familiarization (Storybook exploration, tutorial).

3. **Risk: Recharts Accessibility**
   - **Description**: Chart visualizations may not meet WCAG 2.1 AA without customization.
   - **Likelihood**: Medium (Recharts has accessibility support, but requires configuration)
   - **Impact**: Medium (accessibility testing may reveal gaps)
   - **Mitigation**: Use Recharts accessibility features (ARIA labels, keyboard nav), test with screen readers, add data tables as fallback.

---

## Migration Path (If Needed)

### If AG-UI Conversational Features Are Added in Phase 3

1. **Keep Fluent UI 2 for UI Components**: Forms, buttons, cards, etc.
2. **Add AG-UI Protocol for Streaming**: Integrate `@microsoft/fast-react-wrapper` for AG-UI server-sent events
3. **Add CopilotKit for Conversational UI**: `npm install @copilotkit/react-core @copilotkit/react-ui`
4. **Coexist**: Fluent UI 2 (static UI) + CopilotKit (streaming chat) work together
5. **Estimated Effort**: 1-2 weeks to add streaming chat sidebar

### If Multi-Page Features Are Added in Phase 3

1. **Add React Router**: `npm install react-router-dom`
2. **Refactor to Routes**: Convert conditional rendering to `<Route>` components
3. **Update Navigation**: Add Fluent UI `Nav` component for sidebar/header
4. **Estimated Effort**: 2-3 days

### If Custom Branding Is Required

1. **Fluent UI Design Tokens**: Customize theme colors, typography, spacing
2. **OR Switch to Radix UI + Tailwind**: Rebuild components with custom styles
3. **Estimated Effort**: Design tokens (1-2 days), Radix rebuild (2-3 weeks)

---

## References

### Fluent UI 2
- [Fluent UI React Documentation](https://react.fluentui.dev/)
- [Fluent UI Storybook](https://storybooks.fluentui.dev/react/)
- [Fluent UI GitHub](https://github.com/microsoft/fluentui)
- [Fluent UI Design Tokens](https://react.fluentui.dev/?path=/docs/concepts-developer-customizing-themes--page)

### AG-UI Protocol
- [AG-UI Integration with Agent Framework](https://learn.microsoft.com/en-us/agent-framework/integrations/ag-ui/)
- [AG-UI Getting Started (Python)](https://learn.microsoft.com/en-us/agent-framework/integrations/ag-ui/getting-started)
- [AG-UI Dojo Demo](https://dojo.ag-ui.com/microsoft-agent-framework-dotnet)
- [CopilotKit Documentation](https://docs.copilotkit.ai/microsoft-agent-framework)

### Other Technologies
- [Vite Documentation](https://vitejs.dev/)
- [Zustand Documentation](https://github.com/pmndrs/zustand)
- [Recharts Documentation](https://recharts.org/)
- [openapi-typescript-codegen](https://github.com/ferdikoomen/openapi-typescript-codegen)
- [Azure Static Web Apps Documentation](https://learn.microsoft.com/azure/static-web-apps/)

### Related ADRs
- [ADR-001: Microsoft Agent Framework Sequential Orchestration](./ADR-001-microsoft-agent-framework-sequential-orchestration.md)
- [ADR-002: Azure OpenAI Integration with Entra ID](./ADR-002-azure-openai-integration-entra-id.md)
- [ADR-005: FastAPI Backend Architecture](./ADR-005-fastapi-backend-architecture.md)

---

**END OF ADR-006**
