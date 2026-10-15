# 9. Collection of Codespaces usage metrics

Date: 2024-06-13

## Status

Accepted

## Context

In order to know if the initiative to make Codespaces available for researcher use is a success we want to know:
* if codespaces are being used
* who is using them
* how they are being used

The GitHub API provides endpoints related to codespaces.
One of these, the [codespaces organizations endpoint](https://docs.github.com/en/rest/codespaces/organizations?apiVersion=2022-11-28) provides a list what codespaces are extant in a given organisation, when they were created, their current state, and when they were last used.

Opensafely CLI already contains the same telemetry code (via the vendored Jobrunner) that's used in the secure environment. This telemetry has the ability to trace what commands are run, what the inputs to the commands are, and how long the various stages of execution take.

There are legal and ethical considerations regarding collection of data about users. The UK GDPR [includes](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/personal-information-what-is-it/what-is-personal-data/what-are-identifiers-and-related-factors/#pd2) "online identifiers" within the definition of personal data.

There is an existing Bennett Institute [Metrics](https://github.com/ebmdatalab/metrics) project which is routinely used to measure various other aspects of our usage of GitHub, and display the collected data via Grafana.
It currently utilises the GitHub and Slack API.
It currently polls the GitHub API at 9am every day.

## Decision

We will use extend the metrics codebase as this already contains large parts of the functionality required for codespace usage metrics, which are also a good conceptual fit with the existing metrics.

We will query the GitHub API endpoint for the `opensafely` organisation's codespaces, as all OpenSAFELY research study repositories are stored within this organisation.

We will store the data in the metrics database, and present the collected data via Grafana.

The collected codespaces metrics will only be accessible to authenticated members of the Bennett Institute.

We will publicly state what information we collect about codespaces usage.

## Consequences

We will miss codespaces that are created from repositories based on the OpenSAFELY research template but are not in the `opensafely` organisation.

We will miss codespaces that are created after 9am and are deleted before 9am the next day.

We will not know what opensafely-cli commands are being used by users, but this sort of telemetry is arguably orthogonal from usage of Codespaces.

We believe this data processing is legitimate and our users would not be surprised to find out about its existence.
