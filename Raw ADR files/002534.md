# Decision 003: Use CareerOneStop API for Skills-Based Occupation Matching

**Date:** 2025-11-04  
**Status:** Accepted  
**Deciders:** Sadie Flick

## Context
Our goal is to programmatically provide occupation options to students based on their RAISEC interests and a JSON-formatted list of skills derived from an LLM. We need a way to take this list of skills and their aptitude levels and efficiently query for a ranked list of matching occupations.

We initially investigated the O\*NET API and downloadable database. However, we discovered that the O\*NET API is a **data retrieval** service, not a matching engine. It allows you to get detailed information (including required skills) for a *single, known occupation code* but does not provide a way to submit a list of skills to get a ranked list of matching jobs.

## Options Considered

### 1. O\*NET Local Database / Web Services API
* **Pros:**
    * Local DB provides complete data access with zero latency or rate limiting.
    * Gives us full control over the raw data for fine-tuning.
* **Cons:**
    * **No built-in matching engine.** We would be required to design, build, test, and maintain our own complex matching and ranking algorithm.
    * This custom algorithm would need to score a user's skills against all 1,000+ occupations in the database, which is computationally expensive and slow.
    * This represents a significant development and maintenance burden, adding high complexity to the MVP.

### 2. CareerOneStop Skills Matcher API
* **Pros:**
    * **Purpose-built for this exact use case.** It provides a specific endpoint (`GetSKARankList`) that accepts a list of skill ratings as input.
    * **Returns a pre-ranked list of occupations** with match scores, O\*NET codes, titles, wages, and outlook.
    * Offloads all complex matching and ranking computation to the API server.
    * Maintained by the U.S. Department of Labor, ensuring the matching logic is validated and data is current.
* **Cons:**
    * Creates an external dependency on a third-party API (requires an API key, subject to downtime or rate limits).
    * **Requires a mapping step:** Our LLM-derived skills must be mapped to the 40 standard "Skills and Knowledge" identifiers that this specific API uses.

## Decision
We chose **Option 2: CareerOneStop Skills Matcher API**.

This API directly solves our core problem with a single, dedicated endpoint. The development effort required to map our user's skills to the 40 standard API skills is significantly lower and less complex than building, validating, and maintaining an entire occupation-ranking algorithm from scratch.

## Consequences
* **Positive:**
    * Massively reduces development time and project complexity.
    * Allows us to leverage a professionally maintained and validated matching algorithm immediately.
    * Simplifies our application logic to: 1) Map skills, 2) Call API, 3) Display results.
* **Negative:**
    * We now have an external dependency for a core feature.
    * We have less control over the matching algorithm itself (it's a "black box").
* **Neutral:**
    * This decision shifts the primary development challenge from *algorithm design* to *data mapping*.

## Implementation Notes
* **When:** To be implemented as the primary mechanism for the skills-to-occupation matching feature.
* **Where:** A new service/module will be created to act as a client for the CareerOneStop API.
* **How:**
    1.  Register for a CareerOneStop API key.
    2.  Call the `GetSkills` endpoint once and store the resulting 40 standard skill identifiers and their descriptions locally.
    3.  Develop the "crosswalk" logic (likely using the LLM) to map the user's skills to these 40 standard skills and generate a 0-5 rating for each.
    4.  Format these 40 ratings into the pipe-delimited string required by the API.
    5.  Call the `GetSKARankList` endpoint with this string and the desired number of results (e.g., 15).
    6.  The results from this API call will then be presented to the user.