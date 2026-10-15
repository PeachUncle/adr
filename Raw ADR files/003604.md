# Decision: SigFile-CLI Packaging Strategy

## Status
- Date: 2024-04-04
- Type: Architecture
- Status: Under Review

## Context
The SigFile-CLI is a critical component of the SigFile ecosystem, providing command-line interface functionality for development process tracking. We need to decide whether to:
1. Package SigFile-CLI separately as a standalone tool
2. Bundle it with SigFile releases for simplified installation

## Analysis

### Option 1: Separate Packaging
**Pros:**
- Independent versioning and updates
- Smaller download size for users who don't need CLI
- Clearer separation of concerns
- Easier maintenance and testing
- Can be installed via pip independently
- Follows Unix philosophy of doing one thing well

**Cons:**
- Additional installation step for users
- Potential version mismatch between SigFile and CLI
- More complex dependency management
- Users need to manage two separate tools

### Option 2: Bundled Packaging
**Pros:**
- Single installation process
- Guaranteed version compatibility
- Simplified user experience
- Reduced support complexity
- Consistent feature set

**Cons:**
- Larger download size
- Less flexibility in version management
- More complex release process
- Potential bloat for users who don't need CLI

## Decision
**Recommended Approach: Hybrid Model**

1. **Primary Distribution:**
   - Keep SigFile-CLI as a separate package
   - Maintain independent versioning
   - Allow pip installation: `pip install sigfile-cli`

2. **Bundled Option:**
   - Include SigFile-CLI as an optional component in SigFile releases
   - Use dependency specification in SigFile's setup.py:
     ```python
     extras_require={
         'cli': ['sigfile-cli>=0.1.0'],
     }
     ```
   - Allow installation via: `pip install sigfile[cli]`

3. **Version Management:**
   - Define compatible version ranges in SigFile's requirements
   - Use semantic versioning to ensure compatibility
   - Document version requirements clearly

## Implementation Plan

1. **Short Term:**
   - Document the hybrid approach in README
   - Update SigFile's setup.py with CLI dependency
   - Add installation instructions for both methods

2. **Medium Term:**
   - Implement version compatibility checks
   - Add CLI version validation in SigFile
   - Create migration guides for version updates

3. **Long Term:**
   - Consider unified versioning if needed
   - Evaluate user feedback on installation methods
   - Optimize bundle size if necessary

## Consequences
### Positive
- Flexible installation options
- Clear version management
- Maintained separation of concerns
- Improved user experience
- Reduced support complexity

### Negative
- Slightly more complex documentation
- Need to maintain compatibility matrix
- Additional testing requirements

## Related Documents
- [Development Pipeline Documentation](../docs/development_pipeline.md)
- [Version Compatibility Matrix](../docs/version_compatibility.md)
- [Installation Guide](../docs/installation.md) 