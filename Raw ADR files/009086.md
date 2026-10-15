---
title: "ADR 00Z – Front-End Framework Selection for Astro Integration"
date: 2025-10-08
status: Proposed
deciders: [Platform/DevEx]
tags: [frontend, astro, nx, tailwind, eslint, solid, preact, react, vue, qwik, angular, alpine, ripple]
---

# Alternatives Considered
| Framework     | Rejected Because                                                     |
| ------------- | -------------------------------------------------------------------- |
| **React**     | Overly heavy runtime; more boilerplate than Solid/Preact.            |
| **Vue 3**     | Excellent DX but larger syntax surface and slower islands hydration. |
| **Angular**   | Overkill for Astro component islands.                                |
| **Qwik**      | Early-stage; incomplete test ecosystem.                              |
| **Ripple**    | Not production-ready.                                                |
| **Alpine.js** | Limited feature set for complex UI logic.                            |

# Context

We need to select a **front-end framework** to integrate with **Astro**, **TailwindCSS**, **ESLint**, and **Nx** for building interactive "islands" within a web application.

The framework should balance:
1. **Ecosystem Stability** — actively maintained, well-documented, and community-supported.  
2. **Developer Ergonomics** — concise syntax and minimal lines of code to build arbitrary UI components.  
3. **Testing Framework Support** — mature support for Vitest, Jest, Playwright, and Testing Library.  

This decision assumes Astro will handle routing and page rendering; the chosen framework will power **client-side interactive components** only.

---

# Decision

Adopt **Solid.js** as the primary front-end framework for Astro integrations, with **Preact** as a secondary lightweight alternative for extremely small, performance-critical components.

---

# Rationale

### Why Solid.js
- **Modern reactive model** with fine-grained reactivity—no virtual DOM overhead.
- **Concise syntax** similar to React but requiring fewer lines of code for comparable components.
- **Astro-native integration** via official `@astrojs/solid-js` adapter.
- **Excellent performance** and ergonomics with strong TypeScript and ESLint support.
- **Works seamlessly in Nx**, using the `@nx/solid` plugin or community presets.
- **Testing support** using Vitest + Testing Library (`@solidjs/testing-library`) and Playwright.

### Why not React
- While React remains the ecosystem leader, its runtime and JSX abstraction are heavier than needed for Astro islands.
- Solid achieves equivalent DX and JSX familiarity while producing smaller bundles and simpler reactivity without hooks overhead.

### Why Preact as a secondary option
- Preact provides **near drop-in React compatibility** at a fraction of the size.
- Mature ecosystem, great testing and LSP support, and **official Astro integration**.
- Best suited for **very small or performance-critical Astro islands**.

---

# Comparison Table

| Framework | Ecosystem Stability | LOC (Simple Component) | Testing Support | Nx Integration | Astro Support | Notes |
|------------|--------------------|-------------------------|-----------------|----------------|----------------|--------|
| **Solid.js** | ⭐⭐⭐⭐ Active community, backed by SolidStart | ~12 LOC | ✅ Vitest, RTL, Playwright | ✅ `@nx/solid` plugin | ✅ Official Astro adapter | Excellent performance and concise syntax. |
| **Preact** | ⭐⭐⭐⭐ Backed by OpenCollective, long-lived project | ~13 LOC | ✅ Jest, Vitest, React Testing Library | ✅ via Nx React plugin | ✅ Official Astro adapter | Lightweight React-compatible option. |
| **React** | ⭐⭐⭐⭐⭐ Backed by Meta, most widely used | ~14 LOC | ✅ Jest, Vitest, RTL, Playwright | ✅ Official Nx plugin | ✅ Official Astro adapter | Largest ecosystem, but heavier runtime. |
| **Vue 3** | ⭐⭐⭐⭐ Stable, strong funding & docs | ~16 LOC | ✅ Vitest, Vue Test Utils, Cypress | ✅ `@nx/vue` | ✅ Official Astro adapter | Great DX but less concise. |
| **Angular** | ⭐⭐⭐⭐ Backed by Google, enterprise focus | ~27 LOC | ✅ Jasmine, Jest, Karma | ✅ Official Nx plugin | ! Partial SSR integration | Too heavy for Astro islands. |
| **Qwik** | ⭐⭐ New, Builder.io-backed | ~13 LOC | ! Limited Testing Library integration | ! Partial Nx integration | ✅ Official Astro adapter | Promising, but immature. |
| **Alpine.js** | ⭐⭐⭐ Lightweight, stable | ~9 LOC | ! Minimal DOM-based testing | ❌ None | ✅ Works natively | Excellent for trivial interactivity only. |
| **Ripple** | ⭐ Unproven | ~18 LOC | ! Minimal support | ❌ None | ! Limited examples | Experimental. |

