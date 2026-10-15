---
scope: Jobberknoll
date: 2024-12-30
deciders: "@tchojnacki"
informed: "@mlodybercik, @jakubzehner, @piterek130"
---

# Domain model and database schema changes for Jobberknoll

## Context and Problem Statement

The current soft-delete behavior of Jobberknoll is mainly left-over from the monolithic database schema. Back then, this functionality was necessary, to retain referential integrity. However, since the database table is separated and other databases refer to its entities using unconstrained UUIDs, there is a need for another justification for the soft-delete behavior. Common arguments in favor of soft-delete are as follows: easier upkeeping of referential integrity (does not apply), the ability to restore deleted entities (because of GDPR, records would be redacted, so restoration is not possible regardless), the ability to track changes i.e. audit logs (this can be achieved by other means, e.g. event sourcing). On the other hand, the soft-delete behavior makes the implementation more complex, reduces performance (in both the time and space domain) and increases the risk of bugs in an already security-sensitive service.

The current database design has some notable mistakes:

- There is a bitmap index defined for `account_type` column, which is not used in any query and more importantly, it is not supported by the current database engine (PostgreSQL).
- The `account_type` column is stored as `CHAR(1)` instead of an `ENUM` type supported by PostgreSQL, which would remove the need for its serialization and deserialization on each query executed by the infrastructure layer. There is also no need for this column to be named distincly from the `type` field in the domain model, since it is not a reserved keyword in PostgreSQL. `CHECK`s regarding the `account_type` would also not be necessary if the column were to be changed to an `ENUM`.
- The `is_active` column is possibly redundant, as it is used only in the soft-delete logic.
- The `last_modified` column is stored as a `TIMESTAMP` even though it would only ever get compared to [RFC 7519](https://www.rfc-editor.org/rfc/rfc7519.txt) `NumericDate` which has a resolution of seconds, and is counted from the Unix epoch, making it easily storable in an `INT` column.

This would in total bring the byte size of the table row from 16 + 1 + 256 + 256 + 61 + 1 + 8 + 17 = 616 to 16 + 4 + 256 + 256 + 61 + 4 + 17 = 614.

If schema were to be updated the following changes to the domain model would be convenient:

- Removal of the `isActive` field.
- Separating the storage of `phoneNumber` for account types lacking phone number support vs. passengers which have not supplied this field.

## Considered Options

- Retaining old model, schemas and delete behavior
- Removing soft-delete logic and fixing schema mistakes

## Decision Outcome

Chosen option: **Removing soft-delete logic and fixing schema mistakes**, because it heavily simplifies the service implementation while retaining almost indistinguishable functionality for the consumers.

All of the changes proposed in the context and problem statement will be implemented.

### Consequences

- Good, because implementation of a security-sensitive service is simplified.
- Good, because the performance of the service is (negligibly) improved.
- Good, because the storage size of the table is (negligibly) reduced.
- Bad, because only dates up to year 2106 will be supported.
