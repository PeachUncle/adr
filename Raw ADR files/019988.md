---
status: 'superseded by ADR-0032'
date: 2025-09-24
decision-makers: voder.ai website team
consulted: startup advisors, technical team
informed: stakeholders
---

# Use Vercel for Static Site Deployment

## Context and Problem Statement

The voder.ai website needs to be deployed to a publicly accessible URL for founder validation testing. We need a static hosting platform that provides automatic deployment, custom domain support, SSL certificates, and reliable performance for our Vite-built static site.

## Decision Drivers

- Automatic deployment from Git main branch required for development workflow
- Custom domain support needed for professional branding (voder.ai)
- SSL certificate configuration must be automatic and maintained
- Site performance critical for user experience (sub-2 second load times)
- Development team needs deployment status visibility and monitoring
- Cost considerations for startup budget (need free tier for validation phase)
- Long-term pricing scalability as product grows beyond validation
- Integration with existing GitHub-based development workflow

## Considered Options

- Vercel
- Netlify
- GitHub Pages
- AWS S3 + CloudFront
- Firebase Hosting

## Decision Outcome

Chosen option: "Vercel", because it provides the best balance of automatic deployment, performance optimization, custom domain management, and developer experience for our Vite-based static site deployment needs.

### Consequences

- Good, because automatic deployment from GitHub with zero configuration required
- Good, because excellent Vite integration with optimized build and caching
- Good, because automatic SSL certificate management for custom domains
- Good, because global CDN with edge optimization improves performance
- Good, because free tier (100GB bandwidth, 100 serverless function invocations) sufficient for validation phase
- Good, because clear upgrade path ($20/month Pro tier with 1TB bandwidth when needed)
- Good, because comprehensive deployment monitoring and status dashboard
- Good, because serverless functions available if needed for future enhancements
- Bad, because vendor lock-in to Vercel platform and pricing model
- Bad, because Pro tier required for team collaboration features ($20/month/member)
- Bad, because bandwidth costs can scale significantly with high traffic ($40 per 100GB over limit)
- Bad, because limited control over server configuration compared to self-hosted options

### Confirmation

Deployment success confirmed by:

- Site accessible at <https://voder.ai> with valid SSL certificate
- Automatic deployment triggered on main branch commits
- Site loads under 2 seconds from multiple global locations
- Deployment status visible in Vercel dashboard and GitHub integration
- Custom domain properly configured with DNS pointing to Vercel

## Pros and Cons of the Options

### Vercel

Excellent integration with modern frontend frameworks and Git-based workflows.

- Good, because zero-configuration deployment for Vite projects
- Good, because automatic preview deployments for pull requests
- Good, because global CDN with edge optimization built-in
- Good, because automatic SSL certificate management
- Good, because excellent custom domain support with DNS management
- Good, because comprehensive analytics and performance monitoring
- Good, because serverless functions support for future API needs
- Neutral, because free tier has bandwidth limitations (100GB/month) but sufficient for validation
- Bad, because vendor lock-in with proprietary platform
- Bad, because pricing can become expensive at high scale ($20/month base + bandwidth overages)

### Netlify

Strong competitor with similar feature set and good developer experience.

- Good, because automatic deployment from Git repositories
- Good, because form handling and serverless functions included
- Good, because split testing and branch deploys built-in
- Good, because generous free tier (300 build minutes, 100GB bandwidth/month) with good performance
- Good, because custom domain and SSL certificate support
- Neutral, because good Vite support but not as optimized as Vercel
- Neutral, because Pro plan ($19/month) competitive with Vercel for team features
- Bad, because slightly more complex configuration for custom domains
- Bad, because less integrated developer experience compared to Vercel

### GitHub Pages

Simple and free option integrated with existing GitHub workflow.

- Good, because completely free for public repositories (unlimited bandwidth)
- Good, because direct integration with GitHub repositories
- Good, because automatic deployment from repository branches
- Good, because custom domain support with SSL certificates
- Neutral, because sufficient performance for basic static sites
- Neutral, because zero ongoing costs but limited to public repositories only
- Bad, because limited build customization (Jekyll-focused)
- Bad, because no serverless functions or advanced features
- Bad, because less performant global CDN compared to commercial options
- Bad, because limited deployment monitoring and analytics

### AWS S3 + CloudFront

Enterprise-grade solution with maximum control and scalability.

- Good, because highly scalable and reliable infrastructure
- Good, because complete control over configuration and optimization
- Good, because cost-effective at scale (S3 ~$0.023/GB storage, CloudFront ~$0.085/GB transfer)
- Good, because integrates with full AWS ecosystem for future needs
- Neutral, because SSL certificate management via AWS Certificate Manager (free)
- Neutral, because predictable costs but requires traffic estimation for budgeting
- Bad, because complex setup requiring significant DevOps knowledge
- Bad, because manual configuration for automatic deployment from Git
- Bad, because higher operational overhead for deployment pipeline
- Bad, because overkill complexity for simple static site deployment

### Firebase Hosting

Google's hosting solution with good performance and integration options.

- Good, because fast global CDN with good performance
- Good, because automatic SSL certificate provisioning
- Good, because integrates with Firebase ecosystem for future features
- Good, because free tier (10GB hosting, 360MB/day transfer) adequate for validation
- Neutral, because custom domain support available but less streamlined
- Neutral, because pay-as-you-scale pricing ($0.026/GB beyond free tier)
- Bad, because less optimized for modern frontend frameworks like Vite
- Bad, because more complex deployment configuration compared to Vercel/Netlify
- Bad, because limited Git integration requiring manual deployment pipeline setup

## More Information

**SUPERSEDED BY ADR-0032**: This decision has been superseded due to a critical architectural inconsistency discovered during email capture implementation. While Vercel provides excellent Vite integration and deployment experience, it cannot support Netlify Forms functionality required for Release 0.5's email capture goals.

ADR-0032 switches hosting to Netlify to enable integrated form handling while maintaining GitHub Actions deployment control and quality gates. The business-critical need for working email capture outweighs the Vite optimization benefits for our single-page validation site.

---

**Original Decision Context** (superseded):

This decision supports Release 0.5's deployment requirements by providing reliable static site hosting with automatic deployment, SSL certificate management, and global CDN distribution. The Vercel platform aligns with our Vite-based build system and GitHub-centric development workflow.

The approach balances deployment automation with cost-effectiveness during the validation phase while providing a clear scaling path for future growth.
