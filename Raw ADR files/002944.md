# Architecture Decision Record (ADR)

## ADR-14: Hosting Strategy

### Status
- ACCEPTED

### Context
The AI grading and feedback system for Certifiable is currently hosted in the USA. Given that multiple countries have agreed to adopt Certifiable's system, a decision needs made on how to host the go-forward system to account for data privacy and performance concerns.

### Decision
The decision is to host the system solely in the USA, contingent on obtaining explicit user agreement for data storage and processing. If the system is extended to a country or jurisdiction where data residency or privacy regulations require storage or processing of an individuals data locally, then this decision will need to be revisited.

### Alternatives Considered

#### 1. Host the system solely in the USA

*Description*:

Hosting the system solely in the USA, simplifying the delivery and management of the software, avoiding replication and in particular cost concerns of an internatially deployed ecosystem. This option would rely on users agreeing to have their data stored and processed within the USA, and relies upon participating countries to agree to this model.

*Pros*:
- Simplified Management: Centralized infrastructure simplifies maintenance, updates, and security management.
- Cost Efficiency: Reduced operational costs due to leveraging economies of scale by maintaining a single hosting location.
- Streamlined Development: Easier development and deployment processes with a unified environment.

*Cons*:
- Latency Concerns: Potential latency for users accessing the system from outside the USA.
- Regulatory Risks: Relies on user consent, which may require frequent re-evaluation to ensure continued compliance with evolving international data protection laws.
- Single Point of Failure: Risk of regional outages affecting all users if not adequately managed with backup and disaster recovery strategies.

#### 2. Distributed, Regional Hosting Model

*Description*:

Hosting individual instances of the system in regional locations to avoid complex data residency and privacy regulations, and maximise latency and performance of the candidates experience.

*Pros*:
- Performance: Localized data and processing could reduce latency for regional users.
- Regulatory Compliance: Facilitates compliance with local data protection regulations.

*Cons*:
- Complexity: Increases the complexity of managing infrastructure across multiple regions.
- Cost: Higher operational costs due to infrastructure duplication.
- Provisioning: Localized AI capabilities may not be as readily available or at the same price point as services available in the USA.
- Data Management: Additional complexity to manage cross-region replication of test questions, case-studies and grading criteria.

#### 3. Hybrid Hosting Model

*Description*:

Hosting databases and processing services in regional locations, while centralized control of test resources and management is maintained in the USA.

*Pros*:
- Flexibility: Combines centralized control with local presence, balancing operational and compliance needs.
- Regulatory Compliance: Facilitates compliance with local data protection regulations.

*Cons*:
- Complex Implementation: Managing a hybrid distributed infrastructure could prove challenging.
- Coordination Efforts: May require more complex data synchronization and application update processes.
- Cost: Higher operational costs due to infrastructure duplication.
- Provisioning: Localized AI capabilities may not be as readily available or at the same price point as services available in the USA.

### References

### Date
02/13/2025
