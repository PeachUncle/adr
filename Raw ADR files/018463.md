# ADR00: Telemetry Composite Action

## Context and Problem Statement

In modern CI/CD pipelines, capturing telemetry data is crucial for monitoring, debugging, and improving the software development lifecycle. To streamline this process, we need a structured approach to export telemetry data using the Open Telemetry Trace Exporter Action in GitHub Actions.

## Decision

We will implement a reusable workflow to export GitHub Workflow telemetry data using OTLP (Open Telemetry Protocol) to a configurable endpoint. This workflow will be designed to:
- Export telemetry data at the end of a workflow run.
- Support both `workflow_run` event triggers and current workflow completion.
- Integrate with OpenTelemetry tools and services like Jaegar, Grafina, Honeycomb.

## Considered Options

1. **Manual Implementation in Each Workflow**: Manually add telemetry export steps to each workflow.
2. **Reusable Workflow with Open Telemetry Trace Exporter Action**: Create a reusable workflow that can be called by multiple workflows to export telemetry data.

## Decision Outcome

We chose Option 2, the reusable workflow, due to the following reasons:
- **Maintainability**: Centralizes telemetry export logic in one place, making updates and maintenance easier.
- **Reusability**: Allows multiple workflows to reuse the same telemetry export logic, reducing redundancy.
- **Scalability**: Simplifies the integration of telemetry export across various projects and repositories.

## Detailed Workflow Description

### Action Inputs

| Name            | Description                                                                                 | Required | Default               |
|-----------------|---------------------------------------------------------------------------------------------|----------|-----------------------|
| otlp-endpoint    | The destination endpoint to export OpenTelemetry traces to                                  | true     |                       |
| otlp-headers     | Network Headers for the destination endpoint to export OpenTelemetry traces to.             | true     |                       |
| run-id           | Workflow Run ID to Export                                                                   | false    | env.GITHUB_RUN_ID     |

### Action Outputs

| Name    | Description                                  |
|---------|----------------------------------------------|
| traceId | The OpenTelemetry Trace ID for this Trace    |

### Reusable Workflow: `otel-export-trace.yml`

This workflow will be stored in the `.github/workflows` directory and will be designed to export telemetry data using the Open Telemetry Trace Exporter Action.

```yaml
name: OpenTelemetry Export Trace

on:
  workflow_run:
    workflows: ["PR check"]
    types: [completed]

jobs:
  otel-export-trace:
    name: OpenTelemetry Export Trace
    runs-on: ubuntu-latest
    steps:
      - name: Export Workflow Trace
        uses: inception-health/otel-export-trace-action@latest
        with:
          otlp-endpoint: grpc://api.honeycomb.io:443/
          otlp-headers: ${{ secrets.OTLP_HEADERS }}
          githubToken: ${{ secrets.GITHUB_TOKEN }}
          runId: ${{ github.event.workflow_run.id }}
