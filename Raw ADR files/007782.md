# ADR: Frontend Responsive Image Implementation Strategy for Copper Print Gallery

## Date
2024-07-28

## Status
Proposed

## Context
With the decision to create multiple versions of each image to support various devices and display densities, we need a strategy to effectively implement responsive images in the frontend of the Copper Print Gallery. This strategy should ensure that the most appropriate image version is served to each user, optimizing for both performance and visual quality.

## Decision
We have decided to implement a comprehensive responsive image strategy using a combination of HTML5 features and JavaScript enhancements. The key components of this strategy are:

1. Use of `srcset` and `sizes` attributes:
   - Implement `srcset` to provide the browser with multiple image sources.
   - Use `sizes` to hint at the image's displayed size in different layouts.

2. Art Direction with `<picture>` element:
   - Utilize the `<picture>` element for cases where we need to change the image aspect ratio or make significant crops for different screen sizes.

3. Lazy Loading:
   - Implement native lazy loading using the `loading="lazy"` attribute.
   - Enhance with a JavaScript lazy loading library for broader browser support.

4. Client-side Detection and Selection:
   - Implement JavaScript to detect device capabilities (e.g., DPI, viewport size).
   - Dynamically select the most appropriate image version based on these capabilities and network conditions.

5. Fallback Mechanisms:
   - Ensure graceful fallback for browsers that don't support advanced responsive image features.

Example implementation:

```html
<picture>
  <source
    media="(min-width: 1200px)"
    srcset="/images/123e4567_xlarge.webp 3840w,
            /images/123e4567_large_2x.webp 3200w,
            /images/123e4567_large.webp 1600w"
    sizes="(min-width: 1200px) 1100px, 100vw">
  <source
    media="(min-width: 800px)"
    srcset="/images/123e4567_large.webp 1600w,
            /images/123e4567_medium_2x.webp 1600w,
            /images/123e4567_medium.webp 800w"
    sizes="(min-width: 800px) 750px, 100vw">
  <img src="/images/123e4567_medium.webp"
       srcset="/images/123e4567_medium.webp 800w,
               /images/123e4567_thumbnail_2x.webp 400w,
               /images/123e4567_thumbnail.webp 200w"
       sizes="(max-width: 799px) 100vw, 800px"
       alt="Artwork description"
       loading="lazy">
</picture>
```

## Consequences

### Positive
- Optimal image delivery for various devices and network conditions.
- Improved page load times and reduced bandwidth usage.
- Enhanced user experience with appropriate image quality for each device.
- Future-proofing for new devices with varying pixel densities.

### Negative
- Increased complexity in HTML structure.
- Potential for increased initial development time.
- Need for careful testing across a wide range of devices and browsers.

### Risks
- Browser inconsistencies in handling responsive images.
- Potential for selecting overly large images on small devices with high DPI screens.

## Implementation Notes
- Develop a standardized component or utility function to generate responsive image markup.
- Implement server-side logic to dynamically generate `srcset` and `sizes` attributes based on available image versions.
- Consider using a build process to automate the generation of responsive image markup.
- Implement monitoring to track which image versions are being served most frequently.

## Related Decisions
- Definition of Image Version Names and Properties for Copper Print Gallery
- Image Processing Workflow for Copper Print Gallery

## References
- Responsive Images: [MDN Web Docs](https://developer.mozilla.org/en-US/docs/Learn/HTML/Multimedia_and_embedding/Responsive_images)
- Responsive Images in CSS: [CSS-Tricks](https://css-tricks.com/responsive-images-css/)
- Native lazy-loading for the web: [web.dev](https://web.dev/native-lazy-loading/)
