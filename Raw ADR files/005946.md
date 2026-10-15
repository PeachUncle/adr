# ADR-003: Technology Stack Selection

**Date**: 2025-10-24
**Status**: Accepted
**Author**: Leo (System Architect)
**Reviewed By**: CTO

---

## Context

When creating `antarose-template-nodejs`, we needed to select technologies for:

1. **Frontend Framework**: React ecosystem choice
2. **Backend Framework**: Node.js framework choice
3. **Styling Solution**: CSS approach
4. **Component Library**: UI components
5. **Type Safety**: JavaScript vs TypeScript
6. **Development Tooling**: Linting, formatting, etc.

Each decision impacts:
- Developer experience
- Performance
- Community support
- Learning curve
- Long-term maintenance
- Hiring and team growth

---

## Decision Summary

**Frontend Stack**:
- **Framework**: Next.js 15 (App Router)
- **UI Library**: React 19
- **Styling**: Tailwind CSS 3.4
- **Components**: shadcn/ui (Radix UI + Tailwind)
- **Icons**: Lucide React
- **Language**: TypeScript 5.x

**Backend Stack**:
- **Runtime**: Node.js 20 LTS
- **Framework**: Express 5
- **Security**: Helmet 8
- **CORS**: cors 2.8
- **Compression**: compression 1.8
- **Language**: TypeScript 5.x

**Development Tools**:
- **Linting**: ESLint 9
- **Formatting**: Prettier 3
- **Dev Server (Backend)**: ts-node-dev 2

---

## Frontend Technology Decisions

### 1. Next.js 15 (App Router)

**Decision**: Use Next.js 15 with App Router

#### Alternatives Considered

| Framework | Pros | Cons | Why Not Chosen |
|-----------|------|------|----------------|
| **Next.js 15** | ✅ App Router, ✅ React 19, ✅ SSR/SSG/ISR, ✅ Production-ready | ⚠️ Learning curve | **CHOSEN** |
| Remix | ✅ Nested routing, ✅ Progressive enhancement | ❌ Younger ecosystem, ❌ Smaller community | Smaller community than Next.js |
| SvelteKit | ✅ Fast, ✅ Small bundles | ❌ Smaller ecosystem, ❌ Less hiring pool | React is more widely known |
| Nuxt 3 | ✅ Excellent DX, ✅ Vue ecosystem | ❌ Vue (we chose React) | Different paradigm |
| Vite + React Router | ✅ Flexible, ✅ Fast | ❌ No SSR out of the box, ❌ More setup | Too manual for template |
| Create React App | ✅ Simple | ❌ Deprecated, ❌ No SSR | Officially deprecated |

#### Why Next.js 15?

1. **Industry Standard**:
   - Used by Vercel, Netflix, Twitch, Hulu, TikTok, Nike
   - Largest React framework community
   - Most job postings mention Next.js

2. **App Router Benefits**:
   ```typescript
   // Server Components by default (performance)
   export default function Page() {
     return <div>Rendered on server, fast!</div>
   }

   // Client Components when needed
   'use client'
   export default function Interactive() {
     const [state, setState] = useState(0)
     return <button onClick={() => setState(state + 1)}>{state}</button>
   }
   ```

3. **Multiple Rendering Strategies**:
   - SSG (Static Site Generation): Build-time pre-rendering
   - SSR (Server-Side Rendering): Request-time rendering
   - ISR (Incremental Static Regeneration): Periodic updates
   - CSR (Client-Side Rendering): Traditional SPA

4. **Zero-Config Production Optimizations**:
   - Automatic code splitting
   - Image optimization
   - Font optimization
   - Route prefetching

5. **Deployment Flexibility**:
   - Vercel (zero-config)
   - Netlify
   - Cloudflare Pages
   - Self-hosted Docker
   - AWS, GCP, Azure

#### Consequences

**Pros**:
- ✅ Best-in-class developer experience
- ✅ Massive ecosystem (packages, guides, tutorials)
- ✅ Production-ready defaults
- ✅ Easy hiring (many React developers know Next.js)

