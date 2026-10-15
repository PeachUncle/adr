---
docid: ADR-099
title: ADR CLOUD IMAGE STORAGE PROCESSING
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

﻿# ADR: Cloud-Based Image Storage with Dynamic Processing

**DocID**: `ADR-CLOUD-IMAGE`  
**Status**: DRAFT  
**Date**: 2026-01-01  
**Author**: @Architect  
**Reviewers**: @Backend, @Frontend, @DevOps, @Security, @TechLead

---

## Context

B2X requires a robust image storage and processing solution to support:
- Product images (multiple sizes, formats)
- CMS media assets
- User-generated content (UGC)
- Dynamic image transformations (resize, crop, format conversion)
- Modern format delivery (WebP, AVIF)
- CDN integration for global delivery
- Visual search capabilities (future: image embeddings)

Current state: Basic file upload to local/cloud storage without transformation pipeline.

**Requirements from Product Vision** (see [PRODUCT_VISION.md](../.ai/requirements/PRODUCT_VISION.md)):
> "Media & image delivery: support serving images from cloud blob storage (S3, Azure Blob, GCS), first‑class support for modern formats (WebP, AVIF), and dynamic on‑the‑fly resizing/optimization with CDN integration."

---

## Decision Drivers

| Priority | Driver |
|----------|--------|
| P0 | Performance: Sub-100ms image delivery globally |
| P0 | Modern formats: Automatic WebP/AVIF conversion |
| P1 | Self-hosted option: Control over data & costs |
| P1 | Integration: Works with existing S3/Azure/GCS storage |
| P2 | Cost predictability: Avoid surprise bills at scale |
| P2 | Security: Signed URLs, access control |
| P3 | AI features: Future support for image embeddings/visual search |

---

## Options Considered

### Option 1: imgproxy (Self-Hosted) ⭐ RECOMMENDED

**Overview**: Self-hosted, Go-based image processing server. Open-core model with Pro features.

| Aspect | Details |
|--------|---------|
| **Type** | Self-hosted (Docker/K8s) |
| **License** | Open Source (MIT) + Pro ($49/mo) |
| **Performance** | Fastest in benchmarks (Go + libvips) |
| **Formats** | JPEG, PNG, GIF, WebP, AVIF, JPEG XL, HEIC |
| **Storage** | Any HTTP source, S3, GCS, Azure Blob |
| **Security** | URL signing, authorization headers |
| **Pricing** | Infrastructure cost only (self-hosted) |

**Pros**:
- ✅ **Fastest performance** - Go-based, highly optimized
- ✅ **No vendor lock-in** - runs on your infrastructure
- ✅ **Predictable costs** - no per-request pricing
- ✅ **URL-based API** - simple integration
- ✅ **Modern format support** - AVIF, WebP, JPEG XL
- ✅ **Security built-in** - URL signing, image bomb protection
- ✅ **Kubernetes-native** - easy scaling

**Cons**:
- ❌ Infrastructure management required
- ❌ Pro features require license ($49/mo or $499/yr)
- ❌ No built-in DAM/asset management

**Pro Features** (paid):
- Video thumbnail generation
- Advanced watermarking
- PDF/PSD preview generation
- GIF to MP4 conversion
- Advanced smart cropping (object detection)

**URL Example**:
```
https://imgproxy.example.com/{signature}/rs:fill:300:200/g:sm/plain/s3://bucket/image.jpg
```

**References**:
- Website: https://imgproxy.net/
- GitHub: https://github.com/imgproxy/imgproxy (10.2k stars)
- Docs: https://docs.imgproxy.net/

---

### Option 2: Imageflow (Self-Hosted)

**Overview**: Rust-based image processing library with .NET bindings. Created by ImageResizer team.

| Aspect | Details |
|--------|---------|
| **Type** | Self-hosted (library/.NET Server) |
| **License** | AGPLv3 (free) or Commercial |
| **Performance** | Up to 17x faster than ImageMagick |
| **Formats** | JPEG, PNG, GIF, WebP, AVIF |
| **Storage** | S3, Azure Blob, filesystem |
| **Security** | URL signing |
| **Pricing** | AGPLv3 free / Commercial license |

