---
status: "accepted"
date: {2024-01-06}
deciders: {Sushain Garg}
---
# MERN Stack for Development of Visa Application System.

## Context and Problem Statement

The Visa Application System needs a modern, efficient, and scalable technology stack for development. The stack should facilitate rapid development, handle diverse data types, support a seamless user experience, and integrate well with the chosen cloud platform (AWS).

## Decision Drivers

* Rapid Development: The chosen stack should enable quick prototyping, efficient development, and streamlined testing processes.
* Data Flexibility: The stack should accommodate various data types, including structured and unstructured data, to effectively manage visa application information.
* User Experience: The stack should create a user-friendly interface with smooth interactions and responsive performance.
* Ecosystem Integration: The stack should integrate well with AWS services and other potential third-party tools or libraries.
* Developer Expertise: The availability of expertise in the chosen stack is crucial for successful implementation and maintenance.
* JavaScript Proficiency: strong JavaScript skills align well with a JavaScript-based stack.

## Considered Options

* MERN stack (MongoDB, Express, React, Node.js)
* LAMP stack (Linux, Apache, MySQL, PHP)
* Java-based stacks (Spring Boot, Angular, etc.)
* Serverless architectures

## Decision Outcome

Chosen option: "MERN stack with Redux Toolkit", because
MERN offers a cohesive JavaScript ecosystem for full-stack development, efficient performance, flexibility with diverse data types, a strong focus on user experience through React, and seamless integration with AWS services. Redux Toolkit simplifies state management and streamlines development.

### Consequences

* Good, because Rapid development with JavaScript's agility and the MERN stack's synergy.
* Good, because Flexibility in handling various data types with MongoDB's schema-less nature.
* Good, because Enhanced user experience with React's component-based structure and focus on UI.
* Good, becauase Excellent integration with AWS services and other JavaScript-based tools.
* Good, Leverages existing JavaScript expertise.
* Bad, because Potential limitations for specific requirements that might be better suited to alternative technologies.
* Bad, because Need for JavaScript proficiency across the development team.


### Confirmation

Compliance with this ADR will be confirmed through code reviews, architecture diagrams, and technology stack documentation to ensure adherence to the MERN stack with Redux Toolkit.

