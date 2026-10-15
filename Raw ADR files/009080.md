---
title:
  'ADR 001 – Comparison of Development Ecosystems for a Portfolio and Business
  Web application'
date: 2025-10-07
status: Accepted
deciders: [Em Jones, Platform/DevEx]
tags: [adr, pwa, ecosystem, open-source, long-term-maintenance]
---

## Context

We are designing an **open-source, long-lived progressive web application
(PWA)** for task management that should run on both desktop and mobile
devices.  
The project is intentionally **backend-agnostic**, prioritizing **developer
experience**, **codebase scalability**, **performance**, and **portability**.  
Because contributors may come from a diverse open-source background, the chosen
ecosystem should give priority to accessibility, documentation quality, and
over-time sustainability.

The following ecosystems evaluated for suitability:

- **Bun (with TypeScript)**
- **Node.js (with TypeScript)**
- **Deno (with TypeScript)**
- **.NET (≥ 6)**
- **Golang**
- **Rust**
- **Elixir**
- **Java**
- **PHP**
- **Ruby**
- **Other considerations**

---

## Decision drivers

| Priority | Factor                  | Description                                                                      |
| -------- | ----------------------- | -------------------------------------------------------------------------------- |
| 1        | Developer Experience    | Simplicity, ergonomics, scaling maintainable codebases, open-source friendliness |
| 2        | Application Performance | Runtime speed, memory footprint, startup time, and client bundle size            |
| 3        | Ecosystem Maturity      | Availability of PWA libraries, community health, long-term support               |
| 4        | Deployment Flexibility  | Compatibility with serverless, containerized, and edge environments              |

---

## Comparison summary

