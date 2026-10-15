# 14. Log level usage

Date: 2024-02-15

## Status

2024-02-15 accepted

## Context

It's not always clear what information should be logged at which level. While it might never be possible to definitely tell the log level to use for every log line, a set of guidelines will be helpful to reach a common understanding how each level is meant to be used.

## Decision

There are 6 log levels that we should use that are supported by our logger - fatal, error, warning, info, debug and trace. We should stick to using those and avoid defining custom levels.

The main guideline for using a given log level should be a severity of what's happening, judged by when a developer should be notified about a given situation, even if no actual notification system is set in place.

- Fatal level should be used if application encountered an unrecoverable problem and has to exit. Developers should be notified immediately about such errors, and it should be treated as a showstopper.
- Error level should be used if application encountered a recoverable problem. Developers should be notified immediately about such errors.
- Warning level should be used if application encountered a recoverable problem of a lesser severity or an unusual situation. Developers should be notified once every few days about summary of warnings that have happened, unless there's a sharp increase in their number.
- Info level should be used for any information that can help with reasoning application behavior. Those logs should be available for developers on demand via a log storage system.
- Debug level should be used for more detailed and less important information. By default, they are enabled on pre-production environments and disabled on production.
- Trace level should be used for very detailed information, needed for complex debugging, that can also introduce a lot of clutter in logs. By default, they are disabled on all environments.

We should aim for a 0 error policy. All problems that are logged at this level should be urgently taken care of. If a problem that is happening doesn't require an urgent developer attention, it shouldn't be logged as an error, but as a warning or info. It is important to remember, that even if a log line is added to a try-catch block, it doesn't automatically mean it should be logged as error.

We should aim to have as few warning as possible and reduce their number over time. If a problem that is logged as a warning happens very frequently during a normal system usage, and it's impossible to reduce it by improving code quality or other means, it should likely be logged as info.

## Consequences

With this guideline in place, it should be more clear which log level should be used in a given situation. Using development urgency as a guiding principle, should also mean that things that are logged as errors will actually be noticed earlier and taken more seriously. There is a risk that with this approach, we will have some actualy urgent problems being logged with lower level. However, I see that as less of a problem, than having too many things being logged as errors, which often ends with people not treating all errors seriously.
