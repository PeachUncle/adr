---
status: accepted
date: 2022-05-25
---
# Use Hanami::API for the REST API

## Context and Problem Statement

The dominant tool for building REST APIs in Ruby is definitely Rails, but it is
far from the only choice. As described in [0003-rest-api](0003-rest-api.md),
this API will be rather minimal, and the HTTP/JSON parts can be considered
generally uninteresting. We are not extending an existing application with an
API, nor do we intend to integrate other functions into this application that
bias us toward a specific library or framework.

Thus, we are free to choose what we believe are the best tools for the specific
jobs of defining the API, handling routing, processing parameters, and
serializing response data.

## Considered Options

* Rails
* Grape
* Sinatra
* Roda
* Hanami::API (hanami-api)

## Decision Outcome

Chosen option: Hanami::API

We have chosen to use Hanami::API to build the REST API portions. We need very
few facilities for building a typical web application, so using a minimal
framework with low coupling seems wise.

We have also decided to implement the data model and layer explicitly with ROM,
as outlined in [0004-rom-for-data-layer](0004-rom-for-data-layer.md). With the
choice made to not use ActiveRecord, one obvious advantage to using Rails is
not present. There is also some philosophy and design lineage in Hanami, shared
with Sequel and ROM, which should prove complementary.

## More Information

Despite Hanami::API being relatively young as a distinct entity, it is part of
the Hanami project, which has some longevity. It is essentially a packaging of
the new router for Hanami 2.0, explicitly introduced as a low risk way to work
with a meaningful subset of Hanami (which, in its entirety, comprises a range
of full-stack features and conventions intended to be used together). We see
this as a close match to the goals for this project and, generally, an
opportunity to gain experience with Hanami without a larger commitment.

Roda has a similar, minimal, assemble-your-own-framework mindset. It has
features for routing, tokens, JSON, and others, as plugins. It would likely
work about as well as Hanami::API in keeping parts of the application
decoupled. If there are implementation challenges, Roda would likely be the
choice as a replacement component. Sinatra could also possibly provide for this
need, though it is so minimal in design that we would need to invent or adopt
external conventions. Indeed, Sinatra's simplicity was inspirational for both
Roda and Hanami, which layer on further components and conventions in an
explicit, opt-in fashion, contrasted with Rails' implicit, opt-out style.

Grape is interesting because of how thorough it is in supporting a variety of
requirements and scenarios, particularly around versioning and documentation.
However, it is unclear how far the opinionated nature extends into encouraging
coupling. The philosophy seems quite similar to that of Rails, which is to say,
using a significant amount of module inclusion and blocks to establish a DSL,
within a broad and implicit context. This implies a tighter coupling to that
DSL and the tool itself, which we believe may impair our long term maintenance
posture.

Rails was excluded based on how pervasive and implicit its conventions are,
and our experience of trying to decouple from those framework details. With
this project, we seek to emphasize the domain over the tooling, and experience
in maintaining Rails applications has shown us that deep familiarity with the
range of conventions is required for meaningful discoverability -- that the
domain is entangled with the framework provisions in ways that are difficult
to discern without deep expertise in both.
