# ✅ ADR-002: Hexagonal Architecture & Naming Conventions

## 🌟 Decision

We adopt **Hexagonal Architecture (Ports & Adapters)** for all microservices, with standardized **file naming conventions** aligned with the **NestJS + TypeScript + DDD community**.
This includes using the suffix `UseCase` for all application-layer use case classes, and organizing code **by layer first**, then **by feature** within each layer.

---

## 💡 Architecture Layers Overview

### 🟩 1. Domain Layer
- **What:** Core business rules, pure logic
- **No NestJS, DB, or HTTP dependencies**
- **Contents:**
  - Entities
  - Value Objects
  - Domain Exceptions
  - Domain Repositories (interfaces only)
- **Naming:** `PascalCase.ts`

**Examples:**
```
Task.ts                          → class Task  
TaskRepository.ts                → interface TaskRepository  
TaskStatus.ts                    → enum TaskStatus  
InvalidTaskStatusException.ts    → class InvalidTaskStatusException  
```

---

### 🗭 2. Application Layer
- **What:** Use case orchestration, ports, and DTOs
- **Contains:**
  - `UseCases`: Application services implementing business workflows
  - `Ports`: Interfaces needed by the application
  - `DTOs`: Structured input/output objects
- **Naming:**  
  - Use cases: `PascalCaseUseCase.ts`  
  - Ports: `PascalCasePort.ts`  
  - DTOs: `PascalCaseDto.ts`

**Examples:**
```
CreateTaskUseCase.ts             → class CreateTaskUseCase  
NotificationPort.ts              → interface NotificationPort  
CreateTaskRequestDto.ts          → interface CreateTaskRequestDto  
```

- **Port In (Driving Port):** Optional interface for each use case (e.g., `ICreateTaskUseCase`) — helpful in strict DDD or for mocking.
- **Port Out (Driven Port):** Mandatory interface to describe outbound dependencies (`NotificationPort`, `TaskRepository`, etc.)

---

### 🔵 3. Infrastructure Layer
- **What:** NestJS controllers, DB clients, external integrations
- **Contains:**
  - Controllers (REST, Socket)
  - Adapters (DB, HTTP, Mail, etc.)
  - NestJS Modules and Configs
- **Naming:** `PascalCaseSuffix.ts` (e.g., `TaskController.ts`, `EmailNotificationAdapter.ts`)

**Examples:**
```
TaskController.ts               → class TaskController  
PrismaTaskRepository.ts         → class PrismaTaskRepository implements TaskRepository  
EmailNotificationAdapter.ts     → class EmailNotificationAdapter implements NotificationPort  
```

---

## ⚡ Use Case Flow

```plaintext
📦 Controller (REST/SOCKET)
    ↓
📘 Application UseCase (e.g., CreateTaskUseCase)
    ↓
1️⃣ Domain Repository or Application Port
    ↓
🔌 Infrastructure Adapter (e.g., PrismaTaskRepository)
    ↓
💽 External System (e.g., DB, Mailgun)
```

| Case                          | Port Type         | Example                                |
|------------------------------|-------------------|----------------------------------------|
| Domain persistence (Tasks)   | Domain Repository | `TaskRepository → PrismaTaskRepository`|
| Side-effects (Email, Stripe) | Application Port  | `NotificationPort → EmailNotificationAdapter`|

---

## 📁 Recommended Folder Structure (By Layer > By Feature)

```plaintext
src/
├── domain/
│   ├── task/
│   │   ├── entities/                → Task.ts
│   │   ├── repositories/            → TaskRepository.ts
│   │   ├── value-objects/           → TaskStatus.ts
│   │   └── exceptions/              → InvalidTaskStatusException.ts
│   └── user/
│       └── ...

├── application/
│   ├── task/
│   │   ├── use-cases/               → CreateTaskUseCase.ts
│   │   ├── ports/                   → NotificationPort.ts
│   │   └── dto/                     → CreateTaskRequestDto.ts
│   └── user/
│       └── ...

└── infrastructure/
    ├── task/
    │   ├── controllers/
    │   │   ├── rest/            → TaskController.ts
    │   │   └── sockets/         → TaskSocketGateway.ts
    │   ├── adapters/
    │   │   ├── database/        → PrismaTaskRepository.ts
    │   │   └── external-services/
    │   │       → EmailNotificationAdapter.ts
    │   └── config/                  → AppModule.ts
    └── user/
        └── ...
```

---

## ✅ Summary Table

| Layer          | File Name Example              | Class/Interface             | Purpose                      |
|----------------|--------------------------------|-----------------------------|------------------------------|
| Domain         | `TaskRepository.ts`            | `interface TaskRepository`  | Persistence port             |
| Application    | `NotificationPort.ts`          | `interface NotificationPort`| External system port         |
| Application    | `CreateTaskUseCase.ts`         | `CreateTaskUseCase`         | Use-case logic               |
| Infrastructure | `PrismaTaskRepository.ts`      | `PrismaTaskRepository`      | Implements domain repository |
| Infrastructure | `EmailNotificationAdapter.ts`  | `EmailNotificationAdapter`  | Implements application port  |

---