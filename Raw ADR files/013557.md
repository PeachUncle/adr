# 1. Use Explicit Contexts

## Status
Accepted

## Context
Michael Nygard has a very interesting idea that should allow system to evolve over time. From his book [Release It!]():

>Suppose your service receives this fragment of JSON inside a request: `{"item": "029292934"}`
>
>How much do we know about the item? Is that string the item itself? Or is it an item identifier? Maybe the field would be better named “itemID.” Supposing that it is an identifier, our service can’t do very much with it. In fact, only four things are possible:
>
>1. Pass it through as a token to other services. (This includes returning it to the same caller in the future.)
>2. Look it up by calling another service.
>3. Look it up in our own database.
>4. Discard it.
>
>In the first case, we’re just using the “itemID” as a token. We don’t care about the internal structure. In this case it would be a mistake to convert it from string to numeric. We’d be imposing a restriction that doesn’t add any value and will probably need to be changed—with huge disruption—in the future.
>
>In the second and third cases, we’re using the “itemID” as something we can resolve to get more information. But there’s a serious problem here. The bare string shown earlier doesn’t tell us who has the authoritative information. If the answer isn’t in our own database, we need to call another service. Which service?
>
>This issue is so pervasive that it does not even look like a problem at first. In order to get item information, your service must already know who to call! That’s an implicit dependency.
>
>That implicit dependency limits you to working with just the one service provider. If you need to support items from two different “universes,” it’s going to be very disruptive.
>
>Suppose instead the initial fragment of JSON looked like this: `{"itemID": "https://example.com/policies/029292934"}`
>
>This URL still works if we just want to use it as an opaque token to pass forward. From one perspective, it’s still just a Unicode string.
>
>This URL also still works if we need to resolve it to get more information. But now our service does not have to bake in knowledge of the solitary authority. We can support more than one of them.
>
>By the way, using a full URL also makes integration testing easier. We no longer need “test” versions of the other services. We can supply our own test harnesses and use URLs to those instead of the production authorities.
>
>This example is all in the context of interservice communication. But making implicit context into explicit context has big benefits inside services as well. If you’ve worked on a Ruby on Rails system, you might have run into difficulty when trying to use multiple relational databases from a single service. That’s because ActiveRecord uses an implicit database connection. This is convenient when there’s just one database, but it becomes a hindrance when you need more than one.
>
>Global state is the most insidious form of implicit context. That include configuration parameters. These will slow you down when you need to go from “one” to “more than one” of a collaboration.

## Decision
When possible, we will use a URI as the primary key for objects. Depending on the system in question, it may not be an easily resolvable location and may have to be deconstructed a bit before getting to something readable. For example: `mongodb:read-only-user@mongodb.example.com:5762/some-dataset?_id=9876` probably won't have an available protocol handler, so one must be written.  

## Consequences
If we can use stable names for the authority portion of the URI, we should be able to move services around and still have systems find the data they need. One element we have to be keenly aware of is that changing the scheme portion later will be very difficult, if not impossible. If available, an HTTP or GraphQL URI should be preferred over direct database or coordinates. In practical terms, this means that we still use database generated primary keys but return a URL as the ID of the asset.  For example, document `1234` would be exposed to the caller as `http://alpha.test.example.com/user/1234`. If that URI is ever "tugged" on, hyperlinks are provided to other possible operations on the resource.