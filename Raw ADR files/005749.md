---
id: adrs-adr006
title: "ADR006: Implementation of Timeout Pattern"
description: >
  Architecture Decision Record (ADR) to implement of Timeout Pattern
---
*Status: [Final]*

## Context:

Incoming calls from the SDK to our system goi through many critical dependency chains. For example, when the SDK is requesting an authorisation from the Payment Gateway authorizer service, the latter orchestrates the authorization by interfacing with the Credit Card Network (CCN) service, which, in turn, communicates with external bank system. 

This intricate dependency structure poses a potential risk of network performance issues, leading to prolonged waits and indefinite blocking during service calls. Such challenges can significantly impact the overall responsiveness and reliability of the payment authorization process.

This diagram illustrates an example of this dependency chain : 

![Timeout](https://github.com/pns-si5-al-course/al-newbank-23-24-al-23-24-b-v5/blob/main/adr/images/timeout.png)

## Decision:

To proactively address the risk associated with potential network performance issues and indefinite blocking during service calls, we propose the implementation of the Timeout Pattern. This strategic pattern involves setting time limits for service calls. Also, to ensure comprehensive coverage, the Timeout Pattern will be integrated into the SDK, enabling clients to benefit from timely responses and preventing indefinite blocking at the client level.

## Implementation Plan

1. Timeout Configurations: Set timeout limits for all service calls based on response times, network latency, and acceptable system responsiveness.
2. SDK Integration: Add Timeout settings to the SDK. Developers using our SDK can pick their own timeout limit for the functions they use, preventing indefinite blocking on their side.

## Risks and Considerations

- **Configurability:** Ensuring that the timeout values are configurable and adjustable based on different service requirements and environmental conditions.
- **Degradation of serivce quality:** In peak times, having too many timeouts can lead to a degraded service quality felt by the end user when receiving many failed attempts.

## Consequences:

* Improved system responsiveness by avoiding prolonged waits for unresponsive services.
* Mitigation of potential performance bottlenecks due to indefinite blocking during service calls.
* Enhacing Resilience against fluctuations in network conditions or temporary service unavailability.
