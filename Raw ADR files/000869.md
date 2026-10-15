
# Bet Keeper Image Storage

## Context and problem statement

In BetKeeper some blob items also must be somewhere stored such as avatar images or bet confirmation images. Images should be uploaded from application and users of application should be able to fetch avatars of other users. 

## Decision drivers

- Blob sotrage for User avatars that allow to upload data from application logic and to read resource via direct resource URI. 
- It must be free including capacity and traffic ussage (less then 5GB of storage and less than 1.000.000 of monthy requests)

## Conidered options

- **Amazon S3**  
Amazon Web Services S3 storage provide public buckets with SDK tools for Node.js environment. There is 5 GB of storage size for free tier but this free tier last only 12 months. 
- **Cloudflare R2**  
Has unlimited count of requests and 10GB of storage with public buckets that can be controlled using Amazon S3 SDK. Has [free tier](https://developers.cloudflare.com/r2/pricing/#free-tier) without limitations. 


```typescript
const UserAvatar = ({ username }) => {
  const imageUrl = `https://your-cdn-domain.com/avatars/${username}.jpg`;

  return (
    <img
      src={imageUrl}
      alt={`${username}'s avatar`}
      width={100}
      height={100}
      style={{ borderRadius: '50%' }}
    />
  );
};
```

- **Google Cloud Storage**  
Free Tier includes 5 GB of Regional Storage per month, 1 GB of outbound data, and 5,000 Class A and 50,000 Class B operations monthly. New users get $300 in credits for 90 days to explore any Google Cloud product. Public Access for buckets or individual objects via signed URLs with ACLs. CDN Integration - Easily pair with Google Cloud CDN for fast global delivery and caching. Fine-grained IAM policies, encryption at rest and in transit.

```typescript
<Image
  src="https://storage.googleapis.com/your-bucket-name/user-avatars/john.jpg"
  alt="John's avatar"
  width={100}
  height={100}
/>
```

- **Netlify Blobs**  
[Netlify](https://www.netlify.com/) has free plan, though exact limits aren't always published. It's designed to support typical small-to-medium app needs. Zero Configuration - No need to set up buckets or manage access policies manually.
S3-like API: You can use getStore() and getDeployStore() to read/write blobs programmatically. Metadata Support for blobs (e.g., country, timestamp). Public Access serving blobs publicly via Netlify CDN. Secure by Default: Blobs are encrypted at rest and in transit.

```typescript
import Image from 'next/image';

export default function UserAvatar({ username }) {
  const imageUrl = `https://your-site.netlify.app/.netlify/blobs/user-avatars/${username}.jpg`;

  return (
    <Image
      src={imageUrl}
      alt={`${username}'s avatar`}
      width={100}
      height={100}
      priority
    />
  );
}
```


## Decision Outcome


📆 Date: 25.10.2025

Both Cloudflare R2 and Netlify are great solutions. 
Both are modern, developer-friendly object storage solutions with generous free tiers and CDN integration. Netlify can be setup fater but **Cloudflare R2** is better solution to save images from application hosted on Vercel. It will be working with SDK and there is no egress fees when accessing to Cloudflare CDN. Users will be able to fetch profile images via public URLs. 

[Back to top](./readme.md)  
[Previous](./03-application.md)  