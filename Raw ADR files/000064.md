# ADR-007: Use of external LLMs

## Date:
2024-09-26

## Status:
Accepted

## Context:
Our [interview with the AI expert](/Requirements/Research/interview-ai-expert.md) led to new insight concerning
LLMs, and some important assumptions [A24, A25, A21, A20](/Requirements/requirements-and-assumptions.md)

The following AI-use-cases need to be supported:
- A: Resume-Tips [A24, A25, A21, A20](/Requirements/requirements-and-assumptions.md)
- B: Automatic filling of employee data during registration [A24, A25, A21, A20](/Requirements/requirements-and-assumptions.md)
- C: Transformation of resume to story [A24, A25, A21, A20](/Requirements/requirements-and-assumptions.md)
- D: Extraction of features from stories and open role [A24, A25, A21, A20](/Requirements/requirements-and-assumptions.md)

We discussed three propositions:
- A: Use external AI (LLM) services as offered for example by Azure, Google, OpenAI.
  - +: Little development cost
  - +: Easy adaptation to the latest trends and models.
  - +: Tendency to become cheaper
  - +: Very fast time to market
  - -: Expensive.
  - -: Many API limitations such as rate-limits, delays, quotas, short lifecycle of models 
  - -: Regulatory considerations due to data privacy need to be made
- B: Use self controlled open-source LLM in a container running on the cloud
  - +: Specialized hardware can be used as a service this way.
  - +: A lot of control over fine-tuning, rates, and the runtime.
  - +: Less regulatory considerations due to data privacy need to be made.
  - -: Current LLMs will be surpassed soon due to fast evolving market. (A20)
  - -: Requires more development, configuration, maintenance, know-how, therefore higher cost.
  - -: High infrastructure cost due to resource heavy computing
- C: Use self controlled open-source LLM on-prem
  - +: Data privacy
  - +: Full control over LLM
  - -: Specialized hardware needs to be procured and additional staff needed. Delay in project timeline.
  - -: High electricity cost
  - -: High procurement and additional staff cost

## Decision

- Proposition A: We use external LLMs
- We need additional fault-tolerance and interoperability: we use an event-driven design for every LLM client in the system.

## Consequences:

- AI development can start without delay, faster TTM.
- Need to somehow track rate to avoid surpassing rate-limit (currently not solved, part of our [Known Limitations](/README.md#known-limitations))
- Cost is more predictable.

### Strengthened characteristics:

- Cost (especially due to tendency to become cheaper)
- Feasibility (less hardware, staff, talent required. Ability to use latest LLMs)
- Interoperability (due to the chosen design)
- Fault-tolerance (due to the chosen design)
- Availability (cloud providers SLA)

### Weakened characteristics:

- Feasibility (Need to check privacy regulations)
- Responsiveness (User-facing AIs)
- Observability (Fewer metrics about external system)
- Deployability (Due to the risk of LLMs becoming EOL (end-of-life). High effort of testing and migrating to new LLMs)