# ADR Summary: Implementation of Authentication, Technologies, and Database Design

## Context

The project involved the utilization of various technologies for authentication, including Microsoft Authentication Library, Express.js, and initially MySQL for the database. Familiarity with these technologies influenced the choice, although Microsoft Authentication Library posed a learning curve as it was unfamiliar territory.

## Decision

### 1. Authentication Technology

- **Choice:** Microsoft Authentication Library, Express.js, MySQL.
- **Rationale:** Familiarity with these technologies, except for Microsoft Authentication Library, was a primary consideration.
- **Learning Experience:** Despite challenges, the learning from Microsoft Authentication Library was deemed valuable.

### 2. OAuth 2.0 Verification

- **Decision:** Omitted the use of PKCE keys and encryption due to time constraints.
- **Rationale:** Prioritized feature development over securing the app, given the perceived low likelihood of use.

### 3. Feature Development

- **Completed Flows:** Vendor processes, dish addition, user and order management.
- **Challenges:** Complex logic for order status updates, especially during control transfer stages.
- **Unfinished Aspects:** Time constraints led to incomplete elements.

### 4. Database Design

- **Utilized:** TypeORM for the database, MySickle for familiarity.
- **Normalization:** Aimed for strong normalization, potentially overdoing it according to fifth normal form.
- **Enum Variables:** Avoided to maintain simplicity.

### 5. Transition to Postgres

- **Challenge:** Late realization that the project used Postgres, not MySQL.
- **Outcome:** Postgres integration postponed due to time limitations.

### 6. Read Structure

- **Approach:** Combined query and URL parameters for legibility and self-explanatory reads.

### 7. Trade-offs

- **Incomplete Aspects:** Encryption and admin role.
- **Access Separation:** Ensured vendors can only access their own dishes.
- **Authorization:** Implemented for security, preventing unauthorized access.

## Consequences

- **Learning Value:** Despite challenges, the project provided valuable learning experiences.
- **Future Considerations:** Postponed Postgres integration and unfinished aspects may be addressed in future iterations.

This ADR provides a concise summary of key decisions, their rationale, and the consequences, offering insights into the project's development choices and trade-offs.
