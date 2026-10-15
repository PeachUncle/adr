# ADR-1021 API Over Under Fetching

## Status

Accepted, Proposed, Deprecated or Superseded (list DR)

## Context

In API Design it is easy to over and under fetch data.

## Decision



## Why / Notes

### Option 1 Include Everything

Heavy on the server

### Option 2 Many small endpoints

Heavy on the network

### Option 3 Fields parameter

OK for a few. too cumbersome on all. can't optimize db or queries.
Will most fields in the whole system be optional? That would get ridiculous quickly.

### Option 4 Separate Endpoints

Create distinct endpoints for each data variation, such as /users/{id} for basic
user information and /users/{id}/detailed for more detailed user information. 

This approach offers clearer separation of concerns and allows for more consistent
response structures. It also simplifies authorization logic if different endpoints have different access restrictions. 
It's a good choice when the data variations are significant and potentially involve different authorization levels. 

### Option 5. Nested Resources or include / embed:

Nest related resources under a parent resource, such as /users/{user_id}/orders to
 retrieve a user's orders. This can be useful when the relationship between resources
  is strong and clients frequently need both parent and child data.
However, nesting can lead to overfetching and complex structures if not implemented
 carefully. Consider using optional expansion parameters (e.g., ?include=items, ?embed=items) to control the data returned. 

Example:
Let's say you have a Product resource. You might have:

    /products/{id}: Returns basic product information (ID, name, price). 

/products/{id}?include=details: Returns basic info + detailed description, specifications. 
/products/{id}?include=reviews: Returns basic info + list of reviews for the product. 
/products/{id}/images: Returns a list of image URLs for the product. 

/posts?embed=comments
/comments?embed=post

### other notes

- [Should REST API return all "subdata" immediately, or only the identifier and have the subdata fetced from different route?](https://www.reddit.com/r/webdev/comments/5y7lcq/should_rest_api_return_all_subdata_immediately_or/)
In the past, I've made this an option to the user as a URL parameter when the choice was not intuitively obvious. Something like ?deep=true, ?verbose=true, ?compact=true, ?shallow=true depending on which way you want the default to fall. As long as your are consistent the API will be very usable. 

- [Why Mobile Development Needs Separate API Endpoints (And Why We’re Not Just Complaining About the Backend)](https://medium.com/@vignarajj/why-mobile-development-needs-separate-api-endpoints-and-why-were-not-just-complaining-about-the-63406c2e41c2)




## Consequences



## Other Possible Options

## Not an Option

