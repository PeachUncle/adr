# ADR-009: Copywriter Specialist Agent Architecture

**Status:** Accepted
**Date:** 2025-11-03
**Decision Makers:** Architecture Team
**Related ADRs:** ADR-001 (Multi-agent Architecture), ADR-002 (TDD Methodology), ADR-007 (Content Manager Agent)

## Context

The AI Marketing Director system currently has:
- **Executive Layer:** CMO Agent (strategic oversight)
- **Management Layer:** Campaign Manager, Social Media Manager, Content Manager
- **Specialist Layer:** LinkedIn Manager, Twitter Manager, Bluesky Manager, Analytics Specialist

The Content Manager Agent requires specialized content creation capabilities to:
1. Write high-quality marketing copy across multiple formats
2. Maintain consistent brand voice and tone
3. Create content for various channels (blog, social media, email)
4. Adapt writing style for different audiences
5. Generate content at scale while maintaining quality

Without a Copywriter Specialist:
- Content Manager has no way to generate written content
- No specialized writing expertise for different content types
- No brand voice consistency enforcement
- Manual copywriting required for all content
- Content creation becomes a bottleneck

## Decision

We will implement a **Copywriter Specialist Agent** as a specialist-layer agent that:

1. **Creates written content** across multiple formats (blog posts, social media, emails, case studies)
2. **Maintains brand voice** with configurable tone and style guidelines
3. **Adapts writing style** for different audiences and channels
4. **Integrates with LLM** (Claude) for content generation
5. **Validates content quality** against readability and brand standards
6. **Provides content variations** for A/B testing

### Architecture Design

```
┌─────────────────────────────────────────────────┐
│      Copywriter Specialist (Specialist Layer)   │
│  - Content creation (blog, social, email)       │
│  - Brand voice consistency                      │
│  - Multi-format writing                         │
│  - Content variation generation                 │
└─────────────────────────────────────────────────┘
                      │
      ┌───────────────┼───────────────┐
      ▼               ▼               ▼
┌──────────┐   ┌──────────┐   ┌──────────┐
│   LLM    │   │  Brand   │   │ Content  │
│ (Claude) │   │Guidelines│   │Templates │
└──────────┘   └──────────┘   └──────────┘
```

### Coordination Pattern

```
Content Manager
   ↓ (requests content)
Copywriter Specialist → [LLM, Brand Guidelines, Templates]

Campaign Manager
   ↓ (requests campaign copy)
Copywriter Specialist → [Generate content with campaign context]

Social Media Manager
   ↓ (requests social posts)
Copywriter Specialist → [Platform-specific copy]
```

### Supported Task Types

1. **write_blog_post**: Create long-form blog content with SEO optimization
2. **write_social_post**: Create platform-specific social media posts
3. **write_email**: Create email marketing copy (subject lines, body, CTA)
4. **write_case_study**: Create customer success stories
5. **write_product_description**: Create compelling product descriptions
6. **generate_headlines**: Generate multiple headline variations
7. **rewrite_content**: Rewrite existing content with new tone/style
8. **validate_brand_voice**: Check content against brand voice guidelines

### Key Characteristics

- **LLM Integration:** Uses Claude for content generation with custom prompts
- **Brand Voice Engine:** Maintains and enforces brand voice consistency
- **Content Templates:** Supports templates for common content types
- **Quality Validation:** Checks readability, tone, and brand alignment
- **Multi-Format Support:** Handles blog posts, social media, emails, case studies
- **Variation Generation:** Creates multiple versions for A/B testing
- **Strategy Pattern:** Uses dictionary dispatch for task routing (zero if/elif chains)
- **Exception Wrapping:** All LLM calls wrapped with `AgentExecutionError`

## Consequences

### Positive

1. **Automated content creation:** Generates high-quality copy at scale
2. **Brand consistency:** Ensures all content follows brand guidelines
3. **Multi-format expertise:** Handles different content types with appropriate style
4. **Fast iteration:** Quickly generates content variations for testing
5. **Quality standards:** Validates content against readability and brand criteria
6. **Integration ready:** Works seamlessly with Content Manager
7. **Standards compliance:** Follows all coding directives (Strategy Pattern, guard clauses, full type hints, WHY/HOW documentation)

### Negative

1. **LLM dependency:** Requires LLM access for content generation
2. **Quality variability:** LLM-generated content may require human review
3. **Brand voice drift:** Requires ongoing calibration to maintain voice
4. **Cost considerations:** LLM API usage costs
5. **Context limitations:** LLM context window limits long-form content

### Mitigation Strategies

1. **Prompt engineering:** Well-crafted prompts ensure consistent quality
2. **Brand voice examples:** Provide examples in prompts for consistency
3. **Iterative refinement:** Support content revision workflows
4. **Chunking strategy:** Break long content into manageable chunks
5. **Quality thresholds:** Set minimum readability and brand voice scores

## Implementation Notes

### Task Delegation Pattern

```python
# Copywriter uses LLM to generate content
async def _write_blog_post(self, task: Task) -> dict[str, Any]:
    """Write blog post using LLM with brand voice."""
    topic = task.parameters["topic"]
    target_audience = task.parameters["target_audience"]
    word_count = task.parameters.get("word_count", 1000)

    # Build prompt with brand voice context
    prompt = self._build_blog_post_prompt(
        topic=topic,
        target_audience=target_audience,
        word_count=word_count
    )

    # Guard clause: Check LLM availability
    if not self._llm_client:
        return {"error": "LLM client not configured", "content": ""}

    try:
        # Call LLM with exception wrapping
        response = await self._llm_client.generate(
            prompt=prompt,
            max_tokens=word_count * 2,  # Buffer for markdown formatting
            temperature=0.7
        )

        content = response.text

        # Validate brand voice
        brand_score = await self._validate_brand_voice(content)

        return {
            "content": content,
            "word_count": len(content.split()),
            "content_type": "blog_post",
            "brand_voice_score": brand_score,
            "reading_time": self._calculate_reading_time(content)
        }
    except Exception as e:
        raise AgentExecutionError(
            agent_id=self.agent_id,
            task_id=task.task_id,
            message=f"Failed to generate blog post: {str(e)}",
            original_exception=e
        )
```

