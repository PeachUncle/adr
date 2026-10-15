# Security

* Status: Accepted
* Deciders: Habib Ullah, Rami Kotaiche, Casey Cheung
* Date: 2024-11-28

Technical Story: Sensitive user data and credentials must be protected using robust security measures to comply with GDPR and industry standards.

## Context and Problem Statement

The system handles personal and financial data, requiring stringent security protocols to protect against unauthorized access and breaches. Failing to implement good protection could result in user distrust, legal penalties, and reputational damage.

## Decision Drivers

* Compliance Requirements: Adheres to GDPR and industry security standards.
* User Trust: Users must feel confident that their data is secure.
* Risk Mitigation: Keep vulnerabilities to breaches and unauthorized access as low as possible.
* Future Proof: Ensure solutions are adaptable to growing security threats.

## Considered Options

* End-to-End Encryption with Best Practices
* Basic Obfuscation Techniques

## Decision Outcome

Chosen option: "End-to-End Encryption with Best Practices", because We chose End-to-End Encryption with Best Practices to ensure protection of sensitive data and compliance with GDPR. By including industry-standard encryption for data in transit and at rest, along with secure key management practices, the system will keep risks of breaches and unauthorized access as low as possible.

### Positive Consequences

* Ensures GDPR compliance and user trust.
* Reduces risk of data breaches through strong encryption.

### Negative Consequences

* Requires ongoing updates to address evolving security threats.

## Pros and Cons of the Options

### End-to-End Encryption with Best Practices

Implementation of strong encryption algorithms to secure data during storage and transmission, along with practices like secure key management.

* Good, because - Highest level of data protection.
- Builds user trust and ensures compliance.
* Bad, because - Resource-intensive.
- Requires ongoing updates to address evolving threats and encryption standards.

### Basic Obfuscation Techniques

Simple data masking or scrambling to make data less readable.

* Good, because - Easy to implement.
* Bad, because - Easily reversible and insecure.
- Does not meet GDPR requirements for data security.

## Links

* European Union. (2018). General Data Protection Regulation (GDPR) compliance guidelines. Retrieved November 28, 2024, from https://gdpr-info.eu
* OWASP Foundation. (n.d.). Encryption best practices. Retrieved November 28, 2024, from https://owasp.org
