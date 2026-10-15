---
status: 'accepted'
date: 2025-09-24
decision-makers: voder.ai website team
consulted: startup advisors, technical team
informed: stakeholders
---

# ADR-0032: Switch from Vercel to Netlify for Integrated Form Handling

## Context and Problem Statement

Our current hosting setup creates a critical architectural inconsistency that blocks email capture functionality:

- **ADR-0026**: Site hosted on Vercel for Vite optimization
- **ADR-0031**: Chose Netlify Forms for email capture (superseded)
- **Reality**: Netlify Forms only works on Netlify-hosted sites

This fundamental platform incompatibility means our email signup form appears functional but doesn't actually capture emails for follow-up, completely undermining Release 0.5's core goal of testing product-market fit through founder engagement.

The current form implementation includes a comment "Simulate form submission" confirming no actual email storage occurs. This represents a critical business blocker that requires immediate architectural resolution.

## Decision Drivers

- **Critical Business Impact**: Email capture is essential for Release 0.5 validation
- **Architectural Consistency**: Form handling must work with hosting platform
- **Implementation Simplicity**: Minimize complexity while enabling functionality
- **Deployment Control**: Maintain quality gates and GitHub Actions workflow (ADR-0029)
- **Cost Efficiency**: Early-stage startup budget constraints
- **Timeline Urgency**: Release 0.5 requires immediate resolution

## Considered Options

### Option 1: Switch to Netlify Hosting + Forms

Move hosting to Netlify to enable built-in form handling while maintaining GitHub Actions deployment control.

### Option 2: Stay on Vercel + Custom Serverless Solution

Build custom email capture using Vercel serverless functions + external database (Airtable/Supabase).

### Option 3: Third-party Form Service

Use platform-agnostic form service (Formspree) that works with any hosting.

### Option 4: Email Marketing Platform Integration

Direct integration with email marketing service (ConvertKit) bypassing form storage.

## Decision Outcome

Chosen option: **Option 1 - Switch to Netlify Hosting + Forms**, because it provides the optimal balance of architectural consistency, implementation simplicity, and functionality while preserving our deployment control requirements.

### Rationale

**Architectural Consistency**: Eliminates the fundamental platform incompatibility by hosting and form handling on the same platform, ensuring email capture actually works.

**Implementation Simplicity**: Requires only deployment configuration changes and adding `data-netlify="true"` to existing form - zero custom code needed.

**Maintains Deployment Control**: Can continue using GitHub Actions with Netlify CLI, preserving all quality gates and deployment workflow benefits from ADR-0029.

**Superior Form Handling**: Netlify Forms provides professional email capture with dashboard access, CSV export, and webhook integration - better than custom solutions.

**Cost Effective**: Netlify free tier (300 build minutes, 100GB bandwidth) is more generous than Vercel and sufficient for validation phase.

**Future Flexibility**: Maintains data ownership with easy export to email marketing tools when ready to scale.

### Consequences

- Good, because resolves critical email capture functionality immediately
- Good, because eliminates architectural inconsistency between hosting and forms
- Good, because maintains all deployment control and quality gate benefits
- Good, because Netlify free tier is more generous than Vercel (300 vs 100 build minutes)
- Good, because built-in form handling is more reliable than custom solutions
- Good, because preserves GitHub Actions deployment workflow with minimal changes
- Bad, because requires migration effort and potential deployment downtime
- Bad, because loses Vercel's optimized Vite integration (but difference likely minimal for single-page site)
- Bad, because supersedes previous hosting decision and investment

## Implementation Plan

### Phase 1: Netlify Setup

1. Create Netlify account and connect to GitHub repository
2. Configure build settings (build command: `npm run build`, publish directory: `dist`)
3. Set up custom domain (voder.ai) with DNS configuration
4. Test basic deployment and site accessibility

### Phase 2: GitHub Actions Migration

1. Update deployment workflow to use Netlify CLI instead of Vercel CLI
2. Replace `VERCEL_TOKEN` secret with `NETLIFY_AUTH_TOKEN`
3. Update deployment commands from `vercel --prod` to `netlify deploy --prod`
4. Maintain all quality gates and verification steps

### Phase 3: Form Integration

1. Add `data-netlify="true"` attribute to existing form element
2. Update form submission handler to allow actual form submission
3. Remove `event.preventDefault()` and "simulate" comment
4. Maintain existing client-side validation and analytics tracking

### Phase 4: Validation and Cutover

1. Test email submissions appear in Netlify dashboard
2. Verify CSV export functionality for email lists
3. Confirm analytics tracking (Microsoft Clarity) still works
4. Update DNS to point to Netlify
5. Monitor deployment and email capture functionality

## Confirmation

Success will be measured by:

- Site successfully deployed and accessible at <https://voder.ai>
- Email addresses captured and accessible via Netlify dashboard
- CSV export functionality working for email campaign preparation
- Maintained Microsoft Clarity conversion tracking
- GitHub Actions deployment workflow functioning with quality gates
- Zero downtime during migration process
- All existing functionality preserved

## Superseded Decisions

This decision **supersedes ADR-0026** (Use Vercel for Static Site Deployment) due to the discovery of fundamental incompatibility with required email capture functionality.

While ADR-0026's rationale for Vercel's superior Vite integration remains valid, the business-critical need for working email capture outweighs the performance optimization benefits, especially for a simple single-page validation site.

## More Information

This decision resolves the critical architectural inconsistency that prevents Release 0.5 from achieving its primary validation goals. The email capture functionality is essential for testing product-market fit through founder engagement and follow-up conversations.

Netlify's integrated approach (hosting + forms) eliminates the complexity of managing multiple platforms while providing superior email handling capabilities compared to custom solutions. The migration preserves all deployment control benefits while enabling the core business functionality needed for successful validation.

The decision prioritizes business functionality over technical optimization, recognizing that working email capture is more valuable than marginal Vite build performance improvements during the validation phase.
