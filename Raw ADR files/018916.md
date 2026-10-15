---
status: accepted
date: 2025-10-06
decision-makers: Matthias Wallner Géhri
---

# Use OpenAPITools Generator (swift6) for Service API Clients

## Context and Problem Statement

Thriftwood needs to integrate with multiple media management services (Radarr, Sonarr, Lidarr, etc.) that provide OpenAPI/Swagger specifications. How should we implement HTTP clients for these services? Should we manually code request/response models and endpoints, or leverage OpenAPI code generation for type-safe, spec-driven clients?

This decision impacts Milestone 2 (Radarr, Sonarr), Milestone 4 (Lidarr), and sets precedent for all future service integrations that provide OpenAPI specifications.

Key questions:

- Which OpenAPI generator provides the best Swift 6 support?
- How do we balance type safety, performance, and maintainability?
- What's the best integration pattern with our MVVM-C architecture?
- Which services can benefit from code generation vs. manual implementation?
- How do we handle multiple OpenAPI specs (one per service)?
- Should generated code be committed to source control or generated at build time?

## Decision Drivers

- **Swift 6 Compatibility**: Must support Swift 6 strict concurrency and modern Swift features
- **Type Safety**: Compile-time guarantees for API requests/responses reduce runtime errors
- **Maintainability**: API changes reflected in generated code, not manual updates
- **Performance**: Efficient runtime performance and reasonable generation times
- **Integration**: Works well with URLSession and our existing architecture
- **Spec-Driven Development**: Aligns with project's specification-driven workflow
- **Reduced Boilerplate**: Eliminate ~300+ lines of manual model/endpoint definitions per service
- **Testing**: Generated code enables easy mocking
- **Multi-Service Support**: Must support multiple OpenAPI specs (Radarr, Sonarr, Lidarr) without conflicts
- **Build Workflow**: Generation step must integrate well with development workflow
- **Source Control**: Prefer committed source files for diffing and review over ephemeral build-time generation
- **CLI-First**: Prefer command-line tools over build plugins for flexibility and control
- **Maturity**: Stable, proven tool with active community and long track record

## Considered Options

- Option 1: OpenAPITools/openapi-generator (swift6 target)
- Option 2: Apple Swift OpenAPI Generator with URLSession transport
- Option 3: Manual AsyncHTTPClient implementation with Codable models
- Option 4: CreateAPI
- Option 5: Swagger-Codegen (Legacy)
- Option 6: Hybrid approach (generated models, custom HTTP layer)

## Decision Outcome

Chosen option: **"Option 1: OpenAPITools/openapi-generator (swift6 target)"**, because it's a mature, proven tool with excellent Swift 6 support, handles multiple services elegantly via CLI, generates committed source files that can be reviewed and diffed, and provides extensive customization options. The swift6 generator is marked STABLE and specifically designed for Swift 6.x clients with urlsession library support.

### Consequences

- Good, because type-safe API clients are generated from OpenAPI specs
- Good, because it's a mature tool (10+ years) with proven stability
- Good, because swift6 generator is marked STABLE with full Swift 6 support
- Good, because CLI-based workflow allows scripting and automation
- Good, because generated code is committed to source control (visible diffs, code review)
- Good, because multi-service architecture is straightforward (one command per service)
- Good, because extensive configuration options via YAML/JSON
- Good, because no Swift Package Manager build plugin complexity
- Good, because it reduces manual HTTP/model code by ~70%
- Good, because API changes cause compile-time errors (not runtime failures)
- Good, because it supports urlsession library (native iOS networking)
- Good, because it supports async/await and modern Swift concurrency
- Good, because large community and extensive documentation
- Good, because customizable via Mustache templates if needed
- Good, because supports OpenAPI 2.0, 3.0, and 3.1
- Neutral, because it requires maintaining OpenAPI spec files in the repository
- Neutral, because generated code must be regenerated when specs change (via script)
- Bad, because there's a learning curve for generator configuration
- Bad, because generated code is committed (increases repository size)
- Bad, because it cannot be used for services without OpenAPI specs (SABnzbd, NZBGet, Tautulli)
- Bad, because requires Java runtime installed on development machine

