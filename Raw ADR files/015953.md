# ADR 3: Layered Domain-Driven Design (DDD) for Feature Implementation

Status: Accepted

Date: 2026-01-08

Deciders: Project Lead

## 1. Context and Problem Statement

As the Tauri application grows, we face increasing complexity in managing state, database transactions, and business logic. Without a formal structure, the Rust backend risks becoming a collection of "fat" Tauri commands where IPC logic, database queries, and business rules are tightly coupled. This makes unit testing difficult and increases the risk of partial database writes (lack of atomicity).

## 2. Decision Drivers

- _Data Integrity_: All database operations within a single user action must be atomic.
- _Testability_: Business logic must be testable without requiring a running SQLite instance or a Tauri environment.
- _Type Safety_: We must maintain strict type safety across the Rust-TypeScript bridge.
- _Decoupling_: The "Core" logic should not know that it is being called by Tauri or that it is persisting to SQLite.

## 3. Considered Options

### Option A: Clean Architecture with Unit of Work (The Proposed Design)

A four-layer approach (Domain, Application, Infrastructure, Interface) using a Repository Pattern and a trait-extended Unit of Work.

- Good, because: Provides the highest level of isolation. Business logic is pure and easily mockable. The UoW ensures that if a Use Case fails, the transaction is never committed.
- Bad, because: Significant boilerplate. Every new feature requires a Trait, a Struct, a Use Case, and a Command.

### Option B: Transaction-Passing Functional Services

Passing a mutable reference to a transaction (`&mut SqliteTransaction`) directly through simple function calls.

- Good, because: Much faster to implement; less "boilerplate" code and fewer traits to manage.
- Bad, because: Harder to mock for unit tests. The business logic becomes "aware" of the database technology (SQLite), violating the Dependency Inversion Principle.

### Option C: Vertical Slices (Feature-Based Modules)

Instead of horizontal layers (all Repos together), everything for a single feature is kept in one module.

- Good, because: High cohesion. You don't have to jump between four different folders to understand how "Create Model" works.
- Bad, because: Can lead to code duplication across features if shared logic isn't carefully managed.

## 4. Decision Outcome

Chosen Option: Clean Architecture with Unit of Work (Option A)

### Justification

This option was chosen because the long-term maintainability of the project outweighs the initial cost of boilerplate. The use of the `RailwayModelUowExt` trait specifically solves the Rust "borrow checker" issues often found when trying to share a transaction across multiple repositories, providing a safe, factory-like interface for data access.

### Consequences

Positive:

- Atomicity by Default: The Interface layer (Tauri Command) controls the transaction lifecycle, making it impossible to forget a `commit()` or `rollback()`.
- Framework Agnostic: If we ever move away from Tauri to a web-based backend, the Application and Domain layers remain 100% untouched.

Negative:

- Learning Curve: New developers must understand the "Trait Extension" pattern for the UoW to access repositories.
- File Proliferation: A simple feature might require 4-5 new files.

Neutral:

- Continuous use of specta is required to ensure the Interface layer stays in sync with the Frontend.
