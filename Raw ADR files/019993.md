---
status: 'superseded by ADR-0032'
date: 2025-09-24
decision-makers: voder.ai website team
consulted: startup advisors, technical team
informed: stakeholders
---

# ADR-0031: Implement Email Capture Technical Solution

## Context and Problem Statement

The current email signup form only sends analytics events to Microsoft Clarity but doesn't actually store email addresses in any accessible way for follow-up outreach. This creates a critical gap between our interest capture strategy (ADR-0030) and our ability to execute on that strategy.

We need a technical solution that actually captures and stores email addresses in a way that enables us to contact interested founders, while balancing cost, implementation complexity, and follow-up effectiveness for an early-stage startup.

## Decision Drivers

- **Follow-up Capability**: Must enable export/access to email addresses for outreach campaigns
- **Implementation Cost**: Minimize upfront development time and complexity
- **Ongoing Cost**: Startup budget constraints require cost-effective solution
- **Data Ownership**: Prefer to maintain control over customer relationships and data
- **Deployment Speed**: Must be deployable quickly for Release 0.5 testing
- **Privacy Compliance**: Handle basic GDPR/privacy requirements responsibly
- **Analytics Integration**: Maintain existing Microsoft Clarity conversion tracking
- **Export Capability**: Easy export to email marketing tools when needed

## Considered Options

### Option 1: Netlify Forms (Static Site Form Handling)

Built-in form handling provided by Netlify hosting platform.

### Option 2: Serverless Function + Airtable (Hybrid Approach)

Custom Vercel serverless function storing emails in Airtable database.

### Option 3: Email API Service (Formspree)

Third-party service specializing in form submissions and email collection.

### Option 4: Email Marketing Service (ConvertKit/Mailchimp Embedded)

Direct integration with professional email marketing platform.

### Option 5: Backend Database Service (Supabase)

Full database solution with API for email storage and management.

### Option 6: Google Sheets + Apps Script

Serverless function writing emails directly to Google Sheets.

## Decision Outcome

Chosen option: **Option 1 - Netlify Forms**, because it provides the optimal balance of zero implementation cost, immediate deployment capability, and adequate follow-up functionality for our current validation stage.

### Rationale

**Zero implementation complexity**: Requires only adding `data-netlify="true"` to existing form HTML. No backend development, serverless functions, or API integrations needed.

**Immediate deployment**: Can be deployed in minutes without additional infrastructure setup or configuration.

**Cost-effective**: Completely free for up to 100 submissions/month (sufficient for Release 0.5 validation), then $19/month for higher volumes.

**Adequate follow-up capability**: Provides CSV export of all form submissions, email notifications, and webhook integration for future automation needs.

**Data accessibility**: All submissions accessible via Netlify dashboard with export capabilities. Easy migration to dedicated email marketing tools when ready to scale.

**Maintains analytics**: Preserves existing Microsoft Clarity tracking while adding actual email storage capability.

### Consequences

- Good, because enables immediate email collection with zero development overhead
- Good, because provides foundation for email follow-up campaigns and customer outreach
- Good, because free tier covers validation phase with clear pricing for scale
- Good, because maintains data ownership while providing professional handling
- Bad, because creates vendor dependency on Netlify for email storage
- Bad, because limited automation capabilities compared to dedicated email marketing platforms
- Neutral, because will eventually need migration to dedicated email marketing platform for advanced features

### Decision Confirmation

Implementation success will be confirmed by:

- Email submissions appearing in Netlify dashboard within minutes
- Successful CSV export of submitted email addresses
- Maintained Microsoft Clarity conversion tracking
- Ability to conduct email outreach campaigns using exported data
- Form submission rate tracking and optimization capability

## Pros and Cons of the Options

### Option 1: Netlify Forms Analysis

Zero-configuration form handling built into hosting platform.

- Good, because requires absolutely zero backend development or infrastructure setup
- Good, because free tier (100 submissions/month) covers validation phase adequately
- Good, because provides instant email notifications and dashboard access to submissions
- Good, because offers CSV export for easy migration to email marketing tools
- Good, because includes spam protection and basic analytics out of the box
- Bad, because creates hosting platform dependency for email functionality
- Bad, because limited automation compared to dedicated email marketing solutions
- Bad, because pricing ($19/month) becomes significant at higher submission volumes

### Option 2: Serverless Function + Airtable Analysis

