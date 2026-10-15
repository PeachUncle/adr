# Adopt Peewee as ORM for SPLit MVP

- **Status:** accepted  
- Date: 2025-05-27
- **Tags:** orm, peewee, python, mvp-scope, simplification

## Context

Early architecture drafts for SPLit assumed SQLAlchemy as the ORM layer. While powerful, SQLAlchemy introduces considerable boilerplate (declarative base, session and transaction management, migration tooling) and a steeper learning curve—overkill for a single-developer MVP. The goals for our first iteration are:

- **Minimal setup** and faster onboarding  
- **Clear separation** of business logic and data access  
- **Easy future replacement** of the ORM if requirements evolve  

Peewee provides a lightweight, expressive API with out-of-the-box MySQL support, native JSON fields, and straightforward multiple-database connections. It aligns perfectly with our MVP constraints and can be swapped out later by rewriting only the `models/` and `data_access/` layers.

## Decision

We will adopt **Peewee** as the ORM for the SPLit MVP. All ORM-related code will live under `src/orm/` with this structure:

```
src/
└── orm/
    ├── models/                
    │   ├── base.py            ← Database connections & BaseModel
    │   ├── logs.py            ← split_logs.logs
    │   ├── events_log.py      ← split_events.events_log
    │   ├── users.py           ← split_users.users
    │   ├── portfolios.py      ← split_portfolios.portfolios
    │   ├── portfolio_items.py ← split_portfolios.portfolio_items
    │   ├── portfolio_history.py ← split_portfolios.portfolio_history
    │   ├── initial_filtration.py  ← split_math_core.initial_filtration
    │   └── final_selections.py    ← split_math_core.final_selections
    │
    ├── data_access/           
    │   ├── logs_dao.py
    │   ├── events_dao.py
    │   ├── users_dao.py
    │   ├── portfolios_dao.py
    │   ├── portfolio_items_dao.py
    │   ├── portfolio_history_dao.py
    │   ├── initial_filtration_dao.py
    │   └── final_selections_dao.py
    │
    └── users_interaction/      
        └── backend/
            └── portfolio_mngr/
                └── logic.py   ← imports only DAO functions
```

In `models/base.py` we configure five MySQL connections:

```python
from peewee import MySQLDatabase, Model

DB_PARAMS = { 'host': '…', 'user': '…', 'password': '…' }

split_logs_db        = MySQLDatabase('split_logs',        **DB_PARAMS)
split_events_db      = MySQLDatabase('split_events',      **DB_PARAMS)
split_users_db       = MySQLDatabase('split_users',       **DB_PARAMS)
split_portfolios_db  = MySQLDatabase('split_portfolios',  **DB_PARAMS)
split_math_core_db   = MySQLDatabase('split_math_core',   **DB_PARAMS)

class BaseModel(Model):
    class Meta:
        database = None  # overridden in each model
```

We will implement Peewee **models** for all tables, DAO modules exposing typed functions for each model, and ensure business logic imports only DAO functions. Table creation is automated via `database.create_tables([...])`. Unit tests will cover DAO methods, and integration tests will run against a test MySQL instance.

## Consequences

✅ Rapid development with minimal boilerplate  
✅ Strong separation between business logic and data access  
✅ Straightforward future migration to SQLAlchemy or another ORM by rewriting only `models/` and `data_access/`  

⚠️ Peewee’s query DSL is less feature-rich than SQLAlchemy’s, and its community and ecosystem are smaller  
