# ADR-005: Frontend State Management Approach

## Status

**Accepted** - 2026-01-07

## Context

Luminote's frontend needs to manage various types of state:

1. **Configuration State**: Provider, model, target language, API key
1. **Content State**: Extracted content, translated blocks, block mappings
1. **UI State**: Loading states, error states, modal visibility, active pane
1. **Translation State**: Current translation job, progress, streaming updates
1. **History State**: Recent visits, cached content
1. **User Preferences**: Pane width, theme, language preferences

Key requirements:

- State updates should be reactive and efficient
- Complex state (like streaming translations) needs careful management
- State should persist across page reloads where appropriate
- State should be easily testable
- State management should work well with SvelteKit's SSR
- GitHub Copilot should be able to follow patterns easily

We need to choose a state management approach that:

- Leverages Svelte's built-in reactivity
- Avoids unnecessary complexity
- Provides clear patterns for common scenarios
- Works well with TypeScript
- Supports both local and persistent state

## Decision

We will use **Svelte Stores** with a structured approach based on state type,
avoiding external state management libraries.

### State Management Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Svelte Components                        │
│  (Subscribe to stores, dispatch actions)                   │
├─────────────────────────────────────────────────────────────┤
│                      Store Layer                            │
│  ┌──────────────┬──────────────┬──────────────────────┐   │
│  │ Config Store │ Content Store│ Translation Store    │   │
│  │ (Writable)   │ (Derived)    │ (Custom Store)       │   │
│  └──────────────┴──────────────┴──────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                   Storage Adapters                          │
│  (localStorage, IndexedDB, sessionStorage)                 │
├─────────────────────────────────────────────────────────────┤
│                     API Layer                               │
│  (Backend communication)                                   │
└─────────────────────────────────────────────────────────────┘
```

### Store Types by Use Case

| State Type    | Store Type     | Persistence      | Example             |
| ------------- | -------------- | ---------------- | ------------------- |
| Configuration | Writable Store | localStorage     | Provider, language  |
| API Keys      | Writable Store | sessionStorage   | API key (opt-in)    |
| UI State      | Writable Store | None             | Modal open, loading |
| Content       | Writable Store | None (ephemeral) | Extracted content   |
| Translation   | Custom Store   | None             | Streaming state     |
| Derived Data  | Derived Store  | None             | Filtered blocks     |
| History       | Writable Store | IndexedDB        | Past translations   |

### Store Implementation Patterns

#### 1. Simple Writable Store

```typescript
// src/lib/stores/ui.ts

import { writable } from 'svelte/store';

interface UIState {
  isConfigModalOpen: boolean;
  isHistoryPanelOpen: boolean;
  activePane: 'source' | 'translation';
  isDraggingDivider: boolean;
}

const initialState: UIState = {
  isConfigModalOpen: false,
  isHistoryPanelOpen: false,
  activePane: 'translation',
  isDraggingDivider: false,
};

export const uiState = writable<UIState>(initialState);

// Helper functions
export const openConfigModal = () =>
  uiState.update((state) => ({ ...state, isConfigModalOpen: true }));

export const closeConfigModal = () =>
  uiState.update((state) => ({ ...state, isConfigModalOpen: false }));

export const setActivePane = (pane: 'source' | 'translation') =>
  uiState.update((state) => ({ ...state, activePane: pane }));
```

#### 2. Persistent Writable Store

```typescript
// src/lib/stores/config.ts

import { writable } from 'svelte/store';
import type { Writable } from 'svelte/store';

interface ConfigState {
  provider: string;
  model: string;
  target_language: string;
  api_key: string;
}

const DEFAULT_CONFIG: ConfigState = {
  provider: 'openai',
  model: 'gpt-4',
  target_language: 'en',
  api_key: '',
};

