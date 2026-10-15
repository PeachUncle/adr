### ADR 06: Analytics as Part of Regular Database

- **Title**: Analytics as part of regular database
- **Status**: Accepted
- **Context**:  
  ClearView needs to provide reporting and analytics functionality to track system performance, candidate-job matching outcomes, and other business metrics. Initially, a separate analytics database could be set up to handle this, but this adds complexity and operational overhead, especially given that real-time analytics is not a current requirement. To simplify the architecture and reduce costs, the decision has been made to embed analytics within the regular operational database, avoiding the need for a dedicated analytics database for now. This allows us to generate periodic reports and perform batch processing without the additional complexity of a real-time analytics pipeline.

- **Decision**:  
  Analytics data will be stored in the same relational database as the operational data, avoiding the need for a separate analytics database. The regular database will handle:
  1. **Aggregated Data**: Storing aggregated data from candidate-job matching, system usage, and other metrics used for reporting.
  2. **Business Reporting**: Providing data for periodic business reports on key metrics like active users, matches, employer engagement, and service performance.
  3. **Batch Processing**: Analytics will be run in batch mode, avoiding the complexities and costs of real-time analytics.

  By embedding analytics in the regular database, we simplify the system architecture and keep costs low, while retaining the ability to generate valuable insights from the stored data.

- **Consequences**:
  - **Positive**:
    - **Simplified Architecture**: Embedding analytics in the regular database reduces the need for a separate data pipeline or additional infrastructure for handling analytics, lowering both operational complexity and costs.
    - **Cost Efficiency**: This approach saves the costs associated with managing a separate analytics database, making it more efficient for ClearView’s current scale and requirements.
    - **Easy Maintenance**: Maintaining a single database simplifies database administration tasks such as backups, monitoring, and scaling.
    - **Scalability Options**: If real-time or advanced analytics needs grow in the future, it will be fairly easy to move the analytics data to a separate dedicated database as the system scales.

  - **Negative**:
    - **Performance Risks**: Combining both operational and analytics data in the same database may increase the load on the database, potentially affecting the performance of core system functionalities if queries become too complex or if analytics data grows significantly.
    - **Limited Analytics Capabilities**: Embedding analytics in the regular database may limit the ability to perform advanced or real-time analytics, which could become a bottleneck if more sophisticated analytics features are required in the future.
    - **Scaling Issues**: As the system grows, the volume of analytics data may outpace the capacity of the regular database, necessitating a migration to a dedicated analytics solution, which would require additional development and migration efforts.