**Cons**:
- ⚠️ Learning curve for App Router (different from Pages Router)
- ⚠️ Some magic (file-based routing, automatic imports)
- ⚠️ Vercel-optimized (but works elsewhere)

---

### 2. React 19

**Decision**: Use React 19 (latest stable)

#### Why React?

1. **Largest Ecosystem**:
   - 220k+ packages on npm
   - Most Stack Overflow answers
   - Largest hiring pool

2. **Industry Adoption**:
   - Used by Meta, Airbnb, Netflix, Uber
   - ~42% of developers use React (Stack Overflow 2024)

3. **React 19 Features**:
   - Server Components (performance)
   - Improved hooks
   - Automatic batching
   - Better error boundaries

#### Alternatives Considered

| Library | Market Share | Pros | Cons |
|---------|--------------|------|------|
| **React** | ~42% | ✅ Largest ecosystem | ⚠️ Virtual DOM overhead | **CHOSEN** |
| Vue 3 | ~18% | ✅ Great DX, ✅ Simpler | ❌ Smaller ecosystem | Smaller community |
| Svelte | ~5% | ✅ No runtime, ✅ Fast | ❌ Much smaller ecosystem | Too niche for template |
| Angular | ~20% | ✅ Enterprise, ✅ Opinionated | ❌ Heavy, ❌ Steep learning curve | Too heavy |
| Solid | ~2% | ✅ Fast | ❌ Very small community | Too new/experimental |

**Decision Rationale**: React's ecosystem size makes it the safest choice for a general-purpose template.

---

### 3. Tailwind CSS 3.4

**Decision**: Use Tailwind CSS for styling

#### Alternatives Considered

| Approach | Pros | Cons | Why Not Chosen |
|----------|------|------|----------------|
| **Tailwind CSS** | ✅ Fast, ✅ Consistent, ✅ Small bundle | ⚠️ HTML looks cluttered | **CHOSEN** |
| CSS Modules | ✅ Scoped styles | ❌ More boilerplate, ❌ Naming | More manual work |
| Styled Components | ✅ CSS-in-JS, ✅ Dynamic | ❌ Runtime overhead, ❌ Larger bundle | Performance cost |
| Emotion | ✅ Fast CSS-in-JS | ❌ Still runtime overhead | Performance cost |
| Vanilla CSS | ✅ No dependencies | ❌ Naming conflicts, ❌ Hard to maintain | Error-prone |
| CSS-in-TS (Vanilla Extract) | ✅ Type-safe, ✅ Zero runtime | ❌ More complex setup | Too complex for template |

#### Why Tailwind CSS?

1. **Utility-First Benefits**:
   ```tsx
   // Old way (CSS Modules)
   <div className={styles.card}>...</div>
   // styles.module.css: .card { padding: 1rem; border-radius: 0.5rem; ... }

   // Tailwind way
   <div className="p-4 rounded-lg shadow-md">...</div>
   // Clear, concise, no context switching
   ```

2. **Minimal Bundle Size**:
   - Only used classes are included (PurgeCSS)
   - Typical bundle: ~10-20KB (vs 100KB+ for Bootstrap)

3. **Design Consistency**:
   - Predefined spacing scale (4, 8, 16, 24...)
   - Predefined color palette
   - No "magic numbers" in CSS

4. **Perfect for shadcn/ui**:
   - shadcn/ui is built with Tailwind
   - Seamless integration

#### Consequences

**Pros**:
- ✅ Rapid development
- ✅ Consistent design
- ✅ Small bundle size
- ✅ No naming conflicts

**Cons**:
- ⚠️ HTML can look cluttered with many classes
- ⚠️ Learning curve for traditional CSS developers
- ⚠️ Harder to override in some cases

---

### 4. shadcn/ui (Radix UI + Tailwind)

**Decision**: Use shadcn/ui for UI components

#### Alternatives Considered

