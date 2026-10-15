# Component Library & Design System

* Status: accepted
* Deciders: Platform Team, Frontend Team
* Date: 2025-12-06

## Context and Problem Statement

With the frontend stack chosen (React + Vite + TanStack Router + TanStack Query, client-only), we need a shared component library and design system that can serve multiple applications (e-commerce, POS, admin, merchandising, order management) without introducing a production Node/BFF dependency. The library must be composable, accessible, browser-first, and easy to consume across apps in the Nx monorepo while keeping frontend and backend strictly separated.

## Constraints

- Client-only deployment: static assets; no Node server required at runtime.
- Strict frontend/backend separation; backend concerns stay in Spring services.
- Multiple apps share the same library; avoid app-specific forks.
- React/Vite/TanStack Router/Query baseline; no Redux/NgRx; minimal client global state.
- Nx monorepo: generators/affected analysis should work for components and tokens.
- Browser-first: prefer native capabilities (fetch, Intl, forms) over bespoke shims.

## Guiding Principles (from frontend standards)

- Composable, prop-driven components; presentational parts are logic-free.
- Cross-cutting concerns (auth, telemetry, analytics) live in shared hooks/services, not in UI primitives.
- Accessibility-first defaults (ARIA, focus management, keyboard support).
- Routable surfaces: views/pages must be addressable; components support layout/routing patterns.
- Code sharing across all frontends; avoid divergent theming or styling stacks per app.
- Type safety with TypeScript and generated API types where applicable.
- Performance and DX: fast HMR, small bundles, code-splitting by route/feature.

## Decision Criteria

1. **Design tokens and theming**: CSS variables/theme tokens with light/dark and brand extensibility; no per-app hard forks. Tokens generated/validated via Nx pipelines.
2. **Component model**: Headless or low-opinion primitives that are composition-friendly; avoid tightly coupled “kitchen sink” components. Styling should be swappable (e.g., CSS variables, utility classes).
3. **Accessibility**: Built-in ARIA roles, focus management, keyboard navigation, and form semantics. Must pass axe checks out of the box.
4. **Type safety**: Strict TypeScript types for props, slots, and theming contracts; minimal reliance on `any`.
5. **Cross-app compatibility**: Works for web, POS, and admin surfaces; no runtime that assumes SSR. Must deploy as static assets with Vite builds.
6. **Routing alignment**: Plays well with TanStack Router (or React Router) for layouts, navigation components, and link handling without requiring SSR.
7. **State boundaries**: Components stay presentational; data fetching/mutations live in hooks/services (TanStack Query). No bundled global state managers.
8. **Theming + design consistency**: Single source of truth for typography, spacing, color, and motion tokens; Storybook-like previews for validation.
9. **Performance**: Tree-shakeable, minimal runtime, avoids heavy peer deps. Supports code-splitting and lazy loading where appropriate.
10. **Ecosystem and maintenance**: Actively maintained upstream (if adopting a headless kit) with permissive licensing; strong documentation and community support.
11. **Testing**: Components are testable with RTL + axe; provide fixtures/mocks to make adoption easy across apps.

## Options (to evaluate against criteria)

- Headless primitives (e.g., Radix UI) + custom theming layer (high composability, strong accessibility)
- Utility-first styling (e.g., Tailwind) + headless components (fast styling, consistent tokens via CSS vars)
- Minimal in-house headless primitives + tokens (maximum control, higher maintenance)
- Full UI kits:
  - **MUI** (largest LLM/AI footprint, mature theming, rich components; heavier runtime)
  - **Ant Design** (enterprise-friendly, strong data components; LLM familiarity good but less than MUI)
  - **shadcn/ui (Radix + Tailwind)** (codegen per project, high composability; lighter ecosystem support, per-app sync risk)
  - **Chakra** (simpler theming, smaller ecosystem than MUI/AntD)

## Deep Dive: MUI vs shadcn/ui

Based on research conducted December 2025, these two options represent fundamentally different architectural approaches and warrant detailed comparison.

### Architecture Comparison

| Aspect | MUI | shadcn/ui |
|--------|-----|-----------|
| **Model** | Dependency (npm package) | Ownership (copy source into project) |
| **Styling** | Runtime CSS-in-JS (Emotion) | Static CSS (Tailwind) |
| **Updates** | Central npm updates; potential breaking changes | Manual updates; you control timing |
| **Runtime overhead** | ~25KB gzipped (Emotion + theme) | Zero runtime |
| **Bundle (simple page)** | ~104KB gzipped | ~80KB gzipped |

