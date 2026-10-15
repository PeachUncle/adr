# API to retrieve PWAs and pipelines

* Status: accepted 
* Deciders: Chris T, Sam W
* Date: 2024-03-12

Technical Story: 
https://fivium.atlassian.net/browse/S29-136

## Context and Problem Statement

On S29 we plan to give the users the option to add pipelines either individually by pipeline number or in bulk via pwa reference.
We already have an API that will provide the pipelines based on ids, pipeline number, pwa ids or pwa reference. 
However, we need the user to select PWA references, which they can't do with our pipelines API.

## Considered Options
With both scenarios, we'll need new api methods in EPA. It would also probably be worth removing the pwa reference parameter from /pipelines 
regardless of the chosen option, as it's not needed if there's a pwas api. 

### Option 1
Create a /pwas api that returns the pipelines in the json request, similar to how the /pipelines api works currently. 
This means that we automatically get the pwa id and reference for each pipeline & we get all the pipleine ids and numbers for each pwa.

### Option 2
Similar to organisation unit/groups relationship. Instead of getting all the data at once from a singular api, we only get the pipelines 
for a pwa if it's specified in the projection root. 
This would involve having a /pwas api that just takes pwaIds or a reference and returns only pwa information. 
Then if the consumer asks for pipelines in their projection root, then we make a request to the /pipelines endpoint with the pwaIds parameter. 

## Decision Outcome
I think that option 2 makes the most sense. It means that we only get the data we need, option 1 could mean receiving all the pipeline information even if it's not asked for in the projection root. 
It's also consistent with similar EPA relationships (org groups/units) & is more similar to how a graphql request works. However, it will be more code. 

Chosen option: option 2, because it follows similar patterns that already exist on EPA & means that we only retrieve the data that we need. 
