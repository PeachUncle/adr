# [ADR-001][Selection of time series database for sensor data storage]

* Status: **accepted**
* Stakeholders: developers responsible for the REST API and the MQTT broker service. In addition, those responsible for continuous delivery.
* Author: Mateusz Miekicki <miekickimateusz@gmail.com>
* Deciders:
* Date: 2023-04-02
* Gist: The decision on which time series database to choose for storing sensor data.

Technical Story: As a data engineer, I need to select an appropriate time series database to store sensor data efficiently and ensure easy retrieval and analysis of data.

## Context and Problem Statement

In our project, we have sensors generating data continuously, and we need to store this data for later analysis. We need to select a time series database that can store the sensor data efficiently and provide us with easy retrieval and analysis of the data.

## Decision Drivers

* Must: Support for time series data and efficient data storage
* Must: Easy data retrieval and analysis
* Must: Open source
* Must: SDK for C++ and Python
* Should: Scalability and high availability
* Should: Support for multiple data types
* Could: Easy integration with other tools
* Won't: High licensing cost

## Considered Options

* Questdb
* TDengine
* InfluxDB
* Timescale

## Decision Outcome

Questdb, because it offers excellent support for time series data, efficient data storage, and easy retrieval and analysis of the data. It also provides scalability and high availability and supports multiple data types. Additionally, Timescale has easy integration with other tools, making it an ideal choice for our project.

### Positive Consequences

* Efficient storage and retrieval of time series data
* Scalability and high availability
* Support for multiple data types
* Easy integration with other tools

### Negative Consequences

* Additional effort required for setup and configuration
* Three different interfaces for using the base, which can mix things up at the beginning

### Assumptions
* We only use Python and C++, Docker-based configuration.
* Insertion only via ILP interface

## Pros and Cons of the Options

### QuestDB

[QuestDB docs](https://questdb.io/docs/)

### SWOT
#### Strengths
* Very fast for both data ingest and queries, thanks to a custom columnar storage engine.
* Supports advanced SQL features like JOINs, subqueries, and window functions.
* Easy integration with popular data visualization and analysis tools like Grafana and Jupyter Notebooks.
* Has a free Community Edition that is open-source and can be used for non-commercial purposes.
* Integration with a highly efficient interface from InfluxDB.
* Integration with PostgreSQL interface.
* Friendly online interface.
#### Weaknesses
* Limited documentation and smaller user community compared to other options on this list.
* Limited integrations with third-party tools and libraries.
* Limited enterprise-level features like replication and high availability in the Community Edition.
* Poor configuration from docker.
#### Opportunities
* Questdb can potentially become more popular with the rise of real-time analytics and IoT applications that require fast data processing and analysis.
* As the user community grows, more integrations and tooling may become available.
#### Threats
* Competition from other time-series databases that are more established and have larger user communities.
* Potential for data storage limitations in the Community Edition, which only supports a limited amount of data storage.

### TDengine

[TDengine docs](https://docs.tdengine.com/)

### SWOT
#### Strengths
* Very fast and efficient, thanks to a custom memory-first storage engine.
* Supports advanced SQL features like JOINs and window functions.
* Offers an open-source Community Edition that is free to use.
* Easy to use with Python and C++.
#### Weaknesses
* Smaller user community compared to other options on this list.
* Limited integrations with third-party tools and libraries.
* Limited enterprise-level features like replication and high availability in the Community Edition.
* Chinese technical thought, I don't believe in it
#### Opportunities
* Tdengine can potentially become more popular with the rise of real-time analytics and IoT applications that require fast data processing and analysis.
* As the user community grows, more integrations and tooling may become available.
#### Threats
* Competition from other time-series databases that are more established and have larger user communities.
* Potential for data storage limitations in the Community Edition, which only supports a limited amount of data storage.

### InfluxDB

[InfluxDB docs](https://docs.influxdata.com/)

### SWOT
#### Strengths
* Very popular and widely used, with a large user community and extensive documentation.
* Offers both a free open-source Community Edition and a paid enterprise-level version with advanced features.
* Integrates well with many popular tools and libraries like Grafana, Telegraf, and Kapacitor.
* Very fast and efficient, thanks to a custom high-performance storage engine.
#### Weaknesses
* Can be complex to set up and configure for larger deployments.
* Limited support for advanced SQL features like JOINs and subqueries.
* The free Community Edition has some limitations, like a lack of clustering and high availability features.
* Hard configuration with docker
#### Opportunities
* InfluxDB is already very popular and widely used, and is likely to continue to be a popular choice for time-series databases.
* As the user community grows, more integrations and tooling may become available.
#### Threats
* Competition from other time-series databases that are more established and have larger user communities.
* Potential for vendor lock-in with the enterprise-level version, which has many advanced features not available in the open-source Community Edition.


### Timescale

[Timescale docs](https://docs.timescale.com/)

### SWOT
#### Strengths
* Timescale is an open-source relational database built specifically for time-series data, making it well-suited for time-series applications.
* Timescale can integrate well with Docker, which allows for easy deployment and scalability.
* Timescale supports both C++ and Python, providing flexibility for developers who use these languages.
* Timescale is highly scalable, allowing for the handling of large amounts of data and high write throughput.
#### Weaknesses
* Timescale is relatively new compared to other time-series databases, and may not have the same level of community support and resources available.
* While Timescale is open source, its licensing is not as permissive as some other open-source databases, which may limit its use in some contexts.
#### Opportunities
* Timescale is well-positioned to capture market share in the growing time-series database market.
* The flexibility and scalability of Timescale could make it attractive to businesses looking to handle large amounts of time-series data.
* The integration with Docker makes Timescale a good fit for containerized environments.
#### Threats
* There are many established players in the time-series database market, such as InfluxDB, that could limit Timescale's ability to gain market share.
* The complexity of managing time-series data at scale may limit adoption, particularly among smaller organizations.
* The licensing limitations of Timescale may be a disadvantage compared to some other open-source databases.
## Links

* [Link type] [Link to ADR] <!-- example: Refined by [ADR-0005](0005-example.md) -->
* … <!-- numbers of links can vary -->

## Note
### Glossary