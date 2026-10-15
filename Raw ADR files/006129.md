# ADR-003: Build vs Buy (Component Selection - Prioritizing Open Source and Avoiding Vendor Lock-in)

### Date: 2024-09-30
### Status: Accepted

### Decision Maker: Engineering Team

### Context:

As a non-profit organization with limited resources and a small engineering team, we need to make prudent decisions about technology selection. Our team has limited bandwidth and expertise, so we need to prioritize solutions that are easy to implement, maintain, and scale. We also want to avoid vendor lock-in and maintain flexibility in our technology stack.

### Decision:

We will prioritize the use of generic open-source products whenever possible. This approach aligns with our values and resource constraints, providing the following benefits:

- **Cost-effectiveness**: Open source solutions often have no licensing fees, reducing our financial burden.
- **Flexibility and Control**: We retain control over our technology stack and can customize solutions to our specific needs.
- **Community Support**: Open source projects often have active communities that provide support and contribute to ongoing development.
- **Avoidance of Vendor Lock-in**: We are not tied to a specific vendor and can switch solutions if needed.
  - In cases where using a commercial product is unavoidable, we will:
    - Abstract the integration point: We will create an abstraction layer to interact with the commercial product, allowing us to switch providers later if necessary.
    - We will prioritize well-tested and "boring" technologies that are widely adopted and have a proven track record. This will minimize the risk of encountering unexpected issues and reduce the need for specialized expertise.

### Consequences:

- Reduced development costs: Open source solutions can significantly reduce development costs.
- Increased maintainability: Well-established open source projects are generally easier to maintain due to community support and documentation.
- Potential limitations: Some open source solutions may have limited functionality or require more effort to integrate compared to commercial alternatives.
- Increased responsibility: We are responsible for maintaining and supporting the chosen open source components.


### Alternatives Considered:

Relying heavily on commercial products: This was rejected due to the potential for vendor lock-in and the higher costs associated with licensing and support.

### Notes:

- We will carefully evaluate open source options to ensure they meet our functional and non-functional requirements.
- We will consider factors such as community activity, documentation quality, and security when selecting open source components.
