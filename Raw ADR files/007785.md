# ADR: Definition of Image Version Names and Properties for Copper Print Gallery

## Date
2024-07-27 (Updated: 2024-07-28)

## Status
Proposed

## Context
The Copper Print Gallery system needs to manage multiple versions of each uploaded image to cater to different display contexts and device capabilities. We need a standardized definition of these versions to ensure consistency across all services and the frontend application. After further consideration, we've expanded the initial proposal to better support a wider range of devices, including high-DPI displays.

## Decision
We have decided to define the following standard image versions:

1. Original: The unmodified, original uploaded image.
2. Thumbnail: A small version for previews and listings.
3. Medium: A medium-sized version for typical web viewing.
4. Large: A larger version for detailed viewing or high-resolution displays.
5. XLarge: An extra large version for 4K and other high-resolution displays.
6. 2x versions: High-resolution versions of thumbnail, medium, and large for high-DPI displays.

These versions will be defined in a shared configuration as follows:

```json
{
  "IMAGE_VERSIONS": [
    {"name": "original", "max_width": null, "max_height": null, "format": "preserve"},
    {"name": "thumbnail", "max_width": 200, "max_height": 200, "format": "webp"},
    {"name": "thumbnail_2x", "max_width": 400, "max_height": 400, "format": "webp"},
    {"name": "medium", "max_width": 800, "max_height": null, "format": "webp"},
    {"name": "medium_2x", "max_width": 1600, "max_height": null, "format": "webp"},
    {"name": "large", "max_width": 1600, "max_height": null, "format": "webp"},
    {"name": "large_2x", "max_width": 3200, "max_height": null, "format": "webp"},
    {"name": "xlarge", "max_width": 3840, "max_height": null, "format": "webp"}
  ]
}
```

Properties:
- `name`: The identifier for the version.
- `max_width` and `max_height`: The maximum dimensions for the version. Null means no limit.
- `format`: The output format for the image version.

## Consequences

### Positive
- Comprehensive support for a wide range of devices, including high-DPI displays.
- Improved image quality on high-resolution screens.
- Flexibility to serve appropriately sized images for different contexts.
- Future-proofing for emerging high-resolution display technologies.

### Negative
- Increased storage requirements due to additional image versions.
- Longer processing time for each uploaded image.
- More complex logic in the frontend to choose the appropriate version.

### Risks
- Increased complexity in managing and serving multiple image versions.
- Potential for increased bandwidth usage if version selection is not optimized.
- Need for more sophisticated caching strategies to handle multiple versions efficiently.

## Implementation Notes
- Store this configuration in a central location accessible by all relevant services.
- Implement logic in the frontend to select the appropriate image version based on device capabilities and network conditions.
- Consider using responsive image techniques (e.g., srcset and sizes attributes) in the frontend to leverage these multiple versions effectively.
- Ensure the Image Processing Service can handle creating all these versions efficiently.
- Implement a caching strategy that can effectively manage multiple versions of each image.
- Monitor storage usage and adjust retention policies if necessary.

## Related Decisions
- Image ID Assignment and Versioning
- Image Processing Workflow for Copper Print Gallery
- Frontend responsive image implementation strategy

## References
- Responsive Images: [MDN Web Docs](https://developer.mozilla.org/en-US/docs/Learn/HTML/Multimedia_and_embedding/Responsive_images)
- WebP image format: [Google Developers](https://developers.google.com/speed/webp)
- High-DPI Images for Variable Pixel Densities: [Web Dev](https://web.dev/serve-responsive-images/)