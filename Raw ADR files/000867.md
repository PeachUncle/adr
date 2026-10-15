
# Bet Keeper Hosting

## Context and problem statement

Based on the requirements and expected useage there is a need to define where the application will be hosted.

## Decision drivers

- It must be available through Internet connection
- It must be free
- There should be 'server' layer to hide confidential configuration data (connection to DB and auth provider)
- Application will be probably running in node.js environment

## Conidered options

- **GitHub pages**  
Great for SinglePageApplications without any external integrations because WebApps expose API_KEYS and other confidential strings
- **Vercel**  
Great integration with GitHub and easy deployment process.  Wide range of supported frameworks. Free for personal projects with Web Application Firewall, DDoS mitigation and trafic insights.
- **Heroku**  
Cloud plaform for deploying and scaling apps. Supported many languages.  
Unfortunately only paid option
- **AWS**  
This provider offers multiple free tier solutions and for example there are AWS Lamba free package with 1 Milion of free request per month and also 25 GB of SQL database storage. But it does not support Node.js project hosting deployment.
- **GCP**  
Offers Compute Engine that has limited deployment locations (focused on US). Offers also Google App Engine that can host Node.js environments. There is also cloud run such as AWS Lambda. This has disadvantage that it is more complicated and requires checking if traffic does not reach the end of free package.

- **Azure**  
Microsoft also offer a similar solutions but has Azure App Servie that offer cloud platform to create and run web applications to host servers. But it has only 60 minutes of CPU work per day to be free. There is also a Static Web Apps but it does not offer any backend integration.

## Decision Outcome

📆 Date: 08.04.2025

From all hosting services the easiest to maintain and the completly safe regarding to availablitiy and pricng is **Vercel**.


[Back to top](./readme.md)  
[Next](./01-storage.md)