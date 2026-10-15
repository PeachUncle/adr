---
docid: ADR-066
title: ADR 028 Ai Consumption Monitoring
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

﻿# ADR-028: AI Consumption Monitoring and Limiting for MCP Server Operations

**Status:** Proposed  
**Date:** 3. Januar 2026  
**Context:** MCP Server AI Integration  
**Decision Authors:** @Architect, @Security, @DevOps

---

## Problem

The B2X platform integrates AI services through MCP (Model Context Protocol) servers for tenant administrators. However, without proper controls, AI consumption could lead to:

- **Uncontrolled Costs**: Unlimited AI API calls driving up operational expenses
- **Resource Abuse**: Malicious or accidental overuse of AI resources
- **Security Risks**: Unauthorized AI access from other system components
- **Compliance Issues**: Lack of audit trails for AI usage in regulated environments
- **Performance Degradation**: AI service overload affecting system responsiveness

Current architecture lacks centralized AI consumption monitoring, rate limiting, and cost controls specifically for MCP operations.

---

## Solution

**Implement Comprehensive AI Consumption Monitoring and Limiting System**

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server Layer                         │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              AI Service Gateway                      │    │
│  │  ┌─────────────────────────────────────────────────┐ │    │
│  │  │   Request Validation & Authorization            │ │    │
│  │  └─────────────────────────────────────────────────┘ │    │
│  │  ┌─────────────────────────────────────────────────┐ │    │
│  │  │   Usage Metering & Rate Limiting               │ │    │
│  │  └─────────────────────────────────────────────────┘ │    │
│  │  ┌─────────────────────────────────────────────────┐ │    │
│  │  │   Cost Monitoring & Budget Control             │ │    │
│  │  └─────────────────────────────────────────────────┘ │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                 AI Provider Services                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│  │ OpenAI      │ │ Anthropic   │ │ Local LLM  │ ...        │
│  └─────────────┘ └─────────────┘ └─────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. AI Service Gateway
**Purpose:** Centralized entry point for all AI API calls from MCP servers

**Features:**
- Single point of access for AI services
- Request routing and load balancing
- Response caching and optimization
- Emergency shutdown capabilities

#### 2. Request Validation & Authorization
**Purpose:** Ensure only authorized MCP operations can access AI services

**Implementation:**
- JWT token validation with tenant context
- MCP tool-specific authorization
- Request signing verification
- Tenant isolation enforcement

#### 3. Usage Metering & Rate Limiting
**Purpose:** Control and monitor AI consumption patterns

**Features:**
- Per-tenant rate limits (requests/minute, tokens/hour)
- Per-tool usage quotas
- Burst handling with token bucket algorithm
- Automated throttling with backoff strategies

#### 4. Cost Monitoring & Budget Control
**Purpose:** Real-time cost tracking and budget enforcement

**Features:**
- Cost calculation per API call (input/output tokens)
- Budget allocation per tenant/month
- Real-time alerts at 80%, 90%, 100% budget utilization
- Hard limits with automatic blocking

#### 5. Audit & Compliance Logging
**Purpose:** Complete audit trail for regulatory compliance

**Features:**
- Structured logging of all AI interactions
- GDPR-compliant data handling
- Export capabilities for compliance reporting
- Retention policies aligned with legal requirements

### Technical Implementation

#### Service Architecture

```csharp
// AI Service Gateway Interface
public interface IAIServiceGateway
{
    Task<AIResponse> ExecuteAsync(AIRequest request, CancellationToken ct);
}

// Request/Response Models
public record AIRequest(
    string TenantId,
    string ToolName,
    string Model,
    string Prompt,
    Dictionary<string, object> Parameters
);

public record AIResponse(
    string Content,
    int InputTokens,
    int OutputTokens,
    decimal Cost,
    TimeSpan Duration
);
```

#### Rate Limiting Implementation

```csharp
// Rate Limiter Service
public interface IRateLimiter
{
    Task<bool> CheckLimitAsync(string tenantId, string toolName);
    Task RecordUsageAsync(string tenantId, string toolName, int tokens);
}

// Configuration
public class RateLimitConfig
{
    public int RequestsPerMinute { get; set; } = 60;
    public int TokensPerHour { get; set; } = 10000;
    public int BurstLimit { get; set; } = 10;
}
```

#### Cost Monitoring

```csharp
// Cost Calculator
public interface ICostCalculator
{
    decimal CalculateCost(string model, int inputTokens, int outputTokens);
}

// Budget Manager
public interface IBudgetManager
{
    Task<bool> CheckBudgetAsync(string tenantId, decimal cost);
    Task RecordCostAsync(string tenantId, decimal cost);
    Task<BudgetStatus> GetBudgetStatusAsync(string tenantId);
}
```

#### Security Controls

```csharp
// API Key Management
public interface IApiKeyManager
{
    Task<string> GetApiKeyAsync(string provider);
    Task RotateApiKeyAsync(string provider);
}

// Request Signing
public interface IRequestSigner
{
    string SignRequest(AIRequest request, string secretKey);
    bool VerifySignature(string signature, AIRequest request, string secretKey);
}
```

### Database Schema

