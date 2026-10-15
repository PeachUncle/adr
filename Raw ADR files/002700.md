# Event-Driven chosen architecture Style

## Context
MonitorMe aims to provide instantaneous alerts to medical professionals by leveraging received vital data, enabling swift responses to potential problems with a patient. 
The system's core functionality revolves around real-time monitoring of vital signs, ensuring that healthcare providers receive timely notifications, facilitating prompt and 
effective interventions when necessary.

## Evaluation Criteria 
In the requirements analysis phase, the team identified the following pivotal architectural characteristics for the MonitorMe system:
- Performance - each patient’s vital signs must be analyzed and a medical professional need to be alerted if an issue is detected (e.g., decrease in oxygen level) or reaches a preset threshold (e.g., temperature has reached 104 degrees F).
- Responsiveness - data is read from eight different patient-monitoring devices and sent to a consolidated monitoring screen (per nurses station) with an average response time of 1 second or less
- Fault Tolerance - MonitorMe must still function for other vital sign monitoring (monitor, record, analyze, and alert), if any vital sign device (or software) fails 

## Options
1) Event-driven architecture focuses on the flow of events within a system or between different systems, often in the form of messages or notifications. Various components of a system communicate and react to events asynchronously, rather than through direct, synchronous method calls. Event-driven architectures excel at providing real-time responsiveness. In the context of MonitorMe, where timely alerts for potential patient issues are critical, the event-driven model aligns with the need for instantaneously processing vital sign data and triggering alerts. And can also enhance fault tolerance by allowing the system to gracefully handle faults or disruptions. This is critical for ensuring continuous monitoring and alerting capabilities, especially in a healthcare setting where system reliability is paramount.

2) Microservice architecture approach was considered as well since it offers numerous benefits, including agility, scalability, and ease of maintenance. But it may introduce certain challenges in terms of performance, especially in scenarios where low latency is crucial, such as providing fast alerts in healthcare systems. 

## Decision
After conducting a thorough assessment utilizing the Architecture Styles Worksheet, the team has arrived at the decision that the most fitting architectural solution for the MonitorMe system is the adoption of an event-driven architecture. This conclusion is based on the alignment of the event-driven paradigm with the identified project requirements and essential architectural characteristics. The team foresees that embracing an event-driven architecture will effectively address the dynamic nature of vital sign monitoring, offering scalability and responsiveness crucial for the system's success.

## Status
Proposed

## Consequences:

Real-time Responsiveness: Event-driven architectures excel at delivering real-time updates, aligning with the system's goal of monitoring vital signs promptly and providing instantaneous notifications to medical professionals.

Fault Tolerance Enhancement: The event-driven approach enhances fault tolerance by enabling the system to gracefully handle faults or disruptions, ensuring uninterrupted monitoring and alerting capabilities.

The decision to embrace an event-driven architecture for the MonitorMe system is substantiated by its positive impact on adaptability, integration, real-time responsiveness, scalability, and fault tolerance. Acknowledging potential challenges, the team is poised to capitalize on the benefits while proactively addressing complexities, learning curve factors, and risks associated with data consistency and routing logic.

Adaptability Benefit: Leveraging an event-driven architecture provides adaptability, empowering the MonitorMe system to seamlessly integrate new features and integrations without causing major disruptions.

![ArchitectureStyle](https://github.com/ArchitectsEvolutionZone/MonitorMe/blob/main/2.ArchitectureVisualization/ArchitectureStylesWorksheet.png)

## Usefull links 
- [C4 Diagram](https://github.com/ArchitectsEvolutionZone/MonitorMe/blob/main/2.ArchitectureVisualization/C4Diagram.md)
- [Architectural style](https://github.com/ArchitectsEvolutionZone/MonitorMe/blob/main/2.ArchitectureVisualization/ArchitectureStyle.md)

