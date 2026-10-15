# ADR-006: Notification Channels (Including Lack of Internet Connectivity)

## Date:
2024-04-03

## Status:
Accepted

## Context:
The context for this decision is to define the notification channels or mediums for sending alerts and notifications to owners in the Fishy Watch system, considering both online and offline scenarios where internet connectivity may be limited or unavailable.

## Decision:
After analyzing the requirements and considerations, we have defined the following notification channels for Fishy Watch, including options for scenarios with and without internet connectivity:

### Notification Channels:
1. **Email Notifications**:
   - Send alerts and notifications via email to owners' registered email addresses.
   - Email notifications are suitable for non-urgent alerts and provide detailed information and action recommendations.

2. **SMS Alerts**:
   - Send SMS alerts to owners' mobile numbers for immediate notification of critical alerts.
   - SMS alerts are effective for urgent alerts, especially in scenarios where internet connectivity is limited or unreliable.

3. **Mobile App Push Notifications**:
   - Utilize push notifications within the Fishy Watch mobile app to alert owners about new alerts or critical events.
   - Push notifications work seamlessly in online scenarios but may not be available without internet connectivity.

4. **Offline Alerting**:
   - Implement offline alerting mechanisms within the mobile app to store and display recent alerts even without internet access.
   - Offline alerts provide a fallback option for owners to review critical information during connectivity disruptions.

5. **Web Dashboard Alerts**:
   - Display alerts and notifications on the web dashboard accessible to owners when they log in to the Fishy Watch platform.
   - Web dashboard alerts are effective in online scenarios but may not be accessible without internet connectivity.

6. **Integration with Third-Party Services (Optional)**:
   - Integrate with third-party notification services such as SMS gateways or offline messaging platforms for additional offline notification channels.
   - Third-party integrations can extend notification capabilities in offline environments.

## Consequences:
### Pros:
- Multi-Channel Communication: Using multiple notification channels ensures owners receive alerts through various mediums, accommodating different preferences and connectivity scenarios.
- Immediate Notification: SMS alerts and mobile app push notifications provide immediate notification, especially in urgent situations.
- Offline Accessibility: Offline alerting mechanisms and stored alerts in the mobile app offer information access during internet connectivity disruptions.
- Flexibility and Redundancy: Integration with third-party services and offline messaging platforms adds redundancy and flexibility to notification delivery.

### Cons:
- Dependency on Connectivity: Some notification channels, such as mobile app push notifications and web dashboard alerts, require internet connectivity for real-time delivery.
- Delayed Notifications: In offline scenarios, notifications may be delayed until connectivity is restored, impacting response times for critical alerts.
- Configuration and Maintenance: Managing multiple notification channels and offline alerting mechanisms requires careful configuration, monitoring, and maintenance efforts.