**Pros**:
- ✅ **Excellent .NET integration** - Imageflow.NET Server
- ✅ **High quality output** - linear light processing
- ✅ **Fast** - Rust core, native performance
- ✅ **Query string API** - ImageResizer compatible
- ✅ **Mature** - 10+ years of development

**Cons**:
- ❌ AGPLv3 requires open-sourcing or commercial license
- ❌ Smaller community than imgproxy
- ❌ Less active development recently
- ❌ No built-in object detection

**URL Example**:
```
/images/photo.jpg?width=300&height=200&mode=crop&format=webp
```

**References**:
- Website: https://www.imageflow.io/
- GitHub: https://github.com/imazen/imageflow (4.4k stars)
- .NET Server: https://github.com/imazen/imageflow-dotnet-server

---

### Option 3: Thumbor (Self-Hosted)

**Overview**: Python-based smart image service with AI cropping.

| Aspect | Details |
|--------|---------|
| **Type** | Self-hosted (Python/Docker) |
| **License** | MIT (fully open source) |
| **Performance** | Moderate (Python-based) |
| **Formats** | JPEG, PNG, GIF, WebP |
| **Storage** | S3, filesystem, HTTP |
| **Security** | URL signing |
| **Pricing** | Free |

**Pros**:
- ✅ **100% open source** - no paid tiers
- ✅ **Smart cropping** - face/feature detection
- ✅ **Extensible** - plugin architecture
- ✅ **Large community** - well documented

**Cons**:
- ❌ **Slower** than Go/Rust alternatives
- ❌ **No AVIF support** by default
- ❌ **Python dependency** - different from our stack
- ❌ **Less active** - fewer updates recently

**URL Example**:
```
/unsafe/300x200/smart/example.com/image.jpg
```

**References**:
- Website: https://thumbor.org/
- GitHub: https://github.com/thumbor/thumbor (9.6k stars)

---

### Option 4: Cloudinary (SaaS)

**Overview**: Full-featured media management SaaS with AI capabilities.

| Aspect | Details |
|--------|---------|
| **Type** | SaaS (managed) |
| **License** | Proprietary |
| **Performance** | Excellent (global CDN) |
| **Formats** | All formats + video |
| **Storage** | Cloudinary-managed |
| **Security** | Signed URLs, access control |
| **Pricing** | Usage-based (can be expensive) |

**Pros**:
- ✅ **Zero infrastructure** - fully managed
- ✅ **Feature-rich** - AI background removal, auto-tagging
- ✅ **Global CDN** - built-in delivery
- ✅ **DAM included** - asset management
- ✅ **.NET SDK** - good integration
- ✅ **Video support** - streaming, transcoding

**Cons**:
- ❌ **Expensive at scale** - usage-based pricing
- ❌ **Vendor lock-in** - proprietary storage
- ❌ **Data residency** - limited control
- ❌ **Unpredictable costs** - traffic spikes = surprise bills

**Pricing** (2025):
- Free: 25 credits/month
- Plus: $99/month (225 credits)
- Advanced: $249/month (600 credits)
- Enterprise: Custom

**URL Example**:
```
https://res.cloudinary.com/demo/image/upload/w_300,h_200,c_fill/sample.jpg
```

**References**:
- Website: https://cloudinary.com/
- Docs: https://cloudinary.com/documentation

---

### Option 5: ImageKit (SaaS)

**Overview**: Modern image/video API platform with DAM.

| Aspect | Details |
|--------|---------|
| **Type** | SaaS with external storage support |
| **License** | Proprietary |
| **Performance** | Excellent (CloudFront CDN) |
| **Formats** | All modern formats + video |
| **Storage** | Your S3/GCS/Azure + ImageKit DAM |
| **Security** | Signed URLs, access control |
| **Pricing** | Usage-based (more predictable) |

**Pros**:
- ✅ **Use existing storage** - no migration needed
- ✅ **Modern formats** - WebP, AVIF automatic
- ✅ **Video streaming** - HLS/DASH support
- ✅ **AI features** - smart crop, background removal
- ✅ **Better pricing** than Cloudinary
- ✅ **ISO 27001, GDPR compliant**

