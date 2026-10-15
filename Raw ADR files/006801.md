# ADR 1: Migration From LAMP to Serverless (AWS)
 
## Context
The current codebase and infrastructure of bahai-library.com has reached a critical limit that seriously endangers the future of the project.

BLO was built in 1997 in a traditional LAMP stack and architecturally upgraded up to 2010. It has not had any major changes or upgrades since, and runs on PHP 5.6, which will be unsupported by BLO's current hosting in November 2023.

The technologies and architecture BLO currently runs on are fragile in many ways, from massive security risks to maintainability barriers, with hard limits on application development and growth.

The nature of its architecture, specially at the data layer, means it cannot be simply modified (refactored) into a more maintainable codebase, or enhanced with modern features within its current form.

To make it maintainable and expandable it must either be rebuilt entirely, or eventually critically malfunction, be hacked, or both. This could happen in a few months or in a few years, and there is no way to predict it.

The current codebase was built in a necessarily ad-hoc way, meaning it's hard to understand without extensive familiarity with the ins and outs of its c.15,000 lines of code. It would take a senior developer 1-3 weeks of full time employment merely to understand the app well enough to begin to maintain it. This would be exacerbated in the absence of Baha'i context. Even with good familiarity, there is a high risk of side-effects from any code changes, a risk heightened if the developer is more junior.

This means that outside of Jonah Winters, its creator, it is currently very hard and/or very risky to onboard any new software maintainers, placing on Jonah the burden of being a single point of failure for the entire project.

Specifically, core issues include:

1) the current data structure in the database, which makes it hard to maintain and evolve, although you did an excellent job overall which will make the migration doable.
2) the tight coupling of this data layer and the view, because of how many pages are stored in the database. This makes it very hard to break free from both, the old database, and the old view.
3) 100,000+ URLs, which need to be preserved for the 141,000 backlinks 
4) a huge amount of archive metadata that also needs to be preserved
5) EOL PHP version, with associated security holes, along with other potential exploits linked to the database implementation

## Decision
Baha'i library will now be developed entirely in the Cloud (Serverless) harnessing the infrastructure, tools and services available in Amazon's AWS:
- decouple the static content from the data layer, mirroring the existing site in AWS object storage (S3), allowing the option for the site to be switched while work on a new data architecture, a public API, and/or a new frontend takes place
- migration and reconstruction will be iterative and staged, beginning with static layeras a potentially deployable increment, progressing to API specification, database architecture, and new view layer plus consumer applications 
- place data in S3 Intelligent-Tiering, so unvisited assets can be automatically moved into colder storage and highly visited ones remain on standard S3 for economic and environmental savings, as well as a tool for detecting and removing data noise from migration and bloat
- if there are gaps in the S3 mirror, revert to legacy BLO page, and create a script that will download the missing page and PUT it into the S3 bucket, so users themselves help us heal any data gaps.
- once the static mirror has been migrated and decoupled from both the existing PHP and MySQL, the work can begin to recreate the data architecture around a new Restful API, which can power a new view layer or multiple ones, as well as new applications beside the website
- in the small amount of "glue code" needed for serverless functions, use JavaScript for the largest pool of potential maintainers
- since legacy BLO is paid for for one more year, use it as failover backstop so any defects in the AWS migration will redirect to the legacy version, ensuring graceful failure and service continuity
- cost control measures will be implemented from the start including AWS budgets, anomaly detection, budget reports and absolute spending limits


## Status
Accepted

## Consequences
- rapidly and powerfully recreate and extend the current bahai-library.com functionality via AWS service orchestration (S3, Cloudfront, Route53, API Gateway, AWS Lambda, etc ) in ways that would be logistically prohibitive coding it from the ground up
- close all current security vulnerabilities
- remove technical constraints on maintenance, evolution and scalability
- remove accummulated bloat
- reduce running costs compared to current managed servers
- lower the BLO environmental footprint
- build on Amazon's state of the art, secure and infinitely scalable infrastructure
- transfer the core of maintenance work to Amazon, and concentrate our future software development effort on features unique to bahai-library.com
- make maintenance and expansion mostly language agnostic, to maximise the range of software developers who can volunteer or contract to help maintain it