### Content Types and Formats

```python
CONTENT_TYPES = {
    "blog_post": {
        "format": "markdown",
        "typical_length": "800-2000 words",
        "tone": "informative, engaging",
        "structure": "intro, body sections, conclusion, CTA"
    },
    "social_post": {
        "format": "plain_text",
        "typical_length": "50-280 characters",
        "tone": "conversational, engaging",
        "structure": "hook, value, CTA"
    },
    "email": {
        "format": "html",
        "typical_length": "150-500 words",
        "tone": "professional, personal",
        "structure": "subject, preview, body, CTA"
    },
    "case_study": {
        "format": "markdown",
        "typical_length": "1000-1500 words",
        "tone": "professional, data-driven",
        "structure": "challenge, solution, results, testimonial"
    }
}
```

### Brand Voice Guidelines

```python
class BrandVoiceGuidelines:
    """Brand voice configuration for consistent content generation."""

    tone_attributes: List[str]  # ["professional", "friendly", "authoritative"]
    vocabulary_do: List[str]    # Encouraged words/phrases
    vocabulary_dont: List[str]  # Words/phrases to avoid
    sentence_structure: str      # "short and punchy" vs "flowing and descriptive"
    personality_traits: List[str]  # ["helpful", "innovative", "trustworthy"]

    def to_prompt_context(self) -> str:
        """Convert guidelines to LLM prompt context."""
        return f"""
        Brand Voice:
        - Tone: {', '.join(self.tone_attributes)}
        - Personality: {', '.join(self.personality_traits)}
        - Use words like: {', '.join(self.vocabulary_do[:5])}
        - Avoid words like: {', '.join(self.vocabulary_dont[:5])}
        - Writing style: {self.sentence_structure}
        """
```

### Integration with Content Manager

```python
# Content Manager delegates to Copywriter
content_manager -> copywriter.write_blog_post(
    topic="AI in Marketing",
    target_audience="Marketing Directors",
    word_count=1500
)

# Campaign Manager requests campaign copy
campaign_manager -> copywriter.write_social_post(
    campaign_id="campaign_001",
    platform="linkedin",
    message_type="announcement"
)

# Social Media Manager requests platform-specific posts
social_media_manager -> copywriter.write_social_post(
    platform="twitter",
    content_type="thread",
    main_topic="Product launch"
)
```

### Quality Validation

```python
async def _validate_brand_voice(self, content: str) -> float:
    """
    Validate content against brand voice guidelines.

    WHY: Ensures content consistency with brand identity.
    HOW: Analyzes tone, vocabulary, and style against guidelines.

    Returns:
        Brand voice score (0-100)
    """
    score = 0.0

    # Check tone attributes (40 points)
    tone_score = self._analyze_tone(content)
    score += tone_score * 0.4

    # Check vocabulary usage (30 points)
    vocab_score = self._check_vocabulary(content)
    score += vocab_score * 0.3

    # Check readability (30 points)
    readability_score = self._calculate_readability(content)
    score += readability_score * 0.3

    return score
```

### Testing Strategy

1. **Unit tests:** 12+ tests covering all task types with mocked LLM
2. **Integration tests:** Full workflows with real LLM calls (or mocked)
3. **Brand voice tests:** Verify content matches brand guidelines
4. **Content quality tests:** Validate readability and structure
5. **Error handling tests:** LLM failures, invalid parameters

## Alternatives Considered

### Alternative 1: Content Manager Handles Copywriting Directly
Content Manager directly calls LLM for content generation.

**Rejected because:**
- Violates single responsibility principle
- Content Manager is for coordination, not specialized writing
- No dedicated brand voice management
- Difficult to reuse copywriting across other agents
- Can't independently improve copywriting without affecting management logic

### Alternative 2: External Copywriting Service (No Agent)
Use external API service for content generation without agent wrapper.

**Rejected because:**
- No integration with multi-agent workflows
- No brand voice consistency enforcement
- No content quality validation
- Doesn't fit multi-agent architecture
- No context awareness of campaigns or strategy

### Alternative 3: Template-Based Content Generation
Use pre-defined templates instead of LLM generation.

**Rejected because:**
- Limited flexibility and creativity
- Requires extensive template maintenance
- Cannot adapt to new content types easily
- Less natural, engaging content
- Doesn't leverage AI capabilities

## References

- ADR-001: Multi-agent Department Architecture
- ADR-002: TDD Methodology
- ADR-005: Exception Wrapping Standard
- ADR-007: Content Manager Agent
- MULTIAGENT_ARCHITECTURE.md: System architecture document
- DEVELOPMENT_STANDARDS.md: Coding standards

## Notes

This ADR establishes Copywriter Specialist as a key content creation agent. Future enhancements may include:
- Multi-language content generation
- Industry-specific writing styles
- Sentiment analysis and optimization
- Real-time content personalization
- Integration with content analytics for continuous improvement
- A/B test variant generation with hypothesis tracking
