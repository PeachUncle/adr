# ADR 001 - Event Driven Architecture

Date: 19-05-2025

## Status
Accepted

# Summary
Decision was made to use event-driven architecture, to allow us to emit movie match events so that we can display a movie match to all users in a session at the same time.

## Context
The key features of MoviePicker are:
- Retrieving movie data from an external source
- Creating a session for a group of people
- Swiping functionality to 'like' or 'dislike' a movie
- Real-time updates to show if a movie is a match to all users in the session

To do this, we require:
- API to an external movie platform to retrieve data
- Ability to create/edit/delete sessions and have multiple sessions running at once (scalability)
- Real-time updates and interaction between the system and all of the devices connected to the session

## Decision
To best achieve these goals, our team has chosen to use an event-driven architecture approach, as this is a common solution used to problems where real-time updates are required.

Events will occur for the following tasks:
- User swiping: 'liking' a movie will create an event
- Movie match: if the required number of users 'like' the movie, this creates a movie match event

We will also need to ensure that the UI synchronises with the backend, and when these events occur (particularly the movie match), that the UI also reacts accordingly.

## Consequences
Other alternative solutions could be:
1. Monolithic Architecture
    - This would be simpler to implement, however the downside is it does not work well for managing the real-time updates across multiple devices
    - Real-time updates is a MUST HAVE feature of this product, so cannot be compromised

The difficult parts of this will be getting the movie matches to display concurrently on all devices at once. This will require some kind of event handler in our AWS Terraform to be able to receive the movie match event and send responses to all devices.

## Next Steps
The next steps to achieve this will be to understand how exactly we manage multiple requests and synchronise the events across multiple devices, and how we can use AWS to do this. It is anticipated we will use some kind of event bus or event handler to manage the events, but the exact implementation will need to be investigated.