**Cons**:
- ❌ **Still SaaS** - some vendor dependency
- ❌ **Usage-based** - costs scale with traffic
- ❌ **Less feature-rich** than Cloudinary

**Pricing** (2025):
- Free: 20GB bandwidth/month
- Standard: From $49/month
- Enterprise: Custom

**URL Example**:
```
https://ik.imagekit.io/your_id/image.jpg?tr=w-300,h-200
```

**References**:
- Website: https://imagekit.io/
- Docs: https://imagekit.io/docs/

---

### Option 6: Bunny Optimizer (SaaS/CDN)

**Overview**: CDN with integrated image optimization.

| Aspect | Details |
|--------|---------|
| **Type** | CDN + Optimization |
| **License** | Proprietary |
| **Performance** | Excellent (global PoPs) |
| **Formats** | WebP, AVIF |
| **Storage** | Origin-based (your storage) |
| **Security** | Token auth |
| **Pricing** | Fixed $9.50/month per site |

**Pros**:
- ✅ **Simple pricing** - flat rate per site
- ✅ **No per-request cost** - unlimited optimizations
- ✅ **Built-in CDN** - global delivery
- ✅ **Easy setup** - no code changes

**Cons**:
- ❌ **Limited transformations** - basic resize/crop
- ❌ **No advanced AI features**
- ❌ **Less flexible** than dedicated solutions

**References**:
- Website: https://bunny.net/optimizer/

---

## Comparison Matrix

| Feature | imgproxy | Imageflow | Thumbor | Cloudinary | ImageKit | Bunny |
|---------|----------|-----------|---------|------------|----------|-------|
| **Type** | Self-hosted | Self-hosted | Self-hosted | SaaS | SaaS | CDN+SaaS |
| **Performance** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **WebP** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **AVIF** | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ |
| **Smart Crop** | Pro | Basic | ✅ | ✅ | ✅ | Basic |
| **Video** | Pro | ❌ | ❌ | ✅ | ✅ | ❌ |
| **AI Features** | Pro | ❌ | Basic | ✅✅✅ | ✅✅ | ❌ |
| **DAM** | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ |
| **.NET SDK** | ❌ | ✅✅✅ | ❌ | ✅ | ✅ | ❌ |
| **Use Own Storage** | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| **Predictable Cost** | ✅✅✅ | ✅✅✅ | ✅✅✅ | ❌ | ⭐⭐ | ✅✅✅ |
| **Vendor Lock-in** | None | None | None | High | Medium | Low |

---

## Recommendation

### Primary: **imgproxy** (Self-Hosted)

**Rationale**:
1. **Best performance** - Go-based, fastest in benchmarks
2. **Cost predictable** - infrastructure cost only, no per-request fees
3. **No vendor lock-in** - runs on our Kubernetes cluster
4. **Modern formats** - AVIF, WebP, JPEG XL support
5. **Security-first** - URL signing, image bomb protection
6. **Simple integration** - URL-based API, works with any storage

### Secondary (Fallback): **Imageflow** (.NET native)

**When to consider**:
- If deep .NET integration is critical
- If AGPLv3 is acceptable or commercial license acquired
- For specific ImageResizer compatibility needs

### Not Recommended for B2X:

| Option | Reason |
|--------|--------|
| Cloudinary | Too expensive at scale, vendor lock-in |
| Thumbor | Slower performance, no AVIF, Python dependency |
| Bunny | Limited transformation features |

---

