# ADR 004: API Versioning Strategy

## Context

When designing the Cloud Connexa Python client, we needed to determine an API versioning strategy that would:

1. Support multiple API versions simultaneously (initially v1.0 and v1.1.0)
2. Provide a seamless developer experience when transitioning between versions
3. Maintain backward compatibility for client applications
4. Leverage new API features when available
5. Enable future API version support with minimal codebase changes

## Decision

We have decided to implement a multi-faceted versioning strategy with:

1. **Version-Aware Client**
   - Client instance configured with specific API version
   - Default to latest supported version (currently v1.1.0)
   - Allow explicit version selection for backward compatibility

2. **Factory-Based Service Creation**
   - Service implementations specific to each API version
   - Automatic selection based on client's configured version
   - Common interface across all version implementations

3. **Adapter Pattern for Response Handling**
   - Version-specific adapters to normalize API responses
   - Consistent model interfaces regardless of API version
   - Transparent handling of version-specific data structures

4. **Graceful Degradation**
   - Fallback mechanisms for version-specific features
   - Feature detection at runtime when needed
   - Clear error messages when using unsupported features

## Implementation Details

### Version Configuration

The client accepts an explicit API version at initialization:

```python
# Default to latest version (1.1.0)
client = CloudConnexaClient(
    api_url="https://api.cloudconnexa.com",
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# Explicitly use older version
client_v1_0 = CloudConnexaClient(
    api_url="https://api.cloudconnexa.com",
    client_id="your_client_id",
    client_secret="your_client_secret",
    api_version="1.0"
)
```

### Service Factory Implementation

Services are created via a factory that selects the appropriate implementation:

```python
class ServiceFactory:
    @classmethod
    def create_service(cls, service_type, client, version=None):
        """Create a service instance based on type and version."""
        if version is None:
            version = client.api_version
            
        if service_type == "network":
            if version == "1.0":
                return NetworkServiceV1(client)
            elif version == "1.1.0":
                return NetworkServiceV110(client)
        # Other service types...
        
        raise ValueError(f"Unsupported service type or version: {service_type}, {version}")
```

### Version-Specific Service Implementation

Each service has version-specific implementations with a consistent interface:

```python
class BaseNetworkService:
    """Base class defining network service interface."""
    
    def list(self, **kwargs):
        """List networks."""
        raise NotImplementedError()
        
    def get(self, network_id):
        """Get a single network."""
        raise NotImplementedError()
        
    # Other standard methods...

class NetworkServiceV1(BaseNetworkService):
    """v1.0 implementation of NetworkService."""
    
    def __init__(self, client):
        self.client = client
        
    def list(self, **kwargs):
        """List networks using v1.0 API."""
        # v1.0 implementation
        response = self.client.execute_request("GET", "/networks", params=kwargs)
        return [NetworkAdapter.to_model(item, version="1.0") for item in response.json().get("networks", [])]
        
    def get(self, network_id):
        """Get a single network using v1.0 API."""
        # v1.0 implementation
        response = self.client.execute_request("GET", f"/networks/{network_id}")
        return NetworkAdapter.to_model(response.json(), version="1.0")

class NetworkServiceV110(BaseNetworkService):
    """v1.1.0 implementation of NetworkService."""
    
    def __init__(self, client):
        self.client = client
        
    def list(self, **kwargs):
        """List networks using v1.1.0 API."""
        # v1.1.0 implementation (may be identical to v1.0 for this method)
        response = self.client.execute_request("GET", "/networks", params=kwargs)
        return [NetworkAdapter.to_model(item, version="1.1.0") for item in response.json().get("networks", [])]
        
    def get(self, network_id):
        """Get a single network using v1.1.0 API."""
        # v1.1.0 implementation (may be identical to v1.0 for this method)
        response = self.client.execute_request("GET", f"/networks/{network_id}")
        return NetworkAdapter.to_model(response.json(), version="1.1.0")
```

### Adapter Pattern for Data Models

Adapters handle version-specific response formats:

```python
class NetworkAdapter:
    """Adapter for network response data."""
    
    @classmethod
    def to_model(cls, data, version=None):
        """Convert API response to model."""
        if version == "1.0":
            # Handle v1.0 format
            return NetworkModel(
                id=data.get("id"),
                name=data.get("name"),
                cidr=data.get("cidr"),
                internet_access=data.get("internetAccess", "split_tunnel_on"),
                egress=data.get("egress", False),
            )
        else:
            # Handle v1.1.0 format (may include additional fields)
            return NetworkModel(
                id=data.get("id"),
                name=data.get("name"),
                cidr=data.get("cidr"),
                internet_access=data.get("internetAccess", "split_tunnel_on"),
                egress=data.get("egress", False),
                # v1.1.0 specific fields could be added here
            )
```

### Version-Specific Feature Handling

For features only available in certain versions:

```python
class DNSServiceV1(BaseDNSService):
    """v1.0 implementation of DNSService."""
    
    def get(self, record_id):
        """Get a single DNS record using v1.0 API."""
        # v1.0 doesn't have a single record endpoint, so list and filter
        records = self.list(record_id=record_id)
        return records[0] if records else None

class DNSServiceV110(BaseDNSService):
    """v1.1.0 implementation of DNSService."""
    
    def get(self, record_id):
        """Get a single DNS record using v1.1.0 API."""
        # v1.1.0 has a dedicated endpoint for this
        response = self.client.execute_request("GET", f"/dns/{record_id}")
        return DNSAdapter.to_model(response.json(), version="1.1.0")
```

## Migration Approach

When a new API version is released, we adopt the following migration approach:

1. **Implementation Phase**
   - Add new version-specific service implementations
   - Update adapters to handle new response formats
   - Implement new features as version-specific methods
   - Maintain full backward compatibility

2. **Testing Phase**
   - Add tests for new API features
   - Add version compatibility tests
   - Verify graceful degradation when needed
   - Test migration scenarios

3. **Documentation Phase**
   - Document API differences between versions
   - Provide migration guides for client users
   - Document version-specific features and limitations
   - Update examples to showcase new capabilities

4. **Release Phase**
   - Update default version for new clients
   - Provide clear upgrade path for existing users
   - Support both versions during transition period
   - Encourage adoption of new features

## Alternative Approaches Considered

### URL-Based Versioning Only

**Pros:**
- Simpler implementation
- Less code duplication

**Cons:**
- No abstraction for client users
- Breaks backward compatibility
- More error-prone when using version-specific features

### API Version Auto-Detection

**Pros:**
- Less configuration for the user
- Automatic use of latest available version

**Cons:**
- Unpredictable behavior for client applications
- Harder to test and maintain
- May break during API transitions

### Separate Client Classes Per Version

**Pros:**
- Complete separation of concerns
- Clear versioning boundaries

**Cons:**
- Significant code duplication
- Harder to maintain consistency
- More difficult for users to migrate

## Consequences

### Positive

- Clean abstraction for client users
- Consistent interface across versions
- Easy migration between versions
- Support for version-specific features
- Clear extension path for future versions

### Negative

- Increased implementation complexity
- More code to maintain
- Need for comprehensive testing across versions
- Version-specific bugs and edge cases

## Implementation Notes

- The default version is set to the latest stable API version (currently 1.1.0)
- Service implementations should inherit from a common base class
- Adapters handle all version-specific response format differences
- Error messages should clearly indicate version compatibility issues
- Tests should verify behavior across all supported versions

## Related Decisions

- [001: Client Structure](001_client_structure.md)
- [003: Error Handling](003_error_handling.md) 