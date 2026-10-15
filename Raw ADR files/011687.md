# 2. Start with a Monolith

Date: 2021-03-15

## Status

Accepted

## Context

HMPPS general policy on microservice development is to [separate user and business interfaces by default](https://structurizr.com/share/56937/decisions#%2FRefer%20and%20monitor%20an%20intervention:1). This is adopted in order to build microservices with bounded contexts, and to
provide business logic APIs from the start.

The above ADR mentions some consequences that are directly relevant to this project, in particular "Contracts between the UI and the service components will take a while to stabilise, creating churn in the beginning."

Our service is intended to be run in a production environment, but is
intended to test a narrow range of functionality with a very small number of users.

Our service replaces some functions currently in nDelius, but data needs to be written back to maintain data integrity. To do this, the service will be reading and writing from existing HMPPS data providers (such as Community API or Assess Risks & Needs) to display and update live data.  Details of data flow and synchronisation will be addressed in a future ADR.

Because data needed by other services will be written back into existing data providers such as nDelius, our service will not be mastering data to be accessed directly by other services for the forseeable future.

In this ADR, we use the following terminology:

* *Monolith*: A single server-side application that renders a user interface, manages data storage, and provides APIs for third parties, within a particular bounded context. No implication is intended around the size of the application itself, or of its context. Small monoliths that only embody a few business processes within a microservices architecture are sometimes referred to as [microliths](https://en.paradigmadigital.com/techbiz/microservices-vs-microliths-vs-monoliths/). However, the term does not appear to be in common use, so while it might be appropriate, we do not use it here.

## Decision

We will initially build the "Manage a Sentence in the Community" product as a single server-side application, following the [MonolithFirst](https://www.martinfowler.com/bliki/MonolithFirst.html) strategy described by Martin Fowler.
The same application will be responsible for user interface, database storage, and communication to external APIs. This
is in contravention of the above HMPPS default, but is appropriate in this case.

We will do this because monolithic applications are quicker to get started with and iterate. A multi-tier architecture
does not confer any advantages at this early stage of development, and adds complexity to the iterative process of an
early-stage application. For our product at this stage we believe that this is a premature optimisation.

Note that this design does not mean that the application stands alone. It will use other MoJ services for access to existing data, or for functionality outside its own bounded context (i.e. authentication). The application will act as a microservice within the HMPPS architecture, but
will not be internally split into a user interface and API backend.

## Consequences

At some point it may be appropriate to split the application into a two-tier architecture that adds a business-level API or
database storage that can be reused by other clients. That change will be documented in an ADR that supercedes this one.

A choice to split the application in future will be based in part on the following criteria:

* Identification of smaller reusable bounded contexts within the application. For instance, calendar integration might be reusable by other services, and be split out.
* Pushing functionality into the browser client. If the user interface becomes more focused on running in the browser for performance or other reasons, a proper _internal_ business logic API will be required.
* If data mastered by this application needs to be exposed to other users, appropriate _external_ APIs will need to be built. These could be built in the monolith, but the team may wish to "dogfood" the APIs by changing our user interface to use them as well.
* Performance issues, such as high volumes of data throughput. If business logic code is properly identified as the bottleneck, it could be split out in order to optimise or reimplement in a higher-performance language.

The internal software design of the application must take care to separate UI and business logic, to take into account that
in future the business logic may need to be exposed via an API or reimplemented in Kotlin. Tight coupling of UI and business logic should be avoided.

These consequences need to be kept under review by HMPPS, to make sure that the ADR still applies and if not, to make a decision to change structure. While active, the team will implicitly keep this decision under review, but if the project does not have a sprinting team building it, an occasional review still needs to be done, especially if development work is to restart.
