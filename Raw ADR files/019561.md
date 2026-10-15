---
ID: umd-fcrepo-webapp-0002
Author: Peter Eichman <peichman@umd.edu>
Status: Accepted
Date: 2023-09-11

---
# Caching WebAC Lookups

## Context

Authorization checks of Fedora resources requested by a non-admin user
are taking too long and causing timeout errors. These are preventing
use of the interactive editing features of Archelon.

### Technical Background

This issue first appeared when upgrading Tomcat from 7.0 to 8.5. This
upgrade was necessitated by the lack of a Tomcat 7.x Docker image that
supported ARM architecture (at that time). However, it is unclear
whether it was the version of Tomcat that caused this error to appear,
if it was some other concomitant change (such as a change in the JDK
version), or if it was simply coincidental with now having resources
with many more pages.

Detailed logging of the authorization subsystem in fcrepo revealed that
a single request for the metadata of a resource resulted in 227 ACL
checks. Many of these resources were checked multiple times, ranging from
2 to 11 times.

## Decision

Implement a cache of ACL lookups, so that repeated lookups within the
same request can be processed more quickly.

- The cache will be implemented in the [fcrepo-module-auth-webac] module
- The cache should be short-lived, but long enough to support clusters
  of requests to the same or sibling resources (e.g., all pages in an
  item)
- The cache does not need to persist to disk

### Considered Cache Implementations

- [Caffeine]
- [Ehcache]

Caffeine was selected since it is already a dependency of the fcrepo
project.

## Consequences

- **Page load time is improved** from >2 minutes (the cause of the timeouts)
  to ~30 seconds for a load with an un-primed cache, and <1 second for
  further requests to that resource within the cache expiry period.
- **Incorrect ACL information could be returned** if an ACL is changed, or
  a resource is changed to be protected by a different ACL. However, both of
  these cases are infrequent enough to warrant the risk. Also, since the
  primary use case of the cache is for clusters of related requests, a
  short TTL should be sufficient.
- **Diverges from the fcrepo community implementation.** However, we already
  maintain our own forks of the [fcrepo4] and [fcrepo-module-auth-webac] code,
  so this additional feature does not add a significant maintenance burden.

[Caffeine]: https://github.com/ben-manes/caffeine
[Ehcache]: https://www.ehcache.org/
[fcrepo4]: https://github.com/umd-lib/fcrepo4
[fcrepo-module-auth-webac]: https://github.com/umd-lib/fcrepo-module-auth-webac
