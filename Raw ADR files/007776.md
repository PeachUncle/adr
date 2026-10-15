# ADR: Use Amazon S3 for File Storage in Copper Print Gallery

## Date
2024-07-31

## Status
Proposed

## Context
The Copper Print Gallery system needs a reliable and scalable solution for storing and serving artwork images. Our deployment platform, Heroku, does not provide persistent file storage on its dynos. We need a file storage solution that can handle various image sizes, is cost-effective for our current small scale, and can integrate well with our Heroku-deployed application.

## Decision
We have decided to use Amazon S3 (Simple Storage Service) for file storage in the Copper Print Gallery system.

## Rationale
1. Reliability: S3 offers high durability and availability for stored objects.
2. Scalability: Can easily handle our current needs and scale as our storage requirements grow.
3. Cost-effectiveness: Pay-as-you-go pricing model is suitable for our small-scale start.
4. Integration: Well-documented SDKs available for easy integration with our application.
5. CDN Compatibility: Can be easily integrated with a CDN (e.g., Amazon CloudFront) for improved content delivery.
6. Versioning: Supports object versioning, which can be useful for tracking changes to artwork images.

## Consequences

### Positive
- Reliable and scalable storage for artwork images.
- Separation of concerns: file storage is handled independently from our application logic.
- Potential for easy CDN integration in the future.
- Backup and versioning capabilities built-in.

### Negative
- Introduces dependency on Amazon Web Services.
- Requires careful management of access keys and permissions.

### Risks
- Potential for increased costs if not managed properly as storage needs grow.
- Need to ensure proper security configurations to prevent unauthorized access.

## Implementation Notes
1. Create an Amazon S3 bucket dedicated to the Copper Print Gallery system.
2. Use the AWS SDK in our application to interact with S3.
3. Store S3 access credentials securely using Heroku Config Vars.
4. Implement server-side logic to generate pre-signed URLs for secure, time-limited access to images.
5. Set up appropriate bucket policies and access controls to ensure security.
6. Consider implementing a caching strategy to reduce S3 requests and improve performance.

## Alternatives Considered
1. Heroku Add-ons (e.g., Bucketeer, CloudCube): Provide S3-compatible storage but with potential limitations and additional costs.
2. Google Cloud Storage: Similar capabilities to S3, but S3 was chosen for its ubiquity and extensive documentation.
3. DigitalOcean Spaces: A simpler object storage solution, but S3 offers more advanced features and better integration options.

## Related Decisions
- Heroku Deployment Strategy for Copper Print Gallery
- System requirements specification

## References
- Amazon S3 Documentation: [https://docs.aws.amazon.com/s3/index.html](https://docs.aws.amazon.com/s3/index.html)
- Using AWS S3 to Store Static Assets and File Uploads: [https://devcenter.heroku.com/articles/s3](https://devcenter.heroku.com/articles/s3)
- AWS SDK for JavaScript: [https://docs.aws.amazon.com/sdk-for-javascript/](https://docs.aws.amazon.com/sdk-for-javascript/)