## Proposed Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         B2X                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     │
│  │   Frontend   │     │   Admin UI   │     │   Store API  │     │
│  └──────┬───────┘     └──────┬───────┘     └──────┬───────┘     │
│         │                    │                    │              │
│         └────────────────────┼────────────────────┘              │
│                              │                                   │
│                              ▼                                   │
│                    ┌─────────────────┐                          │
│                    │   CDN (Edge)    │                          │
│                    │  CloudFront/    │                          │
│                    │  Bunny/Fastly   │                          │
│                    └────────┬────────┘                          │
│                             │                                    │
│                             ▼                                    │
│                    ┌─────────────────┐                          │
│                    │    imgproxy     │                          │
│                    │  (Kubernetes)   │                          │
│                    │  - URL signing  │                          │
│                    │  - Resize/crop  │                          │
│                    │  - Format conv  │                          │
│                    └────────┬────────┘                          │
│                             │                                    │
│              ┌──────────────┼──────────────┐                    │
│              ▼              ▼              ▼                    │
│       ┌───────────┐  ┌───────────┐  ┌───────────┐              │
│       │    S3     │  │   Azure   │  │    GCS    │              │
│       │  Bucket   │  │   Blob    │  │  Bucket   │              │
│       └───────────┘  └───────────┘  └───────────┘              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### URL Structure

```
# Pattern
https://images.B2X.io/{signature}/{processing}/{source}

# Examples
# Resize to 300x200, WebP format
https://images.B2X.io/abc123/rs:fill:300:200/f:webp/plain/s3://products/shoe.jpg

# Smart crop, AVIF format
https://images.B2X.io/abc123/rs:fill:400:400/g:sm/f:avif/plain/s3://products/model.jpg

# Watermarked product image
https://images.B2X.io/abc123/rs:fit:800:600/wm:0.5:ce:10:10:0.3/plain/s3://products/item.jpg

# DPR-aware (2x retina)
https://images.B2X.io/abc123/rs:fill:300:200/dpr:2/f:webp/plain/s3://products/shoe.jpg
```

---

## Responsive Images Strategy (srcset & sizes)

### Why Responsive Images?

| Scenario | Without srcset | With srcset |
|----------|----------------|-------------|
| Mobile (375px, 2x) | Downloads 1200px image (500KB) | Downloads 750px image (150KB) |
| Tablet (768px, 1x) | Downloads 1200px image (500KB) | Downloads 768px image (180KB) |
| Desktop (1920px, 1x) | Downloads 1200px image (500KB) | Downloads 1200px image (350KB) |
| **Bandwidth saved** | - | **40-70%** |

### Predefined Size Presets

Define standard breakpoints for consistent responsive images:

```typescript
// src/config/image-sizes.ts
export const IMAGE_PRESETS = {
  // Product images
  productThumb: {
    sizes: [150, 300, 450],  // 1x, 2x, 3x
    defaultSize: 150,
    aspectRatio: '1:1',
  },
  productCard: {
    sizes: [200, 400, 600, 800],
    defaultSize: 400,
    aspectRatio: '4:3',
  },
  productHero: {
    sizes: [400, 800, 1200, 1600, 2400],
    defaultSize: 800,
    aspectRatio: '16:9',
  },
  
  // CMS images
  cmsFullWidth: {
    sizes: [640, 960, 1280, 1920, 2560],
    defaultSize: 1280,
    aspectRatio: 'auto',
  },
  cmsThumbnail: {
    sizes: [100, 200, 300],
    defaultSize: 100,
    aspectRatio: '1:1',
  },
  
  // Avatar/Profile
  avatar: {
    sizes: [32, 64, 96, 128],
    defaultSize: 64,
    aspectRatio: '1:1',
  },
} as const;

export type ImagePreset = keyof typeof IMAGE_PRESETS;
```

### Backend: URL Generation Service

