---
status: accepted
date: 2024-03-29
deciders: the-blazing-dev
---

# Bz prefix

## Context and Problem Statement

To differentiate the extension methods from this project from others (which could have a slightly different behavior) we
could introduce a `Bz` prefix (which stands for `Blazing`) to different places of the source code.

## Decision Drivers

* Not conquering with existing extensions from existing projects
* giving the future users the possibility to easily spot the origin of an extension method
* Not colliding with classes and methods Microsoft could add in the future

## Considered Options

* Prefix every class and method
* Only prefix short-named classes
* No prefixes at all
* Use a mix of the above

## Decision Outcome

Chosen option: "Use a mix of the above", because the other options could not fully convince me.
It is definitely a personal decision and I hope it will be the right one ;) 

## Pros and Cons of the Options

### Prefix every class and method

`new BzDisposeAction(...)`
`myString.BzHasContent()`

* Good, because the origin is clear
* Good, because no collision with existing extensions and future framework enhancements
* Good, because consumers could inherit from the classes (e.g. to add more logging) and the origin would still be clear
* Good, because it could lower the hurdle to pull the library into the user's projects
* Bad, because not so fluent to read
* Bad, because more to write

### Only prefix short-named classes

But what is "short-named"? `DisposeAction`? Yes? And `AsyncDisposeAction`?
Probably all extension methods would need the prefix: `.BzHasContent()`, `.BzFallback(...)`, `.BzClamp(...)`

* Good, because it could be a good balance between "no existing/future collision" and "not too much to write"
* Neutral, because the short extension methods are probably the most used ones
* Bad, because the line between short and long is very difficult to draw
* Bad, because probably the most used parts need the prefix which could be annoying

### No prefixes at all

* Good, because users should not really care about the origin if the name is descriptive enough
* Good, because it is not very popular in C# (at least in non-component classes)
* Good, because C# extension methods are ignored if the class itself provides a method with the same name
* Bad, because it is annoying to have name collisions, which could also pop up after a package update / framework update
* Bad, because I already had such collisions

### Use a mix of the above

Proposal:

* use `Bz` prefix for extension method classes (not methods)
    * Good, because it does not hurt
    * Good, because if called manually (or redirecting from existing internal extension methods) the source is clear
* don't use `Bz` prefix for most extension methods
    * Good, because developers are not annoyed with the prefixes all day
* use `Bz` prefix for extension methods if they already collide with existing methods (e.g. `myString.BzSplit`)
    * Good, because users are pointed to different behavior
* put utility classes in different namespace
    * Good, because if someone has potential extension collisions but only wants to use utilities he only imports the
      utility namespace and everything just works
    * Good, because if utilities are later provided through a dedicated NuGet they are already separated 