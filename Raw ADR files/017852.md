# ADR 002: Email Provider - Resend

**Date**: 2026-01-13  
**Status**: Accepted (supersedes initial AWS SES decision)

## Context

The application needs to send transactional emails:
- Email verification after registration
- Password reset links
- (Future) Notifications

Options considered:
1. **AWS SES** - Amazon's email service
2. **Resend** - Modern email API for developers
3. **SendGrid** - Twilio's email platform
4. **Mailgun** - Email API service

Initially, we chose AWS SES but later migrated to Resend.

## Decision

**Use Resend for transactional emails.**

Implementation:
```java
// Simple HTTP POST to Resend API
HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("https://api.resend.com/emails"))
    .header("Authorization", "Bearer " + apiKey)
    .header("Content-Type", "application/json")
    .POST(HttpRequest.BodyPublishers.ofString(jsonPayload))
    .build();
```

## Why Not AWS SES?

| Issue | AWS SES | Resend |
|-------|---------|--------|
| **Setup complexity** | IAM roles, policies, instance profiles, domain verification in sandbox | API key + DNS records |
| **Sandbox mode** | Starts in sandbox, must request production access | No sandbox, works immediately |
| **SDK size** | Heavy AWS SDK (~10MB) | No SDK needed (HTTP client) |
| **IAM coupling** | EC2 needs IAM role for SES access | Just an API key |
| **Terraform complexity** | 4 resources (role, policy, profile, identity) | Zero AWS resources |
| **Local development** | Needs AWS credentials or mocking | Just disable in config |

## Consequences

### Pros
- **Simpler setup**: One API key vs IAM role/policy/profile chain
- **No AWS SDK**: Uses built-in Java HTTP client
- **Better DX**: Cleaner logs, better error messages
- **Modern API**: RESTful, well-documented
- **Good free tier**: 3,000 emails/month free
- **Better deliverability**: Purpose-built for transactional email

### Cons
- **External dependency**: Not in AWS ecosystem
- **Cost at scale**: $20/month for 50k emails (vs ~$5 on SES)
- **Less control**: Fewer advanced features than SES

### Cost Comparison

| Volume | AWS SES | Resend |
|--------|---------|--------|
| 3,000/month | ~$0.30 | Free |
| 10,000/month | ~$1.00 | Free |
| 50,000/month | ~$5.00 | $20 |
| 100,000/month | ~$10.00 | $40 |

For a starter app, Resend's free tier is more than sufficient.

## Configuration

```yaml
# application.yml
app:
  email:
    enabled: true
    api-key: ${RESEND_API_KEY}
    from-address: noreply@yourdomain.com
```

Required DNS records for domain verification:
- TXT: `resend._domainkey` (DKIM)
- TXT: `send` (SPF)
- MX: `send` (bounce handling)
- TXT: `_dmarc` (DMARC policy)

## Migration Path

If needed, migrating back to SES or to another provider:
1. `EmailService` is the only class that knows about Resend
2. Swap implementation, keep same interface
3. Update environment variable from `RESEND_API_KEY` to new provider's key

## References

- [Resend Documentation](https://resend.com/docs)
- [AWS SES Pricing](https://aws.amazon.com/ses/pricing/)