| Library | Approach | Pros | Cons |
|---------|----------|------|------|
| **shadcn/ui** | Copy-paste | ✅ Full control, ✅ No dependency | ⚠️ Must update manually | **CHOSEN** |
| Material UI | Dependency | ✅ Complete, ✅ Material Design | ❌ Heavy (800KB), ❌ Opinionated style |
| Chakra UI | Dependency | ✅ Great DX, ✅ Accessible | ❌ Runtime overhead, ❌ CSS-in-JS |
| Ant Design | Dependency | ✅ Enterprise-grade | ❌ Not Tailwind-based, ❌ Heavy |
| Radix UI | Headless | ✅ Accessible, ✅ Unstyled | ❌ Must style everything manually |
| Headless UI | Headless | ✅ Tailwind Labs official | ❌ Limited components |

#### Why shadcn/ui?

1. **Not a Dependency**:
   ```bash
   # shadcn/ui approach
   npx shadcn-ui@latest add button
   # Copies component code to your project
   # You own the code!

   # Traditional library approach
   npm install some-ui-library
   # External dependency
   # Can't easily customize
   ```

2. **Full Customization**:
   ```typescript
   // components/ui/button.tsx
   // This is YOUR code, modify as needed
   export function Button({ className, ...props }) {
     return <button className={cn("...", className)} {...props} />
   }
   ```

3. **Built on Radix UI**:
   - Accessibility primitives (WAI-ARIA)
   - Keyboard navigation
   - Focus management
   - Screen reader support

4. **Styled with Tailwind**:
   - Consistent with rest of app
   - Easy to customize
   - No CSS-in-JS overhead

#### Consequences

**Pros**:
- ✅ Full control over component code
- ✅ No runtime dependency
- ✅ Can modify without worrying about updates
- ✅ Accessible by default (Radix UI)

**Cons**:
- ⚠️ Must manually update components (no `npm update`)
- ⚠️ More initial setup (run `add` command for each component)

---

### 5. Lucide React (Icons)

**Decision**: Use Lucide React for icons

#### Alternatives Considered

| Library | Icons | Bundle Size | Tree-Shakable |
|---------|-------|-------------|---------------|
| **Lucide React** | 1000+ | Small | ✅ | **CHOSEN** |
| Heroicons | 200+ | Small | ✅ | Too few icons |
| React Icons | 20,000+ | Large | ⚠️ (with care) | Too many styles |
| Font Awesome | 1000+ | Large | ❌ | Not tree-shakable |
| Material Icons | 2000+ | Large | ⚠️ | Material Design only |

#### Why Lucide React?

1. **shadcn/ui Default**:
   - Designed to work together
   - Consistent style

2. **Tree-Shakable**:
   ```typescript
   // Only bundles imported icons
   import { Home, User, Settings } from 'lucide-react'
   // Result: ~3KB (vs 500KB for Font Awesome)
   ```

3. **Consistent Design**:
   - All icons match in style
   - Modern, clean look

---

## Backend Technology Decisions

### 1. Express 5

**Decision**: Use Express 5 for backend framework

#### Alternatives Considered

| Framework | Philosophy | Pros | Cons |
|-----------|-----------|------|------|
| **Express 5** | Minimalist | ✅ Simple, ✅ Huge ecosystem | ⚠️ Less opinionated | **CHOSEN** |
| Fastify | Performance | ✅ Fast, ✅ TypeScript-first | ❌ Smaller ecosystem | Smaller community |
| Hapi | Enterprise | ✅ Opinionated, ✅ Plugins | ❌ Less flexible | Too opinionated for template |
| Koa | Minimalist | ✅ Modern, ✅ Async/await | ❌ More setup needed | More manual than Express |
| NestJS | Enterprise | ✅ Angular-like, ✅ TypeScript | ❌ Heavy, ❌ Steep learning curve | Too complex for minimal template |

#### Why Express 5?

1. **Industry Standard**:
   - 64 million downloads/week (npm)
   - Used by IBM, Uber, Accenture
   - Most Node.js tutorials use Express

