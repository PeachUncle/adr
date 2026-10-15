# ADR-003: Cloudflare R2 for Image Storage

## Status
**Accepted**

## Date
2025-01-XX

## Context

MyUglyRocks is a photo-heavy application where users:
- Upload photos at each tumbling stage (before/during/after)
- Share finished results to the community gallery
- Upload avatar images

### Storage Requirements
1. **Scale**: Potentially thousands of photos per active user
2. **Performance**: Fast image loading globally
3. **Cost**: Predictable pricing, ideally low egress costs
4. **Integration**: S3-compatible API for standard tooling
5. **CDN**: Built-in or easy CDN integration
6. **Reliability**: High durability for user-generated content

### Estimated Usage (MVP → Growth)
| Metric | MVP (100 users) | Growth (1K users) |
|--------|-----------------|-------------------|
| Photos/user/month | 50 | 50 |
| Avg photo size | 2 MB | 2 MB |
| Total storage | 10 GB | 100 GB |
| Monthly egress | 50 GB | 500 GB |

### Options Considered

#### Option A: Cloudflare R2
- S3-compatible API
- Zero egress fees
- Built-in CDN integration
- $0.015/GB stored/month

#### Option B: AWS S3 + CloudFront
- Industry standard
- Excellent tooling
- Egress fees: $0.09/GB
- More complex pricing

#### Option C: Vercel Blob Storage
- Native Next.js integration
- Simple setup
- Higher per-GB costs
- Vercel lock-in

#### Option D: DigitalOcean Spaces
- S3-compatible
- $5/month for 250GB + 1TB egress
- Simpler pricing than AWS

#### Option E: Self-hosted MinIO
- Full control
- Requires infrastructure management
- No built-in CDN

## Decision

**Use Cloudflare R2 for image storage with Cloudflare CDN.**

### Rationale

1. **Zero Egress Fees**: The killer feature. For a photo-heavy app, egress costs can dominate. R2's zero egress means predictable costs regardless of traffic.

2. **S3 Compatibility**: We can use the AWS SDK, making future migration straightforward if needed.

3. **Built-in CDN**: Cloudflare's global network serves images from edge locations worldwide.

4. **Simple Pricing**:
   - Storage: $0.015/GB/month
   - Class A ops (writes): $4.50/million
   - Class B ops (reads): $0.36/million
   - Egress: **$0**

5. **Custom Domain**: Easy to set up `media.myuglyrocks.com` for branded URLs.

### Cost Comparison (at 500GB storage, 2TB monthly egress)

| Provider | Storage | Egress | Total/month |
|----------|---------|--------|-------------|
| Cloudflare R2 | $7.50 | $0 | ~$10 |
| AWS S3 + CloudFront | $11.50 | $170 | ~$185 |
| DigitalOcean Spaces | $5 | $10 (overage) | ~$20 |
| Vercel Blob | ~$50 | ~$50 | ~$100 |

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       IMAGE UPLOAD FLOW                          │
└─────────────────────────────────────────────────────────────────┘

User uploads photo
        │
        ▼
┌───────────────────┐
│  ASP.NET API      │
│  /photos/upload   │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐     ┌───────────────────┐
│  Validate         │────>│  Upload Original  │
│  • File type      │     │  to R2            │
│  • File size      │     │  /cycles/{id}/... │
│  • Dimensions     │     └─────────┬─────────┘
└───────────────────┘               │
                                    ▼
                          ┌───────────────────┐
                          │  Queue Background │
                          │  Job (Hangfire)   │
                          └─────────┬─────────┘
                                    │
                          ┌─────────▼─────────┐
                          │  Generate Sizes   │
                          │  • thumb: 200px   │
                          │  • medium: 600px  │
                          │  • large: 1200px  │
                          └─────────┬─────────┘
                                    │
                          ┌─────────▼─────────┐
                          │  Upload Variants  │
                          │  to R2            │
                          └───────────────────┘
