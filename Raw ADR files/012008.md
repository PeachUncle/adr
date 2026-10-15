# ADR 002 - Databases

Date: 01/05/2025

## Status
Accepted

# Summary
Decision was made to not store movie data within our application, and instead use the TMDb API and send requests only when we require movie data.

## Context
MoviePicker collates movie information from a range of platforms, so we needed to find a centralised source that we could get this data from. We thought about initially storing the movie data ourselves in databases hosted on AWS, however we realised this would take up a lot of space and it may affect the performance of the application. So we decided to investigate if there was another source that already contained all of this data that we could simply make an external API request to when we needed it. This would save us needing to store information like movie titles, actors, genres, descriptions, ratings and movie photos. Instead we could just reference each movie by its unique ID in our databases.

## Decision
The decision was made to make API requests to the TMDb database, which stores movie data and a range of different attributes associated to movies. This means that when our application displays movie options on the UI, we simply make a request to TMDb with a specified movie ID, and retrieve all of the corresponding data we require on our UI. This will mean we don't need to have another database of our own storing movie data, and instead the only databases we need will store the session information and the number of swipes on each movie ID.

## Consequences
One potential consequence of this approach that we discussed was that we may be making a lot of calls to TMDb at once. If we have lots of current sessions running, each with a large number of users, then we will be making requests every time a new movie is displayed on a person's device. This could cause issues with connectivity or with the speed of our application. This will mean we need to ensure our application is scaled appropriately in periods of high activity and that our load balancer can handle all of these requests.