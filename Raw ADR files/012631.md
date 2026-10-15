# ADR-005: n8n Integration Strategy

## Status
**Accepted**

## Context
Nucleus needs to integrate with n8n workflows to evaluate AI node outputs. The integration must be simple, reliable, and work with n8n's existing node ecosystem without requiring custom development or complex setup.

Forces at play:
- Need for simple integration with existing n8n workflows
- Requirement for minimal setup and configuration
- Support for n8n's HTTP Request Node capabilities
- JSON-based data exchange
- Error handling and retry logic
- Future extensibility to other workflow platforms

## Decision
We will use HTTP-based integration with n8n through the existing HTTP Request Node.

Key aspects of this decision:
- **HTTP Request Node**: Use n8n's built-in HTTP Request Node
- **JSON Templates**: Provide ready-to-use JSON templates for common scenarios
- **Single Endpoint**: `/api/evaluate` endpoint for all evaluation requests
- **Standard HTTP**: RESTful API with JSON request/response
- **Error Handling**: Standard HTTP status codes and error responses
- **Documentation**: Comprehensive integration guides and examples

## Consequences

### Positive
- **Simplicity**: No custom nodes or complex setup required
- **Compatibility**: Works with any n8n version and deployment
- **Flexibility**: Can be used in any n8n workflow
- **Standardization**: Uses well-understood HTTP/REST patterns
- **Documentation**: Rich ecosystem of HTTP Request Node examples
- **Error Handling**: Leverages n8n's built-in error handling
- **Testing**: Easy to test with standard HTTP tools

### Negative
- **Manual Setup**: Users must configure HTTP Request Node manually
- **Template Management**: Need to maintain and distribute JSON templates
- **Error Complexity**: HTTP errors require manual handling in workflows
- **Versioning**: API changes may break existing workflows
- **Security**: HTTP-based integration requires proper authentication/authorization

### Neutral
- **Performance**: HTTP overhead compared to direct integration
- **Monitoring**: Standard HTTP monitoring and logging

## Rationale
HTTP-based integration was chosen over alternatives like:
- **Custom n8n Node**: Would require development and distribution effort
- **Webhook Approach**: Less flexible, harder to control
- **Direct Integration**: Would require n8n platform changes
- **Message Queue**: Overkill for simple request/response pattern

The decision prioritizes simplicity and compatibility over performance. The HTTP Request Node is a well-established pattern in n8n, and our approach leverages existing knowledge and tooling.

## Related Decisions
- [ADR-006: Single API Endpoint Design](ADR-006-single-api-endpoint.md)
- [ADR-001: Clean Architecture Pattern](ADR-001-clean-architecture.md)

## References
- [n8n HTTP Request Node Documentation](https://docs.n8n.io/integrations/builtin/cluster-nodes/n8n-nodes-base.httprequest/)
- [n8n Integration Templates](../n8n-integration-templates.md)
- [Outlook Email Workflow Example](../outlook-email-summarization-workflow.json) 