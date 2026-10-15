
# Fine Tuning the implementation of Service Oriented Architecture

## Context and Problem Statement.
Due to our previous architecture being focused around client-server, we needed to rethink how our 'services' would interact.
Initially the idea was to have a centralised database, and shard it based on location (branch). However due to SOA being a modular architecture, we needed to consider how the databases would handle shared data and synchronisation.

## Decision Drivers:
* A solid foundation moving forward in regard to Architecture and Data.
* Clear implementation steps.
* Clear data architecture.

## Considered Options:
* A mutual sharded database that connects the two services.
* Storing state and important information in the user database. 
* Keeping data isolated and corresponding through messages/ requests/

## Pros and Cons:

### Mutual Database
Pros: 
* Easy Implementation
* Experience in the Architecture
* Less application flow overhead.
Cons: 
* Tightly coupled services.
* Against the ethos of SOA.

### User Table Dependent Structure
Pros: 
* Centralised Database for querying the state of books.
* Easier implementation and less SQL bloat.

Cons: 
* Making 2x more API requests than required.
* Lack of scalability/ cross branch functionality.

### Isolated Data/ Message Buffer
Pros: 
* Complete modularity.
* Adheres to the principles of SOA.
* Large breadth of previously implemented systems to reference when implementing ourselves.

Cons: 
* Lack of experience in the architecture.
* Overkill for a library system.
* Annoying implementation.

### Decision Outcome
Isolated Data:

Keeping data isolated allows for us to move forward with modular services in confidence. Ultimately, if we had shared data, the services wouldn't be plug and play, which is the ethos of Service Oriented Architecture. They should be so modular that we could build one on Rust and another with Typescript, it wouldn't matter. 

Sharing data, would simply couple these services together, meaning we'd have issues stack tracing problems, scaling the service horizontally, and handling expansion. 

Having modular services with their own databases that are then sharded based on Branch allows for traffic to be balanced, the addition of more branches, and ease of development when adding additional services down the road. 

In the event of a collapse of a single service, other services would remain functional. For example, in the event of our email verification service going down, we'd still have full functionality for the rest of the system for existing users. 
