<!-- cspell:words turbopack -->

# Frontend framework

**Date:** `24.07.2025`

**Status:** [`superseded by 4. Alternative architecture`](/development/adr/004-alternative-architecture)

## Context

Obviously I want to use `React` for this application. That's the best frontend framework for me and my usages. The documentation suggest that you should always use framework to create new applications. And in a principle I agree with this. However, there's kind of a weird moment in the framework space imho. And the most important thing to note at the beginning - RSC sparks joy af for me.

On one hand we've got `Next.js`, which in the "app router flavor" sometimes still feel a little bit beta. There're a lot of edge cases, issues, weird magic and patterns that still aren't polished. Moreover, it sometimes is a bit tied to Vercel in annoying fashion. Some stuff is undocumented and hard to deploy in a nice fashion in an environment outside (like Fly.io, that's changing in the future though). The `Webpack`/`Turbopack` is painful to work with and I much more believe in the ecosystem around `Vite`. That's a hard pill to swallow for me. Every single time when I use it I fall in love with RSC even deeper, but I also get to hate a lot of `Next.js` quirks even more.

There's also the `React Router`, renamed from `Remix`. The migration story didn't left me fully happy tbh. However, they feel the most unopinionated and flexible of all solutions. They support both SPA and SSR and now they also have SSG solution built-in. They let you use completely custom `http` server. They feel the least possessive `React` framework out of all. Their story around upgrades/new features (future/unstable flags) and support is one of the best. In theory they have an RSC API, but they're even more unstable and not yet ready for serious usage. And while all of their APIs felt really nice - that changed once I tasted RSCs 😄

The new kid on the block - `TanStack Start` is a really interesting case. I've bet on `TanStack Router` which is used under the hood a long time ago and I still think that was a good bet. The type safety is unmatched and now that they're stable and have file-based routing (which is actually recommended and solves a lot of pain points) they look like one of the best routing solutions for SPAs. However, I have a few hurdles with it - one thing is trying to be framework-agnostic which for many cases limits stuff you can do. But more importantly - `TanStack Start` the layer above the router itself is still not ready and feels very shake'y. I don't vibe with some of their choices and they put a lot of eggs into baskets that I don't worry about.

However, recently one thing that's popping out is low-level integration with RSCs like `Parcel` or `Vite` ones. They enable a lot of stuff and powerful usages, while obviously requiring higher buy-in and effort.

<!-- cspell:ignore replicache -->

One important concern - is RSC an optimal solution here? I'm not sure, that app could be potentially better by using something highly client-side heavy, like Replicache, TanStack DB, Zero, Jazz Tools etc. That's what I initially considered. However as noted in preface, I just like RSCs. I enjoy using them, I enjoy learning about them. It's all about enjoying it 😄

## Decision

Use `@vitejs/plugin-rsc` to basically build custom RSC framework. Start with really low-level and not fully optimal solution while building app. If it has at least some success and it outgrows the super basic API - improve it. Also since RSCs are really portable across frameworks - migrating to `React Router` when RSCs got more stable over there is always an option.

It'll also enable me to use advanced features like `Activity` or `"use cache"` in a sweet self-contained manner.

## Consequences

I'll spend time building some basic stuff I wouldn't have to do otherwise. It'll also make the app a little less sturdy at the beginning. I think that's a good balance here.
