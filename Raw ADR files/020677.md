# ADR 0002: Add Centralized Zod Validation Package

## Status

Accepted

## Context

We are building a monorepo with a Rust backend and (future) TypeScript frontends. To ensure reliability and a good user experience, we must validate data in two places:
1.  **Backend (Rust):** For security and data integrity.
2.  **Frontend (TypeScript):** For fast, client-side user experience.

We need a "set it and forget it" workflow where the backend's API contract is the single source of truth, and our frontend validation logic is automatically generated from it.

During implementation, we discovered a critical distinction:
* **Runtime Validation:** In Rust, `#[validate(email)]` from the `validator` crate checks data *at runtime*.
* **API Contract:** `#[derive(ToSchema)]` from `loco_openapi` (re-exporting `utoipa`) *only* defines the API schema.

These two systems are **not** automatically linked. A `#[validate]` attribute does not inform the `ToSchema` derive, so our initial OpenAPI spec simply said `"type": "string"` for emails, not `"format": "email"`. This led to our frontend tests (correctly) failing, as they were flagging a mismatch between our *expectations* and the *actual contract*.

## Decision

We will create a new, centralized validation package, `@zouari-rs/validation`, to solve this. This package will act as the "bridge" between the backend contract and all frontend applications.

1.  **Package:** `@zouari-rs/validation` will be created. It will contain both manually-defined schemas (e.g., `src/env.ts`) and auto-generated schemas.

2.  **Tooling:** We will use `@hey-api/openapi-ts` and its built-in `zod` plugin. It is Zod v4 compatible and correctly generates schemas from an OpenAPI spec.

3.  **Source of Truth:** The `openapi.json` file served by the running Rust backend is the definitive API contract.

4.  **Backend Policy (The Core Fix):** To ensure the API contract is accurate, developers **must** use both `#[validate]` and `#[schema]` annotations on all data-transfer objects (DTOs). The `#[validate]` rule enforces Rust's runtime, and the `#[schema]` rule informs the `openapi.json` contract.

    **Example (`backend/src/models/users.rs`):**

    ```rust
    use validator::Validate;
    use loco_openapi::prelude::*; // Provides ToSchema and schema

    #[derive(Debug, Deserialize, Serialize, ToSchema, Validate)]
    pub struct LoginParams {
        #[validate(email)]
        #[schema(format = "email", example = "user@example.com")]
        pub email: String,

        #[validate(length(min = 8))]
        #[schema(min_length = 8)]
        pub password: String,
    }
    ```

5.  **Workflow:** A new root script, `pnpm run sync:schemas`, will be the standard workflow for developers. This script chains `curl` (to fetch the `openapi.json`) and `pnpm --filter @zouari-rs/validation generate:schemas` (to run `openapi-ts`).

6.  **Contract Testing:** The Vitest tests in `@zouari-rs/validation` (e.g., `tests/api.test.ts`) are a non-negotiable part of this workflow. They serve as the **end-to-end "contract test"**. A failing test (as we experienced) correctly signals that the API contract is out of sync with developer expectations.

## Consequences

### Positive

* **Reliable Contract:** The "fail-fast" test in `packages/validation` proves that our frontend schemas are perfectly aligned with the backend's `openapi.json`.
* **Single Source of Truth:** The "set it and forget it" goal is achieved. We edit Rust structs, and this change propagates all the way to frontend Zod schemas via an automated, test-verified path.
* **Developer Experience:** Frontend applications can now import `@zouari-rs/validation/api` and receive Zod schemas that are guaranteed to match the backend contract.

### Negative

* **Workflow Discipline:** This solution is not fully automatic. It relies on developer discipline to:
    1.  Remember to add **both** `#[validate]` and `#[schema]` annotations in Rust.
    2.  Remember to run `pnpm run sync:schemas` after starting the backend.
* **"Leaky" Abstraction:** A developer must understand *why* both annotations are needed; the system does not enforce it at compile time.
