# ADR 006: Home Page Architecture

**Status:** Proposed  
**Date:** 2025-01-09  
**Deciders:** Jeff Crosley (Architect)  
**Supersedes:** None  
**Related:** ADR 004 (Design System), ADR 005 (Feature Status)

---

## Context

The home page (landing/portfolio introduction) is the primary entry point for visitors. It must:

1. **Communicate value** with modern design and clear copy (see design spec)
2. **Reuse components** across frameworks (buttons, cards, badges needed in future sub-apps/pages)
3. **Scale maintainably** as features expand (e.g., dedicated Skills sub-app, Experience timeline)
4. **Integrate with existing architecture** (Nx monorepo, Stencil + Angular, design tokens)
5. **Demonstrate portfolio capabilities** (full-stack, cross-framework, TDD-ready)

### Current State

- `nav-shell` app uses **condensed page architecture** (inline templates + styles)
- Stencil library (`@jeffapp/ui-components`) has `app-button` and `app-card` (partially implemented)
- Angular module (`@jeffapp/ui-angular`) exists but is minimal
- Design tokens (`@jeffapp/design-tokens`) provide CSS custom properties for theming
- No shared data structures (skills, highlights) yet

### Requirements from Design Spec

1. **Hero Section:** Full-bleed SVG geometric pattern + dark overlay + centered CTA
2. **Bio Section:** 2-3 paragraphs (max width 700px, generous spacing)
3. **Technical Skills:** 5 categories, badge-based UI (icon + label)
4. **Professional Highlights:** 3 items with left-border accent cards
5. **Call-to-Action:** 3 balanced buttons driving exploration + contact
6. **Footer:** Contact info, GitHub + LinkedIn links, nav shortcuts

---

## Decision

Implement the home page using a **hybrid Stencil + Angular architecture** that:

1. **Extracts reusable UI components to Stencil** (`app-button`, `app-card`, `app-skill-badge`)
2. **Wraps Stencil components in Angular module** (`@jeffapp/ui-angular`) for ease of use in nav-shell
3. **Keeps page-specific logic in single Angular component** (`home.component.ts`)
4. **Stores data as JSON** (`skills.json`) for future API migration
5. **Uses design tokens** for all styling (colors, spacing, typography)
6. **Includes SVG asset** for hero pattern with CSS animations

### Architecture Overview

```
jeffapp (monorepo root)
│
├── libs/
│   ├── ui-components/                 # Stencil Web Components
│   │   └── src/components/
│   │       ├── app-button/            # NEW: Filled/outlined button
│   │       │   ├── app-button.tsx
│   │       │   └── app-button.scss
│   │       ├── app-card/              # EXISTING: Card container
│   │       │   ├── app-card.tsx       # (complete implementation)
│   │       │   └── app-card.scss
│   │       └── app-skill-badge/       # NEW: Skill badge (icon + label)
│   │           ├── app-skill-badge.tsx
│   │           └── app-skill-badge.scss
│   │
│   ├── ui-angular/                    # Angular Wrappers
│   │   └── src/lib/
│   │       ├── button/
│   │       │   ├── app-button.directive.ts  # NEW: Wraps app-button
│   │       │   └── app-button.directive.spec.ts
│   │       ├── card/
│   │       │   ├── app-card.component.ts    # NEW: Wraps app-card
│   │       │   └── app-card.component.spec.ts
│   │       ├── skill-badge/
│   │       │   ├── app-skill-badge.component.ts  # NEW: Wraps app-skill-badge
│   │       │   └── app-skill-badge.component.spec.ts
│   │       └── ui-angular.module.ts  # UPDATED: Export new wrappers
│   │
│   └── design-tokens/                 # Already exists
│       └── src/
│           ├── _tokens.scss
│           ├── _typography.scss
│           └── _animations.scss
│
├── apps/
│   └── nav-shell/
│       └── src/
│           ├── app/
│           │   └── pages/
│           │       └── home.component.ts     # NEW: Single page component
│           │
│           └── assets/
│               ├── data/
│               │   └── skills.json          # NEW: Skills data
│               └── images/
│                   └── hero-pattern.svg     # NEW: Geometric pattern SVG
│
└── docs/
    └── design/
        └── home-page-design-spec.md         # REFERENCE
```

---

## Component Specifications

### 1. Stencil: `app-button` (Enhanced)

**Purpose:** Reusable button component for all UI frameworks.

