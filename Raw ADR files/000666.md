# 006_uuid_or_long

## Context

Each database table needs a primary key. Traditionally in Spring (if you look at books, like Java Persistence by Tudose) Longs are used for that. However, there is also the option nowadays of using UUIDs, which I (EWL) so far have chosen for the AttendanceTracker. However, is this a good choice?

There are quite some articles on the internet describing the tradeoffs between Longs and UUIDs. (there are good reasons not to use ints; see https://www.cybertec-postgresql.com/en/uuid-serial-or-identity-columns-for-postgresql-auto-generated-primary-keys/ : the four wasted bytes don't matter much in view of the pain of migration when you run out of space (some tables may get large Ids simply because of deletions; or, as https://brandur.org/nanoglyphs/026-ids states "32-bit serials are never worth it.")

Longs, of course, are smaller than UUIDs, so databases need less memory. This may also affect performance as indexes need to be stored in memory/the cache.

UUIDs have some advantages, however:

1. if ever databases are sharded/distributed, UUIDs win
2. if ever databases are merged with other databases, UUIDs win as there won't be conflicts
3. UUIDs help for security purposes, as brandur states: "IDs that are opaque to users (i.e. not a sequence) are beneficial for security and business. They prevent iteration/collision attacks, and make it difficult to infer anything the quantities of data that exists, or the rate at which it’s being generated." and "Avoid serial ids in public APIs. Serial ids produce compact id spaces, so if an attacker knows user_id 123 exists, they can guess that id's 1 through 122 also exist. iirc, that exact approach was used to scrap the Parlor data, since their message ids where auto-increment ids."
4. UUIDs help avoid bugs/errors. As 'Human_Capitalist' said on https://www.reddit.com/r/PostgreSQL/comments/kzv50w/uuid_vs_int_for_primary_key_which_is_better_with/ : "You don't realize how many potential errors you have with INTs until they go away, and you start catching them all due to the uniqueness of UUIDs. It becomes impossible for a user to access the wrong table by mistake. And UUIDs only look confusing for the first month or two, you soon start just calling out the last 3 or 4 digits to identify a row to a colleague or check a result, and it's no harder than disambiguating two 7-digit numbers that only vary by 1..."

Further sources:

- https://www.baeldung.com/uuid-vs-sequential-id-as-primary-key
- https://blog.boot.dev/clean-code/what-are-uuids-and-should-you-use-them/
- https://stackoverflow.com/questions/12378220/api-design-and-security-why-hide-internal-ids/

An important rule in software development (see Code Complete 2) is to not optimize performance until it turns out to be a problem, use the simplest solution available instead. Sequential Ids and UUIDs are about equally simple to code, but UUIDs avoid a lot of problems. Flexibility is usually far more important than performance (until performance matters, of course), so UUIDs for now seem to be the way to go.

## Decision

We'll choose UUIDs for now.

## Status [Proposed, Accepted, Deprecated, Superseded]

Accepted

## Consequences

- if performance ever becomes slow, ULIDs (https://github.com/ulid/spec) may be the way to go. If we have time, it may even be worth to use ULIDs before going into production, but the costs/benefits of such an intervention and its necessary extra code should likely be investigated first.
