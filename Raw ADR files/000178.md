**Title**: ADR-0001-Retry Mechanisms for Provider Calls

**Status**: [[Accepted Status]], (By [[Hadi]] - at 2024-10-02)

**Tags**: [[Resilience]], [[Integration]], [[Retry]], [[Providers]]

**Context**: The flight ticket selling system heavily relies on external providers for fetching flight information and pricing. However, these providers might experience occasional downtimes or transient failures, leading to potential service disruptions for users. To mitigate such issues and ensure a resilient system, the implementation of retry mechanisms for calling the providers is under consideration.

**Decision**: We decide to implement retry mechanisms for calling the providers to enhance the resilience of the flight ticket selling system. When a call to a provider fails due to network issues, timeouts, or other transient errors, the system will automatically retry the request after a brief delay. This retry mechanism will include configurable parameters such as maximum retry attempts, exponential backoff strategies, and jitter to prevent overwhelming the providers' services during high loads.

**Justification**: The decision to implement retry mechanisms is based on the necessity to provide a seamless user experience even in the face of temporary provider failures. By retrying failed requests, we increase the chances of successfully retrieving the required flight information and pricing for customers, thus reducing the impact of transient provider issues on the system's availability. Additionally, incorporating exponential backoff and jitter helps prevent the system from flooding the providers with retry attempts, thereby minimizing the risk of exacerbating the underlying issues.

**Consequences**:

✅**Improved Resilience**: The implementation of retry mechanisms enhances the system's resilience by mitigating the impact of transient provider failures.
✅**Enhanced User Experience**: Users will experience fewer disruptions and errors when accessing flight information and pricing, leading to higher satisfaction and retention.
❌**Increased System Complexity**: Introducing retry mechanisms adds complexity to the system, requiring careful implementation and monitoring to ensure optimal performance and resource utilization.
❌**Potential Delay in Response**: While retrying failed requests can increase the likelihood of success, it may also result in slightly delayed responses for some requests, especially during periods of prolonged provider unavailability.
❌**Resource Consumption**: The retry mechanisms may increase resource consumption, particularly during peak usage times or when facing frequent provider failures. Therefore, proper resource management and monitoring are crucial to prevent overloading the system.