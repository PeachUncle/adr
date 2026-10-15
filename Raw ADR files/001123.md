# Handling Resume files in Blob Storage

## Context

The way ClearView handles files is of crucial importance since it can negatively impact system performance if not done properly. The files are uploaded by candidates, read by the AI module to extract important information and remove PII, but they should be also stored so that the HR Integration module can use them when employers unlock a candidate profile.

## Decision: 
The decision is to store Resume files in Blob Storage because of its advantages in scalability, security and cost-efficiency.

Our modules can access the Blob Storage and use the Resume files as needed. The files will be transmitted between modules. We chose to go with the Amazon S3 solution.

## Status
Proposed

## Options
  * File-Based Storage in Cloud: There are several solutions for storing files in cloud, such as AWS S3, Azure Blob Storage, Google Cloud Storage that are similar in functionality.
  * Database Storage: Storing Blobs in a database would easier implementation that is not as performant as dedicated storage solutions.
  * On-Premises File Servers:  A good solution for security, but not that cloud friendly.
 
Modern HR systems are in cloud and since we are already proposing a cloud-based infrastructure in AWS we think that AWS S3 is a good solution for ClearView. Multiple cloud storage providers could also be added in future to ensure data redundancy.

## Consequences
  * Scalability: AWS S3 is capable of handling very large volumes of data that makes it ideal for a growing system.
  * Availability: AWS S3 provides multiple availability zones and files can be stored closer to users, thus reducing latency and improving performance.
  * Security: AWS S3 has built-in security mechanisms and is compliant with major industry standards.
  * Cost-Efficiency: AWS S3 offers multiple plans to allow cost optimization based on data access patterns.
  * Performance: AWS S3 ensures fast read and write operations for large amounts of data.
  * Integration complexity: AWS S3 uses REST APIs to integrate with other systems.
  * Disaster Recovery: AWS S3 provides high durability and redundancy.
  * Data integrity/consistency: AWS S3 provides high durability for the stored resumes, ensuring that they are securely stored and accessible when needed. In order to protect against data loss, data is replicated across multiple locations.
   

## Useful links
- [C4 diagram](https://github.com/octaviaah/ClearView/blob/main/2.ArchitectureVisualization/C4Diagram.md)
