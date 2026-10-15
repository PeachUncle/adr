---
title: "ADR 00Y – Web Application Linting Toolchain Selection"
date: 2025-10-08
status: Proposed
deciders: [Platform/DevEx]
tags: [frontend, linting, astro, nx, eslint, prettier, biome, typescript, lsp]
---
# Decision Summary 
 Adopt ESLint + Prettier as the core linting and formatting stack with official Astro and Nx integrations.
Evaluate Biome for future consolidation once its Nx/Astro ecosystem support matures.

# Context

We require a **modern, language-aware linting and formatting toolchain** that:

- Integrates cleanly with **Astro** and **Nx** monorepos  
- Provides **Language Server Protocol (LSP)** integration for IDE feedback  
- Works consistently across **TypeScript, HTML, CSS, React, Vue, Angular, and Solid.js**  

The goal is to ensure consistent developer experience, style enforcement, and fast CI feedback while avoiding redundant overlapping tools.

---

# Decision

Adopt the following **linting and formatting stack**:

- **Primary linter:** [ESLint](https://eslint.org/) (with framework-specific plugins)  
- **Formatter:** [Prettier](https://prettier.io/)  
- **Optional unified alternative (experimental):** [Biome](https://biomejs.dev/) for high-performance all-in-one lint+format use cases  
- **Nx Integration:** via `@nx/linter` and `eslint-config-nx`  
- **Astro Integration:** via `eslint-plugin-astro`  
- **LSP Integration:** through the **VS Code ESLint Language Server** and **Prettier extension**

This combination ensures mature support, wide adoption, and tight IDE/CI integration.

---

# Comparison of Linting Ecosystem

| Tool | Astro Integration | Nx Integration | LSP Support | Framework Coverage | Performance | Ecosystem Maturity | Notes |
|------|-------------------|----------------|--------------|--------------------|--------------|--------------------|-------|
| **ESLint** | ✅ via `eslint-plugin-astro` | ✅ via `@nx/eslint` | ✅ ESLint Language Server | ✅ React, Vue, Angular, Solid, TS, JS | ⚡ Moderate | ⭐⭐⭐⭐⭐ Most mature | Canonical web linting tool; huge plugin ecosystem. |
| **Prettier** | ✅ via `prettier-plugin-astro` | ✅ integrated easily via Nx executor | ✅ Prettier LSP extension | ✅ HTML, CSS, TS, JSX, Markdown | ⚡⚡ Fast | ⭐⭐⭐⭐⭐ Industry standard | Complements ESLint for formatting. |
| **Biome (Rome successor)** | ! Partial (Astro plugin planned) | ! Not yet integrated with Nx | ✅ Biome LSP | ✅ TS, JSX, CSS | ⚡⚡⚡ Extremely fast | ⭐⭐ Newer ecosystem | Promising unified formatter/linter but immature for large Nx repos. |
| **Stylelint** | ✅ via Astro & Vite CSS pipelines | ✅ runs in Nx via custom executor | ✅ Stylelint LSP | ✅ CSS, SCSS, PostCSS | ⚡ Moderate | ⭐⭐⭐⭐ Mature CSS ecosystem | Recommended addition for large design systems. |
| **TSLint** | ❌ Deprecated | ❌ | ❌ | ✅ TS only | — | ❌ Deprecated | Superseded by ESLint. |
| **VLS / Volar / Vue-eslint-parser** | ✅ via Astro & Vue | ✅ (Nx plugin support) | ✅ via Volar LSP | ✅ Vue SFC | ⚡ Fast | ⭐⭐⭐⭐ | Used internally via ESLint parser plugins. |

---

# Rationale

### 1. Developer Experience (LSP Integration)
- **ESLint** provides the richest IDE support through the official **ESLint Language Server** (VS Code, NeoVim, JetBrains).  
- **Prettier** integrates seamlessly with LSP extensions, ensuring auto-format on save without ESLint conflicts.  
- **Biome** introduces an all-in-one LSP but lacks mature plugin coverage for Astro/Nx, making it less suitable today.

### 2. Ecosystem Maturity
- ESLint has a decade of active development, with stable backing from OpenJS Foundation.  
- Nx supports ESLint natively via the `@nx/linter` executor and `eslint-config-nx`.  
- Astro provides an official `eslint-plugin-astro` and `prettier-plugin-astro`, ensuring first-party support.  
- Prettier is ubiquitous across teams and integrates easily in CI/CD pipelines.  
- Biome is emerging from the Rome project with strong performance but minimal plugin ecosystem today.

### 3. Framework Compatibility
- ESLint handles TS/JS plus framework-specific rules:  
  - React: `eslint-plugin-react`, `eslint-plugin-react-hooks`  
  - Vue: `eslint-plugin-vue`  
  - Angular: `@angular-eslint`  
  - Solid: `eslint-plugin-solid`  
  - Astro: `eslint-plugin-astro`  
- Prettier supports cross-framework formatting for `.tsx`, `.vue`, `.astro`, `.svelte`, `.css`, and `.html`.  
- Stylelint can optionally be layered for advanced CSS validation and design-token enforcement.

---

# Recommended Configuration

### Package Setup

```bash
pnpm add -D eslint prettier eslint-config-prettier eslint-plugin-prettier \
  eslint-plugin-astro eslint-plugin-solid stylelint prettier-plugin-astro
```
### ESLint Base Config
```js
module.exports = {
  root: true,
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:astro/recommended',
    'plugin:solid/typescript',
    'plugin:prettier/recommended',
    'plugin:@nx/typescript'
  ],
  parserOptions: {
    ecmaVersion: 2023,
    sourceType: 'module'
  },
  env: { browser: true, es2023: true },
};

```

### Nx Integration
Add the following executor to project.json or workspace.json:

```json
"lint": {
  "executor": "@nx/linter:eslint",
  "options": {
    "lintFilePatterns": ["apps/**/src/**/*.{ts,tsx,vue,astro}"]
  }
}

```

### Astro + Prettier Config
```js
module.exports = {
  plugins: ['prettier-plugin-astro'],
  astroAllowShorthand: true,
  astroSortAttributes: 'asc',
  singleQuote: true,
  trailingComma: 'es5'
};
```
---
# Alternatives Considered
| Option                  | Reason Not Chosen                                           |
| ----------------------- | ----------------------------------------------------------- |
| **Biome only**          | Excellent performance, but poor Nx/Astro integration today. |
| **Rome (legacy)**       | Superseded by Biome; project discontinued.                  |
| **Custom Vite plugins** | Fragmented linting experience, no unified LSP.              |
| **TSLint**              | Deprecated; replaced by ESLint.                             |


---
# Consequences
* Pros: Consistent linting and formatting across the monorepo; unified developer experience with full LSP integration; robust support for Astro, React, Vue, Angular, and Solid.

* Cons: Two-tool setup (ESLint + Prettier) introduces mild redundancy; requires occasional sync of lint/format rules.

* Mitigation: Use eslint-config-prettier and eslint-plugin-prettier to prevent rule overlap.
---
# References

- [ESLint Documentation](https://eslint.org/docs/latest/)
- [Nx Linter Plugin](https://nx.dev/packages/linter)
- [Astro ESLint Plugin](https://github.com/ota-meshi/eslint-plugin-astro)
- [Prettier Documentation](https://prettier.io/docs/en/)
- [Prettier Plugin for Astro](https://github.com/withastro/prettier-plugin-astro)
- [Stylelint Documentation](https://stylelint.io/)
- [Biome (Rome) Documentation](https://biomejs.dev/)
- [Volar / Vue LSP](https://github.com/vuejs/language-tools)

