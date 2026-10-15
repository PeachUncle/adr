# ADR-004: Dynamic Dependency Version Management

## Status
Accepted

## Context
Generated SDKs need up-to-date dependencies to ensure security patches, performance improvements, and compatibility with modern development environments. However, hardcoded dependency versions quickly become outdated and may contain security vulnerabilities.

## Decision
We will implement a dynamic dependency version fetching system with multi-tier fallback strategies to ensure generated SDKs always use current, secure dependency versions.

## Architecture

### Three-Tier Version Resolution Strategy

#### Tier 1: Live NPM Version Fetching (Primary)
```bash
npm show <package> version
```
- **Advantages**: Always returns latest stable version
- **Use Case**: Online development environments with npm available
- **Fallback Trigger**: Command fails or times out

#### Tier 2: NPM Registry API (Secondary)
```bash
curl -s https://registry.npmjs.org/<package>/latest
```
- **Advantages**: Works without npm CLI, lighter weight
- **Use Case**: Build environments without npm but with internet access
- **Fallback Trigger**: API request fails or returns invalid JSON

#### Tier 3: Hardcoded Fallback Versions (Tertiary)
```ocaml
let fallback_versions = [
  ("typescript", "5.9.2");
  ("@types/node", "24.5.2");
  ("jest", "30.1.3");
]
```
- **Advantages**: Always available, no network dependency
- **Use Case**: Offline environments, CI systems with restricted network access
- **Update Strategy**: Regularly updated through generator releases

### Implementation

```ocaml
type version_strategy = LiveFetch | ApiFallback | HardcodedFallback

let get_package_version ?(use_fallback_first=false) package_name =
  if use_fallback_first then
    get_fallback_version package_name
  else
    match fetch_latest_version_npm package_name with
    | Ok version -> Ok version
    | Error _ ->
      match fetch_latest_version_api package_name with
      | Ok version -> Ok version
      | Error _ -> get_fallback_version package_name
```

### Version Validation

#### Format Validation:
- **Semantic Versioning**: Validate against semver patterns (X.Y.Z)
- **Version Range**: Ensure versions are reasonable (not too old, not pre-release)
- **Security**: Avoid known vulnerable versions

#### Quality Assurance:
- **Integration Testing**: Generated SDKs must build with fetched versions
- **Compatibility Matrix**: Track which versions work together
- **Regression Testing**: Ensure new versions don't break existing functionality

### CLI Integration

```bash
# Use live version fetching (default)
auth-sdk-generator specs/app.auth output/

# Force offline/fallback mode
auth-sdk-generator --offline specs/app.auth output/
auth-sdk-generator --fallback-versions specs/app.auth output/

# Version debugging
auth-sdk-generator --debug-versions specs/app.auth output/
```

### Language-Specific Implementation

#### TypeScript Dependencies:
- **Core**: `typescript`, `@types/node`
- **Testing**: `jest`, `@types/jest`
- **Build Tools**: Latest compatible versions
- **Version Constraints**: Maintain compatibility matrix

#### Python Dependencies:
- **Core**: `requests` (HTTP client)
- **Development**: `pytest`, `mypy`, `black`, `flake8`
- **Version Strategy**: Use pip/PyPI latest stable versions
- **Python Version Compatibility**: Support Python 3.8+

## Error Handling and Resilience

### Network Failure Handling:
- **Timeout**: Reasonable timeouts for network requests (5-10 seconds)
- **Retry Logic**: Limited retries with exponential backoff
- **Graceful Degradation**: Fall back to next tier on any failure
- **User Feedback**: Clear messaging about which strategy was used

### Version Conflict Resolution:
- **Compatibility Checking**: Validate version combinations work together
- **Dependency Resolution**: Handle transitive dependency conflicts
- **Override Mechanisms**: Allow users to specify version constraints

### Caching Strategy:
- **Local Cache**: Cache successful version lookups for session duration
- **Cache Invalidation**: Reasonable cache TTL to balance performance and freshness
- **Cache Keys**: Include package name and strategy used

## Security Considerations

### Supply Chain Security:
- **Official Registries**: Only fetch from official npm/PyPI registries
- **HTTPS**: All API requests use HTTPS
- **Version Validation**: Validate versions match expected patterns
- **Dependency Scanning**: Future integration with security vulnerability databases

### Fallback Version Management:
- **Regular Updates**: Monthly/quarterly updates to fallback versions
- **Security Patches**: Immediate updates for security vulnerabilities
- **Version Testing**: All fallback versions must pass integration tests
- **Documentation**: Track why specific fallback versions were chosen

## Monitoring and Observability

### Version Analytics:
- **Success Rates**: Track success rates for each tier
- **Version Distribution**: Monitor which versions are being used
- **Failure Analysis**: Analyze common failure patterns
- **Performance Metrics**: Track fetching performance and timeouts

### Alerting:
- **Fallback Usage**: Alert when systems consistently fall back to hardcoded versions
- **Version Staleness**: Alert when fallback versions are significantly outdated
- **Security Vulnerabilities**: Alert on known vulnerable versions

## Testing Strategy

### Unit Tests:
- **Version Fetching**: Test each tier independently
- **Fallback Logic**: Test fallback chain behavior
- **Error Handling**: Test network failures and invalid responses
- **Version Validation**: Test version format validation

### Integration Tests:
- **Generated SDKs**: Build generated SDKs with fetched versions
- **Version Compatibility**: Test multiple version combinations
- **Offline Mode**: Test generation in offline environments
- **Performance**: Test version fetching performance under load

### Make Target Tests:
```bash
make test-live-versions      # Test with live version fetching
make test-fallback-versions  # Test with fallback versions
make test-versions          # Test both strategies
```

## Consequences

### Positive:
- **Security**: Generated SDKs use latest dependency versions with security patches
- **Compatibility**: Generated SDKs work with current development environments
- **Reliability**: Multi-tier fallback ensures generation works in all environments
- **Maintenance**: Reduces manual dependency version updates
- **User Experience**: Generated SDKs use modern, well-supported dependencies

### Negative:
- **Complexity**: Version management adds complexity to generator
- **Network Dependency**: Live fetching requires internet connectivity
- **Variability**: Different environments may generate SDKs with different versions
- **Performance**: Version fetching adds latency to generation process
- **Maintenance**: Fallback versions require regular updates

## Future Enhancements

### Planned Features:
1. **Version Constraints**: Support for version ranges and constraints
2. **Security Integration**: Integration with vulnerability databases
3. **Custom Registries**: Support for private/enterprise package registries
4. **Version Locking**: Generate lock files for reproducible builds
5. **Dependency Analysis**: Advanced dependency conflict resolution

### Monitoring Improvements:
1. **Analytics Dashboard**: Real-time monitoring of version usage
2. **Automated Updates**: Automated fallback version updates
3. **Quality Gates**: Block generation with known vulnerable versions
4. **Performance Optimization**: Caching and parallel version fetching

## Related ADRs
- ADR-001: OCaml-Based Architecture
- ADR-002: Multi-Language SDK Generation Strategy
- ADR-003: In-Memory Validation Architecture