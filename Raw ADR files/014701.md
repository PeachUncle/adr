# ADR-0022: Disaster recovery

## Status

Accepted

Date of decision: 2024 Q4

## Context and Problem Statement

A catastrophic infrastructure failure can make the application unavailable, and lead to data loss. Our disaster recovery
strategy will determine how long that downtime is likely to be in different scenarios, and how much data would be lost.
This is roughly equivalent to our Recovery Time Objective (RTO) and Recovery Point Objective (RPO) respectively.

Our underlying assumption is that the application can tolerate a small amount of downtime, as it is not critical
infrastructure, but this should be avoided if possible, and that data loss is more critical given the legal requirement
on landlords to register their data.

## Considered Options

* Single availability zone deployment for application and data
* Single availability zone deployment for application, data backed up to a second availability zone
* Single availability zone deployment for application, data backed up to a different availability zone and also a
  different region (and AWS account)
* Multi-availability zone deployment for application and data
* Multi-availability zone deployment for application and data, data backed up to a different region (and AWS account)

## Decision Outcome

Multi-availability zone deployment for application, data backed up to a different availability zone and also a different
region (and AWS account) - this option:

- is AWS best practice (indeed, AWS makes it difficult to not deploy to multiple AZs if a load balancer is present)
- represents the equal best RPO and RTO of the various options,
- does not cost significantly more than replicating data-only across multiple AZs, which is required for an acceptable
  RPO

## Pros and Cons of the Options

### Single availability zone deployment for application and data

Both the web application and the RDS database would be deployed to single instances in one availability zone

* Good because it would be the lowest cost option
* Bad because in the case of a single availability zone failure the service would become unavailable until either the
  issue was resolved or the service was manually redeployed to a different availability zone
* Bad because in the case of a single availability zone failure all data since the last RDS backup log event would be
  lost (up to
  5 mins of data typically)
* Bad because in the case of catastrophic data loss in the availability zone all data for the database would be lost
* Bad because in the case of catastrophic data loss in a region or the AWS account being compromised all data for the
  database would be lost or compromised

### Single availability zone deployment for application, data backed up to a second availability zone

The web application would be deployed to a single availability zone, the RDS database would have a primary instance in
the same availability zone, and a passive stand-by instance in a second availability zone with data synchronised to it

* Neutral, because it is a medium cost option
* Bad because in the case of a single availability zone failure the service would become unavailable until either the
  issue was resolved or the service was manually redeployed to a different availability zone
* Good because in the case of a single availability zone failure or catastrophic data loss in the availability zone
  almost all data (< 1 min potential loss) would be preserved in the second availability zone
* Bad because in the case of catastrophic data loss in a region or the AWS account being compromised all data for the
  database would be lost or compromised

### Single availability zone deployment for application, data backed up to a different availability zone and also a different region (and AWS account)

The web application would be deployed to a single availability zone, the RDS database would have a primary instance in
the same availability zone, and a passive stand-by instance in a second availability zone with data synchronised to it.
Backups would also be replicated to another AWS account and stored in a different region

* Neutral, because it is a medium cost option
* Bad because in the case of a single availability zone failure the service would become unavailable until either the
  issue was resolved or the service was manually redeployed to a different availability zone
* Good because in the case of a single availability zone failure or catastrophic data loss in the availability zone
  almost all data (< 1 min potential loss) would be preserved in the second availability zone
* Good because in the case of catastrophic data loss in a region or the AWS account being compromised the vast majority
  of the data (from the most recent transaction logs) will be preserved in another region

### Multi-availability zone deployment for application and data

The web application would be deployed to 2 or more availability zones, the RDS database would have a primary instance in
the one availability zone, and two active read replicas in 2 other availability zones in an RDS cluster

* Bad, because it is a higher cost option, when we can likely tolerate a reasonable amount of downtime
* Good because in the case of a single availability zone failure the service would continue to be available
* Good because in the case of a single availability zone failure or catastrophic data loss in the availability zone
  almost all data (< 1 min potential loss) would be preserved in the second availability zone
* Bad because in the case of catastrophic data loss in a region or the AWS account being compromised all data for the
  database would be lost or compromised

### Multi-availability zone deployment for application and data, data backed up to a different region (and AWS account)

The web application would be deployed to 2 or more availability zones, the RDS database would have a primary instance in
the one availability zone, and two active read replicas in 2 other availability zones in an RDS cluster.
Backups would also be replicated to another AWS account and stored in a different region

* Bad, because it is a higher cost option, when we can likely tolerate a reasonable amount of downtime
* Good because in the case of a single availability zone failure the service would continue to be available
* Good because in the case of a single availability zone failure or catastrophic data loss in the availability zone
  almost all data (< 1 min potential loss) would be preserved in the second availability zone
* Good because in the case of catastrophic data loss in a region or the AWS account being compromised the vast majority
  of the data (from the most recent transaction logs) will be preserved in another region

