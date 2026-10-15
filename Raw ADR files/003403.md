# ADR 001: Choice of Playwright over Selenium

**Status:** Accepted  
**Date:** 2025-12-30  
**Decision Makers:** SDET Lead, QA Team

## Context

The framework needed a reliable automation library for both UI and API testing. The primary candidates were:
- Selenium WebDriver
- Playwright
- Cypress

## Decision

We chose **Playwright** as the automation engine.

## Rationale

### Advantages of Playwright

1. **Unified API for UI and API Testing**
   - Single library handles browser automation AND API calls
   - No need for separate tools (RestSharp, HttpClient)
   - Consistent async/await patterns

2. **Modern Architecture**
   - Built-in auto-wait mechanisms (no explicit waits needed)
   - Network interception out-of-the-box
   - Native mobile viewport emulation

3. **Better Performance**
   - Faster than Selenium (direct browser protocol)
   - Parallel browser contexts (isolation without extra overhead)
   - Built-in trace viewer for debugging

4. **Developer Experience**
   - Official .NET support (not community-driven like Selenium)
   - Strong typing with C# 12 features
   - Excellent documentation

5. **Enterprise Features**
   - Video recording built-in
   - Screenshot capture without external libraries
   - Trace files for post-mortem analysis
   - Network HAR export

### Why Not Selenium?

- Requires separate API testing library (RestSharp/HttpClient)
- Manual wait management (WebDriverWait, ExpectedConditions)
- Slower execution speed
- Community-maintained .NET bindings (not official)
- No built-in video recording

### Why Not Cypress?

- JavaScript/TypeScript only (team expertise is C#)
- Limited API testing capabilities
- Cannot run outside browser context
- Not suitable for .NET ecosystems

## Consequences

### Positive
- Single technology stack for UI + API
- Reduced learning curve (one API to learn)
- Better CI/CD performance
- Native video/screenshot support

### Negative
- Smaller community compared to Selenium
- Team needs to learn Playwright-specific patterns
- Some legacy tools expect Selenium (not a concern here)

### Mitigation
- Comprehensive training materials
- Document Playwright best practices
- Leverage official Microsoft documentation

## Alternatives Considered

| Tool | Pros | Cons | Decision |
|------|------|------|----------|
| Selenium | Large community | Slow, fragmented ecosystem | ❌ Rejected |
| Cypress | Great DX | JS only, limited API | ❌ Rejected |
| Playwright | Modern, fast, .NET native | Smaller community | ✅ **Selected** |

## References
- [Playwright .NET Documentation](https://playwright.dev/dotnet/)
- [Selenium vs Playwright Comparison](https://playwright.dev/docs/why-playwright)
