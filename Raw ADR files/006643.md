# ADR-001: Front Door Premium for PCI-DSS Compliance

## Status

Accepted

## Date

2025-12-04

## Context

The e-commerce platform requires PCI-DSS compliance for payment card processing. This necessitates
Web Application Firewall (WAF) protection with managed rule sets to protect against OWASP Top 10
vulnerabilities and payment-related attacks.

### Requirements

- PCI-DSS v4.0 compliance for payment data handling
- WAF with managed OWASP Core Rule Set
- Bot protection for credential stuffing prevention
- DDoS protection at Layer 7

### Considered Alternatives

1. **Azure Front Door Standard** - $100/month with WAF, but limited rule customization
2. **Azure Front Door Premium** - $330/month with full WAF capabilities
3. **Azure Application Gateway with WAF v2** - $200+/month, regional only
4. **Third-party WAF (Cloudflare/Akamai)** - Variable cost, additional vendor

## Decision

We selected **Azure Front Door Premium** for the following reasons:

| Feature                   | Standard | Premium | Our Need         |
| ------------------------- | -------- | ------- | ---------------- |
| Managed WAF Rules         | Basic    | Full    | Full (PCI-DSS)   |
| Bot Protection            | ❌       | ✅      | Required         |
| Private Link Origins      | ❌       | ✅      | Nice to have     |
| Custom Rules              | Limited  | Full    | Required         |
| Log Analytics Integration | Basic    | Full    | Required (audit) |

### Cost Impact

- **Additional Cost**: $230/month over Standard tier
- **Annual Cost**: ~$2,760 additional
- **Justification**: PCI-DSS non-compliance risk far exceeds this cost

## Consequences

### Positive

- Full PCI-DSS WAF compliance out of the box
- Bot protection prevents automated attacks on login/checkout
- Centralized security logging for compliance audits
- Future-ready for Private Link origins if needed

### Negative

- Higher monthly cost ($330 vs $100)
- Premium tier has more complex configuration options
- Requires security team training on custom rules

### Mitigations

- Document WAF configuration in runbook
- Create alert rules for WAF blocks
- Schedule quarterly rule set updates

## References

- [Azure Front Door Pricing](https://azure.microsoft.com/pricing/details/frontdoor/)
- [PCI-DSS WAF Requirements](https://docs-prv.pcisecuritystandards.org/PCI%20DSS/Standard/PCI-DSS-v4_0.pdf)
- [Front Door WAF Documentation](https://learn.microsoft.com/azure/web-application-firewall/afds/afds-overview)