function createConfigStore(): Writable<ConfigState> & {
  setProvider: (provider: string) => void;
  setModel: (model: string) => void;
  setTargetLanguage: (language: string) => void;
  setAPIKey: (key: string) => void;
  reset: () => void;
} {
  // Load initial state from localStorage
  const loadState = (): ConfigState => {
    if (typeof window === 'undefined') return DEFAULT_CONFIG;

    const stored = localStorage.getItem('luminote_config');
    if (!stored) return DEFAULT_CONFIG;

    try {
      const parsed = JSON.parse(stored);
      // Never load API key from localStorage
      return { ...DEFAULT_CONFIG, ...parsed, api_key: '' };
    } catch {
      return DEFAULT_CONFIG;
    }
  };

  const { subscribe, set, update } = writable<ConfigState>(loadState());

  // Persist to localStorage (excluding API key)
  const persist = (state: ConfigState) => {
    if (typeof window === 'undefined') return;
    const { api_key, ...persistable } = state;
    localStorage.setItem('luminote_config', JSON.stringify(persistable));
  };

  return {
    subscribe,
    set: (value: ConfigState) => {
      set(value);
      persist(value);
    },
    update: (updater: (state: ConfigState) => ConfigState) => {
      update((state) => {
        const newState = updater(state);
        persist(newState);
        return newState;
      });
    },
    setProvider: (provider: string) => {
      update((state) => {
        const newState = { ...state, provider };
        persist(newState);
        return newState;
      });
    },
    setModel: (model: string) => {
      update((state) => {
        const newState = { ...state, model };
        persist(newState);
        return newState;
      });
    },
    setTargetLanguage: (target_language: string) => {
      update((state) => {
        const newState = { ...state, target_language };
        persist(newState);
        return newState;
      });
    },
    setAPIKey: (api_key: string) => {
      update((state) => ({ ...state, api_key }));
      // Note: API key is NOT persisted
    },
    reset: () => {
      set(DEFAULT_CONFIG);
      if (typeof window !== 'undefined') {
        localStorage.removeItem('luminote_config');
      }
    },
  };
}

export const configStore = createConfigStore();
```

#### 3. Derived Store

```typescript
// src/lib/stores/content.ts

import { writable, derived } from 'svelte/store';
import type { Readable } from 'svelte/store';

export interface ContentBlock {
  id: string;
  type: 'paragraph' | 'heading' | 'list' | 'quote' | 'code';
  text: string;
  level?: number;
  metadata?: Record<string, any>;
}

export interface ContentState {
  sourceBlocks: ContentBlock[];
  translatedBlocks: ContentBlock[];
  blockMapping: Record<string, string>; // source id -> translated id
}

export const contentState = writable<ContentState>({
  sourceBlocks: [],
  translatedBlocks: [],
  blockMapping: {},
});

// Derived store: blocks by type
export const headingBlocks: Readable<ContentBlock[]> = derived(
  contentState,
  ($state) => $state.sourceBlocks.filter((block) => block.type === 'heading')
);

// Derived store: translation progress
export const translationProgress: Readable<number> = derived(
  contentState,
  ($state) => {
    if ($state.sourceBlocks.length === 0) return 0;
    return ($state.translatedBlocks.length / $state.sourceBlocks.length) * 100;
  }
);

// Derived store: untranslated blocks
export const untranslatedBlocks: Readable<ContentBlock[]> = derived(
  contentState,
  ($state) => {
    const translatedIds = new Set(Object.keys($state.blockMapping));
    return $state.sourceBlocks.filter((block) => !translatedIds.has(block.id));
  }
);
```

#### 4. Custom Async Store (for streaming)

```typescript
// src/lib/stores/translation.ts

import { writable } from 'svelte/store';
import type { Readable } from 'svelte/store';
import { streamTranslation } from '$lib/utils/translation-stream';
import type { TranslationRequest, BlockTranslation } from '$lib/types';

interface TranslationState {
  isTranslating: boolean;
  currentBlock: number;
  totalBlocks: number;
  error: string | null;
  results: BlockTranslation[];
}

