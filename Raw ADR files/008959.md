# ADR-010: Image Loading Performance Optimization

## Status
Accepted

## Context

The DuperHeroes game features 194+ hero characters with visual representations that are critical to gameplay. The current image loading implementation has significant performance issues that impact user experience:

**Current Problems:**
- 214 images totaling **374MB** with individual files up to **7.5MB** each
- All 193+ hero images load simultaneously on the battlecards page
- No lazy loading causing network congestion and slow initial page loads
- Layout shift from missing image dimensions
- Poor error handling for failed image loads
- No responsive image variants for different use cases
- No modern image formats (WebP) for better compression

**Performance Impact:**
- Initial page load times of 10+ seconds on slower connections
- Cumulative layout shift during image loading
- Poor user experience with blank spaces and loading delays
- Network congestion from simultaneous image requests
- No progressive enhancement for modern browsers

The project needed a comprehensive solution to optimize image loading while maintaining the visual quality essential for the superhero identification game.

## Decision

We will implement a two-phase image loading performance optimization strategy:

**Phase 1: Quick Wins (Immediate Performance Fixes)**
- Add native lazy loading to all images
- Set explicit image dimensions to prevent layout shift
- Compress largest images (>2MB) to <500KB each
- Implement enhanced error handling with emoji fallbacks
- Add loading states for better user experience

**Phase 2: Advanced Optimization (Modern Loading Techniques)**
- Create responsive image variants (120px, 300px, 600px)
- Implement WebP conversion with progressive enhancement
- Add advanced intersection observer for intelligent loading
- Implement progressive loading with blur-up technique
- Update all components to use responsive images

## Alternatives Considered

### Option 1: CDN-Based Image Optimization
- **Description**: Use a CDN service like Cloudinary or ImageKit for automatic optimization
- **Pros**: Automatic optimization, global distribution, no build process required
- **Cons**: External dependency, ongoing costs, potential vendor lock-in, overkill for static site
- **Risk Level**: Medium

### Option 2: Client-Side Image Compression Only
- **Description**: Focus only on compressing existing images without responsive variants
- **Pros**: Simple implementation, immediate file size reduction
- **Cons**: No responsive loading, still loads large images on mobile, limited performance gains
- **Risk Level**: Low

### Option 3: Progressive Web App with Service Workers
- **Description**: Implement PWA features with service worker caching for images
- **Pros**: Advanced caching, offline support, app-like experience
- **Cons**: Significant complexity, browser compatibility issues, overkill for simple game
- **Risk Level**: High

### Option 4: External Image Hosting
- **Description**: Move all images to external hosting service (AWS S3, etc.)
- **Pros**: Scalable, global distribution, professional image management
- **Cons**: External dependency, hosting costs, potential loading delays, complexity
- **Risk Level**: Medium

## Consequences

### Positive
- **70-80% faster initial page loads** with Phase 1 optimizations
- **60-70% faster image load times** with Phase 2 advanced techniques
- **Eliminated layout shift** through explicit dimensions and loading states
- **Reduced network requests** from 193 simultaneous to ~10-15 initially
- **40-60% bandwidth savings** through WebP format and responsive variants
- **Better user experience** with progressive loading and error handling
- **Modern browser optimization** with WebP support and intersection observer
- **Maintained visual quality** while significantly improving performance

### Negative
- **Build process complexity** added for image processing
- **Development overhead** for maintaining responsive image variants
- **Storage increase** from multiple image sizes (mitigated by compression)
- **Browser compatibility considerations** for WebP and intersection observer
- **Maintenance burden** for image processing scripts

### Neutral
- **No external dependencies** - all optimizations use native browser features
- **Backward compatibility** - graceful fallbacks for older browsers
- **Static site architecture** maintained - no server-side processing required

## Implementation Notes

### Phase 1 Implementation
- **Native Lazy Loading**: Add `loading="lazy"` attribute to all `<img>` tags
- **Explicit Dimensions**: Set `width` and `height` attributes to prevent layout shift
- **Image Compression**: Target 80% quality JPEG compression for files >2MB
- **Error Handling**: Implement retry logic with exponential backoff
- **Loading States**: Add CSS animations for visual feedback during loading

### Phase 2 Implementation
- **Build Scripts**: Create Node.js scripts using Sharp library for image processing
- **Responsive Variants**: Generate thumbnail (120px), medium (300px), large (600px) sizes
- **WebP Conversion**: Create WebP versions with JPEG fallbacks using `<picture>` element
- **Advanced Loading**: Implement intersection observer with 50px root margin
- **Progressive Enhancement**: Add blur-up technique for smooth loading transitions

### Technical Implementation Details
```javascript
// Responsive image generation
const sizes = {
    thumbnail: { width: 120, height: 120, quality: 80 },
    medium: { width: 300, height: 300, quality: 85 },
    large: { width: 600, height: 600, quality: 90 }
};

// Progressive image component
function createProgressiveImage(hero, size = 'thumbnail') {
    const slug = getHeroSlug(hero.superhero_name);
    return `
        <div class="progressive-image">
            <div class="placeholder"></div>
            <picture>
                <source srcset="./images/${size}/${slug}.webp" type="image/webp">
                <img src="./images/${size}/${slug}.jpg" 
                     alt="${hero.superhero_name}" 
                     class="actual hero-image"
                     loading="lazy"
                     width="${getSizeConfig(size).width}" 
                     height="${getSizeConfig(size).height}">
            </picture>
        </div>
    `;
}
```

### Build Process Integration
- **npm Scripts**: Add `images:responsive` and `images:webp` commands
- **GitHub Actions**: Integrate image processing into deployment workflow
- **Development Workflow**: Local image processing for testing and development

### Success Metrics
- **Page Load Time**: 70-80% improvement in initial load time
- **Image Load Time**: 60-70% faster individual image loading
- **Layout Stability**: Eliminate cumulative layout shift
- **Network Efficiency**: Reduce initial requests from 193 to ~10-15
- **Bandwidth Usage**: 40-60% reduction in image bytes transferred

## References
- [GitHub Issue #15: Phase 1 Image Loading Quick Wins](https://github.com/ghelleks/duperheroes/issues/15)
- [GitHub Issue #16: Phase 2 Image Optimization & Modern Loading](https://github.com/ghelleks/duperheroes/issues/16)
- [WebP Image Format](https://developers.google.com/speed/webp)
- [Intersection Observer API](https://developer.mozilla.org/en-US/docs/Web/API/Intersection_Observer_API)
- [Native Lazy Loading](https://web.dev/native-lazy-loading/)
- [Sharp Image Processing Library](https://sharp.pixelplumbing.com/)
