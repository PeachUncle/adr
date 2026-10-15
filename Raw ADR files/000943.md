# ADR-003: Integrate MusicBrainz metadata to create records by MBID

## Context

We need to support creating a record using a MusicBrainz ID (MBID). When an MBID is provided, the application should automatically fetch the tracklist from MusicBrainz and persist it with the record. The solution must:

- Validate MBID format to reject obvious invalid IDs early.
- Handle valid and invalid MBIDs gracefully without breaking record creation.
- Persist the tracklist alongside the record data and return it in API responses.
- Be testable with both unit and end-to-end tests.

## Decision

1. Add a `tracklist: string[]` field to the Record domain, schema, repositories, and outputs.

2. Introduce a metadata abstraction and implementation for MusicBrainz.

   - Provide a `MusicMetadataService` interface and an injection token, with a concrete implementation `MusicBrainzService` registered in the module.

3. Use the native `fetch` API for HTTP requests and parse MusicBrainz XML responses via `fast-xml-parser`.

   - `fmt=xml` chosen to match functional requirements (`medium-list → track-list → track → recording/title`).
   - HTTP headers include a custom `User-Agent` as described in the site documentation.
   - Parsing is performed with focused helpers to extract clean `string[]` titles.

4. Validate MBID format and handle failures gracefully.

   - MBID validated as UUID (v4 pattern) in the create-record use case.
   - On invalid MBID format: return 400.
   - On fetch/parsing failures: log warning and proceed with an empty `tracklist` to keep creation resilient.

5. Extend tests to cover the MBID flow.
   - Unit tests verify MBID validation, successful fetch populating tracklist, and creation without MBID.
   - E2E tests mock the metadata service for determinism and validate 400 on invalid MBID input.

## Rationale

- Tracklist as `string[]` keeps the model simple and aligned with current API needs. It is sufficient for listing purposes and doesn’t introduce extra complexity prematurely.
- A metadata interface decouples our application from MusicBrainz specifics and enables future providers or changes without ripple effects.
- Validating MBID format close to the use case makes it consistent across transport layers and ensures a single source of truth.
- Non-throwing fetch behavior (returning `[]` on errors) avoids blocking record creation due to external service instability, while still providing logs for observability.

## Alternatives Considered

- Parse JSON instead of XML:

  - Reject: due challenge specifications

- Make tracklist a richer structure (disc/position/duration):

  - Pros: More fidelity for UI/analytics.
  - Cons: More schema churn and testing burden without immediate product need.

- Hard fail on metadata fetch failure:

  - Pros: Guarantees records with MBID always have tracklists.
  - Cons: Reduces resilience, couples record creation to external uptime.

- Use a third-party HTTP client (e.g., Axios):
  - Pros: Built-in retries, interceptors, convenience.
  - Cons: Added dependency without strong need; native `fetch` is sufficient.

## Consequences

- We introduce a new dependency: `fast-xml-parser`.
- Tracklist data increases document size minimally; indexes and queries remain unaffected.
- External call during creation may add small latency when MBID is present.
- Logging warns on fetch failure, aiding observability without crashing flows.

## Future Improvements

- Add retry/backoff strategy (e.g., exponential backoff) and timeouts to the metadata fetch.
- Cache tracklists by MBID (in-memory or Redis) to reduce external calls.
- Enrich `tracklist` with disc/position/duration metadata or store a structured type.
- Add telemetry for external call durations and failure rates.

## References

- MusicBrainz Web Service: https://musicbrainz.org/doc/MusicBrainz_API
- fast-xml-parser: https://github.com/NaturalIntelligence/fast-xml-parser