function createTranslationStore() {
  const { subscribe, set, update } = writable<TranslationState>({
    isTranslating: false,
    currentBlock: 0,
    totalBlocks: 0,
    error: null,
    results: [],
  });

  return {
    subscribe,
    startTranslation: async (request: TranslationRequest) => {
      set({
        isTranslating: true,
        currentBlock: 0,
        totalBlocks: request.content_blocks.length,
        error: null,
        results: [],
      });

      try {
        await streamTranslation(
          request,
          // onBlock
          (translation: BlockTranslation) => {
            update((state) => ({
              ...state,
              currentBlock: state.currentBlock + 1,
              results: [...state.results, translation],
            }));
          },
          // onError
          (error: Error) => {
            update((state) => ({
              ...state,
              error: error.message,
              isTranslating: false,
            }));
          },
          // onComplete
          () => {
            update((state) => ({
              ...state,
              isTranslating: false,
            }));
          }
        );
      } catch (error) {
        update((state) => ({
          ...state,
          error: error instanceof Error ? error.message : 'Unknown error',
          isTranslating: false,
        }));
      }
    },
    reset: () => {
      set({
        isTranslating: false,
        currentBlock: 0,
        totalBlocks: 0,
        error: null,
        results: [],
      });
    },
  };
}

export const translationStore = createTranslationStore();
```

### Component Usage Patterns

#### 1. Subscribe in Component

```svelte
<!-- src/lib/components/ConfigPanel.svelte -->
<script lang="ts">
  import { configStore } from '$lib/stores/config';

  // Auto-subscribe with $
  $: provider = $configStore.provider;
  $: model = $configStore.model;

  function handleProviderChange(newProvider: string) {
    configStore.setProvider(newProvider);
  }
</script>

<div>
  <select value={provider} on:change={(e) => handleProviderChange(e.target.value)}>
    <option value="openai">OpenAI</option>
    <option value="anthropic">Anthropic</option>
  </select>
</div>
```

#### 2. Derived Values

```svelte
<!-- src/lib/components/TranslationProgress.svelte -->
<script lang="ts">
  import { translationProgress } from '$lib/stores/content';
</script>

<div class="progress-bar">
  <div class="progress-fill" style="width: {$translationProgress}%"></div>
  <span>{$translationProgress.toFixed(0)}%</span>
</div>
```

#### 3. Async Actions

```svelte
<!-- src/lib/components/TranslateButton.svelte -->
<script lang="ts">
  import { translationStore } from '$lib/stores/translation';
  import { configStore } from '$lib/stores/config';

  async function handleTranslate() {
    await translationStore.startTranslation({
      content_blocks: sourceBlocks,
      target_language: $configStore.target_language,
      provider: $configStore.provider,
      model: $configStore.model,
      api_key: $configStore.api_key,
    });
  }
</script>

<button
  on:click={handleTranslate}
  disabled={$translationStore.isTranslating}
