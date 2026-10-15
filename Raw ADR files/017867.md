# Architecture Decision Record – Static Website Project

**Author**: Rishwanth Perumandla  
**Date**: June 5, 2025  
**Project**: Static Website Architecture  
**Purpose**: To formally capture key architectural decisions for designing a scalable, cost-conscious, and reliable static business website.

---

## 1. Problem Context

A client needed a simple yet professionally architected website to showcase services, provide basic lead capture, and represent the business brand. The expected traffic was initially low (<100 users/day), but growth was anticipated.

This was not just a development exercise — it was an opportunity to define a **foundation that won’t break** as traffic grows or the site evolves into a larger platform.

---

## 2. Key Constraints

- Budget: <$10/month to start
- Technical Team: Low DevOps overhead, minimal infrastructure maintenance
- Content Type: Mostly static pages, no dynamic user sessions or dashboards
- Uptime Target: >99.9% availability
- SEO and Page Speed: High priority
- Image-heavy sections (banners, services, team, etc.)

---

## 3. Architectural Options Considered

| Architecture Stack               | Benefits                                                                 | Drawbacks                                                              |
|----------------------------------|--------------------------------------------------------------------------|------------------------------------------------------------------------|
| Shared Hosting (e.g. Hostinger) | Cheap, simple UI, includes domain + SSL                                 | Poor scalability, unpredictable speed, weak observability              |
| AWS S3 + CloudFront              | Edge caching, serverless, scalable, minimal maintenance, secure         | No backend logic (e.g. forms require external integrations)            |
| AWS Lightsail + WordPress        | CMS flexibility, flat monthly pricing, quick launch                      | Limited customization, not built for scale                             |
| AWS Elastic Beanstalk (WP stack)| Managed infra, scalability, versioned deployments, auto recovery        | More expensive (~$40–50/mo), setup and teardown require expertise      |
| EC2 + RDS (manual)               | Full control, modular, production-grade                                  | High setup, ongoing sysadmin work, poor ROI for low-traffic workloads |

---

## 4. Decision: S3 + CloudFront + Route 53

I chose to architect the solution using:

- **S3**: For storing and serving static assets (HTML, CSS, JS, images)
- **CloudFront**: For edge caching, improved global load speed, and traffic burst handling
- **Route 53**: For DNS management with domain-level routing
- **AWS Certificate Manager (ACM)**: For free HTTPS

### Rationale:

- **Scalability**: Virtually infinite — from 10 users/day to millions/month without re-architecture
- **Performance**: Global low-latency delivery through CloudFront's edge locations
- **Security**: S3 public access blocked, HTTPS enforced via CloudFront + ACM
- **Cost-Efficiency**: Hosting and traffic delivery estimated to stay well under $1–2/month for <10GB traffic
- **Zero Maintenance**: No patching, no updates, no instance monitoring

---

## 5. Cost Breakdown (Estimate)

| Service            | Usage Estimate                  | Monthly Cost |
|--------------------|----------------------------------|--------------|
| S3 (Storage)       | 1–3 GB                          | ~$0.07       |
| CloudFront         | 3–5 GB data out                 | ~$0.40       |
| Route 53           | 1 hosted zone + 1 domain query  | ~$0.50       |
| SSL (ACM)          | Unlimited via CloudFront        | Free         |
| **Total**          |                                  | **~$1.00**   |

---

## 6. Alternatives Preserved

Although S3 + CloudFront was chosen for this phase, I preserved alternative IaC templates and WordPress options for future migration:

- Terraform module for Lightsail WP + Route 53
- AMI-backed EC2 snapshot for full-stack WordPress deployment
- Documented upgrade path to Beanstalk or EKS for future dynamic workloads

---

## 7. Image and Asset Strategy

- Images are stored in **S3** using clean pathing with cache-busting via versioned URLs
- All image URLs served via **CloudFront**, ensuring optimized delivery
- Lazy loading enabled on the frontend to reduce LCP and improve Core Web Vitals
- Backup strategy: lifecycle policies to move infrequent assets to S3 Glacier if needed

---

## 8. Future Scaling Considerations

If traffic scales, or content needs to be updated more frequently:

- Introduce **GitHub Actions CI/CD** to auto-deploy from the main branch
- Switch to **headless CMS** (e.g., Contentful, Sanity) → use static JSON generation in CI
- Plug in **CloudFront Functions** or **Lambda@Edge** for SEO or header manipulation
- Enable **Route 53 failover + health checks** for multi-region disaster tolerance

---

## 9. Summary

This decision was made not because it's the easiest route, but because it's the **most aligned with current needs, costs, and future flexibility**.

I believe good architecture isn't overengineering — it's **just enough structure to evolve cleanly**.

**Signed:**  
Rishwanth Perumandla  
Solutions Architect  
[rishwanth.com](https://rishwanth.com)

