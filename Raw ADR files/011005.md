# ADR-012: Email Specialist Agent Architecture

**Status:** Accepted
**Date:** 2025-11-03
**Decision Makers:** Architecture Team
**Related ADRs:** ADR-001 (Multi-agent Architecture), ADR-002 (TDD Methodology), ADR-007 (Content Manager Agent), ADR-008 (Analytics Specialist Agent), ADR-009 (Copywriter Specialist Agent), ADR-011 (Designer Specialist Agent)

## Context

The AI Marketing Director system currently has:
- **Executive Layer:** CMO Agent (strategic oversight)
- **Management Layer:** Campaign Manager, Social Media Manager, Content Manager
- **Specialist Layer:** LinkedIn Manager, Twitter Manager, Bluesky Manager, Analytics Specialist, Copywriter Specialist, SEO Specialist, Designer Specialist

The Campaign Manager, Content Manager, and Copywriter require email marketing capabilities to:
1. Create and send email campaigns for product launches, newsletters, promotions
2. Manage email templates and personalization
3. Implement A/B testing for subject lines and content
4. Segment email lists for targeted messaging
5. Track email performance (open rates, click rates, conversions)
6. Automate email workflows (drip campaigns, nurture sequences)
7. Ensure email deliverability best practices
8. Integrate with email service providers (SendGrid, Mailchimp, HubSpot)

Without an Email Specialist:
- No automated email campaign creation and delivery
- Campaign Manager cannot execute email components of campaigns
- No email performance tracking and optimization
- Manual email list management required
- Missing critical marketing automation capabilities
- No email A/B testing or personalization

## Decision

We will implement an **Email Specialist Agent** as a specialist-layer agent that:

1. **Creates email campaigns** with templates, personalization, and dynamic content
2. **Manages email delivery** through ESP integrations (SendGrid, Mailchimp, HubSpot)
3. **Implements A/B testing** for subject lines, content, and send times
4. **Segments email lists** based on demographics, behavior, and engagement
5. **Tracks email performance** with detailed analytics (opens, clicks, conversions, bounces)
6. **Automates email workflows** including drip campaigns and nurture sequences
7. **Ensures deliverability** through best practices, spam score checking, and list hygiene
8. **Manages email templates** with responsive design and brand consistency

### Architecture Design

```
┌─────────────────────────────────────────────────┐
│      Email Specialist (Specialist Layer)        │
│  - Email campaign creation & delivery           │
│  - Template management & personalization        │
│  - A/B testing & optimization                   │
│  - List segmentation & automation               │
└─────────────────────────────────────────────────┘
                      │
      ┌───────────────┼───────────────┐
      ▼               ▼               ▼
┌──────────┐   ┌──────────┐   ┌──────────┐
│Email ESP │   │  Email   │   │  Email   │
│(SendGrid)│   │Templates │   │Analytics │
│          │   │          │   │          │
└──────────┘   └──────────┘   └──────────┘
```

### Coordination Pattern

```
Campaign Manager
   ↓ (requests email campaign)
Email Specialist → [ESP, Templates, Copywriter, Designer]

Content Manager
   ↓ (requests newsletter)
Email Specialist → [Create newsletter, send to subscribers]

Copywriter Specialist
   ↓ (provides email copy)
Email Specialist → [Use copy in email template]

Designer Specialist
   ↓ (provides email header)
Email Specialist → [Include header in email template]

Analytics Specialist
   ↑ (receives email performance data)
Email Specialist → [Report opens, clicks, conversions]
```

### Supported Task Types

1. **create_email_campaign**: Create and configure email campaign
2. **send_email**: Send email to recipient list or segment
3. **schedule_email**: Schedule email for future delivery
4. **create_email_template**: Create reusable email template
5. **segment_email_list**: Segment subscribers based on criteria
6. **ab_test_email**: Create A/B test for subject lines or content
7. **track_email_performance**: Track email campaign metrics
8. **create_drip_campaign**: Create automated drip campaign workflow

### Key Characteristics

