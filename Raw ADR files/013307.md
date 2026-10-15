# ODR2: Building dynamic web frontends using Webflow

**Status:** \(draft\) accepted

**Deciders:** Adi Eyal, JD Bothma, Lunga Mthembu, Matthew Stark

**Date:** 2019-10-?

## Context and Problem Statement

We build many fairly simple but often at least slightly interactive or data-driven tools for the web.

Convenient, usable interfaces are critical to most of our projects. The friction stopping a user from completing their task must be minimised.

We usually ought to iterate towards an ideal solution since it is hard to predict what the right tool is to build, or what users will find challenging to use.

We have found iteration with the typical designer + frontend developer\(s\) arrangement frustrating, since frontend developers struggle to implement the design and struggle to communicate what can be compromised in the design, while designers struggle to communicate what the essential aspects of the design are.

## Decision drivers

* The designer must be able to rapidly iterate on the design in a tight loop with feedback from users 
* We do not have the massive budgets industry dev teams like e-commerce have to push pixels to perfection 
* The design process must be informed by real or very realistic data
* The design must be aesthetically pleasing - this promotes trust and confidence in a tool, as well as excitement and enthusiasm for using a tool

## Considered options

* Webflow with custom javascript to manipulate the page content based on data from outside webflow
  * Perhaps hosted by webflow with custom javascript linked from elsewhere
  * Perhaps exported and hosted as a static site or as django templates
* Hand-written html with a css framework like bootstrap, ES6 and/or jQuery
  * Perhaps react for particularly interactive components
  * Perhaps a component library with hand-written HTML like Materialize CSS
* React full sites, e.g. with frameworks like Gatsby

## Decision outcome

Chosen option: _"Webflow with custom javascript to manipulate the page content based on data from outside webflow"_ because in trials we found it effective at meeting the above requirements in our context.

## Positive consequences

* We have been able to build and iterate on beautiful interfaces rapidly with a very small team of skilled developers, even though they are not CSS experts.
* We have been able to continue building user interfaces despite our frontend lead developer leaving the organisation.
* **There's no styling step for frontend developers.** We can rapidly prototype design options in-browser with working HTML and CSS, and then the it's built - there's no re-implementation step after design. Only Javascript needs to be written if the new component needs dynamic data in production.
* Webflow developers can build fun or helpful interactions which often work without additional dev effort in the final page.

## Negative consequences

* This approach requires strict discipline from the webflow developer and javascript developer to adhere to conventions that keeps a site built using this approach maintainable.
* There is very little existing awareness of this approach.
  * We have to discover and codify the conventions ourselves.
  * Every new developer working on our projects has to learn this approach and the required conventions
* Every dynamic/data-driven component requires javascript to be written - e.g. we have to build our own library for populating and responding to user interaction of a dropdown.
  * We might be able to build a reusable library of this code
* **Webflow does not lend itself to branching in the development process** as is important when
  * two or more changes are being implement
  * one has to be released without the other
  * it is not clear at the outset which will be released first
  * e.g. the main menu is being changed in a way that requires javascript changes, but we can't make the javascript changes yet because we need to fix another bug more urgently, but the main menu has already been changed in webflow.
  * This becomes less of an issue
    * the more established the webflow component library \(and its accompanying javascript\) is
    * and the more you use cloned components over in-place components 
* You can't upgrade your component library quite like a typical one. You can backport features to old sites though, and manually fix conflicting styles.
* It's hard for other organisations to build on such user interfaces, even though they can clone the webflow project.
  * Webflow Lite $16/month or Team $70+/month is needed to be able to update and export the design or components, which impacts on other organisations' willingness to build on as open source.
  * Upstreaming improvements, or merging in upstream changes, is less controlled and well-defined than coded interfaces.
* We often have to stop and think whether an interaction should be built in webflow or javascript/css
  * This might still be cheaper considering that we often don't have to build those interactions outside webflow.
* Repository history of CSS and HTML files become useless due to Webflow not necessarily respecting consistency and order when exporting.



