# ADR-0028: Database Migrations

## Status

Accepted

Date of decision: 2025-03-21

## Context and Problem Statement

At the moment we run our migrations (and populate any seed data) every time the WebApp starts up a new instance. While this is suitable for our `integration` and `test` environment, we might (or might not) want a more granular level of control for our production environment. We will also want a way to reset or clean the databases in the lower environments.

## Considered Options

* Run migrations and seeding data on start up, with only manual cleaning of the database via the bastion host
* Run migrations and seeding data on start up, automatically cleaning the database each time
* Run migrations and seeding data on start up, with a Github Action to clean data in the database on demand
* Run migrations as a separate step in the deployment pipeline, seeding data on start up, with a Github Action to clean data in the database on demand

## Decision Outcome

Run migrations as a separate step in the deployment pipeline, seeding data on start up, with a Github Action to clean data in the database on demand, because while it requires a bit more work to set up, it separates out the concern of starting up the application and running the migrations, which could be useful in multiple different scenarios, including preventing concurrency issues. Also, being able to clean the database in lower environments in a controlled, predictable way gives us the right balance of being able to control when we clean the database without the inherent risks of doing so manually each time.

## Pros and Cons of the Options

### Run migrations and seeding data on start up, with only manual cleaning of the database via the bastion host

Continue with the current default - having the Spring app run all migrations and seed data from the relevant `data-*.sql` file. Require devs to manually connect to the database via the bastion host and run the `flywayClean` task if they need to clean down the data. 

* Good, because it requires no immediate extra development time.
* Bad, because we will have to handle concurrency issues if more than one instance starts up at once and tries to run the migrations.
* Bad, because manually connecting to the database via the bastion host with write access should be something that happens rarely and carefully, whereas it's likely that we'll want to clear data from lower env databases reasonably often.

### Run migrations and seeding data on start up, automatically cleaning the database each time

Continue with the current default - but also have the Spring app clean the database each time it deploys so that it always starts from a known state.

* Good, because it requires very little immediate extra development time.
* Bad, because it would mean needing to be careful that deployments do not interfere with ongoing QA or testing.
* Bad, because we will have to handle concurrency issues if more than one instance starts up at once and tries to run the migrations.

### Run migrations and seeding data on start up, with a Github Action to clean data in the database on demand

Continue with the current default - but also create a Github Action that can be run manually to clean the database on demand.

* Good, because it requires very little immediate extra development time.
* Good, because it would allow us to clean the database as required in a safe and trackable way, with a record that the Action was run and when remaining on Github.
* Bad, because we will have to handle concurrency issues if more than one instance starts up at once and tries to run the migrations.

### Run migrations as a separate step in the deployment pipeline, seeding data on start up, with a Github Action to clean data in the database on demand

Add an extra step, likely as a separate callable action, in our pipeline that runs database migrations after an application has been deployed - and also create a Github Action that can be run manually to clean the database on demand.

* Neutral, because it requires some extra development time in the short term.
* Good, because it would allow us to clean the database as required in a safe and trackable way, with a record that the Action was run and when remaining on Github.
* Good, because we know the migrations will run once per deployment even if we are starting up multiple instances.