- **ESP Integration:** Integrates with SendGrid, Mailchimp, HubSpot APIs
- **Template Engine:** Responsive email templates with personalization variables
- **A/B Testing:** Statistical significance testing for email variants
- **List Management:** Segmentation, subscription management, list hygiene
- **Performance Tracking:** Real-time analytics for opens, clicks, conversions
- **Automation Workflows:** Drip campaigns, triggered emails, nurture sequences
- **Deliverability Optimization:** Spam score checking, sender reputation monitoring
- **Strategy Pattern:** Uses dictionary dispatch for task routing (zero if/elif chains)
- **Exception Wrapping:** All external API calls wrapped with `AgentExecutionError`

## Consequences

### Positive

1. **Automated email marketing:** Creates and sends campaigns at scale
2. **Multi-channel integration:** Enables email components in campaigns
3. **Performance optimization:** A/B testing improves email effectiveness
4. **Audience targeting:** List segmentation enables personalized messaging
5. **Marketing automation:** Drip campaigns and workflows reduce manual work
6. **ESP flexibility:** Can switch between email service providers
7. **Standards compliance:** Follows all coding directives (Strategy Pattern, guard clauses, full type hints, WHY/HOW documentation)

### Negative

1. **ESP costs:** Email service providers charge based on volume
2. **Deliverability complexity:** Spam filters and sender reputation require careful management
3. **Email regulations:** Must comply with CAN-SPAM, GDPR, privacy laws
4. **Template maintenance:** Email templates require testing across clients
5. **Rate limiting:** ESP APIs have rate limits and throttling

### Mitigation Strategies

1. **Cost controls:** Set daily/monthly send limits and monitor usage
2. **Deliverability monitoring:** Track bounce rates, spam complaints, sender score
3. **Compliance checks:** Automated validation for unsubscribe links, physical address
4. **Template testing:** Test templates across major email clients (Gmail, Outlook, Apple Mail)
5. **Rate limiting:** Implement exponential backoff and queue management

## Implementation Notes

### Task Delegation Pattern

```python
# Email Specialist creates email campaign
async def _create_email_campaign(self, task: Task) -> dict[str, Any]:
    """
    Create and configure email campaign.

    WHY: Enables structured email campaign creation with templates and segmentation.
    HOW: Uses ESP API to create campaign with template, list, and settings.
    """
    campaign_name = task.parameters["campaign_name"]
    template_id = task.parameters.get("template_id")
    subject_line = task.parameters["subject_line"]
    recipient_list_id = task.parameters["recipient_list_id"]

    # Guard clause: Validate ESP client is available
    if not self._esp_client:
        return {"error": "Email service provider not configured", "campaign_id": None}

    # Guard clause: Validate template exists
    if template_id and not await self._template_exists(template_id):
        return {"error": f"Template {template_id} not found", "campaign_id": None}

    try:
        # Create campaign via ESP
        campaign = await self._esp_client.create_campaign(
            name=campaign_name,
            subject=subject_line,
            template_id=template_id,
            list_id=recipient_list_id,
            from_name=self._sender_name,
            from_email=self._sender_email,
            reply_to=self._reply_to_email
        )

        # Check spam score
        spam_score = await self._check_spam_score(campaign.preview_html)

        # Validate deliverability
        deliverability_check = await self._validate_deliverability(campaign)

        return {
            "campaign_id": campaign.id,
            "campaign_name": campaign_name,
            "subject_line": subject_line,
            "recipient_count": campaign.recipient_count,
            "spam_score": spam_score,
            "deliverability_status": deliverability_check["status"],
            "preview_url": campaign.preview_url,
            "status": "draft"
        }

    except Exception as e:
        raise AgentExecutionError(
            agent_id=self.agent_id,
            task_id=task.task_id,
            message=f"Failed to create email campaign: {str(e)}",
            original_exception=e
        )
```

### Email Template Structure

```python
class EmailTemplate:
    """Email template with personalization support."""

    def __init__(
        self,
        template_id: str,
        name: str,
        subject_line: str,
        html_content: str,
        text_content: str,
        personalization_fields: list[str],
        category: str
    ):
        self.template_id = template_id
        self.name = name
        self.subject_line = subject_line
        self.html_content = html_content
        self.text_content = text_content
        self.personalization_fields = personalization_fields  # ["first_name", "company"]
        self.category = category  # "newsletter", "promotional", "transactional"

    def render(self, recipient_data: dict[str, Any]) -> tuple[str, str]:
        """
        Render template with recipient data.

        WHY: Personalizes email content for each recipient.
        HOW: Replaces personalization variables with recipient data.

        Returns:
            Tuple of (rendered_html, rendered_text)
        """
        rendered_html = self.html_content
        rendered_text = self.text_content

        for field in self.personalization_fields:
            value = recipient_data.get(field, "")
            rendered_html = rendered_html.replace(f"{{{{{field}}}}}", value)
            rendered_text = rendered_text.replace(f"{{{{{field}}}}}", value)

        return rendered_html, rendered_text
```

