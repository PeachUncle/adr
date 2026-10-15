
# Architecture Design Record - Application State Storage Location

> Last updated Nov. 6, 2022

## Context and Problem Statement

How do we plan on storing application state locally for our application? What are the considerations for choosing different localstorage methods? We need a performant and versatile solution.

## Considered Options

* Cookies
* localStorage
* Session storage
* IndexedDB
* WebSQL

## Decision Outcome

Chosen option: **localStorage**

### Consequences

* Good, convenient and universal API
* Good, all team members should already be familiar with localStorage
* Good, stores data with no expiration date and with privacy such that data is never transferred to the server
* Good, storage limit is about 5MB.
* Neutral, because a little more complex than other options 
* Bad, because it is does not allow for a lot of flexibility(e.g. only stored as string in lists of key value pairs)

## Pros and Cons of the Options

### Cookies

* Good, convenient and universal API
* Neutral, because unclear regulatory restrictions on cookies in certain jurisdictions
* Bad, because small storage size limit (less than 4KB)
* Bad, because takes more effort to serialize more complex data

###  Session storage

* Good, very similar to localStorage
* Neutral, provides individual use of storage but is not appropriate for our specifications
* Bad, not persistent across sessions (clear on tab close).

###  IndexedDB

* Good, because allows for more complex storage functionality
* Bad, because blocks the DOM
* Bad, because reportedly inconsistent API implementations across browsers
* Bad, because using a DB can add unnecessary complexity and footguns

###  WebSQL

* Bad, because deprecated and support being dropped from current browser versions

## More Information

Local storage appears to be the standard way of storing persistent data for web applications. The most useful part of local storage is it is the only way to have DOM non blocking IO calls as you can asynchronously access local storage inside a web worker. This is probably irrelevant to our use case since our data is very small (n=100). The structure of our data is also straightforward and not demanding of a more involved DB.

