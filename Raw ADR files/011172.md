# ADR 003: Choosing Celery for notification management in scheduled visits and payment receipts

**Date:** 2024-10-07

## Context

In the `visits` and `payments` microservices, we need to implement asynchronous notification handling. For the `visits` microservice, this involves sending email reminders about scheduled visits. These notifications should be sent a day before each visit to the respective users (patients). In the `payments` microservice, emails with receipts for visits need to be sent to users after successful payments.

Due to the potentially large volume of operations in both microservices, we require a solution that allows for asynchronous task processing and scalability. These operations are time-consuming and should not block the system from handling other requests.

### Requirements:

- Asynchronous task handling.
- Task scheduling (notifications in the `visits` microservice must be sent at a specific time).
- Scalability to accommodate varying numbers of users and operations.

## Options

1. **Celery**
   - **Pros:**
     - Mature and stable library for asynchronous task processing.
     - Built-in support for task scheduling (e.g., via Celery Beat).
     - Well-integrated with Django and other technologies used in the project.
     - Supports scalability by allowing multiple workers to be run.
     - Compatible with various message brokers (RabbitMQ, Redis).
   - **Cons:**
     - Requires additional infrastructure (message broker and optional result backend).
     - May be overly complex for simpler use cases.

## Decision

We decided to use **Celery** for handling notifications in the `visits` and `payments` microservices because it offers the best capabilities for asynchronous task processing and scheduling. Its scalability and integration with our Django framework will allow us to extend notification functionalities easily in the future.

Celery, combined with Redis as the message broker, meets our needs for efficiently and reliably handling a large number of notifications.

## Consequences

1. **Infrastructure:** We need to deploy additional infrastructure components such as a message broker (Redis) and Celery Beat for task scheduling in the `visits` microservice.
2. **Maintenance:** Configuring and maintaining Celery and the message brokers require additional administrative resources.
3. **Scalability:** In the future, we can easily scale the solution by running more Celery workers to handle increased user, visit, or payment volumes.
4. **Costs:** Using Celery with a message broker may generate additional operational costs for infrastructure maintenance, but these costs will remain lower than using cloud-based options like AWS Lambda.

## Summary

Celery provides the flexibility and scalability needed for managing notifications, which is critical for the efficient operation of the `visits` and `payments` microservices in the long term.

