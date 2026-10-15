### **ADR-013: Aligning Node.js Module Systems for Backend Compatibility**

**Date:** 2025-09-14

**Status:** Decided & Implemented

### **Context**

Following the adoption of an NPM workspace structure (ADR-012), a critical runtime error emerged when starting the backend API server: `ReferenceError: require is not defined in ES module scope`.

This error was caused by a conflict between two different JavaScript module systems:

1.  **ES Modules (ESM):** The `packages/frontend/package.json` file contains `"type": "module"`, a directive required by the Vite frontend ecosystem. This instructs Node.js to treat all files with a `.js` extension within that directory as modern ES Modules (using `import`/`export`).
2.  **CommonJS (CJS):** The backend API, built with Express, was written using the traditional Node.js module system, CommonJS (using `require()`/`module.exports`).

When Node.js attempted to run `api/server.js`, it respected the `"type": "module"` directive and tried to interpret the file as ESM. This failed immediately because the `require()` function is not a valid construct in the ES Module system.

### **Decision**

We will align the backend API code to be explicitly recognized as CommonJS by Node.js, while allowing the frontend code to remain as ES Modules. This will be achieved by **renaming all server-side JavaScript files in the `packages/backend/api/` directory and its subdirectories from the `.js` extension to the `.cjs` extension.**

The `.cjs` extension serves as an explicit instruction to the Node.js runtime to interpret these specific files using the CommonJS loader, thereby overriding the package-level `"type": "module"` directive. All internal `require()` paths within the backend were also updated to point to the new `.cjs` files.

### **Consequences**

*   **Pros:**
    *   **Resolves the Runtime Crash:** This change directly fixes the `require is not defined` error, allowing the backend server to start correctly.
    *   **Clear Separation of Concerns:** It creates a clear and explicit distinction between the frontend's ESM code and the backend's CJS code, even though they coexist in the same workspace. This reduces ambiguity.
    *   **Minimal Code Refactoring:** This approach allows us to keep the existing, stable CommonJS code for the backend without undertaking a risky and time-consuming migration of the entire Express API to ESM syntax.
    *   **Preserves Frontend Tooling:** It does not interfere with Vite's expectation that the frontend source code (`.tsx`, `.ts`) is handled as ES Modules.

*   **Cons:**
    *   **Mixed Module System:** The project now officially contains two different module systems. Developers must be aware of this context and use the correct syntax (`.cjs` for backend, `.ts`/`.tsx` for frontend). This is a minor but acceptable complexity.

### **Alternatives Considered**

1.  **Migrate the Entire Backend to ES Modules:** This would involve changing all `require()` statements to `import` and `module.exports` to `export`. This was rejected because:
    *   It would be a significant, time-consuming refactor with a high risk of introducing subtle bugs.
    *   Some older Express middleware and libraries have historically had tricky interoperability with ESM.
    *   The current CJS implementation is stable and well-understood; there was no compelling business reason to rewrite it.
2.  **Remove `"type": "module"` from `packages/frontend/package.json`:** This was rejected as it would break the Vite build process and violate the conventions of the modern frontend tooling we are using.
3.  **Run Backend from a Separate Workspace:** We could have moved the `api` folder into its own workspace without `"type": "module"`. The chosen solution was simpler and kept the backend and frontend logically grouped within the `packages/` directory structure.
