# Cloudflare Chosen for AI Assistant Hosting

- **Status**: Accepted
- **Decider**: Team AI Assistant, including user and collaborators
- **Date**: 2025-02-12

## Context and Problem Statement

I am planning to implement an AI assistant to help visitors of my portfolio website summarize content more effectively and enable hiring managers to dynamically engage with my experiences and working style.

To achieve this, I need to implement and maintain an infrastructure capable of supporting:
- A **Backend API** to process questions and handle AI tasks.
- A **ChatRoom Frontend** for seamless interaction with users.
- **Infrastructure that minimizes costs and enhances maintainability**, enabling:
  - Continuous Deployment (CD) for always-up-to-date AI models and content.
  - Reliable Hosting for both the API and the ChatRoom.

This document determines the **hosting architecture and infrastructure tools for this project**, striking a balance between simplicity, performance, and cost-effectiveness, while ensuring the platform can scale with future needs.

## Decision Drivers

Our key priorities when selecting infrastructure are:

1. **Pay by Request**
  - The platform should follow a pay-per-use model with a free tier, ensuring there are no costs incurred if no requests are made. This keeps the project budget-friendly during development and in low-traffic periods.

2. **Feature-Rich**
  - The platform should provide built-in tools for hosting, API processing, or serverless functionality, and allow easy configuration for continuous deployment (CD) workflows.

3. **Minimal Configuration**
  - The platform should require minimal setup and configuration, allowing quick development cycles without being bogged down by infrastructure management.

4. **Future-Proofing**
  - The platform should have the ability to evolve with the project’s needs, such as scaling to handle occasional traffic spikes or integrating additional features over time.

## Considered Options

The two platforms considered for hosting both the **API backend** and **ChatRoom frontend** are:
1. **Google Cloud Platform (GCP)**: Cloud Run for running serverless containers and Cloud Storage for static content, managed using Terraform for IaC (Infrastructure as Code).
2. **Cloudflare**: Workers and Pages for serverless backend and static frontend hosting, with infrastructure managed using Wrangler.

---

## Decision Outcome

- **Chosen Option**: **Cloudflare**
  - Cloudflare was selected due to its simplicity, speed, and generous free tier, making it ideal for a low-cost initial implementation.

### Positive Consequences

- Easy and fast deployment using Cloudflare Workers and Pages.
- Cost-effectiveness for small-scale, low-traffic projects due to the generous free tier.
- Built-in developer-friendly tools, like Wrangler CLI, simplify both setup and deployments.

### Negative Consequences

- Potential vendor lock-in due to custom APIs for configuring Workers and Pages.
- Limited native debugging support for backend issues, as Cloudflare does not provide full `stdout` logging.

---

## Risks and Mitigations

- **Risk 1**: Vendor Lock-in
  - **Explanation**: Cloudflare’s custom runtime and configuration may make it difficult to migrate to other platforms in the future.
  - **Mitigation**: Use generic APIs and maintain a simple, modular architecture in code to make migration easier when needed.

- **Risk 2**: Debugging Challenges
  - **Explanation**: Cloudflare’s lack of traditional `stdout` logging could make identifying and fixing backend errors more difficult.
  - **Mitigation**: Utilize Cloudflare’s advanced Logpush capabilities or integrate third-party monitoring tools, and use local Wrangler CLI tools for development before deploying code.

---

## Future Considerations

- As the project grows, consider revisiting GCP Cloud Run for complex backend needs or advanced scalability requirements.
- Periodically review Cloudflare’s pricing model to ensure it remains cost-effective for future traffic needs or added features.
- Evaluate the feasibility of hybrid deployment models (e.g., using GCP for the backend and Cloudflare for the frontend) if specific limitations arise.

---

## Pros and Cons of the Options

### GCP

| **Aspect**              | **Pros**                                                                                     | **Cons**                                                                                 |
|--------------------------|---------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| **Deployment Model**     | Supports deployment using Dockerfiles, providing full control over the runtime environment. | Slower deployment times due to Docker build overheads, often taking several minutes.    |
| **Debugging**            | Extensive logging support, captures all `stdout` and offers detailed metadata logging.       | Setup complexity for logging pipelines and metadata visibility without IaC tools.       |
| **Configuration**        | Suitable for highly complex solutions with specific deployment requirements.                 | Higher learning curve and configuration effort when using Terraform or similar tools.   |
| **Cost**                 | Free tier available for Cloud Run and Cloud Storage.                                        | Pricing can escalate due to the overhead of managing containers and storage resources.  |  

### Cloudflare

| **Aspect**              | **Pros**                                                                                     | **Cons**                                                                                 |
|--------------------------|---------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| **Deployment Speed**     | Extremely fast provisioning and deployment using Wrangler commands (under 1 minute).         | Lack of native Dockerfile-based deployment may limit certain backend setups.            |
| **Free Tier**            | Generous free tier with nearly zero cost, and no credit card is required to start.          | Drawbacks if project scales beyond free limits (e.g., expensive add-ons for specific use cases). |
| **Tooling**              | Developer-friendly tools (e.g., Wrangler CLI) with highly simplified configuration.          | Debugging is limited due to lack of traditional `stdout` logging; requires workarounds. |
| **Feature Set**          | Built-in support for modern web hosting features including serverless functions and CD.       | Vendor lock-in risk due to custom deployment/configuration mechanisms.                  |  

---

## Links

- [Cloudflare Workers Documentation](https://developers.cloudflare.com/workers/)
- [Cloudflare Pages Documentation](https://developers.cloudflare.com/pages/)
- [Wrangler CLI Documentation](https://developers.cloudflare.com/workers/wrangler/)
- [GCP Cloud Run Documentation](https://cloud.google.com/run/)
- [Terraform Documentation](https://developer.hashicorp.com/terraform/docs)