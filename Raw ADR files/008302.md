# 050621-Back-endStack

Deciders: Carlos Guerrero, Liu He, Waynar Bocangel Calderon

Last Updated: May 8, 2021 1:33 AM

State: Accepted

Tags: backend

# May 6, 2021

## Context and Problem:

Ensuring everywhere access by having an online and offline connection to a database where all the user data is stored.

## Decision Drivers:

- Wanting to implement everywhere access
- Tool familiarity and ease of use
- Library availability and ease of use

## Considered Options:

- PouchDB + CouchDB
- IndexedDB + NodeJS + MongoDB
- PouchDB + NodeJS + MongoDB

## Decision Outcome:

After careful consideration PouchDB was chosen to be the user side database manager because of the documentation on the API and the ease of use. On the other hand (edited May 6th) NodeJS + MongoDB were chosen as the database and manager for the cloud database because of their integration as well as the NodeJS libraries that facilitate authentication, encryption, and easy data storage in MongoDB.

### Positive Consequences:

- Development has started and is moving at a faster pace than with other options.
- The tools used secure flexibility for the user while giving structure to the project.
- The user will be able to access their information from anywhere online and offline

### Negative Consequences:

- A layer of complexity is introduced into the app in the form of data handling
- Increases the risk of over engineering significantly for the backend

## Pros and Cons of the Options:

### Option 1 Pros:

- PouchDB is used as an API for data handling both for the user side and the cloud
- No API design needed for sync with the cloud

### Option 1 Cons:

- CouchDB is really complex and hard to setup before the PouchDB API can be used
- By not having a NodeJS API many great useful libraries for encryption and authentication will not be available
- All backend-tasks would need to move to the front-end which might decrease speed and responsiveness

### Option 2 Pros:

- NodeJS libraries for encryption and authentication are available, making the development time shorter and easier.
- Great integration between NodeJS and MongoDB
- MongoDB + NodeJS is easier to use than the PouchDB API for cloud connection
- Uses a NodeJS API where all authentication and encryption is handled outside the front-end potentially increasing speed and responsiveness

### Option 2 Cons:

- IndexedDB's API is harder to learn than PouchDB's API
- NodeJS API must be designed
- Use of two different APIs, MongoDB for the server and IndexedDB for the user side
- More freedom in NodeJS means higher risk of over engineering

### Option 3 Pros:

- Pouch DB is significantly easier to use than the IndexedDB API making development faster
- NodeJS libraries for encryption and authentication are available, making the development time shorter and easier.
- Great integration between NodeJS and MongoDB
- MongoDB + NodeJS is easier to use than the PouchDB API for cloud connection
- Uses a NodeJS API where all authentication and encryption is handled outside the front-end potentially increasing speed and responsiveness

### Option 3 Cons:

- NodeJS API must be designed
- Use of two different APIs, MongoDB for the server and PouchDB for the user side
- More freedom in NodeJS means higher risk of over engineering