### A/B Testing Implementation

```python
async def _ab_test_email(self, task: Task) -> dict[str, Any]:
    """
    Create A/B test for email campaign.

    WHY: Enables data-driven optimization of email performance.
    HOW: Creates variants, sends to test segments, measures results.
    """
    campaign_id = task.parameters["campaign_id"]
    test_type = task.parameters["test_type"]  # "subject_line", "content", "send_time"
    variant_a = task.parameters["variant_a"]
    variant_b = task.parameters["variant_b"]
    test_size_percent = task.parameters.get("test_size_percent", 20)

    # Guard clause: Validate campaign exists
    campaign = await self._get_campaign(campaign_id)
    if not campaign:
        return {"error": f"Campaign {campaign_id} not found"}

    # Guard clause: Validate test size
    if not 10 <= test_size_percent <= 50:
        return {"error": "Test size must be between 10% and 50%"}

    try:
        # Create A/B test variants
        if test_type == "subject_line":
            variant_a_config = {"subject_line": variant_a}
            variant_b_config = {"subject_line": variant_b}
        elif test_type == "content":
            variant_a_config = {"content_id": variant_a}
            variant_b_config = {"content_id": variant_b}
        elif test_type == "send_time":
            variant_a_config = {"send_time": variant_a}
            variant_b_config = {"send_time": variant_b}

        # Create test via ESP
        ab_test = await self._esp_client.create_ab_test(
            campaign_id=campaign_id,
            test_type=test_type,
            variant_a=variant_a_config,
            variant_b=variant_b_config,
            test_size_percent=test_size_percent,
            winning_metric="open_rate"  # or "click_rate", "conversion_rate"
        )

        return {
            "ab_test_id": ab_test.id,
            "campaign_id": campaign_id,
            "test_type": test_type,
            "variant_a": variant_a_config,
            "variant_b": variant_b_config,
            "test_size_percent": test_size_percent,
            "test_recipients": ab_test.test_recipients,
            "winner_selection": "automatic",
            "status": "scheduled"
        }

    except Exception as e:
        raise AgentExecutionError(
            agent_id=self.agent_id,
            task_id=task.task_id,
            message=f"Failed to create A/B test: {str(e)}",
            original_exception=e
        )
```

### List Segmentation

```python
async def _segment_email_list(self, task: Task) -> dict[str, Any]:
    """
    Segment email list based on criteria.

    WHY: Enables targeted messaging to specific audience segments.
    HOW: Applies filters to subscriber list and creates segment.
    """
    list_id = task.parameters["list_id"]
    segment_name = task.parameters["segment_name"]
    criteria = task.parameters["criteria"]  # {"engagement": "active", "location": "US"}

    # Guard clause: Validate list exists
    email_list = await self._get_list(list_id)
    if not email_list:
        return {"error": f"List {list_id} not found"}

    try:
        # Build segmentation query
        query_conditions = []

        for key, value in criteria.items():
            if key == "engagement":
                # engagement: "active", "inactive", "new"
                if value == "active":
                    query_conditions.append("opened_last_30_days = true")
                elif value == "inactive":
                    query_conditions.append("opened_last_90_days = false")
                elif value == "new":
                    query_conditions.append("subscription_date > DATE_SUB(NOW(), INTERVAL 30 DAY)")
            elif key == "location":
                query_conditions.append(f"country = '{value}'")
            elif key == "industry":
                query_conditions.append(f"industry = '{value}'")
            else:
                query_conditions.append(f"{key} = '{value}'")

        # Create segment via ESP
        segment = await self._esp_client.create_segment(
            list_id=list_id,
            name=segment_name,
            conditions=query_conditions
        )

        return {
            "segment_id": segment.id,
            "segment_name": segment_name,
            "list_id": list_id,
            "subscriber_count": segment.subscriber_count,
            "criteria": criteria,
            "created_at": segment.created_at.isoformat()
        }

    except Exception as e:
        raise AgentExecutionError(
            agent_id=self.agent_id,
            task_id=task.task_id,
            message=f"Failed to segment email list: {str(e)}",
            original_exception=e
        )
```

