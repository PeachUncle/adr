# Take Shelter Now Website Tech Stack

- **Status:** Active
- **Last Modified:** 2025-05-28

## Context and Problem Statement

We need to align on the technologies we'll use to build out the Take Shelter Now website we're envisioning.
At the time of writing we do have a specific scope in mind, which is to serve mainly the Springfield MO region.
Of course, it would be great for this to scale up beyond that, but we won't spend any time optimizing for that until we find success in our target region.

## Decision Drivers

- The website needs to load a minimal amount of assets as we want it to load as quickly as possible
- We want to avoid paying for hosting and services, at least until there is a significant number of users
- We do want to avoid a backend for the time being as it makes the hosting/deployment more complicated
- The tools we pick should have ample documentation to allow for an easy onboarding path for new contributors

## Options Considered

### Core Framework

- [Svelte](https://svelte.dev/docs/svelte/overview) with [SvelteKit](https://svelte.dev/docs/kit/introduction) generating a static site
- [React](https://react.dev/) with [Next.js](https://nextjs.org/) generating a static site

### Styling

- [Tailwind](https://tailwindcss.com/) + shadcn ([Svelte](https://www.shadcn-svelte.com/), [React](https://ui.shadcn.com/))
- Material UI ([Svelte](https://sveltematerialui.com/), [React](https://mui.com/material-ui/))

### Mapping libraries

- [Leaflet.js](https://leafletjs.com/) with [OpenStreetMap](https://www.openstreetmap.org)
- [Google maps](https://developers.google.com/maps/documentation/javascript/overview)
- [Apple MapKit JS](https://developer.apple.com/documentation/mapkitjs/)

### Data Storage

- Google sheets with build time conversion to static JSON
- Hard coded JSON

## Decision Outcome

### Core Framework

[Svelte](https://svelte.dev/docs/svelte/overview) with [SvelteKit](https://svelte.dev/docs/kit/introduction) generating a static site

While not the most popular frontend framework, Svelte does have bundle size advantages over React as the compiler will only bundle framework features that are actually used.
It also quite user friendly and easy to pick up from the docs.

### Styling

[Tailwind](https://tailwindcss.com/) + [shadcn](https://www.shadcn-svelte.com/)

This decision also comes from keeping bundle sizes in mind.
Shadcn in particular means we only pay the cost for the components we actually use.

### Mapping libraries

[Leaflet.js](https://leafletjs.com/) with [OpenStreetMap](https://www.openstreetmap.org)

While Google Maps and MapKit both have generous free tiers, Leaflet and OpenStreetMaps being open source gives us more flexibility over time.

### Data Storage

Google sheets with build time conversion to static JSON

While we will eventually want an API so that we're not loading all the data at once, for now keeping it one chunk should work for our use case.
Also, keeping it in a Google sheet vs hard coded JSON allows for easy updates by those not familiar with git

### Positive Consequences

- These options allow us to build a lightweight, while featureful web application
- We should be able to quick a working MVP fairly quickly with these tools
- Many of these options stay the same even if we scale up to many more regions

### Negative Consequences

- Svelte is definitely not the most popular JS framework, new contributors will likely have to learn the framework
- Using Tailwind + shadcn is going to product more code in our repo than if we were just using a component library
- The site will have to be built and deployed for data updates to show up
- As our data set grows, we may cause performance issues by loading irrelevant data

## Links

- [public-google-sheets-parser](https://github.com/fureweb-com/public-google-sheets-parser)
- [OpenStreetMap Tile Server Usage Policy](https://operations.osmfoundation.org/policies/tiles/)
