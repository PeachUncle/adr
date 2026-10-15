# 4. Copy nDelius Application Logic

Date: 2021-02-03

## Status

Accepted

## Context

nDelius is currently the foundational system for the National Probation
Service, holding most of the information about the activities of the service
and its users. As new digital services, with a more focused scope, are created
there is often a need to exchange data with nDelius. New services must read
data from nDelius to determine the current state of an activity and write data
to nDelius to reflect activity that has occured outside of the application
boundary. It is currently possible to interact with the nDelius database
directly using Community API, however, this method bypasses the nDelius
application tier. Bypassing the application logic for read operations results
in actions such as audit log writes and data access restrictions needing to be
applied as a secondary concern. While this is possible it relies on the
consumer understanding the necessary actions and executing the correct steps
as part of their service logic. Bypassing the application logic for write
operations means complex data validations are not run and any associated
processing, such as linked appointments being created as part of a specific
Contact creation, is not executed. Consequently writing data to nDelius via
Community API requires a deep knowledge of the internals of the foundational
application and re-implementation of any essential logic in Community API
code. In addition, due to the potential impact on the main nDelius application
of changes Community API, write operations also require extensive testing to
be scheduled and actioned by the NDST team before release beyond development
environments.

The intention of Delius API is to provide endpoints that encapsulate and
expose the nDelius application logic to the new digital services. This reduces 
the knowledge needed when integrating allows reuse of tested endpoints in
multiple services. To do this we need to ensure the API application can
execute the correct logic and that this logic is kept in line with the main
nDelius application. There are various options for doing this:

### Refactor the nDelius Application Logic into a Shared Library

Refactor the logic out of the main nDelius application and create
a shared library component that can be imported and used by both the main
application and the API service. This strategy maintains a single, canonical,
source of truth for the logic and allows for management of the component using
semantic versioning. The application logic is tied to the nDelius database
model (the PDM) and a versioned component would help make the link between the
logic and the PDM explicit. A versioned component would also aid change
management of application logic across the two systems. The drawbacks of this
method are that the upfront work to refactor the logic is significant and
there is a need to work within the main nDelius application. Given the current
workload of the NDST team and the focus on Day 1 deliverables this is not
likely to be possible.

### Deploy the Delius API into a Shared Application Container and Use Remote EJB Calls

The nDelius application components are currently implemented as EJBs.
Theoretically we could deploy the API application into the same application
container as the main application and make remote EJB calls to execute the
logic. This would avoid duplicating the application logic, however, it would
mean the API application would be closely tied to the main application. The
close coupling of both application deployment and runtime would limit the
benefit of the API application in that it is unlikely we would be able to
deploy the API on a faster cycle and would not have the ability to change the
application logic in any way at all. The need to deploy to a WebLogic would
also severely constrain the way the API application is built and mean that we
cannot use the standard patterns of the Digital Studio.

### Copy the Application Logic and Manually Synchronise Changes Over Time

Take small, specific elements of the nDelius application logic and copy this
into a service layer of the API application. This would introduce duplication
of the logic across the two systems which would need to be managed as part of
the development flow of nDelius, the nDelius PDM and the nDelius API. The main
advantage of this method is that we would be able to move quickly to create
an MVP API application targeted at supporting the Day 1 activities without the
need for complex infrastructure work on nDelius. It also means the technical
choices of the API application are unconstrained and the Digital Studio
patterns and supporting tools, knowledge and experience can be fully
leveraged. 

## Decision

We will copy the application logic and manually synchronise changes over time.

## Consequences

The decision to duplicate the application logic has been taken as a way of
minimising dependencies and enabling a small, focused MVP to be built without
the constraints of the existing application. It is clear that there are
significant drawbacks to this method around change management across the two
applications and the PDM. These drawbacks may only manifest over a period of
time. This decision should be reviewed regularly to ensure what we are
building is manageable over the long term as it is likely that the duplication
will persist for a significant period. As the API application is intended to
initially only support a small subset of the nDelius application logic this
may not be a problem. However, the decision may place constraints on the type
and number of endpoints the API can provide. 

The major impact of the decision is on the NDST team, as the ultimate managers
of both nDelius and the Delius API. It is expected that the acceptance
criteria of the new API will explicitly include an acceptance of this extra
overhead. The Delius API team expects to help with planning and input on how
best to manage the parallel development of the two system going forward. 

To mitigate the duplication of logic it is possible that the API application
could become the single, canonical source of truth for the logic over time.
This would involve the main nDelius application making calls to the API
application as needed. Although this is technically feasible it would require
explicit effort and prioritisation from NDST and whether this is possible and
on what timescale it could happen is currently unknown.
