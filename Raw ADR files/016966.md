<!--
#######################################################################

Tractus-X - Special Interest Group (SIG) Architecture

Copyright (c) 2025 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This work is made available under the terms of the
Creative Commons Attribution 4.0 International (CC-BY-4.0) license,
which is available at
https://creativecommons.org/licenses/by/4.0/legalcode.

SPDX-License-Identifier: CC-BY-4.0

#######################################################################
-->

# Decision Record: Issuer Capabilities in Identity Hub

## Problem statement

In the current Tractus-X architecture, the wallet ([tractusx-identityhub](https://github.com/eclipse-tractusx/tractusx-identityhub)) covers holder and verifier capabilities, but issuer capabilities are covered by a separate service ([tractusx-issuerservice](https://github.com/eclipse-tractusx/tractusx-issuerservice)).
This separation works well at the present time, where only the Core Service Provider (CSP) is an issuer of verifiable credentials (VCs).

However, in the mid- to long-term future, an increasing number of use cases will require regular member companies to also become issuers.
The current separation of wallet vs issuer service would require all such member companies to run two separate services.

At the same time, when running many wallet instances, the additional resources required by combining wallet and issuer service will add up and negatively impact scalability.
This scalability, however, is important for [solution 1 - operator offers wallet as a service](https://github.com/catenax-eV/cx-ex-ssi/blob/main/docs/Issuance/issuance.md#solution-1-operator-offers-wallets-as-a-service), see also roadmap and sig-release items X, Y, and Z.

## Evaluation criteria

- regular member companies must be able to become issuers without an excessive increase in resource demands
- the tractusx-identityhub must remain scalable and not become unnecessarily resource-intensive

## Possible solutions

### Solution 1: Integrate issuer capabilities into the tractusx-identityhub.

Issuer capabilities will be added to the tractusx-identityhub, such that it covers features for issuers, holders, and verifiers in a single service.
The distribution will be modularised in such a way that the issuer capabilities can be included if need be and excluded otherwise.

### Solution 2: Keep wallet and issuer separate

Issuer capabilities could be kept separated, but it would increase the complexity for maintaining and doing releases of the different components.

## Decision: Solution 1

Issuer Service will be merged with the Identity Hub repository.  
The [tractusx-issuerservice repo](https://github.com/eclipse-tractusx/tractusx-issuerservice) (based on the upstream framework) will be deprecated. 
### Rationale

- having one repository makes both deployment and maintenance easier  
- this solution is consistent with the upstream [EDC Identity Hub](https://github.com/eclipse-edc/IdentityHub), which also does not separate issuer capabilities into its own service.  
- an increasing number of use cases (e.g. DPP, PCF, CCM) will require regular participants to have issuer capabilities  
- the images can be published separately still and enabled and disabled in the helm charts
  - https://github.com/eclipse-tractusx/digital-product-pass/tree/main/dpp-verification
- It can be still split in the future again if needed
- The images can be published separately still and enabled and disabled in the helm charts.

### Actions

- deprecate the [tractusx-issuerservice](https://github.com/eclipse-tractusx/tractusx-issuerservice)  
- integrate issuer capabilities into the [tractusx-identityhub](https://github.com/eclipse-tractusx/tractusx-identityhub)  
- publish two images: one including and one excluding issuer capabilities  


### Consequences

- The issuer service repo will be deprecated
- Identity Hub users will need to enable and disable the runtimes from the identity hub issuer capabilties.  

## NOTICE  

- SPDX-FileCopyrightText: 2025 Contributors to the Eclipse Foundation  
- Source URL: https://github.com/eclipse-tractusx/sig-architecture  

