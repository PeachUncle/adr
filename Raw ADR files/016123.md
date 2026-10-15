# ADR-0003: JSZip for SAZ File Parsing

## Status

**Accepted**

**Date**: 2024-12-20

**Author(s)**: SAZ Viewer Team

## Context

**Problem Statement**: Need to parse Telerik Fiddler .saz files (which are ZIP archives) entirely in the browser to extract HTTP session data while maintaining our client-side only architecture.

**Background**:
- .saz files are standard ZIP archives with a specific folder structure
- Contains a `raw/` folder with numbered files for each HTTP session
- Files contain raw HTTP request/response data
- Files can range from a few KB to hundreds of MB
- Must work entirely in browser JavaScript (no native code)
- Need reliable, well-maintained library

**Forces at Play**:
- **Must-haves**: 
  - Pure JavaScript implementation
  - Reliable ZIP extraction
  - Works in modern browsers
- **Should-haves**: 
  - Good performance for large files
  - Support for async operations
  - Small bundle size
- **Constraints**: 
  - Must run in browser environment
  - No native dependencies
  - No server-side processing

## Decision Drivers

1. **Browser Compatibility**: Must work in all modern browsers without polyfills
2. **Reliability**: Well-tested, mature library with active maintenance
3. **Performance**: Handle files up to 100MB+ without blocking UI
4. **API Design**: Simple, intuitive API for reading ZIP contents
5. **Bundle Size**: Reasonable impact on application bundle
6. **License**: Permissive license compatible with our MIT license

## Considered Options

### Option 1: zip.js

**Description**: JavaScript library for working with ZIP files using Web Workers

**Pros**:
- ✅ Excellent performance with Web Workers
- ✅ Supports very large files via streaming
- ✅ Modern API with Promises
- ✅ Active maintenance

**Cons**:
- ❌ More complex API
- ❌ Larger bundle size (~50KB)
- ❌ Web Worker setup adds complexity
- ❌ Overkill for our use case

**Cost/Effort**: Higher implementation complexity

---

### Option 2: JSZip (Chosen)

**Description**: Widely-used JavaScript library for creating, reading, and editing ZIP files

**Pros**:
- ✅ Simple, intuitive API
- ✅ Excellent documentation
- ✅ Very mature (10+ years)
- ✅ Large community and ecosystem
- ✅ Actively maintained
- ✅ MIT licensed
- ✅ Promise-based async operations
- ✅ ~30KB minified+gzipped
- ✅ Proven in production across thousands of apps

**Cons**:
- ❌ Loads entire file into memory (acceptable for our use case)
- ❌ Not optimized for extremely large files (>200MB)

**Cost/Effort**: Low - straightforward integration

---

### Option 3: Custom ZIP Parser

**Description**: Build our own minimal ZIP parser for .saz files specifically

**Pros**:
- ✅ Smallest possible bundle size
- ✅ Optimized for our exact needs
- ✅ No external dependencies

**Cons**:
- ❌ High development and testing effort
- ❌ ZIP format is complex and error-prone
- ❌ Need to handle edge cases and compression
- ❌ Ongoing maintenance burden
- ❌ Likely to have bugs vs. mature library
- ❌ No community support

**Cost/Effort**: Very high - not justified for functionality available in libraries

---

### Option 4: fflate

**Description**: Fast compression/decompression library with ZIP support

**Pros**:
- ✅ Very fast performance
- ✅ Small bundle size
- ✅ Modern, actively developed
- ✅ Supports streams

**Cons**:
- ❌ More complex API than JSZip
- ❌ Less mature (newer library)
- ❌ Smaller community
- ❌ Less documentation and examples

**Cost/Effort**: Medium - newer library, less proven

## Decision

**Chosen Option**: JSZip

**Rationale**: 

JSZip is the clear choice for several compelling reasons:

1. **Proven Reliability**: With over 10 years in production and millions of downloads, JSZip is battle-tested. It handles edge cases in ZIP format that we would likely miss in a custom implementation.

2. **Perfect API Fit**: The API is intuitive and matches our needs exactly:
   ```typescript
   const zip = await JSZip.loadAsync(file);
   const rawFolder = zip.folder('raw');
   const files = Object.keys(rawFolder.files);
   const content = await rawFolder.file('1_c.txt').async('text');
   ```

3. **Async Operations**: Promise-based API works perfectly with React's async patterns. We can show loading states and keep UI responsive.

4. **Memory Model Works for Our Use Case**: While JSZip loads the entire file into memory, our target files are typically 10-50MB. The .saz files that are 200MB+ are rare edge cases. For typical use, JSZip's approach is actually simpler and more reliable.

5. **Ecosystem and Support**: Extensive StackOverflow questions, GitHub issues, and documentation mean problems are already solved. Active maintenance means security and compatibility updates.

6. **Bundle Size Acceptable**: At ~30KB gzipped, the cost is very reasonable for the functionality and reliability gained.

**Implementation Plan**: 
1. Install JSZip via npm
2. Create useSazParser hook for file loading
3. Implement async parsing with progress indication
4. Handle errors gracefully (corrupted files, wrong format)
5. Extract session files from raw/ folder
6. Parse HTTP request/response data from text content

## Consequences

### Positive Consequences

- ➕ Reliable ZIP extraction with minimal code
- ➕ Simple, maintainable implementation
- ➕ Promise-based async operations
- ➕ Good performance for typical file sizes
- ➕ Excellent documentation and community support
- ➕ Security updates and bug fixes maintained by community
- ➕ Works consistently across all modern browsers

### Negative Consequences

- ➖ Entire file loaded into memory (but acceptable for our use case)
- ➖ External dependency to maintain (but stable and well-maintained)
- ➖ May struggle with files >200MB (very rare edge case)

### Neutral Consequences

- 🔄 Need to stay updated with JSZip releases
- 🔄 Bundle includes full JSZip even though we only use read operations

### Risks and Mitigation

| Risk | Impact | Probability | Mitigation Strategy |
|------|--------|-------------|---------------------|
| JSZip maintenance stops | Medium | Very Low | Library is widely used; fork or migrate to fflate if needed |
| Memory issues with large files | Low | Low | Document file size limits; show warning for very large files; consider Web Worker if needed |
| Security vulnerability in JSZip | Medium | Low | Monitor security advisories; update promptly; JSZip has good security track record |
| Performance issues | Low | Very Low | Implement loading states; show progress; test with realistic file sizes |

## Follow-up Actions

- [x] Install JSZip dependency
- [x] Implement useSazParser hook
- [x] Add error handling for invalid ZIP files
- [x] Add error handling for missing raw/ folder
- [x] Test with various .saz file sizes
- [x] Document supported file size range
- [ ] Add progress indication for large files
- [ ] Consider Web Worker implementation if performance issues arise

## References

- [JSZip Documentation](https://stuk.github.io/jszip/)
- [JSZip GitHub Repository](https://github.com/Stuk/jszip)
- [Telerik SAZ Format Specification](https://docs.telerik.com/fiddler/knowledge-base/SAZ-Format)
- [ZIP File Format Specification](https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT)

## Notes

This decision prioritizes developer productivity and code reliability over maximum performance optimization. For 95% of use cases, JSZip provides the perfect balance. If we encounter users with extremely large files (>200MB), we can revisit this decision and potentially add Web Worker support or migrate to a streaming library. However, the cost of premature optimization would outweigh the benefits given the typical file sizes users work with.

The fact that Fiddler itself splits sessions into separate files within the ZIP archive works in our favor - even large capture sessions are split into many small files that JSZip handles efficiently.
