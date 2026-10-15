# ADR-006: RESTful API Design Principles

## Status
Accepted

## Context
The SMS messaging platform needs to expose a REST API for external clients to send messages and retrieve message information. The API should be:

- Intuitive and easy to use for developers
- Following industry standards and best practices
- Well-documented with interactive documentation
- Consistent in naming, error handling, and response formats
- Scalable and maintainable
- Supporting different client types (web, mobile, server-to-server)

The API will be the primary interface for the SMS service and needs to be designed for long-term stability and evolution.

## Decision
We will implement a RESTful API following REST principles and industry best practices.

**API Design Standards**:
- **Version**: API versioning through URL path (`/v1/`)
- **Format**: JSON for request/response bodies
- **Documentation**: OpenAPI 3.0 specification with Swagger UI
- **Error Handling**: RFC 7807 Problem Details for HTTP APIs
- **Authentication**: Designed for future JWT/API key integration
- **Validation**: Comprehensive input validation with clear error messages

## Consequences

### Positive
- **Developer Experience**: Intuitive API that follows familiar REST patterns
- **Interoperability**: Standard HTTP methods and status codes work with all clients
- **Documentation**: Auto-generated interactive documentation via Swagger UI
- **Tooling Support**: Excellent tooling support for REST APIs
- **Caching**: HTTP caching semantics for performance optimization
- **Stateless**: Each request is self-contained, enabling better scalability
- **Industry Standard**: Follows widely adopted REST principles

### Negative
- **Over-fetching**: May return more data than needed (vs GraphQL)
- **Multiple Requests**: May require multiple API calls for complex operations
- **Real-time Limitations**: REST is request-response, not ideal for real-time updates

### Neutral
- **Versioning Strategy**: Need to manage API evolution and backward compatibility
- **Performance Optimization**: May need caching and optimization strategies
- **Documentation Maintenance**: Keep documentation synchronized with implementation

## API Design Specification

### URL Structure

**Base URL**: `http://localhost:8080`
**API Prefix**: `/v1`

**Resource-based URLs**:
```
/v1/messages                    # Message collection
/v1/messages/{id}              # Individual message
/v1/users/{userId}/messages    # User-specific messages
/v1/messages/stats             # Message statistics
/v1/messages/failed            # Failed messages
```

### HTTP Methods

| Method | Usage | Idempotent | Safe |
|--------|-------|------------|------|
| GET | Retrieve resources | ✓ | ✓ |
| POST | Create new resources | ✗ | ✗ |
| PUT | Update/replace resources | ✓ | ✗ |
| PATCH | Partial updates | ✗ | ✗ |
| DELETE | Remove resources | ✓ | ✗ |

### HTTP Status Codes

**Success Codes**:
- `200 OK` - Successful retrieval
- `202 Accepted` - Async operation accepted
- `204 No Content` - Successful operation with no response body

**Client Error Codes**:
- `400 Bad Request` - Invalid request syntax or validation error
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation failed

**Server Error Codes**:
- `500 Internal Server Error` - Unexpected server error
- `503 Service Unavailable` - Service temporarily unavailable

### Request/Response Format

**Content Type**: `application/json`

**Send Message Request**:
```json
POST /v1/messages
Content-Type: application/json

{
  "sender": "+1234567890",
  "recipient": "+1987654321",
  "text": "Hello, this is a test message!"
}
```

**Send Message Response**:
```json
HTTP/1.1 202 Accepted
Content-Type: application/json

{
  "id": "be9d4804-233f-4e54-92c3-16a7228dd800",
  "sender": "+1234567890",
  "recipient": "+1987654321", 
  "text": "Hello, this is a test message!",
  "status": "PENDING",
  "created_at": "2025-07-16T19:22:09",
  "updated_at": "2025-07-16T19:22:09"
}
```

### Pagination

**Query Parameters**:
```
GET /v1/messages?page=0&size=20&status=SENT
```

**Response Format**:
```json
{
  "messages": [...],
  "total_count": 150,
  "page": 0,
  "page_size": 20,
  "total_pages": 8
}
```

### Error Handling

**RFC 7807 Problem Details**:
```json
HTTP/1.1 400 Bad Request
Content-Type: application/problem+json

{
  "type": "https://example.com/problems/validation-error",
  "title": "Constraint Violation",
  "status": 400,
  "detail": "Request validation failed",
  "instance": "/v1/messages",
  "violations": [
    {
      "field": "sendMessage.request.recipient",
      "message": "Invalid recipient phone number format. Use international format (e.g., +1234567890)"
    }
  ]
}
```

## Implementation Details

### Controller Implementation

**Message Controller**:
```java
@Path("/v1/messages")
@Tag(name = "SMS Messages", description = "SMS message operations")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
public class MessageController {

    @POST
    @Operation(summary = "Send SMS message", description = "Send a new SMS message")
    @APIResponse(responseCode = "202", description = "Message accepted for processing")
    @APIResponse(responseCode = "400", description = "Invalid request")
    public Response sendMessage(@Valid SendMessageRequest request) {
        MessageResponse response = messageService.sendMessage(request);
        return Response.accepted(response).build();
    }

    @GET
    @Path("/{messageId}")
    @Operation(summary = "Get message by ID", description = "Retrieve a specific SMS message by its ID")
    public Response getMessage(@PathParam("messageId") UUID messageId) {
        return messageService.getMessage(messageId)
                .map(message -> Response.ok(message).build())
                .orElse(Response.status(Response.Status.NOT_FOUND).build());
    }
}
```

### Validation

