# ADR-010: SEO Specialist Agent Architecture

**Status:** Accepted
**Date:** 2025-11-03
**Decision Makers:** Architecture Team
**Related ADRs:** ADR-001 (Multi-agent Architecture), ADR-002 (TDD Methodology), ADR-007 (Content Manager Agent), ADR-009 (Copywriter Specialist Agent)

## Context

The AI Marketing Director system currently has:
- **Executive Layer:** CMO Agent (strategic oversight)
- **Management Layer:** Campaign Manager, Social Media Manager, Content Manager
- **Specialist Layer:** LinkedIn Manager, Twitter Manager, Bluesky Manager, Analytics Specialist, Copywriter Specialist

The Content Manager and Copywriter Specialist require SEO expertise to:
1. Optimize content for search engines and discoverability
2. Research and target relevant keywords
3. Improve organic search rankings
4. Analyze SERP (Search Engine Results Page) competition
5. Generate SEO-optimized meta descriptions and titles
6. Provide technical SEO recommendations
7. Track keyword rankings and SEO performance

Without an SEO Specialist:
- Content is created without keyword optimization
- No systematic approach to improving search rankings
- Missing competitive SERP analysis
- No tracking of organic search performance
- Content Manager has no SEO expertise for content strategy
- Copywriter lacks keyword guidance for content creation

## Decision

We will implement an **SEO Specialist Agent** as a specialist-layer agent that:

1. **Conducts keyword research** for content topics and campaigns
2. **Optimizes content** for search engines (on-page SEO)
3. **Analyzes SERP** to understand competition and opportunities
4. **Generates meta descriptions** and title tags optimized for CTR and rankings
5. **Suggests internal linking** strategies for site architecture
6. **Audits SEO** for existing content and identifies issues
7. **Tracks keyword rankings** and organic search performance
8. **Generates SEO reports** with actionable recommendations

### Architecture Design

```
┌─────────────────────────────────────────────────┐
│      SEO Specialist (Specialist Layer)          │
│  - Keyword research & analysis                  │
│  - Content SEO optimization                     │
│  - SERP analysis & competitive intel            │
│  - Meta description generation                  │
│  - Technical SEO recommendations                │
└─────────────────────────────────────────────────┘
                      │
      ┌───────────────┼───────────────┐
      ▼               ▼               ▼
┌──────────┐   ┌──────────┐   ┌──────────┐
│   SEO    │   │  Search  │   │   AI     │
│  Tools   │   │ Console  │   │  (LLM)   │
│(SEMrush) │   │ (Google) │   │(Analysis)│
└──────────┘   └──────────┘   └──────────┘
```

### Coordination Pattern

```
Content Manager
   ↓ (requests keyword research)
SEO Specialist → [Keyword tools, SERP analysis]

Copywriter Specialist
   ↓ (requests content optimization)
SEO Specialist → [Analyze content, suggest improvements]

Campaign Manager
   ↓ (requests SEO audit)
SEO Specialist → [Audit content, track rankings]
```

### Supported Task Types

1. **keyword_research**: Research and analyze keywords for content topics
2. **optimize_content**: Optimize existing content for target keywords
3. **analyze_serp**: Analyze search results for target keywords
4. **generate_meta_descriptions**: Create SEO-optimized meta descriptions
5. **suggest_internal_links**: Recommend internal linking opportunities
6. **audit_seo**: Audit content for SEO issues and opportunities
7. **track_rankings**: Monitor keyword rankings over time
8. **generate_seo_report**: Create comprehensive SEO performance reports

### Key Characteristics

- **External Tool Integration:** Integrates with Google Search Console, SEMrush, Ahrefs APIs
- **AI-Powered Analysis:** Uses LLM for content optimization suggestions
- **Keyword Database:** Maintains keyword research and ranking data
- **SERP Tracking:** Monitors search engine results and competition
- **Content Scoring:** Evaluates content SEO quality with scoring system
- **Recommendation Engine:** Provides actionable SEO improvement suggestions
- **Strategy Pattern:** Uses dictionary dispatch for task routing (zero if/elif chains)
- **Exception Wrapping:** All external API calls wrapped with `AgentExecutionError`
- **Caching:** Caches SERP data and keyword research (24-hour TTL) to reduce API calls

## Consequences

### Positive

1. **Improved search rankings:** Systematic approach to SEO increases organic visibility
2. **Data-driven decisions:** Keyword research guides content strategy
3. **Competitive intelligence:** SERP analysis reveals opportunities
4. **Content quality:** SEO optimization improves content relevance
5. **Performance tracking:** Monitors rankings and identifies trends
6. **Integrated workflow:** Works seamlessly with Content Manager and Copywriter
7. **Standards compliance:** Follows all coding directives (Strategy Pattern, guard clauses, full type hints, WHY/HOW documentation)

