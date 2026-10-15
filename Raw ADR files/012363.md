# ADR 0008: Use Docusaurus for Developer Documentation

## Status

Accepted

## Context

We need a structured, easy-to-navigate, and contributor-friendly documentation site to support the Meatbag app. It must be capable of housing:

- Architecture Decision Records (ADRs)
- Guides (deployment, testing, onboarding)
- Design rationale
- API documentation
- Feature overviews
- Future documentation like PRDs, tutorials, and API references

Several options were considered:

| Tool                   | Pros                                                                             | Cons                                 |
| ---------------------- | -------------------------------------------------------------------------------- | ------------------------------------ |
| **JSDoc**              | Automatically generates API docs from comments                                   | Poor UX for broader guides or TOC    |
| **TypeDoc**            | Strong for API docs with TypeScript                                              | Requires TS and not great for guides |
| **Confluence**         | Rich enterprise feature set                                                      | Not open source, not repo-based      |
| **Markdown-only wiki** | Simple and integrated                                                            | No search, navigation, or theming    |
| **Docusaurus**         | Versioned docs, sidebar navigation, Markdown-based, Git-integrated, search-ready | Requires initial setup               |

## Decision

We chose **[Docusaurus](https://docusaurus.io/)** as the documentation platform.

It enables:

- Writing all docs in Markdown using Git workflows
- Custom sidebar and nested folder navigation
- Developer-friendly DX with hot reload and MDX support
- Easy deploys to Vercel alongside our app (monorepo)
- Built-in search (via `@docusaurus/plugin-content-docs` and Algolia DocSearch)
- Future integration of JSDoc- or TypeDoc-generated docs via `/docs/api/`

## Consequences

- Documentation will live in `/docs/docs/` and be version-controlled
- Contributors can write and edit docs using Markdown and Git workflows
- We can organize content into logical folders: `guides/`, `api/`, `features/`, `adr/`, etc.
- No automatic source-code docs yet — functions/components/hook docs will be written manually for now
- Future plans to integrate auto-generated reference material using:
  - `JSDoc` + Docusaurus plugin or static output to `/docs/docs/api/`
  - `TypeDoc` if/when the project migrates to TypeScript

## Future Considerations

- Add an internal style guide for documentation contributions
- Consider using Docusaurus blog mode for tutorials or changelogs
- Evaluate documentation automation options as codebase grows
- If code switches to TypeScript, reevaluate use of [TypeDoc](https://typedoc.org/)

---

_Created: 2025-06-20_
