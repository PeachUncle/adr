---
type: ADR
status: accepted
authors:
  - David Vega
---

# ADR 3: Immutable Deployments

## Context

Enterprise deployments require immutable, reproducible, and fast delivery of applications. Traditionally, Next.js apps are deployed by copying source and building on the server or in Docker. This ADR documents a pattern where the app is prebuilt, packaged as an npm package, and deployed via npm or Docker without copying or building source code in the target environment.

## Decision

Adopt a pattern where the Next.js app is:
- Built locally or in CI (generating `.next`, `public`, etc.)
- Packaged as an npm package containing only runtime files (no source or dev dependencies)
- Published to npm (public or private registry)
- Deployed by installing the package and running `npm start` (no build step required)
- Optionally, a Docker image is built that installs the npm package and runs the app

## Implementation Summary

1. **Build & Package**: Run `npm ci && npm run build`. Prepare a package including `.next`, `public`, `next.config.js`, `package.json`, and other runtime files. Exclude source and dev files via the `files` field in `package.json`.
2. **Publish**: Publish the package to npm (`npm publish`).
3. **Docker Image**: Use a Dockerfile to install the npm package and run `npm start`.

### Example Dockerfile

```Dockerfile
FROM node:20-alpine
WORKDIR /app
RUN npm install @dukeofgaming/ab-app@latest
WORKDIR /app/node_modules/@dukeofgaming/ab-app
EXPOSE 3000
CMD ["npm", "start"]
```

## Consequences

### Pros (Enterprise-Relevant)
- **Immutability**: Each deploy is a versioned, tamper-proof artifact.
- **Speed**: No build step or source copying on the deploy target; instant startup.
- **Auditability**: Versioned npm packages provide a clear deployment trail.
- **Consistency**: What is tested is exactly what is deployed.
- **Security**: Only runtime files are shipped; no dev/test code.
- **Rollbacks**: Revert by changing the installed package version.
- **Integrates with Docker**: Enables container-based immutable deployments.

### Cons
- **Large Package Size**: Prebuilt apps can be large; careful curation of files is needed.
- **No Hotfixes in Production**: All fixes require a new build and publish.
- **Node.js Compatibility**: Target must match the build environment.
- **Uncommon for Next.js**: Not the default Next.js deployment pattern; requires documentation and training.

## References
- See `package.json` for the `files` field and runtime packaging.
- See this ADR for the Dockerfile example.
- Next.js docs: https://nextjs.org/docs/pages/api-reference/create-next-app#using-templates