#### AI Usage Tracking
```sql
CREATE TABLE ai_usage_logs (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    tool_name VARCHAR(100) NOT NULL,
    model VARCHAR(50) NOT NULL,
    request_timestamp TIMESTAMP NOT NULL,
    input_tokens INT NOT NULL,
    output_tokens INT NOT NULL,
    cost DECIMAL(10,4) NOT NULL,
    duration_ms INT NOT NULL,
    status VARCHAR(20) NOT NULL
);

CREATE TABLE tenant_ai_budgets (
    tenant_id UUID PRIMARY KEY,
    monthly_budget DECIMAL(10,2) NOT NULL,
    current_spend DECIMAL(10,2) NOT NULL DEFAULT 0,
    last_reset TIMESTAMP NOT NULL,
    alert_threshold DECIMAL(3,2) NOT NULL DEFAULT 0.8
);

CREATE TABLE rate_limits (
    tenant_id UUID,
    tool_name VARCHAR(100),
    requests_per_minute INT NOT NULL,
    tokens_per_hour INT NOT NULL,
    burst_limit INT NOT NULL,
    PRIMARY KEY (tenant_id, tool_name)
);
```

### Monitoring & Alerting

#### Metrics to Monitor
- AI API call volume per tenant/tool
- Cost accumulation rates
- Rate limit hit rates
- Response times and error rates
- Budget utilization percentages

#### Alert Conditions
- Budget utilization > 80%
- Rate limit exceeded
- API key rotation required
- Unusual usage patterns detected

### Security Considerations

#### API Key Security
- Keys stored in Azure Key Vault / AWS Secrets Manager
- Automatic rotation every 30 days
- Least privilege access patterns
- Audit logging for key access

#### Request Security
- All requests must include valid JWT tokens
- Request signing with HMAC-SHA256
- Tenant context validation
- Input sanitization and validation

#### Abuse Detection
- Pattern analysis for unusual request volumes
- Geolocation-based restrictions
- Automated blocking for suspicious patterns
- Manual review triggers for high-cost operations

### Deployment & Operations

#### Configuration Management
- Environment-specific rate limits and budgets
- Provider-specific API endpoints and keys
- Monitoring thresholds and alert rules

#### Health Checks
- AI provider connectivity tests
- Rate limiter status
- Budget service availability
- Database connectivity

#### Backup & Recovery
- Usage log archival (7-year retention for compliance)
- Budget state snapshots
- Configuration backups

### Migration Strategy

#### Phase 1: Infrastructure Setup
- Deploy AI Service Gateway service
- Set up monitoring and alerting
- Configure initial rate limits and budgets

#### Phase 2: MCP Integration
- Update MCP servers to use gateway
- Implement request validation
- Enable usage tracking

#### Phase 3: Advanced Controls
- Deploy cost monitoring
- Implement budget controls
- Enable audit logging

#### Phase 4: Optimization
- Fine-tune rate limits based on usage patterns
- Implement caching and optimization
- Add predictive scaling

### Success Metrics

- **Cost Control**: 95% of AI costs within budgeted amounts
- **Performance**: <100ms additional latency per AI call
- **Reliability**: 99.9% uptime for AI services
- **Security**: Zero unauthorized AI access incidents
- **Compliance**: 100% audit trail completeness

### Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Gateway bottleneck | High latency | Horizontal scaling, caching |
| Budget overspend | Cost overrun | Hard limits, real-time monitoring |
| Key compromise | Security breach | Rotation, monitoring, encryption |
| Audit failure | Compliance violation | Redundant logging, validation |

---

## Consequences

### Positive
- **Cost Control**: Predictable AI expenses with budget enforcement
- **Security**: Isolated AI access preventing unauthorized usage
- **Compliance**: Complete audit trails for regulatory requirements
- **Performance**: Optimized AI usage with caching and rate limiting
- **Monitoring**: Real-time visibility into AI consumption patterns

### Negative
- **Complexity**: Additional service layer increases system complexity
- **Latency**: Gateway introduces minimal request latency
- **Operational Overhead**: Additional monitoring and maintenance requirements

### Neutral
- **Development Effort**: Requires implementation of gateway and monitoring services
- **Configuration Management**: New configuration parameters for rate limits and budgets

---

## Alternatives Considered

### Alternative 1: Per-Service Rate Limiting
- **Pros**: Simpler implementation, no central gateway
- **Cons**: Inconsistent enforcement, harder monitoring, security gaps
- **Decision**: Rejected due to security and compliance requirements

### Alternative 2: Third-Party AI Gateway
- **Pros**: Faster implementation, managed service
- **Cons**: Vendor lock-in, less control, compliance concerns
- **Decision**: Rejected due to regulatory requirements and cost

### Alternative 3: Client-Side Controls Only
- **Pros**: Minimal infrastructure changes
- **Cons**: Easy to bypass, no server-side enforcement
- **Decision**: Rejected due to security requirements

---

## Implementation Plan

### Phase 1 (Week 1-2): Core Infrastructure
- [ ] Design and implement AI Service Gateway service
- [ ] Set up database schema for usage tracking
- [ ] Implement basic request validation

### Phase 2 (Week 3-4): Rate Limiting & Cost Control
- [ ] Implement rate limiter with Redis backing
- [ ] Add cost calculation and budget management
- [ ] Set up monitoring dashboards

### Phase 3 (Week 5-6): Security & Compliance
- [ ] Implement API key management and rotation
- [ ] Add request signing and verification
- [ ] Enable audit logging and compliance features

### Phase 4 (Week 7-8): Integration & Testing
- [ ] Update MCP servers to use gateway
- [ ] Comprehensive testing and performance validation
- [ ] Documentation and training

---

## References

- [ADR-022] Multi-Tenant Domain Management
- [KB-017] AI Cost Optimization
- [CMP-002] MCP Server Security Assessment
- [GL-006] Token Optimization Strategy