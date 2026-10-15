# 3. Create Generic Rather Than Application-Specific Endpoints

Date: 2021-02-01

## Status

Accepted

## Context

The API endpoints we provide determine the utility of the API service for a
variety of potential clients. Providing more generic endpoints (e.g. /contact)
gives flexibility and enables use of the API service to achieve goals that are
not fully specified ahead of time. There are drawbacks to generic API
endpoints, however, in that the client must know more about the implementation
details of nDelius in order to correctly use the service. Endpoints may expose
the internal nDelius data model (e.g. Contacts and NSIs) and these entities
may only make sense when created as a set. By providing generic APIs we enable
certain entities to be created in isolation and potentially left unlinked. It
is also necessary to know the details of the data that must be supplied to the
endpoints in order to achieve specific goals (e.g. what Contact Type must I
supply to create an Appointment?).

In contrast providing a higher-level, more specific API endpoint (e.g.
/DFInterventionAppointment) allows greater encapsulation of implementation
details and requires less detailed knowledge of the 'correct' way of using the
system. The drawback of this method is needing to provide specific APIs for
each client wishing to use the service ahead of time.

## Decision

To begin with we will provide generic APIs for specific entities within
nDelius, however, we will only allow a small, defined subset of types to be
used in create operations.

## Consequences

We expect that creating generic endpoints, initially for Contacts and NSIs
will enable us to support both the Interventions and Probation End-to-End use
cases. Creating a small, authorised list of Contact Types and NSI Types that
can be used when creating these entities should limit the possibility for
accidental misuse whilst allowing us to extend the client use-cases in a
managed but low-overhead way.

If we need to provide API endpoints that group calls to the nDelius API to
achieve certain complex actions we can make use of Community API to do this.
