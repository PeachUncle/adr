# ADR-0019: Search Algorithm Basis

## Status

Accepted

Date of decision: 2024-11-06

## Context and Problem Statement

Local authority users need to be able to find both landlord and property records in the database using a search
function so that they can interact with those records. There should be eventually over 4.6 million records in
the database so search needs to be relatively fast and good at finding intended records over millions of rows.

What basis for database searching should we use?

## Considered Options

* Naive Substring Matching
* Full Text Search
* Trigram Search

## Decision Outcome

Trigram Search, because it allows efficient fuzzy matching on relatively short strings that are not a body
of text written in a known language. This is the best fit for our current use case of searching names,
email addresses and similar values that are not that long and not written in words from a language.

## Pros and Cons of the Options

### Naive Substring Matching

Using inbuilt Postgres functions and operators for matching substrings such as LIKE, ILIKE, ~ or ~*.

* Good, because it is included with Postgres by default.
* Good, because it is very simple to write queries using these operators and functions.
* Bad, because without additional support it will have very slow performance.
* Bad, because it requires exact matching to return values.
* Bad, because it gives no way to rank similarity (i.e. it matches or it doesn't)
* Neutral, because we could offer RegEx support to LA Users.

### Full Text Search

Using inbuilt Postgres functions for searching documents for text matches using `tsvector`s and `tsquery`s.

* Good, because it is included with Postgres by default.
* Neutral, because writing queries requires understanding some additional background on Postgres text search.
* Neutral, because it is language aware and can match equivalent words (e.g. match properties to property)
  * This is neutral because we are searching for names, emails etc. rather than english words.
* Neutral, because it is performant for searching for word matches on large natural language documents.
* Bad, because it requires exact matches for terms that are not words in a language it knows.
* Good, because it gives a way to rank similarity.

### Trigram Search

Use the Postgres trigram extension (`pg_trgm`) to carry out trigram search to find close text matches.

* Neutral, because it is included in an easily added extension to Postgres.
* Neutral, because writing queries requires understanding some additional background on Postgres trigram search.
* Good, because with indexes it has fast performance on matching short strings.
* Good, because it matches based on string similarity without requiring exact or language aware matches.
* Good, because it gives a way to rank similarity.
* Good, because it allows matching even with typos in the search term.
* Good, because it allows for multiple configurable valuables and variable applications to give best results.
* Good, because it massively improves the performance of exact substring matching if required.
* Bad, because search indices can become very large (as large or larger than the searched data)

## More Information

* https://www.postgresql.org/docs/current/functions-matching.html
* https://www.postgresql.org/docs/current/textsearch-intro.html
* https://www.postgresql.org/docs/current/pgtrgm.html