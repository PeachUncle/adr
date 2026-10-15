---
title: [Users/User Profiles ADR] - [Store locations]
status: Proposed
date: 05-25-2025
decision-makers: [Noeh Parrales, Thanh-Long Nguyen-Trong, Phiroze Duggal, Christos Enotiadis]
---

- store locations based on so that we can add [markers](https://developers.google.com/maps/documentation/javascript/advanced-markers/add-marker)

- [text search](https://developers.google.com/maps/documentation/javascript/place-search)

figure out how to get and store coordinates so that we can use markers on the map

## Summary

The team ultimately consulted and chose the Google Maps API to solve the issue of needing to store markers on a map. This is a crucial function of our application in order to save data, locations, and memories.

**One-sentence overview of the decision.**

Currently we have the Google Maps API simply rendering a map of the chosen location, but with this new addition of enabling the marker feature for the Google Maps API and integrating it we will be able to create markers on the map based on text queries, which will then be coordinated with the backend team so that we can place and view memories. The next step will be coordinating to display these created memories on the List, and also on the list only page accessed via the toggle.

## Context and Problem Statement

We must figure out how to get and store coordinates so that we store them in the IndexDB to efficiently create markers on the map. Currntly, we were using the Google Maps API which renders the map of a chosen location (San Diego), but we had no way of display that information on the UI and no way of storing that information in the backend. Saving these coordinates are crucial for the app in order to save, view, and share memories. This is a main, if not the main feature of the application.

## Considered Options

- Google Maps API (chosen option)
- Mapbox GL JS
- Leaflet

## Decision Outcome

We ended up using Google Maps API as the other options did not match the capabilities and ease/usability as compared with Google Maps.

### Consequences

Google Maps API

- API is not free
- Limited to 10,000 API requests
- Requires secure key handling

Mapbox GL JS

- Its more complex to set up, the styling and configuration requires more effort
- Set up includes generating and securing access tokens
- Also charges based on map loads and API requests

Leaflet

- Large styling and behavior options assigned with Leaflet Maps API
- tiles do not stay cached offline as well as when using gmaps

### Confirmation

Google Maps API

## Pros and Cons of the Options

Pros:

- Usability perk - no other API option compares with Google Maps to display and store precise coordinate data.
- Extremely Lenient API Requests limit
- Almost impossible to surpass more than 10,000 API Requests for our demo.
- Almost every other API is fully paid or has lower limits.
- Search feature allows for increased User Accessibility for search for places when adding to their map
- Best Mobile Optimization amongst available APIs.

Cons:

- API contains a threshold of requests before we must pay (10,000 API requests). The API is not free.
- Almost impossible to change to alternatives once we implement Google Maps API
- Privacy - Google will store the user's location data and usage.

## More Information
