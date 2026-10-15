---
id: adrs-adr001
title: 'ADR001: Mitigation of Single Point of Failure : Payment Gateway'
description: >
   Architecture Decision Record (ADR) to Mitigate the Single Point of Failure (SPOF) represented by the Payment Gateway Servive
---

*Status: [Final]*

## Context

The current payment gateway service operates as a Single Point of Failure (SPOF), where all transactions are processed within a single service. This service handles both payment authorization and payment confirmation steps. This configuration poses potential risks to availability and resilience.

## Decision

The decision is to divide the service into two separate services with clearly defined responsibilities:

1. **Authorizer Service:**
   - Responsible for the initial authorization of transactions.

2. **Confirmation Service:**
   - Responsible for confirming the transaction after authorization.

This division into two services aims to reduce the risk of system failure in case of issues with one of the services. The separation of responsibilities also facilitates maintenance, scalability, and more granular issue resolution.

**Architecture Change using Strangler Fig Pattern:**

The adoption of the Strangler Fig Pattern will guide the implementation of this architectural change which involves gradually replacing parts of the existing payment gateway with the new services. 
Here is how we will go about it : 

  1. **Identify Incremental Steps:**
      - Identify components and functionalities within the existing payment gateway service that handle the authorization process and confirmation process.
  2. **Build New Authorizer Service:**
      - Extract, adjust, build and run the new authorization service alongside the existing payment gateway.
  3. **Gradual Migration:**
      - Gradually route authorization requests through the loadbalancer to the new Payment Authorizer Service while still using the existing service for other functionalities.
  4. **Monitor and Test:**
      - Monitor the performance and reliability of the new service.
      - Conduct end-to-end testing to ensure freedom from regressions.
  5. **Repeat for Confirmation Service:**
      - Apply the same steps for the confirmation service.

This phased approach ensures minimal congnitive overload, allows for end to end testing, and facilitates a smooth transition from the monolithic payment gateway to the split services for authorization and confirmation.

**Payment Gateway Architecture: Before and After Splitting :**

Before :
![Architecture Before](https://github.com/pns-si5-al-course/al-newbank-23-24-al-23-24-b-v5/blob/main/adr/images/spof-before.svg)
After :
![Architecture After](https://github.com/pns-si5-al-course/al-newbank-23-24-al-23-24-b-v5/blob/main/adr/images/spof-after.png)

## Consequences

### Advantages:
1. Reduction of SPOF and improve of availability: Dividing the PaymentGateway Service into two services reduces the risk of system failure, enhancing overall reliability.
3. Ease of maintenance and scalability: Clearly defined responsibilities of authorization and confirmation services allow for more efficient maintenance, scalability, and targeted updates.

### Disadvantages:
1. Increased complexity in terms of coordination between services and additional critical points to handle