2. **Simple and Flexible**:
   ```typescript
   // Classic simplicity
   app.get('/api/hello', (req, res) => {
     res.json({ message: 'Hello!' })
   })
   ```

3. **Express 5 Improvements**:
   - Better async error handling
   - Promises support
   - Route parameters improvements

4. **Massive Ecosystem**:
   - 10,000+ middleware packages
   - Every problem has a solution
   - Extensive documentation

#### Consequences

**Pros**:
- ✅ Easy to learn
- ✅ Flexible (not opinionated)
- ✅ Huge ecosystem
- ✅ Easy hiring (everyone knows Express)

**Cons**:
- ⚠️ Less opinionated (more decisions to make)
- ⚠️ Slightly slower than Fastify

---

### 2. Security Stack (Helmet + CORS + Compression)

**Decision**: Use standard middleware for security and performance

#### Why These Middlewares?

**Helmet** (Security Headers):
```typescript
app.use(helmet())
// Sets:
// - Content-Security-Policy
// - X-Content-Type-Options: nosniff
// - X-Frame-Options: DENY
// - Strict-Transport-Security
// ... and more
```

**CORS** (Cross-Origin):
```typescript
app.use(cors({ origin: 'http://localhost:3000', credentials: true }))
// Required for frontend-backend communication
```

**Compression** (Response Compression):
```typescript
app.use(compression())
// Reduces response size by ~70-90%
```

**Why These?**:
1. Industry standard (millions of downloads)
2. Battle-tested (used in production by thousands of companies)
3. Simple APIs (just `app.use()`)
4. No configuration needed (sensible defaults)

---

## Cross-Stack Decisions

### 1. TypeScript 5.x

**Decision**: Use TypeScript everywhere

#### JavaScript vs TypeScript

| Aspect | JavaScript | TypeScript |
|--------|------------|------------|
| Type Safety | ❌ Runtime errors | ✅ Compile-time errors |
| IDE Support | ⚠️ Basic | ✅ Excellent (autocomplete, refactoring) |
| Refactoring | ⚠️ Risky | ✅ Safe |
| Learning Curve | ✅ Easy | ⚠️ Moderate |
| Ecosystem | ✅ Universal | ✅ Growing rapidly |

#### Why TypeScript?

1. **Catch Errors Early**:
   ```typescript
   // TypeScript catches this
   function add(a: number, b: number) {
     return a + b
   }
   add("hello", "world") // ❌ Compile error

   // JavaScript doesn't
   function add(a, b) {
     return a + b
   }
   add("hello", "world") // ✅ Returns "helloworld" (bug!)
   ```

2. **Better IDE Experience**:
   - Autocomplete shows available methods
   - Inline documentation
   - Safe refactoring (rename, move)

3. **Industry Trend**:
   - ~80% of new projects use TypeScript
   - All major frameworks support it
   - Easier hiring (developers expect TypeScript)

4. **Next.js and Express Integration**:
   - Both have excellent TypeScript support
   - Type definitions available
   - First-class experience

#### Consequences

**Pros**:
- ✅ Fewer runtime errors
- ✅ Better developer experience
- ✅ Easier refactoring
- ✅ Self-documenting code (types as documentation)

**Cons**:
- ⚠️ Steeper learning curve for beginners
- ⚠️ Compilation step required
- ⚠️ Sometimes verbose

---

### 2. ESLint + Prettier

**Decision**: Use ESLint for linting, Prettier for formatting

#### Why Both?

**ESLint**: Catches bugs
```typescript
// ESLint catches
const user = getUser()
console.log(user.name) // ⚠️ user might be null
```

**Prettier**: Formats code
```typescript
// Before Prettier
function hello(  name:string  ){return`Hello ${name}`}

// After Prettier
function hello(name: string) {
  return `Hello ${name}`
}
```

**Separate Concerns**:
- ESLint = Code quality
- Prettier = Code style

---

## Rejected Alternatives

### What We Explicitly Avoided

