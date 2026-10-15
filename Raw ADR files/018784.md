# 4. Handle Abuse From Tickets

Date: 12/2/2019

## Attendees

- Briana Coppard
- Adrian Evans
- Apoorv Kansal
- David Allen
- Nick Dawbarn
- Tim Patullock
- Daniel Bradford
- Lucas Hills
- Levi Serebryanski
- Wayne See

## Status

Accepted

## Context

The endpoint we use to submit tickets, `api/v2/requests`, is getting a lot of spam from requests that look like the Web Widget. The abuse team believes that adding recaptcha to the Web Widget will help mitigate this problem by adding friction to this process.

The concern with this is that the request endpoint itself is still open for abuse, and the spam requests might not be coming from the Web Widget, they might just have some params in the request to make it seem that way.

The issue is that the request endpoint is used heavily by app developers and customers with their own web forms set up. This means adding authenitcation directly to the endpoint will likely break a lot of things and Zendesk will need to give lots of warning to our customers that this change is coming.

In a meeting with Max McCal from the box office team (who owns the request endpoint) and David Niergarth and David Liberman from orca team (abuse team) we discussed these concerns and they believed that the abusers aren't very sophisticated so are using the Web Widget as the vector for attack, even though they could simply curl the endpoint. The would like us to implement recaptcha or something to close off this angle. The Box office team is working on a longer term fix for the endpoint itself but it will likely take a lot of time for this to be implemented as it breaks many apps and many customer implementations.

In an investigation I concluded it was very unlikely that the spammers were using the Web Widget as we weren't seeing any increase in ticket submission user action blips and many customers didn't even have the widget configured. However it would still be a good idea to implement something in the widget to shut down the chance for spammers to use it.

### Possible Approaches

Note that all these solutions have the same con that they don't fix the root issue that the requests endpoint is easy to spam. The Box Office team is in charge of fixing that issue but it will be a long process.

**Implement Recaptcha in Widget**

This approach is based on Help Centers implementation for recaptcha. It's not the most secure implementation but will get the job done for most use cases.

- We generate a new Web Widget Google Recaptcha account for the client side rendering of the captcha service. This would be similar to how Help Center does it so will have the lowest security settings and won't have site whitelisting. This allows us to use the same key for all customers of the Web Widget.
- We set up recaptcha in the contact form of the Web Widget. This shows if the customer has the "require captcha" setting turned on in this Zendesk account.
- We build a verification service that the Web Widget can hit after a form is submitted. This would add the secret key to the payload and call out to googles authentication service and then proxy the response back.
- If we get a negative response from the endpoint we would stop the form from submitting.

Pros:

- No change to the request endpoint
- We could use this for all the forms in the Web Widget, not just the request form
- No code needed from the customer to implement this

Cons:

- More friction for legitimate users.
- This service would be better to be built into the requests endpoint

Future enhancements this could allow:

- Add captacha to all forms
- We would allow customers to be able to specifiy their own google keys. This would allow them to add a site whitelist and specify how many steps the end user needs to validate.

**Proxy ticket requests through embeddable**

- We send all requests through embeddable. This would allow us to do some spam detection and block requests from the same ip address.
- We could potentially combine this with the recaptcha approach and do validation for captcha on this endpoint.

Pros:

- No change to the request endpoint
- No code needed from the customer to implement this
- Potentially no friction for end users

Cons:

- Redoing functionality that should be handled by the requests endpoint
- More for us to own
- Feels like we would be moving backwards from all the work we did to make the Widget hit classic directly
- Potential for us to accidentally block legitimate traffic

The requests endpoint is going to get spam detection added to it that would be much nicer then this so this would always be a temporary measure.

**Rate limit on the client**

- Stop any new request from being sent for maybe 1 minute after a request is sent.
- We could store something in local storage to stop the end user from simply refreshing the page. If we also store this in local state even if they clear cookies it wouldn't work. They would have to refresh the page and clear cookies over and over to spam the endpoint.
- Backoff over time
- Send a blip if we hit the backoff to track this

Pros:

- Very easy to implement
- Unlikely to introduce any friction to legitimate users

Cons:

- There are ways to get around this and continue to use the widget to spam the endpoint

If Max and David are correct that most of these spammers aren't very sophisticated this could be all the friction we need to add to the experience for them to move on. This could be a small measure to help until the proper fix is implemented on the requests endpoint.

## Decision

We Rate limit on the client as a first step to this

- Give a reasonable rate limit: 3 per minute with a backoff that doubles in time each time it is hit. Show a message to users to say "try again later" for legitimate users if this is ever hit.

We like this because until the request endpoint itself has authentication added or some way to mitigate spam it is still very vulnerable no matter what we do, and it doesn't seem worth spending more time to add something like captcha which will cause friction to legitimate customers unless then request endpoint starts blocking requests that don't have it because it would still be easy to circumvent the captcha.

## Consequences

- We will implement the client side rate limiting for tickets in the widget.
- Could reduce spam from the widget.
- Could impact legitmate customer workflow if they rely on the widget to send a lot of requests for some reason.
- Extra thing in localstorage from us.
