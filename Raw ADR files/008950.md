# ADR-001: TypeScript for Netlify Functions

## Status
Accepted

## Context
According to the organization's TECH_STACK_RULES.md, the preferred language hierarchy for backend services is:
1. Go
2. Rust  
3. Java
4. TypeScript (frontend only)

This project uses TypeScript for backend Netlify Functions, which appears to violate the established rules.

## Decision
We will use TypeScript for this WhatsApp webhook implementation on Netlify Functions.

## Rationale

### Platform Constraints
1. **Netlify Functions Requirements**: Netlify Functions natively support JavaScript/TypeScript through Node.js runtime
2. **Go Support Limitations**: While Netlify supports Go functions, they require additional build steps and have less seamless integration
3. **Development Speed**: TypeScript functions deploy instantly without compilation steps on Netlify

### Project Scope Considerations
1. **Simple Webhook**: This is a stateless webhook handler, not a complex backend service
2. **Serverless Architecture**: Functions are ephemeral and event-driven, minimizing traditional backend concerns
3. **No Database**: No complex data persistence or transactions requiring Go's performance benefits
4. **Limited Concurrency**: Webhook receives sequential events, not high-concurrency workloads

### TypeScript Benefits for This Use Case
1. **Type Safety**: Full type checking for WhatsApp API payloads
2. **Native JSON**: Seamless JSON parsing without struct definitions
3. **Ecosystem**: Direct use of Facebook's SDK if needed
4. **Netlify Integration**: First-class support in Netlify CLI and dashboard

### Compliance Justification
Per TECH_STACK_RULES.md Section 8 (Migration & Refactoring Rules):
- This is not a "complex business logic" service (Java use case)
- This is not a "high-concurrency system" (Go use case)  
- This is not a "performance-critical component" (Rust use case)
- This is a simple event handler that processes webhooks

## Consequences

### Positive
- Faster development and deployment
- Native Netlify platform support
- Simpler build pipeline
- Lower operational complexity
- Good developer experience

### Negative
- Deviates from organizational language preferences
- Potentially slower performance than Go (acceptable for webhook use case)
- Sets precedent for TypeScript backend usage (mitigated by clear scope definition)

### Mitigation
- Document this exception clearly
- Limit TypeScript usage to serverless functions only
- Consider migration to Go if:
  - Service grows beyond simple webhook handling
  - Performance becomes a concern
  - Need to integrate with other Go services

## Review
This decision should be reviewed if:
- Webhook volume exceeds 10,000 requests/minute
- Additional complex business logic is required
- Service needs to be integrated into larger Go-based architecture
- Netlify platform is replaced with container-based deployment

## References
- [TECH_STACK_RULES.md](../../.claude/TECH_STACK_RULES.md)
- [Netlify Functions Documentation](https://docs.netlify.com/functions/overview/)
- [WhatsApp Cloud API Requirements](https://developers.facebook.com/docs/whatsapp/cloud-api)

---
**Date**: 2025-08-12  
**Author**: DTC DevOps Team  
**Reviewers**: Pending