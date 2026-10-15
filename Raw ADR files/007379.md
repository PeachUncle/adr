# ADR-013: Backend-Free Philosophy (CharacterCraft Lite)

## Status
Accepted

## Context
CharacterCraft Lite was designed from the beginning to be:

- Easy to share and run **without setup**
- Friendly for **educational use**, browser demos, and workshops
- Fully functional **offline**, even when disconnected

Given this intent, we deliberately chose to keep the Lite version **backend-free**, relying only on frontend technologies and browser APIs (e.g., localStorage, fetch, clipboard).

## Decision
The Lite edition of CharacterCraft will remain **frontend-only** and not depend on any server, database, or hosted API.

Key principles:
- No login or authentication required
- No cloud or storage dependencies
- Everything runs in the browser — no install or account needed
- Generated content is downloaded or copied by the user only

This allows:
- Portability (single-file use)
- Offline-first Progressive Web App (PWA) support
- Zero setup for instructors, students, or casual users
- GitHub Pages-friendly deployment with no backend logic

## Consequences
✅ Maximizes portability and ease of use  
✅ Enables full offline support via PWA  
✅ Simplifies deployment and hosting  
✅ Encourages local-first and privacy-respecting design  
⚠️ Limits complexity of dynamic features (e.g., user accounts, saved profiles)
⚠️ Some advanced use cases (e.g., collaborative editing, saved sessions) are deferred to the Pro/API version

## Future Considerations
While Lite remains backend-free, we are planning a **Pro or SaaS edition** of CharacterCraft with:
- A backend powered by API endpoints
- Support for saved personas and reusable templates
- Secure access to RAG pipelines and model configurations
- Integration with hosted vector databases, LLMs, or third-party services

These features will live in a **separate repo** and not compromise the simplicity of the Lite edition.

---

*This ADR reflects our commitment to accessibility, transparency, and empowering users without requiring infrastructure.*

