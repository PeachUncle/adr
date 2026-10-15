---
status: 'accepted'
date: 2025-09-23
decision-makers: voder.ai website team
consulted: startup advisors, UX research
informed: stakeholders
---

# ADR-0030: Select Interest Capture Method for Closing Moment

## Context and Problem Statement

The closing moment of our single-page website needs a method to capture interest from founders who resonate with the AI slop problem. This is critical for Release 0.5's goal of testing product-market fit and building a pipeline for future engagement.

We need to balance conversion rate (getting interested users to engage) with follow-up effectiveness (our ability to convert that interest into business). The solution must be cost-effective for an early-stage startup while providing actionable data for product development.

## Decision Drivers

- **Cost efficiency**: Minimize upfront development and ongoing operational costs
- **Follow-up effectiveness**: Maximize our ability to contact and convert interested users
- **Conversion rate**: Minimize friction for users who resonate with our message
- **Data ownership**: Maintain control over user data and relationships
- **Implementation speed**: Can be deployed quickly for Release 0.5 testing
- **Analytics capability**: Track conversion from problem recognition to interest
- **Legal compliance**: Handle privacy requirements with minimal overhead
- **Signal quality**: Distinguish serious business interest from casual curiosity

## Considered Options

### Option 1: Self-hosted Email Signup Form (Current Implementation)

Form collects email address with client-side validation and analytics tracking.

### Option 2: Contact Information Display Only

Simple display of email/LinkedIn with no data collection mechanism.

### Option 3: Third-party Form Service (Typeform/Mailchimp)

Embedded form from dedicated service provider with built-in CRM.

### Option 4: Calendar Booking Link (Calendly)

Direct link to schedule a discovery conversation.

### Option 5: Social Media Follow Buttons

Twitter/LinkedIn follow buttons for ongoing engagement.

### Option 6: Hybrid Approach (Contact + Analytics)

Display contact info but track clicks/interest via analytics events.

## Decision Outcome

Chosen option: **Option 1 - Self-hosted Email Signup Form**, because it provides the optimal balance of conversion rate, follow-up effectiveness, and cost control for our current stage.

### Rationale

**Best follow-up capability**: Email gives us direct, permission-based contact method that founders expect and check regularly. Unlike social media or contact forms, we can initiate meaningful business conversations.

**Cost-effective ownership**: Zero ongoing costs beyond analytics (already using Microsoft Clarity). No monthly SaaS fees or vendor lock-in. Data stays under our control.

**Appropriate friction level**: Email signup is low enough friction for interested founders while high enough to filter out casual browsers. Matches our target audience's business communication preferences.

**Measurable signal quality**: Email addresses are valuable business assets that people share thoughtfully. Higher quality signal than social follows or contact form submissions.

## Consequences

### Positive

- Direct communication channel with interested founders
- No ongoing vendor costs or dependencies
- Full control over user data and follow-up timing
- Analytics integration for conversion tracking
- Can iterate quickly on messaging and UX

### Negative

- Requires handling email data responsibly (privacy compliance)
- No built-in CRM features (but unnecessary at current scale)
- Success depends on our email follow-up execution
- May miss users who prefer other contact methods

## Pros and Cons of the Options

### Option 1: Self-hosted Email Signup Form Analysis

- Good, because email is the primary business communication channel for founders
- Good, because we own the relationship and data completely
- Good, because zero ongoing costs and vendor dependencies
- Good, because integrates cleanly with our existing analytics
- Bad, because requires responsible data handling practices
- Bad, because success depends entirely on our follow-up execution

### Option 2: Contact Information Display Only Analysis

- Good, because zero implementation cost and no data handling
- Good, because appears professional and established
- Bad, because very low conversion rate (most users won't reach out)
- Bad, because no way to measure or track interest levels
- Bad, because puts all burden on user to initiate contact

### Option 3: Third-party Form Service Analysis

- Good, because professional appearance and built-in CRM features
- Good, because handles compliance and data management automatically
- Bad, because $50-200/month ongoing costs for early-stage startup
- Bad, because creates vendor dependency and data portability concerns
- Bad, because requires integration work and doesn't leverage existing analytics

### Option 4: Calendar Booking Link Analysis

- Good, because pre-qualifies highly interested prospects
- Good, because directly converts to sales conversations
- Bad, because very high friction - most interested users won't book
- Bad, because creates immediate time commitment pressure
- Bad, because inappropriate for early product-market fit testing stage

### Option 5: Social Media Follow Buttons Analysis

- Good, because very low friction and familiar user pattern
- Good, because leverages existing platform engagement mechanisms
- Bad, because social follows don't indicate serious business interest
- Bad, because difficult to convert social engagement to business conversations
- Bad, because platform dependency and algorithm changes affect reach

### Option 6: Hybrid Approach Analysis

- Good, because provides multiple engagement paths for different user preferences
- Good, because maintains professional appearance while gathering analytics
- Bad, because click tracking provides less actionable data than email addresses
- Bad, because still requires users to initiate contact with uncertain conversion
- Bad, because more complex implementation for marginal benefit

## Implementation Notes

Current implementation includes:

- Email validation with user feedback
- Analytics tracking for conversion measurement
- Accessible form design with proper labeling
- Mobile-responsive styling consistent with brand
- Success messaging that sets appropriate expectations

## Confirmation

Success will be measured by:

- Email signup conversion rate from total visitors
- Quality of email follow-up conversations (engagement rate)
- Conversion from email interest to product discovery calls
- Cost per qualified lead compared to alternative approaches

## More Information

This decision supports Release 0.5's core goal of testing whether we can articulate the AI slop problem in a way that resonates with founders. Email capture provides the clearest signal of resonance while maintaining our ability to follow up and validate product-market fit through direct conversation.

The approach aligns with startup best practices of maintaining control over customer relationships while minimizing fixed costs during the validation phase.
