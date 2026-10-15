# Publishing Webhook

## Date
2025-09-19

## Status
`Accepted`

## Context
The current publishing mechanism as described in the previous publishing ADR (0008_publishing.md) was working well, but after adding new API endpoints and considering the support of new consumer applications, we believe it's worthwhile to improve upon our publishing mechanism. Below are some of the issues/limitations with the current publishing mechanism.
1. Consumer applications have to support separate publishing and unpublishing endpoints.
2. To support publishing additional entities (ie. collections), consumer applications will have to add additional endpoints.
3. The current publishing mechanism contains an additional Item serialization, now that we have an API we should try to match that serialization.
4. Now that the Apotheca API is providing download links we should change the publishing payload so it doesn't include paths to the files in S3 and instead includes the Apotheca download URLs

## Decision
1. To make the publishing mechanism more agnostic and make consumer application integration easier we will move toward having a publishing webhook that sends a payload to one endpoint on the consumer application. The payload will contain the action and the data that should applied.
2. The payload send to the consumer application will be in the format below. The `item` key will contain the same Item serialization returned by the Resource API.
   ```json
   { "data": { "item": {} }, "event": "publish" }
   ```
3. The consumer application will be expected to respond with 2XX http status code and a URL that resolves to the newly published item if the publish request was successful. If the request was unsuccessful, the consumer application will be expected to respond with a 5XX code.

## Consequences
1. Consumer applications will only need to implement one endpoint, but the downside is that this one endpoint will have to support different actions.
2. The publish payload is still going to be large because it will include a serialization of the Item that includes all its Assets.
