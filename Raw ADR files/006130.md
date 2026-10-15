# ADR-005: Payments

### Date: 2024-09-30

### Status: Proposed

### Decision Maker: Engineering Team

### Context:

Our Clearview application needs to process payments for services like resume unlocking (pay-per-view or subscriptions). We need to integrate with a payment gateway that is secure, reliable, and cost-effective for a non-profit organization.

### Decision:

We will integrate with a payment gateway that offers:

- Low transaction fees: Minimize costs for our non-profit organization.
- Easy integration: Reduce development time and effort for our small engineering team.
- Strong security: Protect sensitive financial data.
- Reliable service: Ensure consistent uptime and minimal disruptions.
- Good service level in the US: Our primary user base is in the US.


Based on research and considering our specific needs, we will evaluate the following options:

**Stripe**: Popular and widely used, known for its developer-friendly API and robust features.   
**PayPal**: Ubiquitous and trusted by users, offers a variety of payment options.   

We will conduct a detailed comparison of these options, considering factors such as:

- Transaction fees for non-profits: Identify the most cost-effective option.
- Ease of integration with our technology stack: Evaluate API documentation and available SDKs and how easy its to integrate.
- Security features and compliance certifications: Ensure data security and regulatory compliance.
- SLA's and customer support: Assess reliability and responsiveness.
- Popularity among similar non-profits: Learn from the experiences of other organizations.


### Consequences:

- Secure and reliable payment processing: Enable seamless and secure transactions for our users.
- Reduced development effort: Choose a payment gateway with easy integration.
- Cost-effectiveness: Minimize transaction fees.
- Potential vendor lock-in: Mitigate this risk by abstracting the integration layer.

### Notes:

- We will document the final decision and rationale for choosing a specific payment gateway.
- We will implement appropriate security measures to protect sensitive payment information.
- We will monitor the performance and cost of the chosen payment gateway on an ongoing basis.

  