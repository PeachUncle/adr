# ADR-0018: infrastructure-repository

## Status

Accepted

Date of decision: 2024-11-19

## Context and Problem Statement

The configuration of the infrastructure for the project wil be managed by Terraform (as per ADR 0003: Provisioning
Strategy). There is a choice over where that Terraform code should 'live'.

## Considered Options

* The PRSDB WebApp repository
* A new PRSDB Infrastructure repository

## Decision Outcome

A new PRSDB Infrastructure repository, because the configuration it helps reduce the risk of the accidental release of
infrastructure changes, and helps to maintain a logical separation from the application code and infrastructure code.

## Pros and Cons of the Options

### The PRSDB WebApp repository

The configuration would be kept in a top-level `terraform` folder in the PRSDB-WebApp repository on github. Deployment
of the infrastructure would be managed by either a separate stage in the app's deployment pipeline, or by a separate
pipeline that is triggered only by changes to the `terraform` folder.

* Good, because there is a single source of truth for the WebApp as a whole.
* Good, because we can enforce that infrastructure changes are deployed before application changes that depend on them.
* Bad, because care would be needed to avoid the risk of infrastructure changes being released accidentally.
* Bad, because running terraform steps of the pipeline each time (if we opted to do so) would slow the pipeline down
  when infrastructure changes are likely to be much more rare than application changes.
* Bad, because if we have other independent functionality in a different repository later (e.g. as we will likely have
  as part of bulk upload
  processing) then it would not be intuitive for the shared infrastructure to be in the WebApp repository.

### A new PRSDB Infrastructure repository

The configuration would be kept in a new repository called `PRSDB-Infra`, containing only the terraform code for the
application. It would have its own set of pipelines for deploying any infrastructure changes.

* Good, because we would have more fine-grained control by default of when infrastructure changes are released.
* Good, because (for this application) the infrastructure is logically independent of the application for the most part.
* Good, because it will be more intuitive to look in a dedicated infrastructure repository if/ when we have other
  elements of code outside the WebApp repository
* Bad, because we will need a manual process to ensure for that infrastructure changes are released before/ alongside
  application changes that depend on them
* Neutral, because both repositories will need to be looked at to get a full understanding of the application, but this
  is easily surmountable e.g. by cross-referencing in ReadMe files.
