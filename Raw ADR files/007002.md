# Hosting

* Status: Accepted
* Deciders: Habib Ullah, Casey Cheung, Rami Kotaiche
* Date: 2024-11-12

Technical Story: The hosting solution must handle variable user loads efficiently, provide high availability, and support disaster recovery.

## Context and Problem Statement

The application needs a reliable hosting solution that supports variable user loads, has high availability, and allows for quick disaster recovery. The hosting must also integrate well with other components and support global deployment.

## Decision Drivers

* Scalability: Ability to handle different user demands across multiple platforms.
* High Availability: Keeping downtime as low as possible.
* Cost Efficient: Best possible cost without affecting performance.

## Considered Options

* AWS Cloud
* Google Cloud Platform (GCP)
* On-Premises Hosting

## Decision Outcome

Chosen option: "AWS Cloud", because AWS Cloud was selected as the hosting solution for its largee range of managed services, global infrastructure, and great scalability. AWS enables the system to handle variable user loads, supports high availability and provides robust disaster recovery options.

### Positive Consequences

* Highly scalable and supports global deployment.
* Offers extensive managed services for databases, authentication, etc.
* Pay-as-you-go model optimizes costs.

### Negative Consequences

* Dependence on a single cloud provider can lead to vendor lock-in.
* Initial learning curve for configuring AWS services efficiently.

## Pros and Cons of the Options

### AWS Cloud

A cloud service provider offering a wide range of scalable and globally distributed infrastructure solutions.

* Good, because - Comprehensive service offerings and global infrastructure.
- Pay-as-you-go pricing model keeps costs based on usage.
* Bad, because - Vendor lock-in risk.
- Initial learning curve for configuring and optimizing AWS services.

### Google Cloud Platform

A cloud service provider focused on integrating cloud hosting with advanced AI/ML capabilities.

* Good, because - Strong AI/ML integrations.
* Bad, because - Smaller ecosystem compared to AWS.

### On-Premises Hosting

A traditional hosting model where all infrastructure is owned and managed on-site.

* Good, because - Full control over infrastructure.
- Not dependent on third-party providers.
* Bad, because - High initial setup and maintenance costs.

## Links

* Amazon Web Services (AWS). (2024). AWS global infrastructure and services overview. Retrieved November 12, 2024, from https://aws.amazon.com
* Google Cloud Platform (GCP). (2024). Cloud hosting and AI/ML capabilities. Retrieved November 12, 2024, from https://cloud.google.com