**Props:**

```typescript
@Prop() label: string;              // Button text
@Prop() variant: 'primary' | 'secondary' = 'primary'; // Styling variant
@Prop() size: 'small' | 'medium' | 'large' = 'medium'; // Size variant
@Prop() disabled: boolean = false;  // Disabled state
@Prop() type: 'button' | 'submit' | 'reset' = 'button'; // HTML type
@Prop() ariaLabel?: string;         // Accessibility label
```

**Events:**

```typescript
@Event() buttonClick: EventEmitter<MouseEvent>; // Emitted on click
```

**Styling:**

- Primary (filled): sapphire-600 → sapphire-500 on hover
- Secondary (outlined): transparent → sapphire-600 on hover
- Sizes: 36px (small), 44px (medium), 52px (large)
- Focus ring: sapphire-500 outline

**Usage in Angular:**

```html
<app-button
	label="Explore Work"
	variant="primary"
	size="medium"
	(buttonClick)="handleExplore()"
>
</app-button>
```

**Location:** `libs/ui-components/src/components/app-button/`

---

### 2. Stencil: `app-card` (Complete Implementation)

**Purpose:** Container for content with optional image, title, description, accent styling.

**Props:**

```typescript
@Prop() title: string;                // Card heading
@Prop() description: string;          // Body text
@Prop() imageUrl?: string;            // Optional image
@Prop() imageAlt?: string = 'Card image';
@Prop() variant: 'default' | 'highlighted' | 'compact' = 'default';
@Prop() accentColor?: 'sapphire' | 'emerald' | 'none' = 'none';
@Prop() accentPosition?: 'left' | 'top' = 'left'; // Border accent
```

**Events:**

```typescript
@Event() cardClick: EventEmitter<{ title: string }>;
```

**Styling (for home page highlights):**

- Accent position: left (4px border)
- Accent color: sapphire (default) → emerald (hover)
- Background: bg-secondary (slate-50/slate-800)
- Border radius: 0 8px 8px 0 (square left for accent bar)
- Hover: translateX(4px), shadow-md

**Location:** `libs/ui-components/src/components/app-card/`

---

### 3. Stencil: `app-skill-badge` (NEW)

**Purpose:** Display a skill with icon and label; hover for emphasis.

**Props:**

```typescript
@Prop() name: string;              // Skill name (e.g., "Angular")
@Prop() iconUrl: string;           // SVG icon URL
@Prop() iconAlt?: string;          // Icon alt text
@Prop() href?: string;             // Optional link (e.g., to docs)
@Prop() target?: '_self' | '_blank' = '_self';
```

**Styling:**

- Default: transparent bg, bordered, monochrome icon
- Hover: bg-tertiary, sapphire border, sapphire icon, translateY(-2px)
- Icon: 24px (desktop), 20px (mobile)
- Label: font-size-sm, font-weight-medium

**Accessibility:**

- If `href` provided, render as `<a>` with proper focus/target attributes
- Otherwise, render as semantic `<span>` with role="img" and aria-label

**Location:** `libs/ui-components/src/components/app-skill-badge/`

---

### 4. Angular: `@jeffapp/ui-angular` Module (Enhanced)

**Purpose:** Framework-specific wrappers for Stencil components + utilities.

**Exports:**

```typescript
// Directives wrapping Stencil components
export { AppButtonComponent } from './lib/button/app-button.directive'
export { AppCardComponent } from './lib/card/app-card.directive'
export { AppSkillBadgeComponent } from './lib/skill-badge/app-skill-badge.directive'

// Utilities (future)
export { ResponsiveService } from './lib/services/responsive.service'
export { ThemeService } from './lib/services/theme.service'
```

**Module Declaration:**

```typescript
@NgModule({
	imports: [CommonModule],
	declarations: [
		AppButtonComponent,
		AppCardComponent,
		AppSkillBadgeComponent
	],
	exports: [
		AppButtonComponent,
		AppCardComponent,
		AppSkillBadgeComponent
	]
})
export class UiAngularModule {}
```

**Button Directive Example:**

