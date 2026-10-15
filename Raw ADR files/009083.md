---
title: "ADR 003 – Front-End Framework Selection for a Progressive Web Application"
date: 2025-10-08
status: Proposed
deciders: [Platform/DevEx]
tags: [frontend, pwa, nodejs, astro, nextjs, remix, sveltekit, nuxt, tanstack]
---

# Decision Summary

Use **Astro** for this PWA project.  
It provides the simplest path to an offline-capable, mostly static, islands-architecture web app with excellent developer experience and ecosystem maturity.

---
# Context

We need to select a web front-end framework for building a **simple Progressive Web Application (PWA)**.  
The app will be:

- **Primarily client-rendered**, using an **“islands architecture”** for interactivity.  
- **Offline-capable (local-first)**, with caching and service workers.  
- **Targeted for both desktop and mobile** devices.  
- **Maintained long-term**, prioritizing **developer experience** and **ecosystem maturity**.

We evaluated the following frameworks within the **Node.js ecosystem**:

- **Astro**  
- **Next.js**  
- **Remix**  
- **SvelteKit**  
- **TanStack Start**  
- **Nuxt (Vue)**  
- **Qwik** *(added for consideration due to its islands and resumability focus)*

---

# Comparison

| Framework | Architecture Fit (Islands) | Offline / PWA Support | DX & Ecosystem | Performance | Maturity | Notes |
|------------|----------------------------|------------------------|----------------|--------------|-----------|--------|
| **Astro** | ✅ Native “Islands” model | ✅ Excellent via integrations | ⭐⭐⭐⭐⭐ Best DX | ⚡ Excellent | Mature | Ideal for mostly static sites with interactive islands. Uses adapters for SSR or SSG. |
| **Next.js** | ! Partial (RSC replaces islands) | ✅ Next PWA plugin | ⭐⭐⭐⭐ Very mature | ⚡ High | Very mature | RSC model powerful but heavier than needed for simple PWAs. |
| **Remix** | ! SSR-first, client hydration optional | ✅ Built-in service workers | ⭐⭐⭐⭐⭐ Great DX | ⚡ High | Mature | Focuses on web fundamentals; great offline support but more server-bound. |
| **SvelteKit** | ✅ Component islands via hydration | ✅ Built-in PWA support | ⭐⭐⭐⭐⭐ Excellent | ⚡⚡ Lightning fast | Mature | Strong DX; seamless offline and local state handling. |
| **TanStack Start** | ✅ Designed for islands & React Query | ! Experimental PWA plugins | ⭐⭐⭐⭐ DX improving | ⚡ Very fast | Beta | Great promise for React-based PWAs; still maturing. |
| **Nuxt 3** | ✅ Supports islands via “partial hydration” | ✅ PWA & offline modules | ⭐⭐⭐⭐⭐ Excellent | ⚡⚡ High | Mature | Vue-based; strong ecosystem; great SSR flexibility. |
| **Qwik** | ✅ “Resumable” architecture | ! PWA requires extra config | ⭐⭐⭐ DX emerging | ⚡⚡⚡ Exceptional | Young | Future-looking approach; excellent performance but smaller community. |

---

# Analysis

### Astro
Astro is built explicitly around **islands architecture**, making it the most natural fit for this use case. It supports **static generation by default**, enabling fast loading and easy offline caching. With its **integrations for React, Svelte, Vue, and Solid**, it allows flexibility without coupling the project to one UI library.

**Strengths**
- True islands model out-of-the-box.
- Excellent developer experience and minimal boilerplate.
- Mature plugin ecosystem (including official PWA integrations).
- Can progressively enhance without a full runtime on the client.

**Weaknesses**
- Limited dynamic routing and SSR support compared to Next.js.
- Heavier on build-time static generation for interactivity.

---

### SvelteKit
SvelteKit offers an elegant DX and native support for **PWA features**, with excellent **local-first capabilities** and **lightweight reactivity**.  
It’s well-suited for small-to-medium apps and provides the simplicity of Astro with more flexibility for dynamic interactivity.

