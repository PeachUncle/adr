# 9. Spike an Interface before Writing Feature Specs

Date: 2023-09-01

## Status

Accepted

## Context

When I last started building this project, it was my best attempt yet. I
had working end-to-end acceptance tests driven though a browser, and I
was developing a domain language.

Before I started testing my code, I always found it difficult to pick up
old code. I'd write something, then a couple years would pass, and then
I'd look at my code with a mixture of confusion and disgust.

When I started doing test-driven development, I stopped writing code I
didn't understand, and I stopped being afraid of messing with code that
I hadn't looked at in years. The problem was that I'd often write code
that didn't actually **do** anything. For example, I once wrote a to-do
list with an elaborate and well-defined model for list items and how
they could behave, but there was no user interface, so there was no way
to actually use the dang thing.

When I started doing behavior-driven development, I started building
things that work, and this project was no exception. I figured I could
get the features implemented and iterate on a design later. But I don't
have any experience using HTML, CSS, and JavaScript to design a user
experience. I built a tool with all the features I wanted, but it wasn't
satisfying to actually use it (especially not on a touch screen).

I'm hoping that I can get a proof of concept together. Something that
might forget everything on a reload, and something that certainly
doesn't have any form of authentication, but something that feels good
on iPhones and android devices, on tablets and desktops, and maybe I'll
even try a couple screen readers. I don't use assistive technologies
today, but accidents happen.

As they say, being able-bodied is a temporary condition.

If I can get an interface together that basically feels fun and
pleasing, then I can put it in its own branch, start over, and rebuild
it with tests.

## Decision

I'll build an interface without tests until I have something that feels
good to me on every device I expect to want to use.
