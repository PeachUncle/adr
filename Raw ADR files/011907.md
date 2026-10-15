# Architecture Decision Record (ADR)

**Title:** Data Store Selection for Time Series Collections in IoT Devices Data

**Date:** [06/03/2024]

**Status:** Accepted

**Context:**

The Metrics Capturing System is designed to handle and examine data gathered from a vast range of medical IoT devices. Considering the typical characteristics of IoT data, such as being timestamped from a multitude of sensors, it's vital to adopt a robust data storage strategy that is specifically tailored for time series data. This approach guarantees that data is stored in a manner that facilitates quick access and analysis, which is indispensable for immediate monitoring and decision-making processes.

**Decision:**

After evaluating several data stores suitable for time series collections, the following data stores were identified as suitable for our IoT devices data:

1. **InfluxDB**: An open-source time series database designed to handle high write and query loads. It is optimized for fast, high-availability storage and retrieval of time series data in fields such as operations monitoring, application metrics, IoT sensor data, and real-time analytics.
2. **TimescaleDB**: An open-source database that combines the relational database capabilities of PostgreSQL with the scalability and performance of a time series database. It is designed to handle large volumes of time series data efficiently.
3. **OpenTSDB**: A scalable, distributed time series database built on top of Apache HBase. It is designed to store and serve metrics collected from thousands of hosts.
4. **Amazon Timestream**: A fully managed, serverless time series database service provided by AWS that makes it easy to store and analyze trillions of time series data points per day at 1/10th the cost of relational databases.

**Rationale:**

- **InfluxDB**: Offers high performance and scalability, making it suitable for large-scale IoT data storage and analysis.
- **TimescaleDB**: Combines the strengths of PostgreSQL with time series capabilities, offering a powerful and flexible solution for IoT data.
- **OpenTSDB**: Provides a robust and scalable solution for storing and querying large volumes of time series data, ideal for IoT applications.
- **Amazon Timestream**: Offers a fully managed service that simplifies the deployment and management of time series databases, making it an attractive option for teams already using AWS.

**Consequences:**

- **Pros:** The selected data stores offer a range of features that can meet the varying requirements of IoT data storage, from scalability and performance to ease of use and integration with existing systems.
- **Cons:** The choice of data store depends on the specific requirements of the project, including factors such as scalability, performance, and the existing technology stack.

**Decision Maker:** [Rami Chalhoub]

**Decision Approver:** [Kishore Allwynraj]

**Implementation Plan:**

1. **Initial Selection:** Based on the above analysis, the team will initially focus on **InfluxDB** and **TimescaleDB** for their proven scalability and robustness.
2. **Technical Evaluation:** The team will conduct a technical evaluation of these data stores to assess their suitability for the project's specific requirements, including factors such as performance, scalability, and ease of integration.
3. **Integration:** Once the optimal data store is identified, the team will proceed with integrating it into the data storage pipeline for IoT devices data.
4. **Monitoring and Optimization:** After integration, the team will monitor the performance of the data storage mechanism and optimize the configuration as necessary to ensure optimal performance.

**Review Date:** [06/03/2024]
