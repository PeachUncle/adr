---
status: 'superseded by ADR-0032'
date: 2025-09-24
decision-makers: Product Owner, Development Team
consulted: DevOps Engineers, Site Reliability Engineers
informed: Project Stakeholders
---

# Use Vercel DNS for voder.ai Domain Management

> **⚠️ SUPERSEDED**: This decision has been superseded by [ADR-0032: Switch from Vercel to Netlify for Integrated Form Handling](0032-switch-from-vercel-to-netlify-for-integrated-form-handling.accepted.md). The project has switched to Netlify hosting, which will handle domain and DNS management through Netlify's infrastructure.

## Context and Problem Statement

The voder.ai domain is registered with Namecheap and needs DNS configuration to point to Vercel for the static website deployment. We must choose a DNS provider that offers reliable performance, security features, and ease of management for our production website.

The domain currently uses Namecheap's default nameservers (dns1.registrar-servers.com, dns2.registrar-servers.com) and requires an A record pointing to Vercel's IP (76.76.21.21) to complete the deployment.

## Decision Drivers

- DNS resolution performance and global distribution critical for website speed
- Reliability and uptime requirements for production website availability
- Security features needed to protect against DNS-based attacks
- Cost considerations for startup budget constraints
- Management complexity and ease of configuration
- Integration capabilities with Vercel deployment platform
- Analytics and monitoring features for DNS performance tracking
- Future scalability for additional domains and subdomains

## Considered Options

- Namecheap Basic DNS
- Cloudflare DNS
- Vercel DNS
- Amazon Route 53
- Google Cloud DNS

## Decision Outcome

Chosen option: "Vercel DNS", because it provides seamless integration with our Vercel deployment platform, eliminates the need for third-party DNS configuration, and simplifies the deployment workflow while maintaining professional-grade DNS performance.

### Consequences

- Good, because seamless integration with Vercel deployment platform eliminates configuration complexity
- Good, because automatic optimization for Vercel-hosted sites with no manual DNS record management
- Good, because unified management within Vercel dashboard reduces operational overhead
- Good, because automatic SSL certificate management and domain verification
- Good, because eliminates dependency on additional third-party services
- Good, because Vercel's global edge network provides reliable DNS performance
- Good, because no additional cost beyond domain registration
- Neutral, because DNS features limited to Vercel ecosystem requirements
- Bad, because vendor lock-in to Vercel platform for DNS management
- Bad, because fewer advanced DNS features compared to specialized providers like Cloudflare
- Bad, because less flexibility for future non-Vercel deployments

### Confirmation

DNS configuration success confirmed by:

- voder.ai domain automatically configured in Vercel DNS after nameserver change
- SSL certificate issued automatically by Vercel after DNS verification
- Website loads at <https://voder.ai> with Vercel's optimized routing
- DNS propagation completed within 24 hours globally
- Vercel dashboard showing domain status as verified and active

## Pros and Cons of the Options

### Cloudflare DNS

Industry-leading DNS service with comprehensive security and performance features.

- Good, because global Anycast network with 200+ data centers provides fastest resolution
- Good, because free tier includes DDoS protection, DNS filtering, and security features
- Good, because excellent Vercel integration and automatic SSL optimization
- Good, because comprehensive DNS analytics and performance monitoring included
- Good, because automatic IPv6 support and modern DNS features (DNSSEC, CAA records)
- Good, because can add CDN, WAF, and performance features later without changing DNS
- Good, because professional-grade DNS management interface with bulk operations
- Good, because 100% uptime SLA and enterprise-grade infrastructure
- Neutral, because free tier sufficient for current needs with clear upgrade path
- Neutral, because requires changing nameservers from Namecheap (one-time setup)
- Bad, because advanced features may tempt over-engineering for simple static site
- Bad, because dependency on Cloudflare service availability

### Namecheap Basic DNS

Default DNS service included with domain registration.

- Good, because already configured and requires no additional setup
- Good, because no dependency on third-party DNS provider
- Good, because included free with domain registration
- Good, because simple interface sufficient for basic DNS records
- Good, because direct integration with domain registrar for unified management
- Neutral, because adequate performance for basic website hosting needs
- Neutral, because supports all standard DNS record types needed for Vercel
- Bad, because limited global distribution compared to specialized DNS providers
- Bad, because no advanced security features (DDoS protection, DNS filtering)
- Bad, because no DNS analytics or performance monitoring
- Bad, because slower DNS resolution from many global locations
- Bad, because no automatic security optimizations or modern DNS features

### Amazon Route 53

AWS's enterprise DNS service with advanced features and AWS integration.

- Good, because highly reliable with 100% uptime SLA
- Good, because excellent performance with global edge locations
- Good, because advanced features like health checks and traffic routing
- Good, because tight integration with AWS services for future expansion
- Good, because programmatic DNS management via API and Infrastructure as Code
- Good, because comprehensive monitoring and logging capabilities
- Neutral, because pay-per-query pricing model predictable for static sites
- Neutral, because professional-grade features suitable for enterprise needs
- Bad, because overkill complexity for simple static website deployment
- Bad, because costs approximately $0.50/month per hosted zone plus query charges
- Bad, because requires AWS account setup and learning AWS-specific concepts
- Bad, because less intuitive interface compared to specialized DNS providers

### Google Cloud DNS

Google's enterprise DNS solution with global infrastructure.

- Good, because reliable infrastructure with Google's global network
- Good, because competitive performance with global Anycast
- Good, because integration with Google Cloud services
- Good, because programmatic management via API and Terraform
- Good, because comprehensive logging and monitoring in Google Cloud Console
- Neutral, because pay-per-zone and per-query pricing model
- Neutral, because enterprise-focused features and interface
- Bad, because unnecessary complexity for static website hosting
- Bad, because costs approximately $0.20/month per zone plus query charges
- Bad, because requires Google Cloud account and billing setup
- Bad, because less specialized for web performance compared to Cloudflare
- Bad, because limited free tier compared to other options

### Vercel DNS

Vercel's integrated DNS service optimized for Vercel deployments.

- Good, because seamless integration with Vercel deployment platform
- Good, because automatic configuration and optimization for Vercel sites
- Good, because unified management within Vercel dashboard eliminates complexity
- Good, because automatic SSL certificate management and domain verification
- Good, because no additional cost beyond Vercel hosting
- Good, because Vercel's global edge network provides reliable performance
- Good, because eliminates need for third-party DNS service dependencies
- Good, because optimal routing and performance for Vercel-hosted content
- Neutral, because DNS features focused on web hosting rather than advanced enterprise needs
- Neutral, because performance adequate for most static website requirements
- Bad, because limited to Vercel ecosystem (vendor lock-in)
- Bad, because fewer advanced DNS features (no DDoS protection, limited analytics)
- Bad, because less flexibility for future non-Vercel deployments
- Bad, because newer service with less proven track record than specialized DNS providers

## More Information

This decision supports the requirement for custom domain configuration in the DEV-DEPLOY story. Vercel DNS provides the optimal integration with our Vercel deployment platform while eliminating the complexity of third-party DNS configuration and reducing operational overhead.

The choice enables seamless domain management within the existing Vercel workflow while maintaining professional-grade DNS reliability for our validation phase and beyond.

Migration steps:

1. Update nameservers at Namecheap to Vercel DNS (ns1.vercel-dns.com, ns2.vercel-dns.com)
2. Verify DNS propagation and automatic Vercel domain verification
3. Confirm HTTPS certificate issued automatically by Vercel
4. Test website accessibility at <https://voder.ai>
5. Monitor DNS performance through Vercel dashboard
