---
docid: ADR-070
title: ADR 029 Microsoft Extensions Ai Adoption
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

﻿---
docid: ADR-029
title: Microsoft.Extensions.AI Adoption for MCP Server
status: Accepted
date: 2026-01-03
owner: @Backend
---

# ADR-029: Microsoft.Extensions.AI Adoption for MCP Server

## Context

The B2X MCP server requires AI provider integrations for OpenAI, Anthropic, and Azure OpenAI. Initially, we implemented custom IAIProvider interfaces with direct SDK calls. However, since we're not yet released, we have the opportunity to adopt Microsoft's official Microsoft.Extensions.AI library for better long-term maintainability and alignment with .NET ecosystem standards.

## Decision

**We will adopt Microsoft.Extensions.AI (version 10.1.1) for all AI provider implementations in the MCP server.**

### Rationale

1. **Official Microsoft Support**: Microsoft.Extensions.AI provides official abstractions that are maintained and supported by Microsoft
2. **Unified Interface**: IChatClient interface provides consistent API across all providers
3. **Built-in Features**: Includes telemetry, middleware, and extensibility points out of the box
4. **Future-Proof**: Aligns with Microsoft's AI strategy and .NET 10 ecosystem
5. **Tenant Isolation Maintained**: Custom security controls and tenant isolation remain intact
6. **Not Yet Released**: Pre-release timing allows for architectural changes without breaking existing deployments

## Implementation Details

### Package Changes
- Added `Microsoft.Extensions.AI` v10.1.1
- Added `Microsoft.Extensions.AI.OpenAI` v10.1.1
- Added `Microsoft.Extensions.AI.Anthropic` v10.1.1
- Added `Microsoft.Extensions.AI.AzureAIInference` v10.1.1

### Provider Refactoring
Each provider now uses Microsoft.Extensions.AI's IChatClient:

```csharp
// OpenAI Provider
var client = new OpenAIClient(apiKey).AsChatClient(model);

// Anthropic Provider
var client = new AnthropicClient(apiKey).AsChatClient(model);

// Azure OpenAI Provider
var client = new AzureOpenAIClient(new Uri(endpoint), new ApiKeyCredential(apiKey))
    .AsChatClient(model);
```

### Additional Providers Added (2026-01-03)

Following the successful Microsoft.Extensions.AI adoption, we expanded the provider ecosystem to include local and on-premise AI options:

#### Ollama Provider
- **Package**: OllamaSharp v5.4.12 (Microsoft-recommended)
- **Implementation**: Uses OllamaSharp's Microsoft.Extensions.AI integration
- **Features**: Local and network Ollama instances, tenant-specific endpoints
- **Security**: Maintains tenant isolation and consumption monitoring

```csharp
// Ollama Provider
var ollamaClient = new OllamaSharp.OllamaApiClient(endpoint);
var client = ollamaClient.AsChatClient(model);
```

#### GitHub Models Provider
- **API**: GitHub Models (OpenAI-compatible endpoint)
- **Implementation**: Uses OpenAI-compatible client pointing to GitHub's inference API
- **Features**: Access to GitHub's AI models through unified interface
- **Endpoint**: `https://models.inference.ai.azure.com`

```csharp
// GitHub Models Provider
var client = new OpenAIClient(
    new ApiKeyCredential(apiKey),
    new OpenAIClientOptions { Endpoint = new Uri("https://models.inference.ai.azure.com") }
).AsChatClient(model);
```

### Preserved Features
- ✅ Tenant-specific API key retrieval from Key Vault
- ✅ Custom consumption tracking and monitoring
- ✅ Exclusive AI access control middleware
- ✅ Multi-tenant isolation and security
- ✅ System prompt management from database
- ✅ Token usage reporting

## Consequences

### Positive
- **Maintainability**: Official Microsoft abstractions reduce custom code maintenance
- **Consistency**: Unified IChatClient interface across all providers
- **Features**: Built-in telemetry, middleware support, and extensibility
- **Future Compatibility**: Automatic updates with .NET releases
- **Ecosystem Alignment**: Follows Microsoft AI development patterns

### Negative
- **Dependency**: Additional Microsoft.Extensions.AI package dependency
- **Migration Effort**: Refactoring existing custom implementations
- **Learning Curve**: Team needs to understand new abstractions

### Risks
- **Library Maturity**: Microsoft.Extensions.AI is relatively new (2024 release)
- **Breaking Changes**: Potential future breaking changes in early versions
- **Vendor Lock-in**: Increased dependency on Microsoft AI ecosystem

## Alternatives Considered

### Alternative 1: Keep Custom Implementation
- **Pros**: Full control, no external dependencies, proven security model
- **Cons**: Higher maintenance burden, no ecosystem alignment, custom abstractions

### Alternative 2: Direct SDK Usage Only
- **Pros**: Simple, direct API access, minimal abstraction overhead
- **Cons**: Inconsistent interfaces, no unified middleware, harder testing

### Alternative 3: Wait for Library Maturity
- **Pros**: Adopt when library is more stable
- **Cons**: Miss pre-release architectural flexibility, delay ecosystem alignment

## Compliance and Security

- **Security**: All existing security controls (Key Vault, tenant isolation, consumption monitoring) remain unchanged
- **Compliance**: No impact on GDPR, data protection, or regulatory compliance
- **Audit**: Custom security implementations provide better audit trails than generic abstractions

## Testing Strategy

- **Unit Tests**: Update existing provider tests to use Microsoft.Extensions.AI mocks
- **Integration Tests**: Verify end-to-end AI functionality with real providers
- **Security Tests**: Ensure tenant isolation and access controls work with new implementation
- **Performance Tests**: Validate that Microsoft.Extensions.AI doesn't introduce performance regressions

## Rollback Plan

If issues arise with Microsoft.Extensions.AI:
1. Revert to custom IAIProvider implementations
2. Keep Microsoft.Extensions.AI packages for future evaluation
3. Document lessons learned for future adoption attempts

## Implementation Timeline

- **Phase 1** (Completed 2026-01-03): Package updates, provider refactoring, and ecosystem expansion
  - ✅ Microsoft.Extensions.AI adoption for OpenAI, Anthropic, Azure
  - ✅ Ollama provider integration using OllamaSharp
  - ✅ GitHub Models provider integration
  - ✅ All providers registered in DI container
  - ✅ Build and test validation successful
- **Phase 2** (Next): Update unit tests and integration tests
- **Phase 3** (Future): Add Microsoft.Extensions.AI middleware for telemetry
- **Phase 4** (Future): Evaluate additional Microsoft.Extensions.AI features

## Related Documents

- [KB-006] Wolverine Patterns - CQRS implementation patterns
- [ADR-001] Wolverine over MediatR - CQRS framework decision
- [CMP-002] MCP Server Security Assessment - Security requirements
- [REQ-004] MCP Server for Tenant Administrators - Feature requirements

---

**Decision Made By**: @Backend (with input from @Architect and @Security)  
**Approved By**: @SARAH  
**Implementation Owner**: @Backend  
**Review Date**: Q1 2026