---
status: proposed
date: 2022-05-25
---
# Use GLI to build a command suite terminal application

## Context and Problem Statement

There is a handful of scripts that form a command line interface in the legacy
authorization system. These are implemented as individual files that constitute
one primary kind of transaction each. For example, `qi` queries for
institutions (with an optional wildcard match). This command-line interface is
convenient for some of the users, so we will offer a replacement.

The original scripts all are run from a managed server and connect directly to
the database. We will replace this design with a command line tool that
connects to the API mentioned in [0003-rest-api](0003-rest-api.md).

Many modern tools have moved from a pattern of having individual binaries for
their functions toward a "command suite" style. Well-known examples are git and
kubectl, but there are many more (and not all would be considered modern). We
believe that this pattern is a good one for consistency and discoverability,
integrating online help for all of the commands into a common structure.

There are various Ruby libraries for parsing command line arguments, offering
online help, and dealing with output/logging. Some have specific support for
designing a command suite. This is a common and complicated enough need that
building everything from scratch is not practical, so we should choose one of
the libraries, and design with loose coupling that keeps the I/O separate from
the core operations.

## Considered Options

* [OptionParser](https://ruby-doc.org/stdlib-3.1.2/libdoc/optparse/rdoc/OptionParser.html) (stdlib)
* [Dry::CLI](https://dry-rb.org/gems/dry-cli) (dry-cli)
* [GLI](https://davetron5000.github.io/gli/) (aka "Git-Like Interface")

## Decision Outcome

Chosen option: GLI

We have selected GLI because it is explicitly designed to create suites of
commands. It supports global options (e.g., --verbose), command aliases, and
consistent help output.

We originally planned to use Dry::CLI, but found the help output somewhat
lacking, particularly around subcommands. It also helps that the author of GLI
also literally [wrote the book](https://learning.oreilly.com/library/view/build-awesome-command-line/9781941222409/)
on "Awesome Command Line Applications in Ruby".
