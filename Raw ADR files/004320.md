# ADR-011: Multi-Platform Embedding Strategy

## Status
Accepted

## Context

ToolVault needs to integrate across multiple platform types with varying integration capabilities:

1. **Primary**: Debrief desktop application (native plugin support)
2. **Secondary**: Desktop IDEs like VS Code (extension model)
3. **Tertiary**: Web-based platforms (ArcGIS Online, web IDEs)

### Platform Requirements
- **Debrief**: Native plugin integration with REST API access
- **VS Code**: Extension for developers + Git repository import for analysts
- **Web Platforms**: Simple REST API consumption
- **Python IDEs**: Git repository integration with PROV-compliant tool results

### Integration Constraints
- Stateless operation (no persistent state management)
- Platform-agnostic API design
- Single service deployment model
- PROV (W3C Provenance) compliance for analytical workflows

## Decision

**Selected Strategy: Single FastAPI Service with Platform-Specific Client Adapters**

### Core Architecture
- **Single FastAPI service** provides pure REST API
- **All platforms are REST clients** consuming the same stateless endpoints
- **No state synchronization** - each interaction is independent
- **Web UI included** for discovery and standalone use

## Rationale

### Integration Approach by Platform

**Debrief (Primary):**
```
Debrief Native UI
        ↓ REST API calls
    ToolVault FastAPI Service
        ↓ Optional
    Default Browser (for discovery)
```

**VS Code/Desktop IDEs (Secondary):**
```
VS Code Extension → ToolVault REST API
                ↓
Python Analysts → Git Repository Import → PROV-compliant results
```

**Web Platforms (Tertiary):**
```
Web Application → Direct REST API calls → JSON responses
```

### API Design Philosophy

**Pure REST API:**
```python
# Platform-agnostic endpoints
GET  /api/tools                    # List available tools
GET  /api/tools/{tool_id}          # Get tool details
POST /api/tools/{tool_id}/execute  # Execute tool
GET  /api/bundle/info              # Bundle metadata

# All responses: Pure JSON, no platform-specific formatting
# All operations: Stateless, no session management
```

### Client Integration Patterns

**Desktop Application Integration:**
- Debrief implements native UI that calls ToolVault REST API
- VS Code extension provides UI wrapper around REST calls
- Both can optionally launch web UI in default browser

**Web Platform Integration:**
- Direct REST API consumption via fetch/XMLHttpRequest
- No embedding complexity - just API calls
- Platforms handle their own UI integration

**Git Repository Integration:**
- Python analysts clone tool repositories directly
- Tools provide PROV-compliant output
- Direct Python import and execution within analysis workflows

## Implementation Strategy

### FastAPI Service Architecture
```python
# Single service handles all client types
app = FastAPI(title="ToolVault API")

# Core endpoints - platform agnostic
@app.get("/api/tools")
@app.post("/api/tools/{tool_id}/execute") 
@app.get("/api/bundle/info")

# Static web UI (optional discovery interface)
app.mount("/", StaticFiles(directory="static", html=True))
```

### Platform-Specific Adapters

**Debrief Plugin:**
- Native code that makes HTTP requests to ToolVault REST API
- Provides Debrief-specific UI integration
- Option to launch web UI for tool discovery

**VS Code Extension:**
- TypeScript extension that consumes REST API
- Provides VS Code-specific UI panels and commands
- Integrates with VS Code's file system and terminal

**Web Integration SDK (Optional):**
```javascript
// Simple JavaScript helper for web platforms
class ToolVaultClient {
    constructor(baseUrl) { this.baseUrl = baseUrl; }
    
    async getTools() {
        return fetch(`${this.baseUrl}/api/tools`).then(r => r.json());
    }
    
    async executeTool(toolId, inputs) {
        return fetch(`${this.baseUrl}/api/tools/${toolId}/execute`, {
            method: 'POST', 
            body: JSON.stringify(inputs)
        }).then(r => r.json());
    }
}
```

## Consequences

### Positive
- **Simplified Architecture**: Single service, multiple thin clients
- **Platform Independence**: Same API works across all platforms
- **Stateless Operation**: No complex state synchronization issues
- **Development Efficiency**: One API to maintain, not multiple embedding approaches
- **Security Simplicity**: Standard HTTP security, no cross-origin embedding issues

### Negative
- **Platform-Specific Development**: Each client needs custom implementation
- **No State Sharing**: Users can't share session data between platforms
- **Integration Effort**: Each platform requires dedicated client development

### Neutral
- **Performance**: Network overhead for all operations, but stateless simplicity
- **Feature Parity**: All platforms access same tools, UI differences only
- **Updates**: Service updates affect all platforms uniformly

## Platform-Specific Implementation Notes

### Debrief Integration
```java
// Debrief plugin example (Java/C++)
public class ToolVaultPlugin {
    private String apiBaseUrl = "http://localhost:8000";
    
    public List<Tool> getAvailableTools() {
        // HTTP GET to /api/tools
    }
    
    public void launchDiscoveryUI() {
        Desktop.browse(new URI(apiBaseUrl + "/"));
    }
}
```

### VS Code Extension
```typescript
// VS Code extension
export class ToolVaultProvider {
    constructor(private apiUrl: string) {}
    
    async getTools(): Promise<Tool[]> {
        const response = await fetch(`${this.apiUrl}/api/tools`);
        return response.json();
    }
}
```

### Web Platform Integration
```html
<!-- Simple web integration -->
<script>
const toolVault = new ToolVaultClient('https://toolvault.example.com');
toolVault.getTools().then(tools => renderToolList(tools));
</script>
```

## Development and Deployment

### Single Service Deployment
- One ToolVault FastAPI service per bundle
- Configurable port for multiple bundle instances
- Standard HTTP service - no special embedding requirements

### Client Development
- Each platform maintains its own client code
- Shared API documentation and examples
- Optional JavaScript SDK for web platforms

### Testing Strategy
- API testing covers all client scenarios
- Platform-specific client testing separate
- Integration testing via REST API calls