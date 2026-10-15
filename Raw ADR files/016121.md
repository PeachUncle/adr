# ADR-0001: Client-Side Only Architecture

## Status

**Accepted**

**Date**: 2024-12-20

**Author(s)**: SAZ Viewer Team

## Context

**Problem Statement**: Users need to inspect Telerik Fiddler .saz files containing sensitive HTTP traffic data (cookies, authentication tokens, API requests/responses). Traditional solutions require either installing desktop software or uploading files to a server for processing.

**Background**: 
- .saz files often contain highly sensitive data including credentials, session tokens, and proprietary API interactions
- Users work on various platforms (macOS, Linux, Windows)
- Desktop Fiddler is Windows-only; Fiddler Everywhere requires installation
- Uploading sensitive traffic data to servers creates privacy and compliance risks
- Modern browsers have sufficient capabilities to parse and display complex data structures

**Forces at Play**:
- **Must-haves**: 
  - Zero data transmission to any server
  - Cross-platform compatibility
  - No installation required
- **Should-haves**: 
  - Fast performance for large files
  - Professional debugging experience
- **Constraints**: 
  - Browser sandbox limitations
  - No server-side processing available

## Decision Drivers

1. **Privacy & Security**: Absolute requirement that sensitive HTTP traffic data never leaves the user's machine
2. **Accessibility**: Enable users on any platform without installation requirements
3. **Trust**: Users must be confident their data is processed locally
4. **Simplicity**: Minimize deployment and maintenance complexity
5. **Cost**: Eliminate server infrastructure and associated costs

## Considered Options

### Option 1: Traditional Client-Server Architecture

**Description**: Build a web application with server-side .saz file parsing and processing

**Pros**:
- ✅ More powerful processing capabilities
- ✅ Can handle very large files more easily
- ✅ Easier to implement some features

**Cons**:
- ❌ Requires uploading sensitive data to servers
- ❌ Privacy and compliance concerns
- ❌ Requires server infrastructure and costs
- ❌ Adds latency for file uploads
- ❌ Users must trust the service provider

**Cost/Effort**: High ongoing costs for servers, monitoring, and compliance

---

### Option 2: Desktop Application

**Description**: Build native desktop applications for each platform

**Pros**:
- ✅ Full system access and capabilities
- ✅ Offline functionality guaranteed
- ✅ No privacy concerns

**Cons**:
- ❌ Requires installation and updates
- ❌ Need to maintain multiple platform versions
- ❌ Higher development and maintenance cost
- ❌ Distribution and signing complexity
- ❌ Reduces accessibility

**Cost/Effort**: Very high - requires platform-specific expertise and maintenance

---

### Option 3: Client-Side Web Application (Chosen)

**Description**: Build a single-page web application that runs entirely in the browser, using JavaScript to parse .saz files locally

**Pros**:
- ✅ Zero data transmission - complete privacy
- ✅ No installation required
- ✅ Cross-platform by default
- ✅ Easy distribution via static hosting
- ✅ No server costs
- ✅ Modern browser APIs sufficient for requirements
- ✅ Easy to audit and verify privacy claims

**Cons**:
- ❌ Limited by browser capabilities
- ❌ Performance constraints for very large files
- ❌ No server-side features (but none needed)

**Cost/Effort**: Low - single codebase, free hosting options (GitHub Pages)

## Decision

**Chosen Option**: Client-Side Web Application

**Rationale**: 

The client-side only architecture is the clear winner because:

1. **Privacy First**: This is non-negotiable for a tool handling sensitive HTTP traffic. Client-side processing provides absolute guarantee that data never leaves the user's machine.

2. **Trust Through Transparency**: Users can inspect the source code and verify no network requests are made with their data. This builds trust that can't be achieved with server-side processing.

3. **Universal Access**: A web application works on any device with a modern browser - no platform-specific development needed.

4. **Zero Infrastructure**: Static hosting on GitHub Pages means zero ongoing costs and maximum uptime.

5. **Modern Browser Capabilities**: Browser APIs like FileReader, JSZip, and Web Workers provide sufficient capability to deliver a professional experience.

**Implementation Plan**: 
1. Build React-based SPA with TypeScript
2. Use JSZip for client-side .saz extraction
3. Implement file parsing entirely in JavaScript
4. Host as static site on GitHub Pages
5. Clearly communicate privacy guarantee in UI

## Consequences

### Positive Consequences

- ➕ Complete privacy and security for user data
- ➕ Zero ongoing infrastructure costs
- ➕ Maximum accessibility across platforms
- ➕ Simple deployment and updates
- ➕ Easy to audit for security researchers
- ➕ No compliance overhead for data handling
- ➕ Instant availability - no uploads or waits

### Negative Consequences

- ➖ Limited to browser JavaScript performance
- ➖ Cannot implement server-side features (not needed currently)
- ➖ Memory constraints for extremely large files (>500MB)
- ➖ No persistent storage of user data (by design)

### Neutral Consequences

- 🔄 Need to educate users about how client-side processing works
- 🔄 All computation burden on user's device

### Risks and Mitigation

| Risk | Impact | Probability | Mitigation Strategy |
|------|--------|-------------|---------------------|
| Performance issues with large files | Medium | Medium | Implement async parsing, Web Workers, progress indicators |
| Browser compatibility issues | Low | Low | Use modern build tools, polyfills where needed; target modern browsers |
| Users distrust privacy claims | Medium | Low | Provide clear documentation, open source code, no network dependencies visible in DevTools |

## Follow-up Actions

- [x] Implement file parsing in pure JavaScript
- [x] Document privacy guarantees in README and UI
- [x] Set up GitHub Pages deployment
- [x] Add clear indicators that processing is local
- [ ] Consider Web Worker for parsing very large files

## References

- [Telerik Fiddler SAZ Format Documentation](https://docs.telerik.com/fiddler/knowledge-base/SAZ-Format)
- [JSZip Library Documentation](https://stuk.github.io/jszip/)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)

## Notes

This decision establishes a core principle for the entire application: user privacy through client-side processing. All future feature decisions should be evaluated against this principle.
