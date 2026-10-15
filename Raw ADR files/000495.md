# ADR-004: Environment Variable Standardization

**Author: JP + 2025-06-16**  
**Status**: Accepted  
**Date**: 2025-06-16  

## Context

During the implementation of visual content agents and system integration, we discovered inconsistent environment variable naming and usage patterns across the codebase. This inconsistency creates:

1. **Configuration Confusion**: Different agents using different variable names for the same purpose
2. **Maintenance Overhead**: Multiple fallback patterns and redundant variable checks
3. **Deployment Complexity**: Unclear which variables need to be set in production
4. **Developer Experience Issues**: Inconsistent patterns across different modules

### Current Inconsistencies Identified

**Before Standardization**:
```python
# marketing_orchestrator.py
GEMINI_MODEL = os.getenv("DEFAULT_MODEL_NAME", "gemini-2.0-flash-exp")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

# visual_content_agent.py  
GEMINI_MODEL = os.getenv("DEFAULT_MODEL_NAME", "gemini-2.0-flash-exp")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

# business_analysis_agent.py
self.gemini_api_key = os.getenv("GEMINI_API_KEY")

# main.py
if not os.getenv("GEMINI_API_KEY"):
```

## Decision

We will standardize all environment variables following these principles:

### 1. **Standardized Variable Names**

| Purpose | Variable Name | Default Value | Description |
|---------|---------------|---------------|-------------|
| Gemini Model | `GEMINI_MODEL` | `"gemini-2.5-flash"` | AI model version |
| Gemini API Key | `GEMINI_API_KEY` | None (required) | Authentication key |
| Database Path | `DATABASE_PATH` | `"data/video_venture_launch.db"` | SQLite database location |
| API Port | `API_PORT` | `8080` | Backend API server port |
| Frontend URL | `FRONTEND_URL` | `"http://localhost:5173"` | Frontend application URL |
| Log Level | `LOG_LEVEL` | `"INFO"` | Application logging level |
| Environment | `ENVIRONMENT` | `"development"` | Runtime environment |

### 2. **Configuration Pattern**

**Standardized Pattern**:
```python
# Configuration - Using standardized environment variables
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Validation
if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY not configured - using mock responses")
```

### 3. **Environment File Structure**

**backend/.env**:
```bash
# AI/ML Configuration
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL="gemini-2.5-flash"

# Database Configuration  
DATABASE_PATH="data/video_venture_launch.db"

# Server Configuration
API_PORT=8080
FRONTEND_URL="http://localhost:5173"

# Application Configuration
LOG_LEVEL="INFO"
ENVIRONMENT="development"

# Optional: Google Cloud Configuration (for production)
# GOOGLE_CLOUD_PROJECT=your_project_id
# GOOGLE_CLOUD_LOCATION=us-central1
```

### 4. **Validation and Error Handling**

```python
# Required variables validation
REQUIRED_ENV_VARS = ["GEMINI_API_KEY"]
missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_vars:
    logger.error(f"Missing required environment variables: {missing_vars}")
    # Graceful degradation to mock mode for development
```

## Consequences

### Positive

1. **Consistency**: All modules use the same variable names and patterns
2. **Maintainability**: Single source of truth for configuration
3. **Documentation**: Clear documentation of all required variables
4. **Developer Experience**: Predictable configuration across all components
5. **Production Readiness**: Clear separation of development vs production config
6. **Error Prevention**: Standardized validation prevents configuration errors

### Negative

1. **Migration Effort**: Existing code needs to be updated
2. **Breaking Changes**: Any external scripts using old variable names will break
3. **Documentation Updates**: All documentation needs to reflect new standards

## Implementation Plan

### Phase 1: Core Agent Standardization ✅ COMPLETED
- [x] Update `marketing_orchestrator.py` to use `GEMINI_MODEL`
- [x] Update `visual_content_agent.py` to use `GEMINI_MODEL`  
- [x] Remove fallback to `GOOGLE_API_KEY` and `DEFAULT_MODEL_NAME`
- [x] Ensure consistent error handling patterns

### Phase 2: System-wide Standardization
- [ ] Update `business_analysis_agent.py` configuration
- [ ] Update API main.py configuration validation
- [ ] Update test files to use standardized variables
- [ ] Create environment variable validation utility

### Phase 3: Documentation and Tooling
- [ ] Update README.md with environment variable documentation
- [ ] Create `.env.example` template file
- [ ] Update deployment documentation
- [ ] Add environment validation to Makefile targets

## Validation

### Testing
```bash
# Test with standardized environment variables
make test-comprehensive

# Test configuration validation
make validate-env

# Test mock mode (no API key)
unset GEMINI_API_KEY && make test-quick
```

### Monitoring
- All agents log their configuration on startup
- Missing variables trigger clear warning messages
- Mock mode is clearly indicated in logs

## References

- [12-Factor App Configuration](https://12factor.net/config)
- [Google ADK Environment Best Practices](https://google.github.io/adk-docs/)
- [Python Environment Variable Best Practices](https://docs.python.org/3/library/os.html#os.getenv)

## Related ADRs

- ADR-003: Backend ADK Implementation
- ADR-002: Database Design and Schema
- ADR-001: Technology Stack Selection

---

**Implementation Status**: ✅ Phase 1 Complete - Core agents standardized  
**Next Action**: Phase 2 - System-wide standardization  
**Review Date**: 2025-07-16 (1 month review cycle) 