```csharp
// Services/ImageUrlService.cs
public interface IImageUrlService
{
    string GetUrl(string source, int width, int? height = null, ImageFormat? format = null);
    string GetSrcSet(string source, int[] widths, int? height = null);
    ResponsiveImageUrls GetResponsiveUrls(string source, ImagePreset preset);
}

public class ImgproxyImageUrlService : IImageUrlService
{
    private readonly ImgproxyOptions _options;
    private readonly IUrlSigner _signer;

    public string GetUrl(string source, int width, int? height = null, ImageFormat? format = null)
    {
        var processing = new StringBuilder();
        
        // Resize
        if (height.HasValue)
            processing.Append($"rs:fill:{width}:{height}/");
        else
            processing.Append($"rs:fit:{width}/");
        
        // Format (auto-detect best format if not specified)
        processing.Append(format switch
        {
            ImageFormat.WebP => "f:webp/",
            ImageFormat.Avif => "f:avif/",
            ImageFormat.Jpeg => "f:jpg/",
            _ => "f:auto/"  // Let imgproxy choose based on Accept header
        });
        
        // Quality optimization
        processing.Append("q:85/");
        
        var path = $"/{processing}plain/{EncodeSource(source)}";
        var signature = _signer.Sign(path);
        
        return $"{_options.BaseUrl}/{signature}{path}";
    }

    public string GetSrcSet(string source, int[] widths, int? aspectHeight = null)
    {
        return string.Join(", ", widths.Select(w => 
        {
            var height = aspectHeight.HasValue ? (int)(w * aspectHeight / widths.Max()) : (int?)null;
            return $"{GetUrl(source, w, height)} {w}w";
        }));
    }

    public ResponsiveImageUrls GetResponsiveUrls(string source, ImagePreset preset)
    {
        var config = GetPresetConfig(preset);
        
        return new ResponsiveImageUrls
        {
            Src = GetUrl(source, config.DefaultSize),
            SrcSet = GetSrcSet(source, config.Sizes),
            Sizes = GetDefaultSizes(preset),
            Width = config.DefaultSize,
            AspectRatio = config.AspectRatio,
        };
    }

    private string GetDefaultSizes(ImagePreset preset) => preset switch
    {
        ImagePreset.ProductThumb => "150px",
        ImagePreset.ProductCard => "(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 400px",
        ImagePreset.ProductHero => "(max-width: 640px) 100vw, (max-width: 1280px) 80vw, 1200px",
        ImagePreset.CmsFullWidth => "100vw",
        _ => "100vw"
    };
}

public record ResponsiveImageUrls
{
    public string Src { get; init; } = "";
    public string SrcSet { get; init; } = "";
    public string Sizes { get; init; } = "";
    public int Width { get; init; }
    public string AspectRatio { get; init; } = "auto";
}
```

### Frontend: Vue Composable

```typescript
// src/composables/useResponsiveImage.ts
import { computed, type MaybeRef, unref } from 'vue';
import { IMAGE_PRESETS, type ImagePreset } from '@/config/image-sizes';

interface UseResponsiveImageOptions {
  source: MaybeRef<string>;
  preset: ImagePreset;
  alt: MaybeRef<string>;
  lazy?: boolean;
  placeholder?: 'blur' | 'color' | 'none';
}

interface ResponsiveImageResult {
  src: string;
  srcset: string;
  sizes: string;
  alt: string;
  loading: 'lazy' | 'eager';
  decoding: 'async' | 'sync';
  width: number;
  height: number;
  style: Record<string, string>;
}

const IMGPROXY_BASE = import.meta.env.VITE_IMGPROXY_URL || '/img';

function generateSignature(path: string): string {
  // In production, signatures should be generated server-side
  // This is a placeholder for development
  return 'dev';
}

function buildImgproxyUrl(source: string, width: number, height?: number): string {
  const resize = height ? `rs:fill:${width}:${height}` : `rs:fit:${width}`;
  const path = `/${resize}/f:auto/q:85/plain/${encodeURIComponent(source)}`;
  const signature = generateSignature(path);
  return `${IMGPROXY_BASE}/${signature}${path}`;
}

export function useResponsiveImage(options: UseResponsiveImageOptions): ResponsiveImageResult {
  const { preset, lazy = true, placeholder = 'none' } = options;
  const config = IMAGE_PRESETS[preset];
  
  const source = computed(() => unref(options.source));
  const alt = computed(() => unref(options.alt));
  
  // Calculate height from aspect ratio
  const getHeight = (width: number): number | undefined => {
    if (config.aspectRatio === 'auto') return undefined;
    const [w, h] = config.aspectRatio.split(':').map(Number);
    return Math.round(width * (h / w));
  };
  
  // Generate srcset
  const srcset = computed(() => {
    return config.sizes
      .map(w => `${buildImgproxyUrl(source.value, w, getHeight(w))} ${w}w`)
      .join(', ');
  });
  
  // Generate sizes attribute based on preset
  const sizes = computed(() => {
    switch (preset) {
      case 'productThumb':
        return '150px';
      case 'productCard':
        return '(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 400px';
      case 'productHero':
        return '(max-width: 640px) 100vw, (max-width: 1280px) 80vw, 1200px';
      case 'cmsFullWidth':
        return '100vw';
      case 'cmsThumbnail':
        return '100px';
      case 'avatar':
        return '64px';
      default:
        return '100vw';
    }
  });
  
  const defaultHeight = getHeight(config.defaultSize);
  
  return {
    src: buildImgproxyUrl(source.value, config.defaultSize, defaultHeight),
    srcset: srcset.value,
    sizes: sizes.value,
    alt: alt.value,
    loading: lazy ? 'lazy' : 'eager',
    decoding: 'async',
    width: config.defaultSize,
    height: defaultHeight ?? config.defaultSize,
    style: placeholder === 'color' 
      ? { backgroundColor: '#f3f4f6', aspectRatio: config.aspectRatio.replace(':', '/') }
      : { aspectRatio: config.aspectRatio.replace(':', '/') },
  };
}
```

