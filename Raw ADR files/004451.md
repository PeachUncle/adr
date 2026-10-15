# ADR 0001 — Project Naming, Jurisdiction & Minimum Age

**Date:** 2024-12-04  
**Status:** accepted

## Context

Ursine Arcana is a mobile social/hookup application targeting the furry, pup-play, and fetish communities. The app handles adult content in private contexts and facilitates connections between consenting adults.

**Target Regions:**

- Phase 1: South Africa
- Phase 2: European Union, United States

**South Africa Regulatory Landscape:**

- **POPIA**: Comprehensive data protection law with R10M penalties. Sexual orientation and "sex life" are classified as "special personal information" requiring explicit consent.
- **Film and Publications Act**: Prohibits commercial distribution of X18 content online from SA-hosted sites. User-generated private content between consenting adults is not explicitly prohibited.
- **Consumer Protection Act**: Requires clear ToS, fair terms, cooling-off rights.

## Decision

1. **Project Name**: "Ursine Arcana" in all materials.

2. **Minimum Age**: 18+ enforced via:
   - Mandatory date of birth entry at registration
   - Age gate screen before content access
   - ToS confirmation of 18+ status
   - Account termination for underage users

3. **Age Verification (MVP)**: Self-declaration. Enhanced verification deferred to future ADR based on regulatory changes.

4. **POPIA Compliance (Phase 1)**:
   - Explicit opt-in consent for all data collection
   - Special consent for "sex life" data (kink preferences, tribes, position, looking for)
   - Privacy policy with full POPIA disclosures
   - Data subject access request mechanism
   - Account deletion with full data erasure
   - Breach notification procedures
   - Data retention policy (delete inactive accounts after 2 years)

5. **Content Policy (South Africa)**:
   - Profile images: SFW only (no nudity, no explicit content)
   - Chat images: NSFW allowed between consenting adults (private)
   - No public pornographic content anywhere in app
   - All images pass automated moderation; NSFW flagged for review

6. **Phase 2 Compliance**: Separate ADRs for GDPR (EU) and US state laws.

## Consequences

**Positive:**

- Clear legal foundation for SA launch
- POPIA compliance from day one
- Content policy aligns with FPA requirements

**Negative:**

- Self-declaration age verification is not foolproof
- "Special personal information" consent adds friction to onboarding
- Private NSFW content requires robust moderation

**Risks:**

- FPA interpretation could change; monitor regulatory guidance
- POPIA enforcement is increasing; must maintain compliance
