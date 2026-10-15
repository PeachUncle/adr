# ADR-007: Base URL Strategy for GitHub Pages Deployment

**Status**: Accepted  
**Date**: 2025-12-01  
**Deciders**: Development Team  
**Related**: specs/007-link-fixes-and-organization-updates

## Context

The Physical AI & Humanoid Robotics textbook is deployed to GitHub Pages with a custom base URL (`/physical-ai-and-humanoid-robotics/`). This creates a challenge for generating correct navigation links, particularly in the backend RAG chatbot service which generates source references to documentation pages.

**Problem**: The backend `_source_to_nav_path` function was generating paths like `/docs/module1/week1-intro-physical-ai` without the GitHub Pages base URL prefix, resulting in broken links (404 errors) when users clicked source references in chatbot responses.

**Requirements**:
- Chatbot source links must navigate to correct documentation pages
- Solution must work reliably in production (GitHub Pages)
- Implementation should be maintainable and not introduce complexity
- Frontend and backend must use consistent URL patterns

## Decision

We will **hardcode the GitHub Pages base URL** (`/physical-ai-and-humanoid-robotics`) as a constant in the backend `_source_to_nav_path` function, matching the pattern used in the Docusaurus configuration.

**Implementation**:
```python
def _source_to_nav_path(self, source: str) -> str:
    """Convert a source file path to a navigation path for the chatbot."""
    import re
    
    # Base URL for GitHub Pages deployment
    base_url = "/physical-ai-and-humanoid-robotics"
    
    # Match patterns like module1/week1-intro-physical-ai.md
    match = re.search(r'(module\d+)/([^/]+)\.md', source)
    if match:
        module = match.group(1)
        page = match.group(2)
        return f"{base_url}/docs/{module}/{page}"
    
    # Match intro.md
    if 'intro.md' in source:
        return f"{base_url}/docs"
    
    return ""
```

## Alternatives Considered

### Alternative 1: Environment Variable Configuration

**Approach**: Store base URL in environment variable and read it in the backend service.

**Pros**:
- More flexible for different deployment environments
- Easier to change without code modifications
- Follows 12-factor app principles

**Cons**:
- Adds configuration complexity
- Requires environment variable management in deployment
- Base URL is unlikely to change (deployment-specific)
- Introduces potential for misconfiguration

**Rejected because**: The base URL is deployment-specific and stable. The added flexibility doesn't justify the configuration overhead.

### Alternative 2: Dynamic Detection from Request Headers

**Approach**: Extract base URL from incoming request headers (Host, X-Forwarded-Host, etc.).

**Pros**:
- Automatically adapts to deployment environment
- No hardcoded values
- Works across different domains

**Cons**:
- Unreliable for Server-Sent Events (SSE) streaming
- Complex header parsing logic
- Potential security issues with header manipulation
- Doesn't work for background/async operations

**Rejected because**: SSE streaming makes request context unavailable during response generation. Header-based detection is unreliable and adds security concerns.

### Alternative 3: Configuration File

**Approach**: Create a separate configuration file (JSON/YAML) for deployment settings.

**Pros**:
- Centralized configuration
- Easy to update without code changes
- Can include other deployment-specific settings

**Cons**:
- Overkill for a single configuration value
- Adds file I/O overhead
- Requires file management in deployment
- More complex than needed

**Rejected because**: Creating a configuration file for a single, stable value is unnecessary complexity.

### Alternative 4: Match Frontend Pattern (Docusaurus Config)

**Approach**: Hardcode base URL in backend, matching the Docusaurus `baseUrl` configuration pattern.

**Pros**:
- Consistent with frontend configuration approach
- Simple and reliable
- No runtime overhead
- Easy to understand and maintain
- Matches existing Docusaurus pattern

**Cons**:
- Requires code change if base URL changes
- Less flexible than environment variables

**Selected because**: This approach provides the best balance of simplicity, reliability, and consistency with the existing frontend configuration.

## Rationale

### Why Hardcoding is Appropriate Here

1. **Deployment Stability**: The GitHub Pages base URL is tied to the repository name and organization, which rarely changes
2. **Consistency**: Matches the Docusaurus `baseUrl` configuration pattern in `docusaurus.config.ts`
3. **Simplicity**: No additional configuration, environment variables, or file I/O required
4. **Reliability**: No runtime dependencies or potential for misconfiguration
5. **Performance**: No overhead from environment variable lookups or file reads

### When This Decision Should Be Revisited

- If the project moves to a different deployment platform (e.g., custom domain)
- If multiple deployment environments with different base URLs are needed
- If the repository is renamed or moved to a different organization
- If dynamic base URL detection becomes feasible (e.g., non-SSE architecture)

## Consequences

### Positive

- **Immediate Fix**: Broken chatbot source links are resolved
- **Simple Implementation**: Single constant addition, no configuration management
- **Consistent Pattern**: Matches frontend Docusaurus configuration approach
- **Reliable**: No runtime dependencies or potential for misconfiguration
- **Maintainable**: Clear, easy to understand code
- **Performance**: No overhead from configuration lookups

### Negative

- **Hardcoded Value**: Requires code change if base URL changes
- **Duplication**: Base URL is defined in both Docusaurus config and backend code
- **Less Flexible**: Cannot easily switch between deployment environments

### Mitigation Strategies

1. **Documentation**: Add clear comments in code indicating where base URL is defined
2. **Deployment Guide**: Document base URL configuration in deployment documentation
3. **Code Comments**: Add comment explaining why hardcoding is appropriate
4. **Future Refactoring**: If multiple environments are needed, refactor to environment variable

## Implementation

### Files Modified

- `backend/src/services/agent_service.py`: Added `base_url` constant in `_source_to_nav_path` function

### Code Changes

```python
# Before
return f"/docs/{module}/{page}"

# After
base_url = "/physical-ai-and-humanoid-robotics"
return f"{base_url}/docs/{module}/{page}"
```

### Testing

- Manual testing: Verify chatbot source links navigate to correct pages
- Diagnostics: All modified files pass linting and type checking
- Integration: Confirm links work in production GitHub Pages deployment

## Related Decisions

- **ADR-005**: Website Redesign Architecture (established GitHub Pages deployment)
- **Docusaurus Config**: `baseUrl: '/physical-ai-and-humanoid-robotics/'` in `docusaurus.config.ts`

## References

- GitHub Pages Documentation: https://docs.github.com/en/pages
- Docusaurus Deployment Guide: https://docusaurus.io/docs/deployment
- 12-Factor App Config: https://12factor.net/config
