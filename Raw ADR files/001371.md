# Ledger Table Format for Records and Edges
Date: 2025-07-07

## Status
Approved

## Context
In DeepLynx 1.0, we made use of a ledger system in order to version our nodes (records) and edges tables. The purpose of this mechanism was to provide versioning and historical data. The approach in DL1 was to insert, update, and delete the nodes/edges table by inserting new rows into the table with the same ID and a new created_at date, using ID and created_at as a composite primary key. Data was then queried from a view which selected the record with the `MAX(created_at)` date for each unique ID. While effective at a glance, this method caused some latency on lookup and relied heavily on the performance of the `current_nodes` and `current_edges` views. Eventually we decided to make these views materialized (cached) views to somewhat improve performance, with the views being updated when new data was added to the underlying nodes and edges tables. 

The biggest latency concerns occurred when graph traversal queries were executed, as it required recursive joins among nodes and edges, essentially joining on a sub-query multiple times, resulting in subpar execution times. There were also referential issues that occurred when joins were involved, sometimes causing the query layer to return inaccurate results when certain queries were executed if historical records met certain filter conditions but current records did not. Finally, historical records sometimes contained inaccurate references to classes, projects, or data sources if the information about these domains changed at all from the inception of the record to the time of inspection.

As a part of the new and improved design of DeepLynx Nexus, the decision has been made to include historical information as a snapshot and not a reference. In other words, for non-current records, information usually obtained via join such as class name, tags, etc. will be copied onto the historical record instead of using foreign keys. This will allow flexibility in the current state of the database without adversely affecting the accuracy of historical records. The question then becomes which approach to take in order to store this snapshot data- do we take the table-and-view approach championed by DL1, or go for a different approach by keeping the historical (ledger) data in a separate table?

## Decision
The decision has been made to keep the existing records and edges tables intact and maintain a normalized data format for those tables. In order to store historical data, ledger tables called historical_record and historical_edge have been created. These tables will preserve the historical state of affairs for a given record or edge, and when changes are made to the current records and edges (updates, archivals, or new connections), a new record will be created in the historical table. Maintaining the tables in such a way will allow for de-normalized, non-referential data to exist for historical records and edges, while enabling current records and edges to interact with the rest of the database in a normal way. The charts below showcase how CRUD operations will interact with these tables moving forward:

### Historical Records Table:

- Uses its own `id` as its primary key
- Has `record_id` as a foreign key to the records table
- Has all the fields found on records, as well as `class_name`, `project_name`, `data_source_name`, and `tags`, which is an array of attached tag names at snapshot time

| operation | records table | historical_records table |
|-----------|---------------|--------------------------|
| new record created | Normal INSERT, set `created_at` and `created_by` | INSERT INTO SELECT (grabbing `class_name`, etc from other tables) |
| record updated | Normal UPDATE, new `modified_at` and `modified_by` | INSERT INTO SELECT with new `modified_at` and `modified_by` |
| new tag attached/detached | No change to table; adds to/deletes from the linking table `record_tags` | INSERT INTO SELECT updating tags, `modified_at` and `modified_by` |
| class changed | UPDATE `class_id`, `modified_at` and `modified_by` | INSERT INTO SELECT updating `class_id`, `class_name`, `modified_at` and `modified_by` |
| record archived (soft deleted) | UPDATE, set `archived_at` and `modified_by` | INSERT INTO SELECT, set `archived_at` and `modified_by` |
| record deleted (hard deleted) | DELETE record | INSERT INTO SELECT, set `archived_at` and `modified_by`, set `record_id` to NULL |

### Historical Edges Table:
- Uses its own `id` as its primary key
- Has `edge_id` as a foreign key to the edges table
- Has `origin_id` and `destination_id` as foreign keys to the historical_records tables
- Has all the fields found on edges, as well as `relationship_name`

| operation | edges table | historical_edges table |
|-----------|-------------|------------------------|
| new edge created | Normal INSERT, set `created_at` and `created_by` | INSERT INTO SELECT (grabbing `relationship_name`) |
| relationship changed | UPDATE `relationship_id`, `relationship_name`, `modified_at` and `modified_by` | INSERT INTO SELECT, update `relationship_id`, `relationship_name`, `modified_at` and `modified_by` |
| edge archived (soft deleted) | UPDATE, set `archived_at` and `modified_by` | INSERT INTO SELECT, set `archived_at` and `modified_by` |
| edge deleted (hard deleted) | DELETE edge | INSERT INTO SELECT, set `archived_at` and `modified_by`, set `edge_id` to NULL |

These changes will be handled in the business logic code of the application. Use of INSERT INTO SELECT should be applicable for both individual and bulk CRUD operations.