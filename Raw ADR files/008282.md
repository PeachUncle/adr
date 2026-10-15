# Architecture Design Record - Structure of Storing Application State

> Last updated Nov. 6, 2022

## Context and Problem Statement

How do we plan on structuring our data when storing for our application? The main concerns are ease-of-access for filtered/sorted data and usage of storage space.

## Considered Options

* Store separate tables for separate sortings of data
* Store one data table and sort again whenever displaying under different sorting order

## Decision Outcome

Chosen option: **Single table**

### Consequences

* Good, because do not need extra space to store the same info multiple times based on different sorting options.
* Good, because schema will be simpler than having multiple tables
* Good, because sorting will not need to be performed under each write.
* Good, provides simpler code complexity
* Neutral, because likely low data size for application means either probably works
* Bad, because takes extra time to compute when changing sorting options or creating a new listing.

## Pros and Cons of Other Options

### Multiple Sorted Tables

* Good, because no need to sort data repeatedly when a new filter is selected.
* Good, because once a new listing is created, we just have to find the right place for that listing in each table to update the table.
* Good, avoids having to sort the data repeatedly based on different criteria, but incurs extra storage costs.
* Neutral, because likely low data size for application means either probably works
* Bad, because more storage costs and more tables to manage by the end. 
* Bad, because sorting time will be more with an insert for each table
* Bad, because handling more tables increases code complexity


## More Information

In a low data size setting, both storage costs and computation time for sorts will be low, so either method will probably work.  However, in a larger data setting it might scale better to have a single table in certain use cases, and to have multiple or other similar solutions in others. A single table might be a better choice as well for if the application decides to move to the cloud and each user requires their own account. It is not feasible to have every user store a large amount of tables. This depends on how often the user has to sort the data as well based on the exact size of the data, etc. If we frequently sort and do not have many computing resources or computing is done locally there may be problems with the interface lagging as it waits for sorting.  On the other hand, extreme data size may be a problem for either the server or user depending on where data is stored.