**Bean Validation**:
```java
public class SendMessageRequest {
    
    @NotNull(message = "Sender is required")
    @Pattern(regexp = "\\+?[1-9]\\d{1,14}", 
             message = "Invalid sender phone number format. Use international format (e.g., +1234567890)")
    private String sender;
    
    @NotNull(message = "Recipient is required")
    @Pattern(regexp = "\\+?[1-9]\\d{1,14}",
             message = "Invalid recipient phone number format. Use international format (e.g., +1234567890)")
    private String recipient;
    
    @NotBlank(message = "Message text is required")
    @Size(min = 1, max = 1600, message = "Message text must be between 1 and 1600 characters")
    @Pattern(regexp = ".*\\S.*", message = "Message text cannot be empty or contain only whitespace")
    private String text;
}
```

### OpenAPI Documentation

**Configuration**:
```java
@OpenAPIDefinition(
    info = @Info(
        title = "SMS Service API",
        version = "1.0.0",
        description = "SMS messaging service with REST API and Kafka integration",
        contact = @Contact(
            name = "SMS Platform Team",
            email = "support@intercom.com"
        ),
        license = @License(
            name = "MIT",
            url = "https://opensource.org/licenses/MIT"
        )
    ),
    servers = {
        @Server(url = "http://localhost:8080", description = "Development server"),
        @Server(url = "https://api.sms-platform.com", description = "Production server")
    }
)
public class Application extends Application {
}
```

### Content Negotiation

**Supported Media Types**:
- `application/json` (primary)
- `application/problem+json` (for error responses)

**Future Considerations**:
- `application/xml` (if XML support needed)
- `text/csv` (for bulk exports)

### CORS Configuration

**Cross-Origin Resource Sharing**:
```properties
# Allow CORS for web applications
quarkus.http.cors=true
quarkus.http.cors.origins=http://localhost:3000,https://app.sms-platform.com
quarkus.http.cors.headers=accept,authorization,content-type,x-requested-with
quarkus.http.cors.methods=GET,POST,PUT,DELETE,OPTIONS
```

## API Versioning Strategy

### URL Path Versioning
```
/v1/messages  # Version 1
/v2/messages  # Version 2 (future)
```

**Benefits**:
- Clear and explicit
- Easy to implement
- Good caching support
- Easy to route and proxy

### Version Lifecycle
1. **New Version**: Introduce new version while maintaining old
2. **Deprecation**: Mark old version as deprecated with sunset date
3. **Migration Period**: Provide migration guide and tools
4. **Retirement**: Remove old version after sufficient notice

### Backward Compatibility
- **Additive Changes**: New optional fields (non-breaking)
- **Breaking Changes**: Require new version
- **Documentation**: Clear upgrade guides between versions

## Security Considerations

### Input Validation
- **Phone Number Format**: Strict regex validation
- **Message Content**: Length limits and content filtering
- **SQL Injection**: Use parameterized queries (handled by ORM)
- **XSS Prevention**: Input sanitization for display

### Rate Limiting (Future)
```java
@RateLimited(value = 100, window = "1 minute")
@POST
public Response sendMessage(@Valid SendMessageRequest request) {
    // Implementation
}
```

### Authentication (Future)
```java
@Authenticated
@RolesAllowed({"USER", "ADMIN"})
@GET
public Response getMessages() {
    // Implementation  
}
```

## Performance Optimization

### Caching Strategy
```java
@GET
@Path("/{messageId}")
@CacheResult(cacheName = "messages")
public MessageResponse getMessage(@CacheKey UUID messageId) {
    return messageService.getMessage(messageId);
}
```

### Pagination Best Practices
- **Default Page Size**: 20 items
- **Maximum Page Size**: 100 items
- **Cursor-based Pagination**: For large datasets (future enhancement)

### Response Compression
```properties
# Enable GZIP compression
quarkus.http.enable-compression=true
quarkus.http.compression-level=6
```

## API Testing Strategy

### Contract Testing
```java
@QuarkusTest
public class MessageApiTest {
    
    @Test
    public void shouldCreateMessage() {
        given()
            .contentType(ContentType.JSON)
            .body(new SendMessageRequest("+1234567890", "+1987654321", "Test"))
        .when()
            .post("/v1/messages")
        .then()
            .statusCode(202)
            .body("id", notNullValue())
            .body("status", equalTo("PENDING"));
    }
}
```

### API Documentation Testing
```java
@Test
public void shouldGenerateValidOpenApiSpec() {
    given()
    .when()
        .get("/q/openapi")
    .then()
        .statusCode(200)
        .contentType("application/yaml");
}
```

## Monitoring and Analytics

### API Metrics
- **Request Rate**: Requests per second by endpoint
- **Response Times**: P50, P95, P99 latencies
- **Error Rates**: 4xx and 5xx error percentages
- **Payload Sizes**: Request/response body sizes

### Business Metrics
- **Message Volume**: Messages sent per time period
- **Success Rate**: Successful message delivery percentage
- **User Activity**: Active users and usage patterns

## Documentation Strategy

### Swagger UI Features
- **Interactive Testing**: Test API directly from documentation
- **Code Examples**: Auto-generated client code samples
- **Schema Documentation**: Detailed request/response schemas
- **Authentication**: Integration with auth mechanisms

### Additional Documentation
- **Getting Started Guide**: Quick start for new developers
- **Migration Guides**: Version upgrade instructions
- **Best Practices**: Recommended usage patterns
- **SDK Documentation**: Client library documentation

## Related Decisions
- [ADR-001: Use Microservices Architecture](001-microservices-architecture.md)
- [ADR-003: Use Quarkus as Java Framework](003-quarkus-framework.md)
- [ADR-007: Asynchronous Message Processing Pattern](007-async-processing-pattern.md)