Custom Vercel function storing emails in Airtable database.

- Good, because provides full control over data handling and processing logic
- Good, because Airtable offers excellent data management and export capabilities
- Good, because free tiers on both Vercel and Airtable cover significant usage
- Good, because enables custom automation and integration possibilities
- Bad, because requires serverless function development and deployment
- Bad, because adds infrastructure complexity and potential points of failure
- Bad, because requires managing Airtable API keys and authentication
- Bad, because longer implementation timeline conflicts with Release 0.5 urgency

### Option 3: Email API Service (Formspree) Analysis

Dedicated form-to-email service with storage and management features.

- Good, because specifically designed for form submissions and email collection
- Good, because provides professional email handling and spam protection
- Good, because offers webhook integrations for advanced automation
- Good, because includes email validation and duplicate detection
- Bad, because requires monthly subscription cost ($8-19/month) from day one
- Bad, because creates vendor dependency for core business functionality
- Bad, because limited customization compared to self-hosted solutions
- Bad, because another service to manage and integrate with existing analytics

### Option 4: Email Marketing Service (ConvertKit) Analysis

Direct integration with professional email marketing platform.

- Good, because provides comprehensive email marketing capabilities from the start
- Good, because designed specifically for founder/business audience outreach
- Good, because includes automation, segmentation, and campaign analytics
- Good, because handles compliance and deliverability professionally
- Bad, because significant monthly cost ($29+/month) inappropriate for validation stage
- Bad, because over-engineering for current simple email collection needs
- Bad, because requires learning complex platform before simple email outreach
- Bad, because high switching costs if platform doesn't meet needs

### Option 5: Backend Database Service (Supabase) Analysis

Full database solution with authentication and API capabilities.

- Good, because provides complete control over data structure and access patterns
- Good, because scalable solution that could support entire application backend
- Good, because free tier supports significant usage with generous limits
- Good, because PostgreSQL database enables complex queries and data analysis
- Bad, because massive over-engineering for simple email collection requirement
- Bad, because requires substantial backend development and API implementation
- Bad, because adds operational complexity for database management and backups
- Bad, because long implementation timeline conflicts with immediate deployment needs

### Option 6: Google Sheets + Apps Script Analysis

Serverless function writing emails to Google Sheets spreadsheet.

- Good, because leverages familiar Google Sheets interface for data management
- Good, because free solution with essentially unlimited storage for email addresses
- Good, because easy sharing and collaboration on email lists with team members
- Good, because simple export capabilities to email marketing platforms
- Bad, because requires Apps Script development and deployment complexity
- Bad, because Google Sheets not designed for high-volume or high-frequency writes
- Bad, because limited API rate limits could impact form submission reliability
- Bad, because unprofessional data storage solution for customer information

## Implementation Notes

Implementation steps:

1. Add `data-netlify="true"` attribute to existing form element in `src/app.ts`
2. Add hidden input field with form name for Netlify identification
3. Update form submission handler to allow actual form submission after validation
4. Verify email submissions appear in Netlify dashboard
5. Test CSV export functionality and email notification setup
6. Maintain existing Microsoft Clarity tracking for conversion analytics

Current form styling and validation logic will be preserved, with only minimal changes to enable Netlify form processing.

## Confirmation

Success will be measured by:

- Email addresses successfully captured and accessible via Netlify dashboard
- CSV export functionality working for email list management
- Maintained conversion tracking and analytics via Microsoft Clarity
- Ability to conduct follow-up email campaigns using exported addresses
- Zero deployment issues or form submission failures

## More Information

**SUPERSEDED BY ADR-0032**: This decision has been superseded due to the hosting platform migration from Vercel to Netlify (ADR-0032). The new Netlify hosting enables the originally planned Netlify Forms implementation to work as designed, resolving the critical architectural inconsistency.

ADR-0032 implements the exact email capture approach originally specified in this decision (Netlify Forms with `data-netlify="true"`) but within the context of compatible Netlify hosting rather than incompatible Vercel hosting.

---

**Original Decision Context** (superseded):

This decision supports Release 0.5's core goal of testing whether we can articulate the AI slop problem in a way that resonates with founders. Email capture provides the clearest signal of resonance while maintaining our ability to follow up and validate product-market fit through direct conversation.

The approach aligns with startup best practices of maintaining control over customer relationships while minimizing fixed costs during the validation phase.
