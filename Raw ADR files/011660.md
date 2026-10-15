# API Design Decisions

**Version**: 1.0  
**Date**: 2025-01-15  
**Author**: API Designer Agent

## Overview

This document captures key design decisions made for the Mile Quest API, including rationale and trade-offs.

## Key Design Decisions

### 1. REST over GraphQL

**Decision**: Use REST API with field filtering rather than GraphQL

**Rationale**:
- Simpler implementation for MVP
- Better caching with CloudFront
- Easier offline support
- Lower complexity for mobile clients
- Team expertise with REST

**Trade-off**: Less flexible querying, but mitigated by:
- Optimized dashboard endpoint
- Field filtering parameters
- Proper resource modeling

### 2. Single Dashboard Endpoint

**Decision**: Create `/api/dashboard` that returns all dashboard data

**Rationale**:
- Mobile-first performance (single request)
- Reduced latency on slow connections
- Simplified client logic
- Better offline caching

**Trade-off**: Less granular caching, but acceptable for MVP

### 3. Cursor-Based Pagination

**Decision**: Use cursor pagination instead of offset/limit

**Rationale**:
- Better performance for large datasets
- Stable pagination (no skipped items)
- Works well with real-time updates
- Standard practice for mobile APIs

**Implementation**:
```typescript
{
  "items": [...],
  "nextCursor": "encoded_cursor",
  "hasMore": true
}
```

### 4. Activity Privacy Design

**Decision**: Single `isPrivate` boolean flag on activities

**Rationale**:
- Simple to implement and understand
- Covers MVP privacy requirements
- Easy to enforce in queries
- Clear user mental model

**Rules**:
- Private activities hidden from public leaderboards
- Private activities ALWAYS count for team totals
- Users can always see their own private activities

### 5. Multi-Team Activity Support

**Decision**: Activities can count for multiple teams via `teamIds[]`

**Rationale**:
- Users often in multiple teams
- Avoids duplicate activity logging
- Single source of truth
- Better data integrity

**Trade-off**: Slightly more complex activity creation

### 6. Authentication Token Strategy

**Decision**: Short-lived access tokens (1hr) with refresh tokens

**Rationale**:
- Security best practice
- Allows token revocation
- Reduces impact of token theft
- Standard OAuth2 pattern

**Implementation**:
- Access token in Authorization header
- Refresh token in secure HTTP-only cookie
- Automatic refresh on 401 responses

### 7. Optimistic Updates Support

**Decision**: Return calculated new states in mutation responses

**Rationale**:
- Enables smooth optimistic UI updates
- Reduces follow-up API calls
- Better perceived performance
- Critical for mobile experience

**Example**:
```typescript
// POST /api/activities response includes:
"teamUpdates": [
  {
    "teamId": "...",
    "newTotalDistance": 15420,
    "newPercentComplete": 31.5
  }
]
```

### 8. Invite Code System

**Decision**: Use 6-character alphanumeric codes for team invites

**Rationale**:
- Easy to share verbally
- Works with QR codes
- No email dependency
- Simple implementation

**Format**: `[A-Z0-9]{6}` (e.g., `A3B7X9`)

### 9. Error Response Consistency

**Decision**: Consistent error format with codes and messages

**Rationale**:
- Predictable client error handling
- I18n support via error codes
- Debugging-friendly messages
- Machine-readable codes

**Format**:
```typescript
{
  "success": false,
  "error": {
    "code": "TEAM_FULL",
    "message": "Team has reached maximum capacity of 50 members"
  }
}
```

### 10. Timezone Handling

**Decision**: Store all times in UTC, convert on client

**Rationale**:
- Avoids timezone bugs
- Consistent data storage
- Client controls display
- Works across regions

**Implementation**:
- All dates in ISO 8601 format
- User timezone stored in profile
- Client handles conversion

## Deferred Decisions

### API Versioning Strategy

**Status**: ✅ Resolved (2025-01-15)

**Decision**: URL-based versioning (`/api/v1/...`)

**Rationale**:
- Best compatibility with Next.js App Router
- Clear and visible in all requests
- Simple CloudFront caching rules
- Excellent developer experience
- Easy debugging and testing

**Implementation**:
- All endpoints use `/api/v1/` prefix
- Version detection endpoint at `/api/versions`
- Response headers include version info
- 6-month deprecation policy for old versions
- Beta features use `/api/v1-beta/` prefix

**Reference**: See `api-versioning-implementation.md` for full details

### Rate Limiting Implementation

**Status**: Design complete, implementation details TBD

**Decisions Made**:
- Per-user limits for authenticated requests
- Per-IP limits for auth endpoints
- Activity logging special limits

**To Decide**:
- Redis vs DynamoDB for counters
- Response headers format
- Retry-After implementation

### Batch Operations

**Status**: Deferred to post-MVP

**Potential Endpoints**:
- `POST /api/activities/batch`
- `POST /api/teams/batch-invite`

**Rationale**: Not critical for MVP, adds complexity

## Security Considerations

### API Key Management
- No API keys in MVP (JWT only)
- All auth via Cognito tokens
- No third-party API access

### CORS Policy
- Configured for PWA domain only
- No wildcard origins
- Credentials included

### Input Validation
- Strict type checking
- Length limits on all strings
- Numeric range validation
- SQL injection prevention via Prisma

## Performance Goals

### Response Times (p95)
- Dashboard: < 500ms
- List endpoints: < 300ms
- Mutations: < 200ms
- Auth endpoints: < 1s

### Payload Sizes
- Dashboard: < 50KB
- List pages: < 20KB
- Single resources: < 5KB

## Future Considerations

### V2 Features
- Batch operations
- WebSocket subscriptions
- Image upload endpoints
- Export endpoints
- Admin APIs

### Scalability Preparations
- Cursor pagination ready for large datasets
- Aggregation tables for statistics
- Caching strategy defined
- Sharding considerations in IDs