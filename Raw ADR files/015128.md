## ADR: Database engine for the project to store relational like data and time series database for storing location data

### Context

We need two types of data stored in the RAC system:

- relational like data (users, cars, etc.). We don't need to create complicated relations between tables, but we need to
  store data in a structured way.
- Time series data of the current locations of users and cars. We need to store the data in a way that we can easily
  query the data to get the current location of a user or a car. We also need to be able to query the data to get the
  location of a user or a car at a specific time in the past.

### Decision

We consider using two different database engines for the two types of data:

- Relational like data: **MongoDB**
- Time series data: **Cassandra** - it will be used by highly available microservices to store the current location of users
  and cars. We will use the Cassandra database to store the data in a way that we can easily query the data to get the
  current location of a user or a car. We also need to be able to query the data to get the location of a user or a car
  at a specific time in the past. There will be a different microservice for storing location data because it has to be
  highly available. Location data will be pushed to the search microservice less frequently than actual users and cars
  data.
- Location updates are going to be pushed to the search microservice less frequently than actual users and cars data.
  This is because we don't need to update the location of a user or a car in the search microservice every time the
  location changes. We can update the location of a user or a car in the search microservice every 5 minutes for
  example. This will reduce the load on the search microservice.

### Consequences

- We need to maintain two different database engines.
- Additional complexity in the system - location updates should be pushed to the search service.
- MongoDB is non-relational database engine. In case of more complicated relations between tables we might need to
  consider using a relational database engine.