```typescript
// This directive provides type-safe Angular property binding
// to the Stencil <app-button> Web Component

import {
	Component,
	Input,
	Output,
	EventEmitter
} from '@angular/core'
import { CUSTOM_ELEMENTS_SCHEMA } from '@angular/core'

@Component({
	selector: 'app-button',
	template: `
		<app-button
			[label]="label"
			[variant]="variant"
			[size]="size"
			[disabled]="disabled"
			[ariaLabel]="ariaLabel"
			(buttonClick)="buttonClick.emit($event)"
		>
		</app-button>
	`,
	standalone: true,
	schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class AppButtonComponent {
	@Input() label = 'Click me'
	@Input() variant: 'primary' | 'secondary' =
		'primary'
	@Input() size: 'small' | 'medium' | 'large' =
		'medium'
	@Input() disabled = false
	@Input() ariaLabel?: string
	@Output() buttonClick =
		new EventEmitter<MouseEvent>()
}
```

**Location:** `libs/ui-angular/src/lib/`

---

### 5. Angular: `home.component.ts` (NEW)

**Purpose:** Single-page component combining all sections of the home page.

**Structure:**

```typescript
import { Component, OnInit } from '@angular/core'
import { CommonModule } from '@angular/common'
import { RouterModule } from '@angular/router'
import { CUSTOM_ELEMENTS_SCHEMA } from '@angular/core'
import { UiAngularModule } from '@jeffapp/ui-angular'

interface Skill {
	category: string
	items: Array<{
		name: string
		icon: string // URL to SVG icon
	}>
}

interface Highlight {
	title: string
	description: string
}

@Component({
	selector: 'app-home',
	standalone: true,
	imports: [
		CommonModule,
		RouterModule,
		UiAngularModule
	],
	schemas: [CUSTOM_ELEMENTS_SCHEMA],
	templateUrl: './home.component.html', // OR inline template
	styleUrls: ['./home.component.scss'] // OR inline styles
})
export class HomeComponent implements OnInit {
	protected skills: Skill[] = []
	protected highlights: Highlight[] = []

	constructor() {}

	ngOnInit() {
		this.loadSkills()
	}

	protected loadSkills() {
		// Load skills.json
		// Parse and organize by category
	}

	// Event handlers for CTAs
	protected onExploreWork() {
		// Navigate to /about or relevant page
	}

	protected onGetInTouch() {
		// Navigate to /contact
	}
}
```

**Data Source:** `skills.json` loaded via HttpClient or static import.

**Location:** `apps/nav-shell/src/app/pages/home.component.ts`

---

### 6. Data: `skills.json`

**Purpose:** Centralized skill definitions with categories and icon URLs.

**Structure:**

```json
{
	"skills": [
		{
			"category": "Frontend",
			"items": [
				{
					"name": "Angular",
					"icon": "/assets/icons/angular.svg"
				},
				{
					"name": "React",
					"icon": "/assets/icons/react.svg"
				}
				// ... more skills
			]
		},
		{
			"category": "Backend",
			"items": [
				{
					"name": "Node.js",
					"icon": "/assets/icons/nodejs.svg"
				}
				// ... more skills
			]
		}
		// ... more categories
	]
}
```

**Location:** `apps/nav-shell/src/assets/data/skills.json`

**Note:** Icons can be sourced from:

- `simpleicons.org` (Simple Icons collection, CC0 license)
- `shields.io` (badge SVGs)
- Custom SVG assets

---

### 7. Asset: `hero-pattern.svg`

**Purpose:** Full-bleed geometric pattern for hero section.

**Design:**

- Abstract triangles in varying sizes and opacities
- Gradient: sapphire-600 → amethyst-600
- ViewBox: scalable to any screen size
- CSS-animated (subtle floating motion)

**Example SVG Structure:**

```svg
<svg viewBox="0 0 1200 800" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1e40af;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#7c3aed;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="1200" height="800" fill="url(#grad)" />

  <!-- Triangles with varying opacities -->
  <polygon points="100,0 200,200 0,200" fill="#fff" opacity="0.3" class="float-animate" style="animation-delay: 0s" />
  <polygon points="400,50 550,250 300,250" fill="#fff" opacity="0.5" class="float-animate" style="animation-delay: 0.5s" />
  <!-- ... more triangles -->
</svg>
```

**CSS Animation:**

```scss
@keyframes float {
	0%,
	100% {
		transform: translateY(0px);
	}
	50% {
		transform: translateY(-20px);
	}
}

.float-animate {
	animation: float 6s ease-in-out infinite;
}
```

**Location:** `apps/nav-shell/src/assets/images/hero-pattern.svg`

---

## Data Flow & Integration

### Home Page → Components

