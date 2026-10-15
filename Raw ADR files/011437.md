# ADR 01: Disposable Prototypes

## Status

Accepted

## Context

In the spring of 2025, the Wikimedia Foundation product leadership formally
committed to a new plan around [Reader Investment][1]. Part of this plan included
the formation of a new Reader Growth team with a mandate to grow readership by
"developing new features, enhancing content discovery, evolving presentation of
content in new ways, exploring new technologies, and adapting to a changing
internet."

> To remain relevant and accessible in a changing digital landscape, we aim to
> invest in creating innovative experiences that leverage new technologies and
> formats. This includes tools and features that enable users to browse and
> discover content more intuitively, contextualize and frame knowledge in novel
> ways, and engage with visual, audio, and other multimedia formats that align
> with modern preferences. These efforts are critical for ensuring that the
> platform continues to attract and retain audiences by delivering value that
> adapts to the evolving expectations of knowledge seekers.

In order to carry out this mandate, the new Reader Growth team will be
conducting an ongoing series of experiments. The goal of these experiments is
to identify changes we can make to the Wikipedia reading experience that will
increase the retention of anonymous users. This will largely be done through
A/B testing of logged out users in production (sample rates may vary from 0.1%
to around 1% of logged-out traffic, depending on the Wiki in question).

The `ReaderExperiments` MediaWiki extension is the primary tool that the Reader
Growth team will use to conduct such experiments. This extension will house a
series of prototypes as the team investigates different features to help drive
reader retention on Wikimedia projects.

## Decision

In order to learn quickly and to avoid committing large amounts of resources to
ideas before they have been fully vetted, prototypes in the `ReaderExperiments`
codebase will be developed in a disposable fashion, and will leverage client-side
technology in the browser (as opposed to building new infrastructure on the
back-end) where possible. *No production-scale features will be housed in this
codebase.*

## Consequences

Building software that is meant to stand the test of time and serve
Wikipedia's massive and diverse user population requires a lot of time and
effort. By taking a disposable approach to prototyping, we can lower this cost
while we explore different ideas.

Wherever possible, we will strive to ensure that our disposable prototypes are
self-contained. One consequence of this is that we will likely rely
on client-side technology more heavily than is typical in WMF products: having
a larger JS payload is less of a concern for temporary features that only go
to a small subset of users, and we want to avoid building new back-end
infrastructure until we are sure we want to invest in a particular feature.

Most prototypes developed here will therefore have a ResourceLoader resource
module as their main entry point. Where necessary, we may also stand up "bespoke"
API endpoints to supply any prototype user intefaces with the data they need.
These APIs will either be private or marked as beta/unstable (not intended
for public consumption or re-use).

A typical prototype life-cycle will include the following stages:

* Development stage (locally or on Beta cluster, [Patchdemo][2], etc.)
* Experiment stage (may last a few weeks or months depending on how much data we need):
  the prototype is presented to a small subset of anonymous users as part of an
  A/B test (which is coordinated through [xLab][3]). Other users may be able to manually
  trigger the new feature where relevant by using a URL parameter; this functionality
  is intended to allow visibility and feedback from the community or from other Foundation
  staff.
* Prototype is decommissioned and data is analyzed.
* If the data indicates that the experiment yielded promising results, we may consider
  building a production version of the experimental feature. Any such feature should
  not live in the `ReaderExperiments` codebase (even if some prototype code ends up
  being re-used later on).



[1]: https://docs.google.com/document/d/1CdzSowVINSalHlhxzG50bHNHShaKivxpeommRnwxaho/edit?tab=t.0
[2]: https://toolhub.wikimedia.org/tools/patchdemo
[3]: https://wikitech.wikimedia.org/wiki/Experimentation_Lab
