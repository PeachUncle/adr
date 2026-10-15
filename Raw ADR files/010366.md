# Session Management

## Context

Once a session is created we will need a way to query our SessionService to 
determine who the user is with that session. We will have access to the original
session token via a user’s cookie, so we can use that as an argument, but we 
need to determine what to return and where to put this new code. There are a few
options to consider:

```go
// 1. Return a *Session when we query via session token, then let the caller 
// query for the user separately.
func (ss *SessionService) ViaToken(token string) (*Session, error)
func (us UserService) ViaID(id int) (*User, error)

// 2. Query for the user directly from the SessionService.
func (ss *SessionService) User(token string) (*User, error)


// 3. Query for the user directly from the UserService.
func (us *UserService) ViaSessionToken(token string) (*User, error)
```

## Conclusion

All three of these approaches have a trade-off of some kind. With the first 
approach, we are guaranteed to make multiple database queries. In most cases 
this won’t matter, but SQL databases are very powerful and if our application 
was under load we could optimize queries like this to be done in a single query 
using a join (we will learn about these later).

The second and third approach allow us to optimize the database query, but at 
the cost of intermingling responsibilities. In one case our SessionService needs
to know about the users table and how construct a User object. In the other the 
UserService needs to know about the hashing logic used for session tokens to 
query the sessions table.

We're going to use the second option. Add the following code to the `session.go`
source file.

### Design Decisions and Database

A major factor in our design decision here is the database we are using and the 
way we are structuring our application. We are using a SQL database where joins 
can help us optimize database queries across multiple tables, and we are using a
monolith. That is, we are creating a single Go web server to handle all of our 
incoming traffic.

If using another database, or using microservices, the motivation for one design
decision might no longer be valid, so it is important to keep that in mind and 
opt for the design that works best for each situation.
