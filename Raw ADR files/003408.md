---
Status: Accepted
Date: 04/01/2025
Decision-makers: Sam
---

# Using MongoDB as the Database for the Quizzing Project 
## Context and Problem Statement
The quizzing project requires a scalable and flexible database to handle dynamic user data, quiz results, and real-time interactions. A key consideration is ensuring that the database can handle a variety of data types efficiently, support high-speed read and write operations, and allow easy modifications to data structure as the project evolves. Given these requirements, it is essential to choose a database that supports rapid development, offers strong support for JSON-like data, and scales well with increasing user engagement.

## Decision Drivers

* Scalability to handle increasing user load.
* Flexibility in handling dynamic and semi-structured data (e.g., quiz results, user progress, leaderboards).
* Support for rapid development and iteration.
* Real-time read and write capabilities.
* Robust ecosystem and developer support.

## Considered Options

* **Option 1:** MongoDB  
* **Option 2:** MySQL  
* **Option 3:** PostgreSQL  
* **Option 4:** Firebase Realtime Database  

## Decision Outcome

**Chosen option:** MongoDB, because it offers a flexible schema, easy integration with JavaScript/Node.js (which the quizzing application is built on), excellent horizontal scalability, and the ability to store JSON-like documents. This makes it an ideal fit for the dynamic nature of quiz data (e.g., different quiz formats, user performance tracking).

### Consequences

* **Good, because:**
  * MongoDB’s document model allows for flexible and fast modifications to data structures as new features are added to the application (e.g., new types of quizzes, additional leaderboard attributes).
  * Horizontal scalability ensures that the application can grow as more users participate without significant re-engineering of the database architecture.
  * MongoDB’s integration with the Node.js ecosystem reduces development time.

* **Bad, because:**
  * MongoDB may not be as efficient for complex queries or transactions involving large joins, which could be needed as the project scales or becomes more feature-rich.
  * Potential for data duplication due to the schema-less nature of the database, requiring careful management to avoid redundancy.

### Confirmation
After considering the project’s needs for scalability, flexible data handling, and rapid development, MongoDB was selected as the preferred database solution. This decision is based on the database's ability to handle dynamic data, ease of integration, and scalability as the project grows.

## Pros and Cons of the Options

### **MongoDB**

* **Good, because:**
  * Flexible schema for handling varied and evolving data structures.
  * Highly scalable and supports large amounts of data without performance degradation.
  * Seamless integration with the backend technology stack (Node.js, Express).
  * Excellent support for real-time data operations, such as leaderboard updates.

* **Neutral, because:**
  * Does not provide full ACID transactions out of the box for multi-document operations, which may be needed for specific future features.

* **Bad, because:**
  * Querying large datasets or complex relationships might require more effort and can become inefficient compared to relational databases.

### **MySQL**

* **Good, because:**
  * ACID-compliant transactions ensure data consistency, which is important for some applications that require strict data integrity.
  * Mature, stable, and widely supported with a strong developer community.

* **Neutral, because:**
  * Fixed schema can be restrictive for rapidly changing requirements.

* **Bad, because:**
  * Less flexible for handling semi-structured data compared to NoSQL databases like MongoDB.
  * Vertical scaling limitations could pose challenges as the application grows.

### **PostgreSQL**

* **Good, because:**
  * Strong relational features and support for JSON data types, which allows some flexibility.
  * Excellent at complex queries and joins, useful if the application requires these in the future.

* **Neutral, because:**
  * Slightly more complex to set up and maintain compared to MongoDB.

* **Bad, because:**
  * Slower write performance than MongoDB, especially with large-scale real-time data handling.
  * Horizontal scalability can be more complex and require additional tools.

### **Firebase Realtime Database**

* **Good, because:**
  * Real-time syncing for a fast and responsive user experience.
  * Managed service, which reduces overhead on infrastructure.

* **Neutral, because:**
  * More suitable for mobile-first applications and could be an overkill for a web application.

* **Bad, because:**
  * Limited querying capabilities compared to MongoDB and relational databases.
  * Pricing can become expensive as the application scales.
