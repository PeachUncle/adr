# ADR 0007 — Local Development Orchestration

**Status:** Accepted  
**Date:** 2025-11-05  
**Tags:** #adr #architecture #development #orchestration

---

## 📘 Context

Local development requires running 4 separate services:
- Redis (queue backend)
- API Gateway (Node.js/TypeScript, port 3000)
- Transcription Worker (background process)
- Whisper Service (Python/FastAPI, port 8000)

This creates significant friction for developers who must:
1. Open multiple terminal windows
2. Remember startup order and commands
3. Manage background processes manually
4. Handle Redis installation and configuration

The team needs a simpler way to bootstrap the development environment while maintaining the existing microservice architecture.

---

## 💡 Decision

Implement a bash script (`start-dev.sh`) that orchestrates all services with a single command:

```bash
# Full stack development
./start-dev.sh

# Mock mode (no Whisper service needed)
./start-dev.sh --mock
```

The script:
- Starts Redis as a daemon process
- Launches API Gateway in foreground
- Runs Worker and Whisper Service as background processes
- Supports mock mode to reduce dependencies
- Uses existing `USE_MOCK_WHISPER` functionality

---

## 🧩 Rationale

| Option | Pros | Cons |
|--------|------|------|
| Bash script | Immediate solution, leverages existing mock mode, single command | Platform-dependent, manual process management |
| Docker Compose | Production-like, cross-platform, consistent environments | Complex setup, requires Docker knowledge, not yet implemented |
| Manual setup | Full control, no abstraction | Time-consuming, error-prone, multiple terminals |

**Chosen approach:** Bash script provides immediate value with minimal complexity while leveraging the existing mock functionality already built into the codebase.

---

## ⚙️ Consequences

**Benefits:**
- Single command startup reduces developer friction
- Mock mode allows development without Whisper dependencies
- Maintains existing microservice architecture
- No additional tooling requirements beyond bash

**Trade-offs:**
- Platform-dependent (requires bash and Unix-like environment)
- Manual process management (background processes)
- Not production-like (unlike Docker)
- Requires Redis to be installed locally

---

## 🔮 Future evolution

**Migration criteria to Docker Compose:**
- Multiple developers joining the team
- Cross-platform development needs (Windows/macOS)
- CI/CD pipeline requirements
- Production parity concerns

**Signals for re-evaluation:**
- Developer onboarding becomes bottleneck
- Platform compatibility issues arise
- Need for consistent development environments
- Team growth beyond 2-3 developers

---

**Related ADRs:**  
- [0004-job-enqueu-process.md](./0004-job-enqueu-process.md)

**Supersedes:** none  
**Superseded by:** none