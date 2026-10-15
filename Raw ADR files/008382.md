---
status: "accepted"
date: 2025-06-07
decision-makers: [Whole team]
consulted: [course materials, Lighthouse documentation]
informed: [Whole team]
---

# Integrating Lighthouse Audits into Deployment Pipeline
## Context and Problem Statement

As we developed our web application, we needed a way to objectively measure and improve its performance and accessibility. Manual checks are too inconsistent and time-consuming. We wanted a solution that could automate quality checks and guide us toward meeting performance and accessibility standards.

## Decision Drivers

* Need for objective, repeatable performance and accessibility metrics
* Ensuring code quality after each deployment
* Automating feedback to reduce manual effort and human error
* Supporting accessibility goals for all users
* Ensuring performance across devices with varying capabilities

## Considered Options

* **Use Lighthouse audits integrated into CI/CD pipeline**
* Run Lighthouse manually from Chrome DevTools
* Use other tools like WebPageTest or PageSpeed Insights

## Decision Outcome

Chosen option: **Use Lighthouse audits integrated into CI/CD pipeline**, because it provides automated, repeatable, and actionable metrics that align with our quality goals and runs only when a deployment is successful, minimizing unnecessary resource usage.

### Consequences

* Good, because reports highlight opportunities to improve load time, accessibility, and adherence to best practices
* Good, because automation reduces manual testing burden and catches regressions early
* Good, because reports are easy to interpret and document
* Neutral, because initial setup required some extra GitHub Actions configuration
* Bad, because Lighthouse scores can vary slightly due to network conditions if not run in a controlled environment

### Confirmation

Lighthouse audits are run automatically as part of our GitHub Actions pipeline after a successful deployment. Reports are saved as artifacts or posted in PR comments for team visibility. A performance threshold (e.g., 90+ in key categories) is used to validate compliance. Code reviews check whether recommendations were addressed in each sprint.

## Pros and Cons of the Options

### Lighthouse in CI/CD

* Good, because it provides consistent, automated quality feedback
* Good, because it integrates seamlessly with GitHub Actions
* Good, because reports can be version-controlled or archived
* Bad, because score variability can sometimes cause confusion
* Neutral, because configuration takes initial effort

### Manual Lighthouse Checks

* Good, because it gives the same data
* Bad, because it's easy to forget or skip under time pressure
* Bad, because results aren't consistently recorded or shared

### PageSpeed Insights / WebPageTest

* Good, because they provide external perspectives
* Bad, because they are not easily automatable within the repo
* Bad, because some tools focus only on performance, not accessibility
* Bad, because they spread tool use and diverge from things we have learned in class