### Negative

1. **External API dependency:** Requires SEO tool API access (Google Search Console, SEMrush)
2. **API costs:** SEO tools can be expensive with usage-based pricing
3. **Rate limiting:** Must respect API rate limits for external services
4. **Data freshness:** Keyword rankings update on different schedules
5. **Algorithm changes:** Search engine algorithm updates require adaptation

### Mitigation Strategies

1. **Graceful degradation:** Continue operating with limited data if APIs fail
2. **Caching strategy:** 24-hour TTL reduces API calls and costs
3. **Rate limit handling:** Implement backoff and retry logic
4. **Multiple data sources:** Aggregate data from multiple SEO tools for redundancy
5. **Fallback analysis:** Use AI-powered analysis when external tools unavailable

## Implementation Notes

### Task Delegation Pattern

```python
# SEO Specialist conducts keyword research
async def _keyword_research(self, task: Task) -> dict[str, Any]:
    """
    Research keywords for content topic.

    WHY: Identifies target keywords for content optimization.
    HOW: Uses SEO tools API + AI analysis for keyword opportunities.
    """
    topic = task.parameters["topic"]
    target_audience = task.parameters.get("target_audience")
    language = task.parameters.get("language", "en")

    # Guard clause: Check if we have cached keyword data
    cache_key = f"keywords_{topic}_{language}"
    if cached_data := self._get_cached_keywords(cache_key):
        return cached_data

    try:
        # Fetch keyword data from SEO tools
        keyword_data = await self._fetch_keyword_data(
            topic=topic,
            language=language
        )

        # Use AI to analyze and score keywords
        ai_analysis = await self._analyze_keywords_with_ai(
            keywords=keyword_data,
            topic=topic,
            target_audience=target_audience
        )

        # Combine data sources
        result = {
            "primary_keywords": keyword_data["primary"][:5],
            "secondary_keywords": keyword_data["secondary"][:10],
            "long_tail_keywords": keyword_data["long_tail"][:15],
            "keyword_difficulty": keyword_data["difficulty"],
            "search_volume": keyword_data["volume"],
            "recommendations": ai_analysis["recommendations"],
            "topic": topic
        }

        # Cache for 24 hours
        self._cache_keywords(cache_key, result)

        return result

    except Exception as e:
        raise AgentExecutionError(
            agent_id=self.agent_id,
            task_id=task.task_id,
            message=f"Failed to research keywords: {str(e)}",
            original_exception=e
        )
```

### Content SEO Optimization

```python
async def _optimize_content(self, task: Task) -> dict[str, Any]:
    """
    Optimize content for target keywords.

    WHY: Improves content SEO quality for better rankings.
    HOW: Analyzes content, checks keyword usage, suggests improvements.
    """
    content = task.parameters["content"]
    target_keywords = task.parameters["target_keywords"]

    # Calculate current SEO score
    current_score = self._calculate_seo_score(content, target_keywords)

    # Guard clause: Already well-optimized
    if current_score >= 90.0:
        return {
            "optimized": False,
            "reason": "Content already well-optimized",
            "score": current_score
        }

    # Use AI to generate optimization suggestions
    suggestions = await self._generate_optimization_suggestions(
        content=content,
        target_keywords=target_keywords,
        current_score=current_score
    )

    return {
        "optimized": True,
        "current_score": current_score,
        "suggestions": suggestions,
        "target_keywords": target_keywords,
        "issues_found": self._identify_seo_issues(content, target_keywords),
        "recommended_changes": suggestions["changes"],
        "estimated_improvement": suggestions["score_improvement"]
    }
```

### SERP Analysis

```python
async def _analyze_serp(self, task: Task) -> dict[str, Any]:
    """
    Analyze search engine results page for target keyword.

    WHY: Understand competition and identify ranking opportunities.
    HOW: Fetches SERP data, analyzes top results, identifies patterns.
    """
    keyword = task.parameters["keyword"]
    location = task.parameters.get("location", "US")

    # Guard clause: Check cache for recent SERP data
    cache_key = f"serp_{keyword}_{location}"
    if cached_serp := self._get_cached_serp(cache_key):
        return cached_serp

    try:
        # Fetch SERP data from Search Console or SEO tools
        serp_data = await self._fetch_serp_data(
            keyword=keyword,
            location=location
        )

        # Analyze top 10 results
        analysis = {
            "keyword": keyword,
            "location": location,
            "top_results": serp_data["results"][:10],
            "competition_level": self._calculate_competition_level(serp_data),
            "content_gaps": self._identify_content_gaps(serp_data),
            "ranking_factors": self._analyze_ranking_factors(serp_data),
            "opportunity_score": self._calculate_opportunity_score(serp_data),
            "recommendations": await self._generate_serp_recommendations(serp_data)
        }

        # Cache for 24 hours
        self._cache_serp(cache_key, analysis)

        return analysis

    except Exception as e:
        raise AgentExecutionError(
            agent_id=self.agent_id,
            task_id=task.task_id,
            message=f"Failed to analyze SERP: {str(e)}",
            original_exception=e
        )
```

