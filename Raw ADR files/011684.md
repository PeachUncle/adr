# 6. Authenticate Using OAuth2 Client Credentials Grant

Date: 2021-02-26

## Status

Accepted

## Context

Within the HMPPS application environment we are able to use HMPPS-Auth as a
OAuth2 provider. Using HMPPS-Auth we have the ability to identify a user using
Delius as an Identity Provider, with the authenticated user details passed in
the user\_name and user\_id fields of the access token. For users with Delius
accounts this enables us to apply fine-grained access control based on the
user. There are a number of reasons, however, why this is not a viable
strategy, primarily that our user base do not all have nDelius accounts. In
fact, many end-users of the services that will rely on the Delius API are
external to the MoJ organisation. In cases where users do have an nDelius
account they may also have a NOMIS account and we cannot guarantee
that they will use the nDelius identity when authenticating with a particular
service.

HMPPS-Auth also provides support for the Client Credentials grant type, which
allows creation of a client configuration, assignment of HMPPS-Auth-specific
authorities, applicable scopes and a custom username to be set in the access
token. Using this method we can authenticate a specific client, apply
coarse-grained access control to the Delius API endpoints based on client
roles and also supply the client username for use in Delius database
interactions as needed (e.g. for audit fields). For this to work we will need
to create a matching user in the Delius database for each client.

There is also provision in HMPPS-Auth to set a username explicitly when
requesting a token. Although we do not plan to use this feature it may be an
alternative method of supplying the username in the future.

## Decision

We will use OAuth2 Client Credentials grant type within
[HMPPS-Auth](https://github.com/ministryofjustice/hmpps-auth)
to authenticate clients of the Delius API. We will create a client
configuration for each client and this configuration will contain HMPPS-Auth
roles that describe the permitted interactions with the Delius API. The client
configuration will also contain a Database Username entry which will match a
corresponding user in the Delius database. We will check the validity of the
supplied access tokens on each request using the [Token Verification API](https://github.com/ministryofjustice/token-verification-api)

## Consequences

Creating an OAuth2 client for each Delius API client means that we can ensure
that services are accessing the API in a consistent manner. API endpoint
access can be controlled by HMPPS-Auth roles applicable to the use-case of the
service. Data access restrictions and fine-grained access control can be
applied internally, as needed, based on the client-specific Delius username
set in the 'Database Username' client configuration and supplied in the access
token. Neither of these operations are dependent on the end user identity.

Where we are using a proxy or intermediate service such as [Community API](https://github.com/ministryofjustice/community-api)
to coordinate and orchestrate calls to the Delius API we will need to pass the
access token across the intermediate so that we retain the client information
of the originating service.

Implementing token verification gives us the ability to control the validity
of access tokens in the environment.

## Authentication Overview

![Authentication Overview](../../img/authentication.png?raw=true)