### Frontend: Responsive Image Component

```vue
<!-- src/components/ui/ResponsiveImage.vue -->
<script setup lang="ts">
import { computed, ref } from 'vue';
import { useResponsiveImage } from '@/composables/useResponsiveImage';
import type { ImagePreset } from '@/config/image-sizes';

interface Props {
  src: string;
  alt: string;
  preset: ImagePreset;
  lazy?: boolean;
  class?: string;
  placeholder?: 'blur' | 'color' | 'none';
  fallback?: string;
}

const props = withDefaults(defineProps<Props>(), {
  lazy: true,
  placeholder: 'color',
  fallback: '/images/placeholder.svg',
});

const hasError = ref(false);
const isLoaded = ref(false);

const imageProps = computed(() => 
  useResponsiveImage({
    source: props.src,
    preset: props.preset,
    alt: props.alt,
    lazy: props.lazy,
    placeholder: props.placeholder,
  })
);

const handleError = () => {
  hasError.value = true;
};

const handleLoad = () => {
  isLoaded.value = true;
};
</script>

<template>
  <div 
    class="responsive-image-container"
    :style="{ aspectRatio: imageProps.style.aspectRatio }"
  >
    <!-- Placeholder skeleton -->
    <div 
      v-if="!isLoaded && placeholder !== 'none'"
      class="absolute inset-0 bg-gray-200 dark:bg-gray-700 animate-pulse"
      :class="{ 'rounded': $attrs.class?.includes('rounded') }"
    />
    
    <!-- Actual image -->
    <img
      v-if="!hasError"
      :src="imageProps.src"
      :srcset="imageProps.srcset"
      :sizes="imageProps.sizes"
      :alt="imageProps.alt"
      :loading="imageProps.loading"
      :decoding="imageProps.decoding"
      :width="imageProps.width"
      :height="imageProps.height"
      :class="[
        'w-full h-full object-cover transition-opacity duration-300',
        isLoaded ? 'opacity-100' : 'opacity-0',
        props.class
      ]"
      @error="handleError"
      @load="handleLoad"
    />
    
    <!-- Fallback on error -->
    <img
      v-else
      :src="fallback"
      :alt="alt"
      :class="['w-full h-full object-cover', props.class]"
    />
  </div>
</template>

<style scoped>
.responsive-image-container {
  position: relative;
  overflow: hidden;
}
</style>
```

### Usage Examples

