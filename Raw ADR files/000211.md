# ADR-003: Service Port Configuration Strategy

**Status:** Accepted  
**Date:** 2025-07-01  
**Deciders:** Development Team  

## Context

Mulisa runs multiple services that need distinct ports:

- Client (React/Vite dev server)
- Server (Socket.IO signaling server)  
- AI Service (Future LLM integration)

We discovered port 5000 conflicts with macOS AirPlay Receiver, requiring a port strategy that avoids common conflicts.

## Decision

**Standard port allocation:**
- **Client**: 3000 (Vite default)
- **Server**: 3001 (avoiding 5000 macOS conflict)
- **AI Service**: 5001 (reserved for future use)

## Rationale

### Avoid System Conflicts
- **macOS AirPlay**: Uses port 5000, conflicts with many development servers
- **Common services**: Avoid ports used by system services
- **Development tools**: Align with standard tool defaults where possible

### Logical Grouping
- **3000-3099**: Frontend services (client, potential admin interfaces)
- **5000-5099**: Backend services (AI, data processing)
- **3001**: Signaling/communication layer (bridges frontend/backend)

### Documentation & Maintenance
- **Clear mapping**: Easy to remember and document
- **Consistent across environments**: Same ports dev/staging/production
- **Port range reservation**: Room for additional services in logical groups

## Consequences

### Positive
- ✅ No conflicts with macOS AirPlay or other system services
- ✅ Logical grouping makes service architecture clear
- ✅ Room for growth within defined ranges
- ✅ Easy to remember and document

### Negative
- ⚠️ Non-standard for some tools (typical signaling might use 8080, etc.)
- ⚠️ Requires updating all documentation when changed
- ⚠️ May need firewall rules in production

## Implementation

```javascript
// server/index.js
const PORT = process.env.PORT || 3001;

// client/src/services/socket.ts  
constructor(serverUrl: string = 'http://localhost:3001')

// Future: ai-service/index.js
const AI_PORT = process.env.AI_PORT || 5001;
```

## Documentation Updates Required

All port references updated in:
- README.md
- docs/port-configuration.md
- docs/architecture-visual.html
- Mermaid diagrams in docs/architecture/diagrams/
- Client socket service configuration

## Review Criteria

Review if:
- Additional services need port allocation
- Production deployment requires different strategy
- Docker containerization changes port management needs
- Team reports confusion about current scheme

---

**Related:** ADR-001 (Persistent Connections), ADR-002 (WebRTC Signaling)
