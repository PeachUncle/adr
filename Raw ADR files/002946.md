# Architecture Decision Record (ADR)

## ADR 16: Processing Strategy for Exam Grading

### Status

- ACCEPTED

### Context

Certifiable Inc. operates with a [7-day SLA](../sla-slo-sli.md) for marking exams, providing flexibility in how the grading process is managed. This flexibility opens up multiple processing options, allowing for optimization in terms of cost, efficiency, and sustainability. The key decision is determining the processing strategy that aligns best with these goals while adhering to the SLA.

### Decision

The decision is to implement a daily batch-based processing approach. This method will allow the company to optimize for cost efficiencies and sustainability by choosing optimal times to execute compute-intensive tasks, such as when energy consumption is lower or during non-peak hours.

### Alternatives Considered

#### 1. Daily Batch-Based Processing

*Description*:

Exams are collected and processed in daily batches rather than in real-time. This approach leverages planned computation times to reduce costs, align with energy efficiency goals, and take advantage of bulk processing efficiencies.

*Pros*:

- Cost Efficiency: Batch processing can be scheduled during off-peak times or when energy costs are lower.
- Sustainability: Allows the organization to align compute with periods of lower environmental impact.

*Cons*:

- Delayed Feedback: There might be a perceived delay from exam completion to feedback if not managed properly within the 7-day SLA.
- Resource Management: Requires effective management of resource allocation to handle large batch loads.

#### 2. Real-Time Processing

*Description*:

Each exam is processed immediately upon completion, allowing for rapid feedback and a constant flow of grading tasks.

*Pros*:

- Immediate Results: Provides rapid feedback to exam takers, which can be a competitive advantage.
- Continuous Operation: Ensures steady usage of computational resources, avoiding large spikes in demand.

*Cons*:

- Higher Costs: Continuous processing may not take advantage of cost variances in energy or compute resources.
- Increased Complexity: Requires more sophisticated infrastructure to handle real-time processing and scaling.

### Date
03/10/2025
