# ADR-0001: LLM Gateway Provider-Agnostisch Design

## Status
✅ **ACCEPTED** - 2025-09-09

## Context
Das AI Code Agent System muss verschiedene Large Language Model (LLM) Provider unterstützen (OpenAI, Claude, Azure OpenAI, lokales Ollama) um:
- Vendor Lock-in zu vermeiden
- Kosten zu optimieren (lokale Models vs. Cloud APIs)
- Ausfallsicherheit zu gewährleisten
- Compliance-Anforderungen zu erfüllen (lokale Verarbeitung)

## Decision
Wir implementieren eine **Provider-Agnostische LLM Gateway Architektur** mit folgenden Komponenten:

### **LLM Service Interface**
```typescript
interface LLMProvider {
  generatePatch(prompt: string, options: GenerationOptions): Promise<PatchResult>
  isAvailable(): Promise<boolean>
  getCapabilities(): ProviderCapabilities
}
```

### **Provider Priority & Fallback**
1. **Ollama (Local)** → Privacy-first, kostenlos, offline
2. **Claude (Anthropic)** → Beste Code-Qualität, moderate Kosten  
3. **OpenAI GPT-4** → Bewährt, höhere Kosten
4. **Mock Provider** → Development/Testing fallback

### **Provider Selection Logic**
```typescript
class LLMService {
  async selectProvider(): Promise<LLMProvider> {
    for (const provider of this.providers) {
      if (await provider.isAvailable()) {
        return provider;
      }
    }
    return this.mockProvider; // Fallback
  }
}
```

## Consequences

### **✅ Positive**
- **Flexibility**: Einfacher Provider-Wechsel ohne Code-Änderungen
- **Resilience**: Automatischer Fallback bei Provider-Ausfällen
- **Cost Control**: Optimierung zwischen lokalen und Cloud-basierten Models
- **Compliance**: Lokale Verarbeitung möglich (Ollama)
- **Testing**: Mock Provider für Unit Tests und Development

### **⚠️ Negative**
- **Complexity**: Zusätzliche Abstraktionsschicht
- **Provider-Specific Features**: Lowest-common-denominator Approach
- **Configuration**: Mehr Environment Variables und Setup
- **Monitoring**: Separate Metrics pro Provider erforderlich

### **🔧 Mitigation Strategies**
- Gemeinsame Provider-Konfiguration über Environment Variables
- Einheitliche Logging und Metrics Collection
- Provider-spezifische Optimierungen über Options Parameter
- Circuit Breaker Pattern für robuste Fallback-Logik

## Implementation Notes

### **Environment Configuration**
```bash
# Provider Priority (comma-separated)
LLM_PROVIDERS=ollama,claude,openai,mock

# Provider-specific configs
OLLAMA_URL=http://localhost:11434
CLAUDE_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Fallback behavior
LLM_RETRY_ATTEMPTS=3
LLM_TIMEOUT_SECONDS=30
```

### **Monitoring Requirements**
- `llm_provider_requests_total{provider, status}`
- `llm_provider_response_duration_seconds{provider}`  
- `llm_provider_availability{provider}`
- `llm_provider_errors_total{provider, error_type}`

## Related ADRs
- ADR-0002: RAG vs. Context-only Approach
- ADR-0003: Local vs. Cloud LLM Default Strategy

## References
- [LLM Service Implementation](../services/llm-patch/src/index.ts)
- [Provider Configuration](../services/llm-patch/src/providers/)
- [Monitoring Setup](../ops/monitoring/prometheus.yml)
