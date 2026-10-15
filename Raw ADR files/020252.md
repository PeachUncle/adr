# TSDR-1018 pgx Packages

## Status

Accepted, Proposed, Deprecated or Superseded (list DR)

## Context



## Decision



## Why / Notes

- Decimals
  - https://github.com/jackc/pgx/wiki/Numeric-and-decimal-support - 2022 check if still true.
  - github.com/jackc/pgx-shopspring-decimal
  - SEE TSDR-1019 Decimals & Currency.md
- Misc
  - github.com/jackc/pgx/v5/pgtype
    - Offers Go types for over 70 PostgreSQL types, including uuid, json, bytea,
      and numeric. These types support both database/sql interfaces and pgx's
      higher-performance native interface.

## TODO later (maybe)

- github.com/twpayne/pgx-geos (PostGIS and GEOS via go-geos)
  - Maps
- github.com/jackc/pglogrepl
  - Provides functionality to act as a client for PostgreSQL logical replication.
- github.com/nikolayk812/pgx-outbox
  - A simple Golang implementation for the transactional outbox pattern for PostgreSQL using pgx.
includes links to alternatives in readme.
- github.com/amirsalarsafaei/sqlc-pgx-monitoring
  - A database monitoring/metrics library for pgx and sqlc, enabling tracing, logging, and monitoring of query performance using OpenTelemetry.

## Other Possible Options


## Not an Option

- Scanning
  - [scanny](https://github.com/georgysavva/scany)
    - shortens pgx calls. 
    - [Working with PostgreSQL in Go using pgx](https://donchev.is/post/working-with-postgresql-in-go-using-pgx/)
      "Doing SQL in Go got a lot of hate in the past because of interface{} and 
      manually scanning the result into a struct. But with pgx v5, this is no longer
      the case. I think that libraries like sqlx and scany are great but not necessary anymore."
    - No longer necessary.
  - github.com/stephenafamo/scan
    - A type-safe and flexible package for scanning database data into Go types, 
      supporting structs, maps, slices, and custom mapping functions.
  - github.com/Arlandaren/pgxWrappy
    - Simplifies working with the pgx library, providing convenient scanning of
      nested structures
- Testing and mocking
  - github.com/jackc/pgx/v5/pgmock
    - Allows the creation of a server that mocks the PostgreSQL wire protocol,
      useful for testing by simulating various database behaviors. GitHub
      Issues+4Go Packages+4Go Packages+4
    - we will test api. indirectly testing db.
  - github.com/pashagolub/pgxmock
    - A mock library implementing pgx interfaces, enabling simulation of pgx
      behavior in tests without a real database connection.  
    - we will test api. indirectly testing db.
- UUIDs
  - https://github.com/jackc/pgx/wiki/UUID-Support - 2022 check if still true.
  - github.com/vgarvardt/pgx-google-uuid
    - Adds support for github.com/google/uuid.
  - github.com/jackc/pgx-gofrs-uuid
  - https://github.com/jackc/pgx/blob/master/pgtype/uuid.go
    - seems like UUID is built into pgx now.
- Misc
  - github.com/otan/gopgkrb5
    - Adds GSSAPI/Kerberos authentication support
    - wont be user kerberneties for awhile if ever.    