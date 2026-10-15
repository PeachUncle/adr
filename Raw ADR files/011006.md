# ADR-013: Market Research Agent Architecture

**Status:** Accepted
**Date:** 2025-11-03
**Decision Makers:** Architecture Team
**Related ADRs:** ADR-001 (Multi-agent Architecture), ADR-002 (TDD Methodology), ADR-006 (Campaign Manager Agent), ADR-008 (Analytics Specialist Agent)

## Context

The AI Marketing Director system currently has:
- **Executive Layer:** CMO Agent (strategic oversight)
- **Management Layer:** Campaign Manager, Social Media Manager, Content Manager
- **Specialist Layer:** LinkedIn Manager, Twitter Manager, Bluesky Manager, Analytics Specialist, Copywriter Specialist, SEO Specialist, Designer Specialist, Email Specialist

The CMO, Campaign Manager, and Content Manager require market intelligence capabilities to:
1. Analyze competitors and identify competitive advantages
2. Identify market trends and emerging opportunities
3. Conduct customer sentiment analysis across channels
4. Research industry dynamics and market conditions
5. Perform SWOT analysis for strategic planning
6. Track competitor activities and product launches
7. Identify market gaps and opportunities
8. Provide data-driven market insights for decision-making

Without a Market Research Agent:
- No automated competitive intelligence gathering
- CMO lacks market insights for strategic planning
- Campaign Manager cannot benchmark against competitors
- Content Manager has no trend data for content strategy
- Missing market opportunity identification
- No systematic competitor monitoring

## Decision

We will implement a **Market Research Agent** as a specialist-layer agent that:

1. **Analyzes competitors** using web scraping, API integrations, and public data sources
2. **Identifies market trends** through news analysis, social media monitoring, and data aggregation
3. **Conducts sentiment analysis** on customer feedback, reviews, and social media
4. **Researches industries** using market research APIs (Crunchbase, SimilarWeb, Statista)
5. **Performs SWOT analysis** combining internal and external data
6. **Tracks competitors** with automated monitoring and alerts
7. **Identifies opportunities** by analyzing market gaps and customer needs
8. **Generates insights** using AI/LLM analysis of research data

### Architecture Design

```
┌─────────────────────────────────────────────────┐
│     Market Research Agent (Specialist Layer)    │
│  - Competitive analysis                         │
│  - Market trend identification                  │
│  - Customer sentiment analysis                  │
│  - Industry research & insights                 │
└─────────────────────────────────────────────────┘
                      │
      ┌───────────────┼───────────────┐
      ▼               ▼               ▼
┌──────────┐   ┌──────────┐   ┌──────────┐
│Research  │   │Sentiment │   │  Market  │
│APIs      │   │Analysis  │   │  Data    │
│(CB, SW)  │   │  (NLP)   │   │  Cache   │
└──────────┘   └──────────┘   └──────────┘
```

### Coordination Pattern

```
CMO Agent
   ↓ (requests market analysis)
Market Research Agent → [Research APIs, Sentiment Analysis, LLM]

Campaign Manager
   ↓ (requests competitive analysis)
Market Research Agent → [Competitor tracking, benchmarking]

Content Manager
   ↓ (requests trend analysis)
Market Research Agent → [Trend identification, topic insights]

Analytics Specialist
   ↑ (provides usage data)
Market Research Agent → [Combines with external research]
```

### Supported Task Types

1. **analyze_competitor**: Analyze specific competitor's strategy, products, positioning
2. **identify_market_trends**: Identify emerging trends in target market
3. **analyze_sentiment**: Analyze customer sentiment from reviews, social media
4. **research_industry**: Research industry dynamics, market size, growth
5. **perform_swot_analysis**: Conduct SWOT analysis for strategic planning
6. **track_competitor_activity**: Monitor competitor activities and changes
7. **identify_opportunities**: Identify market gaps and opportunities
8. **generate_market_insights**: Generate AI-powered insights from research data

### Key Characteristics