### Confirmation

Validation criteria for implementation:

- Successfully generate and use clients for Radarr v3 API
- All generated code passes Swift 6 strict concurrency checks
- Generated clients integrate smoothly with our MVVM-C coordinator pattern
- Generation script runs in under 10 seconds for all services
- Generated code compiles without warnings
- Code review process works well with committed generated files

## Pros and Cons of the Options

### Option 1: OpenAPITools/openapi-generator (swift6 target)

[OpenAPITools/openapi-generator](https://github.com/OpenAPITools/openapi-generator) - Mature, community-driven code generator

**Key Specifications:**

- Generator: `swift6` (STABLE)
- Version: 7.16.0+ (installed via Homebrew)
- Library: `urlsession` (default, uses URLSession)
- Languages: 50+ (Swift 6 is one of them)
- OpenAPI Support: 2.0, 3.0, 3.1

**Integration Example:**

```bash
# Generate Radarr client
openapi-generator generate \
  -i openapi/radarr-v3.yaml \
  -g swift6 \
  -c openapi/radarr-config.yaml \
  -o Thriftwood/Services/Radarr/Generated

# Generated code uses native Swift patterns
let api = DefaultAPI()
api.getMovies { (response, error) in
    // Handle response
}

# Or with async/await (with responseAs=AsyncAwait)
let movies = try await DefaultAPI.getMovies()
```

- Good, because it's a mature project (10+ years, 25k+ stars)
- Good, because swift6 generator is marked STABLE (not experimental)
- Good, because excellent Swift 6 support with strict concurrency
- Good, because CLI-based tool allows scripting and automation
- Good, because generated code is committed to source control (reviewable, diffable)
- Good, because multi-service support is straightforward (one command per spec)
- Good, because supports OpenAPI 2.0, 3.0, and 3.1
- Good, because highly customizable via configuration files (YAML/JSON)
- Good, because urlsession library uses native iOS URLSession (no dependencies)
- Good, because supports async/await via responseAs option
- Good, because large active community and extensive documentation
- Good, because customizable via Mustache templates if needed
- Good, because generates idiomatic Swift code (structs, enums, Codable)
- Good, because no Swift Package Manager integration complexity
- Good, because installed via Homebrew (standard macOS workflow)
- Good, because supports batch generation for multiple specs
- Neutral, because requires Java runtime (common on macOS)
- Neutral, because generated code is committed (increases repo size)
- Bad, because less "Apple-native" than first-party solutions
- Bad, because requires manual regeneration when specs change
- Bad, because generated code may be verbose

### Option 2: Apple Swift OpenAPI Generator

[Apple Swift OpenAPI Generator](https://github.com/apple/swift-openapi-generator) - Official Apple solution

**Integration Example:**

```swift
import OpenAPIRuntime
import OpenAPIURLSession

let client = Client(
    serverURL: try Servers.server1(),
    transport: URLSessionTransport()
)
let movies = try await client.getMovies()
```

- Good, because it's a first-party Apple solution
- Good, because excellent Swift 6 support with async/await
- Good, because build-time generation via SPM plugin
- Good, because protocol-based design for testing
- Good, because lightweight runtime dependencies
- Bad, because relatively new (1.0 in 2023, less battle-tested)
- Bad, because build plugin complexity for multiple services
- Bad, because generated code is ephemeral (harder to review)
- Bad, because one spec per target constraint (complex multi-service setup)
- Bad, because limited customization options
- Bad, because no support for OpenAPI 2.0 (Swagger)
- Bad, because smaller community

### Option 3: Manual AsyncHTTPClient Implementation

Manual implementation using URLSession with hand-coded Codable models.

- Good, because it provides full control over implementation
- Good, because it works for any API (spec or no spec)
- Good, because no code generation dependencies
- Good, because uses native URLSession (iOS standard)
- Bad, because manual model definitions are error-prone
- Bad, because no compile-time API validation
- Bad, because ~300+ lines of boilerplate per service
- Bad, because manual updates required when API changes
- Bad, because time-consuming to implement and maintain
- Bad, because prone to inconsistencies across services

### Option 3: OpenAPITools/openapi-generator (Legacy Swift 5)

[OpenAPITools/openapi-generator](https://github.com/OpenAPITools/openapi-generator) with older `swift5` generator

- Good, because mature project with extensive features
- Good, because highly customizable
- Neutral, because same tool as Option 1
- Bad, because swift5 generator lacks Swift 6 features
- Bad, because not the recommended generator for new Swift 6 projects
- Bad, because missing strict concurrency support

### Option 4: CreateAPI (Alternative Tool)

[CreateAPI](https://github.com/CreateAPI/CreateAPI) - Modern Swift-first generator

- Good, because it's a modern Swift-first generator
- Good, because it has good Swift 5.5+ support with async/await
- Good, because it generates clean, idiomatic Swift code
- Good, because it supports URLSession and custom transports
- Good, because no external dependencies in generated code
- Good, because fast generation times
- Bad, because less active development (last major update mid-2023)
- Bad, because Swift 6 strict concurrency support unclear
- Bad, because smaller community than alternatives
- Bad, because limited documentation
- Bad, because fewer customization options
- Bad, because less mature than OpenAPITools

### Option 5: Swagger-Codegen (Legacy, Not Recommended)

[Swagger-Codegen](https://github.com/swagger-api/swagger-codegen)

- Good, because original OpenAPI generator with long history
- Good, because wide language support
- Good, because extensive documentation
- Bad, because deprecated in favor of OpenAPITools/openapi-generator
- Bad, because poor Swift 6 support
- Bad, because outdated Swift patterns
- Bad, because not recommended for new projects

### Option 6: Hybrid Approach

Generate models from OpenAPI specs but implement custom HTTP layer.

- Good, because generated models reduce boilerplate
- Good, because custom HTTP layer provides flexibility
- Neutral, because mix of generated and manual code
- Bad, because complexity of maintaining both approaches
- Bad, because no end-to-end type safety
- Bad, because violates "use packages first" principle

## More Information

### Implementation Approach

#### 1. Installation

OpenAPITools generator is installed via Homebrew:

```bash
brew install openapi-generator
openapi-generator version  # Verify installation (7.16.0+)
```

#### 2. Obtain OpenAPI Specifications

```bash
# Radarr API spec (already downloaded)
# Located at: openapi/radarr-v3.yaml (8,505 lines)

# Sonarr API spec
curl https://raw.githubusercontent.com/Sonarr/Sonarr/develop/src/Sonarr.Api.V3/openapi.json \
  > openapi/sonarr-v3.yaml

# Lidarr API spec
curl https://raw.githubusercontent.com/Lidarr/Lidarr/develop/src/Lidarr.Api.V1/openapi.json \
  > openapi/lidarr-v1.yaml
```

#### 3. Create Generation Configuration Files

Each service gets its own configuration file:

```yaml
# openapi/radarr-config.yaml
library: urlsession
projectName: RadarrAPI
responseAs: AsyncAwait
useSPMFileStructure: false
swiftPackagePath: ""
hashableModels: true
identifiableModels: true
validatable: true
enumUnknownDefaultCase: true
sortModelPropertiesByRequiredFlag: true
hideGenerationTimestamp: true
```

Key configuration options:

- `library: urlsession` - Use native URLSession (no dependencies)
- `responseAs: AsyncAwait` - Generate async/await methods
- `projectName: RadarrAPI` - Namespace for generated code
- `useSPMFileStructure: false` - Disable SPM structure (we control layout)
- `swiftPackagePath: ""` - No package path prefix
- `enumUnknownDefaultCase: true` - Handle unknown enum cases gracefully

#### 4. Generate Clients

```bash
# Generate Radarr client
openapi-generator generate \
  -i openapi/radarr-v3.yaml \
  -g swift6 \
  -c openapi/radarr-config.yaml \
  -o Thriftwood/Services/Radarr/Generated \
  --additional-properties=projectName=RadarrAPI

# Generate Sonarr client
openapi-generator generate \
  -i openapi/sonarr-v3.yaml \
  -g swift6 \
  -c openapi/sonarr-config.yaml \
  -o Thriftwood/Services/Sonarr/Generated \
  --additional-properties=projectName=SonarrAPI

# Or use the script
./scripts/generate-openapi-clients.sh
```

Generated file structure:

```text
Thriftwood/Services/Radarr/Generated/
├── APIs/
│   └── DefaultAPI.swift          # API endpoints
├── Models/
│   ├── Movie.swift
│   ├── AddMovieRequest.swift
│   └── ...                       # All model types
├── APIHelper.swift
├── CodableHelper.swift
├── Extensions.swift
└── OpenISO8601DateFormatter.swift
```

#### 5. Wrap Generated Client in Service Layer

```swift
// Thriftwood/Services/Radarr/RadarrService.swift
import Foundation

/// Service layer wrapper for Radarr API client
final class RadarrService: ObservableObject {
    private let baseURL: URL
    private let apiKey: String

    init(baseURL: URL, apiKey: String) {
        self.baseURL = baseURL
        self.apiKey = apiKey

        // Configure DefaultAPI with base URL and API key
        DefaultAPI.basePath = baseURL.absoluteString
        DefaultAPI.customHeaders = ["X-Api-Key": apiKey]
    }

    func getMovies() async throws -> [Movie] {
        return try await DefaultAPI.getMovies()
    }

    func addMovie(_ request: AddMovieRequest) async throws -> Movie {
        return try await DefaultAPI.addMovie(body: request)
    }

    func searchMovies(query: String) async throws -> [MovieResource] {
        return try await DefaultAPI.searchMovies(term: query)
    }
}
```

#### 6. Register in Dependency Injection Container

```swift
// Thriftwood/Core/DI/DIContainer.swift
extension DIContainer {
    func registerServices() {
        // Radarr service
        container.register(RadarrService.self) { resolver in
            let profile = resolver.resolve(Profile.self)!
            let config = profile.radarrConfig

            return RadarrService(
                baseURL: config.baseURL,
                apiKey: config.apiKey
            )
        }
        .inObjectScope(.container)
    }
}
```

#### 7. Testing with Generated Code

```swift
// ThriftwoodTests/Mocks/MockRadarrService.swift
final class MockRadarrService: RadarrService {
    var mockMovies: [Movie] = []
    var addMovieResult: Result<Movie, Error>?

    override func getMovies() async throws -> [Movie] {
        return mockMovies
    }

    override func addMovie(_ request: AddMovieRequest) async throws -> Movie {
        switch addMovieResult {
        case .success(let movie): return movie
        case .failure(let error): throw error
        case .none: throw TestError.notConfigured
        }
    }
}

// In tests
func testMovieList() async throws {
    let mockService = MockRadarrService(baseURL: URL(string: "https://test.local")!, apiKey: "test")
    mockService.mockMovies = [
        Movie(id: 1, title: "Test Movie")
    ]

    let movies = try await mockService.getMovies()
    #expect(movies.count == 1)
    #expect(movies[0].title == "Test Movie")
}
```

### Service Applicability

#### ✅ Use OpenAPI Generator

Services with OpenAPI/Swagger specifications:

- **Radarr**: OpenAPI v3 spec available (8,505 lines, already downloaded to `openapi/radarr-v3.yaml`)
- **Sonarr**: OpenAPI v3 spec available (GitHub: `/api/v3/swagger`)
- **Lidarr**: OpenAPI v1 spec available (GitHub: `/api/v1/swagger`)
- **Overseerr**: OpenAPI spec available (check GitHub repo for latest)

#### ❌ Use Manual URLSession Implementation

Services without OpenAPI specifications:

- **SABnzbd**: No OpenAPI spec (custom XML-based API)
- **NZBGet**: JSON-RPC API (not REST, no OpenAPI)
- **Tautulli**: Custom REST API (no OpenAPI spec)

### Migration Path for Services

1. **Radarr** (Milestone 2, Week 4): Start with this as OpenAPI spec is already downloaded
2. **Sonarr** (Milestone 2, Week 5): Apply the same pattern
3. **Lidarr** (Milestone 4, Week 11): Continue with same approach
4. **Overseerr**: Evaluate spec availability and quality
5. **Fallback Strategy**: Use manual URLSession implementation for services without specs

### Best Practices

#### Source Control

- **COMMIT generated code to source control** - enables code review and diffs
- Keep OpenAPI specs in version control (`openapi/` directory)
- Document any spec modifications needed for compatibility
- Use semantic versioning for spec files (e.g., `radarr-v3.yaml`)

#### Regeneration Workflow

```bash
# Create a script for easy regeneration
./scripts/generate-openapi-clients.sh

# Run after updating OpenAPI specs
git diff Thriftwood/Services/*/Generated/  # Review changes
./scripts/run-tests.sh                     # Verify compilation
git add Thriftwood/Services/*/Generated/   # Commit changes
```

#### Code Review

- Review generated code in PRs (compare diffs)
- Do NOT manually edit generated files
- If customization needed, wrap generated code in service layer
- Document any workarounds or spec quirks

#### Testing Strategy

- Mock the service layer wrapper (not generated API)
- Use generated models in test fixtures
- Test integration with real API in separate integration tests
- Keep unit tests isolated from generated code

### Configuration Management

Create separate config files per service to customize generation:

```yaml
# openapi/radarr-config.yaml
library: urlsession
projectName: RadarrAPI
responseAs: AsyncAwait
enumUnknownDefaultCase: true

# openapi/sonarr-config.yaml
library: urlsession
projectName: SonarrAPI
responseAs: AsyncAwait
enumUnknownDefaultCase: true
```

### Setup Instructions

1. Install openapi-generator via Homebrew: `brew install openapi-generator`
2. Download OpenAPI spec files to `openapi/` directory
3. Create configuration files for each service in `openapi/`
4. Run generation script: `./scripts/generate-openapi-clients.sh`
5. Add generated files to Xcode project
6. Create service layer wrappers around generated clients
7. Register services in DI container
8. Commit generated code to source control

### Related Decisions

- **ADR-0003**: Use Swinject for Dependency Injection - Generated clients wrapped in services registered in DIContainer
- **ADR-0005**: Use MVVM-C Pattern - Generated clients fit into service layer of architecture
- **ADR-0004**: ~~Use AsyncHTTPClient~~ - Superseded by this decision for services with OpenAPI specs; manual URLSession for services without specs

### Implementation Timeline

- **Milestone 2 Week 4**: Radarr OpenAPI integration (swift6 generator)
- **Milestone 2 Week 5**: Sonarr OpenAPI integration
- **Milestone 4 Week 11**: Lidarr OpenAPI integration
- **Review Date**: After Milestone 2 completion (Week 6) - evaluate effectiveness and developer experience

### Documentation References

- [OpenAPITools/openapi-generator](https://github.com/OpenAPITools/openapi-generator)
- [swift6 Generator Documentation](https://openapi-generator.tech/docs/generators/swift6)
- [OpenAPI Specification](https://www.openapis.org/)
- [Radarr API Documentation](https://radarr.video/docs/api/)
- [Sonarr API Documentation](https://sonarr.tv/docs/api/)
- `.github/copilot-instructions.md` - OpenAPI-first guidance
- `.github/instructions/spec-driven-workflow-v1.instructions.md` - Spec-driven development workflow
