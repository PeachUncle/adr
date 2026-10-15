# 007. REST API Design Patterns and JSON Response Format

**Classifications:** api-design

## Status

Implicitly required

## Context

With NestJS selected as the backend framework and REST APIs confirmed (GraphQL excluded per ADR 001), we need to define the specific API design patterns and JSON response formats for event management and ticket purchasing endpoints.

## Decision

Implement simple REST API design with plain JSON responses, following standard HTTP methods and status codes without additional hypermedia or specification overhead.

### API Structure (sample, not extensive)
- **Events:** `GET /events`, `POST /events`, `GET /events/:id`
- **Tickets:** `POST /events/:id/tickets` (purchase)
- **Standard HTTP status codes:** 200, 201, 400, 404, 409 (conflict for overselling)
- **Plain JSON responses** with consistent error format

### Streaming API for Real-time Updates
- **Server-Sent Events (SSE):** `GET /events/:id/stream` for live ticket statistics
- **Push administrative statistics:** remaining tickets, allocated tickets, confirmed tickets (fully purchased)
- **Event-driven updates:** triggered by ticket purchase/allocation/confirmation actions

### Streaming Data Format
```json
// SSE event data
{
  "eventId": 1,
  "timestamp": "2024-01-15T19:30:15Z",
  "statistics": {
    "totalTickets": 100,
    "remainingTickets": 45,
    "allocatedTickets": 15,    // Reserved but not yet paid
    "confirmedTickets": 40     // Fully purchased/paid
  },
  "lastEvent":{
    "type":"ticket_purchased", // or "ticket_allocated", "ticket_expired"
    "actor": "Joe Blogs", // actor name that relates to teh lastEvent
  } 
}
```

### Response Format Example
```json
// Success response
{
  "id": 1,
  "name": "Concert",
  "date": "2024-01-15T19:00:00Z",
  "totalTickets": 100,
  "availableTickets": 85
}

// Error response
{
  "error": "Insufficient tickets available",
  "code": "TICKETS_SOLD_OUT"
}
```

## Consequences

### Constraints 
- Must follow RESTful conventions for resource endpoints
- Standard HTTP status codes for success/error responses
- JSON request/response format
- Simple, readable API without hypermedia complexity
- Compatible with NestJS decorators and validation pipes
- Streaming API must handle connection management and graceful disconnection
- Real-time updates should not impact core API performance

### Dependencies
- Works seamlessly with NestJS @Controller() and @Body() decorators
- Integrates with class-validator for request validation
- Simple frontend integration without additional parsing logic
- Straightforward API testing and documentation
- Streaming requires NestJS EventEmitter or similar pub/sub mechanism
- Frontend needs EventSource (SSE)

### Risk Level
Low - Simple approach reduces complexity and development time

### Reversibility
Easy - Response format can be enhanced later without breaking existing clients

### Other Considered Options

#### JSON:API Specification
- **How it works:** Standardized JSON format with `data`, `attributes`, `relationships` structure
- **NestJS integration:** Requires custom serializers or third-party libraries
- **Pros:** Standardized, handles relationships well, built-in pagination
- **Cons:** Verbose responses, learning curve, overkill for simple CRUD
- **Rejected:** Too complex for 3-4 hour time constraint

#### JSON HAL (Hypertext Application Language)
- **How it works:** Adds `_links` and `_embedded` fields for hypermedia navigation
- **NestJS integration:** Custom interceptors needed to add HAL structure
- **Pros:** Self-documenting API, enables API discoverability
- **Cons:** Additional complexity, larger response payloads
- **Rejected:** Hypermedia not needed for simple event/ticket operations

#### OpenAPI/Swagger with Custom Response Schemas
- **How it works:** Define strict response schemas with OpenAPI decorators
- **NestJS integration:** Built-in @nestjs/swagger support
- **Pros:** Auto-generated documentation, type safety, validation
- **Cons:** More boilerplate, rigid schema definitions
- **Considered:** Good for documentation but adds development overhead, not practical for time constraints

#### Custom Envelope Format
- **How it works:** Wrap all responses in consistent envelope: `{success: boolean, data: {}, error: {}}`
- **NestJS integration:** Global response interceptor
- **Pros:** Consistent response structure, easy error handling
- **Cons:** Verbose, not standard API practice, or common REST practice
- **Rejected:** Unnecessary wrapper for simple API, added complexity given time constraints

#### Streaming API Alternatives

**Server-Sent Events (SSE) - Selected**
- **How it works:** HTTP connection kept open, server pushes text/event-stream data
- **NestJS integration:** Built-in support with @Sse() decorator
- **Pros:** Simple implementation, automatic reconnection, works through firewalls
- **Cons:** Unidirectional only, limited browser connection pool

**WebSockets**
- **How it works:** Full-duplex communication over persistent connection
- **NestJS integration:** @nestjs/websockets with Socket.IO or native WebSockets
- **Pros:** Bidirectional, lower latency, more flexible
- **Cons:** More complex, connection management overhead, firewall issues

**Polling/Long-polling**
- **How it works:** Client repeatedly requests updates or holds connection open
- **NestJS integration:** Standard REST endpoints with timeout handling
- **Pros:** Simple, works everywhere, no persistent connections
- **Cons:** Higher latency, more server load, not truly real-time 