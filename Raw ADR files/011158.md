# 1. Develop the API, static site, and acceptance tests in isolation

Date: 2021-10-04

## Status

Accepted

## Context

The main thing that I want to build is an iphone app, because that is
the phone that I have. But I don't have a mac, which is what you need to
have to develop one that goes in the app store, so my only option is a
progressive web application (PWA).

According to [this article][1], developing PWAs on iOS is apparently
"great," and [Mozilla has a page about them][2], so I guess I have
everything I need.

[1]: https://love2dev.com/pwa/ios/
[2]: https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps

Whatever I'm making though, the hard part is always figuring out how to
hook in the acceptance tests, so I want to do that first. If I go with
javascript, it looks like [jest][3] is still the thing, although I am
seeing some noise about [testing library][4]. The latter appears to be
built on top of the former, so maybe it doesn't really matter.

[3]: https://jestjs.io/
[4]: https://testing-library.com/

I spent a while with the [redwood tutorial][5], and while there was a
lot that I liked, it looks like [it doesn't support offline apps][6] as
of writing. As a matter of principle, I feel like everything shiny and
new is destined to become outdated and weird, so I'd rather rely on
something that simply isn't weird.

[5]: https://redwoodjs.com/
[6]: https://github.com/redwoodjs/redwood/issues/3093

Besides, this need to completely reinvent web applications is exhausting
at this point. I do like their clear separation of api and web projects
though, so I will keep that in mind.

I'm really talking about four pieces, I think:

1.  A cucumber/selenium harness,
2.  A react app,
3.  The javascript frontend business logic, and
4.  The web application behind the api.

If I code the api in javascript, then I can run unit tests on my react
app, frontend business logic, and api all at once, which would make for
an appealing unity. If nothing else, it is normal to be able to run
things in the root directory.

On the other hand, if I code the api in ruby, then that component is
truly separate, and I'd have a reason to also code the cucumber harness
in ruby. This might at first seem strange, but really there are two ways
of seeing it: either this is a javascript project, or it's a ruby
project with a javascript frontend.

From what I can tell, node is basically considered "not actually ready"
for server-side use, and the main advantage of using it is that
everything is in one language, and one that I don't particularly like.
On the other hand, if I don't use node, then I'm free to use whatever I
actually think is best.

Put this way, I think the way I'd rather conceive of acceptance tests
(rather than e.g. building docker images in a `BeforeAll` function) is
to build 3 images: an api, a static website (that can talk to the api),
and a test running container (that can talk to the static website).
Maybe there'll be a fourth database image, and maybe even others as
well, but these are the three I know I'll need.

This way, running acceptance tests is a matter of `docker-compose up`
instead of `bundle exec cucumber`. If I go this road, I can expect my
project to have this basic structure:

    ./
    |-- api
    |   |-- lib
    |   |   |-- some.rb
    |   |   `-- code.rb
    |   |-- spec
    |   |   |-- some_spec.rb
    |   |   `-- code_spec.rb
    |   |-- Gemfile
    |   `-- Makefile
    |-- features
    |   |-- some.feature
    |   `-- features.feature
    |-- web
    |   |-- lib
    |   |   `-- index.js
    |   |-- test
    |   |   `-- index.js
    |   |-- Makefile
    |   `-- package.json
    |-- Makefile
    |-- README.md
    `-- docker-compose.yaml

## Decision

I'll treat the api, static site, and cucumber container as three
separate software projects all inside a single code repository. What
tools to use for each will be three independent decisions.

## Consequences

This project will seem inaccessible for some developers. Anyone who's
used to seeing a react app or a rails app will be put off by the lack of
familiar structure, and the requirement to know two (or possibly even
three) different programming languages might just be asking too much.

Also, by not just sticking with a known tool, I'm forcing myself to make
a lot of decisions that might be better made for me.

On the other hand, not tying myself to any particular solution frees me
to choose what I think is best for the project, tailoring the tools to
the application instead of the other way around. On principle alone, I
prefer this mindset.

This also frees me up to try more than one framework at a time, seeing
which I come to prefer working with over time. I mean, that actually
kind of just sounds insane, so we'll see if I actually do that.