```vue
<!-- Product Card -->
<ResponsiveImage
  :src="product.imageUrl"
  :alt="product.name"
  preset="productCard"
  class="rounded-lg"
/>

<!-- Hero Banner -->
<ResponsiveImage
  :src="banner.imageUrl"
  :alt="banner.title"
  preset="productHero"
  :lazy="false"
  placeholder="blur"
/>

<!-- Avatar -->
<ResponsiveImage
  :src="user.avatarUrl"
  :alt="user.name"
  preset="avatar"
  class="rounded-full"
/>

<!-- Manual srcset (advanced) -->
<img
  :src="getImageUrl(product.image, 400)"
  :srcset="`
    ${getImageUrl(product.image, 200)} 200w,
    ${getImageUrl(product.image, 400)} 400w,
    ${getImageUrl(product.image, 800)} 800w
  `"
  sizes="(max-width: 640px) 100vw, 400px"
  :alt="product.name"
  loading="lazy"
  decoding="async"
/>
```

### Art Direction with `<picture>`

For different crops at different breakpoints:

```vue
<!-- src/components/ui/ArtDirectedImage.vue -->
<script setup lang="ts">
interface Props {
  src: string;
  alt: string;
  mobileCrop?: 'square' | 'portrait';
  desktopCrop?: 'landscape' | 'wide';
}

const props = withDefaults(defineProps<Props>(), {
  mobileCrop: 'square',
  desktopCrop: 'landscape',
});

const getMobileUrl = (width: number) => {
  const height = props.mobileCrop === 'square' ? width : Math.round(width * 1.25);
  return buildImgproxyUrl(props.src, width, height);
};

const getDesktopUrl = (width: number) => {
  const height = props.desktopCrop === 'wide' 
    ? Math.round(width / 2.35)  // 2.35:1 cinematic
    : Math.round(width / 1.78); // 16:9
  return buildImgproxyUrl(props.src, width, height);
};
</script>

<template>
  <picture>
    <!-- Desktop: wide crop -->
    <source
      media="(min-width: 1024px)"
      :srcset="`
        ${getDesktopUrl(1024)} 1024w,
        ${getDesktopUrl(1440)} 1440w,
        ${getDesktopUrl(1920)} 1920w
      `"
      sizes="100vw"
    />
    
    <!-- Tablet: landscape -->
    <source
      media="(min-width: 640px)"
      :srcset="`
        ${getDesktopUrl(640)} 640w,
        ${getDesktopUrl(960)} 960w
      `"
      sizes="100vw"
    />
    
    <!-- Mobile: square/portrait crop -->
    <source
      :srcset="`
        ${getMobileUrl(375)} 375w,
        ${getMobileUrl(640)} 640w
      `"
      sizes="100vw"
    />
    
    <!-- Fallback -->
    <img
      :src="getDesktopUrl(800)"
      :alt="alt"
      loading="lazy"
      decoding="async"
      class="w-full h-auto"
    />
  </picture>
</template>
```

### imgproxy DPR Support

imgproxy natively supports Device Pixel Ratio:

```
# 2x retina display
/rs:fill:300:200/dpr:2/plain/s3://bucket/image.jpg
→ Returns 600x400 image

# Auto DPR from Client Hints
IMGPROXY_ENABLE_CLIENT_HINTS=true
→ Reads DPR from Sec-CH-DPR header
```

### Performance Best Practices

| Practice | Implementation |
|----------|----------------|
| **Lazy loading** | `loading="lazy"` on below-fold images |
| **Async decoding** | `decoding="async"` on all images |
| **Size hints** | Always provide `width` and `height` to prevent CLS |
| **Preload hero** | `<link rel="preload" as="image" imagesrcset="...">` |
| **Format negotiation** | Use `f:auto` or Accept header for WebP/AVIF |
| **Quality** | 80-85 for photos, 90+ for graphics |
| **Placeholder** | Use CSS aspect-ratio + skeleton for CLS |

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: imgproxy
  namespace: media
