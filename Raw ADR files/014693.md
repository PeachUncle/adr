# ADR-0010: Address Lookups

## Status

Superseded by 0026-address-lookups-revisited

Date of decision: 2024-08-23

## Context and Problem Statement

Users of the Private Rented Sector Database will need to enter addresses: landlord contact addresses and property
addresses, in particular. All property addresses and most landlord contact addresses are expected to be UK based. To
help with data accuracy and to streamline the data input processes, we should allow users to search for UK addresses
(e.g. look them up by postcode).

Which service should we use to perform those lookups?

Further detail can be found
in [Address Lookup Review.docx](https://mhclg.sharepoint.com/:w:/s/PrivateRentedSector/ERf5wdYZQUBPvHVCyt6ZJ40BZBwTRo6BflR6fBtdNPAH6A?e=gZKqmQ).

## Considered Options

* OS Places API
* OS AddressBase Premium
* OS AddressBase Core
* OS Places API + One-Off OS AddressBase Premium
* OS National Geographic Database

## Decision Outcome

OS Places API, because it offers a large, frequently updated dataset through a convenient technical integration.

**- OR -**

OS Places API + One-Off OS AddressBase Premium, if the API rate limit is expected to be problematic at launch, because
the Places API still offers the simplest technical solution in the long term, and the AddressBase Premium data set is
the same one used by the Places API (ensuring compatibility between data).

## Pros and Cons of the Options

### OS Places API

The OS Places API provides a RESTful HTTP API that allows UK address lookups (by several methods, including post code
and free text). There is a rate limit of 600 transactions per minute, although it may be possible to increase this (at a
cost, and by agreement with OS).

* Good, because technical integration is simple, with minimal maintenance overheads.
* Good, because the data is regularly refreshed (essentially on an “ASAP” basis).
* Good, because the dataset is large (meaning increased likelihood that an address will be found when a user searches
  for it).
* Bad, because the rate limit of 600 TPM could potentially be exceeded e.g. shortly after the service launches, when
  many landlords and properties are being registered at once.

### OS AddressBase Premium

The AddressBase Premium product is a downloadable dataset provided by OS. It is the largest dataset provided by OS, and
it is updated every 6 weeks. It is provided in a relational structure.

* Bad, because technical integration is relatively complex, with ongoing maintenance concerns (e.g. monitoring a regular
  job that processes updates).
* Bad, because the periods between data refreshes are relatively long.
* Good, because the dataset is large.
* Good, because there is no imposed rate limit (only the limits of our service’s infrastructure).

### OS AddressBase Core

The AddressBase Core product is a downloadable dataset provided by OS. It is a slightly smaller dataset than AddressBase
Premium. It is updated every week. It is provided in a simple (single table) structure.

* Bad, because the technical integration is relatively complex (though less so than with AddressBase Premium), with
  ongoing maintenance concerns.
* Neutral, because the periods between data refreshes are neither especially long nor short.
* Neutral, because the dataset is likely large enough for our needs, but not the largest available.
* Good, because there is no imposed rate limit.

### OS Places API + One-Off OS AddressBase Premium

The Places API and the AddressBase Premium products use the same data, with the same structure, so they can be combined:
a single (manual) download of the AddressBase Premium data could be used to allow local address lookups for an initial
period (where lookups are expected to be very frequent), then the Places API could be used afterwards (when lookups are
expected to be less frequent).

* Bad, because the technical integration is complex: there is no need for a regular update mechanism, but essentially
  two different systems need to be built.
* Good, because other than the initial period, the data will be frequently refreshed (as per the OS Places API option).
* Good, because the data is large.
* Good, because concerns about rate limits would be mitigated.

### OS National Geographic Database

The OS NGD is a broad product but includes address information – although addresses are only available as a download
(unlike other parts of NGD, which offer API access). It offers a large dataset (although it’s not clear how it compares
to AddressBase Premium), which is refreshed daily. The data model is simple.

* Bad, because the technical integration is relatively complex.
* Good, because the data is refreshed regularly.
* Neutral, because the dataset is likely large enough for our needs but may not be the largest available.
* Good, because there is no imposed rate limit.

## More Information

* [Address Lookup Review.docx](https://mhclg.sharepoint.com/:w:/s/PrivateRentedSector/ERf5wdYZQUBPvHVCyt6ZJ40BZBwTRo6BflR6fBtdNPAH6A?e=gZKqmQ)