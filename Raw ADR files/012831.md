# ADR-009: UI Component Library

## Status

Accepted

## Context

We need a UI component library for the Vue 3 admin dashboard to provide:

- Data tables (for inquiries, bookings, performers lists)
- Forms (inquiry creation, booking management)
- Calendar/date pickers (event scheduling)
- Modals, dialogs, toasts (UX patterns)
- Navigation components (menus, tabs)
- Charts (financial reports - future)

This is an **internal admin tool**, not a public-facing website, so:

- Speed of development > perfect aesthetics
- Functionality > trendy design
- Complete component set > customization

## Decision Drivers

- **Completeness**: Has all components we need out of the box
- **Data tables**: Robust table with sorting, filtering, pagination
- **Calendar**: Good date/time picker components
- **Forms**: Comprehensive form components and validation
- **Documentation**: Clear docs and examples
- **TypeScript support**: Full type safety
- **Theme**: Professional, clean look for business app

## Options Considered

### Option A: PrimeVue

**Pros:**

- ✅ **Comprehensive** - 90+ components out of the box
- ✅ **DataTable** - powerful table with every feature (sort, filter, pagination, export)
- ✅ **Calendar** - excellent date/time pickers
- ✅ **Forms** - every input type you need
- ✅ **Charts** - built-in chart components (for financial reports)
- ✅ **Free** - fully open source, no paid tier
- ✅ **Vue-native** - built specifically for Vue 3
- ✅ **TypeScript** - full type definitions
- ✅ **Themes** - multiple professional themes
- ✅ **Well-documented** - extensive docs and examples
- ✅ **Battle-tested** - mature, used in enterprise

**Cons:**

- ⚠️ **Less trendy** - not as "cool" as shadcn-style
- ⚠️ **Opinionated styling** - harder to customize deeply

**Perfect for:**

- Admin dashboards
- Internal tools
- Data-heavy applications

### Option B: shadcn-vue

**Pros:**

- ✅ **Modern aesthetic** - beautiful, trendy design
- ✅ **Customizable** - you own the code (copy/paste)
- ✅ **Tailwind-based** - easy to customize
- ✅ **Growing ecosystem** - active development

**Cons:**

- ❌ **Incomplete** - missing many components
- ❌ **No DataTable** - would need to build complex table yourself
- ❌ **No Calendar** - would need third-party library
- ❌ **More assembly** - copy/paste each component
- ❌ **Less mature** - newer, less stable

**Perfect for:**

- Marketing sites
- Public-facing apps
- When design > speed

### Option C: Vuetify

**Pros:**

- ✅ **Comprehensive** - full component library
- ✅ **Material Design** - Google's design system
- ✅ **Mature** - very established

**Cons:**

- ❌ **Heavy** - large bundle size
- ❌ **Material Design** - strong opinions, harder to customize
- ❌ **Slower** - performance not as good as PrimeVue

### Option D: Element Plus

**Pros:**

- ✅ **Comprehensive** - full component set
- ✅ **Popular** - large community

**Cons:**

- ⚠️ **Chinese-first docs** - translations can be rough
- ⚠️ **Design system** - very specific aesthetic

## Decision

**We will use PrimeVue.**

### Rationale

1. **Completeness wins**: Has everything we need (DataTable, Calendar, Charts)
2. **Speed to market**: Don't waste time building complex tables from scratch
3. **Admin tool fit**: PrimeVue is designed exactly for this use case
4. **Free & open source**: No hidden costs
5. **Can always reskin later**: If design becomes important, can customize themes

### Theme Choice

**Recommended starter theme:**

- **Lara** (PrimeVue's default modern theme)
- Clean, professional, works well for business apps
- Can switch themes easily if needed

### Installation & Setup

```bash
pnpm add primevue primeicons
```

```tsx
// main.ts
import PrimeVue from 'primevue/config'
import 'primevue/resources/themes/lara-light-blue/theme.css'
import 'primevue/resources/primevue.min.css'
import 'primeicons/primeicons.css'

app.use(PrimeVue)
```

### Key Components We'll Use

**Data Display:**

- `DataTable` - inquiries, bookings, performers lists
- `Column` - table columns with sorting, filtering
- `Calendar` - date pickers for events
- `Chart` - financial reports (Phase 1+)

**Forms:**

- `InputText`, `InputNumber`, `Textarea`
- `Dropdown`, `MultiSelect`
- `Button`

**Navigation:**

- `Menu`, `Menubar` - app navigation
- `TabView` - tabbed interfaces
- `Breadcrumb` - page hierarchy

**Feedback:**

- `Dialog` - modals
- `Toast` - notifications
- `ConfirmDialog` - confirmations

## Consequences

### Positive

- Ship features fast with ready-made components
- Professional-looking UI with zero design work
- Powerful DataTable handles all list views
- Calendar components for scheduling
- No need to build complex components from scratch
- TypeScript support throughout
- Can add charts later without new library

### Negative

- Not as "cool" looking as trendy component libraries
- Harder to deeply customize styling
- Opinionated component design

### Risks

- **Design limitations**: May hit styling walls
  - _Mitigation_: PrimeVue has theming system; can customize. If needed, can migrate specific components to custom ones
- **Aesthetic concerns**: Might not wow users visually
  - _Mitigation_: This is an internal tool; functionality > aesthetics. Can improve design in Phase 2

## Follow-up Actions

- [ ] Install PrimeVue and PrimeIcons
- [ ] Configure Lara theme
- [ ] Create example DataTable for inquiries list
- [ ] Set up Toast service for notifications
- [ ] Create form examples with PrimeVue inputs
- [ ] Configure ConfirmDialog for delete confirmations
- [ ] Document common component patterns in style guide