**Strengths**
- Great offline and local data handling.
- High performance; minimal JavaScript footprint.
- Mature, active community.

**Weaknesses**
- Smaller ecosystem than React-based frameworks.
- Learning curve for developers unfamiliar with Svelte syntax.

---

### Next.js
Next.js offers strong SSR, SSG, and hybrid rendering with massive ecosystem support. However, for an “islands” architecture, its **React Server Components** (RSC) model may be heavier than necessary.

**Strengths**
- Extremely mature ecosystem and tooling.
- Rich PWA and caching support via `next-pwa`.
- Easy hosting and deployment on Vercel.

**Weaknesses**
- RSC model is complex for simple PWAs.
- Larger bundle sizes and hydration overhead.

---

### Remix
Remix emphasizes **web fundamentals** and offers good PWA support with offline caching. It’s optimized for **form-driven UX** and **nested routes**, but leans SSR-first rather than islands-first.

**Strengths**
- Built-in caching, streaming, and offline capabilities.
- Excellent DX and commitment to web standards.

**Weaknesses**
- SSR-first paradigm; less ideal for mostly client-rendered apps.

---

### TanStack Start
An emerging contender designed for **React Query-native architectures** and **fine-grained routing control**.  
Still experimental but promising for future PWAs.

**Strengths**
- Lightweight, data-layer–first approach.
- Strong alignment with modern React data fetching (TanStack Query/Router).

**Weaknesses**
- Immature ecosystem.
- PWA support still evolving.

---

### Nuxt 3
Vue-based alternative offering **partial hydration**, **great PWA support**, and a mature ecosystem.  
Comparable DX to Next.js but simpler setup.

**Strengths**
- Stable ecosystem and tooling.
- Excellent PWA module.
- Hybrid rendering options.

**Weaknesses**
- Vue-based — requires Vue expertise.
- Slightly slower cold starts compared to SvelteKit/Astro.

---

### Qwik
Qwik introduces **resumability** rather than hydration, making it technically ideal for low-interactivity PWAs.  
However, it remains less mature than Astro or SvelteKit.

**Strengths**
- Unmatched performance; instant interactivity.
- Strong architectural alignment with “islands” approach.

**Weaknesses**
- Small community.
- Tooling and ecosystem still growing.

---

# Decision

**Selected Framework: Astro**

Astro best aligns with the intended architecture and priorities:

- **Native islands model** perfectly matches the planned client-side architecture.  
- **Offline-first capabilities** via Astro PWA and service worker integrations.  
- **Strong DX and stable ecosystem**, with flexible support for React/Svelte/Vue components.  
- **Optimized static rendering** for fast load times across mobile and desktop.

**When to revisit:**
If the project’s interactivity becomes highly dynamic or requires real-time SSR, reconsider **SvelteKit** or **Next.js**.

---

# Consequences

### Benefits
- Simplifies architecture for a mostly client-side app.  
- Lower runtime overhead and smaller client bundles.  
- Easier to onboard developers via Astro’s straightforward configuration.  
- High Lighthouse and Core Web Vitals scores by default.

### Drawbacks
- Limited SSR and dynamic route handling.
- Slightly smaller ecosystem than Next.js.

---

# Alternatives Considered

| Framework | Primary Reason for Rejection |
|------------|------------------------------|
| **Next.js** | Overly complex for islands-based PWAs |
| **Remix** | SSR-first model conflicts with static-first goals |
| **SvelteKit** | Excellent DX but heavier runtime for simple use case |
| **TanStack Start** | Immature ecosystem |
| **Nuxt 3** | Vue-specific; different stack |
| **Qwik** | Immature tooling; not production-proven |

---

# References

- [Astro Documentation](https://astro.build/docs)  
- [SvelteKit Documentation](https://kit.svelte.dev/docs)  
- [Next.js Documentation](https://nextjs.org/docs)  
- [Remix Docs](https://remix.run/docs)  
- [TanStack Start](https://tanstack.com/start/latest)  
- [Nuxt Documentation](https://nuxt.com/docs)  
- [Qwik Docs](https://qwik.builder.io/docs)


