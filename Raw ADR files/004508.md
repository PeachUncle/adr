---
status: "accepted"
date: {2024-01-06}
deciders: {Sushain Garg}
---
# Encryption at Rest and in Transit for Visa Application System

## Context and Problem Statement

### The Visa Application System (VAS) stores and transmits sensitive personal data, including:
* Personal information (PII)
* Passport details
* Financial information
* Potentially health records
### Regulatory compliance (GDPR, HIPAA, etc.) and industry best practices mandate robust data protection measures.
### Encryption at rest and in transit is essential to:
* Safeguard data confidentiality and integrity
* Prevent unauthorized access and data breaches
* Mitigate the impact of potential system compromises


## Decision Drivers

* Data Protection Compliance: Adhere to strict legal requirements for safeguarding sensitive personal data.
* Security Best Practices: Implement industry-standard encryption techniques for comprehensive protection.
* Data Breach Prevention: Render stolen data unreadable without appropriate decryption keys.
* User Privacy: Protect confidentiality and integrity of user information to maintain trust.

## Considered Options

* Encryption at rest and in transit for all sensitive data
* Partial encryption or limited data security measures

## Decision Outcome

Chosen option: "Encryption at rest and in transit for all sensitive data", because
it Provides the most comprehensive protection, aligns with regulations, best practices, and ethical obligations.


## Consequences

### Good 

* Enhanced data security and compliance
* Protection against unauthorized access, data breaches, and cyberattacks
* Reduced risk of sensitive data exposure in case of system compromises

### Challenges

* Performance overhead due to encryption/decryption (needs evaluation and optimization)
* Need for secure key management and access control
* Increased complexity in configuration and maintenance

## Technical Implementation Details

### Encryption at Rest

* Utilize AWS encryption services (KMS, EBS encryption, S3 encryption) for data storage and backups.
* Evaluate MongoDB's native encryption features for database-level protection.

### Encryption in Transit

* Mandate HTTPS for all communication between application, services, and users.
* Enforce TLS for service-to-service communication within the microservices architecture.
* Implement secure key exchange mechanisms (e.g., Diffie-Hellman) for initial setup.

### Key Management

#### Establishing a robust key management strategy, including:

* Secure key generation, storage, and rotation
* Access control mechanisms to protect encryption keys
* Logging and auditing of key usage
* Consider integration with AWS Key Management Service (KMS)

## Confirmation

### Compliance will be confirmed through:

* Code reviews
* Security audits
* Network traffic analysis
* Data storage configuration checks
* Key management practices

