---
status: "accepted"
date: 2025-06-08
decision-makers: [Whole team (team 13)]
consulted: [W3Schools, ESlint/Prettier docs, course materials]
informed: [All team]
---

# Standardizing Code Formatting with ESLint, Prettier, and W3Schools Style Guide

## Context and Problem Statement

Our codebase includes multiple HTML, CSS, and JavaScript files, written and edited by different team members. Without standardized formatting, the code becomes harder to read, debug, and maintain — especially for new contributors or learners reviewing the repo. We needed a way to enforce consistent styling, reduce syntax errors, and align with best practices that are accessible to learners.

## Decision Drivers

* Ensure consistency in code style across files and contributors
* Reduce manual formatting and avoid unnecessary Git diffs
* Catch common bugs and maintain high code quality
* Support beginner-friendly conventions that are easy to follow

## Considered Options

* Use ESLint + Prettier with W3Schools Style Guide
* Only use ESLint with custom rules
* Manual formatting and team-based review
* Use Airbnb Style Guide with ESLint

## Decision Outcome

Chosen option: **"Use ESLint + Prettier with W3Schools Style Guide"**, because it provides the most accessible, beginner-friendly, and automated solution for formatting and linting, and aligns with our educational goals.

### Consequences

* Good, because code formatting is consistent and automated
* Good, because new contributors (especially learners) can quickly onboard with familiar syntax via W3Schools
* Good, because ESLint helps us catch JavaScript issues early
* Bad, because the W3Schools style guide is not as rigorous or modern as Airbnb’s — but that’s intentional to stay beginner-friendly

### Confirmation

Linting and formatting are integrated into our Git workflow (e.g., pre-commit hooks or CI checks). We run `eslint .` and `prettier --check .` to ensure compliance. Pull requests are reviewed with style and lint consistency in mind.

## Pros and Cons of the Options

### ESLint + Prettier + W3Schools Style Guide

* Good, because Prettier handles opinionated formatting automatically
* Good, because ESLint helps catch logic and syntax errors
* Good, because W3Schools style guide is geared toward learners
* Neutral, because Prettier overrides some ESLint formatting rules
* Bad, because W3Schools guide lacks the depth of more advanced style guides

### ESLint Only

* Good, because it's customizable and linting is powerful
* Neutral, because formatting needs manual enforcement or custom rules
* Bad, because formatting is not automated
* Bad, because team needs to agree and memorize custom rules

### Manual Formatting

* Neutral, because team can define whatever looks best
* Bad, because it’s slow and subjective
* Bad, because it leads to inconsistent code and merge conflicts

### W3Schools Style Guide with ESLint

* Good, because it's geared towards learners, which we are
* Neutral, because it may not be as strict or in-depth as industry standards

## More Information

* ESLint: https://eslint.org/
* Prettier: https://prettier.io/
* W3Schools HTML Style Guide: https://www.w3schools.com/html/html_styles.asp
* Configs are located in `/configs` in `The_club_triton` repo
