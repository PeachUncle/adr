# ADR-0032: Web Analytics

## Status

Draft

Date of decision: {yyyy-MM-dd}

## Context and Problem Statement

To support understanding of the use of our service, we would like large scale, automated insight into our users'
behaviour when using the web app - i.e. we need some web analytics.

The exact metrics we will want to track are still TBC, but likely to include:
- Number of visits / unique visitors (to some approximation) to each page
- Entry and exit pages for each visitor
- Dwell time per page
- Response times / a similar performance metric

Where will we get that data, and how will we analyse it?

## Considered Options

* Google Analytics 4
* Plausible Analytics
* CloudFront access logs + analyser

## Decision Outcome

{Title of Option X}, because {summary justification / rationale}.

## Pros and Cons of the Options

### Google Analytics 4

Google Analytics 4 (GA4) is the latest iteration of Google's web analytics tool. It is, by default, more privacy-friendly
than previous versions - for example, out of the box, it does not log IPs. It includes a 'tag' for tracking web behaviour
(page views, user engagement, various actions such as scrolling and file downloads) and a web UI for analysis of data. It
is a complex and highly configurable tool. Further analysis can be performed via data exports through BigQuery.

* Good, because it is widely used - globally, within UK gov (e.g. gov.uk published content), and within MHCLG (e.g.
  elections services, EPB, Funding Service).
* Good, because it should be simple to get legal / data protection approval (as it is common).
* Good, because it captures the data we will likely need.
* Good, because it quite aggressively deduplicates people when calculating 'unique' visitors.
* Good, because it is free.
* Neutral, because it requires careful configuration (which requires expertise to set up and maintain).
* Bad, because it uses non-essential cookies, and therefore requires a cookie consent banner to be shown.
* Bad, because users frequently reject cookie banners and use ad blockers, reducing the amount of data we collect
  (Register to Vote measured GA opt-in rates to be around 33%).
* Neutral, because it is a US-based tool, but can be configured to store and process data in the EU.
* Neutral, because it requires us to trust a 3rd party script, but from a reputable source.

### Plausible Analytics

Plausible Analytics is privacy-focused, lightweight alternative to Google Analytics. There are a number of similar
alternatives (such as Simple Analytics, and Matomo); Plausible has been chosen as the most appropriate option within
that group.

* Neutral, because it is not widely used, but has been used in MHCLG before (on CORE).
* Neutral, because there is a _risk_ of delay (e.g. if we need legal / data protection approval) - although it is
  already on the Cyber assured list, and does not require TDA sign-off.
* Bad, because it does not capture performance metrics (e.g. response times), so we'd need to source that data elsewhere
  (e.g. Treo, or rely on server-side timings).
* Neutral, because it's deduplication of 'unique' visitors is weak (based on IP, persisting only for 24 hours).
* Bad, because it is costly (£2.5k+ / year for 5M page views per month).
* Good, because it is (relatively) simple.
* Good, because it does not use cookies (or fingerprinting, etc) - this should mean we can avoid a cookie banner.
* Good, because data never leaves the EU.
* Neutral, because it requires us to trust a 3rd party script, but one that is open source and auditable (at least at a
  given point in time).

### CloudFront access logs + analyser

Our web traffic is routed through CloudFront, AWS's CDN. This can be configured to store access logs (most notably in
S3 or CloudWatch Logs). Downstream tools can then be used to analyse those logs - e.g. AWS Athena and QuickSight, or
specialist software.

* Neutral, because this technique is occasionally used (e.g. EPB make use of CloudFront log data).
* Bad, because it only captures minimal data (e.g. requested URLs, server-side response times; no user-level tracking).
* Bad, because it incurs cost (through use of additional AWS services).
* Good, because it is simple.
* Good, because it does not use cookies (or fingerprinting, etc).
* Good, because data would remain in the UK.
* Good, because no Javascript is required.

## More Information

* [Information on GA4 in the EU](https://support.google.com/analytics/answer/12017362?hl=en)
* [Plausible's privacy focus and EU hosting](https://plausible.io/privacy-focused-web-analytics#hosted-in-the-eu-powered-by-european-owned-cloud-infrastructure)
* [Plausible's unique visitor counting](https://plausible.io/data-policy#how-we-count-unique-users-without-cookies)
* [CloudFront logging configuration](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/standard-logging.html)