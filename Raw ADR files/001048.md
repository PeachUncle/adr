# ADR 003: Use of Flask as the microservice framework
## Context
The purpose of this app is to predict cardiac risk according to the data provided by the patient. The app will use Flask as the microservice framework to handle the backend logic.
## Decision
The decision to use Flask as the microservice framework is based on the following factors:
* Simplicity and ease of use: Flask is a lightweight web framework for Python, making it easy to set up and use for a small team.
* Performance: Flask is known for its good performance and efficiency, handling over 2 million requests per second.
* Scalability: Flask is able to handle thousands of concurrent requests without much effort.
* Integration with other libraries: Flask is compatible with a wide range of libraries, such as SQLAlchemy for ORM and OAuth for authentication.
## Rationale
Using Flask for the cardiac risk prediction app is advantageous due to its simplicity, performance, and scalability. Flask's ease of use and compatibility with other libraries make it an ideal choice for a small team like ours, allowing us to focus on building the app rather than spending time setting up and configuring the framework. Additionally, Flask's good performance and scalability ensure that the app can handle a large number of requests, providing a smooth user experience.
## Status
Accepted
## Consequences
The use of Flask as the microservice framework for the cardiac risk prediction app has the following consequences:
Efficient development: Flask's simplicity and ease of use allow the development team to focus on building the app rather than configuring the framework.
High performance: Flask's good performance ensures that the app can handle a large number of requests, providing a smooth user experience.
Scalability: Flask's UNIX PID model and compatibility with other libraries enable the app to scale well, handling thousands of concurrent requests without much effort.
## Conclusion
Based on the above factors, Flask is an excellent choice for the microservice framework for the cardiac risk prediction app. Its simplicity, performance, and scalability make it an ideal fit for this app, allowing the team to focus on building a high-quality app that provides a smooth user experience.