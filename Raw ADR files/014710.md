# ADR-0031: Handling virus scan results

## Status

Accepted

Date of decision: 2025-06-03

## Context and Problem Statement

When a file has been scanned we need to trigger appropriate actions based on the scan results. These include:

- Moving the file from the quarantine bucket to the appropriate destination bucket if it is safe.
- Deleting the file if it is not safe.
- Notifying the user of the outcome of the scan.
- Updating the database with the key of the file if it is safe.

GuardDuty can both tag the S3 object and trigger an EventBridge event with the result of the scan.

How should we handle the results of the virus scan?

## Considered Options

* Lazily read the tag on the S3 Object
* Background process on WebApp polling S3 to check tags
* EventBridge event -> ephemeral ECS task (our scheduled tasks approach)

Note: For the EventBridge option, the event can either directly trigger the action, or it can be added as a message to
an SQS queue which is then processed asynchronously.

## Decision Outcome

EventBridge event -> ephemeral ECS task, because it will not block users, requires less temporary code that will be
discarded after the pilot, and while it requires additional infrastructure, this is infrastructure we would have needed
post-pilot in any case.

## Pros and Cons of the Options

### Lazily read the tag on the S3 Object

The scan results would only be read when the WebApp attempts to access the file. To ensure the user is notified of the
results of the scan in a timely manner they would be prevented from completing the compliance journey until the scan
results have been obtained (with progressive enhancement for those with javascript to show a loading spinner).

On reading the tag, if the file is safe it would be moved to the appropriate destination bucket and the database
updated, else the file would be deleted and the user emailed as well as being notified on the loading page.

* Good, because it is the simplest solution to implement.
* Good, because it does not require us to implement infrastructure for asynchronous processing.
* Bad, because we would need additional logic to handle the loading state in the WebApp.
* Bad, because it would delay the user in the compliance journey until the scan results are available, when in the vast
  majority of cases the file will be safe.
* Bad, because if the user closes the browser before the scan results are available, they will not be notified of the
  outcome of the scan.
* Bad, because we would likely replace this with an asynchronous solution in the future, so it would be temporary.

### Background process on WebApp polling S3 to check tags

This option would involve the WebApp having a background process that periodically checks the S3 objects in the
quarantine bucket for the scan result tags and then takes the appropriate action when the tag is detected.

* Good, because it would not require us to implement infrastructure for asynchronous processing.
* Good, because it would be relatively simple to implement.
* Bad, because if there were a large number of files being scanned, processing the results could cause performance
  issues in the WebApp.
* Bad, because we would likely replace this with an asynchronous solution in the future, so it would be temporary.

### EventBridge event -> ephemeral ECS task

This option would involve GuardDuty triggering an EventBridge event when the scan results are available, which would
then trigger an ephemeral ECS task to process the results. The ECS task would be a clone of the WebApp codebase, but
without a webserver running. The trigger could either be the event itself or an SQS queue that the ECS task listens to.

* Good, because it would allow us to process the results asynchronously without blocking the user.
* Good, because it would allow us to scale the processing of the results independently of the WebApp.
* Good, because it would allow us to handle a large number of files being scanned without impacting the WebApp
  performance.
* Neutral, because it would require us to implement infrastructure for asynchronous processing, which we would not
  otherwise be doing for the pilot, but which we would be implementing later.
* Bad, because it could result in a large number of ECS tasks being created if there are a large number of files being
  scanned, which could lead to increased costs (although, ignoring malicious usage, there should not be high volumes of
  files uploaded during pilot).


