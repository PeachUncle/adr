# ADR 2: Adoption of PHP and GoogieHost for Backend Server

**Created By:** Matthew

**Date:** 2024-05-13

**Decision Maker:** Jett, Bernie

**Stakeholders:** Team 10

**Status:** Draft

## Context:
Our application currently relies on AWS for backend server hosting. However, we have encountered significant complexity and persistent errors when deploying and managing the application on AWS. These issues have led to increased development time, higher maintenance efforts, and challenges in ensuring a stable environment. To streamline our backend operations, we need to consider alternative solutions that are easier to manage and maintain.

## Decision:
We are thinking to use PHP as our backend programming language and GoogieHost as our hosting provider. PHP offers simplicity and ease of use for web development, while GoogieHost provides a free, straightforward cloud server solution that meets our hosting needs without the complexities associated with AWS.

## Consequences:
- Reduced Complexity: PHP's ease of use and GoogieHost's user-friendly interface will reduce the complexity of backend development and server management, allowing our team to focus more on application features and improvements.
- Cost Savings: By using GoogieHost, a free cloud hosting provider, we will significantly reduce our hosting costs compared to AWS, providing a cost-effective solution for our backend needs.
- Improved Stability: GoogieHost's simplified hosting environment is expected to offer greater stability, reducing the frequency of deployment errors and runtime issues experienced with AWS.
- Learning Curve: Transitioning to PHP may require some initial learning and adjustment for team members who are not familiar with it. However, PHP's widespread use and extensive documentation should facilitate this process.
- Scalability Considerations: While GoogieHost provides an immediate solution, we need to monitor its scalability and performance as our application grows. Future considerations may include moving to a more robust hosting solution if required.

Overall, adopting PHP and GoogieHost for our backend server aligns with our objective to simplify backend operations, reduce costs, and improve application stability. This decision will enable our team to deliver a more reliable and maintainable application.