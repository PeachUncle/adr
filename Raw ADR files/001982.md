# ADR-023: Visualization API and Dashboard

## Status

Accepted

## Context

As the Gemantria project advances through Phases 5-6 (correlation and pattern analytics), the static JSON exports need to be made accessible through interactive web interfaces. The current pipeline produces rich analytics data but lacks the ability for users to explore this data in real-time. External consumers also need programmatic access to the analytics without direct file system access.

The existing web UI (Phase 5-C) focuses on graph visualization, but doesn't provide comprehensive analytics dashboards or programmatic API access to the correlation and pattern data.

## Decision

Implement a complete visualization layer consisting of:

1. **REST API Server** (`src/services/api_server.py`) providing programmatic access to analytics data
2. **Interactive Dashboard** (`webui/dashboard/`) with real-time metrics and pattern exploration
3. **Report Integration** documenting API endpoints and their data sources

## Rationale

### Benefits and Advantages

- **Real-time Access**: Users can explore analytics without regenerating reports
- **Programmatic Integration**: External tools can consume analytics data via REST API
- **Interactive Exploration**: Dashboards enable filtering, sorting, and visual pattern discovery
- **Operational Visibility**: Live metrics provide immediate feedback on pipeline health
- **Scalability**: API-based architecture supports multiple concurrent users

### Trade-offs Considered

- **Additional Complexity**: New service layer increases system complexity
- **Performance Overhead**: API server adds runtime dependencies
- **Maintenance Burden**: Additional components require ongoing maintenance
- **Security Surface**: API endpoints expand potential attack surface

### Alignment with Project Goals

- **Accessibility**: Makes complex analytics accessible to non-technical users
- **Integration**: Enables external tools to leverage gematria analytics
- **Monitoring**: Provides real-time visibility into semantic network health
- **User Experience**: Transforms static data into interactive exploration

## Alternatives Considered

### Alternative 1: Static File Serving Only

- **Pros**: Simpler implementation, no additional services
- **Cons**: No interactivity, limited external integration
- **Reason Rejected**: Doesn't provide the required interactive exploration capabilities

### Alternative 2: Database Direct Access

- **Pros**: Real-time data access, no export delays
- **Cons**: Exposes internal database schema, security risks
- **Reason Rejected**: Violates data access patterns and security principles

### Alternative 3: Embedded Dashboard in Existing UI

- **Pros**: Single application, consistent user experience
- **Cons**: Couples analytics tightly to graph visualization
- **Reason Rejected**: Analytics deserve separate, focused exploration interface

## Consequences

### Positive

- **Enhanced User Experience**: Interactive exploration of complex analytics
- **API Ecosystem**: Foundation for third-party integrations
- **Real-time Monitoring**: Live dashboard for pipeline health
- **Documentation**: Comprehensive API documentation in reports

### Negative

- **Operational Complexity**: Additional service to deploy and monitor
- **Resource Requirements**: API server consumes additional system resources
- **Version Compatibility**: API contracts must be maintained across versions

### Implementation Requirements

1. **API Server Implementation**:

   - FastAPI application with CORS support
   - JSON response formatting with error handling
   - Parameterized endpoints with filtering capabilities
   - Comprehensive logging and monitoring

2. **Dashboard Components**:

   - React components using existing TypeScript/Visx stack
   - Real-time data fetching with error handling
   - Responsive design following existing UI patterns
   - Interactive filtering and exploration capabilities

3. **Report Integration**:
   - "Interactive Analytics Endpoints" section in pipeline reports
   - API startup instructions and endpoint documentation
   - Data source mapping and freshness indicators

## Related ADRs

- **ADR-016**: Insight Metrics & Ontology (data structures being exposed)
- **ADR-018**: Pattern Correlation Engine (correlation data being served)
- **ADR-022**: Cross-Text Pattern Analysis (pattern data being visualized)

## Notes

### API Design Principles

- **RESTful Design**: Standard HTTP methods and resource-based URLs
- **Parameter Flexibility**: Optional query parameters for filtering and pagination
- **Consistent Responses**: Standardized JSON response format across endpoints
- **Error Handling**: Comprehensive error responses with appropriate HTTP status codes

### Dashboard Architecture

- **Component Separation**: Distinct components for different analytics views
- **Data Fetching**: Centralized API client with caching and error handling
- **Visual Consistency**: Follows existing design system and interaction patterns
- **Performance Optimization**: Lazy loading and efficient rendering for large datasets

### Security Considerations

- **CORS Configuration**: Properly configured for production deployment
- **Rate Limiting**: Consider implementing rate limiting for API endpoints
- **Data Validation**: Input validation on all API parameters
- **Access Logging**: Comprehensive logging of API access patterns

### Future Extensions

- **Authentication**: API key or token-based authentication
- **Caching**: Redis or in-memory caching for frequently accessed data
- **WebSocket Support**: Real-time updates for live pipeline monitoring
- **Advanced Filtering**: Complex query capabilities for large datasets

### Monitoring and Observability

- **API Metrics**: Request/response metrics and error rates
- **Performance Monitoring**: Response time tracking and optimization
- **Usage Analytics**: Dashboard usage patterns and feature adoption
- **Health Checks**: Automated monitoring of API endpoint availability
