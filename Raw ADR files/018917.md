# ADR-0007: Milestone 4 Service Implementation Strategies

**Status**: Accepted  
**Date**: 2025-10-06  
**Deciders**: Development Team  
**Related**: ADR-0004 (AsyncHTTPClient), ADR-0006 (OpenAPI Generator)

## Context

Milestone 4 introduces three new service integrations (Tautulli, Overseerr, Lidarr) and a unified search layer. We need to determine the optimal implementation approach for each service's HTTP client, following our established package-first philosophy.

### Service API Analysis

1. **Tautulli** (Plex monitoring)
   - API Type: Custom command-based REST API
   - Authentication: API key (query parameter)
   - OpenAPI: ❌ Not available
   - Documentation: https://github.com/Tautulli/Tautulli/wiki/Tautulli-API-Reference
2. **Overseerr** (Media requests)
   - API Type: RESTful API
   - Authentication: API key (X-Api-Key header)
   - OpenAPI: ✅ Available (`overseerr-api.yml`)
   - Source: https://github.com/sct/overseerr/blob/develop/overseerr-api.yml
3. **Lidarr** (Music management)
   - API Type: RESTful API (\*arr family)
   - Authentication: API key (X-Api-Key header)
   - OpenAPI: ✅ Available (`openapi.json`)
   - Source: https://raw.githubusercontent.com/lidarr/Lidarr/develop/src/Lidarr.Api.V1/openapi.json

## Decision

### Tautulli: Manual AsyncHTTPClient Implementation

**Rationale**:

- No OpenAPI specification available
- Custom command-based API (not standard REST)
- Simple enough that manual implementation is straightforward
- No suitable Swift packages found for command-based APIs
- AsyncHTTPClient (already in dependencies) is sufficient

**Implementation**:

```swift
// Custom wrapper around AsyncHTTPClient
final class TautulliService: TautulliServiceProtocol {
    private let httpClient: HTTPClient

    func call<T: Codable>(command: String, params: [String: String]) async throws -> T {
        // Manual HTTP request construction
    }
}
```

**References**: ADR-0004 (AsyncHTTPClient for non-OpenAPI services)

### Overseerr: Swift OpenAPI Generator

**Rationale**:

- Official OpenAPI 3.0 specification available
- Type-safe client generation preferred over manual implementation
- Consistent with package-first philosophy
- Reduces maintenance burden

**Implementation**:

1. Download `overseerr-api.yml` to `openapi/overseerr.yaml`
2. Configure `openapi-generator-config.yaml` for Overseerr target
3. Add build phase for generation
4. Wrap generated client with service protocol

**References**: ADR-0006 (OpenAPI Generator for \*arr services)

### Lidarr: Swift OpenAPI Generator

**Rationale**:

- Part of \*arr family (same as Radarr/Sonarr)
- Official OpenAPI specification available
- Consistent approach across \*arr services
- Proven pattern from Radarr/Sonarr implementation

**Implementation**:

1. Download `openapi.json` to `openapi/lidarr-v1.json`
2. Configure generator (same as Radarr/Sonarr)
3. Music-specific models auto-generated
4. Follow established service protocol pattern

**References**: ADR-0006, Issue #133 (Radarr OpenAPI)

## Consequences

### Positive

- **Consistency**: All \*arr services use OpenAPI Generator
- **Type Safety**: Generated clients provide compile-time safety for Overseerr and Lidarr
- **Maintainability**: Auto-generated code stays in sync with API changes
- **No External Dependencies**: Tautulli uses built-in AsyncHTTPClient (already in deps)
- **Package-First**: Evaluated Swift packages; AsyncHTTPClient is best fit

### Negative

- **Tautulli Manual Work**: More code to write and maintain
- **OpenAPI Version Risks**: Overseerr/Lidarr specs must stay up-to-date
- **Mixed Approaches**: Three different services use two different approaches

### Mitigation

- **Tautulli**: Keep service layer thin; delegate complexity to models
- **OpenAPI Updates**: Document sync process in `scripts/sync-openapi-spec.sh`
- **Testing**: Comprehensive unit and integration tests for all services
- **Documentation**: ADR explains why each approach was chosen

## Package Search Results

### Tautulli HTTP Client Search

**Searched**:

- Swift Package Index: "HTTP client", "REST client", "API client"
- GitHub: Swift HTTP networking libraries
- Evaluated: Alamofire, AsyncHTTPClient (Swift NIO)

**Conclusion**:

- ✅ **AsyncHTTPClient** already in dependencies (from Milestone 1)
- No additional package needed
- Custom wrapper for Tautulli's command-based API is straightforward

### Overseerr/Lidarr Search

**Searched**:

- Swift Package Index: "OpenAPI", "Swagger", "API generator"
- GitHub: Swift OpenAPI code generators

**Conclusion**:

- ✅ **swift-openapi-generator** (Apple official)
- Already established in ADR-0006 for Radarr/Sonarr
- Mature, well-maintained, Swift 6 compatible

## Implementation Order

1. **Tautulli**: Manual implementation (Issue #149 exists)
2. **Overseerr**: OpenAPI spec download → generator setup → service wrapper
3. **Lidarr**: OpenAPI spec download → generator setup → service wrapper
4. **Universal Search**: Orchestration layer (no HTTP client needed)

## Alternatives Considered

### Tautulli: Use Alamofire

**Rejected**:

- Adds dependency bloat
- AsyncHTTPClient already available
- No significant benefit over manual implementation
- Custom API doesn't benefit from Alamofire's abstractions

### All Services: Manual AsyncHTTPClient

**Rejected**:

- Ignores available OpenAPI specifications
- More code to write and maintain for Overseerr/Lidarr
- Loses type safety benefits
- Contradicts package-first philosophy

### Generate Custom OpenAPI for Tautulli

**Rejected**:

- Significant upfront work to reverse-engineer API
- Maintenance burden to keep in sync
- Official spec doesn't exist
- Not worth effort for command-based API

## References

- [Tautulli API Reference](https://github.com/Tautulli/Tautulli/wiki/Tautulli-API-Reference)
- [Overseerr OpenAPI Spec](https://github.com/sct/overseerr/blob/develop/overseerr-api.yml)
- [Lidarr OpenAPI Spec](https://raw.githubusercontent.com/lidarr/Lidarr/develop/src/Lidarr.Api.V1/openapi.json)
- [Swift OpenAPI Generator](https://github.com/apple/swift-openapi-generator)
- [AsyncHTTPClient](https://github.com/swift-server/async-http-client)
- ADR-0004: Use AsyncHTTPClient for HTTP Networking
- ADR-0006: Use OpenAPI Generator for \*arr Services
