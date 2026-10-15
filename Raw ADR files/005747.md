---
id: adrs-adr003
title: 'ADR003: Retry Mechanism for payment calls in sdk '
description: >
   Architecture Decision Record (ADR) to implement retry Mechanism for payment calls in sdk
---
*Status: [Final]*

## Context
Our system relies on payment services (payment gateway authorizer and payment gateway confirmation) for critical functionality, and we have observed intermittent failures during peak usage times. These failures appear to be transient and are due to increased load on payment services. To ensure the reliability of our sdk, we need to make a decision on how to handle these transient failures.

## Decision
We will implement a retry mechanism for payment calls to address transient failures faced.

## Options Considered
* Fixed Retries: Allow for a fixed number of retries for each failed payment call.
* Exponential Backoff: Use an exponential backoff for retries, increasing the delay between successive retrial attempts.
  
##  Decision Rationale
After considering the options, we have decided to implement the exponential backoff strategy. This decision is based on the understanding that transient failures may occur due to temporary spikes in payment service load. Exponential backoff allows us to gracefully handle such situations by increasing the time between retries, reducing the load on the failing services.

### Example of Retry Strategy with the SDK :
<img src="https://github.com/pns-si5-al-course/al-newbank-23-24-al-23-24-b-v5/blob/main/adr/images/retry.png" width="500" height="500" alt="Example">

## Consequences
* Payment calls will be retried using an exponential backoff strategy, and clients can configure the retry mechanism with default values:

      `retries : 3`
  
      ` factor: 2`

      ` minTimeout: 1000`
  
      ` maxTimeout: 3000`
  
      ` randomize: true`

* Failed payment calls and retry attempts are logged
* Retry attempts are not considered as metrics; only failed payments are. 
* The system will be more resilient to transient failures, reducing the impact of payment service fluctuations on overall system reliability.
  
## Additional Documentation
[Exponential backoff](https://advancedweb.hu/how-to-implement-an-exponential-backoff-retry-strategy-in-javascript/)