```

### Bucket Structure

```
myuglyrocks-media/
├── avatars/
│   └── {userId}/
│       └── avatar.{ext}
│
├── cycles/
│   └── {cycleId}/
│       └── stages/
│           └── {stageRunId}/
│               ├── {photoId}_original.{ext}
│               ├── {photoId}_large.jpg
│               ├── {photoId}_medium.jpg
│               └── {photoId}_thumb.jpg
│
└── posts/
    └── {postId}/
        └── {photoId}.jpg    # Reference to stage photo
```

### URL Pattern

```
https://media.myuglyrocks.com/cycles/{cycleId}/stages/{stageId}/{photoId}_medium.jpg
```

## Consequences

### Positive

- **Predictable Costs**: No surprise egress bills during traffic spikes
- **Fast Global Delivery**: Cloudflare's edge network is extensive
- **S3 Compatibility**: Easy to use existing SDKs and tools
- **Simple Setup**: Single service for storage + CDN
- **No Vendor Lock-in**: S3-compatible means easy migration

### Negative

- **Cloudflare Ecosystem**: While S3-compatible, some Cloudflare-specific features
- **Less Mature than S3**: Fewer third-party integrations and less documentation
- **Image Transformations**: No built-in transforms (need to generate sizes ourselves)
- **Bandwidth Limits**: Free tier has some limits on transform operations

### Implementation Details

#### SDK Usage

```csharp
// Use AWS SDK with R2 endpoint
var credentials = new BasicAWSCredentials(accessKeyId, secretAccessKey);
var config = new AmazonS3Config
{
    ServiceURL = "https://{account_id}.r2.cloudflarestorage.com"
};
var s3Client = new AmazonS3Client(credentials, config);
```

#### Image Processing

We'll use **ImageSharp** for .NET to generate image variants:

```csharp
public async Task ProcessPhotoAsync(Guid photoId, Stream original)
{
    using var image = await Image.LoadAsync(original);

    // Generate variants
    var sizes = new[] { (200, "thumb"), (600, "medium"), (1200, "large") };

    foreach (var (maxDimension, suffix) in sizes)
    {
        image.Mutate(x => x.Resize(new ResizeOptions
        {
            Size = new Size(maxDimension, maxDimension),
            Mode = ResizeMode.Max
        }));

        await UploadToR2Async(photoId, suffix, image);
    }
}
```

#### Caching Strategy

| Asset Type | Cache-Control | Notes |
|------------|---------------|-------|
| Original photos | private, max-age=0 | Not served directly |
| Generated variants | public, max-age=31536000 | Immutable (ID in URL) |
| Avatars | public, max-age=86400 | 1 day cache, invalidate on change |

## Alternatives Rejected

### AWS S3 + CloudFront
Rejected primarily due to egress costs. For a photo-sharing app, egress can easily become the dominant cost. At our projected usage, S3+CloudFront would cost 10-20x more than R2.

### Vercel Blob Storage
Rejected due to higher costs and Vercel lock-in. While integration with Next.js is seamless, photos are uploaded/managed from our ASP.NET backend, not Next.js.

### Self-hosted MinIO
Rejected because we don't want to manage storage infrastructure. The operational overhead of maintaining durable, globally-distributed storage is not worth the cost savings for this project.

## Migration Path

If we need to migrate away from R2:
1. All URLs are abstracted behind our API
2. S3-compatible API means existing code works with AWS/DigitalOcean
3. Can run parallel storage during migration
4. Update DNS to point to new CDN

## Related Decisions
- [ADR-001-database.md](./ADR-001-database.md) - Photo metadata stored in PostgreSQL

## References
- [Cloudflare R2 Documentation](https://developers.cloudflare.com/r2/)
- [R2 Pricing](https://developers.cloudflare.com/r2/pricing/)
- [SixLabors ImageSharp](https://docs.sixlabors.com/articles/imagesharp/)
