---
# Configuration for the Jekyll template "Just the Docs"
parent: Decisions
nav_order: 1
title: ADR 0001 - Choosing the Database Technology
status: proposed
date: 2024-05-10
deciders: Project Team
consulted: Professor, Dev (TA)
informed: Entire Team
---

# Choosing Between SQL Lite, MongoDB, and NoSQL for Local Data Storage

## Context and Problem Statement

In our recent project lead meeting, concerns were raised about using PostgreSQL due to its complexity and the professor's preference for simplicity. The professor advised starting with local data storage solutions that are simpler and more aligned with the goals of the project. We are considering SQL Lite, MongoDB, and NoSQL options to find a balance between simplicity and functionality.

## Decision Drivers

- **Simplicity**: The solution must be easy to implement and maintain.
- **Local Storage Capability**: Ability to run and store data locally without complex setup.
- **Performance**: The database should handle our project's data needs efficiently.

## Considered Options

- **SQL Lite**
  - Lightweight and easy to integrate.
  - Uses familiar SQL syntax, which is educational and widely applicable.
- **MongoDB**
  - Flexible schema and document-oriented, which could be advantageous for our varied data types.
  - Known for scalability and powerful querying capabilities.
- **NoSQL (generic)**
  - Offers flexibility in data storage models.
  - Typically easy to scale and manage.

## Decision Outcome

Chosen option: "SQL Lite", because it meets the simplicity criterion and provides sufficient functionality for our local storage needs without adding unnecessary complexity. It also uses SQL, which is educational and familiar to most team members.

### Consequences

- Good, because it allows for easy setup and integration with our existing technologies.
- Good, because it supports our learning objectives by using widely understood SQL.
- Bad, because it may not offer as much flexibility in handling unstructured data as MongoDB or generic NoSQL solutions.

## Pros and Cons of the Options

### SQL Lite

- Good, because it requires minimal setup and is lightweight.
- Bad, because it may not scale as well as MongoDB if project requirements grow.

### MongoDB

- Good, because of its flexibility with document-oriented data structures.
- Bad, because it might introduce complexity that goes against the professor's advice.

### NoSQL (generic)

- Good, because it offers scalability and flexibility.
- Bad, because the learning curve might detract from other project goals.

## More Information

This decision will be revisited if project requirements change significantly or if we find SQL Lite to be inadequate for our needs during development.
