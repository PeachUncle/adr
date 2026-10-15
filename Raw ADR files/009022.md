# ADR-003: Semantic Kernel for AI Integration

**Status:** ✅ Accepted  
**Date:** October 2025  
**Context:** Phase 1 - AI/LLM Integration Planning

## Context

The system requires LLM integration for:

- Generating assessment questions based on curriculum
- Evaluating open-ended student responses
- Providing personalized feedback
- Adaptive difficulty adjustment recommendations

Options considered:

- Direct OpenAI API calls
- LangChain (Python ecosystem)
- Semantic Kernel (.NET native)
- Custom abstraction layer
- Azure AI Search with grounding

## Decision

Selected **Microsoft Semantic Kernel** as the primary framework for LLM integration and agent orchestration.

## Rationale

1. **.NET Native**: First-class C# support with async/await patterns
2. **Multi-Provider**: Supports Azure OpenAI, OpenAI, Ollama, and local models
3. **Plugin Architecture**: Extensible skill/function system for tool use
4. **Memory & Context**: Built-in semantic memory and context management
5. **Enterprise Ready**: Microsoft-supported with Azure integration
6. **Prompt Engineering**: Template system with variable substitution
7. **Agent Framework**: Supports agent-to-agent (A2A) communication patterns

## Consequences

### Positive

- Unified abstraction for multiple LLM providers
- Easy to swap between Azure OpenAI (production) and Ollama (development)
- Plugin system naturally maps to subject-specific agents (Math, Physics, etc.)
- Semantic memory helps maintain context across assessment sessions
- Strong typing and compile-time safety for agent configurations

### Negative

- Additional learning curve for Semantic Kernel API
- Dependency on Microsoft's framework evolution
- Overkill for simple prompt-response patterns (some agents use direct HTTP)
- Documentation still maturing for advanced scenarios

### Risks Mitigated

- Abstracted LLM calls behind ILLMService interface for easier migration
- Configured multiple providers for redundancy
- Implemented fallback to stub provider for testing without LLM access

## Implementation Details

**Agent Base Class** (src/AcademicAssessment.Agents/Shared/A2ABaseAgent.cs):

```csharp
public abstract class A2ABaseAgent
{
    protected readonly Kernel _kernel;
    protected readonly ILLMService _llmService;
    
    protected A2ABaseAgent(Kernel kernel, ILLMService llmService)
    {
        _kernel = kernel;
        _llmService = llmService;
    }
}
```

**Provider Configuration**:

- **Azure OpenAI** (Production): GPT-4o for complex reasoning
- **Ollama** (Development): llama3.2:3b for local testing
- **Stub Provider** (CI/CD): Mock responses for unit tests

## Alternative Considered: Direct OpenAI SDK

**Rejected because:**

- Would require custom abstraction for multi-provider support
- No built-in memory or context management
- Would need to implement agent communication patterns manually
- Less idiomatic for .NET ecosystem

## Related Decisions

- ADR-004: Ollama for Local LLM Execution
- ADR-010: Multi-Agent Architecture for Assessment Generation
- ADR-090: Question Generation Strategy

## References

- `src/AcademicAssessment.Agents/` - All agent implementations use Semantic Kernel
- `src/AcademicAssessment.Infrastructure/Services/LLMService.cs`
- Commit: `a75945f` - "feat: Implement A2A Protocol Foundation"
- docs/architecture/A2A_AGENT_INTEGRATION_PLAN.md
