# ADR 005: Navigation Shell Architecture & Feature Status Management

**Status:** Proposed  
**Date:** 2025-01-18  
**Deciders:** Jeff Crosley (Architect)

## Context

JeffApp is a portfolio application designed to demonstrate capabilities to prospective employers across multiple frameworks and platforms. The navigation shell must:

- Adapt responsively from mobile (hamburger menu) to desktop (persistent drawer)
- Provide space for sub-applications (microfrontends) to occupy the full main area
- Clearly label in-progress work (WIP) to set transparent expectations about project maturity
- Allow visitors to see the full scope of work (not hide incomplete features)
- Maintain a clean, professional interface on all screen sizes

### Current State

- Navigation is inline in header (not responsive)
- No drawer/menu system for mobile
- No feature status indicators
- Sub-applications have limited space due to fixed header layout

### Requirements

**Navigation Architecture:**

- **Mobile-first responsive:** Hamburger menu on small screens (< 1024px), persistent drawer on desktop
- **Desktop drawer:** 280px persistent sidebar, always visible
- **Mobile drawer:** Dismissible overlay with dark backdrop, slides from left
- **Non-shifting layout:** Drawer overlays main content (doesn't push it), no layout shift
- **Header:** Contains only theme toggle button
- **Drawer:** Contains portfolio title and all navigation links
- **Main content:** Full-width, flexible space for sub-applications
- **Smooth animations:** Use design token durations (`--duration-normal: 300ms`)

**Feature Status Management:**

- **Transparent labeling:** WIPs must be clearly marked (🚧 WIP badge)
- **Always visible:** Features should be accessible regardless of maturity (show don't hide)
- **Scalable:** Support multiple status levels (`stable`, `wip`, `beta`, future extensibility)
- **Declarative:** Route definitions should be the single source of truth for status
- **Integrated into navigation:** Badges appear inline with navigation links in the drawer
- **Portfolio-appropriate:** Demonstrates architectural maturity and thoughtful feature management

## Decision

Implement a **Responsive Navigation Shell** with integrated feature status management:

1. **Responsive Drawer Navigation**

   - Mobile (< 1024px): Hamburger menu → dismissible overlay drawer
   - Desktop (≥ 1024px): Persistent 280px left sidebar
   - Non-shifting layout: Drawer overlays content with semi-transparent backdrop
   - Smooth transitions using design token durations

2. **Header & Drawer Layout**

   - Header: Theme toggle button only (minimal, always visible)
   - Drawer: Portfolio title + navigation links + feature status badges
   - Main area: Full-width, flexible for sub-applications

3. **Feature Status Management**
   - Route metadata (`data.status`) — Declarative feature status at route definition
   - FeatureVisibilityService — Maps status → indicator text
   - FeatureStatusDirective — Adds CSS classes for styling
   - Badges integrate seamlessly into drawer navigation links

### Architecture Overview

```
apps/nav-shell/src/app/
├── app.ts                                 # Root component (header + drawer + main)
├── app.routes.ts                          # Route definitions with status metadata
├── components/
│   ├── navigation-drawer/
│   │   ├── navigation-drawer.component.ts # Responsive drawer (mobile/desktop)
│   │   ├── navigation-drawer.component.scss
│   │   └── navigation-drawer.component.spec.ts
│   └── nav-link/
│       ├── nav-link.component.ts          # Reusable nav link with badge
│       ├── nav-link.component.scss
│       └── nav-link.component.spec.ts
├── directives/
│   └── feature-status.directive.ts        # CSS class management for status
├── services/
│   ├── feature-visibility.service.ts      # Status → indicator mapping
│   └── drawer.service.ts                  # Drawer state management (open/close)
└── types/
    └── feature.types.ts                   # FeatureStatus, NavLink types

libs/ui-angular/src/lib/
├── directives/
│   └── feature-status.directive.ts        # Can be shared if used elsewhere
└── services/
    └── feature-visibility.service.ts      # Shared service
```

### Responsive Behavior

**Mobile (< 1024px):**

```
┌─────────────────┐
│ 🌙  (theme)     │  ← Header (only)
├─────────────────┤
│                 │
│  Main Content   │  ← Full width
│                 │  (Router outlet for pages/subapps)
│                 │
└─────────────────┘

[When hamburger clicked]
┌─────────────────┐
│ 🌙  ☰ (menu)    │  ← Header
├─────────────────┤
│ [Dark overlay]  │  ← Backdrop (40% opacity)
├─────────────────┤
│ Drawer          │  ← Slides from left (280px)
│ • Home          │
│ • About         │
│ • Components 🚧 │
│ • GitHub        │
└─────────────────┘
```

**Desktop (≥ 1024px):**

```
┌──────────┬──────────────────┐
│ 🌙       │                  │
├──────────┤  Main Content    │  ← Full width, router outlet
│ Drawer   │  (Pages/Subapps) │
│ (280px)  │                  │
│ • Home   │                  │
│ • About  │                  │
│ • Comp 🚧│                  │
│ • GitHub │                  │
│          │                  │
└──────────┴──────────────────┘
```

### Feature Status Levels

```typescript
type FeatureStatus = 'stable' | 'wip' | 'beta';

// Semantics:
// - stable:  Production-ready, no badge
// - wip:     Work-in-progress, shows 🚧 badge (implies unfinished/rough)
// - beta:    Released but experimental, shows 🧪 badge (implies feedback welcome)
```

### Implementation Details

#### 1. Route Definitions

```typescript
// apps/nav-shell/src/app/app.routes.ts
export const routes: Routes = [
  {
    path: '',
    component: HomePage,
    data: { status: 'stable' },
  },
  {
    path: 'about',
    component: AboutPage,
    data: { status: 'stable' },
  },
  {
    path: 'components',
    component: ComponentsPage,
    data: { status: 'wip' },
  },
];
```

#### 2. Navigation Data Structure

```typescript
// apps/nav-shell/src/app/app.ts
protected navigationLinks: NavLink[] = [
  { label: 'Home', route: '/', status: 'stable' },
  { label: 'About', route: '/about', status: 'stable' },
  { label: 'Components', route: '/components', status: 'wip' },
  { label: 'GitHub', route: 'https://github.com/jeffcrosley', status: 'stable', external: true },
];
```

#### 3. FeatureVisibilityService

```typescript
// apps/nav-shell/src/app/services/feature-visibility.service.ts
import { Injectable } from '@angular/core';

export type FeatureStatus = 'stable' | 'wip' | 'beta';

@Injectable({ providedIn: 'root' })
export class FeatureVisibilityService {
  /**
   * Map feature status to user-facing indicator badge
   * Always returns indicator (regardless of environment)
   *
   * @param status - Feature status level
   * @returns Indicator text (e.g., "🚧 WIP") or null if stable
   */
  getIndicator(status: FeatureStatus): string | null {
    switch (status) {
      case 'wip':
        return '🚧 WIP';
      case 'beta':
        return '🧪 Beta';
      case 'stable':
      default:
        return null;
    }
  }
}
```

#### 4. DrawerService (State Management)

```typescript
// apps/nav-shell/src/app/services/drawer.service.ts
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class DrawerService {
  private isOpen$ = new BehaviorSubject<boolean>(false);

  constructor(private breakpointService: BreakpointService) {
    // Auto-close drawer on desktop (for cases where it was open on mobile)
    this.breakpointService.isDesktop$.subscribe((isDesktop) => {
      if (isDesktop) {
        this.close();
      }
    });
  }

  getIsOpen(): Observable<boolean> {
    return this.isOpen$.asObservable();
  }

  open(): void {
    this.isOpen$.next(true);
  }

  close(): void {
    this.isOpen$.next(false);
  }

  toggle(): void {
    this.isOpen$.next(!this.isOpen$.value);
  }
}
```

#### 5. BreakpointService (Responsive Detection)

```typescript
// apps/nav-shell/src/app/services/breakpoint.service.ts
import { Injectable, OnDestroy } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class BreakpointService implements OnDestroy {
  private readonly DESKTOP_BREAKPOINT = 1024; // --breakpoint-lg
  private isDesktop$ = new BehaviorSubject<boolean>(this.checkIsDesktop());
  private mediaQuery: MediaQueryList;

  constructor() {
    this.mediaQuery = window.matchMedia(`(min-width: ${this.DESKTOP_BREAKPOINT}px)`);
    this.mediaQuery.addEventListener('change', this.onMediaChange.bind(this));
  }

  getIsDesktop(): Observable<boolean> {
    return this.isDesktop$.asObservable();
  }

  private checkIsDesktop(): boolean {
    return window.matchMedia(`(min-width: ${this.DESKTOP_BREAKPOINT}px)`).matches;
  }

  private onMediaChange(event: MediaQueryListEvent): void {
    this.isDesktop$.next(event.matches);
  }

  ngOnDestroy(): void {
    this.mediaQuery.removeEventListener('change', this.onMediaChange.bind(this));
  }
}
```

#### 6. FeatureStatusDirective

```typescript
// apps/nav-shell/src/app/directives/feature-status.directive.ts
import { Directive, ElementRef, Input } from '@angular/core';
import type { FeatureStatus } from '../services/feature-visibility.service';

/**
 * Adds CSS classes to elements based on feature status
 * Allows styling of WIP/beta features with visual indicators
 *
 * Usage: <a [appFeatureStatus]="'wip'">Components</a>
 * Result: <a class="feature-wip">Components</a>
 */
@Directive({
  selector: '[appFeatureStatus]',
  standalone: true,
})
export class FeatureStatusDirective {
  @Input() appFeatureStatus!: FeatureStatus;

  constructor(el: ElementRef) {
    if (this.appFeatureStatus !== 'stable') {
      el.nativeElement.classList.add(`feature-${this.appFeatureStatus}`);
    }
  }
}
```

#### 7. Root App Component

```typescript
// apps/nav-shell/src/app/app.ts
@Component({
  selector: 'app-root',
  imports: [CommonModule, RouterModule, NavigationDrawerComponent],
  template: `
    <header class="app-header">
      <button class="theme-toggle" (click)="toggleTheme()" ...>
        <!-- Theme icon -->
      </button>
      <button *ngIf="!(breakpoint.getIsDesktop() | async)"
              class="hamburger"
              (click)="drawer.toggle()">
        ☰
      </button>
    </header>

    <div class="app-container">
      <app-navigation-drawer
        [links]="navigationLinks"
        [isOpen]="(drawer.getIsOpen() | async)">
      </app-navigation-drawer>

      <main class="main-content"
            [class.overlay-active]="(drawer.getIsOpen() | async)"
            (click)="drawer.close()">
        <router-outlet></router-outlet>
      </main>
    </div>
  `,
  styles: [...]
})
export class App {
  protected navigationLinks = [...];

  constructor(
    public drawer: DrawerService,
    public breakpoint: BreakpointService,
    protected themeService: ThemeService,
    protected featureVisibility: FeatureVisibilityService
  ) {}
}
```

#### 8. NavigationDrawerComponent

```typescript
// apps/nav-shell/src/app/components/navigation-drawer/navigation-drawer.component.ts
@Component({
  selector: 'app-navigation-drawer',
  imports: [CommonModule, RouterModule, FeatureStatusDirective],
  template: `
    <aside class="nav-drawer" [class.open]="(isOpen$ | async)">
      <div class="drawer-header">
        <h1 class="portfolio-title">Jeff Crosley</h1>
      </div>

      <nav class="drawer-nav">
        <ul class="nav-links">
          @for (link of links; track link.label) {
            <li>
              <a [routerLink]="link.route"
                 [href]="link.external ? link.route : null"
                 [target]="link.external ? '_blank' : null"
                 [appFeatureStatus]="link.status"
                 [attr.data-status]="link.status"
                 routerLinkActive="active"
                 [routerLinkActiveOptions]="{ exact: link.route === '/' }">
                {{ link.label }}
                @if (getIndicator(link.status)) {
                  <span class="feature-badge">{{ getIndicator(link.status) }}</span>
                }
              </a>
            </li>
          }
        </ul>
      </nav>
    </aside>
  `,
  styles: [...]
})
export class NavigationDrawerComponent {
  @Input() links!: NavLink[];
  @Input() isOpen$!: Observable<boolean>;

  constructor(private featureVisibility: FeatureVisibilityService) {}

  getIndicator(status: FeatureStatus): string | null {
    return this.featureVisibility.getIndicator(status);
  }
}
```

## Consequences

### Positive

- **Responsive by design:** Mobile-first, scales elegantly to desktop
- **Space-optimized:** Main content gets full width (especially important for sub-applications)
- **Non-invasive navigation:** Drawer overlays content, doesn't push it
- **Accessibility:** Always-visible theme toggle in header
- **Feature transparency:** WIP badges clearly visible in drawer
- **Scalable pattern:** Easy to add new status levels or navigation items
- **Portfolio-appropriate:** Shows thoughtful responsive design and feature management
- **Composable:** Services and components are independently reusable

### Negative

- **Mobile complexity:** Drawer management adds code and state
- **Animation overhead:** Slide animations may impact low-end mobile devices
- **Visual clutter (mobile):** Drawer + backdrop takes significant space
- **User education:** Hamburger icon convention varies across browsers/platforms

### Mitigation

- Use CSS transforms for performant animations (will-change, GPU acceleration)
- Implement touch gesture detection (swipe to close on mobile)
- Add visual affordance to hamburger icon (e.g., animated icon)
- Test on actual devices across breakpoints
- Provide keyboard navigation (Esc to close drawer, Tab through links)
- Document navigation patterns in README

## Alternatives Considered

### Top Navigation Bar (Rejected)

```
┌────────────────────────────────────────┐
│ Home | About | Components 🚧 | GitHub  │
└────────────────────────────────────────┘
```

**Rejected because:**

- ❌ No space on mobile (wraps awkwardly)
- ❌ Title disappears or competes for space
- ❌ Hard to accommodate badges inline on small screens

### Tab-based Navigation (Rejected)

```
┌──────┬──────┬────────┬────────┐
│ Home │ About│ Comp 🚧│ GitHub │
├──────┴──────┴────────┴────────┤
│        Content Area            │
└───────────────────────────────┘
```

**Rejected because:**

- ❌ Reduces usable content space
- ❌ Drawer pattern is more professional/modern
- ✅ Could revisit for dashboard-like interfaces

### Sticky Header + Bottom Nav (Mobile Only)

**Rejected because:**

- ❌ Two navigation surfaces create confusion
- ❌ Bottom nav obscures main content on small screens
- ✅ Valid for mobile-only apps (not applicable here)

## Implementation Plan

1. **Create FeatureVisibilityService** (`apps/nav-shell/src/app/services/feature-visibility.service.ts`)
2. **Create FeatureStatusDirective** (`apps/nav-shell/src/app/directives/feature-status.directive.ts`)
3. **Update navigationLinks** with `status` field
4. **Update app.ts template** to display badges
5. **Add styling** for feature badges and WIP links
6. **Write tests** for service and directive
7. **Test manual QA** — verify badges appear in both dev and prod builds
8. **Document pattern** in CONTRIBUTING.md for future features

## Future Considerations

- **Analytics:** Track which WIP features users visit
- **Feedback:** Add "Report issues" link on WIP pages
- **Feature Flags:** Integrate with feature flag service for A/B testing
- **Stencil Components:** Extend pattern to Stencil web components
- **Dashboard:** Create admin dashboard showing feature status overview
- **Deprecation:** Use `deprecated` status for features being sunset

## References

- Related: ADR 004 (Design System Architecture)
- Implementation: `apps/nav-shell/src/app/services/`, `apps/nav-shell/src/app/directives/`
- Angular Routing: https://angular.io/guide/router
- Angular Directives: https://angular.io/guide/attribute-directives
- Feature Flags Pattern: https://martinfowler.com/articles/feature-toggles.html
