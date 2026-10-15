    title:  use multiple code repositories for the accessnews.org project

    date:   2022-12-03 12:49
    status: accepted

## Context

[ADR "use volunteers.accessnews.org subdomain for volunteer coordination"](./20221203_103534-volunteers.accessnews.org_subdomain.md) only describes a representational separation (on the web level), but the content (comprising only static files at the moment) could be served from the same repo as web servers can be configured to serve different directories. (The abovementioned ADR already lists the consequence of having to use 2 web servers.)

However, [ADR "make static website using GitHub pages and Jekyll static site generator"](./20221203_103534-volunteers.accessnews.org_subdomain.md) makes this a hard requirement, because the only way to serve subdomains with [GitHub Pages](https://docs.github.com/en/pages) is to make a separate repository, and apply the subdomain in its settings.

## Decision

The content and code for the sub- and apex domains will be kept in different code repositories (namely, [`access-news.github.io`](https://github.com/access-news/access-news.github.io) and [`volunteers.accessnews.org`](TODO: add link)).

## Consequences

Pros:

+ Both the sub- and apex domains are planned to evolve past being static websites to become full-fledged web applications, and the technologies used may not necessarily be the same for both.

+ Clean separation of concerns.

Cons:

+ **Documentation complications** (-> necessary 3rd repo)

  `accessnews.org` is one project comprising 2 sub-projects at the moment, each of which should have its own documentation when they turn into web applications, but some decisions would affect all of them (including future sub-projects), and the top-level project should be documented somewhere too.

  Currently, [`access-news/_`](https://github.com/access-news/_) is the management repo of the `access-news` GitHub organization, and the top-level ADRs are stored there. (See [ADR "document architecture decisions"](./20221203_095536-document_architecture_decisions.md) about ADRs themselves.)

  TODO: Propose ADR about creating a docs subdomain and standalone repo. See more below.

+ **ADR fragmentation**

  As mentioned above, ADRs are kept in a 3rd repo right now, but as sub-projects become more involved, they will require their own architecture desicions that only pertains to them.

  The proposed docs ADR in the TODO above could be a solution by keeping **all** ADRs in one repo dedicated to documentation. Each ADR could be tagged to allow for filtering (e.g., to see ADRs for one project only, not-superseded ones). Either lose the textfile format, opting to store ADRs in a database (via a web app in the docs repo), or write a script to parse the ADRs (e.g., to build a dependency graph).

  Another possibility is to use a "distributed linked list" (probably not an accurate description) where each ADR is stored in the repo that it affects with chronological links leading back and forth (plus mentions, like in this ADR). Some of the downsides:
  + if the repos are not reachable, then the link breaks
  + no way to list the ADRs other than traversing the list - or keeping a central ledger; albeit, this approach could be combined with the database idea (but then, there would be a crawler to parse the links across repos, and it would be hard to guarantee consistency; basically all the problems that of a distributed project).

vim: set tabstop=2 shiftwidth=2 expandtab:
