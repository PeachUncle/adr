# Backend Language

[Return to index](https://cse210-group5.github.io/cse210-fa22-ucsd-group5/decisions/)

|  Status  | Confidence |   Date    |
| -------- | ---------- | --------- |
| Decided | Moderate | 3-Nov-22 |

Depends on [ADR-0003](0003-data-storage.md)

## Context and Problem Statement

The backend will store, manage and update all data that the app will work with. This includes all notes, the topics any configs etc. The methods written in the backend would be called by the frontend and used to serve the data in the app.

## Decision Drivers

* Functionality: The language should be a good fit to support the functionality of our app such as integrating well with the storage we use
* Documentation: The language should have good documentation available for learners to work with it
* Simplicity: The language should enable us to accomplish tasks with simple methods.

## Considered Options

* Javascript
* Node.js
* Python

## Decision Outcome

Chosen option: "Javascript", because it is general enough, satisfies capability requirements, some team members have familiarity with it, and integrates well with our frontend tech stack.

<!-- This is an optional element. Feel free to remove. -->
## Pros and Cons of the Options

### Javascript

* Good, because well-known and widely used so has lots of guiding examples and documentation
* Good, because its client side scripting characteristics align well with out application requirements
* Good, because it is easy to integrate with our javascript based frontend
* Good, because some team members are well versed in it
* Bad, because it has a slightly strict learning curve for the newer practitioners

### Node.js

* Good, because it does not contain OS specific constraints and might allow for easy portability
* Good, because npm provides easy environment and package management
* Bad, because it is for server side scripting which does not align with our application requirements

### Python

* Good, because of high familiarity and ease of working
* Bad, because it is not easy to integrate with a web app fontend
* Bad, because can be cumbersome to write simple functionality