1. **Webpack** (vs Vite/Next.js built-in)
   - Reason: Too complex to configure, Next.js handles it

2. **Class-based React Components**
   - Reason: Function components are modern standard

3. **Redux** (vs Zustand/TanStack Query)
   - Reason: Too much boilerplate for minimal template

4. **GraphQL** (vs REST)
   - Reason: REST is simpler for learning

5. **Monorepo Tools** (Turborepo, Nx)
   - Reason: Too complex for minimal template (see ADR-001)

6. **CSS-in-JS** (Styled Components, Emotion)
   - Reason: Runtime overhead, Tailwind is faster

---

## Technology Maturity Matrix

| Technology | Maturity | Community | Job Market | Decision |
|------------|----------|-----------|------------|----------|
| Next.js | Mature | Large | High | ✅ Safe |
| React | Very Mature | Very Large | Very High | ✅ Safe |
| TypeScript | Mature | Large | High | ✅ Safe |
| Tailwind | Mature | Large | Growing | ✅ Safe |
| Express | Very Mature | Very Large | Very High | ✅ Safe |
| shadcn/ui | Growing | Medium | Medium | ✅ Good |
| Lucide React | Growing | Medium | Low | ✅ Acceptable |

**Risk Level**: **Low** - All technologies are production-proven

---

## Future Technology Considerations

### Technologies to Watch

1. **Bun** (JavaScript runtime)
   - Status: Growing
   - When: When it reaches LTS stability
   - Impact: Replace Node.js

2. **Remix** (React framework)
   - Status: Acquired by Shopify
   - When: If it surpasses Next.js in adoption
   - Impact: Replace Next.js

3. **Biome** (Linter + Formatter)
   - Status: Growing
   - When: When it reaches feature parity with ESLint + Prettier
   - Impact: Replace ESLint + Prettier

4. **React Server Components**
   - Status: Stable in Next.js 15
   - When: Now (already using)
   - Impact: Already using via Next.js

---

## Decision Validation Metrics

We'll measure if our technology choices were correct:

1. **Community Engagement**:
   - GitHub stars on template
   - Issue/PR activity
   - Community feedback

2. **Maintenance Burden**:
   - Dependency update frequency
   - Breaking changes per year
   - Time spent on maintenance

3. **User Satisfaction**:
   - Setup time (target: <5 minutes)
   - Developer survey (if 100+ users)

**Review Schedule**: Every 6 months or when major version releases

---

## Lessons Learned (Proactive)

1. **Prefer Mature over Cutting-Edge**:
   - Next.js 15 > Next.js 14 Canary
   - React 19 Stable > React 18 Beta features
   - Node.js 20 LTS > Node.js 21 Current

2. **Prefer Standards over Frameworks**:
   - REST > GraphQL (for this template)
   - TypeScript > JavaScript
   - Standard middleware > Custom solutions

3. **Prefer Simple over Powerful**:
   - Express > NestJS
   - Tailwind > CSS-in-JS
   - Minimal dependencies > Full-featured

---

## Conclusion

Our technology stack balances:

- **Popularity**: All technologies are widely adopted
- **Stability**: Mature, production-proven choices
- **Simplicity**: Easy to learn and understand
- **Performance**: Fast by default
- **Extensibility**: Easy to add features later

**Risk Assessment**: **Low**
- All technologies are battle-tested
- Large communities ensure long-term support
- Industry-standard choices make hiring easier

---

## References

- [State of JS 2023](https://stateofjs.com/)
- [Stack Overflow Developer Survey 2024](https://survey.stackoverflow.co/)
- [npm Trends](https://npmtrends.com/)
- [Next.js vs Remix Comparison](https://remix.run/blog/remix-vs-next)
- [Express vs Fastify Benchmark](https://github.com/fastify/benchmarks)
- [Tailwind CSS Performance](https://tailwindcss.com/docs/optimizing-for-production)

---

**Status**: Accepted
**Last Updated**: 2025-10-24
**Author**: Leo (System Architect)
**Approved By**: CTO (Pending)
