# 2. Microservices vs Event driven architecture style

Date: 2023-09-14

## Status

Accepted

## Context


After qualifying the  [requirements](./doc/arch-char.md) into valid architecture characteristics 
we found the following aspects be the driving characteristics.

- Performance
- Responsiveness
- Availability
- Elasticity

Furthermore, we identify that

- The key feature of the system is to act upon the **event** when an update in booking as taken place in original system and reflect in the system in real time. This event should trigger workflow to update the booking details in our system and notify the user.

- Another flow of receiving booking details from email is similar in nature. In particular, an **event** of receiving an email is with booking details, triggers the flow to add/update the booking into system. 

- System has strong analytics use-cases for which data will be moved from booking storage to analytics storage, see [ADR-0003](/doc/adr/0003-dedicated-db-for-analytics-usage.md). Along with benefits of event driven arch style, with growing demand of near real time data for analytics, it makes strong case to consider update in booking system as event which triggers copy of the data to analytics storage. 

Microservices is a revolutionary arch style and offers great value in many characteristics including scalability and elasticity but lacks severally in performance and cost. Along with this, since we do not have many services, it will add additional complexity to have microservices architecture implemented in this case. 

On the other hand, The system requirements are around event based solution and Event driven arch style scores astonish well in performance and fault tolerance. It is not the costliest and does quite well in elasticity. 

## Decision

We will implement an **Event-driven** architecture.

## Consequences

### Positive

- Performance
- Responsiveness
- Less moving parts
- Near real time analytics data
- Cost

### Negative

- Error Handling is difficult
- Difficult to test

| [🏠 home](../../README.md#adr) | [<< **ADR** Space based architecture style ](./0001-arch-style-space-based.md) | [**ADR** Dedicated storage for analytics >>](./0003-dedicated-db-for-analytics-usage.md) |