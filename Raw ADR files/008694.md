# ADR-002: Python Entry Points and Package Structure

## Status
Accepted

## Date
2025-08-08

## Context

During initial development, we implemented an ad-hoc entry point script (`run_bot.py`) outside the `src/` directory to handle Python import path issues. This approach created several problems:

1. **Inconsistent project structure**: Main code in `src/`, entry point outside
2. **Import path manipulation**: Required `sys.path.insert()` hacks to make imports work
3. **Non-standard packaging**: Didn't follow Python packaging best practices
4. **Deployment complexity**: Entry points scattered across project structure

### Technical Issues Encountered
- Python `ImportError: attempted relative import with no known parent package` when running modules directly
- System environment variables overriding `.env` file values
- Async entry point compatibility issues with setuptools console scripts

### Research Context
Python packaging standards recommend:
- All source code contained within organized package directories
- Entry points defined in `pyproject.toml` using `[project.scripts]`
- UV package manager best practices for dependency management
- Proper separation of synchronous and asynchronous entry points

## Decision

We will restructure the project to use proper Python entry points following modern packaging standards:

### Entry Point Configuration
```toml
[project.scripts]
discord-bot = "src.discord_bot.main:cli_main"
publishing-api = "src.publishing_api.main:main"
```

### Code Structure Changes
1. **Discord Bot Entry Point**: Add synchronous `cli_main()` wrapper for async `main()` function
2. **Publishing API Entry Point**: Implement proper `main()` function for uvicorn server startup
3. **Import System**: Enhanced with fallback strategy for both absolute and relative imports
4. **Environment Loading**: Prioritize `.env` file over system environment variables using `load_dotenv(override=True)`

### Repository Cleanup
- Remove ad-hoc entry point scripts
- Enhance `.gitignore` with proper Python patterns
- Remove tracked cache files and logs from version control
- Follow UV package manager best practices for lockfile management

## Consequences

### Positive
- **Standard Python packaging**: Follows Python community best practices
- **Simplified commands**: `uv run discord-bot` and `uv run publishing-api`
- **No import hacks**: Eliminates `sys.path` manipulation
- **Deployment ready**: Can be installed as proper Python package
- **Better developer experience**: Consistent, memorable commands
- **Tool compatibility**: Works with UV, pip, and Python packaging ecosystem

### Negative
- **Migration effort**: Required updating documentation and workflows
- **Learning curve**: Developers need to understand entry point system
- **Debugging complexity**: Entry point issues can be harder to debug than direct script execution

### Neutral
- **File organization**: Source code remains in same structure, just better organized
- **Development workflow**: Similar commands with cleaner implementation

## Implementation Details

### Entry Point Functions
```python
# Discord Bot - src/discord_bot/main.py
def cli_main():
    """Synchronous entry point for command line usage."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        sys.exit(1)

# Publishing API - src/publishing_api/main.py  
def main():
    """Entry point for command line usage."""
    import uvicorn
    uvicorn.run("src.publishing_api.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
```

### Import Strategy
```python
# Hybrid import approach for maximum compatibility
try:
    # Try absolute import first (when run as module)
    from src.discord_bot.api_client import PublishingAPIClient
    from src.discord_bot.config import BotConfig
    from src.discord_bot.modals import BookmarkModal, MediaModal, NoteModal, ResponseModal
except ImportError:
    # Fall back to relative imports (when run from package)
    from .api_client import PublishingAPIClient
    from .config import BotConfig
    from .modals import BookmarkModal, MediaModal, NoteModal, ResponseModal
```

### Environment Variable Priority
```python
# Configuration files now prioritize .env over system environment
from dotenv import load_dotenv
load_dotenv(override=True)  # .env file takes precedence
```

## Usage Examples

### Development
```bash
# Start Discord bot
uv run discord-bot

# Start Publishing API
uv run publishing-api

# Run tests
uv run pytest

# Verify credentials
uv run python scripts/verify-credentials.py
```

### Production (after installation)
```bash
# Install package
uv pip install -e .

# Run from anywhere
discord-bot
publishing-api
```

## Alternative Approaches Considered

### Option 1: Keep run_bot.py (Rejected)
- **Pros**: No code changes required
- **Cons**: Non-standard, import hacks, deployment complexity

### Option 2: Move entry points into src/ (Rejected)
- **Pros**: Code organization improvement
- **Cons**: Still requires import path manipulation, non-standard packaging

### Option 3: Use click CLI framework (Deferred)
- **Pros**: Rich CLI features, argument parsing
- **Cons**: Additional dependency, over-engineered for current needs

## Monitoring and Success Criteria

### Success Metrics
- [x] Entry points work correctly with `uv run` commands
- [x] No import errors during bot startup
- [x] Environment variables load properly from `.env` file
- [x] Repository structure follows Python packaging standards
- [x] Documentation updated to reflect new usage patterns

### Validation Tests
- [x] `uv run discord-bot` starts successfully and connects to Discord
- [x] `uv run publishing-api` starts uvicorn server without errors
- [x] GitHub authentication works with `.env` file credentials
- [x] Import system handles both absolute and relative import scenarios
- [x] Repository contains only appropriate tracked files

## References

- [Python Packaging User Guide](https://packaging.python.org/en/latest/)
- [UV Package Manager Documentation](https://docs.astral.sh/uv/)
- [PEP 621 - Storing project metadata in pyproject.toml](https://peps.python.org/pep-0621/)
- [setuptools Entry Points Documentation](https://setuptools.pypa.io/en/latest/userguide/entry_point.html)

## Related Documents

- [ADR-001: Architecture Decision](adr-001-architecture-decision.md) - Original architecture decisions
- [Technical Specification](../../specs/technical/discord-publish-bot-technical-spec.md) - Implementation details
- [Project Requirements](../../projects/active/discord-publish-bot.md) - Feature requirements and roadmap

---
**Author:** GitHub Copilot  
**Status:** Implemented  
**Implementation Date:** 2025-08-08  
**Next Review:** 2025-08-22
