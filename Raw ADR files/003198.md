# ADR-001: Choice of Primary Backend Platform

**Date:** 2025-09-02

**Status:** Decided & Implemented

## Context

The PlumbingPOC project requires a full-stack solution to serve as a client management and quoting platform. The core requirements include secure user authentication, relational data storage, **secure file storage for user-uploaded images and documents**, and real-time capabilities for features like the communication log. The development timeline is highly accelerated.

## Decision

We will use **Supabase** as the primary Backend-as-a-Service (BaaS) platform. This decision centralizes our **database, authentication, object storage,** and real-time needs into a single, managed service.

## Consequences

*   **Pros:**
    *   **Development Velocity:** Supabase provides an immense out-of-the-box feature set that enabled the rapid prototyping phase.
    *   **Integrated Security Model:** The use of Postgres Row Level Security (RLS) provides a powerful, declarative way to enforce data access rules at the database level.
    *   **Scalability & Maintainability:** As a managed service, Supabase handles database scaling, backups, and maintenance, reducing operational overhead.
    *   **Real-time Functionality:** The built-in Realtime server is critical for features like the `CommunicationLog.tsx`, enabling a live, interactive user experience.
    *   **Integrated Object Storage:** Supabase Storage provides an S3-compatible solution for handling file uploads (`uploadAttachment` in `requestController.js`). This is crucial for the quote request flow and is secured with its own policy layer, as defined in `supabase/SUPABASE_DATABASE_AND_AUTH_SETUP.md`. This avoids needing a separate S3/Cloudinary/etc. integration.

*   **Cons:**
    *   **Vendor Lock-in:** The application is now deeply integrated with the Supabase ecosystem, including its Storage API. Migrating to another platform would be a significant effort.
    *   **Cost at Scale:** While the free/pro tiers are generous, pricing for high-traffic applications with significant **storage egress** or database usage must be monitored.

*   **Alternatives Considered:**
    *   **Firebase/Firestore:** A strong competitor. We chose Supabase due to its foundation in standard Postgres and its more transparent, S3-like Storage solution.
    *   **Custom Backend (Node.js + Postgres + S3 on AWS):** This would offer maximum flexibility but was rejected due to the significantly higher initial development and operational effort, which would have compromised our goal of rapid prototyping.
