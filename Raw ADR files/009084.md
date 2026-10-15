---
title: "ADR 00X – CSS Utility/Styling Framework Selection"
date: 2025-10-08
status: Proposed
deciders: [Platform/DevEx]
tags: [frontend, css, design-system, tailwind, unocss, stylex, tachyons]
---

# Context

We need a **CSS styling approach** for web applications that optimizes **developer experience** (IDE/LSP support and day-to-day stability) and **ecosystem maturity** (community resources, adoption, and company backing).  
Candidates: **Tailwind CSS**, **UnoCSS**, **StyleX**, **Tachyons** (and similar Node.js–ecosystem tools).

---

# Decision

Adopt **Tailwind CSS** as the default styling framework.

**Why:**  
- **Best-in-class DX & LSP:** official VS Code IntelliSense with autocomplete, hover, diagnostics, and class validation.  
- **Ecosystem maturity & backing:** widely adopted, backed by **Tailwind Labs** with sustainable commercial products/partners and large community resources (UI kits, docs, plugins).

We’ll revisit if product constraints shift strongly toward typed CSS-in-JS with strict compile-time guarantees (see **StyleX**) or if we standardize on Vite-first atomic pipelines (see **UnoCSS**).

---

# Consequences

- **Pros:** Excellent IDE experience out-of-the-box; large pool of examples/components; stable release cadence; straightforward onboarding.  
- **Cons:** Utility-class HTML can become dense without conventions; theming beyond Tailwind’s tokens may require light config. (Mitigations: enforce class ordering, extract components, use `@apply` sparingly.)

---

# Comparison (focused on DX/LSP + Maturity)

| Tool | LSP / IDE Support (DX) | Stability & Day-to-Day DX | Ecosystem Maturity & Backing | Notes / When to Use |
|---|---|---|---|---|
| **Tailwind CSS** | **Official VS Code IntelliSense** (autocomplete, hovers, diagnostics). | Very stable, predictable utility API; rich docs. | **Tailwind Labs** backing; proven revenue & partner program; huge community & UI libraries. | Default choice for rapid delivery with top-tier DX + resources. |
| **UnoCSS** | **VS Code extension** + dedicated **language server**; good completions/hover. | Excellent with Vite; on-demand atomic classes = tiny CSS. | Strong OSS momentum (Vue/Vite ecosystem) but smaller org vs Tailwind. | Great for Vite-first apps needing extremely fine-grained atomic utilities. |
| **StyleX** (Meta) | ESLint rules; compiler/Babel plugins; **no official LSP** comparable to Tailwind/UnoCSS yet. | Powerful, typed, atomic CSS compiled at build; evolving DX (Babel/SWC trade-offs). | **Backed by Meta**; actively developed, public releases and roadmap. **Newer** OSS ecosystem than Tailwind. | Choose when you need **typed CSS-in-JS** with strict constraints and are comfortable with Babel/ESLint setup. |
| **Tachyons** | No modern LSP/IntelliSense story; classic utility CSS. | Stable but **minimally maintained**; fine for static sites. | Older project; small activity vs Tailwind/UnoCSS. | Lightweight legacy utility set; not recommended for new large apps. |

> Also considered: **CSS Modules**, **Vanilla Extract**, **Styled Components/Emotion** (DX trade-offs, different paradigms). None surpass Tailwind on combined **LSP + ecosystem** for our needs.

---

# Rationale

## 1. Developer Experience (LSP & Stability)
- Tailwind’s **official IntelliSense** provides first-party autocompletion, hover info, and class validation, reducing CSS lookup/typo friction and improving code confidence.  
- UnoCSS offers a credible **language server** and VS Code extension; excellent for teams already standardized on Vite, but still less ubiquitous than Tailwind’s plugin.  
- StyleX relies on **ESLint + compiler plugins** rather than an established LSP. Powerful for constraints/typing, but IDE assistance is currently less streamlined than Tailwind/UnoCSS.

## 2. Ecosystem Maturity (Community & Backing)
- Tailwind is backed by **Tailwind Labs** with demonstrated commercial sustainability (Tailwind UI & partner program) and a very large community/content ecosystem.  
- StyleX is backed by **Meta** and used at massive scale internally, with active open-source releases—but public ecosystem and third-party resources are still maturing relative to Tailwind.  
- UnoCSS is community-driven with strong momentum in the Vue/Vite world, but lacks a comparable commercial entity behind it.  
- Tachyons is stable but comparatively quiet in maintenance and community growth.

---

# Implementation Sketch

- Adopt **Tailwind CSS** with the **official VS Code IntelliSense** extension for all contributors.  
- Establish **design tokens** in `tailwind.config.{js,ts}` and document class usage conventions (ordering, extraction to components).  
- Provide a starter component library and linting/formatting rules to keep utility classes tidy.

---

# Alternatives Considered

- **UnoCSS** — Strong candidate if we move to a Vite-only toolchain and want ultra-minimal CSS via on-demand utilities.  
- **StyleX** — Reconsider if we require **strict, typed styling constraints** and are willing to standardize on Babel/ESLint-driven compilation flow.  
- **Tachyons** — Suitable for very small/static sites; not recommended for long-term product development due to ecosystem stagnation.

---

# References

- [Tailwind CSS Documentation](https://tailwindcss.com/docs)  
- [Tailwind Labs](https://tailwindcss.com/company)  
- [Tailwind CSS IntelliSense Extension](https://marketplace.visualstudio.com/items?itemName=bradlc.vscode-tailwindcss)  
- [UnoCSS Documentation](https://unocss.dev/)  
- [UnoCSS VS Code Extension](https://marketplace.visualstudio.com/items?itemName=antfu.unocss)  
- [StyleX Documentation](https://stylexjs.com/)  
- [StyleX GitHub Repository (Meta)](https://github.com/facebook/stylex)  
- [Tachyons Documentation](https://tachyons.io/)  
- [Tachyons GitHub Repository](https://github.com/tachyons-css/tachyons)

