# Design: 3-Layer SDK Architecture

## Context

HAI3 needs a modular, SOLID-compliant architecture that:
- Allows users to pick individual SDK pieces
- Provides a cohesive framework for those who want it
- Lets users own their rendering code (CLI-generated)
- Supports future framework adapters (Vue, Solid, Svelte)

**Stakeholders:**
- SDK consumers wanting individual packages
- Framework users wanting HAI3 patterns with custom UI
- React users wanting full HAI3 experience
- Future Vue/Solid/Svelte adapter authors

**Constraints:**
- SDK packages must have ZERO @hai3 inter-dependencies
- Backward compatibility for existing @hai3/uicore users
- TypeScript strict mode with exceptional typing quality
- All protections (ESLint, dependency-cruiser) implemented BEFORE code changes

## Goals / Non-Goals

**Goals:**
- Full SOLID compliance across all packages
- Types-first design with best TypeScript techniques
- TDD approach: protections before implementation
- CLI-generated layout following shadcn/ui model
- Framework-agnostic core enabling future adapters

**Non-Goals:**
- Vue/Solid/Svelte adapters (future work)
- Breaking existing apps (backward compat required)
- Changing the event-driven Flux pattern (it works well)

## SOLID Principles Validation

### S - Single Responsibility Principle

Each package has ONE reason to change:

| Package | Single Responsibility | Changes When |
|---------|----------------------|--------------|
| `@hai3/state` | Complete dataflow pattern (events + store + effects) | Flux architecture changes |
| `@hai3/screensets` | Screenset contracts + registry | Screenset contract changes |
| `@hai3/api` | HTTP communication | API patterns change |
| `@hai3/i18n` | Internationalization | i18n strategy changes |
| `@hai3/framework` | Plugin-based SDK integration + layout state | HAI3 patterns change |
| `@hai3/react` | React bindings | React-specific needs change |

**Why @hai3/state instead of separate events/store packages:**
- Events and store are tightly coupled in Flux pattern
- Neither makes sense standalone - events without handlers, store without events
- Complete dataflow pattern is the atomic unit of value
- Reduces package count without violating SRP (single responsibility = Flux pattern)

### O - Open/Closed Principle

Packages are open for extension, closed for modification:

| Extension Point | Mechanism |
|-----------------|-----------|
| Custom events | Module augmentation of `EventPayloadMap` |
| Custom slices | `registerSlice()` function |
| Custom API services | `apiRegistry.register()` |
| Custom translations | `i18nRegistry.registerLoader()` |
| Custom screensets | `screensetRegistry.register()` |

### L - Liskov Substitution Principle

Base types can be substituted with derived types:

```typescript
// Base type
interface ApiService {
  get<T>(url: string): Promise<T>;
  post<T>(url: string, data: unknown): Promise<T>;
}

// Any implementation can substitute
class RestApiService implements ApiService { ... }
class MockApiService implements ApiService { ... }
class GraphQLApiService implements ApiService { ... }
```

### I - Interface Segregation Principle

Users import ONLY what they need:

```typescript
// User wants flux (events + store)
import { eventBus, createStore, registerSlice } from '@hai3/state';

// User wants just API
import { RestProtocol } from '@hai3/api';  // No flux, standalone

// User wants full framework
import { createHAI3App } from '@hai3/framework';  // Gets everything wired
```

### D - Dependency Inversion Principle

High-level modules don't depend on low-level modules:

```
WRONG (current):
  @hai3/react → @hai3/uikit (concrete implementation)

RIGHT (proposed):
  @hai3/react → NO UI dependency
  CLI generates layout → uses user's UI kit
```

## Types-First Design

### Core Type Definitions

Each SDK package exports its types as the primary API:

```typescript
// @hai3/state - Complete dataflow types
export interface EventBus<TEvents extends EventPayloadMap = EventPayloadMap> {
  emit<K extends keyof TEvents>(event: K, payload: TEvents[K]): void;
  on<K extends keyof TEvents>(event: K, handler: (payload: TEvents[K]) => void): Unsubscribe;
  once<K extends keyof TEvents>(event: K, handler: (payload: TEvents[K]) => void): Unsubscribe;
}

export interface EventPayloadMap {
  // Base events - extended via module augmentation
}

export interface RootState {
  // Augmented by slices
}

export type AppDispatch = Dispatch<UnknownAction>;
export type EffectInitializer = (dispatch: AppDispatch, getState: () => RootState) => void;

// @hai3/screensets - Contracts (pure TypeScript, zero deps)
export interface ScreenConfig {
  id: string;
  loader: () => Promise<{ default: unknown }>;
}

export interface MenuItemConfig {
  id: string;
  label: string;  // Translation key
  icon?: string;
  screenId?: string;
  children?: MenuItemConfig[];
}

export interface ScreensetDefinition {
  id: string;
  category: ScreensetCategory;
  defaultScreen: string;
  screens: ScreenConfig[];
  menu: MenuItemConfig[];
}

// @hai3/framework - Layout state shapes (framework owns state)
export interface LayoutDomainState<TConfig = unknown> {
  visible: boolean;
  config: TConfig;
}
```

### TypeScript Best Practices

| Technique | Usage |
|-----------|-------|
| **Discriminated unions** | Event types, action types |
| **Template literal types** | Event names `${screenset}/${domain}/${action}` |
| **Mapped types** | Registry type inference |
| **Conditional types** | Payload extraction from event names |
| **Module augmentation** | Extending EventPayloadMap, RootState |
| **const assertions** | Event name enums, domain IDs |
| **Branded types** | ScreensetId, ScreenId for type safety |

### Example: Type-Safe Event System

```typescript
// Template literal types for event names
type EventName<
  TScreenset extends string,
  TDomain extends string,
  TAction extends string
> = `${TScreenset}/${TDomain}/${TAction}`;

// Branded types for IDs
type ScreensetId = string & { readonly __brand: 'ScreensetId' };
type ScreenId = string & { readonly __brand: 'ScreenId' };

// Conditional type for payload extraction
type PayloadOf<K extends keyof EventPayloadMap> = EventPayloadMap[K];

// Usage - module augmentation extends @hai3/state
declare module '@hai3/state' {
  interface EventPayloadMap {
    'chat/threads/selected': { threadId: string };
    'chat/messages/received': { message: Message };
  }
}

// Type-safe emit
eventBus.emit('chat/threads/selected', { threadId: '123' });  // ✅
eventBus.emit('chat/threads/selected', { wrong: 'key' });     // ❌ Type error
```

## Package Dependency Graph

