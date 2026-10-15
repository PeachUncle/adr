---
docid: ADR-058
title: ADR 023 Tenant Mcp Prompt Management
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

﻿# ADR-023: Tenant-Specific MCP Prompt Management

**Status**: Proposed  
**Date**: 2026-01-03  
**Deciders**: @Architect, @Backend, @Frontend, @Security  
**DocID**: `ADR-023`

---

## Context

B2X implements an MCP (Model Context Protocol) server for tenant administrators (REQ-004), providing AI-powered tools for CMS design, email templates, and system management. Currently, all tenants use the same system prompts, limiting customization capabilities.

**Business Need**: Tenants require the ability to customize AI behavior through prompt engineering to match their brand voice, industry-specific terminology, and operational workflows.

**Current State**:
- MCP server exists with basic tool implementations
- No tenant-specific prompt customization
- Hardcoded prompts in tool definitions
- No version control or rollback capabilities

**Requirements**:
1. **Prompt Management UI**: Interface for viewing, editing, and versioning system prompts
2. **Per-Tool Prompts**: Custom prompts for each MCP tool (CMS design, email templates, etc.)
3. **Prompt Templates**: Base templates with variable substitution
4. **Version Control**: Track prompt changes with rollback capability
5. **Security**: Prevent prompt injection, validate prompt content
6. **Fallbacks**: Default prompts if tenant customizations fail

---

## Decision

We implement a **Tenant Prompt Management System** with the following architecture:

### 1. Data Model

#### TenantPrompt Entity
```csharp
public class TenantPrompt : Entity
{
    public Guid TenantId { get; set; }
    public string ToolName { get; set; } // e.g., "cms-design", "email-template"
    public string PromptKey { get; set; } // e.g., "page-layout-generator"
    public string Content { get; set; }
    public int Version { get; set; }
    public bool IsActive { get; set; }
    public DateTime CreatedAt { get; set; }
    public Guid CreatedBy { get; set; }
    public string? Description { get; set; }
    public Dictionary<string, string> Variables { get; set; } // Template variables
}
```

#### PromptTemplate Entity
```csharp
public class PromptTemplate : Entity
{
    public string ToolName { get; set; }
    public string TemplateKey { get; set; }
    public string BaseContent { get; set; }
    public Dictionary<string, string> DefaultVariables { get; set; }
    public List<string> RequiredVariables { get; set; }
    public bool IsSystemTemplate { get; set; } // Cannot be deleted
}
```

#### PromptVersion Entity (for audit trail)
```csharp
public class PromptVersion : Entity
{
    public Guid TenantPromptId { get; set; }
    public int Version { get; set; }
    public string Content { get; set; }
    public Dictionary<string, string> Variables { get; set; }
    public DateTime CreatedAt { get; set; }
    public Guid CreatedBy { get; set; }
    public string ChangeReason { get; set; }
}
```

### 2. API Design

#### Endpoints

**GET /api/admin/prompts**
- List all prompts for current tenant
- Query parameters: toolName, isActive, page, size
- Response: Paginated list of TenantPrompt DTOs

**GET /api/admin/prompts/{id}**
- Get specific prompt with version history
- Response: TenantPrompt with versions array

**POST /api/admin/prompts**
- Create new tenant prompt
- Body: CreateTenantPromptRequest
- Validation: Check for prompt injection, required variables

**PUT /api/admin/prompts/{id}**
- Update existing prompt (creates new version)
- Body: UpdateTenantPromptRequest
- Creates audit trail entry

**DELETE /api/admin/prompts/{id}**
- Soft delete prompt (mark inactive)
- Cannot delete system templates

**POST /api/admin/prompts/{id}/rollback/{version}**
- Rollback to specific version
- Creates new version with old content

**GET /api/admin/prompts/templates**
- List available prompt templates
- Response: List of PromptTemplate DTOs

#### Request/Response DTOs

