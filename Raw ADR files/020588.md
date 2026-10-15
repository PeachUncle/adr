# ADR 001: Firebase as Backend Platform

## Status

Accepted

## Context

We need a backend platform for the Texas Hold'em poker game that provides:

- Real-time data synchronization for multiplayer gameplay
- User authentication
- Serverless functions for game logic
- Database for game state and player data
- Free tier that supports 10-50 concurrent players

## Decision

Use Firebase (Google Cloud Platform) as the complete backend solution:

- Firebase Firestore for real-time database
- Firebase Authentication for player identity
- Firebase Functions for serverless game logic
- Firebase Hosting for static asset delivery

## Consequences

### Positive

- **Real-time sync**: Firestore provides WebSocket-based real-time updates with minimal latency
- **Free tier**: Generous limits support hobby-scale usage without costs
- **Integrated ecosystem**: Auth, database, functions, and hosting work seamlessly together
- **No server management**: Serverless architecture eliminates DevOps overhead
- **Security rules**: Built-in authorization at database level
- **Local development**: Firebase Emulator Suite enables offline development

### Negative

- **Vendor lock-in**: Migration away from Firebase would require significant refactoring
- **Query limitations**: Firestore has constraints on complex queries (acceptable for our use case)
- **Cold start latency**: Functions may have initial invocation delays (mitigated by keeping functions warm)
- **Cost uncertainty**: If usage exceeds free tier, costs could escalate (monitoring required)

### Neutral

- **NoSQL database**: Requires denormalized data model (acceptable, common pattern)
- **JavaScript/TypeScript only**: Functions limited to Node.js runtime (aligns with our stack)

## Alternatives Considered

- **Self-hosted**: Would require server management, higher complexity, ongoing costs
- **AWS Amplify**: Similar offering but steeper learning curve, less generous free tier
- **Supabase**: Real-time PostgreSQL but requires more infrastructure knowledge

## Compliance

- ✅ **Constitution I (TDD)**: Firebase Emulator Suite supports local testing
- ✅ **Constitution III (Performance-First)**: Real-time updates <100ms p95
- ✅ **Constitution IV (Client-Server Separation)**: Functions enforce server-authoritative logic
- ✅ **Cost constraint**: Free tier sufficient for target scale (10-50 users)
