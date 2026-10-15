# Database Schema Design

[Return to index](https://cse210-group5.github.io/cse210-fa22-ucsd-group5/decisions/)

|  Status   | Confidence    |   Date    |
| --------  | ----------    | --------- |
| Decided   | High          | 13-Nov-22 |

## Context and Problem Statement

Given our system architecture and application we need to define a database schema to store all data in indexed DB

## Decision Drivers

* Completeness: Should be able to store all data required for the application
* Minimalistic: The data should not be unnecessarily repeated.
* Easy Access: It should be easy to directly access the data.

## Decision Outcome

* No timestamp features included in any of the tables (as the app does not support any timestamp based operations)
* For future use cases which require timestamp based operations, we can simply add the attributes createdAt and updatedAt to the tables. This is straightforward, as IndexedDB is a non-relational DB and does not require DB migration in this case.
* Topics and tweets are separated out into separate tables to ensure DB is in 3NF

### Table 1: tweets

| Column Name   | Column Type                   | Data Type | Description   |
| ---           | ---                           | ---       |               |
| tweetId       | Primary Key                   | String    | Unique identifier corresponding to each tweet |
| tweetTitle    | Attribute	                    | String    | Title to be displayed corresponding to each tweet |
| topicId       | Foreign Key (Table: topics)   | String    | Unique Identifier corresponding to each topic |
| textContent   | Attribute	                    | String    | Text content of a tweet |

### Table 2: topics

| Column Name   | Column Type                           | Data Type | Description   |
| ---           | ---                                   | ---       |               |
| topicId	    | Primary Key (Foreign Key from tweets) | String    | Unique Identifier corresponding to each topic |
| topicName	    | Attribute	                            | String    | Title of a topic |
