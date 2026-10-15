# ADR-0003: Provisioning Strategy

## Status

Accepted

Date of decision: 2024-08-23

## Context and Problem Statement

Various production and non-production environments, containing a wide (and changing) range of infrastructure and
services, will be needed as the Private Rented Sector Database (PRSDB) is developed and maintained.

How should we create these environments?

## Considered Options

* Terraform Community Edition 
* AWS CloudFormation 
* Manual Provisioning

## Decision Outcome

Terraform Community Edition, because it allows automated, repeatable provisioning, and is the tool of choice across 
MHCLG (and the wider industry).

## Pros and Cons of the Options

### Terraform Community Edition

Terraform is a platform-agnostic infrastructure-as-code (IaC) tool used to “provision and manage resources in any cloud
or data centre.” It was described as “a de facto choice” on the Thoughtworks Technology Radar (in April 2019, its latest
appearance).
* Good, because it is very commonly used within MHCLG. 
* Good, because it is commonly used in the wider community. 
* Good, because it integrates well with AWS (which PRSDB will use), but also other platforms (which would be helpful if
  any non-AWS resources are ever needed in future). 
* Good, because it has no cost to run (although state must be stored somewhere, and S3 is frequently used for this 
  purpose, which will incur a small cost). 
* Bad, because support is only available through the community (for the Community Edition; the paid Enterprise edition
  includes support from Hashicorp, the owning company).

### AWS CloudFormation

AWS CloudFormation is the AWS native IaC service.
* Bad, because it not commonly used with MHCLG. 
* Good, because it integrates well with AWS. 
* Bad, because it incurs a cost (albeit a small one) to run. 
* Good, because AWS offer support. 
* Bad, because it is relatively verbose and thus slow to write.

### Manual Provisioning

If no IaC tool is used, infrastructure must be provisioned manually.
* Bad, because it is time-consuming (and thus limits the possibility of provisioning ephemeral environments).
* Bad, because it is not easily repeatable: even with comprehensive documentation, unintentional differences can be
* introduced to environments.

## More Information

* Review of the MHCLG technical landscape: [DLUHC Tech Landscape Review.docx](https://mhclg.sharepoint.com/:w:/s/PrivateRentedSector/EZp45cVALmBDl-MmTf5gd9cBajXyR87tPoGDom_OZFiMgg?e=GgSSh6)