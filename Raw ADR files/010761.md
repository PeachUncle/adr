# 0001 Use CKAN to organise data

**Status:** accepted

**Deciders:** Greg Kempe, JD Bothma

**Date:** 2017

**Technical Story:** We need a way to store, document and classify dozens to hundreds of files of structured data \(e.g. CSV, XLSX, APIs\), unstructured data and narrative \(PDF\), and select a specific set of these programmatically and manually/interactively in particular contexts. 

### Context and Problem Statement

Users need to be able to browse and search for datasets, narrowing in on what they are looking for using relevant classifying criteria.

In addition to structured data which is obviously in scope for a data portal, a massive underutilised resource identified in the context of budget analysis and oversight is the documents that provide narrative and are published as part of official prescribed reporting.

These datasets and documents should be easy to discover and understood. This requires classification along criteria relevant to a given dataset, e.g. branch of government, publication date, their scope, as well as definitions and explanations of their content and what use they are suited for.

### Decision Drivers

* Compatibility with existing data discovery and analysis tooling would help uptake
* Vendor lock-in would be a concern, since the point is to open access to these resources. Getting locked in to a maintenance contract could risk sustainability.

### Considered Options

* CKAN
* Socrata
* Custom build, e.g. Django site

### Decision Outcome

**Chosen option:** CKAN, because it offers many proven patterns and tools for organising, documenting and providing access to the range of data and documents the project needs to release. Being open source it is also the most sustainable option to invest in.

### Pros and Cons of the options

#### CKAN

* Good because it is open source - it is always possible to find a developer who can support it. Vendor lock-in is not a concern.
* Good because it has a track record of supporting many government and community-run data portals
* Good because it has a range of built-in and developer-customisable ways of categorising and organising data
* Good because it has powerful dataset search facilities
* Good because its appearance can be customised
* Good because there is a range of authentication, categorisation, dataset documentation, preview and presentation plugins available

#### Socrata

* Good because it has a track record of supporting many government and community-run data portals
* Good because it has a range of built-in ways of categorising and organising data
* Good because it has an attractive clean user interface
* Bad because of reliance on one vendor, needing to export and migrate data and metadata to move to an alternative if needed
* Bad because customisability is limited
* Bad because errors in API requests \(at least the data API, not sure right now about data discovery API\) are not descriptive - just an HTTP 400 Bad Request status with no explanation.

#### Custom build

* Good because we have complete flexibility as to field names, how we want to structure the classification system
* Good because it's very quick to get started - we just build what we need now
* Bad because we have to come up with our own classification system, reinventing a wheel that existing data portal tooling has solved
* Bad because the number of developers already familiar with the codebase is less than an established open source project
* Bad because every new feature is new development, rather than just activating an existing core or plugin feature