```csharp
public class TenantPromptDto
{
    public Guid Id { get; set; }
    public string ToolName { get; set; }
    public string PromptKey { get; set; }
    public string Content { get; set; }
    public int Version { get; set; }
    public bool IsActive { get; set; }
    public DateTime CreatedAt { get; set; }
    public string CreatedByName { get; set; }
    public string? Description { get; set; }
    public Dictionary<string, string> Variables { get; set; }
    public List<PromptVersionDto> Versions { get; set; }
}

public class CreateTenantPromptRequest
{
    public string ToolName { get; set; }
    public string PromptKey { get; set; }
    public string Content { get; set; }
    public string? Description { get; set; }
    public Dictionary<string, string> Variables { get; set; }
}
```

### 3. Frontend Components

#### Prompt Management Page (`/admin/prompts`)
- **Prompt List Component**: Table/grid showing all prompts with status, version, last modified
- **Tool Filter**: Dropdown to filter by MCP tool
- **Search**: Search by prompt key or description
- **Actions**: Edit, View History, Rollback, Delete

#### Prompt Editor Component
- **Template Selector**: Choose from available templates
- **Rich Text Editor**: Monaco editor with syntax highlighting for prompt syntax
- **Variable Manager**: UI for defining template variables
- **Preview Panel**: Show rendered prompt with variable substitution
- **Validation Panel**: Real-time validation feedback
- **Version History**: Timeline showing changes with diff view

#### Key Components

```vue
<template>
  <div class="prompt-management">
    <PromptList 
      :prompts="prompts"
      @edit="openEditor"
      @view-history="showHistory"
    />
    
    <PromptEditor
      v-if="editingPrompt"
      :prompt="editingPrompt"
      :templates="templates"
      @save="savePrompt"
      @cancel="closeEditor"
    />
    
    <PromptHistoryModal
      v-if="showingHistory"
      :versions="versions"
      @rollback="rollbackVersion"
    />
  </div>
</template>
```

### 4. Security Architecture

#### Input Validation
- **Prompt Injection Prevention**: 
  - Sanitize user input to prevent code injection
  - Validate against allowed prompt syntax
  - Rate limit prompt updates (max 10/hour per tenant)

- **Content Validation**:
  - Maximum prompt length (10,000 characters)
  - Allowed characters (alphanumeric, punctuation, newlines)
  - Forbidden patterns (system commands, file paths)

#### Authorization
- **Role-based Access**: Only tenant admins can manage prompts
- **Audit Logging**: All prompt changes logged with user context
- **Version Control**: Automatic versioning prevents accidental data loss

#### Runtime Security
- **Fallback Mechanism**: Use default prompts if tenant prompts fail validation
- **Isolation**: Tenant prompts cannot access other tenant data
- **Monitoring**: Alert on suspicious prompt patterns

### 5. MCP Integration

#### Prompt Resolution Strategy
```csharp
public class TenantAwarePromptProvider : IPromptProvider
{
    public async Task<string> GetPromptAsync(string toolName, string promptKey, Guid tenantId)
    {
        // 1. Try tenant-specific prompt
        var tenantPrompt = await _repository.GetActivePromptAsync(tenantId, toolName, promptKey);
        if (tenantPrompt != null && IsValidPrompt(tenantPrompt.Content))
        {
            return RenderTemplate(tenantPrompt.Content, tenantPrompt.Variables);
        }
        
        // 2. Fallback to system default
        var systemPrompt = await _repository.GetSystemPromptAsync(toolName, promptKey);
        return systemPrompt?.Content ?? GetHardcodedFallback(toolName, promptKey);
    }
}
```

#### Tool Registration
```csharp
public class CmsDesignTool : McpTool
{
    private readonly IPromptProvider _promptProvider;
    
    public CmsDesignTool(IPromptProvider promptProvider)
    {
        _promptProvider = promptProvider;
    }
    
    public override async Task<string> GetSystemPromptAsync()
    {
        var tenantId = _tenantContext.GetCurrentTenantId();
        return await _promptProvider.GetPromptAsync("cms-design", "page-layout-generator", tenantId);
    }
}
```