```
                     LAYER 1: SDK (Flat, zero @hai3 deps)

┌─────────────────────┐  ┌────────────┐  ┌───────────┐  ┌───────────┐
│        state        │  │ screensets │  │    api    │  │   i18n    │
│                     │  │            │  │           │  │           │
│ EventBus, Store,    │  │ Contracts  │  │ Rest/SSE  │  │ Registry  │
│ Effects, Types      │  │ + Registry │  │ Protocols │  │ Loaders   │
└─────────────────────┘  └────────────┘  └───────────┘  └───────────┘
           │                   │              │              │
           └───────────────────┴──────────────┴──────────────┘
                                    │
                     LAYER 2: Framework
                                    │
                     ┌──────────────▼──────────────┐
                     │        @hai3/framework       │
                     │                              │
                     │  • Plugin architecture      │
                     │  • screensetRegistry        │
                     │  • themeRegistry            │
                     │  • routeRegistry            │
                     │  • Effect coordination      │
                     └──────────────┬──────────────┘
                                    │
                     LAYER 3: React Adapter
                                    │
                     ┌──────────────▼──────────────┐
                     │         @hai3/react          │
                     │                              │
                     │  • HAI3Provider             │
                     │  • React hooks              │
                     │  • AppRouter                │
                     │  • NO Layout components     │
                     └─────────────────────────────┘

                     LAYER 4: CLI-Generated (User's Project)

                     ┌─────────────────────────────┐
                     │    src/layout/*.tsx         │
                     │                              │
                     │  • Layout, Header, Menu...  │
                     │  • Uses user's UI kit       │
                     │  • User owns this code      │
                     └─────────────────────────────┘
```

### @hai3/state Package Contents

The flux package provides the complete dataflow pattern:

```typescript
// @hai3/state exports
export {
  // EventBus
  eventBus,           // Singleton event bus instance
  EventBus,           // EventBus class/interface
  EventPayloadMap,    // Type-safe event payloads (augmentable)
  EventHandler,       // Handler function type
  Unsubscribe,        // Cleanup function type

  // Store
  store,              // Redux store instance
  createStore,        // Store factory
  registerSlice,      // Dynamic slice registration
  hasSlice,           // Check if slice exists
  createSlice,        // Re-exported from RTK

  // Effects
  EffectInitializer,  // Effect initializer type

  // State types
  RootState,          // Augmentable root state
  AppDispatch,        // Typed dispatch
};
```

## Layer Rules vs User Code

**IMPORTANT DISTINCTION:**

| Context | Can Import From | Enforced By |
|---------|-----------------|-------------|
| **SDK packages** (flux, layout, api, i18n) | NO @hai3 packages | dependency-cruiser |
| **Framework package** | Only SDK packages | dependency-cruiser |
| **React package** | Only framework | dependency-cruiser |
| **User code** (src/, generated layout) | ANY @hai3 package | Not enforced |

User code and CLI-generated layout code CAN import from any @hai3 package. This is intentional:
- Generated `Header.tsx` imports slices from `@hai3/framework` (owns layout state)
- Generated `Header.tsx` imports types from `@hai3/screensets` (owns contracts)
- Screenset actions emit events via `eventBus` from `@hai3/state`
- Components use `useAppSelector` hook from `@hai3/react` for state access

Layer rules enforce **package-to-package dependencies**, not user code imports.

## Registry Placement

| Registry | Package | Rationale |
|----------|---------|-----------|
| `eventBus` | `@hai3/state` | Core of dataflow pattern |
| `store` | `@hai3/state` | Core of dataflow pattern |
| `apiRegistry` | `@hai3/api` | Registers API services |
| `i18nRegistry` | `@hai3/i18n` | Registers translation loaders |
| `screensetRegistry` | `@hai3/screensets` | Singleton in SDK, re-exported by framework with i18n wiring |
| `themeRegistry` | `@hai3/framework` | Themes are HAI3 pattern (GLOBAL, not per-screenset) |
| `routeRegistry` | `@hai3/framework` | Routing is HAI3 pattern |

## Action Pattern

Actions are **handwritten pure functions** that emit events. They are the ONLY entry point for event emission, maintaining strict knowledge separation between components and the event system.

### Core Principles

1. **Actions are handwritten** - No `createAction` helper in SDK. Actions contain real business logic.
2. **Only actions emit events** - Components call action functions, never `eventBus.emit()` directly.
3. **Knowledge separation** - Components know about action functions, NOT about events.
4. **Actions are pure** - They emit events and return void. No side effects, no store dispatch.

### Why No createAction Helper in SDK?

The user explicitly rejected the `createAction` helper pattern:

> "Action is a pure function, which has logic inside. It's not just an event emitter."
> "Components can't know anything about events by design."

A factory like `createAction()` exposed in SDK would:
- Encourage components to create inline actions (violating knowledge separation)
- Hide the fact that actions contain business logic
- Make it too easy to bypass the action layer

### Action Definition (in Screenset)

Actions are defined in the screenset's `actions/` folder. They are real functions with logic:

```typescript
// src/screensets/chat/actions/threads.ts
import { eventBus } from '@hai3/state';

/**
 * Action: Select a thread for viewing.
 * Contains validation and business logic.
 */
export function selectThread(threadId: string): void {
  // Validation (actions can have logic)
  if (!threadId) {
    console.warn('selectThread called with empty threadId');
    return;
  }

  // Emit event - this is what effects listen to
  eventBus.emit('chat/threads/selected', { threadId });
}

/**
 * Action: Mark thread as read.
 */
export function markThreadRead(threadId: string): void {
  eventBus.emit('chat/threads/marked-read', { threadId });
}
```

### Framework Actions (Internal)

Framework defines core actions internally (not exposed as SDK primitives):

```typescript
// @hai3/framework/src/actions/navigation.ts (INTERNAL)
import { eventBus } from '@hai3/state';

export function navigateToScreen(screensetId: string, screenId: string): void {
  eventBus.emit('navigation/screen/navigated', { screensetId, screenId });
}

export function changeTheme(themeId: string): void {
  eventBus.emit('theme/changed', { themeId });
}
```

These are provided to user code via the plugin system, not as raw SDK exports.

### Component Usage

Components call action functions. They have NO knowledge of events:

```typescript
// src/screensets/chat/screens/threads/ThreadList.tsx
import { selectThread } from '../../actions/threads';

export const ThreadList: React.FC = () => {
  const threads = useThreads();

  return (
    <ul>
      {threads.map(thread => (
        <li key={thread.id} onClick={() => selectThread(thread.id)}>
          {thread.title}
        </li>
      ))}
    </ul>
  );
};

// ❌ FORBIDDEN in components:
// eventBus.emit('chat/threads/selected', { threadId: '123' });
```

### Event-Driven Flux Flow

```
Component calls action function (knows nothing about events)
    ↓
Action (handwritten function, contains business logic)
    → emits Event (via eventBus from @hai3/state)
        → Effect subscribes (in screenset's effects/ folder)
            → Updates Slice (via dispatch)
                → Component re-renders (via useAppSelector hook)
```

### Knowledge Separation Benefits

| Layer | Knows About | Does NOT Know About |
|-------|-------------|---------------------|
| Component | Action functions, useAppSelector hook | Events, eventBus, dispatch |
| Action | Events, eventBus | Effects, slices, store |
| Effect | Events, slices, dispatch | Components, actions |
| Slice | State shape, reducers | Events, components |

## Plugin Architecture

### Why Plugins?

A potential user (external company) wants to integrate HAI3 screensets into their existing platform. They already have their own menu, header, and navigation - they only need HAI3's screenset orchestration.

