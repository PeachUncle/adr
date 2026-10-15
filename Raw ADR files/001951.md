# Monorepo vs multirepo

Contents:

- [Dev notes](#dev-notes)
  - [Issue](#issue)
  - [Decision](#decision)
  - [Status](#status)
- [Details](#details)
  - [Assumptions](#assumptions)
  - [Constraints](#constraints)
  - [Positions](#positions)
  - [Argument](#argument)
  - [Implications](#implications)
- [Related](#related)
  - [Related decisions](#related-decisions)
  - [Related requirements](#related-requirements)
  - [Related artifacts](#related-artifacts)
  - [Related principles](#related-principles)
- [Notes](#notes)

## Dev notes

Used base configs

setting up a pnpm monorepo with vite and ts
https://vedanshmehra.hashnode.dev/setting-up-a-monorepo-with-vite-typescript-and-pnpm-workspaces

useful commands

install pnpm globally

> npm install -g pnpm

pnpm init a new project

> pnpm init

add pnpm package as a dependency inside another package, like:

> pnpm add @pnpm-monorepo/shared

vite init for a new package, inside packages dir

> pnpm create vite

// and then, fill in the package name

pnpm base

> pnpm i

> pnpm dev

### Issue

The project involves developing three major categories of software:

- Front-end GUIs
- Middleware services
- Back-end servers

The source code management (SCM) version control system (VCS) is git.

Issue statement: need to choose, how to organize our codebase.

The top-level choice is to organize as a "monorepo" or "polyrepo" or "hybrid":

- Monorepo means we put all pieces into one big repo
- Polyrepo means we put each piece in its own repo
- Hybrid means some mix of monorepo and polyrepo

For more information: [monorepo-vs-polyrepo](https://github.com/joelparkerhenderson/monorepo-vs-polyrepo)

also need to find the right monorepo tools
Turborepo, yarn workspaces, lerna, pnpm monorepo, etc...

### Decision

Monorepo when an organization/team/project is relatively small, and rapid iteration is higher priority than sustaining stability.

Polyrepo when an organization/team/project is relatively large, and sustaining stability is higher priority than rapid iteration.

from all the workspaces and monorepo tools - pnpmn is the ne kid on the block, it's worth giving a shot to both learn and discover how it differs and what are the benefits of using the latest technology.

### Status

Decision: monorepo with pnpmn.

## Details

### Assumptions

As a hobby-project, this should more of learning new stuff than just using the already established tech stack.

### Constraints

Constraints are well-documented at https://github.com/joelparkerhenderson/monorepo-vs-polyrepo

### Argument

None.

### Implications

CI+CD could take more time for a full build for a monorepo, because CI+CD could build all the projects in the monorepo.
However it's a small project, not a problem, also vite and pnpm is blazingly fast.

Scaing issues in the future: can occur, but as a hobby project, most problably, just won't.

## Related

### Related decisions

The whole package management is going to pnpm as well, not npm or yarn as previously.

### Related requirements

Not at the moment.

### Related artifacts

None.

### Related principles

Easily reversable. If the monorepo doesn't work in practice, it can be split into multi-repos.

## Notes