### 6. Implementation Phases

#### Phase 1: Core Infrastructure (Week 1-2)
- [ ] Create database migrations for prompt entities
- [ ] Implement repository layer for prompt CRUD operations
- [ ] Add basic API endpoints for prompt management
- [ ] Create prompt validation service

#### Phase 2: MCP Integration (Week 3)
- [ ] Implement TenantAwarePromptProvider
- [ ] Update existing MCP tools to use dynamic prompts
- [ ] Add fallback mechanisms
- [ ] Test prompt resolution logic

#### Phase 3: Frontend Development (Week 4-5)
- [ ] Create prompt management UI components
- [ ] Implement prompt editor with Monaco
- [ ] Add version history and rollback functionality
- [ ] Integrate with existing admin layout

#### Phase 4: Security & Testing (Week 6)
- [ ] Implement comprehensive input validation
- [ ] Add audit logging and monitoring
- [ ] Create unit and integration tests
- [ ] Security review and penetration testing

#### Phase 5: Documentation & Training (Week 7)
- [ ] Update API documentation
- [ ] Create user guides for prompt customization
- [ ] Admin training materials
- [ ] Rollout to beta tenants

### 7. Migration Strategy

#### Existing Tenants
- All existing tenants start with system default prompts
- No breaking changes to existing functionality
- Gradual opt-in for prompt customization

#### Data Migration
- Pre-populate system templates from hardcoded prompts
- Create initial TenantPrompt records for tenants with customizations
- Version history starts from migration date

### 8. Monitoring & Analytics

#### Key Metrics
- **Usage**: Number of custom prompts per tenant
- **Performance**: Prompt resolution time (< 100ms target)
- **Errors**: Failed prompt validations, fallback usage
- **Security**: Suspicious prompt patterns detected

#### Alerts
- High error rate in prompt resolution
- Unusual prompt update frequency
- Failed security validations

---

## Consequences

### Positive
- **Flexibility**: Tenants can customize AI behavior to match their needs
- **Brand Consistency**: Prompts can reflect tenant's voice and terminology
- **Innovation**: Enables advanced AI customization features
- **Auditability**: Full version control and change tracking

### Negative
- **Complexity**: Additional layer of abstraction in prompt management
- **Performance**: Slight overhead in prompt resolution
- **Maintenance**: Need to maintain both system and tenant prompts

### Risks
- **Prompt Injection**: Security risk if validation is insufficient
- **Performance Impact**: Database queries for every tool execution
- **Data Consistency**: Ensuring prompt validity across versions

### Mitigation
- **Caching**: Cache resolved prompts with tenant context
- **Validation**: Multi-layer validation (frontend, API, runtime)
- **Monitoring**: Comprehensive logging and alerting
- **Testing**: Extensive security and performance testing

---

## Alternatives Considered

### Alternative 1: Configuration-based Prompts
Store prompts in tenant configuration JSON instead of database entities.

**Pros**: Simpler data model, easier deployment
**Cons**: No version control, harder to manage large prompts, no audit trail

### Alternative 2: File-based Prompts
Store prompts as files in tenant-specific directories.

**Pros**: Easy editing, version control via git
**Cons**: File system management, backup complexity, access control issues

### Alternative 3: Inline Prompt Customization
Allow prompts to be customized directly in tool configuration.

**Pros**: Immediate customization, no additional UI
**Cons**: No reuse, hard to maintain, security risks

**Decision**: Database approach provides best balance of flexibility, security, and maintainability.

---

## References

- [REQ-004: MCP Server for Tenant Administrators](../requirements/REQ-004-mcp-server-tenant-admin.md)
- [ADR-022: Multi-Tenant Domain Management](../decisions/ADR-022-multi-tenant-domain-management.md)
- [MCP Protocol Specification](https://modelcontextprotocol.io/specification)