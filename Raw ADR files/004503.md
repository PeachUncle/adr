---
status: "accepted"
date: {2024-01-06}
deciders: {Sushain Garg}
---
# Host the Visa Application System on Amazon Web Services (AWS).

## Context and Problem Statement

The Visa Application System requires a reliable, scalable, and secure hosting platform to support its features and user base. The system will be developed using a MERN stack (MongoDB, Express, React, Node.js) with Redux Toolkit, and a cloud-based solution is preferred for its flexibility, scalability, and cost benefits.

## Decision Drivers

* Scalability: The system must handle anticipated growth in user traffic and data volume.
* Security: Sensitive user data and application functionality must be protected from unauthorized access and breaches.
* Cost: Hosting costs should be optimized while meeting performance and security requirements.
* Global Reach: The system may need to serve users in multiple regions with low latency and compliance with regional regulations.
* Managed Services: AWS offers a wide range of managed services that can simplify deployment, maintenance, and scaling of the application.


## Considered Options

* Cloud hosting on AWS
* On-premises hosting
* Other cloud providers (Azure, Google Cloud)

## Decision Outcome

Chosen option: "Cloud hosting on AWS", because
AWS provides a globally available infrastructure with high scalability, robust security features, managed services to reduce operational overhead, and cost-effective pricing models that align with the project's requirements.

### Consequences

* Good, because Enhanced scalability to handle fluctuating user demand and data growth.
* Good, because Improved security with AWS's comprehensive security tools and compliance certifications.
* Good, because Reduced operational overhead through managed services like databases, load balancing, and security groups.
* Good, because Potential cost savings compared to on-premises hosting, especially at scale.
* Good, because Access to a wide variety of AWS services and integrations.
* Bad, because Need for expertise in AWS cloud infrastructure and services
* Bad, because Ongoing costs associated with cloud services.
* Bad, because Potential vendor lock-in with AWS services.


### Confirmation

Compliance with this ADR will be confirmed through regular infrastructure reviews and audits to ensure the system is hosted on AWS services and configured according to best practices.