| Ecosystem                       | Developer Experience                                        | Performance                                     | Ecosystem Maturity                                   | Deployment Flexibility                                    | Notes                                               |
| ------------------------------- | ----------------------------------------------------------- | ----------------------------------------------- | ---------------------------------------------------- | --------------------------------------------------------- | --------------------------------------------------- |
| **Bun + TypeScript**            | Adequate speed, modern APIs, minimal config; still evolving | Fast startup, strong bundler/tester performance | Young but growing at a fast pace                     | Great for edge/serverless; still stabilizing              | Ideal for new projects but some tooling gaps remain |
| **Node.js + TypeScript**        | Familiar, large community, mature tooling (Nx, Turbo, etc.) | Solid performance, mature async model           | mature; largest JS ecosystem                         | Works everywhere: containers, serverless, edge            | Best all-around choice for open-source maintainers  |
| **Deno + TypeScript**           | Clean DX, secure by default, modern module system           | Comparable to Node; smaller ecosystem           | Moderately mature; smaller community                 | Well-suited for container/serverless deploys              | Great design but limited adoption so far            |
| **.NET (≥6)**                   | Strong language ergonomics (C#), robust tooling             | Strong and mature runtime JIT/AOT performance   | Enterprise-mature; smaller OSS contributor ecosystem | Good container/serverless support                         | Overkill for lightweight PWAs; complex toolchain    |
| **Golang**                      | Low-complexity language; fast builds; opinionated structure | High runtime performance; small binaries        | Mature ecosystem; less frontend/PWA focus            | Strong container & serverless support                     | Great for APIs; less suited for rich PWA dev        |
| **Rust**                        | high performance; strict compiler; steep learning curve     | Best-in-class runtime/memory performance        | Growing but limited web/PWA libs                     | Great portability; heavy compile times                    | Best for perf-critical backend pieces, not UI DX    |
| **Elixir (Phoenix LiveView)**   | Elegant concurrency, productive for realtime apps           | Fast throughput (`beam` VM)                     | Mature in niche; smaller OSS contributor resources   | Deploys well via containers; fewer serverless options     | Great for collaborative realtime backends           |
| **Java (Spring Boot, Quarkus)** | Verbose but mature; talent availability                     | Good runtime performance (`jvm` optimized)      | Decades-old maturity, stable                         | Strong portability characteristics; heavier runtime       | Enterprise-grade but not ideal for small OSS PWAs   |
| **PHP (Laravel, Symfony)**      | Portable onboarding; approachable syntax                    | Moderate performance; improved with JIT         | Massive ecosystem, declining modern use              | Straightforward deployments; still common on shared hosts | Better for SSR apps than PWAs                       |
| **Ruby (Rails)**                | Great DX, conventions over config                           | Slower runtime                                  | Mature but aging ecosystem                           | Straightforward deploy via containers or PaaS             | Strong DX but weak performance profile              |
| **Other (for example, Python)** | High approachability; dynamic typing                        | Slower startup, GIL limits                      | Mature but less suited to PWA bundling               | Strong container/serverless support                       | Better for automation than interactive PWAs         |

---

## Detailed analysis

### 1. Developer experience (highest priority)

- **Node.js + TypeScript** - currently, the most approachable and collaborative
  environment for open-source work: well-understood patterns, tooling (`eslint`,
  `prettier`, `vitest`, `vite`, `nx`), and ubiquitous CI support.
- **Bun** offers next-generation DX—integrated runtime, bundler, test runner—but
  contributors face occasional version churn and evolving APIs.
- **Deno**’s import-by-url model and permissions sandbox offer comfortable and
  powerful development ergonomics while having less familiarity with many
  contributors.
- **.NET, Rust, Java, and Elixir** have strong but steeper learning curves;
  **Ruby/PHP** easier initially but show their age at scale.

### 2. Application performance

- **Rust, Go, .NET, Elixir, and Bun** lead in raw runtime metrics.
- **Node.js/Deno** provide “fast enough” performance for PWAs—most performance
  wins come from frontend optimization rather than backend throughput.
- **Ruby/PHP** lag behind in concurrency and cold-start latency.

### 3. Ecosystem maturity

- **Node.js** dominates in libraries for PWAs/Web Applications, real-time sync
  (htmx, WebSockets), SSR (Next.js, Remix), and serverless integration.
- **Bun** reuses npm packages, but some rely on Node internals that differ
  slightly.
- **.NET, Java, and PHP** enormous ecosystems but less efficient/compatible for
  html-heavy web applications
- **Deno, Elixir, and Rust** ecosystems growing fast but not yet comparable in
  scope.

### 4. Deployment flexibility

- **Node.js and Bun** both shine: run anywhere—containers, Cloudflare Workers,
  Vercel, AWS Lambda.
- **Deno Deploy** mature for edge hosting.
- **Go, Rust, and .NET** compile to small, self-contained binaries; preferable
  for containerized or FaaS environments.
- **Elixir (`beam`)** performs well in containers while less serverless-native.

---

## Decision

**Adopt Node.js with TypeScript** as the primary framework for the portfolio and
business web application.

**Rationale:**

- Best balance across developer experience, maturity, performance, and
  portability.
- Ubiquitous contributor familiarity ensures long-term sustainability.
- Works seamlessly with modern frontend tooling (Vite, Next.js, Astro, Remix)
  and backend frameworks (Fastify, NestJS).
- Portable to any runtime (Node, Bun, Deno) if desired later.

**Secondary Consideration:**  
Track **Bun** as a future upgrade path once its API and package-compatibility
surface stabilize.

---

## Consequences

- **Benefits**
  - Fast development iteration cycle with TypeScript.
  - Wide hosting/deployment flexibility (serverless, edge, containers).
  - Large dependency and tool ecosystem.

- **Drawbacks**
  - Slightly lower raw performance than Go/Rust.
  - Occasional dependency churn due to npm ecosystem size.
  - Requires disciplined TypeScript config for maintainability.

---

## Alternatives considered

| Ecosystem         | Reason for Rejection                                           |
| ----------------- | -------------------------------------------------------------- |
| **Bun + TS**      | DX and performance promising, but ecosystem still stabilizing. |
| **Deno + TS**     | Elegant but smaller ecosystem adoption; limited contributors.  |
| **.NET**          | Complex toolchain with less purpose-built tooling              |
| **Golang**        | Great backend choice but limited PWA/UI support.               |
| **Rust**          | Overly complex for average open-source contributors.           |
| **Elixir**        | Powerful realtime backend, but niche beyond that scope.        |
| **Java/PHP/Ruby** | Mature but misaligned with **lightweight** PWA goals.          |

---

## References

- [Node.js Documentation](https://nodejs.org/)
- [Bun Documentation](https://bun.sh/docs)
- [Deno Documentation](https://deno.com/manual)
- [.NET Documentation](https://learn.microsoft.com/en-us/dotnet/)
- [Go Documentation](https://go.dev/doc/)
- [Rust Documentation](https://www.rust-lang.org/)
- [Elixir & Phoenix Docs](https://elixir-lang.org/)
- [Java Docs](https://dev.java/)
- [PHP Docs](https://www.php.net/)
- [Ruby on Rails Guides](https://guides.rubyonrails.org/)

---

## **Decision Summary:**

> For a long-lived, backend-agnostic PWA,  
> **Node.js with TypeScript** offers the strongest combination of developer
> experience, ecosystem maturity, and deployment flexibility—while remaining
> performant enough for modern use cases.
