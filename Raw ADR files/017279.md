# 001 – Framework Choice

## Status  
Accepted | 2025-05-26

---

## Context  
The team needs a full-stack web solution that:  
- supports TypeScript end-to-end,  
- is modular and testable for business rules (parking constraints, check-in, etc.),  
- offers a fast, modern front-end developer experience,  
- runs easily in Docker and fits our skill set (TypeScript background).

---

## Decision  
- **Backend**: NestJS 11 (TypeScript)  
  - Opinionated modular architecture with built-in DI  
  - Class-based validation, pipes and guards out of the box  
  - Easy REST endpoints plus optional WebSockets  
  - First-class TypeORM integration  
  - Excellent testability with Jest  

- **Frontend**: Vue 3 + Vite + TypeScript + Pinia + Vue Router  
  - Lightweight, Composition API for fine-grained reactivity  
  - Vite’s super-fast HMR and minimal config  
  - Tailwind CSS integration with utility-first styling  
  - Familiarity: our team has already shipped Vue apps  

- **Language**: 100 % TypeScript (monorepo)  
  - Shared DTOs and types between front and back  
  - Eliminates context switching  

---

## Alternatives Considered

### Backend  
- **Spring Boot (Java)**  
  - Pros: very mature ecosystem, strong typing, enterprise support  
  - Cons: heavier setup, slower startup, team has less recent Java experience  

- **Express.js (TypeScript)**  
  - Pros: minimal, highly flexible  
  - Cons: no built-in DI or conventions → risk of ad-hoc architecture  

- **AdonisJS**  
  - Pros: batteries-included, full MVC  
  - Cons: smaller community, learning curve  

**Why NestJS?**  
It strikes the right balance: structured conventions, powerful CLI, DI, and test support—while staying in TypeScript and matching our team’s existing skills.

### Frontend  
- **React**  
  - Pros: very popular, rich ecosystem  
  - Cons: JSX boilerplate, more conventions to learn for newcomers  

- **Angular**  
  - Pros: all-in-one framework, strong typing  
  - Cons: steep learning curve, larger bundles  

- **Svelte Kit**  
  - Pros: highly performant, minimal overhead  
  - Cons: less mature ecosystem, team unfamiliar  

**Why Vue 3 + Vite?**  
Our team has demonstrable Vue expertise; Vite’s zero-config setup plus lightning-fast HMR makes iteration delightful.

---

## Consequences  
- **Single language across stack** → reduced cognitive load.  
- **Onboarding**: new team members need to learn NestJS and Vue 3 if unfamiliar.  
- **Build chain**: Node-centric, Docker images must include Node runtime.  
- **DX**: fast CLI generators and hot-reload accelerate development.