```
home.component.ts
│
├─ [Hero Section]
│  └─ SVG background (hero-pattern.svg)
│  └─ <app-button> (Explore Work, Get in Touch) x2
│
├─ [Bio Section]
│  └─ Static text (hardcoded in template)
│
├─ [Skills Section]
│  └─ Loop over skills.json categories
│     └─ <app-skill-badge> x N
│
├─ [Highlights Section]
│  └─ Loop over highlights[] data
│     └─ <app-card> x 3
│
├─ [CTA Section]
│  └─ <app-button> x 3 (View Experience, Explore Components, Get in Touch)
│
└─ [Footer]
   └─ Static links + social icons
```

### Styling Strategy

1. **Design Tokens:** All colors, spacing, typography from `@jeffapp/design-tokens`
2. **Component-Level Styles:** Stencil components use Shadow DOM (encapsulated)
3. **Page-Level Styles:** Home component inline SCSS (follows condensed page pattern)
4. **Dark Mode:** CSS custom properties auto-adapt via `[data-theme]` on root

---

## File Structure Summary

### New Files to Create

```
libs/ui-components/src/components/
├── app-button/                           # ENHANCE existing
│   ├── app-button.tsx
│   ├── app-button.scss
│   └── app-button.e2e.ts
│
├── app-card/                             # COMPLETE existing
│   ├── app-card.tsx
│   ├── app-card.scss
│   └── app-card.e2e.ts
│
└── app-skill-badge/                      # NEW
    ├── app-skill-badge.tsx
    ├── app-skill-badge.scss
    └── app-skill-badge.e2e.ts

libs/ui-angular/src/lib/
├── button/
│   ├── app-button.directive.ts           # NEW wrapper
│   └── app-button.directive.spec.ts
│
├── card/
│   ├── app-card.directive.ts             # NEW wrapper
│   └── app-card.directive.spec.ts
│
├── skill-badge/
│   ├── app-skill-badge.directive.ts      # NEW wrapper
│   └── app-skill-badge.directive.spec.ts
│
└── ui-angular.module.ts                  # UPDATED

apps/nav-shell/src/
├── app/pages/
│   └── home.component.ts                 # NEW (single component)
│
└── assets/
    ├── data/
    │   └── skills.json                   # NEW
    └── images/
        └── hero-pattern.svg              # NEW
```

### Files to Update

```
libs/ui-components/
├── src/
│   ├── components/app-button/
│   │   ├── app-button.tsx                # Add size prop
│   │   └── app-button.scss               # Add size variants
│   │
│   └── index.ts                          # Export new components

libs/ui-angular/
└── src/
    ├── lib/
    │   └── ui-angular.module.ts          # Import new directives
    └── index.ts                          # Export new directives

apps/nav-shell/
├── src/
│   ├── app/
│   │   └── app.routes.ts                 # Add home route (update dashboard → home)
│   │
│   └── styles.scss                       # Ensure design tokens imported
│
└── project.json                          # (no changes needed)
```

---

## Library Abstraction Rationale

| Component         | Location          | Reusability | Rationale                                                                                  |
| ----------------- | ----------------- | ----------- | ------------------------------------------------------------------------------------------ |
| `app-button`      | Stencil           | ⭐⭐⭐ High | Core UI element; needed in all frameworks (Angular, React, Vue) and all pages.             |
| `app-skill-badge` | Stencil           | ⭐⭐⭐ High | Skills appear on home, about, future Skills sub-app, potentially React/Vue microfrontends. |
| `app-card`        | Stencil           | ⭐⭐⭐ High | Cards are universal (project showcases, experience timelines, testimonials).               |
| Skills data       | JSON              | ⭐⭐ Medium | Currently home-page-only, but shared by About page later; future API endpoint.             |
| Hero pattern      | SVG asset         | ⭐ Low      | Specific to home page hero; not reused elsewhere (for now).                                |
| Home page layout  | Angular component | ⭐ Low      | Specific to home page; sections could extract later if needed.                             |

---

## Implementation Phases

### Phase 1: Setup & Stencil Components (Week 1)

- [ ] Enhance `app-button` with size variants
- [ ] Complete `app-card` implementation
- [ ] Create `app-skill-badge` component
- [ ] Create hero SVG pattern asset

### Phase 2: Angular Wrappers (Week 1-2)

- [ ] Create Angular directive wrappers for Stencil components
- [ ] Update `ui-angular.module.ts`
- [ ] Write unit tests for wrappers

