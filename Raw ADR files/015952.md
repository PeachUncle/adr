# ADR 2: Communication Bridge (IPC) and Type Generation

Status: Accepted

Date: 2025-12-24

Deciders: Project Lead

## 1. Context and Problem Statement

To ensure high data integrity for the railway collection and maintenance logic, all "source of truth" business rules must reside in Rust. SvelteKit will be strictly limited to UI rendering. We need a communication strategy that allows the frontend to call these Rust functions with zero runtime type errors and maximum security.

## 2. Decision Drivers

- _Logic Centralization_: 100% of domain logic (collection rules, maintenance intervals) must live in Rust.
- _Type Safety_: The frontend must know exactly what data structures the backend expects/returns without manual synchronization.
- _Security_: Must avoid opening network ports (localhost) or loosening Tauri's security sandbox.
- _Scalability_: The solution must remain manageable with an estimated 50+ commands.

## 3. Considered Options

### Option A: Local Axum Server (Sidecar approach)

Run a Rust web server on a random port and use standard fetch from SvelteKit.

- Good because:
  - Familiar REST/OpenAPI patterns; allows organizing logic into standard routes (`/api/locomotives`).

- Bad because:
  - Security: Opens a network port on the user's machine, requiring complex capability management.
  - Complexity: Maintaining an OpenAPI/Swagger spec to generate TypeScript types is a high-overhead task.
  - Performance: Overheads of the network stack (loopback) compared to direct memory-based IPC.

### Option B: Tauri IPC + Specta (Chosen)

Use Tauri’s native invoke system and use the specta crate to export Rust types to TypeScript.

Good because:

- Native Security: Uses Tauri's internal IPC bridge (no open ports).
- Automated Type Safety: Specta generates `*.ts` definitions directly from Rust code during development.
- Speed: Fastest path between the WebView and the Rust process.

Bad because:

- Flat Namespace: Tauri commands are typically registered in a large flat list in main.rs.

## 4. Decision Outcome

Chosen Option: Tauri IPC with Specta Bindings

### Justification

The security risks and "cumbersome" configuration of a local Axum server outweigh its organizational benefits. While we anticipate 50+ commands, the Type Safety provided by Specta is critical for a complex domain like a model railway (where a "Locomotive" object might have dozens of nested properties).

### Consequences

Positive: Zero-cost type safety; if a field name changes in Rust, the SvelteKit build fails immediately.

Negative: We must manage a large `generate_handler![]` list.

Mitigation: To handle the "huge list," we will group commands into Rust modules (e.g., `commands::catalog`, `commands::collection`) and use a helper function to register them cleanly in tauri::Builder.

## 5. Implementation Note: Organizing 50+ Commands

To prevent main.rs from becoming unreadable, we will use the following pattern:
Rust

```rust
// In src/commands/mod.rs
pub fn all_commands() -> impl Fn(tauri::Invoke) {
    tauri::generate_handler![
        collection::get_trains,
        collection::add_train,
        catalog::add_railway_model,
        // ... etc
    ]
}
```