- **Research API Integration:** Crunchbase, SimilarWeb, Statista, Google Trends
- **Sentiment Analysis:** NLP-based sentiment analysis on reviews and social media
- **Trend Detection:** Pattern recognition in market data and news
- **Competitive Intelligence:** Automated competitor monitoring and analysis
- **Data Caching:** 24-hour TTL for expensive research operations
- **LLM-Powered Insights:** Claude integration for analysis and synthesis
- **SWOT Framework:** Structured strategic analysis methodology
- **Strategy Pattern:** Uses dictionary dispatch for task routing (zero if/elif chains)
- **Exception Wrapping:** All external API calls wrapped with `AgentExecutionError`

## Consequences

### Positive

1. **Automated intelligence:** Continuous market and competitor monitoring
2. **Data-driven strategy:** CMO has market insights for strategic decisions
3. **Competitive advantage:** Early identification of threats and opportunities
4. **Trend awareness:** Content and campaigns aligned with market trends
5. **Sentiment tracking:** Understanding of customer perception and satisfaction
6. **Cost effective:** Reduces need for manual research and analyst work
7. **Standards compliance:** Follows all coding directives (Strategy Pattern, guard clauses, full type hints, WHY/HOW documentation)

### Negative

1. **API costs:** Research APIs (Crunchbase, SimilarWeb) can be expensive
2. **Data accuracy:** Third-party data may have quality issues or lag
3. **Rate limiting:** Research APIs have strict rate limits
4. **Scraping challenges:** Web scraping for competitor data is fragile
5. **Privacy concerns:** Sentiment analysis must respect data privacy

### Mitigation Strategies

1. **Cost controls:** Set monthly API usage limits and monitor spending
2. **Data validation:** Cross-reference multiple sources for accuracy
3. **Caching:** 24-hour cache to minimize API calls
4. **Graceful degradation:** Continue with partial data if APIs fail
5. **Privacy compliance:** Only analyze publicly available data

## Implementation Notes

### Task Delegation Pattern

```python
# Market Research Agent analyzes competitor
async def _analyze_competitor(self, task: Task) -> dict[str, Any]:
    """
    Analyze specific competitor's strategy and positioning.

    WHY: Provides competitive intelligence for strategic planning.
    HOW: Uses research APIs, web data, and LLM analysis to profile competitor.
    """
    competitor_name = task.parameters["competitor_name"]
    analysis_depth = task.parameters.get("depth", "standard")

    # Guard clause: Check if research APIs available
    if not self._crunchbase_client and not self._similarweb_client:
        return {"error": "Research APIs not configured", "competitor_profile": None}

    # Check cache first (24-hour TTL)
    cache_key = f"competitor_{competitor_name.lower().replace(' ', '_')}"
    if cache_key in self._research_cache:
        cached_data, cached_time = self._research_cache[cache_key]
        if datetime.now() - cached_time < self._cache_ttl:
            cached_data["cached"] = True
            return cached_data

    try:
        # Fetch competitor data from multiple sources
        competitor_profile = {}

        # Crunchbase: Company info, funding, team
        if self._crunchbase_client:
            cb_data = await self._crunchbase_client.get_organization(competitor_name)
            competitor_profile["company_info"] = {
                "name": cb_data.name,
                "description": cb_data.description,
                "founded_year": cb_data.founded_on,
                "funding_total": cb_data.funding_total,
                "employee_count": cb_data.num_employees_enum,
                "headquarters": cb_data.location,
            }

        # SimilarWeb: Traffic, audience, marketing channels
        if self._similarweb_client:
            sw_data = await self._similarweb_client.get_website_data(
                self._extract_domain(competitor_name)
            )
            competitor_profile["digital_presence"] = {
                "monthly_visits": sw_data.visits,
                "traffic_sources": sw_data.traffic_sources,
                "top_countries": sw_data.geography,
                "engagement_metrics": {
                    "bounce_rate": sw_data.bounce_rate,
                    "pages_per_visit": sw_data.pages_per_visit,
                    "avg_visit_duration": sw_data.visit_duration,
                },
            }

        # LLM Analysis: Strategic insights
        analysis_prompt = f"""
        Analyze this competitor profile and provide strategic insights:

        Company: {competitor_name}
        {json.dumps(competitor_profile, indent=2)}

        Provide:
        1. Competitive positioning analysis
        2. Key strengths and weaknesses
        3. Market strategy assessment
        4. Threats they pose to us
        5. Opportunities to differentiate
        """

        llm_analysis = await self._llm_client.generate(
            prompt=analysis_prompt,
            temperature=0.3  # Lower temperature for analytical tasks
        )

        result = {
            "competitor_name": competitor_name,
            "competitor_profile": competitor_profile,
            "strategic_analysis": llm_analysis.text,
            "analysis_date": datetime.now().isoformat(),
            "data_sources": ["crunchbase", "similarweb", "llm"],
            "cached": False
        }

        # Cache result
        self._research_cache[cache_key] = (result, datetime.now())

        return result

    except Exception as e:
        raise AgentExecutionError(
            agent_id=self.agent_id,
            task_id=task.task_id,
            message=f"Failed to analyze competitor: {str(e)}",
            original_exception=e
        )
```

