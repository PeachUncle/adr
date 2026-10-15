# Use AsyncHTTPClient Over Custom Networking Layer

- Status: accepted
- Deciders: Matthias Wallner Géhri
- Date: 2025-10-04

Technical Story: Milestone 1 Task 1.4 - Implement networking infrastructure for API communication

## Context and Problem Statement

The app needs HTTP networking capabilities to communicate with media management services (Radarr, Sonarr, Tautulli, etc.). Should we build a custom networking layer or use a standard framework?

## Decision Drivers

- **Production Ready**: Battle-tested in real-world applications
- **Swift 6 Compatibility**: Native async/await and concurrency support
- **Feature Complete**: HTTP/2, connection pooling, timeouts, streaming
- **Standard Framework**: Prefer industry-standard solutions over custom code
- **Maintainability**: External maintenance, not custom upkeep
- **Performance**: High-performance networking for API calls
- **Testing**: Built-in testing support
- **Package Philosophy**: Use packages first, custom code last

## Considered Options

- **Option 1**: AsyncHTTPClient (Swift Server Workgroup)
- **Option 2**: Alamofire (third-party iOS/macOS networking)
- **Option 3**: URLSession (Apple's built-in networking)
- **Option 4**: Custom networking layer with URLSession wrapper

## Decision Outcome

Chosen option: **Option 1 - AsyncHTTPClient**

AsyncHTTPClient is the standard Swift HTTP client built on SwiftNIO, providing production-ready networking without requiring custom wrappers. Following the principle: **use standard frameworks over custom implementations**.

### Consequences

- **Good**: Production-ready framework from Swift Server Workgroup
- **Good**: Built on SwiftNIO for high performance
- **Good**: Native async/await support (no callbacks)
- **Good**: HTTP/2 support with connection pooling
- **Good**: Streaming support for large responses
- **Good**: Cross-platform (macOS, Linux, iOS)
- **Good**: Active maintenance by Swift.org
- **Good**: No custom code to maintain
- **Good**: Built-in testing support
- **Neutral**: Lower-level API than Alamofire
- **Bad**: Less iOS-specific convenience features than Alamofire

### Implementation Approach

**Direct Usage** (no custom wrapper):

```swift
import AsyncHTTPClient
import HTTPTypes

final class RadarrService {
    private let httpClient: HTTPClient
    private let baseURL: String
    private let apiKey: String

    init(httpClient: HTTPClient, baseURL: String, apiKey: String) {
        self.httpClient = httpClient
        self.baseURL = baseURL
        self.apiKey = apiKey
    }

    func getMovies() async throws -> [Movie] {
        var request = HTTPClientRequest(url: "\(baseURL)/api/v3/movie")
        request.method = .GET
        request.headers.add(name: "X-Api-Key", value: apiKey)

        let response = try await httpClient.execute(request, timeout: .seconds(30))
        let data = try await response.body.collect(upTo: 10 * 1024 * 1024) // 10MB limit

        return try JSONDecoder().decode([Movie].self, from: Data(buffer: data))
    }
}
```

**DI Registration**:

```swift
container.register(HTTPClient.self) { _ in
    HTTPClient(eventLoopGroupProvider: .singleton)
}.inObjectScope(.container)
```

## Pros and Cons of the Options

### Option 1: AsyncHTTPClient

- **Good**: Standard Swift Server framework
- **Good**: Production-ready and battle-tested
- **Good**: Native async/await support
- **Good**: HTTP/2 and connection pooling
- **Good**: SwiftNIO-based (high performance)
- **Good**: Cross-platform consistency
- **Good**: Active maintenance by Swift.org
- **Good**: Built-in testing capabilities
- **Neutral**: Lower-level API (more control, less convenience)
- **Bad**: Less iOS-specific helpers than Alamofire

### Option 2: Alamofire

- **Good**: iOS-native conveniences (UIImage, Combine)
- **Good**: Rich ecosystem of plugins
- **Good**: Extensive documentation
- **Good**: Large community support
- **Neutral**: Adds abstraction over URLSession
- **Bad**: Third-party dependency (not Apple/Swift.org)
- **Bad**: iOS/macOS only (not cross-platform)
- **Bad**: More features than needed for this app

### Option 3: URLSession

- **Good**: Built into Apple platforms
- **Good**: No external dependencies
- **Good**: Well-documented
- **Neutral**: Requires custom async/await wrappers for older APIs
- **Bad**: Delegate-based API for advanced features
- **Bad**: Less efficient than SwiftNIO for high-throughput
- **Bad**: No HTTP/2 support on some platforms

### Option 4: Custom Networking Layer

- **Good**: Full control over implementation
- **Good**: Tailored to exact needs
- **Bad**: Reinventing the wheel
- **Bad**: Custom code to maintain
- **Bad**: Need to handle edge cases ourselves
- **Bad**: Testing burden on us
- **Bad**: Violates "use packages first" principle

## More Information

### Dependencies Added

```swift
// Package.swift
dependencies: [
    .package(url: "https://github.com/swift-server/async-http-client.git", from: "1.28.0"),
    .package(url: "https://github.com/apple/swift-http-types.git", from: "1.4.0"),
    .package(url: "https://github.com/apple/swift-openapi-runtime.git", from: "1.8.3"),
    .package(url: "https://github.com/apple/swift-openapi-generator.git", from: "1.10.3"),
]
```

### HTTPTypes Integration

Using Apple's `swift-http-types` for type-safe HTTP:

```swift
import HTTPTypes

var request = HTTPClientRequest(url: url)
request.method = .GET
request.headers[.contentType] = "application/json"
request.headers[.authorization] = "Bearer \(token)"
```

### OpenAPI Client Generation

For services with OpenAPI specs (Radarr, Sonarr):

```swift
import OpenAPIRuntime
import OpenAPIURLSession

let client = Client(
    serverURL: try Servers.server1(),
    transport: URLSessionTransport()
)

let movies = try await client.getMovies()
```

### Testing Strategy

Use HTTPClient with test configuration:

```swift
let testClient = HTTPClient(
    eventLoopGroupProvider: .singleton,
    configuration: HTTPClient.Configuration(/* test settings */)
)
```

Or mock the service layer directly (preferred):

```swift
protocol RadarrServiceProtocol {
    func getMovies() async throws -> [Movie]
}

final class MockRadarrService: RadarrServiceProtocol {
    var moviesResult: Result<[Movie], Error> = .success([])

    func getMovies() async throws -> [Movie] {
        try moviesResult.get()
    }
}
```

### Why No Custom Wrapper

AsyncHTTPClient already provides:

- ✅ Request building (HTTPClientRequest)
- ✅ Response handling (HTTPClientResponse)
- ✅ Connection pooling
- ✅ Timeout management
- ✅ Error handling
- ✅ Logging support
- ✅ Testing capabilities
- ✅ SSL/TLS support

Creating custom wrappers would violate the principle: **use standard frameworks over custom implementations**.

## Related Decisions

- 0003: Use Swinject for DI - HTTPClient registered as singleton in DI container
- 0005: OpenAPI Client Generation - OpenAPI clients use AsyncHTTPClient under the hood

## References

- [AsyncHTTPClient GitHub](https://github.com/swift-server/async-http-client)
- [Swift HTTP Types](https://github.com/apple/swift-http-types)
- [Swift OpenAPI Generator](https://github.com/apple/swift-openapi-generator)
- Documentation: `/docs/AsyncHTTPClient-Integration.md`