spec:
  replicas: 3
  selector:
    matchLabels:
      app: imgproxy
  template:
    metadata:
      labels:
        app: imgproxy
    spec:
      containers:
      - name: imgproxy
        image: darthsim/imgproxy:latest
        ports:
        - containerPort: 8080
        env:
        - name: IMGPROXY_KEY
          valueFrom:
            secretKeyRef:
              name: imgproxy-secrets
              key: key
        - name: IMGPROXY_SALT
          valueFrom:
            secretKeyRef:
              name: imgproxy-secrets
              key: salt
        - name: IMGPROXY_USE_S3
          value: "true"
        - name: AWS_ACCESS_KEY_ID
          valueFrom:
            secretKeyRef:
              name: aws-credentials
              key: access-key
        - name: AWS_SECRET_ACCESS_KEY
          valueFrom:
            secretKeyRef:
              name: aws-credentials
              key: secret-key
        - name: IMGPROXY_MAX_SRC_RESOLUTION
          value: "50"  # 50 megapixels max
        - name: IMGPROXY_ALLOWED_SOURCES
          value: "s3://B2X-*"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
```

---

## Implementation Plan

### Phase 1: Infrastructure Setup (Week 1-2)
- [ ] Deploy imgproxy to Kubernetes (dev environment)
- [ ] Configure S3/Azure Blob as source storage
- [ ] Set up URL signing with secure keys
- [ ] Configure CDN caching layer

### Phase 2: Backend Integration (Week 2-3)
- [ ] Create `IImageService` abstraction
- [ ] Implement `ImgproxyImageService`
- [ ] Add URL generation helpers
- [ ] Integrate with Product entity (images)

### Phase 3: Frontend Integration (Week 3-4)
- [ ] Create Vue composable `useOptimizedImage`
- [ ] Add responsive image component
- [ ] Implement lazy loading with placeholders
- [ ] Add srcset generation

### Phase 4: CMS Integration (Week 4-5)
- [ ] Media upload API → S3
- [ ] Thumbnail generation on upload
- [ ] Image picker with transformation preview
- [ ] Bulk image optimization tool

### Phase 5: Production & Monitoring (Week 5-6)
- [ ] Production deployment (HA configuration)
- [ ] Monitoring & alerting setup
- [ ] Performance benchmarking
- [ ] Documentation & runbooks

---

## Cost Estimate

### Self-Hosted (imgproxy) - Monthly

| Resource | Specification | Cost (AWS) |
|----------|---------------|------------|
| imgproxy (3x pods) | 2 vCPU, 4GB RAM | ~$150 |
| S3 Storage | 500GB | ~$12 |
| CloudFront CDN | 1TB egress | ~$85 |
| **Total** | | **~$250/month** |

### SaaS Comparison (at 1TB/month egress)

| Provider | Monthly Cost |
|----------|--------------|
| imgproxy (self-hosted) | ~$250 |
| ImageKit | ~$200-400 |
| Cloudinary | ~$500-1000+ |
| Bunny Optimizer | ~$10 + CDN |

---

## Security Considerations

1. **URL Signing**: All transformation URLs must be signed
2. **Source Restriction**: Only allow configured S3 buckets
3. **Size Limits**: Max source resolution 50MP
4. **Rate Limiting**: Implement at CDN and imgproxy level
5. **CORS**: Configure allowed origins
6. **Secrets**: Store signing keys in Kubernetes secrets/Vault

---

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| imgproxy unavailable | Low | High | Multi-replica deployment, health checks |
| High processing load | Medium | Medium | Horizontal scaling, CDN caching |
| Security vulnerability | Low | High | Regular updates, image bomb protection |
| Storage costs spike | Medium | Low | Lifecycle policies, monitoring alerts |

---

## Decision

**Selected Option**: imgproxy (Self-Hosted)

**Approved by**:
- [ ] @Architect
- [ ] @TechLead
- [ ] @DevOps
- [ ] @Security

---

## References

- [imgproxy Documentation](https://docs.imgproxy.net/)
- [imgproxy GitHub](https://github.com/imgproxy/imgproxy)
- [Imageflow GitHub](https://github.com/imazen/imageflow)
- [ImageKit Documentation](https://imagekit.io/docs/)
- [Cloudinary Documentation](https://cloudinary.com/documentation)
- [B2X Product Vision](../.ai/requirements/PRODUCT_VISION.md)
- [B2X Technical Requirements](../.ai/requirements/TECHNICAL_REQUIREMENTS.md)

---

**Agents**: @Architect, @SARAH | Owner: @Architect
