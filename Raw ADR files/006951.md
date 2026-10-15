# Architectural Decision Record (ADR)
## Hardware

### Context
We are designing the architecture of our expense tracking app, which involves capturing and managing expense-related data, including spending location, receipts, authentication, and media file access.

### Decision
We have decided to include the following hardware components in our app:
1. GPS (Global Positioning System):
	* Use Case: GPS will be used to capture the spending location when users record their expenses.
	* Benefits: Provides location context to expense entries, enhancing expense tracking and analysis.
	* Considerations: We acknowledge that the use of GPS can impact device battery life and may lead to user concerns about privacy, as location data is sensitive.
2. Camera:
	* Use Case: The camera feature will allow users to take pictures of receipts and attach them to their expense entries.
	* Benefits: Simplifies expense tracking by enabling users to capture and store images of receipts, providing visual proof of transactions.
	* Considerations: The camera feature may consume significant storage space and potentially slow down devices with limited resources.
3. Fingerprint Sensor:
	* Use Case: The fingerprint sensor will enable quick and secure user authentication for accessing the app.
	* Benefits: Enhances user convenience by providing a secure and efficient authentication method.
	* Considerations: Some devices may not have a fingerprint sensor, leading to authentication disparities between users with and without this hardware feature.
4. Media File Access:
	* Use Case: Access to media files is required for users to import pictures, including receipts and other images.
	* Benefits: Enables users to attach media files to their expense entries, making expense tracking more comprehensive.
	* Considerations: Requesting media file access permissions may raise privacy concerns among users, and managing imported media files may consume additional storage space.

### Consequences
	* Battery Drain and Privacy Concerns: The use of GPS for spending location may lead to increased battery consumption and user concerns about data privacy.
	* Storage and Performance Impact: Camera functionality may result in significant storage usage and potentially impact app performance on resource-constrained devices.
	* Authentication Disparities: Relying on a fingerprint sensor for authentication can exclude users with devices lacking this feature.
	* Privacy Considerations: Requesting media file access permissions may lead to privacy concerns, and managing imported media files may add complexity and resource usage to the app.

### Considered Alternatives
We considered alternative hardware components, such as microphone for voice input, but concluded that GPS, camera, fingerprint sensor, and media file access are the most relevant and beneficial for the app's core functionality and user experience.

### Summary
The decision to incorporate GPS, camera, fingerprint sensor, and media file access as hardware components in our expense tracking app was made while acknowledging potential negative consequences, including battery drain, storage usage, authentication disparities, and privacy concerns. These concerns will need to be addressed during the development process to ensure a balanced user experience.