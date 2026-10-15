# Initial Module Set for the MVP

- Status: accepted
- Date: 2025-05-28
- Tags: MVP, Core Modules, Task Orchestration, Redis, Celery, Event Logging, Stock Screening, Financial Analytics

## Context

To kick off the MVP of the SPLit application, we have identified a minimal set of modules that deliver critical functionality and support an end-to-end user journey. First, the web UI will render a fixed list of ten equity tickers; second, the system will offer rudimentary final recommendations—Buy, Hold or Sell—to simulate a basic stock screener. This ADR outlines which modules should be prioritised for implementation, their minimal capabilities, and the causal pipeline linking them.

## Decision

### Objectives
- Provide basic operation tracing (logging and event capture).
- Establish a simple user management mechanism (initially with a single user, **user_zero**).
- Offer a web interface for portfolio display.
- Allow basic portfolio control via a “Refresh Data” button.
- Implement minimal task routing between modules.
- Fetch market quotes and fundamental data from an external source.
- Perform initial stock filtering by key metrics and fundamental indicators.
- Generate final recommendations based on the filtering results.

### Workflow (MVP Scenario)
1. WebUI displays ten fixed equity tickers and a “Refresh Data” button.
2. On button click, WebUI calls **portfolioMngr** directly (synchronous API).
3. **portfolioMngr** enqueues a “refresh” task via Redis + Celery and subscribes to its status; statuses are recorded in **eventSrv**.
4. **dataOrchestrator** dequeues the refresh task, then sequentially enqueues tasks for **yahooAPIGateway**, **initlFilter**, and **finalSel**, subscribing to each completion; each module writes results to its own database table and emits completion via Redis + Celery.
5. Upon finalSel completion, **portfolioMngr** pulls updated data from the respective databases and notifies WebUI that data are up to date.
6. WebUI renders the refreshed data for the user.

### Infrastructure
- MySQL (already deployed)
- Peewee as the ORM layer
- Redis + Celery for task queuing and orchestration
- **Persistence & Reliability**:
  - **eventSrv** serves as a durable, secondary journal of task metadata (timestamps, statuses, initiators/executors) in `split_events.events_log`.
  - In the normal scenario, modules communicate via in-memory Redis + Celery queues and rely on DB writes; **eventSrv** is consulted only for audit or in failure-recovery paths.

### Proposed Solution
Implement the following modules in order of priority:

1. **logSrv** (Logger Service)
   - **Minimal functionality**: record all key operations and errors to a file and the `split_logs` database.
   - **Rationale**: essential for debugging.

2. **eventSrv** (Event Service)
   - **Minimal functionality**: persist metadata of completed tasks—timestamps for creation and completion, task status, initiator, and executor—to the `split_events.events_log` table.
   - **Rationale**: maintains an audit trail of task executions for later analysis.

3. **userMgmt** (User Management Service)
   - **Minimal functionality**: manage a user database containing a single **user_zero** account.
   - **Rationale**: lays the groundwork for a multi-user system in future iterations.

4. **webUI** (Web Interface)
   - **Minimal functionality**: display a fixed set of ten equity tickers traded on NYSE/NASDAQ.
   - **Rationale**: serves as the primary entry point for users, showcasing the outputs of backend modules.

5. **portfolioMngr** (Portfolio Management)
   - **Minimal functionality**: maintain a fixed list of tickers for the user’s portfolio.
   - **Rationale**: provide a single, reliable source of portfolio data for analysis.

6. **dataOrchestrator** (Data Orchestrator)
   - **Minimal functionality**: accept tasks from **portfolioMngr**, route requests to **yahooAPIGateway**, **initlFilter**, and **finalSel**, and log statuses to **eventSrv**, all orchestrated via Redis + Celery queues.
   - **Rationale**: ensures asynchronous, scalable, and ordered execution of analysis steps.

7. **yahooAPIGateway** (Yahoo Finance API Gateway)
   - **Minimal functionality**: retrieve time series of market prices and fundamental indicators (P/E, ROE, Debt/Equity, etc.) for a list of tickers.
   - **Rationale**: provides primary data for statistical analysis.

8. **initlFilter** (Initial Stock Filtering)
   - **Minimal functionality**: filter tickers using fundamental indicators (liquidity, leverage, profitability) and assign quantitative scores.
   - **Rationale**: the first analytical step, flagging the most and least suitable stocks.

9. **finalSel** (Final Selection)
   - **Minimal functionality**: generate “Buy/Hold/Sell” recommendations based on **initlFilter** results.
   - **Rationale**: completes the MVP analytics cycle and delivers the end result to the user.


## Consequences

- ✅ Clear separation of responsibilities across modules.
- ✅ A minimal, end-to-end workflow from web UI display of tickers to recommendation output, based on up-to-date data.
- ✅ Flexible architecture, ready to incorporate advanced features of modules implemented first, as well as new modules in future iterations.
- ✅ Supports future audit and compliance requirements.

## Links

[Adopt Peewee as ORM for SPLit MVP](20250527-adopt-peewee-as-orm-for-split-mvp.md)
