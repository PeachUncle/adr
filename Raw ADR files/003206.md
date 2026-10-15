### **ADR-012: Choice of Dependency Management Strategy**

**Date:** 2025-09-14

**Status:** Decided & Implemented

### **Context**

The project was initially structured with two separate `package.json` files: one at the project root and one within the `packages/` directory structure. This led to a "split-brain" dependency model. While functional for a simple setup, adding a new dependency (`react-dropzone`) introduced a transitive dependency on a different version of React than the one specified in the frontend package.

This created a conflict where two instances of the React library were loaded at runtime, causing a critical crash: `Uncaught TypeError: Cannot read properties of undefined (reading 'ReactCurrentDispatcher')`. Initial attempts to resolve this using `npm overrides` in the root `package.json` were unsuccessful, indicating a deeper issue with the module resolution in our hybrid setup.

### **Decision**

We will adopt a **unified, monorepo-style workspace strategy** for all dependency management.

1.  **Single Source of Truth:** All project dependencies (`dependencies` and `devDependencies`) will be consolidated into the single `package.json` at the project root.
2.  **NPM Workspaces:** The root `package.json` will define a workspace that includes the `packages/` directory. This instructs NPM to install all packages in a single, shared `node_modules` folder at the root and create the necessary symbolic links.
3.  **Simplified Sub-Package:** The `packages/frontend/package.json` and `packages/backend/package.json` will contain service-specific metadata and scripts.

### **Consequences**

*   **Pros:**
    *   **Guaranteed Version Consistency:** This structure makes it impossible for conflicting versions of a package (especially React) to be installed. It directly resolves the `ReactCurrentDispatcher` error.
    *   **Simplified Dependency Management:** Developers only need to manage one `package.json` file. Running `npm install` from the root is now the single, authoritative command.
    *   **Easier Auditing & Updates:** Auditing for security vulnerabilities or updating packages is streamlined, as everything is in one place.
    *   **Improved Developer Experience (DX):** Reduces ambiguity and eliminates a class of "works on my machine" errors related to dependency resolution.

*   **Cons:**
    *   **Reduced Encapsulation:** The `packages/` structure is no longer fully self-contained projects. They are now explicitly tied to the root workspace. This is an acceptable trade-off for the gain in stability.
    *   **Workspace Awareness:** Developers must be aware that they are working in an NPM workspace and that all package management should happen at the root level.

### **Alternatives Considered**

1.  **`npm overrides`:** This was attempted first. It failed to resolve the issue, likely due to complexities in how Vite's bundler resolves modules from nested `node_modules` directories. It treated the symptom but not the underlying structural problem.
2.  **Native Drag-and-Drop Implementation:** We considered removing the `react-dropzone` dependency and building the feature with native browser APIs. While this would have solved the immediate error, it would have left the flawed dependency structure in place, risking similar conflicts with future packages. **Fixing the core project structure was deemed the more valuable long-term solution.**
