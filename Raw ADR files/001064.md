# 2. Project Structure

Date: 2025-01-14

## Status

Accepted

## Context

I want to implement Chassis pattern in a way that is flexible for both chassis-based services and classic springboot
services. Most of the time they will use the same build logic and handle cross cutting concerns in the same way.
Applications (pet projects) may use the same components, but may want to experiment with something that is partially
incompatible with cross cutting concerns defined here. We want to have the possibility to treat each module as optional.
I'm a single developer and I want to minimize effort related to development of reusable components.

## Decision

I will create following modules:

| Name              | Purpose                                                                                                                                                                                                                                                                                                                                      |
|-------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| chassis-starter-* | Releasable cross-cutting concern implementation.                                                                                                                                                                                                                                                                                             |
| chassis-bom       | This project will use a Bill of Materials (BOM) for dependency management and modularize cross-cutting concerns like logging, monitoring, and security in separate modules. The structure will ensure that any new cross-cutting module can be added to a central dependency (all) without each microservice needing to manually include it. |
| chassis-all       | Aggregator module that includes all chassis modules                                                                                                                                                                                                                                                                                          |
| chassis-parent    | Parent POM with BOM and build logic (plugin configuration)                                                                                                                                                                                                                                                                                   |
| chassis-test-app  | Application for regression testing purposes                                                                                                                                                                                                                                                                                                  |

## Consequences

Positive:

* Each new springboot-based microservice will be able to use each of the modules separately.
* Cross cutting concerns are like a plugins.
* Ease of experimenting with cross cutting concern.
* Single place of changes

Negative:

* Bundled releases of modules
* Necessity of refactor legacy code like chassis-tools,chassis-tools-test and openapi-parent.