### How Each Works

**MUI**: Components imported from `node_modules`. Theme provider wraps app and provides design tokens via React context. Every `sx` prop and styled component generates CSS at runtime via Emotion. MUI is developing Pigment CSS (zero-runtime) for v6+, but it's opt-in and still maturing.

**shadcn/ui**: CLI copies component source directly into your project (e.g., `./components/ui/button.tsx`). Two-layer architecture: Radix UI handles behavior/accessibility; Tailwind handles styling. All CSS compiled at build time. You own and modify the code directly.

### Performance Analysis

| Metric | MUI | shadcn/ui |
|--------|-----|-----------|
| **Initial bundle** | ~25KB runtime + components | ~0KB runtime |
| **Render overhead** | CSS generated per render cycle | Zero (static CSS) |
| **Dev server startup** | Slower (barrel imports) | Fast |
| **Tree-shaking** | Requires path imports for optimization | Native |

**MUI Performance Gotchas**:
- `sx` prop generates styles at runtime, impacting INP/LCP metrics
- Icon imports from `@mui/icons-material` can be 6x slower in dev mode
- Nested theme providers compound overhead
- Recommended: Use path imports (`import Button from '@mui/material/Button'`) instead of barrel imports

**shadcn/ui Performance**:
- All styles compiled at build time
- Tailwind JIT compiler includes only used classes
- Radix primitives are individually tree-shakeable

### Customization Approaches

**MUI Theming**:
```tsx
const theme = createTheme({
  components: {
    MuiButton: {
      styleOverrides: {
        root: { borderRadius: '8px', textTransform: 'none' },
      },
    },
  },
});
```
- Centralized and consistent across all instances
- Must learn MUI's override API; some customizations require deep selectors

**shadcn/ui Customization**:
```tsx
// Edit components/ui/button.tsx directly
const buttonVariants = cva("inline-flex items-center...", {
  variants: {
    variant: {
      default: "bg-primary text-primary-foreground",
      brand: "bg-brand-500 text-white hover:bg-brand-600", // Add custom
    },
  },
});
```
- Direct control, no API to learn, edit Tailwind classes directly
- Changes are per-project; no central upgrade path

### Nx Monorepo Considerations

**MUI in Monorepo**:
- Theme config lives in shared lib, apps import it
- No special CLI setup required
- npm updates affect all apps simultaneously

**shadcn/ui in Monorepo**:
- Requires `components.json` in each workspace
- Import path aliases need careful tsconfig setup
- Tailwind config must be shared across packages
- CLI has official monorepo support (creates `packages/ui` structure)

Challenges documented in real implementations:
- Tailwind setup command may fail, requiring manual config
- Namespace changes can break import paths
- Tree-shaking depends on proper ESM/CJS configuration

### Ecosystem & Maintenance

| Factor | MUI | shadcn/ui |
|--------|-----|-----------|
| **Established** | 2014 | 2023 |
| **Weekly downloads** | 3.3M | 200K+ |
| **GitHub stars** | 95K+ | 83K+ |
| **Used by** | Spotify, Amazon, Netflix | Vercel, growing adoption |
| **Enterprise components** | MUI X (DataGrid, DatePicker) - paid tiers | Need third-party alternatives |
| **Backing** | MUI Inc. (company) | Community + WorkOS (via Radix) |

**Radix UI Maintenance Risk**: The original Radix co-creator stated it's a "liability" for serious projects. While WorkOS maintains it, many original maintainers left. Base UI (by same team) is emerging as an alternative with similar API. shadcn/ui's copy-paste model mitigates this risk since you own the code.

### Developer Experience

| Factor | MUI | shadcn/ui |
|--------|-----|-----------|
| **Learning curve** | Steeper (theming API, sx syntax) | Lower if team knows Tailwind |
| **Documentation** | Excellent, comprehensive | Good, but newer/smaller |
| **TypeScript** | Excellent | Excellent |
| **Component count** | 50+ ready-to-use | 40+ (growing) |
| **AI/LLM compatibility** | Good | Excellent (source-level access) |

### Scoring Against Decision Criteria

