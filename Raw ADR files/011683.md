# 5. Use Digital Studio Standard Technologies Where Possible

Date: 2021-02-10

## Status

Accepted

## Context

The Delius API is a collaborative effort and the development team is composed
of people from both Unilink and the Digital Studio. Ultimately it is expected
that the API application will be owned by the NDST team and the collaboration
between to two development teams will continue. To simplify the network
topology between the API application and the Delius database the API will be
deployed into the existing Delius AWS environment. It follows from this
decision that we will use the AWS container services (ECR and ECS) to deploy
and run the API service. The selection of patterns to build, test, deploy and
maintain the API application has fewer constraints and the team is free to
choose the technologies and processes that best serve the project. 

## Decision

### Application Build Pipeline

We will use **CircleCI** to build, test and deploy to development 

### Primary Development Language

We will use **Kotlin** as our primary development language and **Gradle** as the
task runner for development and testing 

### Application Packaging and Dependencies 

We will use **Docker** as our application packaging format and **Docker Compose**
as our method of running third-party service dependencies in development
environments 

### Application Monitoring 

We will use **Azure Application Insights** for application performance
management 

## Consequences

The team has decided to make use of the Digital Studio application development
patterns where possible. This decision means the Studio bootstrap tools can be
used to create a skeleton service quickly with standard technologies and
service integrations pre-configured. It also allows reuse of existing MoJ project
work on pipeline configuration, development setup and application monitoring.
This baseline should mean the project is easily understandable across the MoJ
and that developers from the Digital Studio can effectively contribute to
ongoing development.

The use of Kotlin as the primary development language is a more difficult
decision to make. The team expects to use the nDelius Java codebase as a
reference implementation for the application logic. The use of Kotlin in the
API service means that this logic will need to be understood, re-implemented
and then kept in line with the development of the nDelius codebase. The team
feels that it is not possible to reuse the existing code due to the tight
coupling between the application logic and the data model. The nDelius code is
also not factored in a way that allows reuse, as the methods are often very
large with multiple branches of logic. As a consequence the Delius API
developers will need to address how to ensure that the both the API and the
existing nDelius application result in the same outputs from the same
operations. Ideally this would be part of an automated test suite and this is
under investigation as part of the development work. 