### Market Trend Identification

```python
async def _identify_market_trends(self, task: Task) -> dict[str, Any]:
    """
    Identify emerging trends in target market.

    WHY: Enables proactive strategy aligned with market direction.
    HOW: Analyzes news, social media, search trends, and industry reports.
    """
    market_category = task.parameters["market_category"]
    timeframe = task.parameters.get("timeframe", "30_days")

    # Guard clause: Check if trend analysis tools available
    if not self._google_trends_client:
        return {"error": "Trend analysis tools not configured"}

    try:
        trends = []

        # Google Trends: Search interest over time
        if self._google_trends_client:
            trend_data = await self._google_trends_client.get_interest_over_time(
                keywords=self._get_market_keywords(market_category),
                timeframe=timeframe
            )

            # Identify rising queries
            rising_queries = await self._google_trends_client.get_related_queries(
                keyword=market_category
            )

            trends.append({
                "source": "google_trends",
                "trending_topics": rising_queries.get("rising", []),
                "interest_trend": trend_data.direction,  # "rising", "stable", "declining"
            })

        # News Analysis: Extract themes from recent news
        if self._news_api_client:
            news_articles = await self._news_api_client.get_everything(
                q=market_category,
                from_date=(datetime.now() - timedelta(days=30)).isoformat(),
                language="en",
                sort_by="relevancy"
            )

            # LLM: Extract trends from news headlines
            headlines = [article.title for article in news_articles[:50]]
            trend_extraction_prompt = f"""
            Analyze these recent news headlines about {market_category}:

            {json.dumps(headlines, indent=2)}

            Identify:
            1. Emerging trends and themes
            2. Market shifts and changes
            3. New technologies or innovations
            4. Changing customer preferences
            """

            trend_analysis = await self._llm_client.generate(
                prompt=trend_extraction_prompt,
                temperature=0.4
            )

            trends.append({
                "source": "news_analysis",
                "insights": trend_analysis.text,
                "article_count": len(news_articles)
            })

        # Social Media: Trending conversations
        if self._social_listening_client:
            social_trends = await self._social_listening_client.get_trending_topics(
                category=market_category,
                timeframe=timeframe
            )

            trends.append({
                "source": "social_media",
                "trending_hashtags": social_trends.hashtags[:10],
                "conversation_volume": social_trends.total_mentions,
                "sentiment_shift": social_trends.sentiment_trend
            })

        return {
            "market_category": market_category,
            "timeframe": timeframe,
            "trends": trends,
            "trend_count": len(trends),
            "analysis_date": datetime.now().isoformat()
        }

    except Exception as e:
        raise AgentExecutionError(
            agent_id=self.agent_id,
            task_id=task.task_id,
            message=f"Failed to identify market trends: {str(e)}",
            original_exception=e
        )
```

### Sentiment Analysis

