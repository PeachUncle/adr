# Alpine.js Self-Hosting Decision

## Decision Made

**Date**: November 16, 2025 **Status**: Implemented

## Summary

Moved from CDN-based Alpine.js to self-hosted implementation for better
reliability and performance.

## Reasoning

### Problems with CDN Approach

1. **Complex conditional loading** - CDN config had confusing
   production/development logic
2. **Single point of failure** - External CDN could affect critical navigation
   functionality
3. **Network dependency** - Site navigation broken if CDN unavailable
4. **Build complexity** - Extra configuration for environment-specific loading

### Benefits of Self-Hosting

1. **Reliability** - Navigation works regardless of external service status
2. **Performance** - No additional DNS lookup or external HTTP request
3. **Simplicity** - Direct asset inclusion, no complex conditionals
4. **Control** - Version management through Hugo's asset pipeline
5. **Security** - No external script dependencies
6. **Offline development** - Works without internet connection

## Implementation

### Files Changed

- `assets/js/alpinejs.min.js` - Self-hosted Alpine.js v3.14.1
- `layouts/partials/head/cdn.html` - Simplified to always load self-hosted
  version
- `data/cdn.toml` - Removed Alpine.js CDN entry, added documentation comment

### Asset Pipeline

```hugo
{{ $alpinejs := resources.Get "js/alpinejs.min.js" }}
{{ with $alpinejs }}
    {{ $fingerprinted := . | fingerprint }}
    <script defer
            src="{{ $fingerprinted.RelPermalink }}"
            {{ if $fingerprinted.Data.Integrity }} integrity="{{ $fingerprinted.Data.Integrity }}"{{ end }}
            crossorigin="anonymous"></script>
{{ end }}
```

## Impact Assessment

### Positive Impacts

- ✅ Navigation functionality now reliable in all environments
- ✅ Faster page load (one less external request)
- ✅ Simplified build configuration
- ✅ Better offline development experience
- ✅ Hugo asset pipeline benefits (fingerprinting, minification)

### Trade-offs

- ⚠️ Slightly larger initial bundle size (~45KB)
- ⚠️ Manual version updates required (vs. CDN auto-update)

### Mitigation

- Bundle size is minimal for critical functionality gain
- Hugo's fingerprinting ensures cache busting on updates
- Version updates are infrequent for Alpine.js stable releases

## Recommendation

**Keep self-hosted Alpine.js** - Benefits outweigh trade-offs for this critical
navigation dependency.

## Future Considerations

- Monitor Alpine.js version updates
- Consider bundle size optimization if needed
- Document any performance impact measurements
