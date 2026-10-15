# ADR-0002: LLM HTTP Adapter Configured by JSON with LM Studio Defaults

**Date:** 2026-01-09  
**Status:** Accepted  
**Deciders:** blecx, GitHub Copilot  
**Related:** [MVP Spec](../spec/mvp-iso21500-agent.md), [ADR-0001](0001-docs-repo-mounted-git.md), [Chat Transcript](../chat/2026-01-09-blecx-copilot-transcript.md)

## Context

The AI-Agent-Framework uses Large Language Models (LLMs) to generate project management documentation. We need a strategy for integrating with LLMs that:

1. **Supports multiple LLM providers** (LM Studio, OpenAI, Azure, Ollama, etc.)
2. **Provides sensible defaults** for local development (LM Studio)
3. **Allows easy configuration** without code changes
4. **Enables override** for different environments
5. **Gracefully handles unavailability** when LLM is not accessible
6. **Avoids vendor lock-in** to specific LLM providers
7. **Maintains security** by keeping API keys out of code

### Problem Statement

How should we integrate with LLM services in a flexible, configurable, and secure manner?

**Options Considered:**

**Option 1: Hardcode OpenAI API integration**
- ✅ Simple to implement
- ❌ Vendor lock-in to OpenAI
- ❌ Requires paid API key
- ❌ No local development option
- ❌ Configuration via environment variables only

**Option 2: Support multiple LLM SDKs (OpenAI, Anthropic, etc.)**
- ✅ Native support for each provider
- ❌ Complex code with multiple dependencies
- ❌ Maintenance burden for each SDK
- ❌ Still doesn't support local models easily

**Option 3: OpenAI-compatible HTTP adapter with JSON configuration**
- ✅ Single HTTP client for all providers
- ✅ Works with any OpenAI-compatible API
- ✅ Supports local models (LM Studio, Ollama, LocalAI)
- ✅ Configuration via JSON file
- ✅ Easy to override for different environments
- ✅ No vendor lock-in
- ✅ Minimal dependencies
- ❌ Limited to OpenAI-compatible APIs only

**Option 4: Plugin system with provider-specific adapters**
- ✅ Maximum flexibility
- ❌ Over-engineered for MVP
- ❌ Complex to implement and maintain
- ❌ Adds unnecessary abstraction

## Decision

We will **use an OpenAI-compatible HTTP adapter configured via `/config/llm.json`** with defaults for LM Studio.

### Implementation Details

**Configuration File Location:**
```
configs/llm.json          # User configuration (not in git)
configs/llm.default.json  # Default configuration (in git)
```

**Configuration Schema:**
```json
{
  "provider": "lmstudio",                              // Provider identifier
  "base_url": "http://host.docker.internal:1234/v1",  // API endpoint
  "api_key": "lm-studio",                              // API key/token
  "model": "local-model",                              // Model name
  "temperature": 0.7,                                  // Sampling temperature
  "max_tokens": 4096,                                  // Max response length
  "timeout": 120                                       // Request timeout (sec)
}
```

**Loading Priority:**
1. Check for `configs/llm.json` (user override)
2. Fall back to `configs/llm.default.json` (defaults)
3. Allow environment variable overrides for sensitive values

**Docker Volume Mount:**
```yaml
# docker-compose.yml
services:
  api:
    volumes:
      - ./configs:/config:ro  # Mount config as read-only
```

**Default Provider: LM Studio**

Why LM Studio?
- Free and open-source
- Runs completely local (no external API calls)
- Compatible with OpenAI API
- Easy to use for non-technical users
- Supports many open-source models
- Works on Mac, Windows, Linux

**Graceful Fallback:**

When LLM is unavailable:
1. Attempt connection with timeout
2. If connection fails, log warning
3. Fall back to template-based generation
4. System remains fully functional

**Supported Providers:**

Any service with OpenAI-compatible API:
- **LM Studio** (default) - Local models
- **OpenAI API** - GPT-3.5, GPT-4, etc.
- **Azure OpenAI** - Enterprise OpenAI
- **Ollama** - Local models with OpenAI compatibility
- **LocalAI** - Self-hosted OpenAI alternative
- **Text Generation WebUI** - With OpenAI extension
- **vLLM** - High-performance inference server
- **Any custom server** implementing OpenAI's API

## Consequences

### Positive

1. **Flexibility:**
   - Switch between providers without code changes
   - Configure per environment (dev, staging, prod)
   - Easy to test with different models

2. **Local Development:**
   - LM Studio runs locally with no API costs
   - No internet connection required
   - Full privacy (data stays local)
   - Faster iteration during development

3. **Security:**
   - API keys in config files, not in code
   - Config files excluded from git via `.gitignore`
   - Can use environment variables for sensitive values
   - Read-only mount in Docker

4. **No Vendor Lock-in:**
   - Not tied to specific LLM provider
   - Can migrate between providers easily
   - Supports open-source and proprietary models

5. **Simple Implementation:**
   - Single HTTP client (minimal dependencies)
   - Standard JSON configuration
   - No complex SDK integration
   - Easy to debug and troubleshoot

6. **Graceful Degradation:**
   - System works without LLM (template fallback)
   - No hard dependency on external services
   - Users can start without LLM setup
   - Progressive enhancement (add LLM later)

7. **Cost Control:**
   - Use free local models for development
   - Use paid APIs only when needed
   - Configurable per project or environment

### Negative

1. **OpenAI API Limitation:**
   - Only works with OpenAI-compatible APIs
   - Won't work with Anthropic Claude, Google Gemini, etc. (unless via proxy)
   - Mitigation: Most modern LLM services offer OpenAI compatibility

2. **Configuration Management:**
   - Users must create/edit JSON file
   - Mitigation: Provide clear documentation and sensible defaults
   - Future: Add web UI for configuration

