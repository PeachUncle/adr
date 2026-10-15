# ADR 1: Choice of Technology Stack

Status: Accepted

Date: 2025-12-24

Decider: Project Lead

## 1. Context and Problem Statement

The goal is to build a cross-platform application for model railway enthusiasts (likely covering inventory management). The application needs to run on Desktop (Windows/Linux/macOS) and Mobile (Android/iOS) to ensure users can access their data both at their workbench and while at exhibitions or clubs.

We need a framework that balances performance for business logic with a modern, flexible UI
system.

## 2. Decision Drivers

- _Portability_: Must support Desktop and Mobile from a single or highly shared codebase.
- _Performance_: Efficient handling of railway logic or database operations.
- _Sustainability_: Low "bus factor" and strong documentation.
- _User Experience_: Small installation footprint and responsive UI.

## 3. Considered Options

### Option A: GTK 4 using Relm4 (Rust)

Pros:

- Native performance on Linux; leverages Rust’s type safety.

Cons:

- No Mobile Support: Does not target Android or iOS.
- Developer Experience: The API is complex with sparse documentation.
- Risk: The relm4 project has a very low bus factor (dependent on very few maintainers).

### Option B: Kotlin Multiplatform (KMP)

Pros:

- Native performance and integration on Android.
- Strong tooling (IntelliJ/Android Studio) and a robust language (Kotlin).
- Excellent for sharing logic across platforms.

Cons:

- Ecosystem Maturity: Many libraries and APIs are still in "Experimental" phases.
- Desktop Overhead: Requires a JVM on desktop, leading to significantly larger bundle sizes and higher memory usage.

### Option C: Tauri 2 (Rust + Web Frontend)

Pros:

- Small Footprint: Extremely small bundle sizes as it uses the system's native WebView.
- Logic Performance: Uses Rust for the "heavy lifting" (business logic, file I/O).
- UI Flexibility: Allows using any modern JS/TS framework (React, Vue, Svelte) for a highly polished UI.
- Mobile Support: Tauri 2.0 introduces first-class support for Android and iOS.

Cons:

- Non-Native UI: While it uses native windows, the content inside is web-based, which may not always feel "100% native" without extra CSS effort.

## 4. Decision Outcome

Chosen Option: Tauri 2

### Justification

Tauri 2 provides the best compromise between the efficiency of Rust and the ubiquity of Web Technologies. It solves the "Mobile" requirement that disqualified GTK 4, while avoiding the "JVM bloat" and experimental instability associated with KMP on desktop.

The ability to write railway simulation or logic in Rust ensures the app remains fast, while the JS ecosystem provides the best tools for building the complex, data-heavy interfaces required for model railway management.

### Consequences

- _Positive_: We can deploy a <10MB installer on desktop.
- _Positive_: We gain access to the entire NPM ecosystem for UI components (charts, drag-and-drop, etc.).
- _Negative_: We must manage a "Bridge" (IPC) between the Rust backend and the JavaScript frontend.
- _Neutral_: Developers must be comfortable context-switching between Rust and TypeScript.