---
# Analysis
### Ecosystem Stability

- Solid.js is growing rapidly with a dedicated community and backing from SolidStart and Builder.io collaborations.
- Preact is lightweight and proven over many years, supported by OpenCollective.
- React remains the most stable but carries more weight than necessary for Astro use cases.

### Developer Ergonomics (Lines of Code)

- Alpine.js is shortest but too limited for complex islands.
- Solid.js and Preact both achieve near-minimal LOC with modern DX and composable architecture.
### Testing Framework Support
- Solid.js has growing native support for Vitest and Testing Library.
- Preact is React-compatible and benefits from mature test tooling (Jest, Vitest, RTL).
- Both integrate smoothly into Nx CI pipelines and ESLint workflows.

---
# Decision Matrix
| Criteria                   | Weight | Best Option                 |
| -------------------------- | ------ | --------------------------- |
| Ecosystem Stability        | 40%    | **Preact / Solid.js (tie)** |
| LOC (Developer Ergonomics) | 30%    | **Solid.js**                |
| Testing Framework Support  | 30%    | **Solid.js / Preact**       |

---

# LOC Comparison Example

A simple “Hello World” component (whitespace included):

### Solid.js - 15 LOC
```tsx
import { createSignal, createEffect } from 'solid-js';

export default function Hello(props: { name: string }) {
  const [count, setCount] = createSignal(0);

  createEffect(() => {
    console.log('count changed', count());
  });

  return (
    <button onClick={() => setCount(count() + 1)}>
      Hello {props.name} – {count()}
    </button>
  );
}
```
### Preact - 15 LOC
```tsx
import { useEffect, useState } from 'preact/hooks';

export function Hello({ name }: { name: string }) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    console.log('count changed', count);
  }, [count]);

  return (
    <button onClick={() => setCount(c => c + 1)}>
      Hello {name} – {count}
    </button>
  );
}
```
### React - 15 LOC
```tsx
import { useEffect, useState } from 'react';

export function Hello({ name }: { name: string }) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    console.log('count changed', count);
  }, [count]);

  return (
    <button onClick={() => setCount(c => c + 1)}>
      Hello {name} – {count}
    </button>
  );
}
```
### Angular - 18 LOC
```ts
import { Component, Input, effect, signal } from '@angular/core';

@Component({
  selector: 'app-hello',
  template: `
    <button (click)="count.set(count() + 1)">
      Hello {{ name }} – {{ count() }}
    </button>
  `
})
export class HelloComponent {
  @Input() name = 'World';
  count = signal(0);

  constructor() {
    effect(() => console.log('count changed', this.count()));
  }
}
```
### Qwik - 16 LOC
```tsx
import { component$, useSignal, useTask$ } from '@builder.io/qwik';

export const Hello = component$((props: { name: string }) => {
  const count = useSignal(0);

  useTask$(({ track }) => {
    track(() => count.value);
    console.log('count changed', count.value);
  });

  return (
    <button onClick$={() => count.value++}>
      Hello {props.name} – {count.value}
    </button>
  );
});
```

### Vue 3 (SFC)
```vue
<template>
  <button @click="count++">
    Hello {{ name }} – {{ count }}
  </button>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{ name: string }>()
const name = props.name
const count = ref(0)

watch(count, (v) => console.log('count changed', v))
</script>
```
### Alpine.js - 15 LOC
```html
<script>
  function hello(name){
    return {
      name,
      count: 0,
      init(){ this.$watch('count', v => console.log('count changed', v)) }
    }
  }
</script>

<div x-data="hello('World')">
  <button @click="count++">
    Hello <span x-text="name"></span> – <span x-text="count"></span>
  </button>
</div>
```

---
# Consequences
## Benefits

- Extremely fast, concise, and reactive UI development.
- Seamless integration with Astro, Nx, Tailwind, and ESLint.
- Modern developer experience with JSX familiarity.
- Simplified testing setup via Vitest and Playwright.
- Smaller component bundles than React or Angular.

## Drawbacks

- Smaller ecosystem than React (fewer prebuilt components).
- Slight learning curve for fine-grained reactivity model.
- Limited enterprise adoption compared to React or Angular.

---
## References

- [Solid.js Documentation](https://www.solidjs.com/docs)  
- [Preact Documentation](https://preactjs.com/)  
- [Astro Integrations Guide](https://astro.build/integrations/)  
- [Nx Frontend Integration](https://nx.dev/packages)  
- [TailwindCSS Documentation](https://tailwindcss.com/docs)  
- [ESLint Documentation](https://eslint.org/docs/latest/)  
- [Vitest Documentation](https://vitest.dev/)  
- [Playwright Testing Docs](https://playwright.dev/docs/intro)