```python
async def _analyze_sentiment(self, task: Task) -> dict[str, Any]:
    """
    Analyze customer sentiment from reviews and social media.

    WHY: Understanding customer perception guides product and messaging strategy.
    HOW: Uses NLP sentiment analysis on reviews, social posts, and feedback.
    """
    data_source = task.parameters["data_source"]  # "reviews", "social_media", "support_tickets"
    product_or_brand = task.parameters.get("product_or_brand")

    try:
        sentiment_data = []

        # Reviews: Product review sentiment
        if data_source in ["reviews", "all"]:
            if self._review_api_client:
                reviews = await self._review_api_client.get_reviews(
                    product=product_or_brand,
                    limit=500
                )

                # Sentiment analysis on reviews
                review_sentiments = []
                for review in reviews:
                    sentiment_score = await self._analyze_text_sentiment(review.text)
                    review_sentiments.append(sentiment_score)

                avg_sentiment = sum(review_sentiments) / len(review_sentiments)

                sentiment_data.append({
                    "source": "reviews",
                    "total_reviews": len(reviews),
                    "average_sentiment": avg_sentiment,
                    "sentiment_distribution": {
                        "positive": len([s for s in review_sentiments if s > 0.3]),
                        "neutral": len([s for s in review_sentiments if -0.3 <= s <= 0.3]),
                        "negative": len([s for s in review_sentiments if s < -0.3])
                    }
                })

        # Social Media: Mentions and sentiment
        if data_source in ["social_media", "all"]:
            if self._social_listening_client:
                mentions = await self._social_listening_client.get_mentions(
                    keyword=product_or_brand,
                    timeframe="30_days"
                )

                social_sentiments = [m.sentiment for m in mentions if hasattr(m, 'sentiment')]
                avg_social_sentiment = sum(social_sentiments) / len(social_sentiments) if social_sentiments else 0

                sentiment_data.append({
                    "source": "social_media",
                    "total_mentions": len(mentions),
                    "average_sentiment": avg_social_sentiment,
                    "trending_sentiment": "positive" if avg_social_sentiment > 0.2 else "negative" if avg_social_sentiment < -0.2 else "neutral"
                })

        # LLM: Summarize sentiment insights
        sentiment_summary_prompt = f"""
        Analyze this sentiment data for {product_or_brand}:

        {json.dumps(sentiment_data, indent=2)}

        Provide:
        1. Overall sentiment assessment
        2. Key themes in positive feedback
        3. Key themes in negative feedback
        4. Recommended actions based on sentiment
        """

        summary = await self._llm_client.generate(
            prompt=sentiment_summary_prompt,
            temperature=0.3
        )

        return {
            "product_or_brand": product_or_brand,
            "sentiment_data": sentiment_data,
            "sentiment_summary": summary.text,
            "overall_sentiment_score": sum([d.get("average_sentiment", 0) for d in sentiment_data]) / len(sentiment_data),
            "analysis_date": datetime.now().isoformat()
        }

    except Exception as e:
        raise AgentExecutionError(
            agent_id=self.agent_id,
            task_id=task.task_id,
            message=f"Failed to analyze sentiment: {str(e)}",
            original_exception=e
        )
```

### SWOT Analysis