### Phase 3: Home Page Component (Week 2)

- [ ] Create `home.component.ts` (single component, inline template + styles)
- [ ] Create `skills.json` with data structure
- [ ] Implement section rendering (hero, bio, skills, highlights, CTA, footer)
- [ ] Integrate SVG hero pattern with CSS animations
- [ ] Update routes to use home instead of dashboard

### Phase 4: Testing & QA (Week 2-3)

- [ ] Unit tests for home component (TDD)
- [ ] E2E tests for Stencil components
- [ ] Accessibility testing (WCAG AA)
- [ ] Responsive testing (mobile/tablet/desktop)

### Phase 5: Polish & Deployment (Week 3)

- [ ] Performance optimization (image optimization, lazy loading)
- [ ] Dark mode testing
- [ ] Final design review
- [ ] Deploy to Render

---

## Risks & Mitigations

| Risk                             | Impact | Mitigation                                                                  |
| -------------------------------- | ------ | --------------------------------------------------------------------------- |
| Stencil component complexity     | High   | Start simple (button, badge); iterate based on feedback.                    |
| Angular-Stencil integration bugs | Medium | Write integration tests early; test in real component.                      |
| SVG animation performance        | Low    | Test on mobile devices; fallback to static gradient if needed.              |
| Icon sourcing/licensing          | Medium | Use open-source icons (Simple Icons CC0, or custom SVGs); document sources. |

---

## Success Criteria

- [ ] Home page loads in <2s on 4G
- [ ] All Stencil components export properly; no build errors
- [ ] Angular wrappers provide type-safe property binding
- [ ] Dark mode works without additional effort (design tokens handle it)
- [ ] Accessibility audit passes (WCAG AA, Lighthouse >90)
- [ ] Mobile/tablet/desktop layouts render correctly
- [ ] Hero SVG animation smooth on desktop (no jank on mobile)
- [ ] Unit tests cover home component logic
- [ ] E2E tests cover user journeys (hero CTA, skill exploration, footer links)

---

## Handoff Notes

**For QA Coach:**

- Write tests for button variants (primary, secondary, sizes)
- Test skill badge hover/focus states
- Test card accent bar colors and transitions
- Validate hero contrast (text on overlay image)
- Test external links (GitHub, LinkedIn) open in new tab
- Test responsive behavior at 375px, 768px, 1024px

**For Developer:**

- Follow Stencil best practices (Shadow DOM, props validation)
- Use design tokens for all colors/spacing in SCSS
- Ensure Stencil components are framework-agnostic (no Angular-specific code)
- Test Stencil components in multiple browsers (Chrome, Firefox, Safari)
- Document component APIs in JSDoc comments

**For Designer/UX:**

- Validate hero pattern visibility in both light/dark modes
- Test skill badge hover states on touch devices (might not work; ensure keyboard nav works)
- Review footer layout on mobile (<375px edge case)

---

## Appendix: Component API Reference

### `<app-button>`

```typescript
// Props
@Prop() label: string;
@Prop() variant: 'primary' | 'secondary' = 'primary';
@Prop() size: 'small' | 'medium' | 'large' = 'medium';
@Prop() disabled: boolean = false;
@Prop() type: 'button' | 'submit' | 'reset' = 'button';
@Prop() ariaLabel?: string;

// Events
@Event() buttonClick: EventEmitter<MouseEvent>;

// Methods
(public) setFocus(): Promise<void>;
```

### `<app-card>`

```typescript
// Props
@Prop() title: string;
@Prop() description: string;
@Prop() imageUrl?: string;
@Prop() imageAlt?: string = 'Card image';
@Prop() variant: 'default' | 'highlighted' | 'compact' = 'default';
@Prop() accentColor?: 'sapphire' | 'emerald' | 'none' = 'none';
@Prop() accentPosition?: 'left' | 'top' = 'left';

// Events
@Event() cardClick: EventEmitter<{ title: string }>;

// Slots
<slot></slot> // Custom card content
```

### `<app-skill-badge>`

```typescript
// Props
@Prop() name: string;
@Prop() iconUrl: string;
@Prop() iconAlt?: string;
@Prop() href?: string;
@Prop() target?: '_self' | '_blank' = '_self';

// Events (if interactive)
@Event() badgeClick: EventEmitter<{ name: string }>;
```

---

**Architecture Specification Complete. Ready for QA Coach & Developer.**