### SEO Score Calculation

```python
def _calculate_seo_score(self, content: str, target_keywords: list[str]) -> float:
    """
    Calculate SEO quality score for content.

    WHY: Provides quantitative measure of content SEO optimization.
    HOW: Analyzes multiple SEO factors and weights them appropriately.

    Returns:
        SEO score (0-100)
    """
    score = 0.0

    # Keyword presence (30 points)
    keyword_score = self._score_keyword_usage(content, target_keywords)
    score += keyword_score * 0.30

    # Content length (20 points)
    length_score = self._score_content_length(content)
    score += length_score * 0.20

    # Readability (20 points)
    readability_score = self._score_readability(content)
    score += readability_score * 0.20

    # Structure (15 points) - headings, paragraphs
    structure_score = self._score_content_structure(content)
    score += structure_score * 0.15

    # Keyword density (15 points) - not too high, not too low
    density_score = self._score_keyword_density(content, target_keywords)
    score += density_score * 0.15

    return min(score, 100.0)
```

### Integration with Content Manager

```python
# Content Manager requests keyword research for content planning
content_manager -> seo_specialist.keyword_research(
    topic="AI in Marketing",
    target_audience="Marketing Directors",
    content_type="blog_post"
)

# Content Manager requests SEO audit before publishing
content_manager -> seo_specialist.audit_seo(
    content_id="blog_001",
    target_keywords=["AI marketing", "marketing automation"]
)

# Copywriter requests content optimization
copywriter -> seo_specialist.optimize_content(
    content="...",
    target_keywords=["AI marketing tools", "marketing AI"]
)

# Campaign Manager requests SEO performance report
campaign_manager -> seo_specialist.generate_seo_report(
    campaign_id="campaign_001",
    date_range="last_30_days"
)
```

### Testing Strategy

1. **Unit tests:** 14+ tests covering all task types with mocked SEO APIs
2. **Integration tests:** Full workflows with real SEO tool integration (or mocked)
3. **Keyword research tests:** Verify keyword data aggregation and scoring
4. **Content optimization tests:** Validate SEO score calculation and suggestions
5. **SERP analysis tests:** Check competitive analysis and recommendations
6. **Error handling tests:** API failures, rate limiting, invalid parameters
7. **Caching tests:** Verify cache behavior and TTL

## Alternatives Considered

### Alternative 1: Content Manager Handles SEO Directly
Content Manager directly calls SEO tools for keyword research.

**Rejected because:**
- Violates single responsibility principle
- Content Manager is for coordination, not specialized SEO analysis
- No dedicated SEO expertise and methodology
- Difficult to reuse SEO capabilities across other agents
- Can't independently improve SEO without affecting management logic

### Alternative 2: External SEO Service (No Agent)
Use external SEO API service without agent wrapper.

**Rejected because:**
- No integration with multi-agent workflows
- No AI-powered analysis and recommendations
- No caching or optimization strategy
- Doesn't fit multi-agent architecture
- No context awareness of content strategy

### Alternative 3: Manual SEO Process
Rely on human SEO specialist for all optimization.

**Rejected because:**
- Doesn't leverage AI capabilities
- Slow and doesn't scale
- Human bottleneck for content workflow
- Inconsistent methodology
- Contradicts autonomous department vision

## References

- ADR-001: Multi-agent Department Architecture
- ADR-002: TDD Methodology
- ADR-005: Exception Wrapping Standard
- ADR-007: Content Manager Agent
- ADR-009: Copywriter Specialist Agent
- MULTIAGENT_ARCHITECTURE.md: System architecture document
- DEVELOPMENT_STANDARDS.md: Coding standards

## Notes

This ADR establishes SEO Specialist as a key content optimization agent. Future enhancements may include:
- Local SEO optimization
- Voice search optimization
- Featured snippet optimization
- Schema markup recommendations
- Core Web Vitals monitoring
- Backlink analysis and outreach
- Competitor content gap analysis
- SEO forecasting with ML models