3. **LM Studio Learning Curve:**
   - Users need to install and run LM Studio
   - Mitigation: System works without LLM (fallback mode)
   - Detailed setup guide in documentation

4. **No Streaming UI (MVP):**
   - HTTP adapter supports streaming, but UI doesn't display it yet
   - Mitigation: Acceptable for MVP, can add in future

### Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| LM Studio not installed | Medium | Medium | Graceful fallback to templates |
| Wrong API endpoint config | Low | Medium | Clear error messages, health check |
| API key leaked | High | Low | Config excluded from git, documentation warns users |
| LLM provider changes API | Medium | Low | Abstract via adapter, version API requests |
| Token limits exceeded | Medium | Medium | Configurable max_tokens, chunking for long inputs |

## Compliance Notes

### EU AI Act
- **Transparency:** LLM provider and model configurable and logged in audit trail
- **Human Oversight:** Propose/apply workflow ensures human review of AI-generated content
- **Data Privacy:** Local LLM option (LM Studio) keeps data on-premises

### ISO 27001
- **Access Control:** API keys stored in protected config files
- **Cryptographic Controls:** HTTPS recommended for external API calls
- **Logging:** LLM requests/responses logged (hashes by default)

### GDPR (if processing personal data)
- **Data Minimization:** Only send necessary context to LLM
- **Purpose Limitation:** LLM used only for document generation
- **Data Localization:** LM Studio option keeps data local (EU deployment compliant)

## Implementation Notes

**LLM Service** (`apps/api/services/llm_service.py`):
```python
import httpx
import json
from pathlib import Path

class LLMService:
    def __init__(self, config_path: str = "/config/llm.json"):
        self.config = self._load_config(config_path)
        self.client = httpx.AsyncClient(timeout=self.config.get("timeout", 120))
    
    def _load_config(self, config_path: str) -> dict:
        """Load config with fallback to defaults"""
        config_file = Path(config_path)
        if not config_file.exists():
            config_file = Path("/config/llm.default.json")
        
        with open(config_file) as f:
            config = json.load(f)
        
        # Allow environment variable overrides
        if api_key := os.getenv("LLM_API_KEY"):
            config["api_key"] = api_key
        if base_url := os.getenv("LLM_BASE_URL"):
            config["base_url"] = base_url
        
        return config
    
    async def generate_completion(self, prompt: str) -> str:
        """Generate completion with fallback"""
        try:
            response = await self.client.post(
                f"{self.config['base_url']}/chat/completions",
                json={
                    "model": self.config["model"],
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": self.config.get("temperature", 0.7),
                    "max_tokens": self.config.get("max_tokens", 4096),
                },
                headers={"Authorization": f"Bearer {self.config['api_key']}"}
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.warning(f"LLM unavailable: {e}")
            return None  # Caller will use template fallback
```

**Default Configuration** (`configs/llm.default.json`):
```json
{
  "provider": "lmstudio",
  "base_url": "http://host.docker.internal:1234/v1",
  "api_key": "lm-studio",
  "model": "local-model",
  "temperature": 0.7,
  "max_tokens": 4096,
  "timeout": 120
}
```

**Environment Variable Overrides:**
```bash
# Override API key
export LLM_API_KEY="sk-your-openai-key"

# Override base URL
export LLM_BASE_URL="https://api.openai.com/v1"

# Start system
docker compose up
```

**Example Configurations:**

**LM Studio (Default):**
```json
{
  "provider": "lmstudio",
  "base_url": "http://host.docker.internal:1234/v1",
  "api_key": "lm-studio",
  "model": "local-model"
}
```

**OpenAI:**
```json
{
  "provider": "openai",
  "base_url": "https://api.openai.com/v1",
  "api_key": "sk-...",
  "model": "gpt-4"
}
```

**Azure OpenAI:**
```json
{
  "provider": "azure",
  "base_url": "https://your-resource.openai.azure.com/openai/deployments/your-deployment",
  "api_key": "your-azure-key",
  "model": "gpt-4"
}
```

**Ollama:**
```json
{
  "provider": "ollama",
  "base_url": "http://localhost:11434/v1",
  "api_key": "ollama",
  "model": "llama2"
}
```

## Alternatives Considered

We considered but rejected:

1. **Hardcoded OpenAI integration:**
   - Rejected due to vendor lock-in and cost

2. **Multiple LLM SDKs:**
   - Rejected due to complexity and maintenance burden

3. **Environment variables only:**
   - Rejected as less flexible than JSON config (many parameters)

4. **Database-stored configuration:**
   - Rejected as over-engineered for MVP

## Documentation Requirements

Users must be guided on:
1. How to install and run LM Studio (with screenshots)
2. How to create/edit `configs/llm.json`
3. How to use environment variables for overrides
4. How to test LLM connectivity
5. What to do when LLM is unavailable (fallback mode)
6. Security best practices (don't commit API keys)

See: [README.md](../../README.md#llm-configuration) and [QUICKSTART.md](../../QUICKSTART.md#3-optional-configure-llm)

## References

- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [LM Studio](https://lmstudio.ai/)
- [MVP Specification](../spec/mvp-iso21500-agent.md)
- [ADR-0001: Separate Docs Repository](0001-docs-repo-mounted-git.md)
- [Chat Transcript](../chat/2026-01-09-blecx-copilot-transcript.md) - Original discussion

## Review History

| Date | Reviewer | Decision |
|------|----------|----------|
| 2026-01-09 | blecx | Approved |
| 2026-01-09 | GitHub Copilot | Documented |

---

**Previous:** [ADR-0001: Separate Docs Repository](0001-docs-repo-mounted-git.md)  
**Next:** [ADR-0003: Propose/Apply Workflow](0003-propose-apply-before-commit.md)
