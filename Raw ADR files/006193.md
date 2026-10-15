# ADR-09: Agentic Workflow for Trip Planning
**Status**: ACCEPTED

## Context
We are tackling the challenge that most of our customers only use our service on an ad-hoc basis. We would like more of them to rely on us on a regular basis like daily commmute. 

## Current Pain Point
- User accesses our app as an ad-hoc to their daily navigation apps(google maps, apple maps etc.). They need to switch over to our app for booking. The booking experience is not seamless.
- They usually only come to us when their navigation app suggests that no public transport alternatives are available or it's too far for walking.
- As a result, their trip planning experience involves a lot of extra thinking.
- The vehicle booking experience can be too lengthy. For first timers, if they are in a rush, first finding the route, then setting up their account and finally locating a bike is usually too much of a hassle. Many users quit when feeling like there are too many steps.

## Decision
We are adding a **personal mobility agent** that proactively plans, books, and navigates commutes. The solution must integrate multiple internal/external systems (booking, pricing, maps, payments, user usage/minutes), remain **observable and safe under AI uncertainty**, and allow rapid evolution.

We will adopt a **MCP Client + MCP Server** architecture so that the agent (hosted in the MCP **Client/Host**) can invoke **capability servers** (routing, booking, usage, payments, history) through stable, typed tool endpoints.

### High-leval Approach
**MCP (Model–Component–Program) with Client/Server separation** for the agentic commute workflow, where:

- The **Planning Agent (MCP Host / Client)** runs the **Programs** (commute routines), reasons with an **AI Gateway (LLM runtime)**, and calls remote **MCP Servers** as tools.  
- **MCP Servers** expose deterministic **Components**: routing, vehicle availability, user minutes, pricing, payments, and usage history.  
- **Models** (prediction, preference, context) are isolated and versioned; programs orchestrate them and enforce guardrails.

**Scope:** The agent manages **both booking and navigation** end‑to‑end for daily commutes, with opt‑in automation levels (auto‑book / suggest / confirm).


## 3. Architecture Overview

### 3.1 MCP Client (Planning Agent / Host)

- **Programs**: `LeaveForWork`, `ReturnHome`, `ReactiveRebook`, `SubscriptionAdvisor`  
- **Models**: commute prediction, calendar parser, preference model, confidence estimator  
- **Guardrails**: policy checks, budget/minutes limits, geographic geofences, human‑in‑the‑loop confirmation for low confidence  
- **AI Gateway**: routes tool calls to servers; logs prompts/completions with redaction

### 3.2 MCP Servers (Deterministic Components)

- **Routing Server** → Vehicle availability service → Google Maps Routes API  
- **User Minutes Server** → User Minutes API / store  
- **Payment Server** → Pricing API → Payment Service → Stripe/Adyen  
- **History Server** → Usage Data API / history store

> Each server provides: typed schemas, idempotent operations, auth via service tokens, rate limiting, structured errors, and trace context propagation.

### 3.3 Data & Contracts

- **Typed interfaces** (OpenAPI/JSON Schema) for all server tools  
- **Eventing**: commute events (`CommuteSuggested`, `Booked`, `Started`, `Arrived`, `Rebooked`, `PaymentFailed`) emitted to analytics bus  
- **State**: short‑lived agent memory (per session) + durable per‑user preferences

---

## 4. Consequences

### Positive
- **Uncertainty isolation**: Models are sandboxed; **Programs** hold business rules and fallbacks; **Servers** are deterministic.  
- **Safe degradation**: On low confidence or tool failure, programs switch to rule‑based flows (manual confirm, re‑route, reserve backup vehicle).  
- **Evolvability**: Swap/upgrade models without touching servers; add new servers (e.g., transit) without retraining models.  
- **Observability**: Program traces include model confidence, tool calls, and fallback reasons for post‑mortems and tuning.

### Negative
- **Hard to test** since the outcome from LLM is undeterministic
- **Higher orchestration effort** to enumerate uncertainty paths and retries.  
- **Latency sensitivity** from real‑time inference + tool hops; requires caching and parallelization.  
- **Expanded ops surface** (multiple servers, schema/version management, prompt governance).

## 5. Non‑Functional Requirements

- **Reliability**: p99 end‑to‑end suggestion < 1.5s; booking SLO ≥ 99.9% monthly.  
- **Safety/Trust**: explicit consent for auto‑booking; explainability message with each action; one‑click undo/cancel.  
- **Security**: OAuth2/OIDC between client and servers; scoped tokens; PCI isolation for payments; PII minimization + encryption at rest.  
- **Privacy**: differential logging (PII redaction), data retention by purpose; opt‑out and data delete flow.  
- **Observability**: distributed tracing, structured events, model/guardrail metrics (confidence, override rate, fallback rate).

---

## 6. API/Tool Sketches (abridged)

```yaml
# Routing Server (OpenAPI snippet)
POST /route/commute
body: { origin, destination, modes, depart_at }
returns: { steps[], eta, cost_estimate, confidence }
```

```yaml
# Payment Server
POST /passes/purchase
body: { user_id, product_id, price_quote_id }
returns: { payment_id, status }
```

```yaml
# User Minutes Server
GET /users/{user_id}/minutes
returns: { remaining, renewal_at }
```
---

## 7. Metrics of Success

- Weekly Active Commuters (WAC) ↑  
- Commute Conversion Rate (suggested → booked) ↑  
- Repeat Commute Days/User/Week ↑  
- Fallback/Override Rate ↓; Payment Failure Rate ↓  
- Time‑to‑First‑Vehicle and ETA accuracy within target bands

---

## 8. Alternatives Considered

- **Monolithic agent** with direct SDK calls — faster to start, poor isolation/observability.  
- **Generic workflow engine only** — great reliability, but harder to express adaptive agent reasoning.  
- **Pure LLM tools without servers** — weak contracts; harder SLOs and auditing.



