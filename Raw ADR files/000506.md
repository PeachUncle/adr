# ADR-024: AI Development Commandments

**Status**: ✅ **MANDATORY**  
**Date**: 2025-06-28  
**Author**: JP + Claude Sonnet  
**Context**: Binding rules for all AI coding assistants working on this project  

## Context

The `.cursorrules` and other rule files are being ignored by AI coding assistants, leading to architectural regression and inconsistent practices. These commandments serve as **binding architectural guidance** that must be followed by all AI agents working on this codebase.

## The Ten Commandments of VVL Development

### **I. THOU SHALT USE MAKEFILES FOR ALL OPERATIONS**
```bash
# ✅ CORRECT - Always use Makefile targets
make launch-all
make test-quick  
make test-full-stack

# ❌ FORBIDDEN - Direct commands
npm start
python main.py
```

### **II. THOU SHALT NOT CREATE MOCKS, STUBS, OR PLACEHOLDERS**
```python
# ✅ CORRECT - Real implementation
async def generate_image(prompt: str) -> str:
    response = client.models.generate_images(model="imagen-3.0-generate-002", prompt=prompt)
    return response.generated_images[0].image.image_bytes

# ❌ FORBIDDEN - Mock/stub implementations  
def generate_image(prompt: str) -> str:
    return "https://via.placeholder.com/400x300"  # NO PLACEHOLDERS!
```

### **III. THOU SHALT USE GRACEFUL ERROR HANDLING WITH CONTEXT**
```python
# ✅ CORRECT - Graceful with business context
try:
    result = await real_api_call()
except APIError as e:
    logger.error(f"API failed: {e} - implementing fallback with real functionality")
    return create_real_fallback_with_context(business_context)

# ❌ FORBIDDEN - Silent failures or generic errors
try:
    result = await api_call()
except:
    pass  # NEVER DO THIS
```

### **IV. THOU SHALT IMPLEMENT COMPLETE, TESTED FEATURES**
```python
# ✅ CORRECT - Complete implementation with tests
class ImageAgent:
    async def generate_images(self, prompts: List[str]) -> List[Dict]:
        # Full implementation with validation, caching, error handling
        # Real API integration with fallbacks
        # Comprehensive logging and monitoring
        pass

# Tests in tests/test_image_agent.py with 90%+ coverage
```

### **V. THOU SHALT READ LOGS TO VALIDATE FUNCTIONALITY**
```bash
# ✅ MANDATORY - Always check logs after implementation
tail -f logs/backend-debug.log
tail -f logs/frontend-debug.log

# Validate that your implementation works in practice
make test-quick  # Must pass before committing
```

### **VI. THOU SHALT EMIT DETAILED DEBUG LOGGING**
```python
# ✅ CORRECT - Comprehensive debug logging
logger.info(f"🎨 IMAGE_GENERATION_START: campaign={campaign_id}, prompts={len(prompts)}")
logger.info(f"📦 API_RESPONSE: status=success, size={len(image_bytes)}KB")
logger.error(f"❌ GENERATION_FAILED: {error_context}", exc_info=True)

# ❌ INSUFFICIENT - Generic or missing logs
logger.info("Starting image generation")  # NOT DETAILED ENOUGH
```

### **VII. THOU SHALT MAINTAIN ARCHITECTURAL COHERENCE**
```yaml
# ✅ CORRECT - Follow established patterns
FastAPI + SQLite + ADK Agents → Content Generation → Frontend Display

# ❌ FORBIDDEN - Creating architectural silos
New async system + Different database + Custom agents  # BREAKS COHERENCE
```

### **VIII. THOU SHALT USE ENVIRONMENT VARIABLES, NOT HARDCODED VALUES**
```python
# ✅ CORRECT - Environment configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
IMAGE_MODEL = os.getenv('IMAGE_MODEL', 'imagen-3.0-generate-002')
APP_PORT = int(os.getenv('APP_PORT', '8080'))

# ❌ FORBIDDEN - Hardcoded values
api_key = "abc123..."  # NEVER HARDCODE SECRETS
model = "gemini-1.5-flash"  # USE ENV VARS
```

### **IX. THOU SHALT TARGET PRODUCTION-READY GOOGLE CLOUD DEPLOYMENT**
```python
# ✅ CORRECT - Cloud-ready architecture
from google.cloud import storage  # Ready for Cloud Run
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///local.db')  # Local + Cloud

# ❌ SHORT-SIGHTED - Local-only implementations
import sqlite3  # Hard path to local files only
```

### **X. THOU SHALT DOCUMENT FIRST, THEN IMPLEMENT MINIMAL CHANGES**
```markdown
# ✅ CORRECT - Document architectural decisions
## ADR-XXX: Image Generation Enhancement
### Context: Why this change is needed
### Decision: What approach we're taking  
### Implementation: Minimal changes to existing architecture

# ❌ FORBIDDEN - Code without documentation
# Just writing code without ADR documentation
```

---

## **Enforcement Mechanisms**

### **Pre-Commit Validation**
```bash
# These commands MUST pass before any commit
make test-quick           # Fast essential tests
make validate-logs        # Check debug log quality  
make architectural-check  # Verify coherence
```

### **Logging Requirements**
- **Backend**: `logs/backend-debug.log` must show detailed operation traces
- **Frontend**: `logs/frontend-debug.log` must show user interaction flows
- **Agents**: Each agent must log decision making and API interactions

### **Testing Standards**
- **90%+ test coverage** required for all new code
- **Integration tests** must validate real API interactions
- **E2E tests** must verify complete user workflows

### **Documentation Standards**
- **Every function/class** must have clear docstrings
- **Every architectural change** requires an ADR
- **Every API change** must update API documentation

---

## **Violation Consequences**

### **Level 1: Code Quality Issues**
- Missing tests → Implementation rejected
- Missing logs → Feature incomplete
- Hardcoded values → Security violation

### **Level 2: Architectural Violations**
- Creating silos → Major refactoring required
- Breaking patterns → Revert and redesign
- Ignoring ADRs → Implementation reset

### **Level 3: Production Readiness Failures**
- Mock/stub implementations → Complete rewrite
- Missing error handling → System instability
- Poor logging → Debugging impossible

---

## **Success Metrics**

### **Code Quality**
- ✅ 90%+ test coverage maintained
- ✅ All logs provide actionable debugging info
- ✅ Zero hardcoded production values

### **Architectural Integrity**
- ✅ All changes follow established patterns
- ✅ No orphaned or duplicate functionality
- ✅ Clear separation of concerns maintained

### **Production Readiness**
- ✅ Google Cloud deployment compatibility
- ✅ Real functionality, no placeholders
- ✅ Comprehensive error handling and recovery

---

## **Quick Reference Commands**

```bash
# Development Workflow
make launch-all              # Start full stack
make test-quick             # Essential validation
make view-all-logs          # Monitor operations

# Quality Assurance  
make test-full-stack        # Comprehensive testing
make validate-architecture  # Check coherence
make deployment-ready       # Production check

# Documentation
make update-docs           # Sync documentation
make validate-adrs         # Check ADR compliance
```

---

## **Remember: These Are Not Suggestions - They Are Requirements**

Every AI coding assistant working on this project **MUST** follow these commandments. Violations will result in implementation rejection and architectural cleanup requirements.

**The goal is an 87%+ mature, hackathon-ready solution, not experimental code.** 