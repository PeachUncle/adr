    title:  make static website using GitHub pages and Jekyll static site generator

    date:   2022-12-03 10:12
    status: accepted

    date:   2022-12-07 11:20
    status: implemented
    note: https://github.com/access-news/access-news.github.io/commit/b14b1528d6b6afeded7f2afd32ba82d198d999c7

## Context

The [Access News forum](https://forum.accessnews.org) has all the volunteer guides and instructions, but it is not utilized by volunteers at all, so it is simply using precious resources in vain. Hence, it will be decommissioned, and we'll start working on [accessnews.org](https://accessnews.org), the main site for Access News volunteers and subscribers, which will be the new home for the aforementioned documents.

Freeing up resources is important to save on costs, but the lack of time is always a limiting factor, and the new site should be brought up as quickly as possible.

## Decision

[accessnews.org](https://accessnews.org) will be a dynamic web application eventually, but it is more important to create a home for both volunteer and subscriber documents. These are simple formatted text files, therefore a **static website** will suffice for now.

We are going to use [GitHub Pages](https://docs.github.com/en/pages) to host it, and the number of pages is large enough to justify using a **static website generator**, which will be [Jekyll](https://jekyllrb.com/showcase/) in this case, as it is integrated with GitHub Pages so it should be a smooth ride.

## Consequences

Pros:

+ No need to deal with infrastructure (Linux VM, web server configuration, etc.).
+ Built in CI/CD (e.g., changes pushed to the repo will be published automatically).

Cons:

+ Dependence on the GitHub platform.

+ As mentioned in the "Decision" section, this is extra effort as we don't have time to start working on a web app, so this will all be replaced at one point.

+ Extra time to learn Jekyll.

+ The repository has to be named [`access-news.github.io`](https://github.com/access-news/access-news.github.io) instead of `accessnews.org`, because of the GitHub Pages conventions (see [this section](https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages#types-of-github-pages-sites)).


vim: set tabstop=2 shiftwidth=2 expandtab:
