# Use JMeter for Load and Performance Testing

**Date:** 2025-08-13

## Status

Accepted

## Context

In this project, we need to verify that the frontend and backend API can handle expected traffic levels and meet specific Service Level Objectives (SLOs) for response times.  
The test setup should be able to:

- Simulate realistic user behavior (e.g., loading the homepage, clicking through data intervals like 3h, 1d, 1w, 1m).
- Measure performance metrics such as Time-To-Last-Byte (TTLB) and API response times.
- Generate detailed reports (HTML dashboards, raw data files) for analysis.
- Integrate seamlessly into both local developer workflows and automated CI/CD pipelines.

Apache JMeter was evaluated and selected because it meets all these requirements and fits well with our Docker-based infrastructure.

## Alternatives Considered

- **k6**  
  Modern and scriptable in JavaScript, but lacks built-in GUI for test plan creation and has less native CSV/HTML reporting without additional tooling.
  
- **Custom Python scripts**  
  Flexible and Pythonic, but would require building reporting and CI integration manually, as well as re-creating complex browser/resource loading logic.

## Decision

We will use **Apache JMeter** for load and performance testing because:

- It has a mature ecosystem with strong community support.
- It supports both GUI-based and headless (CLI) execution, allowing easy local design and automated CI/CD runs.
- It produces detailed HTML reports and raw JTL data for further processing.
- It integrates well with Docker for reproducible and isolated test environments.
- It supports parameterization via environment variables, making it CI-friendly.

## Consequences

- JMeter test plans (`.jmx` files) can be complex XML and may require knowledge of its structure for advanced modifications.
- Test execution will require Docker or a JMeter installation in the environment.
- Existing team members can leverage JMeter’s GUI to modify test scenarios without writing code.
- Easy integration with GitHub Actions enables automatic SLO validation on pull requests.
