# ADR-009: Conditional Imports for External Dependencies

## Status
Accepted

## Context
The Payments Ingestion system integrates with multiple external services and SDKs:
- Azure Event Hubs SDK (`azure-eventhub`)
- Azure Blob Storage SDK (`azure-storage-blob`)
- Kafka SDK (`kafka-python`)
- PostgreSQL adapter (`psycopg2-binary`)

These dependencies create challenges:
- **Testing**: Tests fail if SDKs aren't installed
- **Development**: Developers may not need all SDKs for their work
- **CI/CD**: Different environments may have different dependencies
- **Optional Features**: Some features may be optional (e.g., Kafka support)
- **Import Errors**: Hard failures prevent code from loading even when feature isn't used

We need a strategy that:
- Allows code to import and test without all dependencies
- Supports optional features gracefully
- Enables local development without Azure credentials
- Maintains type hints and IDE support

## Decision
We will implement **conditional imports** with fallback classes:

1. **Try/Except Import Pattern**
   ```python
   try:
       from azure.eventhub import EventData
       AZURE_EVENTHUB_AVAILABLE = True
   except ImportError:
       AZURE_EVENTHUB_AVAILABLE = False
       # Fallback class for type hints
       class EventData:
           pass
   ```

2. **Feature Flags**
   - Module-level flags indicate availability: `AZURE_EVENTHUB_AVAILABLE`
   - Runtime checks before using SDK features
   - Clear error messages when features unavailable

3. **Fallback Classes**
   - Minimal stub classes for type hints
   - Prevent `NameError` when SDK not available
   - Allow code to load and be tested

4. **Graceful Degradation**
   - Features check availability before use
   - Raise `ImportError` with helpful message if required feature unavailable
   - Allow optional features to be disabled

## Consequences

### Positive
- **Testability**: Tests can run without all SDKs installed
- **Development Flexibility**: Developers can work on subsets of code
- **CI/CD**: Different test environments can have different dependencies
- **Optional Features**: Features can be truly optional
- **Error Messages**: Clear errors when dependencies missing
- **Type Safety**: Type hints still work with fallback classes
- **Import Safety**: Code loads even if optional dependencies missing

### Negative
- **Code Complexity**: More conditional logic in imports
- **Type Accuracy**: Fallback classes less accurate than real types
- **Runtime Errors**: Some errors only appear at runtime vs import time
- **Documentation**: Need to document which dependencies are required
- **Maintenance**: Must keep fallback classes in sync with real classes

## Alternatives Considered

### Always Require All Dependencies
**Pros**: Simpler code, type accuracy, import-time errors
**Cons**: Heavy dependencies, testing complexity, development friction
**Reason rejected**: Too restrictive for development and testing

### Separate Packages
**Pros**: Clear dependencies, optional features
**Cons**: Complex packaging, version management, installation complexity
**Reason rejected**: Single package is simpler for users

### Lazy Imports
**Pros**: Only import when needed
**Cons**: Runtime import errors, harder to detect issues early
**Reason rejected**: Conditional imports provide better error handling

### Dependency Injection
**Pros**: Flexible, testable
**Cons**: More complex architecture, overkill for SDKs
**Reason rejected**: Conditional imports simpler for SDK dependencies

## Implementation Details

### Pattern Example
```python
try:
    from azure.storage.blob import BlobServiceClient
    AZURE_STORAGE_AVAILABLE = True
except ImportError:
    AZURE_STORAGE_AVAILABLE = False
    # Fallback for type hints
    class BlobServiceClient:
        pass

class BlobRawEventStore:
    def __init__(self, ...):
        if not AZURE_STORAGE_AVAILABLE:
            raise ImportError(
                "azure-storage-blob package is required. "
                "Install with: pip install azure-storage-blob"
            )
```

### Storage Module Pattern
- `storage/__init__.py` uses conditional imports
- Only imports `BlobRawEventStore` if Azure SDK available
- Tests can import other storage components without Azure SDK

### Consumer Module Pattern
- `consumer/event_hubs.py` has fallback `EventData` class
- Tests can import and test consumer interface without Azure SDK
- Runtime checks ensure proper error messages

## References
- Source: `src/function_app/storage/__init__.py`
- Source: `src/function_app/consumer/event_hubs.py`
- Source: `src/function_app/connections/hybrid_storage.py`

