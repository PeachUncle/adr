# ADR-012: UI Libraries, Styling & Theming (Svelte 5)

Status: Accepted
Date: 2025-08-22
Owners: Archon Core

## Context

Archon’s desktop UI (via Wails) uses Svelte for the frontend. We need:

- A component library that looks/feels “desktop-class” (dialogs, context menus, resizable panels).
- Compatibility with **Svelte 5** (runes) and **Tailwind CSS v4**.
- Solid theming (light/dark, future brand themes) without framework lock-in.
- Virtualization for large trees/lists (10k+ nodes).
The Svelte ecosystem offers several options (shadcn-svelte, Flowbite Svelte, Skeleton, Melt/Bits headless primitives, etc.) with evolving Svelte 5/Tailwind v4 support.

## Decision

**Primary stack (ship this by default):**

1) **Svelte 5 + Tailwind CSS v4** as the styling foundation. Tailwind v4 is officially released and works with Svelte 5; use its `@custom-variant` dark-mode and `@theme` tokens for color variables.  [oai_citation:0‡Tailwind CSS](https://tailwindcss.com/blog/tailwindcss-v4?utm_source=chatgpt.com)  
2) **shadcn-svelte v1** for ready-to-use, accessible components (dialogs, command palette, context menu, resizable panels, etc.). v1 explicitly targets **Svelte 5** and **Tailwind v4**.  [oai_citation:1‡shadcn-svelte](https://www.shadcn-svelte.com/docs/migration/svelte-5?utm_source=chatgpt.com) [oai_citation:2‡shadcn-svelte](https://shadcn-svelte.com/docs/migration/tailwind-v4?utm_source=chatgpt.com)  
3) **Headless primitives via Bits UI** (and Melt UI builders under the hood) where we need custom behavior/markup. Bits UI is the Svelte headless baseline; Melt provides builder APIs and has tracked Svelte 5 compatibility.  [oai_citation:3‡Bits UI](https://bits-ui.com/?utm_source=chatgpt.com) [oai_citation:4‡GitHub](https://github.com/huntabyte/bits-ui?utm_source=chatgpt.com) [oai_citation:5‡melt-ui.com](https://www.melt-ui.com/?utm_source=chatgpt.com)  
4) **Icons: `lucide-svelte`** (lightweight, consistent, actively maintained).  [oai_citation:6‡npm](https://www.npmjs.com/package/lucide-svelte?utm_source=chatgpt.com) [oai_citation:7‡Lucide](https://lucide.dev/guide/packages/lucide-svelte?utm_source=chatgpt.com)  
5) **Virtualization: `@tanstack/svelte-virtual`** for large lists/trees; if we hit Svelte-5 edge cases, fall back to `svelte-tiny-virtual-list` or the Svelte-5 “virtuallists” port.  [oai_citation:8‡TanStack](https://tanstack.com/virtual?utm_source=chatgpt.com) [oai_citation:9‡npm](https://www.npmjs.com/package/%40tanstack%2Fsvelte-virtual?utm_source=chatgpt.com) [oai_citation:10‡GitHub](https://github.com/TanStack/virtual/issues/866?utm_source=chatgpt.com) [oai_citation:11‡madewithsvelte.com](https://madewithsvelte.com/svelte-virtuallists?utm_source=chatgpt.com)  
6) **Resizable panes:** use shadcn-svelte’s `Resizable` first; if we need more layout control, use PaneForge or svelte-splitpanes.  [oai_citation:12‡shadcn-svelte](https://shadcn-svelte.com/docs/components/resizable?utm_source=chatgpt.com) [oai_citation:13‡GitHub](https://github.com/svecosystem/paneforge?utm_source=chatgpt.com) [oai_citation:14‡orefalo.github.io](https://orefalo.github.io/svelte-splitpanes/?utm_source=chatgpt.com)  
7) **Theme & mode switching:** CSS variables for tokens + Tailwind v4 `@theme` (inline) and **ModeWatcher** to manage light/dark without FOUC, honoring system prefs.  [oai_citation:15‡Tailwind CSS](https://tailwindcss.com/docs/dark-mode?utm_source=chatgpt.com) [oai_citation:16‡shadcn-svelte](https://shadcn-svelte.com/docs/migration/tailwind-v4?utm_source=chatgpt.com) [oai_citation:17‡Mode Watcher](https://mode-watcher.svecosystem.com/?utm_source=chatgpt.com)

**Secondary (opt-in, app areas that want pre-styled admin UI):**

- **Flowbite Svelte** (Tailwind-based, broad component count). Keep it out of core unless a screen clearly benefits; Svelte 5 support exists with caveats, see their Svelte 5 progress and docs.  [oai_citation:18‡Flowbite Svelte](https://flowbite-svelte.com/?utm_source=chatgpt.com)

## Rationale

- **Svelte 5 + Tailwind v4** gives speed and predictable dark mode via `dark:` utilities and `@theme` variables (v4).  [oai_citation:19‡Tailwind CSS](https://tailwindcss.com/blog/tailwindcss-v4?utm_source=chatgpt.com)
- **shadcn-svelte v1** is purpose-built for Svelte 5/Tailwind v4 and ships desktop-appropriate primitives (dialogs, context menus, resizable) with an accessible baseline. We can copy/own component code as needed.  [oai_citation:20‡shadcn-svelte](https://www.shadcn-svelte.com/docs/migration/svelte-5?utm_source=chatgpt.com) [oai_citation:21‡shadcn-svelte](https://shadcn-svelte.com/docs/migration/tailwind-v4?utm_source=chatgpt.com)
- **Headless primitives (Bits/Melt)** keep us flexible for custom tree views, command palettes, and complex panels without styling lock-in.  [oai_citation:22‡Bits UI](https://bits-ui.com/?utm_source=chatgpt.com) [oai_citation:23‡melt-ui.com](https://www.melt-ui.com/?utm_source=chatgpt.com)
- **Virtualization** is essential for responsive trees; TanStack Virtual targets Svelte and is battle-tested; alternatives exist if any Svelte 5 regressions appear.  [oai_citation:24‡TanStack](https://tanstack.com/virtual?utm_source=chatgpt.com) [oai_citation:25‡npm](https://www.npmjs.com/package/%40tanstack%2Fsvelte-virtual?utm_source=chatgpt.com) [oai_citation:26‡GitHub](https://github.com/TanStack/virtual/issues/866?utm_source=chatgpt.com)
- **ModeWatcher** simplifies light/dark, SSR-friendly and avoids FOUC—ideal for a desktop-feel app.  [oai_citation:27‡Mode Watcher](https://mode-watcher.svecosystem.com/?utm_source=chatgpt.com)

## Alternatives Considered

- **Skeleton** (Tailwind design system). Strong toolkit, but Svelte 5 status has been evolving; we’ll reassess when its Svelte 5 support is unequivocally stable for our needs.  [oai_citation:28‡Skeleton](https://www.skeleton.dev/?utm_source=chatgpt.com) [oai_citation:29‡GitHub](https://github.com/skeletonlabs/skeleton/discussions/2375?utm_source=chatgpt.com)
- **Electron-style fully bundled UI kits**: heavier runtime; our Wails + system WebView choice (ADR-011) favors lighter CSS/JS. (See ADR-011.)
- **Flowbite Svelte as primary**: rich set, but we prefer shadcn-svelte’s composability and theming approach for “desktop-class” feel; Flowbite stays as a targeted addition.  [oai_citation:30‡Flowbite Svelte](https://flowbite-svelte.com/?utm_source=chatgpt.com)

## Consequences

- **Positive:** Modern, accessible components; small bundles; fast iteration; drop-in dark mode; scalable lists; copy-editable components.
- **Risks:** Ecosystem churn around Svelte 5 & Tailwind v4; we mitigate via pinned versions and fallback libs (see Implementation Notes).
- **Interop:** Mixing libraries means we must standardize tokens (CSS variables) to keep themes consistent.

## Implementation Notes

- **Packages (core):**  
  - `tailwindcss` v4; configure dark via `@custom-variant` or class on `<html>`.  [oai_citation:31‡Tailwind CSS](https://tailwindcss.com/docs/dark-mode?utm_source=chatgpt.com)  
  - `shadcn-svelte` v1; initialize for Svelte 5/Tailwind v4 per docs.  [oai_citation:32‡shadcn-svelte](https://www.shadcn-svelte.com/docs/migration/svelte-5?utm_source=chatgpt.com) [oai_citation:33‡shadcn-svelte](https://shadcn-svelte.com/docs/migration/tailwind-v4?utm_source=chatgpt.com)  
  - `bits-ui` (headless) + optional `melt-ui` builders.  [oai_citation:34‡Bits UI](https://bits-ui.com/?utm_source=chatgpt.com) [oai_citation:35‡melt-ui.com](https://www.melt-ui.com/?utm_source=chatgpt.com)  
  - `lucide-svelte` for icons.  [oai_citation:36‡npm](https://www.npmjs.com/package/lucide-svelte?utm_source=chatgpt.com)  
  - `@tanstack/svelte-virtual` (primary), `svelte-tiny-virtual-list` and “virtuallists” as fallbacks.  [oai_citation:37‡npm](https://www.npmjs.com/package/%40tanstack%2Fsvelte-virtual?utm_source=chatgpt.com) [oai_citation:38‡GitHub](https://github.com/jonasgeiler/svelte-tiny-virtual-list?utm_source=chatgpt.com) [oai_citation:39‡madewithsvelte.com](https://madewithsvelte.com/svelte-virtuallists?utm_source=chatgpt.com)  
  - `mode-watcher` for light/dark management.  [oai_citation:40‡Mode Watcher](https://mode-watcher.svecosystem.com/?utm_source=chatgpt.com)
- **Theming approach:**  
  - Define semantic CSS variables in `:root` and `.dark` (`--background`, `--foreground`, `--primary`, etc.), then map to Tailwind v4 `@theme` tokens (e.g., `--color-background: hsl(var(--background))`).  [oai_citation:41‡shadcn-svelte](https://shadcn-svelte.com/docs/migration/tailwind-v4?utm_source=chatgpt.com)  
  - Consider **Radix Colors** to generate accessible light/dark scales into those variables; optional now, easy later.  [oai_citation:42‡Radix UI](https://www.radix-ui.com/colors/docs/overview/usage?utm_source=chatgpt.com)
- **Resizable panes:** Prefer `@/components/ui/resizable` from shadcn-svelte; if multi-sash layouts or snap behavior are needed, adopt PaneForge or svelte-splitpanes just for those screens.  [oai_citation:43‡shadcn-svelte](https://shadcn-svelte.com/docs/components/resizable?utm_source=chatgpt.com) [oai_citation:44‡GitHub](https://github.com/svecosystem/paneforge?utm_source=chatgpt.com) [oai_citation:45‡orefalo.github.io](https://orefalo.github.io/svelte-splitpanes/?utm_source=chatgpt.com)
- **Tree view:** Build with headless pieces (e.g., Melt’s tree builder) + virtualization, or use a community tree adapted to our tokens if timelines demand.  [oai_citation:46‡melt-ui.com](https://www.melt-ui.com/docs/builders/tree?utm_source=chatgpt.com)
- **Pinning & CI:** Pin versions in `package.json`; add UI smoke tests (mount key components) to catch upstream breaking changes.
- **Docs & Design Tokens:** Document the token contract (names → meaning) so any 3rd-party component can be themed consistently.

## Review / Revisit

- Revisit if:  
  - Skeleton or another library offers clear, stable Svelte 5 support *and* better desktop components;  
  - `@tanstack/svelte-virtual` shows persistent Svelte 5 issues we can’t workaround;  
  - We adopt brand theming that outgrows our current token set.