### Drip Campaign Implementation

```python
async def _create_drip_campaign(self, task: Task) -> dict[str, Any]:
    """
    Create automated drip campaign workflow.

    WHY: Enables automated nurture sequences and onboarding flows.
    HOW: Creates series of timed emails triggered by subscriber actions.
    """
    campaign_name = task.parameters["campaign_name"]
    trigger_event = task.parameters["trigger_event"]  # "subscription", "purchase", "download"
    email_sequence = task.parameters["email_sequence"]  # List of emails with delays

    # Guard clause: Validate email sequence
    if not email_sequence or len(email_sequence) == 0:
        return {"error": "Email sequence cannot be empty"}

    # Guard clause: Validate each email in sequence
    for idx, email in enumerate(email_sequence):
        if "template_id" not in email or "delay_days" not in email:
            return {"error": f"Email {idx} missing required fields"}

    try:
        # Create drip campaign workflow
        workflow_steps = []

        for idx, email in enumerate(email_sequence):
            step = {
                "step_number": idx + 1,
                "template_id": email["template_id"],
                "delay_days": email["delay_days"],
                "subject_line": email.get("subject_line", ""),
                "condition": email.get("condition")  # Optional: "opened_previous" etc
            }
            workflow_steps.append(step)

        # Create automation via ESP
        drip_campaign = await self._esp_client.create_automation(
            name=campaign_name,
            trigger_event=trigger_event,
            workflow_steps=workflow_steps
        )

        return {
            "drip_campaign_id": drip_campaign.id,
            "campaign_name": campaign_name,
            "trigger_event": trigger_event,
            "email_count": len(email_sequence),
            "workflow_steps": workflow_steps,
            "status": "active",
            "created_at": drip_campaign.created_at.isoformat()
        }

    except Exception as e:
        raise AgentExecutionError(
            agent_id=self.agent_id,
            task_id=task.task_id,
            message=f"Failed to create drip campaign: {str(e)}",
            original_exception=e
        )
```

### Email Performance Tracking

```python
async def _track_email_performance(self, task: Task) -> dict[str, Any]:
    """
    Track email campaign performance metrics.

    WHY: Provides insights for optimization and ROI measurement.
    HOW: Fetches analytics from ESP API and calculates key metrics.
    """
    campaign_id = task.parameters["campaign_id"]

    # Guard clause: Validate campaign exists
    campaign = await self._get_campaign(campaign_id)
    if not campaign:
        return {"error": f"Campaign {campaign_id} not found"}

    try:
        # Fetch performance data from ESP
        stats = await self._esp_client.get_campaign_stats(campaign_id)

        # Calculate derived metrics
        open_rate = (stats.opens / stats.delivered) * 100 if stats.delivered > 0 else 0
        click_rate = (stats.clicks / stats.delivered) * 100 if stats.delivered > 0 else 0
        bounce_rate = (stats.bounces / stats.sent) * 100 if stats.sent > 0 else 0
        unsubscribe_rate = (stats.unsubscribes / stats.delivered) * 100 if stats.delivered > 0 else 0
        click_to_open_rate = (stats.clicks / stats.opens) * 100 if stats.opens > 0 else 0

        return {
            "campaign_id": campaign_id,
            "campaign_name": campaign.name,
            "sent": stats.sent,
            "delivered": stats.delivered,
            "opens": stats.opens,
            "unique_opens": stats.unique_opens,
            "clicks": stats.clicks,
            "unique_clicks": stats.unique_clicks,
            "bounces": stats.bounces,
            "spam_complaints": stats.spam_complaints,
            "unsubscribes": stats.unsubscribes,
            "open_rate": round(open_rate, 2),
            "click_rate": round(click_rate, 2),
            "bounce_rate": round(bounce_rate, 2),
            "unsubscribe_rate": round(unsubscribe_rate, 2),
            "click_to_open_rate": round(click_to_open_rate, 2),
            "revenue": stats.revenue if hasattr(stats, 'revenue') else 0,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise AgentExecutionError(
            agent_id=self.agent_id,
            task_id=task.task_id,
            message=f"Failed to track email performance: {str(e)}",
            original_exception=e
        )
```

### Deliverability Validation

