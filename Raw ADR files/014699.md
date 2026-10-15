# ADR-0020: Exact trigram search

## Status

Draft

Date of decision: Pending

## Context and Problem Statement

Local authority users need to be able to find both landlord and property records in the database using a search
function so that they can interact with those records. There should be eventually over 4.6 million records in
the database so search needs to be relatively fast and good at finding intended records over millions of rows.

In ADR-0019, it was decided to use trigram search as the basis for this search algorithm, but that still gives
a number of different styles of query that could be used.

What is the best way to query the database to return data when searched for by local authority users?
* What database value should be queried?
* What selection criteria should the query use?
* What index if any should be used?

## Considered Options

There are several combinations of answers of the above that make sense together. The full sets of options considered
for each included below.

* Concatenate data values, N results with the highest word similarity, GiST index
* Concatenate data values, word similarity over threshold, GIN index
* Concatenate data values, word similarity over threshold, GiST index
* Concatenate data values, word similarity over threshold & N results with the highest word similarity, GiST index
* Separately query data values, similarity, GIN index

### Considered Options for database values

* Separately query each desired column
* Query over a concatenation of columns

### Considered Options for selection criteria

* Similarity over threshold
* Word similarity over threshold
* Strict word similarity over threshold
* N results with the highest similarity
* N results with the highest word similarity
* N results with the highest strict word similarity

### Considered Options for index
* No indexing
* Add GIN Index
* Add GiST Index

## Decision Outcome

No firm decision reached because major factors are unknown - decision to be finalised when there is a realistic test
dataset to measure performance on.

Interim decision of Concatenate data values, word similarity over threshold & N results with the highest word similarity
without any index, because it will allow ongoing feature development.

Recommendations for changes depending on requirements/experience:
* When the search starts being slow we should add an index to speed it up. With the current set up this will need to be a GiST index.
* If users want to search for unrelated data simultaneously (e.g. email username and name in search as two words) we may want to switch similarity over word similarity and separately query columns
  * Word similarity only matches to a single substring in the concatenated search column

## Pros and Cons of the major Options

### Concatenate data values, N results with the highest word similarity, GiST index
Example query: 
`SELECT t.*, t.name || ' ' || t.email <->> :searchQuery as distance 
FROM table_name t 
ORDER BY distance 
LIMIT 25`
* Good, because fixed number of results
* Bad, because could include bad results
* Unknown, because performance

### Concatenate data values, word similarity over threshold, GIN index
### Concatenate data values, word similarity over threshold, GiST index
Example query: 
`SELECT t.* 
FROM table_name t 
WHERE t.name || '' || t.email %> :searchQuery`
* Bad, because variable number of results
* Good, because will not include bad results
* Unknown, because performance

### Concatenate data values, word similarity over threshold & N results with the highest word similarity, GiST index
Example query: 
`SELECT t.*, t.name || ' ' || t.email <->> :searchQuery as distance 
FROM table_name t 
WHERE t.name || '' || t.email %> :searchQuery 
ORDER BY distance 
LIMIT 25`
* Good, because fixed number of results
* Good, because will not include bad results
* Unknown, because performance

### Separately query data values, similarity over threshold, GIN index
Example query: 
`SELECT t.* 
FROM table_name t 
WHERE t.name % :searchQuery 
OR t.email % :searchQuery`
* Bad, because variable number of results
* Good, because will not include bad results
* Unknown, because will only return when a field closely matches the search query
* Unknown, because performance

## Pros and Cons of the sub Options
### Data values
#### Concatenate data values
* Unknown, because only one clause needs evaluating
* Bad, because parts of the concatenated value might dilute the search term
  * Leads to constraint - cannot use with "Similarity"

#### Separately query data values 
* Unknown, because multiple clauses need evaluating.

### Selection criteria
#### Similarity
* Unknown, because it prefers searches that closely match a queried value
  * Leads to constraint - cannot use with concatenated value

#### Word Similarity
* Unknown, because it prefers searches that closely match a substring of a queried value

#### Strict Word Similarity
* Unknown, because it prefers searches that closely match a space delimited substring of a queried value

#### Over Threshold
* Good, because it works with both GIN and GiST indices
* Bad, because it returns a highly variable number of results
* Good, because the threshold value can be tuned to give more desirable search behaviour

#### N results with the highest
* Bad, because it only works with GiST indices
* Good, because it returns a fixed number of results
* Bad, because it can return results that are not relevant for bad searched

#### Over Threshold and N results with the highest
* Bad, because it only works with GiST indices
* Good, because it returns at most a fixed number of results
* Good, because it won't return completely irrelevant results
* Good, because the threshold value can be tuned to give desired search behaviour
* Bad, because the resulting query is more complicated

### Index types
#### No Indices
* Good, because simplest to implement
* Bad, because performance over larger data sets will be unacceptably slow

#### GIN Index
* Good, because searches will be significantly faster than with GiST
* Bad, because updates will be slower than with GiST
* Bad, because the index will be significantly larger than with GiST
* Bad, because it does not support "N results with the highest..."

#### GiST Index
* Neutral, because searches will be sped up but still slower than with GIN
* Good, because updates will be faster than with GIN
* Good, because the index will be smaller than with GIN
* Good, because it does support "N results with the highest..."

## More Information

* https://www.postgresql.org/docs/current/pgtrgm.html