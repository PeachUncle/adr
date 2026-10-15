# 003 Stop testing with Ubuntu LTS and Homebrew

<!--
doc/decisions/003-Stop-testing-with-Ubuntu-LTS-and-Homebrew.md
Copyright 2025 Keith Maxwell
SPDX-License-Identifier: CC0-1.0
-->

## Context

Earlier versions of this repository included tests using the latest Ubuntu LTS
and Homebrew. See for example:

    git log -- tests/manual/incus-ubuntu-24.04-homebrew.yaml

### Homebrew usage

For me the main advantages of Homebrew are

1. up to date software versions and
2. a wide range of software packages.

I find Homebrew very useful on MacOS; at most I use it occasionally on Linux. I
generally use compiled Linux software from the following sources:

1. A Linux distribution, so Alpine Linux, Fedora Linux etc
2. Third party distribution repositories like [Copr] for Fedora
3. Upstream projects e.g. GitHub releases
4. Public container image registries
5. Homebrew

These are sorted approximately from most-frequently-used to
least-frequently-used. I also sometimes compile software from source locally.

I have not opened any issues with Homebrew. I do not have any ambitions to
contribute to Homebrew from Linux; at most I am an occasional user of Homebrew
on Linux.

### Other Linux Distributions

Irregardless of this decision the repository will continue to include tests
using:

1. Alpine Linux with Podman — `tests/podman` and
2. Fedora Linux with Incus — `tests/incus`.

### Support Tiers

Homebrew documentation includes [instructions for installing] on Fedora Linux.

Homebrew provides [Tier 2] support on Fedora Linux. The only way to receive the
top tier of support on Linux is with Ubuntu. Homebrew will review pull requests
that fix bugs from a Tier 2 supported configuration; however:

> we will close issues only affecting this configuration

—<https://docs.brew.sh/Support-Tiers#linux>

### Costs of testing

There are differences between Linux distributions. Accounting for these,
sometimes minor, differences when running and maintaining a test suite is time
consuming. Time costs are a major consideration.

## Alternatives

1. Continue testing with Ubuntu LTS and Homebrew
2. Stop testing with Ubuntu LTS and Homebrew

## Decision

Decision is 2.

[Copr]: https://copr.fedorainfracloud.org/
[Tier 2]: https://docs.brew.sh/Support-Tiers#linux
[instructions for installing]:
  https://docs.brew.sh/Homebrew-on-Linux#requirements

<!-- vim: set filetype=markdown.htmlCommentNoSpell : -->
