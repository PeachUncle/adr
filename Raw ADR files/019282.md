<!-- cspell:ignore statefulness, replicache, dexie, barebones -->

# Alternative architecture

**Date:** `06.09.2025`

**Status:** `accepted`

## Context

That was fast and it's a good showcase of my issues when building side projects 😄 However, I think that's a reasonable call. To sum up the previous setup:

- Web app based on RSC, with barebones `@vitejs/plugin-rsc` setup
- Backend based on `Effect` `Cluster` and `Workflow` for maximizing statefulness usage and managing long-running parts of the system
- `TimescaleDB` as a database for performance and easy querying timeseries data, filling gaps, moving averages etc.

However, even in the [previous ADR](/development/adr/002-frontend-framework) I outlined that frontend is the most uncertain part. I was discussing the previous idea of using some sync-first approach for much better UX. While I decided that RSC is a fine tradeoff because they really spark joy for me, I'm going back on this. But let's dive deeper into this.

I was excited by various sync-first approaches for a long time, but I was a bit hesitant to dive deeper and use them. Partially because of the ecosystem landscape. What I initially dived into was `Replicache` which was really interesting, but 1) it had a not so simple setup and 2) was partially abandoned to build `Zero` by the same company, which I didn't fully enjoy and buy into the idea. For a long time, a lot of solutions in that space were floating around me, e.g. `Jazz`, `ElectricSQL`, `LiveStore`, `Dexie`, `Convex`. They're all interesting but none of them caught my attention enough to try and build something with it.

A lot changed, when I saw `TanStack DB` which is created in collaboration between `TanStack` umbrella and folks creating `ElectricSQL`. Previously, they've tried to go into direction of embedding `Postgres` directly in the browser with `PGLite` but now they've went all in `TanStack DB` which is even hard to describe. Their description is

> A reactive client store for building super fast apps

But it's so much more, a few things that are the most distinguishing imho.

- It's backed by IVM-like approach to querying normalized data. You fetch the state into the client-side, and treat UI like a materialized view over it.
- It's really flexible and allows multiple sources of data, `ElectricSQL`, `RxDB`, `TrailBase`, `TanStack Query` or even local storage/in-memory based ones.
- Optimistic updates and transactions are built-in concepts
- Offline persistence and paginated data sources are planned

All of its opinions are around how you store and query data in your UI, while the opinions about how it's fetched into the store are handled by `collection` concept.

For a long time I was looking into something that'd be enjoyable to build apps with similar set of trade-offs. So I've decided to take it for a ride in a smaller-scoped project. I've built [Bella](https://github.com/pawelblaszczyk5/bella/tree/main) which was a perfect experiment for me, because I tested a few things at the same time. I've decided to use `ElectricSQL` for the `collection`/`sync` provider and it was a blast. I had so much fun building it, because I could just focus on building user experience, instead of thinking about how data from backend gets into the frontend etc. Moreover, I didn't have to wire some deep framework-level stuff myself. That feeling made me sure that I enjoy building user experiences much more than building some technical marvels.

In that case RSC also doesn't really make sense, maybe in a perfect world and having some unlimited resources allowing to build tailored "framework" - it'd be the best choice. But that's not a reality. In Bella I've experimented again with `TanStack Start`, the experience is much more polished than before, they're moving away from a lot of stuff that I was hesitant about in the past. Moreover, they're the framework that's most focused on client-side stuff. I'm still not fully bought by some of their choices, but it seems like it's the best set of tradeoffs for this case.

At the same time, I've tested `Cluster`/`Workflow` setup, while it was really nice and enjoyable I realized how `Cluster` isn't a silver bullet. It fits a narrow niche, and solves it really, really well. I think that this project, especially with such approach to data fetching doesn't fit that niche. However, `Workflow` is excellent primitive for building long-running stuff and something that could be used later on here. I want to stick to just a simple `Effect` `HttpApi` for now, because it's both excellent primitive and easy to change into `Cluster`/`Workflow` if I have the need.

So we have two out of three existing ADRs trashed already, now it's time for the latest one. `TimescaleDB` made a lot of sense when most of the data fetching would be server side, and I'd have a lot of complicated queries. If I'm diving into client-side sync and there'll be close to none direct data fetching from web app it doesn't really make sense anymore. Plain `Postgres` is just enough, has a rich ecosystem, it's much more open and flexible. Moreover, that's exactly what `ElectricSQL` uses, what a coincidence 😄

## Decision

- `TanStack Start` with `TanStack DB` for client-side routing, rendering, fetching etc. Most of the app is a pure SPA-like experience but we have flexibility to SSR e.g. front page from the same app.
- `Effect` `HttpApi` based backend, with a potential to utilize `Workflow` in the future when in need of long-running jobs. It should have probably 99.9% of backend logic in here, that's one of the parts that I still need to fully crystalize.
- Plain `Postgres` for database, with `ElectricSQL` on top for syncing the state into the client (and maybe server 👀).

## Consequences

Happily I didn't implement too much in the current stack, but I need to start building finally. I think these choices will allow me to move faster, which I really need for this project. I need to finish it one day 😄

The main consequence is potential scaling in the far future. If the user creates a huge amount of data, syncing all of it into the client may no longer be practical. I’ll need to rethink some approaches if that happens. However, I’ve calculated the expected usage and consider this a reasonable tradeoff. If the app reaches that scale, I’ll be more than happy to find solutions to the issue. It'll be mostly used by myself anyway if I finish it at all 😅
