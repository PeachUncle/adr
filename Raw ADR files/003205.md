# ADR-011: Choice of SMS Notification Service

**Date:** 2025-09-13

**Status:** Decided & Implemented

## Context

The application needs to send real-time SMS notifications to administrators for critical business events, such as new quote request submissions and customer quote acceptances. A reliable SMS service is required to ensure timely delivery of these notifications.

## Decision

We will use **Twilio** as our SMS notification service provider, integrated via Netlify Functions for secure, serverless SMS delivery. The implementation follows a decoupled architecture where the Express API triggers SMS notifications through HTTP calls to a dedicated Netlify Function (`send-sms.js`), which handles the actual Twilio API communication.

## Implementation Details

* **Netlify Function:** `packages/backend/netlify/functions/send-sms.js` - Secure microservice for SMS sending
* **Orchestration Service:** `packages/backend/api/services/sms/twilio/client.js` - Handles admin phone number retrieval and function triggering
* **Integration Points:** SMS notifications are triggered in `requestController.js` for:
  * New quote request submissions (`sendNewRequestNotification`)
  * Customer quote acceptances (`sendQuoteAcceptedNotification`)

* **Current Implementation:** `packages/backend/api/services/sms/twilio/client.js`
* **Future Migration:** Will be updated to use Azure Communication Services

## Consequences

*   **Pros:**
    *   **Real-Time Notifications:** Provides immediate SMS alerts to administrators for time-sensitive business events
    *   **Secure Architecture:** Uses Netlify Functions with secret-based authentication to isolate SMS credentials
    *   **Non-Blocking:** Fire-and-forget HTTP calls ensure the main API flow is not delayed by SMS sending
    *   **Scalable:** Serverless architecture automatically handles varying notification volumes
    *   **Reliable Delivery:** Twilio's established infrastructure ensures high SMS deliverability rates

*   **Cons:**
    *   **Cost Model:** SMS delivery incurs per-message costs from Twilio
    *   **Phone Number Management:** Requires acquisition and management of Twilio phone numbers
    *   **External Dependencies:** Adds Twilio service as a critical dependency for notifications
    *   **Phone Number Privacy:** Requires storing admin phone numbers in the database

*   **Alternatives Considered:**
    *   **AWS SNS:** A powerful alternative from AWS. Rejected due to increased complexity and configuration overhead compared to Twilio's straightforward API.
    *   **Direct Express Integration:** Rejected for security reasons - keeping SMS credentials isolated in serverless functions prevents potential exposure.
    *   **Other SMS Providers (e.g., MessageBird, Nexmo):** Twilio was chosen for its comprehensive documentation, developer-friendly SDK, and proven reliability in production environments.

## Security Considerations

* SMS function requires `NETLIFY_FUNCTION_SECRET` header for authentication
* Twilio credentials are stored as Netlify environment variables
* Admin phone numbers are retrieved dynamically from Supabase user_profiles table
* Failed SMS attempts are logged but don't break the main application flow
