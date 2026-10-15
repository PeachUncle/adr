# ADR 0003: Automatic Frontend Environment Validation

## Status

Accepted

## Context

In our Rust backend (Loco.rs), missing environment variables cause an immediate crash on startup (a "fail-fast" mechanism). This is desirable as it prevents the application from running in a misconfigured state.

However, in our Next.js frontend (Node.js runtime), accessing a missing environment variable like `process.env.NEXT_PUBLIC_API_URL` simply returns `undefined`. This does not stop the build or the server. Instead, it leads to silent failures that only manifest as runtime errors (e.g., broken API calls) when a user interacts with the application.

We need a way to bring the backend's "fail-fast" reliability to the frontend, ensuring the application refuses to build or start if the environment is invalid.

## Decision

We will implement **Automatic, Explicit Validation** for all frontend applications using Zod.

1.  **Shared Public Schema:** We will define a `frontendSchema` in our centralized `@zouari-rs/validation` package. This will contain all public variables (prefixed with `NEXT_PUBLIC_`) that are shared across the stack.
2.  **App-Level Enforcement:** The `next.config.ts` file of each frontend application will be the enforcement point. Since this file is read during both `pnpm run dev` and `pnpm run build`, it guarantees validation happens before the app starts.
3.  **Server-Only Extension:** Inside `next.config.ts`, we will extend the shared `frontendSchema` to include app-specific, server-side secrets (e.g., `AUTH_SECRET`) that should not be exposed to the client or the shared package.
4.  **Blocking Behavior:** If validation fails, we will catch the Zod error, log a formatted message, and explicitly exit the process (`process.exit(1)`), stopping the deployment pipeline immediately.

## Consequences

### Positive

* **Fail-Fast Guarantee:** It is now impossible to deploy or start the frontend application with missing required variables.
* **Type Safety:** The Zod schema provides a single source of truth for the shape of our environment configuration.
* **Clear Debugging:** Instead of obscure runtime errors ("cannot read property of undefined"), developers get clear, formatted error logs at startup listing exactly which variables are missing.

### Negative

* **Boilerplate:** Every new frontend application requires a setup block in `next.config.ts` to import and enforce the schema.
* **Double Declaration:** Server-side secrets (like `AUTH_SECRET`) must be defined in `next.config.ts` validation logic, separate from the shared package.
