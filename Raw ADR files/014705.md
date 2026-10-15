# ADR-0026: Address Lookups (Revisited)

## Status

Accepted

Date of decision: 2025-03-20

## Context and Problem Statement

{Describe the context and problem statement, e.g. in free-form text using two or three sentences. You may want to
articulate the problem in the form of a question.}

ADR-0010 decided upon OS Places API as our address lookup solution: users search for an address, and we cache the
result in our local database, for later searches. A key part of the information saved is the local authority. LA
boundaries can change surprisingly often, however, leaving our cached data stale; the same is true for other types
of address changes.

How should we deal with the problem of cached address data going stale?

## Considered Options

* Refresh via OS Places API
* OS AddressBase product
* OS NGD Address
* OS NGD Address + OS Places API

## Decision Outcome

OS NGD Address, because this will minimise stale data and ongoing complexity, as well as the risk of needing replacement
in the future.

## Pros and Cons of the Options

### Refresh via OS Places API

Continue to use OS Places API as we currently do, and when we learn of boundary changes to an LA, work through all
saved addresses in the affected LA(s) to fetch their data again from OS Places API.

* Good, because no changes to existing address lookup journeys are needed.
* Neutral, because extra complexity is needed to work through addresses that need refreshing.
* Bad, because updates are manually triggered, which may cause delays.
* Bad, because updates will take a long time to complete (as they would need to be throttled, to avoid PRSDB's overall
  use hitting the OS Places rate limit).
* Good, because we can control when the updates happen - e.g. so in the case of new / merged LAs, we can coordinate
  updates to addresses at the same time as updates to the LA that existing LA users belong to.


### OS AddressBase product

Regularly ingest an AddressBase product (e.g. AddressBase Plus, a simple CSV-based product, as used by EPB) and search
on that (instead of via OS Places API).

* Bad, because AddressBase products are due to be phased out, according to our OS contact.
* Bad, because existing address lookup journeys will need to be reworked.
* Neutral, because extra complexity is needed to regularly download and ingest the AddressBase data.
* Neutral, because data updates are automatic although not especially rapid (e.g. a 6 week cadence for AddressBase
  Premium).
* Neutral, because we may need to handle addresses moving to a new LA before we have migrated our LA users.


### OS NGD Address

Regularly ingest OS NGD (National Geographic Database - the newest data product for addresses (and much more) that OS encourage
services to use) and search on that (instead of via OS Places API).

* Bad, because existing address lookup journeys will need to be reworked.
* Neutral, because extra complexity is needed to regularly download and ingest the NGD data.
* Good, because data updates are automatic and frequent (we believe daily).
* Neutral, because we may need to handle addresses moving to a new LA before we have migrated our LA users.


### OS NGD Address + OS Places API

Regularly ingest OS NGD (National Geographic Database - the newest data product for addresses (and much more) that OS encourage
services to use) but continue to use OS Places API for address lookups.

* Bad, because although existing address lookup journeys will stay the same, we'll still need to update the LA search
  logic - meaning maintaining two ways of doing very similar things
* Neutral, because extra complexity is needed to regularly download and ingest the NGD data.
* Good, because data updates are automatic and frequent (we believe daily).
* Neutral, because we may need to handle addresses moving to a new LA before we have migrated our LA users.