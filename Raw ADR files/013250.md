# ADR 0002: Access Method for External Git Repositories

## Status

Accepted

## Context

Following ADR 0001, OpsCore requires read access to external private GitLab and GitHub repositories to fetch operational procedure Markdown documents. A secure, reliable, and manageable method is needed to authenticate and authorize OpsCore's access to these repositories.

## Decision

We propose the following methods for OpsCore to access external repositories, offering flexibility and security:

1. **Primary Method: Access Keys (Deploy Keys / Fine-grained PATs)**
    * **GitLab:** Utilize **Deploy Keys** with read-only access (`read_repository`). These keys are specific to a single repository, providing granular access control.
    * **GitHub:** Utilize **Deploy Keys** with read-only access or **Fine-grained Personal Access Tokens (PATs)**. Fine-grained PATs are preferred over classic PATs as they allow scoping permissions strictly to repository contents (read-only) for selected repositories.
    * **Permissions:** While read-only access (`read_repository` on GitLab, `contents:read` on GitHub) is the minimum requirement for fetching documents, granting write access (`write_repository` on GitLab, `contents:write` on GitHub) can be considered for future enhancements, such as allowing OpsCore to directly modify procedure documents.
    * **Configuration:** OpsCore administrators will configure the necessary keys/tokens within the OpsCore system for each target repository or organization. Secure storage and handling of these credentials within OpsCore are paramount.

2. **Alternative/Recommended Method: Application-based Access (GitHub App / GitLab Application)**
    * **Concept:** OpsCore can be registered as a **GitHub App** or a **GitLab Application**. Repository owners/administrators would then install/authorize this application on their specific repositories or organizations, granting it the necessary read-only permissions.
    * **Advantages:** This method offers superior security and manageability:
        * **Granular Permissions:** Permissions are explicitly granted by the user during installation/authorization, adhering to the principle of least privilege.
        * **Centralized Management:** Access control is managed through the Git platform's application interface.
        * **No Manual Key Handling (for users):** Users don't need to generate or share keys directly with OpsCore.
        * **Enhanced Auditability:** Actions performed by the application are typically logged more clearly.
    * **Implementation:** This requires OpsCore to implement the necessary OAuth flows or installation handling logic for GitHub Apps/GitLab Applications.

3. **Phased Approach:**
    * **Initially,** OpsCore will primarily support the **Access Key method** (Deploy Keys and Fine-grained PATs) due to its simpler initial implementation for both OpsCore and potentially for users setting up individual repositories.
    * **The Application-based method** is the recommended long-term solution. Development effort should be allocated to support this method, and users should be encouraged to migrate to it once available for enhanced security and manageability.

## Consequences

* **Pros:**
  * **Access Keys:** Relatively straightforward for users to generate for a single repository; simpler initial implementation for OpsCore.
  * **Application Method:** More secure (least privilege, no user key sharing); easier credential management (rotation/revocation handled by the platform/app); better audit trails; centralized control for organizations.
* **Cons:**
  * **Access Keys:** Requires secure storage and management of keys within OpsCore; potential for keys to have overly broad permissions if not carefully created (especially classic PATs); users need to manage key lifecycle (rotation, revocation).
  * **Application Method:** More complex initial implementation for OpsCore (OAuth flows, app registration); potentially slightly more complex setup for users the first time they authorize the application.
