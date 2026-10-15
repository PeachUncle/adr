## ADR 012: Email Service — SendGrid for Transactional Mail

### Context
We needed a reliable way to send transactional emails—specifically **team-invite messages**—without maintaining our own SMTP infrastructure. Previous ad-hoc approaches (local SMTP, app server relays) led to **deliverability issues**, lack of analytics, and **manual compliance** overhead. We also wanted a solution that fits our CI/CD and secrets management workflow.

### Decision
Adopt **SendGrid** as our managed email provider for transactional messages (invitations now; password resets and notifications later).  
Integration uses SendGrid’s **v3 REST API** with **Dynamic Templates**. Secrets are stored in the app’s secret manager as **API keys** (least-privilege, mail send only). Webhooks will be used to process bounces/blocks/spam reports.

### Status
**Accepted — Implemented**

### Rationale for Change
- **Reliability & Deliverability:** Mature infrastructure, good sender reputation tooling (SPF/DKIM/DMARC guidance).
- **Simple Integration:** Well-documented REST API/SDKs; dynamic templates for localized, versioned content.
- **Generous Free Tier:** Satisfies current volume at zero/low cost; smooth path to paid tiers as we scale.
- **Observability:** Built-in event tracking (opens, clicks, bounces) for troubleshooting and product analytics.
- **Security:** Scoped API keys, domain authentication, and suppression management reduce risk.

### Consequences

**Positive:**
1. Faster feature delivery—no SMTP server to operate or tune.  
2. Improved deliverability via domain auth and provider reputation.  
3. Analytics on delivery/bounce to debug user sign-up issues.  
4. Template management separates copy/design from code deployments.

**Negative / Risks:**
1. **Vendor lock-in:** Template formats and event payloads are provider-specific.  
2. **Cost growth:** Pricing rises with volume; careful monitoring needed.  
3. **Third-party dependency:** Outages or rate limits can affect invites.  
4. **Compliance surface:** Must align with CASL/CAN-SPAM and handle PII correctly.

### Implementation Notes
- **API:** SendGrid v3 REST (Mail Send) from backend service; idempotency keys on invite sends.  
- **Templates:** Dynamic Templates with substitution data (recipient name, team, inviter, CTA URL).  
- **Secrets:** `SENDGRID_API_KEY` stored in secret manager; rotated on a 90-day cadence.  
- **Domain Auth:** Configure **SPF/DKIM** for `mail.<our-domain>`; enforce **DMARC** policy (`p=quarantine` → `p=reject` gradually).  
- **Events:** Webhook endpoint to record bounces/blocks/spam; mark invite tokens accordingly and suppress retries.  
- **Rate Limiting/Retry:** Exponential backoff on 429/5xx; per-recipient cooldown to avoid spam signals.  
- **Auditing:** Log message IDs and template versions for support/debuggability.

### Future Considerations
- **Dedicated IP** once daily volume is stable to control reputation.  
- **Multi-provider failover** (e.g., AWS SES) for critical sends; feature-flag routing.  
- **A/B testing & localization** via template variants and per-locale dynamic data.  
- **DMARC aggregate reports** monitoring; automated alerts on deliverability drops.  
- **Inbound parse** (optional) for reply-to workflows.  
- **Data retention** policy for event logs; minimize stored PI
