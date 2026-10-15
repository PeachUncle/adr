---
adr: 030
title: "Domain Registration and DNS Hosting Strategy"
date: 2025-10-13
status: Accepted
---

# ADR 030 — Domain Registration and DNS Hosting Strategy

Status: Accepted

Date: 2025-10-13

## Context

The PlumbingPOC project (public-facing product: CopilotForTrades.com) requires a public domain name to be pointed at our web application hosted on Netlify. We must decide where to register the domain and where to manage DNS records. This choice affects cost, flexibility, security, and day-to-day management.

Key constraints and requirements:

- Competitive registrar pricing and basic domain management features.
- High-performance DNS hosting with fast propagation and built-in HTTPS/SSL support.
- Minimizing vendor lock-in for future host migrations.
- Separation of concerns for security (domain registrar vs. hosting provider access).

## Decision

We will register the domain with Namecheap (a dedicated domain registrar) and delegate DNS management to Netlify by updating the domain's nameservers at Namecheap to Netlify's nameservers.

In short: register at Namecheap; manage DNS records in Netlify.

## Considered Options

1. Register with Namecheap and manage DNS at Namecheap
   - Register domain at Namecheap and use Namecheap DNS to create A/CNAME/TXT records pointing to Netlify.

2. Register and manage DNS with Netlify
   - Use Netlify's integrated domain registration and DNS management for the whole workflow.

3. Register with Namecheap, delegate DNS to Netlify (Chosen)
   - Register domain at Namecheap, then update Namecheap's nameservers to Netlify's nameservers so Netlify manages DNS records.

## Rationale

We selected Option 3 (register at Namecheap and delegate DNS to Netlify) because it provides the best balance of portability, operational simplicity for day-to-day DNS changes, cost-effectiveness, and security separation.

- Portability & Avoiding Vendor Lock-in
  - Keeping domain registration at a separate registrar (Namecheap) ensures the domain is not locked into Netlify. If we need to migrate hosting to Vercel, AWS, or another provider, we retain full control over the domain and can change DNS delegation without transferring registration.

- Leverage Platform-Specific Benefits
  - Netlify provides a high-performance DNS platform and tight integration with Netlify Hosts (automatic SSL provisioning, simple site-to-record mapping, and convenient UI for DNS records). Registering at Namecheap (which typically has lower registration costs and a focused registrar feature set) plus using Netlify DNS yields the advantages of both.

- Security: Separation of Concerns
  - If a hosting account is compromised, the attacker would not automatically have control of domain registration (which remains in Namecheap). This separation reduces blast radius and provides clearer account boundaries.

- Simplicity of Day-to-Day Management (Post-Setup)
  - After initial delegation, day-to-day DNS management (adding MX/TXT records for email providers such as Resend, updating A/CNAME records, or adding verification records) is handled in the Netlify dashboard alongside site deploys. This centralizes operational changes for site owners and ops engineers.

## Consequences

Positive:

- Increased flexibility and portability — the domain can be re-pointed to another provider without transferring registration.
- Ability to leverage Netlify's DNS performance, automatic TLS, and UI-driven DNS changes.
- Security benefit from separating registrar account credentials from hosting credentials.

Negative:

- Requires managing credentials for two accounts (Namecheap and Netlify) and ensuring both use strong authentication (preferably MFA).
- Slightly more complex initial setup (nameserver delegation + verification) compared to an all-in-one registrar+host approach.

## Implementation Notes / Next Steps

1. Purchase domain at Namecheap using the organizational account.
2. Configure Nameserver Delegation in Namecheap to the Netlify nameservers provided in the Netlify Domains/DNS settings.
3. In Netlify, add the domain (CopilotForTrades.com) to the site and verify ownership following Netlify's instructions.
4. Verify SSL provisioning and that the site serves over HTTPS.
5. Add operational docs (credentials owners, MFA requirements, registrar account contact details) to the project's secure ops documentation.
6. Add DNS change and domain transfer playbooks to `docs/OPS.md` or equivalent (include steps for rotating registrar credentials and transferring the domain if required).

## Alternatives and Revisit Conditions

- If Netlify's DNS capabilities become insufficient for our needs (e.g., advanced DNS features not supported), we may revisit and delegate DNS to a dedicated DNS provider (Cloudflare, AWS Route 53) while keeping registration at Namecheap.
- If organizational policy requires consolidation of domain registration and DNS at a single enterprise provider, revisit this ADR.

## References

- Netlify DNS documentation: https://docs.netlify.com/domains-https/netlify-dns/
- Namecheap registrar: https://www.namecheap.com/

---
Signed-off-by: Project Maintainers
