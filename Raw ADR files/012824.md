# ADR-001: Backend Framework

## Status

Accepted

## Context

We need to choose a backend framework for the Ohana Booking System API. The system will handle:

- CRUD operations for inquiries, bookings, performers, and clients
- Authentication and authorization (admin, coordinator, performer roles)
- Financial tracking (payments, payouts, expenses)
- Background jobs (notifications, reminders)
- Integration points (future: webhooks, third-party APIs)

This is a **solo developer project** with **resume-building** as a secondary goal alongside shipping a production application.

## Decision Drivers

- **Job market visibility**: Framework popularity in enterprise settings
- **Learning investment**: Time spent learning should transfer to future projects
- **Existing experience**: Developer has a past NestJS project to reference
- **AI assistance**: Modern tooling and LLMs can offset boilerplate complexity
- **Ecosystem maturity**: Rich ecosystem for common patterns (auth, validation, ORM)
- **Development velocity**: Need to ship Phase 1 in ~4 weeks

## Options Considered

### Option A: NestJS

**Pros:**

- ✅ **Excellent resume builder** - most common in enterprise job postings
- ✅ **Huge ecosystem** - packages for everything (auth, validation, queues, swagger)
- ✅ **TypeScript-first** - strong typing throughout
- ✅ **Modular architecture** - testable, maintainable at scale
- ✅ **Developer has existing NestJS project** to reference - reduces learning curve
- ✅ **AI copilots excel** at generating NestJS boilerplate
- ✅ **Transferable knowledge** - likely to use NestJS professionally in future
- ✅ **Clear conventions** - dependency injection, decorators, module system

**Cons:**

- ❌ **More boilerplate** - modules, providers, decorators for everything
- ❌ **Steeper initial learning curve** - DI, lifecycle hooks, decorators
- ❌ **Slower initial velocity** - more setup required than batteries-included frameworks
- ❌ **Over-engineering risk** - easy to add unnecessary abstractions

### Option B: AdonisJS v6

**Pros:**

- ✅ **Batteries-included** - ORM, auth, validation, queue out of the box
- ✅ **Faster initial velocity** - strong conventions, less decision fatigue
- ✅ **Simpler mental model** - less abstraction than NestJS
- ✅ **Great DX** - similar to Laravel (familiar patterns)
- ✅ **TypeScript support** - first-class TS integration

**Cons:**

- ❌ **Smaller ecosystem** - fewer third-party integrations
- ❌ **Less resume value** - uncommon in enterprise job postings
- ❌ **Starting from scratch** - no prior Adonis experience
- ❌ **Uncertain future need** - may never use Adonis professionally

### Option C: Express.js (Minimalist)

**Pros:**

- ✅ **Minimal** - only add what you need
- ✅ **Flexible** - no opinions
- ✅ **Widely known** - every Node developer knows Express

**Cons:**

- ❌ **Too much manual work** - need to wire up everything yourself
- ❌ **No structure** - easy to create inconsistent patterns
- ❌ **Not modern** - losing ground to newer frameworks

## Decision

**We will use NestJS as the backend framework.**

### Rationale

1. **Resume building is a valid goal** - NestJS experience directly translates to employability
2. **Past project eliminates learning curve** - developer can reference existing NestJS codebase
3. **AI assistance changes the game** - copilots handle boilerplate pain
4. **4-week timeline is sufficient** - even with NestJS overhead
5. **Future-proof investment** - skills will be reused in professional contexts
6. **Avoid regret** - Learning Adonis now may not be useful later; learning NestJS will be

### Implementation Guidelines

**To maintain velocity:**

- ✅ Keep modules simple - avoid premature abstraction
- ✅ Use NestJS CLI for generation - don't hand-write boilerplate
- ✅ Leverage existing NestJS project patterns
- ✅ Use AI for repetitive module/service/controller creation
- ✅ Focus on functionality over architecture purity

## Consequences

### Positive

- Resume shows modern, enterprise-relevant technology stack
- Skills transfer directly to future professional work
- Strong ecosystem support (auth, ORM, BullMQ queues, testing, swagger)
- Modular codebase will scale well if project grows
- Excellent TypeScript integration throughout
- Can reuse this stack for future projects (standardized approach)

### Negative

- Initial setup takes longer than batteries-included alternatives
- More files and abstractions to manage
- Risk of over-engineering if not disciplined
- Steeper onboarding for future contributors (if any)

### Risks

- **Velocity risk**: Boilerplate could slow Phase 1 delivery
  - _Mitigation_: Use CLI generators, AI assistance, and reference past project
- **Complexity creep**: Easy to add unnecessary abstractions
  - _Mitigation_: Follow "start simple" principle - add complexity only when needed

## Follow-up Actions

- [x] Choose ORM (see ADR-003)
- [x] Choose auth strategy (see ADR-006)
- [ ] Set up NestJS project scaffold with CLI
- [ ] Configure core modules (auth, database, config)
- [ ] Establish coding conventions document
