# 7. Start hosting the API with DigitalOcean and CockroachDB

Date: 2021-11-22

## Status

Accepted

## Context

Given that I haven't in any way yet settled on any details around
implementing the API, it could really be anything. It might be lambdas
in AWS, or a container somewhere, or who knows what else. That said,
I've heard good things about [DigitalOcean][1], and I get the sense
that [Cockroach Labs][2] is doing interesting work.

[1]: https://www.digitalocean.com/
[2]: https://www.cockroachlabs.com/

Furthermore, CockroachDB is [available as a container][3], so I'll be
able to include it in my acceptance tests.

[3]: https://hub.docker.com/r/cockroachdb/cockroach/

DigitalOcean charges &x24;10/month for its most basic Kubernetes setup,
and CockroachDB is free until I exceed 5GB storage or 250,000,000
requests/month (about 8,000,000 /day).

I don't really understand lambdas, and I've been avoiding doing direct
business with Amazon where I can. I probably should learn how to write
things as functions/lambdas instead of always-on services, but I'm
honestly just not interested right now.

## Decision

I'll host the API as a container in Kubernetes with DigitalOcean, and
I'll host the database with CockroachDB.

## Consequences

Lambdas are essentially off the table, as I've committed to running my
API application in a container. Since I always hear good things about
them, I should be careful in how I write the application. I doubt it can
ever be easy to reimplement anything, but it can be well-understood.
If I decide to reimplement the API with lambas, the work should be
well-understood.

With kubernetes, I'm adding my first paid service to the deployment
(second paid service if I count the domain names).

As for CockroachDB, they're a new kid on the block, so it's too soon to
tell what consequences I can expect from starting with them. Whether I
like them or not, if I build my static app to truly work well offline,
then it should also be able to handle database downtime with grace, so I
should always feel free to shop around.
