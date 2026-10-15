# 13. stored datatype in redis and in Domain entities

Date: 2024-05-08

## Status

Accepted

## Context
In a FastAPI application that persists events for external providers, there is a need to decide on the type of data stored in the Redis database. The options considered are:
1. JSON document index vs Minimal index
2. Redis Sorted Set vs Redis Timestamp
3. Use of different types for representing dates in domain entities.

## Decision
After evaluating the options, the decision is to store data in the Redis database using a JSON document index and Redis Sorted Set.

## Pros and Cons

### JSON Document Index
#### Pros:
- **Flexibility**: JSON documents provide flexibility in storing complex data structures.
- **Ease of Querying**: Allows for querying specific fields within the JSON document.
- **Scalability**: Supports storing nested data and evolving data structures.

#### Cons:
- **Storage Overhead**: JSON documents may consume more storage space compared to minimal indexes.
- **Complexity**: Handling nested data structures and querying specific fields may introduce complexity.

### Minimal Index
#### Pros:
- **Efficiency**: Minimal indexes store only essential data, reducing storage overhead.
- **Simplicity**: Provides a straightforward way to store and retrieve data without complex structures.
- **Performance**: Minimal indexes can lead to faster read and write operations.

#### Cons:
- **Limited Querying**: Minimal indexes may limit the ability to query specific fields or nested data structures.
- **Scalability**: May require restructuring data if additional fields are needed in the future.

### Redis Sorted Set
#### Pros:
- **Ordered Data**: Redis Sorted Sets maintain data in a sorted order based on a score.
- **Efficient Range Queries**: Supports efficient range queries for retrieving data within a specific score range.
- **Ranking**: Useful for ranking and leaderboard functionalities.

#### Cons:
- **Limited Data Structure**: Sorted Sets are suitable for specific use cases that require ordering by a score.
- **Complexity**: Managing scores and maintaining the sorted order may introduce complexity.

### Redis Timestamp
#### Pros:
- **Time-based Data**: Redis Timestamps provide a way to store data based on timestamps.
- **Time Series Data**: Suitable for storing time series data and events based on chronological order.
- **Querying by Time**: Enables querying data based on time intervals.

#### Cons:
- **Limited Querying**: Timestamps may limit querying capabilities compared to structured data.
- **Data Structure Constraints**: May not be suitable for storing complex data structures or nested data.
## Pros and Cons of Different Date Storage Types


## Datatypes for Entities in Domain
1. **datetime.datetime:**
   - **Pros:**
     - Provides precise date and time information.
     - Supports arithmetic operations for date/time calculations.
   - **Cons:**
     - Consumes more memory.

2. **datetime.date:**
   - **Pros:**
     - Efficient for applications that only need to work with dates.
     - Supports date-specific operations.
   - **Cons:**
     - Lacks time information.

3. **datetime.time:**
   - **Pros:**
     - Efficient for applications that only need to work with times.
     - Supports time-specific operations.
   - **Cons:**
     - Lacks date information.

4. **str:**
   - **Pros:**
     - Simple and easy to work with.
     - Can be easily stored and exchanged between systems.
   - **Cons:**
     - Requires parsing and formatting for calculations.
     - Not suitable for arithmetic operations.

5. **int/float (timestamp):**
   - **Pros:**
     - Represents a specific point in time as a numeric value.
     - Can be easily compared and manipulated.
   - **Cons:**
     - Requires conversion to/from datetime objects for human-readable representation.
     - May lose precision.

## Selected Decision
The decision to store data in the Redis database using a Minimal Index because the requirements on **FOCUS ON PERFORMANCE**,
and efficient range queries provided by the Sorted Set. This approach balances flexibility, efficiency,
and performance for storing and retrieving events for external providers.
