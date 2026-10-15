# Making a decision on how to best secure my system

## Context and Problem Statement

The CMS will be handling sensitive customer data for large banking and Telecom organisations across multiple different tenants. The system will need to ensure that only authorised users can access the correct information for their company. With Millions of potential users and being required to conform to regulations (GDPR), the system will require strong security to be put into place to protect confidential data, maintain tenant isolation, and ensure that the system is safe to use.

## Considered Options

* **Role Based Access Control (RBAC)**
* **Encryption & Hashing**
* **Single Sign On (SSO)**
* **Local Login Only (Doesn't use SSO)**

## Decision Outcome

Chosen option: ***"RBAC, Hashing + Encryption (HTTPS), and SSO"***, because these features combined will allow the CMS to meet the security needs for managing all of these different industries under one roof. RBAC will ensure that users can only access features suitable to their role. Hashing and encryption will keep user credentials and sensitive data safe (e.g. Hashing sensitive data & making API requests through HTTPS). Single Sign On will allow all employees of each company to securely get access to the system using their work credentials, lowering the risks of having their personal credentials being breached.

### Consequences

* Good, because RBAC will ensure that each role (e.g. Consumer, Agent, Manager and Administrator) can only access what they are allowed to, which will improve the overall security of the system and provide some tenant isolation.

* Good, because hashing (passwords + sensitive information) and encryption (secure api requests) will ensure that if the database were to be compromised in any way or packets were to be intercepted during requests then there will be preventitive security methods, stopping the attackers from reading/viewing the data. 

* Good, because SSO should allow organisations to implement their own autentication systems for their credentials, improving security and user experience.

* Bad, because implementing SSO will introduce more complexity for the system.

* Bad, because managing RBAC permissions can get tedious and will likely take up more time and add to development time, should new features be added in the future.