>
  {#if $translationStore.isTranslating}
    Translating... ({$translationStore.currentBlock}/{$translationStore.totalBlocks})
  {:else}
    Translate
  {/if}
</button>
```

## Consequences

### Positive

- **Built-in Reactivity**: Leverages Svelte's strength
- **Simple API**: Minimal learning curve
- **Type-Safe**: Works well with TypeScript
- **Flexible**: Custom stores for complex state
- **Testable**: Stores are just functions
- **No Dependencies**: No external state management library
- **SSR-Compatible**: Works with SvelteKit's SSR

### Negative

- **Manual Persistence**: Need to handle localStorage manually
- **No Time-Travel Debugging**: Unlike Redux DevTools
- **No Middleware**: Need custom solutions for side effects
- **Limited Tooling**: Fewer debugging tools than Redux/Zustand

### Trade-offs

- Chose Svelte stores over Redux for simplicity and better Svelte integration
- Chose manual persistence over automatic for explicit control
- Chose custom stores over library stores for flexibility
- Accepted lack of time-travel debugging for simpler codebase

## Alternatives Considered

### 1. Redux / Redux Toolkit

**Pros:**

- Predictable state updates
- Excellent DevTools
- Time-travel debugging
- Large ecosystem

**Cons:**

- Boilerplate heavy
- Not idiomatic for Svelte
- Less reactive
- Harder for Copilot to generate

**Verdict:** Rejected - Overkill for our use case, not Svelte-native

### 2. Zustand

**Pros:**

- Simple API
- TypeScript support
- Minimal boilerplate
- Good with React (not Svelte)

**Cons:**

- Not designed for Svelte
- Doesn't leverage Svelte reactivity
- Additional dependency

**Verdict:** Rejected - Not Svelte-native

### 3. XState

**Pros:**

- Explicit state machines
- Visualizable
- Handles complex flows

**Cons:**

- Steeper learning curve
- Verbose for simple state
- Overkill for most of our state

**Verdict:** Rejected - Too complex for our needs

### 4. Context API (SvelteKit's Context)

**Pros:**

- Built into Svelte
- Good for dependency injection
- Component-scoped

**Cons:**

- Not reactive by default
- Limited to component tree
- Not persistent

**Verdict:** Rejected - Not suitable for application-wide state

### 5. Global Variables

**Pros:**

- Simplest possible
- No abstraction

**Cons:**

- Not reactive
- No change tracking
- Hard to test
- No persistence

**Verdict:** Rejected - Doesn't leverage Svelte reactivity

## Implementation Notes

### For GitHub Copilot

When creating stores:

1. **Use factory pattern for complex stores:**

```typescript
function createMyStore() {
  const { subscribe, set, update } = writable(initialState);

  return {
    subscribe,
    // Custom methods
    doSomething: () => update(state => ...),
  };
}

export const myStore = createMyStore();
```

1. **Always type your stores:**

```typescript
interface MyState {
  field: string;
}

export const myStore: Writable<MyState> = writable({ field: '' });
```

1. **Separate concerns:**

```typescript
// Good: One store per domain
export const configStore = ...;
export const contentStore = ...;
export const translationStore = ...;

// Bad: One giant store
export const appStore = ...;
```

1. **Use derived stores for computed values:**

```typescript
// Good
export const completedBlocks = derived(
  translationStore,
  $store => $store.results.length
);

// Bad: Recompute in every component
```

### Testing Stores

```typescript
// tests/stores/config.test.ts

import { get } from 'svelte/store';
import { configStore } from '$lib/stores/config';

describe('configStore', () => {
  beforeEach(() => {
    configStore.reset();
  });

  test('sets provider', () => {
    configStore.setProvider('anthropic');
    const config = get(configStore);
    expect(config.provider).toBe('anthropic');
  });

  test('persists to localStorage', () => {
    configStore.setProvider('anthropic');
    const stored = localStorage.getItem('luminote_config');
    expect(stored).toContain('anthropic');
  });

  test('does not persist API key', () => {
    configStore.setAPIKey('secret');
    const stored = localStorage.getItem('luminote_config');
    expect(stored).not.toContain('secret');
  });
});
```

### Store Organization

```
src/lib/stores/
├── index.ts          # Re-export all stores
├── config.ts         # Configuration state
├── content.ts        # Content and blocks
├── translation.ts    # Translation state
├── ui.ts            # UI state
├── history.ts       # History state
└── preferences.ts   # User preferences
```

## Performance Considerations

- **Avoid unnecessary subscriptions**: Use derived stores
- **Batch updates**: Update store once, not multiple times
- **Unsubscribe when done**: Let Svelte handle auto-unsubscribe
- **Memoize expensive computations**: Use derived stores
- **Lazy load stores**: Don't import all stores everywhere

## References

- [Svelte Stores Documentation](https://svelte.dev/docs/svelte-store)
- [SvelteKit State Management](https://kit.svelte.dev/docs/state-management)
- [Feature Specifications](../feature-specifications.md)

## Changelog

- 2026-01-07: Initial version accepted
