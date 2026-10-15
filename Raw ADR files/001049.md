# ADR 005: Use of an API gateway
## Context
The purpose of the app is to predict cardiac risk according to the data provided by the patient. The app utilizes a machine learning model to predict cardiovascular diseases, ultimately aiming to reduce mortality rates.
## Decision
The app will use an API gateway to interact with various services. This decision is based on the following reasons:
* Efficiency: API gateways enable efficient communication between the app and multiple services as well as streamlining the process of obtaining and processing patient information.
* Security: An API gateway acts as a middleman between the app and the data, ensuring that the app's access to sensitive patient information is secure and controlled.
* Scalability: As the app's user base grows, an API gateway allows for easy scaling of the app's data handling capabilities, ensuring that the app remains responsive and efficient.
## Rationale
The use of an API gateway in our app offers several benefits, including:
* Centralized data management: An API gateway serves as a central point for managing and coordinating data, making it easier to maintain and update the app's data handling logic.
* Improved security: By acting as a middleman between the app and other services, the API gateway ensures that the app's access to sensitive patient information is secure and controlled, reducing the risk of unauthorized access or data breaches.
* Scalability: As the app's user base grows, an API gateway allows for easy scaling of the app's data handling capabilities, ensuring that the app remains responsive and efficient.
## Status
Accepted
## Consequences
Implementing an API gateway in the app may lead to the following consequences:
* Increased development complexity: Integrating an API gateway into the app may increase the development complexity, requiring additional time and resources to implement and maintain.
* Potential performance issues: If the API gateway is not properly optimized, it may introduce latency or performance issues in the app, affecting the user experience.
## Conclusion
Using an API gateway in the app is a reasonable decision, as it provides numerous benefits such as efficient data management, improved security, and scalability. However, it is essential to carefully consider the potential consequences and trade-offs associated with this decision, ensuring that the app's overall performance and user experience are not compromised.
