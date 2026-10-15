---
id: adrs-adr008
title: "ADR008: Implementation of a back pressure mechanism along with Rate Limiter and Enhanced Circuit Breaker"
description: >
  Architecture Decision Record (ADR) to Implement a back pressure mechanism along with Rate Limiter and Enhanced Circuit Breaker for Client Requests.
---

*Status: [Final]*

## Context:
Our current system is vulnerable to service disruptions and performance degradation when the volume of client requests surpasses the system’s capacity. To mitigate this, we are introducing an integrated back pressure mechanism within the SDK, in conjunction with a rate limiter and an enhanced circuit breaker.

## Decision: 
The back pressure mechanism will be embedded within the SDK. The circuit breaker, as part of the SDK, already performs status checks. If a service status returns as 'degraded', it will also be coupled with an expected waiting time before its back to normal state, and all outgoing calls will be temporarily halted by the circuit breaker. Clients are expected to respect this waiting time before attempting to resend their requests.

In parallel, a rate limiter will be implemented to control the influx of client requests. This limiter acts as a safeguard against clients who may attempt to bypass the back pressure mechanism by directly accessing the services. When the threshold is exceeded, the system will issue a status 429 (Too Many Requests) and provide a specific retry-after time.

The enhanced circuit breaker will adapt to these conditions by automatically opening for the duration specified in the retry-after response when an overload is detected. This strategy ensures the system's stability during high demand periods. The circuit breaker will reset to its normal state after the designated period, allowing operations to resume.

### High level view of the mechanism : 

<h4 style="text-align: center;">Healthy state : No backpressure</h4>

![no_backpressure](https://github.com/pns-si5-al-course/al-newbank-23-24-al-23-24-b-v5/blob/main/adr/images/bp-off.png)

<h4 style="text-align: center;">Unhealthy State : backpressure</h4>

![backpressure](https://github.com/pns-si5-al-course/al-newbank-23-24-al-23-24-b-v5/blob/main/adr/images/bp-on.png)

## Consequences:

### Advantages:
1. **SDK-Integrated Back Pressure:** This mechanism ensures system stability by proactively managing client requests based on real-time service status.
2. **Targeted Rate Limiting:** Acts as a secondary line of defense against clients attempting to bypass the back pressure mechanism, ensuring efficient resource utilization.
3. **Responsive Circuit Breaker:** The improved circuit breaker automatically adjusts its open duration based on the response, preventing excessive calls during periods of high demand.
   
## Disadvantages:
1. **Potential Delay:** Clients will face delays due to the enforced waiting period by the back pressure mechanism and the rate limiter.
