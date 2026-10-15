### ADR 04: One Relational Database and One File-Storage DB

- **Title**: One relational database and one file-storage DB
- **Status**: Accepted
- **Context**:  
  ClearView’s architecture must store data for multiple domains, including candidate profiles, job postings, skill extractions, and matches. Additionally, candidate resumes, which can include unstructured data, need to be stored securely. To simplify maintenance and reduce the complexity of managing multiple databases, a decision has been made to use a **single relational database** to store structured data for all domains and a **separate file-storage system** to handle resumes and other file uploads. This approach optimizes for ease of management and reduces the overhead of maintaining multiple database services.

- **Decision**:  
  ClearView will use:
  1. **One Relational Database (PostgreSQL)**: All structured data for the candidate, employer, matching, reporting, and other domains will be stored in a single relational database. This includes candidate profiles, job postings, skill mappings, and match results.
  2. **One File-Storage Database (e.g., AWS S3)**: Candidate resumes and other file-based data will be stored separately in a file-storage database. This allows for efficient storage and retrieval of unstructured data without overloading the relational database.

  By consolidating multiple domains into one relational database and separating file storage, we simplify the architecture and reduce the number of databases that need to be managed.

- **Consequences**:
  - **Positive**:
    - **Simplified Maintenance**: Using a single relational database reduces the complexity of managing multiple database services, making maintenance and updates easier.
    - **Cost-Effective**: With fewer databases to manage, operational costs are reduced. The use of file-storage systems like AWS S3 is a scalable, low-cost option for handling large files like resumes.
    - **Unified Data Access**: Storing all structured data in one database simplifies queries and data management across multiple domains, improving the overall efficiency of data access and retrieval.
    - **Optimized for ClearView’s Scale**: Since ClearView is not expected to handle enormous amounts of data in the near term, this architecture strikes a balance between simplicity and performance.

  - **Negative**:
    - **Compromised Modularity**: Combining multiple domains into a single relational database can blur the boundaries between domains, reducing the modularity of the architecture. This may lead to challenges in maintaining data separation for different services.
    - **Scaling Challenges**: While the current expected scale of ClearView is manageable with a single relational database, as the system grows, scaling the relational database for multiple domains could become a bottleneck. Future data growth may require revisiting this decision.
    - **Potential Data Management Complexity**: As data volume and complexity increase, managing schemas, relationships, and migrations across multiple domains in a single database may become more challenging.
    - **File and Relational Data Coordination**: Although resumes are stored separately, the coordination between the file storage system and the relational database must be carefully handled to ensure consistent and accurate access to both structured and unstructured data.
