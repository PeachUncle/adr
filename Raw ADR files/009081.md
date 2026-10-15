# ADR-014: Documentation Quality and Tooling Stack

**Status:** Proposed  
**Date:** 2025-10-15  
**Author:** Em Jones – Full-stack Engineer, Software Architect, & Cloud Consultant  
**Context:** Developer-facing documentation in codebases, platforms, and internal portals (e.g., Backstage TechDocs, MDX-based design systems).  
**Decision Drivers:**  
- Ease of authoring and reviewing documentation.  
- Quality enforcement (style, structure, and link integrity).  
- Integration with CI/CD pipelines.  
- Compatibility with Markdown and code-adjacent docs (TypeScript, Python, Terraform, etc.).  

---

## 1. Problem Statement

Documentation quality decays quickly in multi-team environments where code and docs evolve independently. Without automation, docs become stale, inconsistent, or hard to discover.  
This ADR compares leading tools for maintaining **documentation quality** and proposes a **composable toolchain** that ensures:
- Style and link validation.  
- Accessibility and Markdown linting.  
- Schema-driven metadata checks for TechDocs and ADRs.  
- Seamless CI/CD integration.  

---

## 2. Options Considered

| Tool | Category | Key Features | Strengths | Weaknesses |
|------|-----------|---------------|------------|-------------|
| **Vale** | Natural-language linter | Customizable rulesets, YAML-based style guides (Google, Microsoft, Write-the-Docs), Markdown/AsciiDoc support | Best for enforcing editorial style and tone consistency | Requires maintaining rulesets; no native CI output visualization |
| **markdownlint (DavidAnson)** | Markdown linter | Rule-based linting for headings, spacing, links | Simple, fast, widely adopted | Limited semantic awareness; no tone/style rules |
| **remark / unified / rehype** | Markdown AST processor | Plugin ecosystem for linting, formatting, custom transforms | Powerful for custom doc pipelines | Requires setup in Node projects; opinionated AST |
| **Lychee / markdown-link-check** | Link validator | Validates internal and external links | Detects broken references early | Can produce false positives on transient links |
| **Prettier** | Formatter | Consistent Markdown formatting | Familiar across teams | No semantic checks or quality rules |
| **DocFX / Docusaurus / MkDocs / Backstage TechDocs** | Site generators | Convert Markdown → Docs site | Integration with CI/CD and MDX support | Focus on publishing, not linting |
| **OpenAPI / Spectral** | Schema validator | Linting YAML/JSON for structured docs | Excellent for API contracts | Not general-purpose for prose docs |
| **Vale + remark + markdownlint + Lychee** | Combined Stack | Integrated in CI | Covers most doc QA categories | Some overlap between rulesets |

---

## 3. Evaluation Criteria

| Criterion | Weight | Rationale |
|------------|---------|------------|
| Integration with CI/CD (GitHub Actions, Azure DevOps, GitLab CI) | 25% | Must run as part of trunk-based pipelines |
| Markdown/MDX support | 25% | Required for developer-facing docs and ADRs |
| Rule customization & extensibility | 20% | Must adapt to internal tone and ADR style |
| Ecosystem maturity | 15% | Tool longevity and active maintenance |
| Performance & simplicity | 15% | Encourages adoption and faster feedback |

---

## 4. Analysis Summary

| Tool / Stack | CI/CD Integration | Extensibility | Ecosystem Maturity | Overall |
|---------------|------------------|----------------|--------------------|----------|
| **Vale** | Excellent (CLI, Actions, DevOps) | High (YAML rulesets) | Mature | ⭐⭐⭐⭐☆ |
| **markdownlint** | Excellent | Medium (JSON config) | Mature | ⭐⭐⭐⭐☆ |
| **remark-lint** | Good | Very High | Mature | ⭐⭐⭐⭐⭐ |
| **Lychee** | Excellent | Low (static validation) | Moderate | ⭐⭐⭐⭐☆ |
| **Prettier** | Excellent | Low | Very Mature | ⭐⭐⭐☆☆ |
| **DocFX / Docusaurus / TechDocs** | Excellent | Medium | Mature | ⭐⭐⭐⭐☆ |

---

## 5. Decision

Adopt a **hybrid documentation quality pipeline** combining the following tools:

### Recommended Stack

| Layer | Tool | Purpose |
|-------|------|----------|
| **Style & Tone** | **Vale** | Enforce consistent writing style (e.g., Google or custom guides). |
| **Syntax & Structure** | **markdownlint** | Catch Markdown structure and whitespace errors. |
| **Semantic & Custom Rules** | **remark-lint** | Validate internal link conventions, frontmatter, and ADR schemas. |
| **Link & Reference Validation** | **Lychee** | Detect broken URLs and intra-repo link rot. |
| **Formatting** | **Prettier** | Maintain consistent Markdown and code-block formatting. |

---

<!-- ## 6. Implementation Plan -->
<!---->
<!-- 1. **Local Pre-commit Hooks** -->
<!--    - Use `pre-commit` or Husky to run `prettier --check`, `markdownlint`, and `vale`. -->
<!-- 2. **CI/CD Integration** -->
<!--    - Add GitHub Action or Azure DevOps pipeline step: -->
<!--      ```yaml -->
<!--      - name: Validate Docs -->
<!--        run: | -->
<!--          npm run lint:md -->
<!--          vale docs/ -->
<!--          lychee --no-progress docs/**/*.md -->
<!--      ``` -->
<!-- 3. **TechDocs Compatibility** -->
<!--    - Integrate with Backstage TechDocs: -->
<!--      - Run linting prior to site generation. -->
<!--      - Fail builds on critical documentation rule violations. -->
<!-- 4. **Authoring Experience** -->
<!--    - VSCode + `markdownlint`, `Vale`, and `remark-lint` extensions. -->
<!--    - Encourage authors to preview via Docusaurus/TechDocs locally. -->

---

## 6. Consequences

**Positive**
- High consistency and link reliability across docs.
- Automated enforcement of editorial guidelines.
- Improved confidence in docs as living artifacts.

**Negative**
- Requires maintaining rule configuration files.
- Slightly longer CI runtimes (~20–30s per pipeline).

---

## 8. Alternatives Considered

- **Rely solely on markdownlint + Prettier** → Simplifies setup but lacks tone/style checks.  
- **Use AI-based grammar tools (Grammarly, LanguageTool)** → Not CI/CD-friendly, inconsistent privacy policies.  
- **Adopt a monolithic docs generator (DocFX, Docusaurus) with built-in linting** → Less flexible, harder to extend for ADR or Backstage workflows.  

---

## 9. Recommendation

Adopt a **layered documentation QA strategy** combining:

> **Vale + markdownlint + remark-lint + Lychee + Prettier**

This stack provides:
- Editorial tone enforcement.  
- Structural and semantic validation.  
- Automated link integrity.  
- Uniform formatting.  
- CI/CD and IDE integration across teams.  

---

## 10. References

- [Vale Style Guide](https://vale.sh/docs/topics/styles/)
- [markdownlint Rules](https://github.com/DavidAnson/markdownlint/blob/main/doc/Rules.md)
- [remark-lint Ecosystem](https://github.com/remarkjs/remark-lint)
- [Lychee Link Checker](https://github.com/lycheeverse/lychee)
- [Prettier Documentation](https://prettier.io/)
- [Backstage TechDocs](https://backstage.io/docs/features/techdocs/)

