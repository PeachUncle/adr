---
id: adrs-adr004
title: "ADR004: Retrieving Backend Services Status"
description: >
  Architecture Decision Record (ADR) to implement a status retrieval for backend services
---

*Status: [Final]*

## Background

Our SDK as is, doesn't perform any healthcheck before sending requests to the backend services. It is only dealing with errors as they arise, and the status of the service being requested is not provided nor clear to the end user of the SDK.

## Context

The context for this ADR is to address the client need to retrieve the status of the services that the SDK is querying.Our SDK users need to know the status of the backend services to ensure the reliability of their applications. We need to provide them a way to check the state of the backend services explicity, and additionally perform said checks within the provided SDK before performing the service calls.

## Decision

To address this need, we have decided to : 
- Create a new service : **Status Reporter**. This service will be responsible for querying our internal Prometheus server to determine the status of backend services.
- Provide the client with an API to interact with the newly created backend service.

As our prometheus is configured to scrape all services for their metrics, the up status is already provided with additional useful information to the **Status Reporter**.

Given the potentially high frequency of calls from various SDK clients on this status reporting service, we have chosen to implement a cache-aside strategy with a TTL of 1 second to reduce the possible number of calls on the Prometheus server down to 1 call every second.

#### Code snippet of the API : 

```JS 
  const newBankClient = new NewBankClient(clientToken);
  const servicesStats = newBankClient.getBackendStatus();
```

The status retrieval call should return a list of the services with their status : 
- UP : denoting an up and running healthy service
- DOWN : denoting a service that stopped, crashed or just unable to be reached anymore
- DEGRADED : denoting a service that is potentially low on resource and/or processing too many requests in the meantime

#### High-level view of the architecture and the interactions : 

![Architecture](https://github.com/pns-si5-al-course/al-newbank-23-24-al-23-24-b-v5/blob/main/adr/images/service-status.png)

## Consequences

### Advantages:
- Visible and comprehsenbile services statuses instead of performing direct calls to the business backends.
- Prometheus server is protected from overload thanks to the read-through caching strategy

### Disadvantages:
- Given the use of the cache read-through strategy there is a potential risk of conccurent changes in the cache as well as the same status result being returned to everyone.
- A lag behind the services' real status by one second.
