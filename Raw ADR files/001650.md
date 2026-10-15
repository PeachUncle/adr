# ADR 002: Technical Stack & Architecture Decisions

## Status
Proposed

## Context
We need to select the specific technologies and architectural patterns to implement the Client-Server architecture defined in `spec/001-architecture.md`. The detailed requirements include a web server (Bridge), a UI (Dashboard), and specific behavior regarding long-running tasks.

## Decisions

### 1. Backend Framework
**Decision**: Use **FastAPI**.
- **Reasoning**: 
    - Native support for asynchronous operations (`async def`), which is critical for handling concurrent LLM requests and bridging the UI and Spreadsheet simultaneously.
    - Automatic generation of OpenAPI documentation helps with "Function Discovery" requirements.
    - Lightweight and easy to bundle.

### 2. Management UI Framework
**Decision**: Use **NiceGUI**.
- **Reasoning**:
    - **Single Process**: NiceGUI runs on top of FastAPI. This allows us to run *both* the Bridge API and the Management UI in a single Python process/entry point. This simplifies distribution and startup (users only run one command).
    - **Event-Driven**: Unlike Streamlit (which re-runs the whole script on interaction), NiceGUI handles events efficiently, making it better for a "Control Panel" that needs to toggle states (Pause/Resume) without screen flickering or state loss.

### 3. Database / Persistence
**Decision**: Use **SQLite**.
- **Reasoning**: 
    - We need to persist execution history (REQ-UI-003) and configuration.
    - Zero-configuration (file-based).
    - Lightweight compared to running a separate Postgres/Redis container.

### 4. Concurrency & Spreadsheet Blocking
**Decision**: **Synchronous (Blocking) Calls for V1**.
- **Context**: LibreOffice UDFs (User Defined Functions) typically block the UI thread until they return.
- **Reasoning**: 
    - Implementing true async behavior in LibreOffice (where the cell says "Loading..." and updates later) requires complex event listeners and macro orchestration.
    - **Risk**: The spreadsheet will freeze while the Agent runs.
    - **Mitigation**: The Management UI will control the "Bridge". We can implement a timeout on the spreadsheet side (e.g., 5 seconds). For very long tasks, we might move to a "Job Submission" model in V2, but for V1, blocking is the simplest implementation path to prove the concept.

## Consequences
- The system will be a single Python application (FastAPI + NiceGUI).
- Users will launch one executable/script to start the backend.
- Long-running agents will temporarily freeze the LibreOffice window (Accepted trade-off for V1).
