# ADR 0001: Layered (Ports & Adapters) Architecture with a Multi-Crate Workspace

* **Status**: In Review
* **Date**: 2025-07-26

## Contents

1.  [Context](#1-context)
2.  [Considered Alternatives](#2-considered-alternatives)
    - [Alternative 1: Simple Monolithic Structure](#alternative-1-simple-monolithic-structure)
    - [Alternative 2: Component-Based (Vertical Slice) Architecture](#alternative-2-component-based-vertical-slice-architecture)
3.  [Decision](#3-decision)
4.  [Directory Structure](#4-directory-structure)
5.  [Layer Breakdown & Code Walkthrough (using Actix-Web)](#5-layer-breakdown--code-walkthrough-using-actix-web)
    - [Layer 3: `domain` (The Core)](#layer-3-domain-the-core)
    - [Layer 2: `application` (Business Logic)](#layer-2-application-business-logic)
    - [Layer 4: `infrastructure` (Implementation Details)](#layer-4-infrastructure-implementation-details)
    - [Layer 1: `api` & `serialization` (Entry Points)](#layer-1-api--serialization-entry-points)
6.  [Consequences](#6-consequences)
    - [Positive](#positive)
    - [Negative](#negative)

---

## 1. Context

This project is a comprehensive, open-source Identity and Access Management (IAM) system. Due to its intended scale and collaborative nature, the architecture must prioritize several key qualities:

* **Maintainability**: The system must be easy to understand and modify without causing unintended side effects.
* **Testability**: Core business logic must be verifiable in isolation, independent of external factors like databases or web frameworks.
* **Scalability & Concurrency**: The structure must support a growing feature set and allow a community of contributors to work on different parts of the system simultaneously without conflict.
* **Flexibility**: The architecture must allow for the evolution of technology, such as swapping out the database or web framework, with minimal impact on the core application.

A decision on the primary architectural pattern is required before significant development begins to ensure these goals are met from the outset.

---

## 2. Considered Alternatives

### Alternative 1: Simple Monolithic Structure

* **Description**: All application code (web handlers, business logic, database models, and queries) would reside within a single Rust crate and a flat module structure (e.g., `src/models.rs`, `src/handlers.rs`, `src/services.rs`).
* **Pros**:
    * Fastest to set up for small projects and prototypes.
    * Lower initial complexity and less boilerplate.
* **Cons**:
    * **High Coupling**: Leads to an inseparable where web logic becomes entangled with database logic.
    * **Poor Testability**: It is extremely difficult to test business logic without instantiating the entire application, including a real database connection.
    * **Low Maintainability**: A small change in one area can have cascading and unpredictable effects on others. This is unacceptable for a large-scale project.
* **Rationale for Rejection**: This approach does not meet our core requirements for maintainability and testability and would quickly become unmanageable.

### Alternative 2: Component-Based (Vertical Slice) Architecture

* **Description**: Code is structured by feature or component. For example, all code related to user management would live in a `user/` directory, containing `user/models.rs`, `user/service.rs`, `user/api.rs`, etc.
* **Pros**:
    * **High Cohesion**: All code for a single feature is located in one place, which can be intuitive for developers working on that feature.
    * **Team Ownership**: Potentially easier to assign feature "ownership" to different teams.
* **Cons**:
    * **High Risk of Architectural Decay**: The boundaries between layers (service, database, API) within a component are based on convention, not compiler enforcement. It is very easy for a developer to accidentally call database code directly from an API handler within the same component, violating the architecture.
    * **Difficult to Manage Cross-Cutting Concerns**: Shared logic like authentication middleware, transaction management, and logging does not fit neatly into a single vertical slice and often ends up in a messy `common` or `shared` module, breaking the encapsulation model.
* **Rationale for Rejection**: While appealing for its cohesion, the lack of compiler-enforced boundaries presents too great a risk of architectural decay for a long-term, collaborative project. The chosen alternative provides stronger guarantees.

---

## 3. Decision

We will adopt a **Layered Architecture**, also known as **Ports and Adapters** or **Hexagonal Architecture**. This pattern will be strictly enforced using a **Rust workspace with multiple distinct crates**, where each crate represents a layer with a single, well-defined responsibility.

The fundamental rule of this architecture is the **Inward Dependency Rule**: dependencies must always point towards the center of the application (`domain`). The outer layers depend on abstractions (Rust traits) defined in the inner layers, never the other way around. This is enforced by the Rust compiler, preventing accidental violations.

This approach was chosen because it provides the best balance of separation of concerns, testability, and long-term maintainability, directly addressing the core requirements outlined in the context.

---

## 4. Directory Structure

The following structure will be used to enforce these architectural boundaries at the file system and compiler level.

```plaintext
.
├── docs/
│   └── ADR/
│       └── 0001-layered-architecture.md  # This document
├── services/
│   ├── backend/              # Rust Workspace for all backend logic
│   │   ├── Cargo.toml        # Defines the workspace members
│   │   ├── crates/
│   │   │   ├── api           # Layer 1: Web (Binary Crate)
│   │   │   ├── application   # Layer 2: Business Logic/Use Cases (Library)
│   │   │   └── common        # Common utilities and shared code
│   │   │   ├── domain        # Layer 3: Core Entities & Rules (Library)
│   │   │   ├── infrastructure# Layer 4: DB, External APIs (Library)
│   │   │   └── serialization # DTOs and mapping logic (Library)
│   │   ├── migrations/       # SQL migration files for sqlx-cli
│   │   └── tests/            # End-to-end integration tests
...
```

---

## 5. Layer Breakdown & Code Walkthrough (using Actix-Web)

This section details each layer's responsibility, illustrated with a complete user registration feature.

### **Layer 3: `domain` (The Core)**

Contains pure business entities and rules. It has zero external dependencies.

* **Example: `crates/domain/src/user.rs`**
    ```rust
    use uuid::Uuid;
    // Pure business entity.
    pub struct User {
        pub id: Uuid,
        pub email: String,
    }
    ```

### **Layer 2: `application` (Business Logic)**

Contains the application's use cases and orchestrates the domain entities. It defines interfaces (**Ports**) for external dependencies.

* **Example Port: `crates/application/src/repositories.rs`**
    ```rust
    use anyhow::Result;
    use async_trait::async_trait;
    use crate::domain::user::User;
    // The "Port" defining a contract for persistence.
    #[async_trait]
    pub trait UserRepository: Send + Sync {
        async fn find_by_email(&self, email: &str) -> Result<Option<User>>;
        async fn create(&self, user: &User, password_hash: &str) -> Result<()>;
    }
    ```

* **Example Service: `crates/application/src/services/user_service.rs`**
    ```rust
    use std::sync::Arc;
    use anyhow::{Result, bail};
    use crate::domain::user::User;
    use crate::repositories::UserRepository;
    use uuid::Uuid;

    pub struct UserService {
        user_repo: Arc<dyn UserRepository>,
    }

    impl UserService {
        pub fn new(user_repo: Arc<dyn UserRepository>) -> Self {
            Self { user_repo }
        }

        pub async fn register_user(&self, email: &str, password: &str) -> Result<User> {
            if self.user_repo.find_by_email(email).await?.is_some() {
                bail!("User with this email already exists");
            }
            // In a real app, use a proper crypto library like argon2
            let password_hash = format!("hashed-{}", password);
            let user = User {
                id: Uuid::new_v4(),
                email: email.to_string(),
            };
            self.user_repo.create(&user, &password_hash).await?;
            Ok(user)
        }
    }
    ```

### **Layer 4: `infrastructure` (Implementation Details)**

Provides concrete implementations (**Adapters**) for the ports. It handles all communication with external systems.

* **Example Adapter: `crates/infrastructure/src/repositories/user_repository_pg.rs`**
    ```rust
    use anyhow::Result;
    use async_trait::async_trait;
    use sqlx::PgPool;
    use std::sync::Arc;
    use application::repositories::UserRepository;
    use domain::user::User;

    // This struct maps to the DB table, NOT the domain model.
    #[derive(sqlx::FromRow)]
    struct UserDb {
        pub id: uuid::Uuid,
        pub email: String,
        pub password_hash: String,
    }

    pub struct PostgresUserRepository {
        pool: Arc<PgPool>,
    }

    impl PostgresUserRepository {
        pub fn new(pool: Arc<PgPool>) -> Self {
            Self { pool }
        }
    }

    #[async_trait]
    impl UserRepository for PostgresUserRepository {
        async fn find_by_email(&self, email: &str) -> Result<Option<User>> {
            let user_db_opt = sqlx::query_as::<_, UserDb>("SELECT * FROM users WHERE email = $1")
                .bind(email)
                .fetch_optional(&*self.pool)
                .await?;

            // Map from the DB model to the Domain model if found
            Ok(user_db_opt.map(|db_user| User {
                id: db_user.id,
                email: db_user.email,
            }))
        }

        async fn create(&self, user: &User, password_hash: &str) -> Result<()> {
            sqlx::query("INSERT INTO users (id, email, password_hash) VALUES ($1, $2, $3)")
                .bind(user.id)
                .bind(&user.email)
                .bind(password_hash)
                .execute(&*self.pool)
                .await?;

            Ok(())
        }
    }
    ```

### **Layer 1: `api` & `serialization` (Entry Points)**

The outermost layer, handling interaction with the outside world using **Actix-Web**.

* **Example DTO using Serde: `crates/serialization/src/dto/user.rs`**
    ```rust
    use serde::{Deserialize, Serialize};
    use uuid::Uuid;

    // The `Deserialize` trait allows this struct to be created from JSON.
    #[derive(Deserialize)]
    pub struct RegisterUserRequest { pub email: String, pub password: String }

    // The `Serialize` trait allows this struct to be converted into JSON.
    #[derive(Serialize)]
    pub struct UserResponse { pub id: Uuid, pub email: String }
    ```

* **Example Actix-Web Handler: `crates/api/src/routes/users.rs`**
    ```rust
    use actix_web::{web, HttpResponse, Responder, post};
    use std::sync::Arc;
    use application::services::user_service::UserService;
    use serialization::dto::user::{RegisterUserRequest, UserResponse};

    #[post("/users")]
    pub async fn register_user_handler(
        // Dependency injection using actix-web's `web::Data`
        user_service: web::Data<Arc<UserService>>,
        // The request body is deserialized from JSON into our DTO
        payload: web::Json<RegisterUserRequest>,
    ) -> impl Responder {
        match user_service
            .register_user(&payload.email, &payload.password)
            .await
        {
            Ok(user) => {
                // On success, serialize the response DTO to JSON and return 201 Created.
                let response = UserResponse {
                    id: user.id,
                    email: user.email,
                };
                HttpResponse::Created().json(response)
            }
            Err(e) => {
                // On error, return a 400 Bad Request with the error message.
                HttpResponse::BadRequest().body(e.to_string())
            }
        }
    }
    ```

* **Example Actix-Web App Setup: `crates/api/src/main.rs`**
    ```rust
    use actix_web::{web, App, HttpServer};
    use std::sync::Arc;
    use sqlx::PgPool;

    // Import all the pieces
    use application::services::user_service::UserService;
    use infrastructure::repositories::user_repository_pg::PostgresUserRepository;
    use crate::routes::users::register_user_handler;

    #[actix_web::main]
    async fn main() -> std::io::Result<()> {
        // --- Composition Root ---
        // 1. Set up the database connection pool
        let db_pool = Arc::new(PgPool::connect("postgres://user:pass@localhost/db")
            .await
            .expect("Failed to create DB pool"));

        // 2. Create concrete repository implementation
        let user_repo = Arc::new(PostgresUserRepository::new(db_pool.clone()));

        // 3. Create service and inject repository
        let user_service = Arc::new(UserService::new(user_repo));

        // 4. Start the Actix-Web server
        println!("Starting server at [http://127.0.0.1:8000](http://127.0.0.1:8000)");
        HttpServer::new(move || {
            App::new()
                // Share the service instance with all handlers
                .app_data(web::Data::new(user_service.clone()))
                // Register the handler
                .service(register_user_handler)
        })
        .bind(("127.0.0.1", 8000))?
        .run()
        .await
    }
    ```

---

## 6. Consequences

### Positive

* **High Maintainability**: Code is organized by responsibility, making it easier to find and modify. The compiler enforces architectural rules.
* **Excellent Testability**: The dependency on abstractions (traits) makes unit testing with mocks straightforward and reliable.
* **Technology Independence**: The core `domain` and `application` are completely decoupled from web and database technologies, allowing for easier upgrades or replacements.
* **Clear Boundaries**: Enforces a clean separation of concerns, which is invaluable for a collaborative open-source project.

### Negative

* **Increased Boilerplate**: Adding a simple feature requires creating or modifying files in multiple crates (Data Transfer Object, handler, service, repository).
* **Steeper Learning Curve**: Developers unfamiliar with this pattern may need time to understand the flow of control and the strict separation of models (Domain vs. Database vs. Data Transfer Object).