```python
async def _perform_swot_analysis(self, task: Task) -> dict[str, Any]:
    """
    Perform SWOT analysis for strategic planning.

    WHY: Structured framework for assessing strategic position.
    HOW: Combines internal data with external research for comprehensive SWOT.
    """
    analysis_scope = task.parameters.get("scope", "company")  # "company", "product", "campaign"
    include_competitors = task.parameters.get("include_competitors", True)

    try:
        # Gather data for SWOT
        swot_data = {
            "strengths": [],
            "weaknesses": [],
            "opportunities": [],
            "threats": []
        }

        # Internal data: From analytics specialist
        if self._analytics_client:
            performance_data = await self._analytics_client.get_performance_metrics()

            # Strong performance = Strength
            if performance_data.get("conversion_rate", 0) > 5.0:
                swot_data["strengths"].append("High conversion rate compared to industry average")

            # Weak performance = Weakness
            if performance_data.get("bounce_rate", 0) > 60:
                swot_data["weaknesses"].append("High bounce rate indicates user experience issues")

        # Market trends = Opportunities/Threats
        market_trends = await self._identify_market_trends(
            Task(
                task_id="swot_trends",
                task_type="identify_market_trends",
                parameters={"market_category": task.parameters.get("market_category", "marketing_automation")},
                assigned_to=self.role,
                assigned_by=task.assigned_by,
                created_at=datetime.now()
            )
        )

        # Parse trends for opportunities/threats (simplified)
        swot_data["opportunities"].append("Emerging AI/ML trends in market automation")
        swot_data["threats"].append("Increased competition from well-funded startups")

        # Competitor analysis = Threats
        if include_competitors and self._crunchbase_client:
            competitors = await self._get_top_competitors()
            for competitor in competitors[:3]:
                if competitor.get("funding_total", 0) > 50000000:
                    swot_data["threats"].append(f"{competitor['name']} well-funded competitor")

        # LLM: Synthesize SWOT analysis
        swot_prompt = f"""
        Create a comprehensive SWOT analysis based on this data:

        Strengths: {swot_data['strengths']}
        Weaknesses: {swot_data['weaknesses']}
        Opportunities: {swot_data['opportunities']}
        Threats: {swot_data['threats']}

        For each category:
        1. Prioritize items by strategic importance
        2. Add any missing items based on context
        3. Provide strategic recommendations
        """

        analysis = await self._llm_client.generate(
            prompt=swot_prompt,
            temperature=0.4
        )

        return {
            "swot_analysis": swot_data,
            "strategic_recommendations": analysis.text,
            "analysis_scope": analysis_scope,
            "analysis_date": datetime.now().isoformat()
        }

    except Exception as e:
        raise AgentExecutionError(
            agent_id=self.agent_id,
            task_id=task.task_id,
            message=f"Failed to perform SWOT analysis: {str(e)}",
            original_exception=e
        )
```

### Testing Strategy

1. **Unit tests:** 15+ tests covering all task types with mocked research APIs
2. **Integration tests:** Full workflows with real API integration (or mocked)
3. **Competitor analysis tests:** Verify data aggregation from multiple sources
4. **Trend detection tests:** Validate trend identification accuracy
5. **Sentiment analysis tests:** Check NLP sentiment scoring
6. **Caching tests:** Verify 24-hour cache reduces API calls
7. **Error handling tests:** API failures, rate limiting, missing data

## Alternatives Considered

### Alternative 1: CMO Handles Research Directly
CMO directly calls research APIs.

**Rejected because:**
- Violates single responsibility principle
- CMO is for strategic decisions, not detailed research execution
- No dedicated research expertise and data synthesis
- Difficult to reuse research capabilities across other agents
- Can't independently improve research without affecting executive logic

### Alternative 2: External Research Service (No Agent)
Use external research API service without agent wrapper.

**Rejected because:**
- No integration with multi-agent workflows
- No data synthesis or insight generation
- No coordination with other agents
- Doesn't fit multi-agent architecture
- No context awareness of business strategy

### Alternative 3: Manual Research Process
Rely on humans for all market research.

**Rejected because:**
- Doesn't scale for continuous monitoring
- Expensive and time-consuming
- Human bottleneck for strategic decisions
- Contradicts autonomous department vision
- Misses real-time opportunities

### Alternative 4: Analytics Specialist Handles Research
Extend Analytics Specialist to include market research.

**Rejected because:**
- Violates single responsibility principle
- Analytics focuses on internal metrics, not external market intelligence
- Different skill sets and data sources
- Too broad scope for single agent
- Reduces focus on core analytics capabilities

## References

- ADR-001: Multi-agent Department Architecture
- ADR-002: TDD Methodology
- ADR-005: Exception Wrapping Standard
- ADR-006: Campaign Manager Agent
- ADR-008: Analytics Specialist Agent
- MULTIAGENT_ARCHITECTURE.md: System architecture document
- DEVELOPMENT_STANDARDS.md: Coding standards

## Notes

This ADR establishes Market Research Agent as the intelligence hub for the marketing department. Future enhancements may include:
- Patent and trademark monitoring
- M&A intelligence and market consolidation tracking
- Regulatory and compliance monitoring
- Technology trend forecasting
- Customer journey analysis
- Win/loss analysis integration
- Predictive market modeling
- Integration with business intelligence tools
- Real-time alert system for market changes
- Automated competitive battlecards generation
