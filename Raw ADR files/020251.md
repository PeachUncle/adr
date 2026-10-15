# ADR-100
# TSDR-100

## Status

Accepted

## Context

format the slog output for human readability.

## Decision

Keep our home brew from Wetesa-0. At some point will have to fix it and make
more robust. I think attribute overwrites are broken? will need those to hide
sensitive information.

## Why / Notes

I had the feeling that there were all these slog pretty handlers out there. There
is but most are one offs and not maintained. After looking them over the only one
that looked like it might work was devslog. But it has too much color and not
actually an improvement over what we have.

[Creating a pretty console logger using Go's slog package](https://dusted.codes/creating-a-pretty-console-logger-using-gos-slog-package)
is worth looking at if we go about fixing our handler.

## Links
- See ADR-011 Logging Package.
- [Awesome-Go: Logging](https://github.com/avelino/awesome-go?tab=readme-ov-file#logging)
- [Go Wiki: Resources for slog](https://go.dev/wiki/Resources-for-slog)
- [awesome-slog](https://github.com/go-slog/awesome-slog)
- **[slog-multi](https://github.com/samber/slog-multi)** - saving in case we want to log to multiple places down the road.
- [slogd](https://github.com/kaihendry/slogd) - slog with duration. with video https://youtu.be/IsPa11N5pzI

## Possible Options (short list)

- [devslog](https://github.com/golang-cz/devslog) - Format logs for development.
  - nice output. a bit too much color.
  - has some nice features like type flaging and only so many values in a slice.
  - does not output context attributes. would have to add that.
- [logging](https://github.com/dusted-go/logging)
  - [Creating a pretty console logger using Go's slog package](https://dusted.codes/creating-a-pretty-console-logger-using-gos-slog-package)
  - [prettylog](https://github.com/sytallax/prettylog)
- [slog-formatter](https://github.com/samber/slog-formatter) - Common formatters for slog + helpers for building your own
  - seems like a lot there. but not widely used?

## Other Possible Options

- [ConsoleHandler](https://gist.github.com/wijayaerick/de3de10c47a79d5310968ba5ff101a19) - similar to Zap’s ConsoleEncoder
  - very small code
- [console-slog](https://github.com/phsym/console-slog) - Handler that prints colorized logs, similar to zerolog's console writer output without sacrificing performances.
- [golog](https://github.com/primalskill/golog) - Development, discard and production handlers with sensible formatting.
  - OK output, someone really liked old school console green screens.
  - would have to add context attributes.
- [humane](https://github.com/telemachus/humane) - a human-friendly (but still largely structured) slog Handler
- [klog](https://github.com/kubernetes/klog) - the text format used by Kubernetes. Provides klog output routing when using the main package’s logger and a simpler logger that just writes to stderr. Both slog/logr and go-logr/logr APIs are supported.
- [slogcolor](https://github.com/MatusOllah/slogcolor) - Color handler for log/slog.
- [slogjson](https://github.com/veqryn/slog-json) - Format using the upcoming **JSON v2** library, with optional single-line pretty-printing: https://github.com/veqryn/slog-json
- [slogor](https://gitlab.com/greyxor/slogor) - A colorful slog handler

## Not an Option

- [logf](https://pkg.go.dev/github.com/AndrewHarrisSPU/logf) - (attr {key} interpolation, rich tty output):  (uses lazy Handler stores: https://go.dev/play/p/psdD7KDF5fp )
  - not maintained?
- [standard library slog: Writing a handler](https://pkg.go.dev/log/slog@go1.24.1#hdr-Writing_a_handler) - we don't need to write our own.
  - [slgotest](https://pkg.go.dev/testing/slogtest@go1.24.1)
- [slogpfx](https://github.com/dpotapov/slogpfx) - Easily prefix your log messages with attributes from the log record.
  - old, low buzz
- [slug](https://github.com/dotse/slug) - a handler that prints colourful logs for humans
  - not maintained
- [tinted](https://pkg.go.dev/github.com/lmittmann/tint) - colorized output
  - tried. our home brew is better.  
- [zlog](https://github.com/jeffry-luqman/zlog) - Handler that writes beautiful, human readable logs.
  - low buzz
- [zlog](https://github.com/icefed/zlog) - Human-friendly output like zap development, json structured logging with more features for slog.
  - low buzz  