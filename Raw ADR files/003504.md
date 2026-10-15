# ADR.4 High Availability and Disaster Recovery

This document provides thoughts and recommendations related to overall survivability of the system, and its particular
components for the cases of natural disasters, blackouts, hardware failures, and even deployment of new releases.

## Status `APPROVED`

## Rationale

As per 99.98% availability requirement the system should be geographically distributed and run redundant application
instances for faster switchover to an instance that is capable of serving traffic.

### Geographical distribution

Geo distribution of services refers to the practice of distributing services across various geographical locations. It's
a key component of business strategies, particularly for companies with broad-ranging operations or those which cater to
customers worldwide.

In the event of a disaster at one location, having services distributed geographically means that other locations can
keep the operation going, thus minimizing or preventing service interruptions.

The closer the server or data center to the user, the faster and more efficiently the service can be delivered. This
reduces latency, increasing the speed of service delivery.

It's also worth mentioning that some jurisdictions require data to be stored or processed locally, necessitating a
geo-distributed service model.

### Component redundancy

As a rule of thumb, more than one instance of an application should be running at a time. Depending on the processing
logic, they can be Active-Active instances behind a load balancer (e.g., components that serve API requests); or
Active-Follower instances in cases when only one instance is allowed to do actual work. Either way, if one of the
instances goes down, another one takes over faster, since it's already running and don't need time to warm-up. This
minimizes loss of data in application failure cases.

### Blue-green deployments

Blue-green deployment is a strategy for updating applications in a way that minimizes downtime and reduces risks
associated with releasing new versions.

In simple terms, imagine you have two identical environments - the "blue" environment and the "green" environment.

The "blue" environment is the live or production environment that is currently serving all the traffic/users. It has
the current version of your application.

The "green" environment is an exact replica of the blue environment, but with the updated version of your application.
This is set up and tested, without impacting the live environment and users.

When the time comes to deploy the update, you simply switch the traffic from the "blue" environment to the "green" one.
This should be a seamless process that is almost or entirely unnoticed by the users.

If something goes wrong in the "green" environment after the deployment, you can easily switch back to the "blue"
environment. This minimizes the potential downtime or impact on users.

The fundamental goal of blue-green deployment is to provide a safe and quick way to release and revert application
updates with little to no downtime.

### Graceful shutdowns

Graceful shutdown of application minimizes or eliminates loss of requests in case if application is needed to be
intentionally stopped (e.g., during a deployment of a new release). The correct graceful shutdown procedure is based
on certain delays, properly configured for a particular runtime environment.

* Pre-wait delay allowing load balancers to re-route traffic to other instances.
* Graceful shutdown delay that specifies a period when application do not accept new requests but trying to process
  all those already in the queue.
* Shutdown timeout gives application time to finish its tasks properly, including closure of the shared resources,
  e.g. database and network connections.

## Decision

1. The product should be deployed to two or more geographically distributed sites, meaning physical datacenters or
   cloud regions. This concern both product and infrastructure components:
    1. Database should be replicated/sharded across regions.
    2. Message brokers should be spread across regions.
    3. Data volumes should be replicated and highly available.
2. On each site, at least two instances of every time- or data- critical component should be run at a time.
3. Rollout of a new release should be without interruption of service in technique known as blue-green deployment. 
   We don't really need nor want (for the sake of saving resources) two real environments, "green" and "blue". Instead,
   the deployment mechanism should be able to start up "green" nodes one by one and re-route traffic to them, whilst 
   "blue" nodes are excluded from load balancing one by one and then stopped. 
4. The development team should make best efforts to ensure code sustainability and minimization of data loss (e.g.
   loss of incoming requests). Transactional processing, correctly implemented shutdown logic is a must.

These decisions fit well on cloud infrastructure, which will be covered in more detail in
ADR.5 [Cloud Deployment](cloud-deployment.md).

## Consequences

Positive:

* High system availability and reliability.

Negative:

* Additional costs for maintaining redundant infrastructure.