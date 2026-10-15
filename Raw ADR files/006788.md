---
status: "proposed"
date: "2024-11-23"
decision-makers: "@Ryangr0"
consulted: "@devops, @engineering, @product"
informed: "@developers, @security"
---

# PostgreSQL vs In-Memory (Lunr) vs Elasticsearch

## Context and Problem Statement

Our Backstage implementation requires a robust and efficient search capability to meet user expectations and business needs. With a dataset of only a few hundred documents, we need a solution that balances performance, cost, and maintainability while addressing the specific needs of our scale and usage patterns.

## Decision Drivers

- Need for efficient search functionality within Backstage.
- Desire for a solution that integrates well with Backstage’s architecture.
- Requirement to support basic and full-text search features.
- Aim to minimize operational overhead given our dataset size.
- Preference for a cost-effective solution aligned with our team's expertise.

## Considered Options

- **Option 1:** Use **PostgreSQL** for Backstage search.
- **Option 2:** Use **In-Memory Search Engine (Lunr)** for Backstage search.
- **Option 3:** Use **Elasticsearch** for Backstage search.

## Decision Outcome

Chosen option:
**Adopt PostgreSQL for Backstage search**, because it provides sufficient capabilities for our dataset size, integrates seamlessly with our current setup, and minimizes additional infrastructure requirements.

### Consequences
- Good, because PostgreSQL is already part of our stack and requires no additional setup.
- Good, because it offers adequate performance for a few hundred documents.
- Good, because it avoids introducing additional complexity and cost.
- Bad, because it may lack scalability for larger datasets in the future.
- Bad, because it provides fewer advanced search features compared to Elasticsearch.

#### Mitigating circumstances
- The current dataset size (a few hundred documents) ensures PostgreSQL’s performance remains acceptable.
- We can reassess and migrate to a more robust solution (e.g., Elasticsearch) if our dataset or requirements grow significantly.

## Pros and Cons of the Options

### **Option 1: PostgreSQL**

**Description:** Use PostgreSQL’s native capabilities (e.g., pg_trgm, full-text search) to implement search in Backstage.

**Pros:**

- **Familiarity:** Our team is already experienced with PostgreSQL.
- **Integration:** Seamless integration with Backstage’s existing database setup.
- **Cost-Effective:** Avoids additional infrastructure and associated costs.

**Cons:**

- **Limited Advanced Features:** Lacks advanced search capabilities such as relevance tuning and complex filtering.
- **Scalability Concerns:** May not meet future needs if the dataset grows significantly.

### **Option 2: In-Memory Search Engine (Lunr)**

**Description:** Use Lunr, an in-memory search engine, for Backstage search.

**Pros:**

- **Zero-Config Setup:** Enabled by default in Backstage, requiring minimal configuration.
- **Ease of Use:** Simple to set up and maintain for development and small-scale deployments.
- **No Additional Infrastructure:** Operates within the existing application environment.

**Cons:**

- **Scalability Issues:** Not suitable for larger datasets due to performance limitations.
- **Limited Advanced Features:** Lacks advanced search functionalities and customization options.
- **Resource Constraints:** In-memory operations may consume significant resources.

### **Option 3: Elasticsearch**

**Description:** Use Elasticsearch, a distributed search engine designed for advanced search and analytics in Backstage.

**Pros:**

- **Advanced Search Features:** Supports full-text search, relevance scoring, and complex filtering.
- **Scalable:** Designed to handle large datasets with horizontal scaling capabilities.
- **Rich Ecosystem:** Offers plugins and integrations for analytics and monitoring.

**Cons:**

- **Operational Overhead:** Requires managing a separate infrastructure component.
- **Resource Intensive:** Higher resource consumption compared to PostgreSQL or Lunr.
- **Learning Curve:** Teams need training to effectively use and manage Elasticsearch.

## More Information

- [Backstage Search Engines Documentation](https://backstage.io/docs/features/search/search-engines/)
- [PostgreSQL Full-Text Search Documentation](https://www.postgresql.org/docs/current/textsearch.html)
- [Lunr.js Documentation](https://lunrjs.com/)
- [Elasticsearch Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)

