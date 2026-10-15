---
docid: ADR-084
title: ADR 041 Ai Mode Switching Strategy
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

﻿# ADR-040: AI Mode Switching Strategy

**DocID**: `ADR-040`  
**Status**: Proposed | **Owner**: @CopilotExpert  
**Created**: 2026-01-05  
**Deciders**: @SARAH, @Architect, @Security  
**Consulted**: @Backend, @DevOps  

## Context

The B2X Framework requires flexible AI integration to support different deployment environments and compliance requirements. Current implementation relies solely on external APIs, but enterprise customers need options for internal or local AI processing to maintain data sovereignty and reduce external dependencies.

## Decision

Implement a dynamic AI mode switching system with three operational modes:

1. **Online Mode** (Default): Uses external AI APIs (OpenAI, Anthropic, etc.)
2. **Network Mode**: Connects to internal Ollama servers within corporate network
3. **Local Mode**: Runs local Ollama instances for air-gapped environments

### Runtime Switching Mechanism

Introduce MCP tool `ai_mode_switching` for dynamic mode changes during runtime:

```json
{
  "tool": "ai_mode_switching",
  "parameters": {
    "mode": "online|network|local",
    "endpoint": "optional_endpoint_url",
    "model": "optional_model_name"
  }
}
```

### Security Integration

- All modes must comply with security.instructions.md requirements
- Network and Local modes require additional validation for internal endpoints
- No secrets or credentials exposed in configuration files
- Input validation for all mode parameters

### Governance Compliance

- Follows GL-008 governance policies for agent permissions
- @CopilotExpert implements configuration changes
- @Security reviews security implications
- @DevOps handles infrastructure setup

## Consequences

### Positive
- Flexible deployment options for different customer environments
- Maintains data sovereignty for sensitive operations
- Reduces external API dependencies where possible
- Enables offline operation capabilities

### Negative
- Increased complexity in AI integration layer
- Performance differences between modes
- Additional testing requirements for mode switching
- Potential configuration errors if not properly managed

### Risks
- Security vulnerabilities in internal Ollama setups
- Performance degradation in Local mode
- Configuration drift between environments

## Implementation

### Configuration Options

```json
// .vscode/mcp.json
{
  "ai_modes": {
    "online": {
      "provider": "openai",
      "api_key_env": "OPENAI_API_KEY"
    },
    "network": {
      "endpoint": "http://internal-ollama.company.com:11434",
      "models": ["llama2", "codellama"]
    },
    "local": {
      "endpoint": "http://localhost:11434",
      "models": ["llama2"]
    }
  }
}
```

### Agent Configuration

Agents can specify preferred modes in their definitions:

```markdown
# Agent Definition
preferred_ai_mode: online
fallback_modes: [network, local]
```

## Alternatives Considered

1. **Static Configuration**: Single mode per deployment - rejected due to lack of flexibility
2. **Environment Variables Only**: No runtime switching - rejected for operational complexity
3. **Plugin Architecture**: Overkill for current requirements - deferred to future phases

## Compliance

- **Security**: Follows security.instructions.md for credential handling
- **Governance**: @CopilotExpert implements, @SARAH approves
- **Testing**: Comprehensive mode switching tests required

## Next Steps

1. Implement MCP tool `ai_mode_switching`
2. Update agent definitions with mode preferences
3. Create monitoring and health checks for each mode
4. Develop automated tests for mode switching
5. Document operational procedures

---

**Agents**: @CopilotExpert | **Owner**: @CopilotExpert</content>
<parameter name="filePath">/Users/holger/Documents/Projekte/B2X/.ai/decisions/ADR-040-ai-mode-switching-strategy.md