```python
async def _validate_deliverability(self, campaign: Any) -> dict[str, Any]:
    """
    Validate email deliverability before sending.

    WHY: Prevents deliverability issues and protects sender reputation.
    HOW: Checks spam score, authentication, content, and compliance.
    """
    issues = []
    warnings = []

    # Check 1: Spam score
    spam_score = await self._check_spam_score(campaign.preview_html)
    if spam_score > 5:
        issues.append(f"High spam score: {spam_score}/10")
    elif spam_score > 3:
        warnings.append(f"Moderate spam score: {spam_score}/10")

    # Check 2: Authentication (SPF, DKIM, DMARC)
    auth_status = await self._check_authentication()
    if not auth_status["spf_valid"]:
        issues.append("SPF authentication not configured")
    if not auth_status["dkim_valid"]:
        issues.append("DKIM authentication not configured")

    # Check 3: Unsubscribe link
    if "unsubscribe" not in campaign.preview_html.lower():
        issues.append("Missing unsubscribe link (CAN-SPAM violation)")

    # Check 4: Physical address
    if not self._has_physical_address(campaign.preview_html):
        issues.append("Missing physical address (CAN-SPAM violation)")

    # Check 5: Broken links
    broken_links = await self._check_links(campaign.preview_html)
    if broken_links:
        warnings.append(f"Found {len(broken_links)} broken links")

    # Determine status
    if issues:
        status = "failed"
    elif warnings:
        status = "warning"
    else:
        status = "passed"

    return {
        "status": status,
        "spam_score": spam_score,
        "issues": issues,
        "warnings": warnings,
        "authentication": auth_status,
        "compliance": len(issues) == 0
    }
```

### Testing Strategy

1. **Unit tests:** 15+ tests covering all task types with mocked ESP client
2. **Integration tests:** Full workflows with real ESP API integration (or mocked)
3. **A/B testing tests:** Verify statistical significance and winner selection
4. **Segmentation tests:** Validate list segmentation logic
5. **Deliverability tests:** Check spam score and compliance validation
6. **Error handling tests:** ESP failures, rate limiting, invalid templates
7. **Performance tests:** Campaign creation and tracking workflows

## Alternatives Considered

### Alternative 1: Campaign Manager Handles Email Directly
Campaign Manager directly calls ESP APIs.

**Rejected because:**
- Violates single responsibility principle
- Campaign Manager is for coordination, not specialized email management
- No dedicated email expertise and deliverability optimization
- Difficult to reuse email capabilities across other agents
- Can't independently improve email without affecting campaign logic

### Alternative 2: External ESP Only (No Agent)
Use ESP API directly without agent wrapper.

**Rejected because:**
- No integration with multi-agent workflows
- No coordination with Copywriter and Designer
- No deliverability validation
- Doesn't fit multi-agent architecture
- No context awareness of campaign strategy

### Alternative 3: Single Generic Messaging Agent
Create one agent for all messaging (email, SMS, push, etc.).

**Rejected because:**
- Too broad scope for single agent
- Email has unique deliverability and compliance requirements
- Different integration patterns for each channel
- Violates single responsibility principle
- Harder to optimize individual channels

### Alternative 4: Manual Email Process
Rely on humans for all email campaign creation and delivery.

**Rejected because:**
- Doesn't scale for high-volume campaigns
- Slow turnaround time
- Human bottleneck for campaign workflow
- Contradicts autonomous department vision
- Expensive for routine email campaigns

## References

- ADR-001: Multi-agent Department Architecture
- ADR-002: TDD Methodology
- ADR-005: Exception Wrapping Standard
- ADR-006: Campaign Manager Agent
- ADR-007: Content Manager Agent
- ADR-009: Copywriter Specialist Agent
- ADR-011: Designer Specialist Agent
- MULTIAGENT_ARCHITECTURE.md: System architecture document
- DEVELOPMENT_STANDARDS.md: Coding standards

## Notes

This ADR establishes Email Specialist as a key marketing automation agent. Future enhancements may include:
- SMS campaign integration
- Push notification support
- Multi-language email campaigns
- Advanced personalization with AI
- Predictive send time optimization
- Email list enrichment and validation
- Transactional email support
- Advanced reporting and attribution
- Integration with CRM systems (Salesforce, HubSpot CRM)
- Email warming and deliverability monitoring
