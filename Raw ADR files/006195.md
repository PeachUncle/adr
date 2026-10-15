# ADR-11: Generative AI Recommendation System for Context-Aware Vehicle Suggestions

## Status
- Accepted

## Context
MobilityCorp aims to improve customer engagement and satisfaction by proactively offering **personalized trip recommendations** through its mobile app and notifications.  
Currently, users rent vehicles on an ad-hoc basis, and the company wants to encourage **habitual use** (e.g., daily commutes, planned errands) by anticipating user intent.

The system should:
- Understand **real-time demand forecasts** (from ADR-10).  
- Personalize messages based on **user history, location, time, and behavior clusters**.  
- Communicate naturally, generating context-aware suggestions such as:  
  > “Bike demand is high in your area — you might want to reserve one 15 minutes earlier than usual.”  
  > “Rain expected at 6 PM — would you prefer to book a car for your commute home?”  
- Maintain **brand tone, factual accuracy**, and **user trust**.

The AI component must integrate with existing **forecasting pipelines**, the **feature store**, and the **user engagement services**.

## Decision
Implement a **Generative AI-based Recommendation System** that combines:
1. **Predictive models** (Prophet, LSTM, GNN from ADR-10) to detect demand surges, patterns, or availability risks.  
2. **Personalization engine** (ML-based clustering + user context features).  
3. **LLM-powered message generation** to turn predictions into personalized, conversational suggestions.

### Technical Approach
- Use **LLM (Large Language Model)** to generate message text dynamically, guided by structured context (user preferences, forecast data, weather, location).  
- Employ **prompt templates** with guardrails to ensure safe, consistent, and brand-aligned outputs.  
- Implement **RAG (Retrieval-Augmented Generation)** to inject current data — forecasts, weather, and availability — into the prompt context.  
- Output is passed to a **notification service** (mobile app, SMS, or email).  
- Include **human-in-the-loop review mode** during pilot phase for quality assurance.

### Example Flow
1. Forecast layer detects high bike demand in Zone 5 for next 30 minutes.
2. Personalization service identifies user segment “morning commuter in Zone 5.”
3. GenAI engine receives structured input:
> {
> "user": "morning_commuter",
> "location": "Zone 5",
> "forecast": "high bike demand next 30 min",
> "weather": "clear",
> "history": "rents e-bike daily at 8:00 AM"
> }

6. LLM prompt template:
> “Generate a short, friendly push notification to help the user plan their trip considering forecasted demand and weather.”

5. Output:
> “It’s a busy morning for bikes in your area! You might want to grab your usual e-bike 15 minutes earlier today.”

6. Notification service delivers the message.

## Rationale
- **Generative AI** allows human-like, contextual communication rather than static notifications.  
- **RAG** ensures responses are grounded in **real-time, factual** data (no hallucination).  
- **Personalization** increases retention, conversion, and frequency of rides.  
- **LLM prompt templates** allow A/B testing of tone, length, and effectiveness.  
- Combines predictive and generative layers for a holistic AI experience.

## Alternatives Considered
1. **Rule-based templates**
- Deterministic, safe
- Not personalized; limited scalability and engagement value
2. **Pre-trained LLM without RAG**
- Fast to deploy
- High risk of irrelevant or factually incorrect messages
3. **Classic recommender (collaborative filtering only)**
- Works for product similarity
- Doesn’t handle dynamic, real-time context like weather or vehicle demand

## Consequences

**Positive**
- Deeply personalized user engagement through contextual, human-like messages.  
- Improved fleet utilization by influencing user behavior.  
- Flexible framework to expand to new use cases (e.g., “return-time reminders,” “maintenance updates”).  

**Negative / Risks**
- LLM output variability — requires prompt control and content moderation.  
- Slight latency due to RAG and LLM inference.  
- Requires careful data governance to avoid over-personalization or privacy violations.  

## Implementation Details
- **LLM type:** model from AI Gateway (ADR-05).  
- **Input context:** user history, forecast, weather, event data, current availability.  
- **Prompt control:** Templated prompts with dynamic fields.  
- **RAG sources:** Feature store + vector embeddings for user/zone profiles.  
- **Content filtering:** Pre- and post-generation filters for tone, factual accuracy, and safety.  
- **Delivery:** Through existing Notification microservice integrated via REST API.

## Metrics for Success
- 20%+ increase in reservation pre-bookings during high-demand periods.  
- ≥90% of generated messages rated “relevant” or “helpful” in user feedback.  
- ≤1% rate of flagged or off-tone messages.  
- Measurable uplift in daily active users (DAU) and ride frequency.

## Status for Next Review
- Move to **ACCEPTED** after pilot test with real-time LLM integration in two major zones, de