**The Problem**: If `screensetRegistry` requires the full `@hai3/framework` (which depends on ALL SDK packages), users who only need screensets would pull in unnecessary dependencies.

**The Solution**: Plugin architecture allows users to compose only the features they need, following patterns from:
- [TanStack](https://tanstack.com/) - Feature plugins extend the core
- [NestJS](https://docs.nestjs.com/modules) - Module composition with DynamicModule
- [AWS SDK v3](https://aws.amazon.com/blogs/developer/modular-packages-in-aws-sdk-for-javascript/) - Modular clients with middleware/plugins
- [Zustand](https://zustand.docs.pmnd.rs/guides/slices-pattern) - Slices composition

### Architecture Overview

```
@hai3/framework
├── createHAI3()              ← Minimal core with plugin system
├── plugins/
│   ├── screensets()          ← Screenset registry + patterns
│   ├── themes()              ← Theme registry
│   ├── layout()              ← Layout domains (header, menu, footer, etc.)
│   ├── routing()             ← Route registry + URL sync
│   ├── effects()             ← Effect coordination system
│   ├── navigation()          ← Navigation actions
│   └── i18n()                ← i18nRegistry + setLanguage
├── presets/
│   ├── full()                ← All 7 plugins (default for hai3 create)
│   ├── minimal()             ← screensets + themes only
│   └── headless()            ← screensets only (external integration)
```

### Plugin Interface

```typescript
/**
 * HAI3Plugin interface - all plugins implement this contract.
 * Follows Liskov Substitution Principle - any plugin can be used interchangeably.
 */
interface HAI3Plugin<TConfig = unknown> {
  /** Unique plugin identifier */
  name: string;

  /** Other plugins this plugin requires */
  dependencies?: string[];

  /** Lifecycle: Called when plugin is registered */
  onRegister?(app: HAI3AppBuilder, config: TConfig): void;

  /** Lifecycle: Called after all plugins registered, before app starts */
  onInit?(app: HAI3App): void | Promise<void>;

  /** Lifecycle: Called when app is destroyed */
  onDestroy?(app: HAI3App): void;

  /** What this plugin provides to the app */
  provides?: {
    registries?: Record<string, unknown>;
    slices?: SliceObject[];
    effects?: EffectInitializer[];
    actions?: Record<string, Action>;
  };
}
```

### Plugin Examples

```typescript
// screensets plugin - minimal, just screenset orchestration
export const screensets = (config?: ScreensetsConfig): HAI3Plugin => ({
  name: 'screensets',
  dependencies: [],  // No other plugins required

  provides: {
    registries: { screensetRegistry: createScreensetRegistry() },
    slices: [screenSlice],
    // NOTE: Navigation actions are in navigation() plugin, not here
    // This allows headless users to provide their own navigation
  },

  onInit(app) {
    // Auto-discover screensets if configured
    if (config?.autoDiscover) {
      discoverScreensets(app.screensetRegistry);
    }
  },
});

// layout plugin - provides all layout domains (uses @hai3/state for events)
export const layout = (): HAI3Plugin => ({
  name: 'layout',
  dependencies: ['screensets'],  // Needs screensets for screen domain

  provides: {
    slices: [headerSlice, footerSlice, menuSlice, sidebarSlice, popupSlice, overlaySlice],
    effects: [initLayoutEffects],  // Effects subscribe to events from @hai3/state
  },

  onInit(app) {
    // Set up event subscriptions via eventBus from @hai3/state
    eventBus.on('layout/popup/requested', (payload) => {
      app.store.dispatch(popupActions.open(payload));
    });
  },
});

// themes plugin - theme management
export const themes = (): HAI3Plugin => ({
  name: 'themes',
  dependencies: [],

  provides: {
    registries: { themeRegistry: createThemeRegistry() },
  },

  onInit(app) {
    // Subscribe to theme change events from @hai3/state
    eventBus.on('theme/changed', (payload) => {
      app.themeRegistry.apply(payload.themeId);
    });
  },
});

// navigation plugin - navigation actions for HAI3 patterns
export const navigation = (): HAI3Plugin => ({
  name: 'navigation',
  dependencies: ['screensets', 'routing'],

  provides: {
    effects: [initNavigationEffects],  // URL sync, history, etc.
  },

  onInit(app) {
    // Subscribe to navigation events from @hai3/state
    eventBus.on('navigation/screen/navigated', (payload) => {
      app.store.dispatch(screenActions.setCurrentScreen(payload));
    });
  },
});
```

### Usage Patterns

#### 1. Full HAI3 Experience (Default)

```typescript
import { createHAI3App } from '@hai3/framework';

// Uses full() preset automatically - all plugins included
const app = createHAI3App();
```

#### 2. Using Presets

```typescript
import { createHAI3, presets } from '@hai3/framework';

// Headless preset - screensets only, for external platform integration
const app = createHAI3()
  .use(presets.headless())
  .build();

// Minimal preset - screensets + themes, no layout domains
const app = createHAI3()
  .use(presets.minimal())
  .build();
```

#### 3. Custom Composition

```typescript
import { createHAI3, screensets, themes, i18n } from '@hai3/framework';

const app = createHAI3()
  .use(screensets())
  .use(themes())
  .use(i18n())
  // NO layout() - they have their own menu/header
  .build();
```

#### 4. External Platform Integration

```typescript
// Company with their own platform - only needs screenset orchestration
import { createHAI3, screensets } from '@hai3/framework';
import { Provider } from 'react-redux';

// Minimal HAI3 setup
const hai3 = createHAI3()
  .use(screensets())
  .build();

// Their own menu component using HAI3 screensets
const TheirMenu: React.FC = () => {
  const allScreensets = hai3.screensetRegistry.getAll();

  return (
    <nav className="their-existing-menu">
      {allScreensets.map(ss => (
        <button key={ss.id} onClick={() => theirNavigate(ss.id)}>
          {ss.name}
        </button>
      ))}
    </nav>
  );
};

// Their screen renderer - injects HAI3 screens into their layout
const TheirScreenRenderer: React.FC<{ screensetId: string; screenId: string }> = ({
  screensetId,
  screenId
}) => {
  const screenset = hai3.screensetRegistry.get(screensetId);
  const screen = screenset.screens.find(s => s.id === screenId);
  const ScreenComponent = React.lazy(screen.loader);

  return (
    <Provider store={hai3.store}>
      <Suspense fallback={<TheirLoadingSpinner />}>
        <ScreenComponent />
      </Suspense>
    </Provider>
  );
};
```

### Presets Definition

```typescript
// presets/full.ts - All features (default)
export const full = (): HAI3Plugin[] => [
  screensets({ autoDiscover: true }),
  themes(),
  layout(),
  routing(),
  effects(),
  navigation(),
  i18n(),
];

// presets/minimal.ts - Screensets + themes, no layout
export const minimal = (): HAI3Plugin[] => [
  screensets({ autoDiscover: true }),
  themes(),
];

// presets/headless.ts - Screensets only, for external integration
export const headless = (): HAI3Plugin[] => [
  screensets({ autoDiscover: false }),  // Manual registration
];
```

### SOLID Compliance

| Principle | How Plugin Architecture Satisfies It |
|-----------|-------------------------------------|
| **S - Single Responsibility** | Each plugin has one job (screensets, themes, layout) |
| **O - Open/Closed** | Add features via new plugins, don't modify existing |
| **L - Liskov Substitution** | All plugins implement `HAI3Plugin` interface |
| **I - Interface Segregation** | Users import only plugins they need |
| **D - Dependency Inversion** | Core depends on `HAI3Plugin` interface, not implementations |

### Dependency Resolution

The plugin system resolves dependencies with clear, predictable behavior:

**Rule: Dependencies are ALWAYS auto-added when unambiguous.**

```typescript
const app = createHAI3()
  .use(layout())      // Declares dependency on 'screensets'
  .use(themes())      // No dependencies
  // screensets() is auto-added with DEFAULT config because layout() depends on it
  .build();
```

**Rule: Error is thrown when auto-resolution is ambiguous (requires config).**

```typescript
// This WORKS - screensets() with default config can be auto-added
const app = createHAI3()
  .use(navigation())  // Depends on 'screensets'
  .build();           // screensets() auto-added with default config

// This FAILS - if the user already has screensets with custom config
const app = createHAI3()
  .use(screensets({ autoDiscover: false }))  // Custom config
  .use(layout())
  // navigation() is NOT auto-added because screensets config is ambiguous
  .build();
// Warning: navigation() requires 'screensets' but it's already configured.
// Explicitly add navigation() if needed.
```

**Dependency Resolution Algorithm:**
1. Collect all plugins' declared dependencies
2. For each missing dependency:
   - If no existing plugin with that name → auto-add with default config
   - If plugin already exists with custom config → warn, don't duplicate
3. Throw error only if a required plugin cannot be instantiated

### Tree-Shaking Benefits

```typescript
// Only screensets - minimal bundle
import { createHAI3, screensets } from '@hai3/framework';
// Bundle: ~15KB (events + store + screensets)

// Full experience
import { createHAI3App } from '@hai3/framework';
// Bundle: ~45KB (all SDK packages + all plugins)
```

## CLI Scaffold Commands

### @hai3/uikit as Default UI Kit

`@hai3/uikit` is a **standalone npm package** (NOT part of SDK/framework layers). It's the default UI kit option at the CLI level:

```
┌─────────────────────────────────────────────────────────────┐
│                    @hai3/uikit (npm package)                │
│                                                             │
│  • Standalone React component library                       │
│  • Based on shadcn/ui + Radix UI + Tailwind                │
│  • NOT a dependency of SDK, framework, or react packages   │
│  • Default option when scaffolding layout                   │
│  • User can swap for any other UI kit                       │
└─────────────────────────────────────────────────────────────┘
```

| UI Kit | Status | Description |
|--------|--------|-------------|
| `@hai3/uikit` | **Default** | HAI3's component library, installed as npm dependency |
| `custom` | **Available** | No bundled UI kit, user provides own components |
| `shadcn` | **Future** | Generate with shadcn/ui imports |
| `mui` | **Future** | Generate with Material UI imports |

### Layout Scaffolding

```bash
# Generate layout with @hai3/uikit (default)
hai3 scaffold layout

# Future: support for other UI kits
# hai3 scaffold layout --ui-kit=shadcn
# hai3 scaffold layout --ui-kit=mui
# hai3 scaffold layout --ui-kit=custom
```

**What happens:**
1. CLI generates layout components in `src/layout/`
2. Generated code imports from `@hai3/uikit`
3. CLI adds `@hai3/uikit` to `package.json` dependencies (if not present)
4. User owns the generated code and can modify freely

**Generated files:**
```
src/layout/
├── Layout.tsx           # Main layout orchestrator
├── Header.tsx           # Header domain (imports from @hai3/uikit)
├── Footer.tsx           # Footer domain
├── Menu.tsx             # Menu domain
├── Sidebar.tsx          # Sidebar domain
├── Screen.tsx           # Screen domain (lazy loading)
├── Popup.tsx            # Popup domain
├── Overlay.tsx          # Overlay domain
├── api/                 # Application-specific API services (optional)
│   ├── AccountsApiService.ts  # User info fetching (example)
│   └── types.ts         # API response types
└── index.ts             # Barrel export
```

### Framework vs Template Boundary (Architectural Clarification)

**Principle:** The framework provides the **state contract and reducers**. Application-specific logic belongs in CLI templates.

| Component | Location | Rationale |
|-----------|----------|-----------|
| `HeaderState`, `HeaderUser` types | `@hai3/framework` | State contracts are framework concerns |
| `setUser`, `setLoading`, `clearUser` reducers | `@hai3/framework` | State management is framework concern |
| `AccountsApiService` class | CLI templates | Application-specific - not all apps have users |
| User fetching `useEffect` in Layout.tsx | CLI templates | Application logic - backends vary |
| API response types | CLI templates | API shapes vary between backends |

**Why this separation:**
1. **Framework is generic** - Not all applications have "accounts" or "users"
2. **API shapes vary** - Different backends have different user endpoint responses
3. **User owns the logic** - Can customize fetching, caching, error handling
4. **Optional feature** - Applications without users skip this entirely
5. **SOLID compliance** - Framework provides extension points, templates provide implementation

### Generated Code Example

```typescript
// Generated Header.tsx (default with @hai3/uikit)
import { Button, Avatar } from '@hai3/uikit';
import { useAppSelector } from '@hai3/react';
import type { RootState } from '@hai3/state';

export const Header: React.FC = () => {
  // State access via useAppSelector hook (no named selector functions)
  const headerState = useAppSelector((state: RootState) => state.layout.header);

  return (
    <header className="flex items-center justify-between p-4">
      <Avatar src={headerState.user?.avatar} />
      <Button variant="ghost">Settings</Button>
    </header>
  );
};
```

### Why Keep @hai3/uikit as Package? (Not CLI Template Like shadcn/ui)

Unlike shadcn/ui's approach where components are copied into user's codebase, @hai3/uikit remains a **standalone npm package** for strategic reasons:

| Reason | Explanation |
|--------|-------------|
| **AI Agent Boundary** | Prevents AI agents from modifying UI kit components during screenset implementation. AI works on business logic (screensets), UX designers maintain the UI kit. |
| **UX Designer Ownership** | The UI kit is maintained by the UX design team, not developers or AI. Clear separation of concerns. |
| **Consistent Updates** | Bug fixes and improvements delivered via npm updates. All projects benefit without regeneration. |
| **Flexibility for Companies** | Organizations can: use as-is, fork and customize, use shadcn/MUI instead, or build custom. |
| **Not Coupled to SDK** | @hai3/uikit has NO dependencies on SDK, framework, or react packages. It's just a CLI default. |

**The door is open**: Companies who want shadcn/ui approach can use `--ui-kit=shadcn` (future) or build their own custom UI kit.

## AI Infrastructure Architecture

> **⚠️ ARCHITECTURAL GAP:** See [proposal.md Issue 3](./proposal.md#issue-3-static-ai-commands-for-plugin-based-framework). The framework is plugin-based but AI commands/guidelines are static. Users who select specific plugins still get ALL guidelines. Phase 13.3 in tasks.md addresses this.

HAI3 separates AI tooling into two distinct domains, following [Nx's generator/executor pattern](https://nx.dev/docs/concepts/decisions/why-monorepos) and [Turborepo's internal vs published packages](https://turborepo.com/docs/core-concepts/internal-packages):

### Two Command Namespaces

| Namespace | Audience | Purpose |
|-----------|----------|---------|
| `hai3dev-*` | HAI3 framework developers | Internal monorepo development |
| `hai3-*` | HAI3-based project developers | User project development |

### HAI3 Monorepo Commands (Internal)

These commands are for HAI3 framework development only. They are **NEVER** shipped to user projects.

```
.claude/commands/           # HAI3 MONOREPO ONLY
├── hai3dev-publish.md      # Publish packages to npm
├── hai3dev-release.md      # Create release with changelog
├── hai3dev-update-guidelines.md  # Update AI source of truth
└── hai3dev-test-packages.md      # Test package changes
```

| Command | Purpose |
|---------|---------|
| `/hai3dev-publish` | Build and publish @hai3/* packages to npm |
| `/hai3dev-release` | Create version, changelog, and git tags |
| `/hai3dev-update-guidelines` | Update `.ai/rules/` source of truth |
| `/hai3dev-test-packages` | Run package integration tests |

### User Project Commands (Technical + Business Aliases)

**Screenset is a fundamental HAI3 concept** - keep technical commands, add business aliases for non-technical users.

Commands:
1. **Technical commands** use HAI3 terminology (screenset, screen, validate)
2. **Business aliases** provide simpler language (feature, page, check)
3. Call **HAI3 CLI** under the hood (ensures consistency)
4. Are **protected by validations** (ESLint, dependency-cruiser)
5. Are **configuration-aware** (only show relevant commands)

```
.claude/commands/           # USER PROJECT (generated by hai3 create)
├── hai3-new-screenset.md   # Technical: create screenset (fundamental HAI3 concept)
├── hai3-new-screen.md      # Technical: add screen to screenset
├── hai3-new-api-service.md # Technical: create API service
├── hai3-new-action.md      # Technical: create action
├── hai3-validate.md        # Technical: validate project
├── hai3-fix-violation.md   # Technical: fix violations
├── hai3-add-feature.md     # Alias: same as hai3-new-screenset (business term)
├── hai3-add-page.md        # Alias: same as hai3-new-screen (business term)
├── hai3-check.md           # Alias: same as hai3-validate (business term)
└── hai3-fix.md             # Alias: same as hai3-fix-violation (business term)
```

### Command Mapping (Technical + Business Aliases)

| Technical Command | Business Alias | CLI Command |
|-------------------|----------------|-------------|
| `/hai3-new-screenset` | `/hai3-add-feature` | `hai3 screenset create <name>` |
| `/hai3-new-screen` | `/hai3-add-page` | `hai3 screen add <name>` |
| `/hai3-new-api-service` | `/hai3-add-service` | `hai3 api-service create <name>` |
| `/hai3-new-action` | `/hai3-add-action` | `hai3 action create <name>` |
| `/hai3-validate` | `/hai3-check` | `hai3 validate` |
| `/hai3-fix-violation` | `/hai3-fix` | `hai3 fix` |

### CLI as Single Source of Truth

**All AI commands delegate to CLI.** This ensures:
- Consistent behavior across AI tools
- Built-in validation (protections)
- Single place to update logic

```markdown
# /hai3-add-feature

> Add a new feature module to your project.

## AI WORKFLOW (REQUIRED)
1. Ask: "What should this feature be called?" (e.g., billing, notifications)
2. Ask: "What category?" (drafts, mockups, production)
3. Run: `hai3 add feature <name> --category=<category>`
4. CLI handles scaffolding + validation automatically
5. Open created files for customization

## PROTECTIONS (CLI enforces these)
- ESLint validates naming conventions
- dependency-cruiser checks import rules
- arch:check validates structure
- If ANY validation fails, CLI shows error and suggests fix
```

### CLI Protection Flow

Every CLI command follows this flow:

```
User runs command (via AI or directly)
    │
    ▼
CLI executes scaffolding/generation
    │
    ▼
CLI automatically runs validations:
├── npm run lint (ESLint)
├── npm run type-check (TypeScript)
└── npm run arch:check (Architecture)
    │
    ├─── If PASS → Show success + next steps
    │
    └─── If FAIL → Show error + suggest `/hai3-fix`
```

### Configuration-Aware Command Generation

When `hai3 create my-app` runs, it generates commands based on project configuration:

```json
// package.json dependencies determine available commands
{
  "dependencies": {
    "@hai3/framework": "^1.0.0",  // Enables framework commands
    "@hai3/react": "^1.0.0"       // Enables react commands
  }
}
```

**Command availability by layer:**

| Layer | Installed Packages | Available Commands |
|-------|-------------------|-------------------|
| SDK | `@hai3/api` only | `/hai3-add-service` |
| Framework | `@hai3/framework` | SDK + `/hai3-add-feature`, `/hai3-add-action`, `/hai3-check`, `/hai3-fix` |
| React | `@hai3/react` | Framework + `/hai3-add-page`, `/hai3-add-component` |

### Multi-Tool Support

HAI3 supports 4 AI coding tools with **single source of truth**:

| Tool | Generated File | Commands Location |
|------|---------------|-------------------|
| Claude Code | `CLAUDE.md` | `.claude/commands/` |
| GitHub Copilot | `.github/copilot-instructions.md` | N/A (instructions only) |
| Cursor | `.cursor/rules/hai3.md` | N/A (rules only) |
| Windsurf | `.windsurf/rules/hai3.md` | N/A (rules only) |

**Note:** Only Claude Code supports custom commands. Other tools get rules/instructions only.

### Source of Truth Structure

```
HAI3 Monorepo:
.ai/
├── rules/                    # Source of truth for rules
│   ├── core.md              # Core patterns (all projects)
│   ├── state.md             # @hai3/state patterns (events + store)
│   ├── screensets.md        # @hai3/screensets patterns (contracts + registry)
│   ├── framework.md         # @hai3/framework patterns (plugins, layout state)
│   ├── react.md             # @hai3/react patterns
│   └── api.md               # @hai3/api patterns
│
├── commands/
│   ├── internal/            # hai3dev-* (monorepo only)
│   │   ├── hai3dev-publish.md
│   │   └── hai3dev-release.md
│   └── user/                # hai3-* (shipped to user projects)
│       ├── hai3-add-feature.md
│       ├── hai3-add-page.md
│       └── hai3-check.md
│
└── templates/               # Templates for generated files
    ├── CLAUDE.md.hbs
    ├── copilot-instructions.md.hbs
    └── cursor-rules.md.hbs

User Project (after hai3 create):
CLAUDE.md                    # Generated, includes project context
.github/copilot-instructions.md
.cursor/rules/hai3.md
.windsurf/rules/hai3.md
.claude/commands/            # Generated based on installed packages
    ├── hai3-new-screenset.md   # Technical command
    ├── hai3-new-screen.md      # Technical command
    ├── hai3-validate.md        # Technical command
    ├── hai3-add-feature.md     # Business alias
    └── hai3-check.md           # Business alias
```

### CLI Commands

```bash
# Technical commands (screenset is fundamental HAI3 concept)
hai3 screenset create <name>  # Create screenset (primary)
hai3 screen add <name>        # Add screen to screenset
hai3 api-service create <name> # Create API service
hai3 action create <name>     # Create action
hai3 validate                 # Run all validations
hai3 fix                      # Auto-fix violations

# Business-friendly aliases (for non-technical users)
hai3 add feature <name>       # Alias for: hai3 screenset create
hai3 add page <name>          # Alias for: hai3 screen add
hai3 add service <name>       # Alias for: hai3 api-service create
hai3 add action <name>        # Alias for: hai3 action create
hai3 check                    # Alias for: hai3 validate

# AI sync command
hai3 ai sync                  # Regenerate AI files from package config
hai3 update                   # Update packages + regenerate AI files
```

### Command Format (User-Friendly)

Commands are written for non-technical users:

```markdown
# /hai3-add-feature

> Add a new feature module to your project.

## What This Does
Creates a complete feature with its own pages, data, and styling.
Think of it like adding a new section to your app (e.g., "Billing", "Settings").

## AI WORKFLOW (REQUIRED)
1. Ask: "What should this feature be called?"
   - Examples: billing, notifications, user-settings
   - Use lowercase with hyphens for multi-word names

2. Ask: "Is this a draft, mockup, or production feature?"
   - Draft: For experimenting with ideas
   - Mockup: For showing to stakeholders
   - Production: For real users

3. Run the CLI command:
   ```bash
   hai3 add feature <name> --category=<category>
   ```

4. The CLI will:
   - Create all necessary files
   - Check for any problems
   - Show you what was created

5. Open the main file for customization

## If Something Goes Wrong
The CLI checks for problems automatically.
If it finds issues, run `/hai3-fix` to resolve them.
```

### Automated Validation (Promptfoo)

Commands are tested using [Promptfoo](https://www.promptfoo.dev/):

```
.ai/tests/
├── promptfoo.yaml           # Main config
├── commands/
│   ├── add-feature.test.yaml
│   ├── add-page.test.yaml
│   └── check.test.yaml
└── assertions/
    └── cli-patterns.yaml    # Reusable assertions
```

**Key test cases:**
1. Command correctly calls CLI with proper arguments
2. Business-friendly language is used (not technical jargon)
3. Error handling suggests `/hai3-fix`
4. Command stays under 500 words (user-friendly = concise)

### llms.txt for Discoverability

Each package also generates `llms.txt` following the [llms.txt standard](https://llmstxt.org/):

```markdown
# @hai3/state

> Complete Flux dataflow pattern for HAI3 SDK - event bus, store, and effects.

## Documentation

- [API Reference](https://hai3.dev/docs/flux/api): EventBus, Store, Slices
- [Flux Pattern](https://hai3.dev/docs/flux/pattern): Actions → Events → Effects → State

## Optional

- [Migration Guide](https://hai3.dev/docs/flux/migration)
```

## Layered Protection Architecture

> **⚠️ NEEDS RE-ASSESSMENT:** See [proposal.md Issue 2](./proposal.md#issue-2-eslintdepcruise-decomposition-misunderstanding). The per-package config approach conflates monorepo-level (SDK source code) protection with user-level (shipped to users) protection. Phase 13.2 in tasks.md addresses this.

Following industry best practices from [Turborepo](https://turborepo.com/docs/guides/tools/eslint), [Nx](https://nx.dev/docs/technologies/eslint), and [TanStack](https://tanstack.com/config/latest/docs/eslint), HAI3 uses a **hybrid configuration pattern**:

- **Shared config package** with layered configs (base → sdk → framework → react → screenset)
- **Per-package configs** that extend the appropriate layer
- **AI CLAUDE.md per package** referencing package-specific constraints

### ESLint Configuration Hierarchy

```
packages/
├── eslint-config/                        # @hai3/eslint-config (internal package)
│   ├── package.json
│   ├── base.js                           # L0: All packages (no-any, unused-imports, prefer-const)
│   ├── sdk.js                            # L1: SDK packages (extends base + no @hai3/*, no React)
│   ├── framework.js                      # L2: Framework (extends base + only SDK deps, no React)
│   ├── react.js                          # L3: React (extends base + only framework dep)
│   └── screenset.js                      # L4: User code (extends base + flux rules, isolation)
│
├── state/
│   └── eslint.config.js                  # extends sdk.js
├── screensets/
│   └── eslint.config.js                  # extends sdk.js
├── api/
│   └── eslint.config.js                  # extends sdk.js
├── i18n/
│   └── eslint.config.js                  # extends sdk.js
├── framework/
│   └── eslint.config.js                  # extends framework.js
├── react/
│   └── eslint.config.js                  # extends react.js
│
presets/
├── standalone/
│   └── configs/eslint.config.js          # extends screenset.js (user projects)
└── monorepo/
    └── configs/eslint.config.js          # extends standalone + monorepo extras
```

### ESLint Layer Definitions

```javascript
// packages/eslint-config/base.js - L0: Universal rules for ALL code
export const baseConfig = [
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    rules: {
      '@typescript-eslint/no-explicit-any': 'error',
      'unused-imports/no-unused-imports': 'error',
      'prefer-const': 'error',
      // ... other universal rules
    },
  },
];

// packages/eslint-config/sdk.js - L1: SDK packages (zero @hai3 deps, no React)
export const sdkConfig = [
  ...baseConfig,
  {
    rules: {
      'no-restricted-imports': ['error', {
        patterns: [
          { group: ['@hai3/*'], message: 'SDK packages cannot import other @hai3 packages' },
          { group: ['react', 'react-dom', 'react/*'], message: 'SDK packages cannot import React' },
        ],
      }],
    },
  },
];

// packages/eslint-config/framework.js - L2: Framework (only SDK deps, no React)
export const frameworkConfig = [
  ...baseConfig,
  {
    rules: {
      'no-restricted-imports': ['error', {
        patterns: [
          { group: ['@hai3/react', '@hai3/uikit', '@hai3/uikit-contracts', '@hai3/uicore'],
            message: 'Framework can only import SDK packages' },
          { group: ['react', 'react-dom', 'react/*'], message: 'Framework cannot import React' },
        ],
      }],
    },
  },
];

// packages/eslint-config/react.js - L3: React adapter (only framework dep)
export const reactConfig = [
  ...baseConfig,
  {
    rules: {
      'no-restricted-imports': ['error', {
        patterns: [
          { group: ['@hai3/state', '@hai3/screensets', '@hai3/api', '@hai3/i18n'],
            message: 'React package imports SDK via framework re-exports' },
          { group: ['@hai3/uikit-contracts'], message: 'uikit-contracts is deprecated' },
        ],
      }],
    },
  },
];

// packages/eslint-config/screenset.js - L4: User code (flux, isolation, all existing rules)
export const screensetConfig = [
  ...baseConfig,
  // All existing flux architecture rules from presets/standalone/
  // Screenset isolation rules
  // Domain-based architecture rules (local plugin)
  // Actions/Effects/Components restrictions
];
```

### Dependency Cruiser Configuration Hierarchy

```
packages/
├── depcruise-config/                     # @hai3/depcruise-config (internal package)
│   ├── package.json
│   ├── base.cjs                          # L0: Universal (no-circular, no-orphans)
│   ├── sdk.cjs                           # L1: SDK (no @hai3 deps)
│   ├── framework.cjs                     # L2: Framework (only SDK deps)
│   ├── react.cjs                         # L3: React (only framework dep)
│   └── screenset.cjs                     # L4: User code (screenset isolation, flux)
│
├── state/
│   └── .dependency-cruiser.cjs           # extends sdk.cjs
├── screensets/
│   └── .dependency-cruiser.cjs           # extends sdk.cjs
├── api/
│   └── .dependency-cruiser.cjs           # extends sdk.cjs
├── i18n/
│   └── .dependency-cruiser.cjs           # extends sdk.cjs
├── framework/
│   └── .dependency-cruiser.cjs           # extends framework.cjs
├── react/
│   └── .dependency-cruiser.cjs           # extends react.cjs
│
presets/
├── standalone/
│   └── configs/.dependency-cruiser.cjs   # extends screenset.cjs (user projects)
```

### Dependency Cruiser Layer Definitions

```javascript
// packages/depcruise-config/base.cjs - L0: Universal rules
module.exports = {
  forbidden: [
    { name: 'no-circular', severity: 'error', from: {}, to: { circular: true } },
    { name: 'no-orphans', severity: 'warn', from: { orphan: true }, to: {} },
  ],
};

// packages/depcruise-config/sdk.cjs - L1: SDK packages
const base = require('./base.cjs');
module.exports = {
  forbidden: [
    ...base.forbidden,
    {
      name: 'sdk-no-hai3-imports',
      severity: 'error',
      from: { path: '^packages/(state|screensets|api|i18n)/src' },
      to: { path: 'node_modules/@hai3/' },
      comment: 'SDK packages must have ZERO @hai3 dependencies',
    },
    {
      name: 'sdk-no-react',
      severity: 'error',
      from: { path: '^packages/(state|screensets|api|i18n)/src' },
      to: { path: 'node_modules/react' },
      comment: 'SDK packages cannot import React',
    },
  ],
};

// packages/depcruise-config/framework.cjs - L2: Framework
const base = require('./base.cjs');
module.exports = {
  forbidden: [
    ...base.forbidden,
    {
      name: 'framework-only-sdk-deps',
      severity: 'error',
      from: { path: '^packages/framework/src' },
      to: { path: 'node_modules/@hai3/(react|uikit|uikit-contracts|uicore)' },
      comment: 'Framework can only import SDK packages',
    },
    {
      name: 'framework-no-react',
      severity: 'error',
      from: { path: '^packages/framework/src' },
      to: { path: 'node_modules/react' },
      comment: 'Framework cannot import React',
    },
  ],
};

// packages/depcruise-config/react.cjs - L3: React adapter
const base = require('./base.cjs');
module.exports = {
  forbidden: [
    ...base.forbidden,
    {
      name: 'react-only-framework-dep',
      severity: 'error',
      from: { path: '^packages/react/src' },
      to: { path: 'node_modules/@hai3/(state|screensets|api|i18n)' },
      comment: 'React package imports SDK via framework, not directly',
    },
    {
      name: 'react-no-uikit-contracts',
      severity: 'error',
      from: { path: '^packages/react/src' },
      to: { path: 'node_modules/@hai3/uikit-contracts' },
      comment: 'uikit-contracts is deprecated',
    },
  ],
};

// packages/depcruise-config/screenset.cjs - L4: User code
const base = require('./base.cjs');
module.exports = {
  forbidden: [
    ...base.forbidden,
    // All existing rules from presets/standalone/configs/.dependency-cruiser.cjs
    // - no-cross-screenset-imports
    // - no-circular-screenset-deps
    // - flux-no-actions-in-effects-folder
    // - flux-no-effects-in-actions-folder
  ],
};
```

### Per-Package CLAUDE.md Integration

Each package's CLAUDE.md references its protection constraints:

```markdown
# @hai3/state

## Protection Layer: SDK (L1)

This package is at the SDK layer with strict constraints:

**ESLint Rules** (from @hai3/eslint-config/sdk.js):
- ❌ Cannot import any @hai3/* packages
- ❌ Cannot import react or react-dom
- ✅ Must follow base rules (no-any, unused-imports)

**Dependency Cruiser Rules** (from @hai3/depcruise-config/sdk.cjs):
- ❌ sdk-no-hai3-imports: Zero @hai3 dependencies
- ❌ sdk-no-react: No React dependencies

**Verify with:**
\`\`\`bash
npm run lint --workspace=@hai3/state
npm run arch:deps --workspace=@hai3/state
\`\`\`
```

### Verification Commands

```bash
# Verify single package
npm run lint --workspace=@hai3/state
npm run arch:deps --workspace=@hai3/state

# Verify layer (all SDK packages)
npm run lint:sdk      # Runs lint on flux, layout, api, i18n
npm run arch:sdk      # Runs arch:deps on SDK packages

# Verify all packages
npm run lint          # All packages
npm run arch:deps     # All packages
npm run arch:check    # Full architecture validation
```

### Layer Inheritance Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│ L0: base.js / base.cjs                                              │
│ • no-explicit-any, unused-imports, prefer-const                     │
│ • no-circular, no-orphans                                           │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
│ L1: sdk.js        │   │ L2: framework.js  │   │ L4: screenset.js  │
│ • no @hai3/*      │   │ • only SDK deps   │   │ • flux rules      │
│ • no React        │   │ • no React        │   │ • isolation       │
│                   │   │                   │   │ • domain rules    │
│ Used by:          │   │ Used by:          │   │                   │
│ state, screensets │   │ framework         │   │ Used by:          │
│ api, i18n         │   │                   │   │ user projects     │
└───────────────────┘   └─────────┬─────────┘   └───────────────────┘
                                  │
                                  ▼
                        ┌───────────────────┐
                        │ L3: react.js      │
                        │ • only framework  │
                        │ • no direct SDK   │
                        │                   │
                        │ Used by:          │
                        │ react             │
                        └───────────────────┘
```

### Protection Coverage Matrix

| Rule Category | SDK | Framework | React | User Code |
|--------------|-----|-----------|-------|-----------|
| **Base Rules** | ✅ | ✅ | ✅ | ✅ |
| no-explicit-any | ✅ | ✅ | ✅ | ✅ |
| unused-imports | ✅ | ✅ | ✅ | ✅ |
| no-circular | ✅ | ✅ | ✅ | ✅ |
| **Layer Rules** | | | | |
| no @hai3/* imports | ✅ | - | - | - |
| only SDK imports | - | ✅ | - | - |
| only framework imports | - | - | ✅ | - |
| no React | ✅ | ✅ | - | - |
| **Flux Rules** | | | | |
| screenset isolation | - | - | - | ✅ |
| actions→events→effects | - | - | - | ✅ |
| no direct dispatch | - | - | - | ✅ |
| **Domain Rules** | | | | |
| domain-event-format | - | - | - | ✅ |
| no-barrel-exports | - | - | - | ✅ |
| no-coordinator-effects | - | - | - | ✅ |

## Migration Strategy

### Phase 1: Protections (TDD)
1. Update ESLint rules for new package boundaries
2. Update dependency-cruiser for flat SDK enforcement
3. Add architecture tests for SOLID compliance
4. Update AI guidelines in `.ai/` folder

### Phase 2: Types & Interfaces
1. Define all package interfaces
2. Ensure full type coverage
3. Set up module augmentation patterns

### Phase 3: SDK Packages
1. Create @hai3/state (complete dataflow pattern: events + store + effects)
2. Create @hai3/screensets (contracts + registry singleton)
3. Create @hai3/api (standalone)
4. Create @hai3/i18n (standalone)

### Phase 4: Framework & React
1. Create @hai3/framework (wires SDK)
2. Create @hai3/react (React bindings, no layout)

### Phase 5: CLI Templates
1. Add `hai3 scaffold layout` command
2. Create templates for @hai3/uikit (default) and custom (no uikit)
3. Update existing `hai3 create` to use new architecture

### Phase 6: Deprecation & Migration (CRITICAL)

**6.0 State Structure Migration**
- Current: `state.uicore.header`, `state.uicore.menu`, etc. (nested under `uicore` key)
- New: `state.layout.header`, etc. - managed by `@hai3/framework` (owns layout slices)
- Requires: Migration helpers, deprecation warnings (state access via useAppSelector hook)

**6.1 Layout Components Migration**
- Current: `<Layout>`, `<Header>`, `<Menu>`, etc. in `@hai3/uicore`
- New: CLI-generated in user's `src/layout/`
- Backward compat: Re-export wrapper that uses CLI-generated components

**6.2 uikit-contracts Migration (30+ files)**
- Types used across uicore, uikit, studio, CLI templates
- Move types to appropriate new packages
- Re-export from deprecated contracts package

**6.3 Actions Refactoring**
- Current: Actions call registries (not pure)
- New: Actions only emit events, effects handle validation
- Example: `navigateToScreen` currently calls `routeRegistry.hasScreen()`

**6.4 @hai3/uicore Deprecation**
1. Update to re-export from framework + react
2. Maintain all existing exports for backward compat
3. Add deprecation warnings in development

## Risks / Trade-offs

### Risk 1: Many Packages to Maintain
- **Risk:** 7 new packages vs 3 current
- **Mitigation:** Clear boundaries, automated testing, monorepo tooling

### Risk 2: CLI Template Updates
- **Risk:** Users don't get updates automatically
- **Mitigation:** `hai3 update layout` command, clear versioning

### Risk 3: Module Augmentation Complexity
- **Risk:** Types across packages can be confusing
- **Mitigation:** Excellent documentation, examples in each package

### Risk 4: Breaking Existing Apps
- **Risk:** Current apps stop working
- **Mitigation:** @hai3/uicore re-exports maintain 100% backward compat

### Risk 5: State Structure Migration
- **Risk:** Code using `state.uicore.X` path breaks
- **Mitigation:** Migration helpers to map old paths, gradual migration guide

### Risk 6: uikit-contracts Migration Scope
- **Risk:** 30+ files across 4 packages need updates
- **Mitigation:** Deprecation re-exports, gradual migration, clear ownership per type

## Critical Assessment

### What This Approach Gets Right

| Aspect | Industry Alignment | Evidence |
|--------|-------------------|----------|
| **Flat SDK packages** | TanStack, shadcn/ui | Zero inter-dependencies enables tree-shaking, independent versioning |
| **CLI-generated layout** | shadcn/ui, Tailwind | User owns code, no runtime abstraction layer overhead |
| **Single source of truth for AI** | Anthropic recommendations | Avoids drift between tool-specific files |
| **Promptfoo for validation** | Industry standard | Used by OpenAI, Anthropic partners for eval |
| **Module augmentation** | TypeScript best practice | Used by Redux Toolkit, React Query |
| **Event-driven architecture** | Redux, RxJS patterns | Proven for loose coupling |

### Potential Concerns

| Concern | Mitigation | Risk Level |
|---------|-----------|------------|
| **7 packages to maintain** | Monorepo tooling, strict boundaries, automated testing | Medium |
| **Users won't update CLI templates** | `hai3 update layout` command, clear versioning in comments | Low |
| **Promptfoo adds CI cost** | Use caching, run on .ai/ changes only, use smaller models for tests | Low |
| **AI guidelines may drift per tool** | Single source + sync command enforces consistency | Low |
| **Breaking changes harder across packages** | Semantic versioning, deprecation warnings, re-export shims | Medium |

### Comparison with Alternatives

| Alternative | Pros | Cons | Why Not Chosen |
|------------|------|------|----------------|
| **Keep monolithic uicore** | Simpler, less packages | SOLID violations, poor tree-shaking | Doesn't scale |
| **Use Turborepo/Nx** | Better build caching | Added complexity, learning curve | Current npm workspaces sufficient |
| **Abstract UI kit interface** | Swap UI kits easily | Runtime overhead, type complexity | CLI templates simpler |
| **Split to micro-packages** | Maximum granularity | Too many packages to manage | 7 is the right balance |

### Industry Research Summary

Based on analysis of TanStack, shadcn/ui, Stripe SDK, Radix UI:

1. **Package granularity**: 5-7 packages is optimal. TanStack has ~6 core packages, shadcn/ui generates per-component.

2. **AI guidelines format**: No industry standard yet. CLAUDE.md is emerging for Claude, llms.txt for general LLMs. Our single-source approach is forward-thinking.

3. **Prompt testing**: Promptfoo is the most mature option. Alternatives (LangSmith, Braintrust) are more opinionated/expensive.

4. **Template over runtime**: shadcn/ui proved users prefer owning code over abstraction layers. 5x adoption vs traditional component libraries.

### Recommended Improvements

1. **Add `@hai3/types` package** - Shared primitives (ScreensetId, ScreenId) prevent duplication
2. **Template versioning header** - Generated files should include version for `hai3 update layout` to work
3. **Prompt regression baseline** - Store golden outputs for comparison, not just pass/fail
4. **Consider Biome over ESLint** - Faster, but less mature plugin ecosystem

## Open Questions

1. **Should SDK packages have a shared types package?** Currently each defines own types. Could have `@hai3/types` for shared primitives.

2. **How to version CLI templates?** When user runs `hai3 scaffold layout`, should it check for updates?

3. **Should @hai3/framework be split per concern?** Could have `@hai3/screensets`, `@hai3/themes`, `@hai3/routing` instead.

4. **Should we use smaller models (Haiku) for prompt tests?** Reduces cost but may miss nuanced issues.

5. **Should prompt tests run on every PR or just .ai/ changes?** Trade-off between safety and CI cost.
