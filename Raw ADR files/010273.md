---
status: accepted
date: 2022-05-25
---
# Use Ruby Object Mapper (ROM) for data access

## Context and Problem Statement

Accessing persistent data is a pervasive need, and there are countless
design patterns and libraries to help. The different options emphasize
different factors in the development process, and could be considered
a key element of architectural style.

Within Ruby, the clearly dominant style is to use the ActiveRecord library
(which implements a hybrid of the Active Record, Table Data Gateway, and Row
Data Gateway patterns). This style encourages a database-centric mindset
and combines concerns around querying, saving, validation, and so on, in
service of locality and convenience at the cost of increased coupling.

The alternatives of the Repository, Data Mapper, and Entity/Value Object
patterns are also supported by mature libraries. These patterns encourage the
separation of concerns, in service of explicit responsibilities and looser
coupling at the cost of increased class count and more layering.

## Considered Options

* ActiveRecord
* Sequel (Sequel::Model)
* Ruby Object Mapper (ROM)

## Decision Outcome

Chosen option: ROM for repositories/entities

We have chosen to use ROM for the data layer to optimize for looser coupling
and explicitness in the data model and behavior. While ActiveRecord is
certainly stable and convenient for most common operations, it results in
objects that have very large and unrestricted API surface. Query or saving
operations can happen anywhere, which typically leads to persistence logic
and coupling to the AR library spreading throughout a codebase. ROM, on the
other hand, promises to make the architectural boundary clear and keep
persistence, transformation, and validation in separate, defined areas.

With smaller, explicit interfaces on objects within our codebase (rather than
left implicit as "just ActiveRecord"), we expect to be insulated from the
specific choice of ROM, should it prove a burden. It is not practical to put a
boundary around ActiveRecord in this way, and we take this boundary as a long
term maintenance gain.

## More Information

These notes are not to say that ActiveRecord is bad because it makes you do bad
things, nor that ROM is good because it prohibits bad things. They are to say
that we are prioritizing the explicit definitions and loose coupling to make
the structure and business rules more evident. As an example, the automatic
schema discovery in ActiveRecord is convenient in active development, but can
obscure structure and inhibit understanding during maintenance or when someone
new joins the team. We are choosing to forgo some of the conveniences and
invest in longer term maintainability.

