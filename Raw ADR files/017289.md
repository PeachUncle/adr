# ADR-001 Choose approach for delivering weather update emails

### Status: accepted
### Date: 06.06.2025
### Author: Olha Dziuhal

## Context

We need to choose a unified approach for delivering city weather update emails at user-defined frequencies:
- Supported frequencies:
  - **Daily**
  - **Hourly**
- A user subscribes to weather updates by confirming their email.
- The chosen method should support **both sending and scheduling**.
- No additional constraints were imposed on infrastructure or third-party services.

## Considered Options

| Approach                        | Description |
|--------------------------------|-------------|
| **1. Cron + Direct Sending**   | A scheduled Laravel command (cron) triggers direct email sending at fixed intervals. |
| **2. Cron + Queued Jobs**      | A scheduled command dispatches email jobs to a queue for asynchronous processing. |
| **3. Per-User Scheduled Queues** | Each user’s subscription creates delayed jobs, allowing user-specific timing via the queue system (e.g., Redis). |
| **4. Third-Party Email Scheduling (e.g., SendGrid API)** | Use external provider APIs that support scheduled delivery at specific times. |

### 1. Cron + Direct Sending

**Pros:**
- Simple setup
- Easy to control timing with Laravel scheduler
- No queue infrastructure needed

**Cons:**
- Blocking (synchronous) email delivery
- Not scalable for large user base
- No per-user timing granularity

---

### 2. Cron + Queued Jobs

**Pros:**
- Easy to implement with Laravel
- Offloads email sending to queue (asynchronous)
- Scalable for medium-to-large user bases

**Cons:**
- Still limited to fixed (non-personalized) cron intervals
- Requires queue infrastructure (e.g., Redis, workers)

---

### 3. Per-User Scheduled Queues

**Pros:**
- Full flexibility in scheduling (per-user frequency and time)
- Async, decoupled, highly scalable
- Can be extended to support retry logic, monitoring, etc.

**Cons:**
- More complex setup (custom logic for scheduling delayed jobs)
- Requires persistent queue backend and monitoring

---

### 4. Third-Party Email Scheduling (e.g., SendGrid)

**Pros:**
- Offloads scheduling and delivery to the provider
- Minimal infrastructure
- Built-in reliability and analytics

**Cons:**
- Limited flexibility in advanced use cases (e.g., user-defined times)
- Vendor lock-in
- May require additional SDK/API integration effort

---

## Decision

**Selected Option:**  
✅ **Per-User Scheduled Queues (Option 3)** using **Redis** as queue backend.

### Why:
- Provides full control over both **when** and **how** emails are sent
- Enables per-user frequency handling (hourly, daily)
- Scalable and asynchronous
- Seamlessly integrates with Laravel queue system

---

## Consequences

### Positive
- Supports per-user, fine-grained delivery control
- Scales with number of users
- Queue workers ensure async handling and retry logic

### Negative
- Requires Redis setup and job monitoring
- Higher development complexity for scheduling logic
