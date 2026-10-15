# ADR-0030: Virus Scanning Tools

## Status

Accepted

Date of decision: 2025-05-16

## Context and Problem Statement

We need to ensure that all files uploaded to our system are scanned for viruses and malware. This is important for the
security of our users and the integrity of our system. Our main goals are ease of implementation and maintenance.

What tooling should we use to scan files for viruses?

## Considered Options

* ClamAV in a container on ECS
* GuardDuty Malware Protection for S3

## Decision Outcome

GuardDuty Malware Protection for S3 because it is a managed service that integrates with our existing AWS infrastructure
and provides real-time scanning of files as they are uploaded to S3. This will be faster to develop due to the
availability of recommended patterns from AWS, and it will be easier to maintain due to not having to manage things like
scaling, patching, and availability of the scanning service.

## Pros and Cons of the Options

### ClamAV in a container on ECS

ClamAV is an open-source antivirus engine that can be run in a containerised environment, such as AWS ECS.

* Neutral, because it is used on other MHCLG projects, but there mostly not on open source projects that we can re-use.
* Good, because it is open source and widely used.
* Good, because we could have full control over how and when it is triggered.
* Bad, because it requires more effort to set up, monitor, and maintain (e.g. patching, scaling, updating virus
  definitions).
* Bad, because we would need to build and maintain the container image, including any supporting code for responding to
  the results of the scan.
* Bad, because we would need to design and implement the supporting 'pipeline' i.e. code & infrastructure for the
  triggering mechanism for the scan, and handling the results of the scan.

### GuardDuty Malware Protection for S3

GuardDuty Malware Protection is an AWS managed service that scans files in S3 for malware.

* Good, because it is a fully managed service, we would not need to maintain it or worry about scaling, availability
  etc.
* Good, because it gives us the option of either reading tags or acting on the events it publishes to EventBridge.
* Good, because it should be faster to implement, with best practice patterns and examples available from AWS.
* Bad, because it may incur higher ongoing costs.
* Neutral, because we are not aware of other MHCLG/ Gov projects using it at present, as it is relatively new.