| Criterion | MUI | shadcn/ui |
|-----------|-----|-----------|
| 1. Design tokens/theming | ✅ Strong (theme provider) | ✅ CSS variables + Tailwind |
| 2. Headless/composable | ⚠️ Opinionated | ✅ Excellent (Radix primitives) |
| 3. Accessibility | ✅ Good | ✅ Excellent (WCAG via Radix) |
| 4. Type safety | ✅ Excellent | ✅ Excellent |
| 5. Static deploy (no SSR) | ✅ Yes | ✅ Yes |
| 6. Routing alignment | ✅ Works with any router | ✅ Works with any router |
| 7. State boundaries | ✅ Components are presentational | ✅ Components are presentational |
| 8. Theming consistency | ✅ Enforced by Material Design | ✅ Enforced by your tokens |
| 9. Performance | ⚠️ Runtime overhead | ✅ Zero runtime |
| 10. Ecosystem/maintenance | ✅ Strong, company-backed | ⚠️ Radix maintenance concerns |
| 11. Testing | ✅ RTL compatible | ✅ RTL compatible |

### Risk Assessment

**MUI Risks**:
- Bundle bloat: Easy to import too much without path imports
- Upgrade pain: v4→v5 migration was difficult for many teams
- Material Design lock-in: Apps look "Material" unless heavily customized
- Runtime performance: CSS-in-JS overhead in performance-critical apps

**shadcn/ui Risks**:
- Radix UI maintenance uncertainty (mitigated by code ownership)
- Manual updates: No `npm update`; must manually sync changes
- Fewer built-in components: No DataGrid equivalent
- Monorepo complexity: More initial setup required

### Recommendation Matrix

| Scenario | Recommendation |
|----------|----------------|
| Data-heavy admin dashboards | MUI (DataGrid alone is worth it) |
| Tight deadlines, no designer | MUI (Material Design = instant UX) |
| Performance-critical consumer app | shadcn/ui |
| Custom brand, unique design | shadcn/ui |
| Team new to frontend | MUI (more guidance) |
| Team knows Tailwind | shadcn/ui |
| AI/LLM to modify components | shadcn/ui (source-level access) |

### Sources

- [MUI Bundle Size Guide](https://mui.com/material-ui/guides/minimizing-bundle-size/)
- [shadcn/ui Monorepo Docs](https://ui.shadcn.com/docs/monorepo)
- [Anatomy of shadcn/ui](https://manupa.dev/blog/anatomy-of-shadcn-ui)
- [Is MUI Overrated? 2025](https://junkangworld.com/blog/is-mui-overrated-the-brutally-honest-truth-for-2025)
- [Radix UI Future Concerns](https://dev.to/mashuktamim/is-your-shadcn-ui-project-at-risk-a-deep-dive-into-radixs-future-45ei)
- [Nx + shadcn/ui Guide](https://medium.com/@sakshijaiswal0310/building-a-scalable-react-monorepo-with-nx-and-shadcn-ui-a-complete-implementation-guide-96c2bb1b42e8)
- [React UI Libraries 2025 Comparison](https://makersden.io/blog/react-ui-libs-2025-comparing-shadcn-radix-mantine-mui-chakra)

## Decision

**Chosen: shadcn/ui + Tailwind CSS**

Given our constraints (Nx monorepo, multiple apps, client-only, browser-first, no forks), shadcn/ui + Tailwind CSS is the accepted solution:

1. **Zero runtime** aligns with browser-first philosophy
2. **Shared `libs/ui` package** provides "no forks" consistency across apps
3. **Better tree-shaking** for multiple smaller apps
4. **AI-friendly architecture** for future tooling integration
5. **Code ownership** mitigates Radix maintenance concerns

**Risk mitigations**:
- Monitor Radix development; if stalled, migrate affected primitives to Base UI (similar API)
- For complex data grids, use TanStack Table or AG Grid as complementary solutions
- Code ownership model means we can fork/modify components if upstream changes

## Consequences

**Positive**:
- Zero runtime overhead improves Core Web Vitals (LCP, INP)
- Full control over component source enables rapid customization
- Tailwind's utility-first approach aligns with team's existing CSS knowledge
- AI/LLM tooling can directly read and modify component source

**Negative**:
- Manual effort required to sync upstream component updates
- No built-in DataGrid; requires TanStack Table integration
- Initial monorepo setup more complex than MUI
- Team members unfamiliar with Tailwind will need onboarding

**Neutral**:
- Radix UI maintenance risk is mitigated by code ownership but should be monitored

## Implementation Plan

- [ ] Set up shared `libs/ui` package in Nx monorepo
- [ ] Configure shadcn/ui CLI with `components.json` for monorepo structure
- [ ] Establish design token pipeline (CSS variables for colors, spacing, typography)
- [ ] Implement initial component set: Button, Input, Modal, Dialog, Select
- [ ] Integrate TanStack Table for data grid requirements
- [ ] Create Storybook for component documentation and visual testing
- [ ] Document component ownership and update procedures
