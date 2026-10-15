# ADR-005: Choice of Hosting and Deployment Platform

**Date:** 2025-09-02

**Status:** Decided & Implemented

## Context

The PlumbingPOC project consists of a static frontend application (built by Vite) and a serverless Node.js API backend. The primary requirement for deployment is a seamless, Git-based Continuous Integration and Continuous Deployment (CI/CD) workflow that can handle this modern "Jamstack" architecture with minimal configuration.

## Decision

We will use **Netlify** as our primary platform for hosting the frontend, deploying the serverless backend functions, and managing the CI/CD pipeline.

## Consequences

*   **Pros:**
    *   **Integrated Git Workflow:** Netlify's core value proposition is its direct integration with GitHub. Pushing code to the main branch automatically triggers a build and deploy, which is ideal for rapid, iterative development.
    *   **Unified Full-Stack Hosting:** The platform is purpose-built to host static site assets and manage serverless functions in a single, cohesive environment. The proxying of `/api` requests to the serverless function is handled automatically, simplifying configuration.
    *   **Zero-Ops & Scalability:** Netlify is a fully managed platform, eliminating the need for us to provision, manage, or scale servers. It handles the CDN for the frontend and the execution environment for the backend functions.
    *   **Generous Free Tier:** The free tier is sufficient for development, prototyping, and small-scale production use, making it highly cost-effective.
    *   **SMS Notification Support:** Netlify Functions have been successfully implemented to handle SMS notifications via Twilio integration, providing a secure, serverless solution for real-time admin alerts on new quote requests and quote acceptances.

*   **Cons:**
    *   **Serverless Function Limitations:** Netlify Functions have constraints on execution time (e.g., 10 seconds on the free tier). This is a critical consideration for our AI API calls, which could time out if the external LLM is slow. This risk must be monitored.
    *   **Platform Lock-in:** The `netlify.toml` configuration and function deployment format are specific to Netlify. While the underlying Express app is portable, migrating the full CI/CD pipeline to another provider (like Vercel or AWS) would require a dedicated effort.

*   **Alternatives Considered:**
    *   **Vercel:** The most direct competitor to Netlify, offering a very similar feature set. The choice of Netlify was likely based on developer preference or prior experience.
    *   **AWS Amplify:** A powerful alternative from AWS that also provides an integrated full-stack workflow. It is often perceived as more complex to configure than Netlify.
    *   **Self-Managed on AWS (S3/CloudFront + Lambda):** This approach offers maximum power and flexibility but was rejected due to its immense configuration and operational complexity, which would have been contrary to the project's goal of rapid development.
