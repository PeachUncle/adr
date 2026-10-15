---
date: { 2024-10-13 }
written-by: { Ahmed Sulaimon }
decision-makers: { Ahmed Sulaimon, Ayman Sammo, Nayan Stanley }
---

# Distributed database vs single database

## Context and Problem Statement

- How should the web application store data

## Considered Options

- [Distributed databases](#Distributed-databases)
- [Single database](#Single-database)

## Decision Outcome

**Chosen option:** Distributed databases
**Rationale:**

- AML has a national network of branches across England, serving a large and growing user base
  (projected to be at least 20% of the 55.98 million population, with 10% annual growth).
  The system needs to be highly scalable to handle increasing demand, both in terms of users and the media catalog, without performance degradation.
  A single database would likely struggle to keep up with this scale efficiently, especially when handling millions of simultaneous requests.
  Using a multi-database architecture allows you to horizontally scale the system by distributing the load across multiple databases. [See below for pros and cons](#pros-cons).

### Consequences

- **Positive:** Scalability: Multi-database systems can scale better horizontally.
- **Positive:** Fault Tolerance: With multiple databases, if one database fails, the system may continue to operate with the remaining databases.
- **Positive:** Performance: You can optimize databases for specific functions.
- **Positive:** Specialization: You can use different database systems suited for different needs (e.g., relational for structured data, NoSQL for unstructured data,
  graph databases for relationships).
- **Negative:** Complexity: Managing multiple databases increases system complexity
- **Negative:** Higher Costs: Running multiple databases requires more infrastructure, leading to higher operational costs in terms of hosting, monitoring, and maintenance.
- **Negative:** Data Consistency Challenges: Ensuring that data remains consistent across different databases (e.g., when a user borrows a book) can be difficult and may require implementing complex logic for distributed transactions.

### Confirmation

<!-- Is this valid option for the project & why -->

<a name="pros-cons"></a>

## Pros and Cons of the Options

<a name="Distributed Databases"></a>

### Distributed Databases

- **Pros:**

  - Scalability.
  - Fault Tolerance.
  - Performance.
  - Specialization.

- **Cons:**
  - Complexity.
  - Higher Costs
  - Data Consistency Challenges

<a name="Single database"></a>

### Single database

- **Pros:**
- Simplified Management: Managing a single database is easier
- Cost-Effective: Using a single database reduces infrastructure and operational costs.
- Consistency: All data is in one place, ensuring that data updates are consistent.
- Easier Development: It’s simpler to develop applications with a single database because there’s no need for synchronization or complex data distribution mechanisms.

- **Cons:**
  - Scalability Issues: As the library grows, a single database might become a bottleneck.
  - Single Point of Failure: If the database goes down, the entire system goes down.
  - Limited Flexibility: A single database may limit your ability to use specialized database systems optimized for certain types of data

## More Information

<!-- How did the team come up with the decision -->
