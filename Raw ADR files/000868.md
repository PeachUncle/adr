
# Bet Keeper Data Storage

## Context and problem statement

Bet Keeper data must be persisted in database in cloud environment.

## Decision drivers

- Data must be accessible from deployment location
- It must be free
- There will be some relationship between entities (probably we need relational DB)
- Data access does not have to be real time
- There will be no huge volume of data

## Conidered options

- **Firebase**  
Google solution has no-cost spark plan to handle Cloud Firestore with 1GiB storage and 20K writes/day and 50K reads/day. But this is non relational database. There is also a Cloud SQL Database but it is Paid option.
- **Azure SQL Database**  
Cloud solution for SQL database by Microsoft but it does not have free tier option. There is an option for 12 months of free plan for specific services.
- **Supabase**  
Rock solid PostgreSQL database verified by developers. Simple solution with possibility to migrate data in and out any time. It has dedicated UI with dashboard. It has build in integration to simplify the data management. 
It has unlimited API request with 50,000 MAU (Monthly Active Users) and up to 0.5GB of storage with 5GB transfer and 1GB Blob storage. Free projects are paused after 1 week of inactivity. There is a limit of 2 active projects.
- **Gel (EdgeDB)**  
[Spuercharded postres](https://www.geldata.com/) with modern data model, graph queries and integrated Auth solutions. It is free with up to 1GB of storage and 1/2 GiB RAM and 1/16 vCPU.
- **Neon**  
[Neon](https://neon.tech/) is a postrges database hosted as serverless platform. It is free up to 10 projects with 0.5GB of storage and 190h of compute hours. It does not require credit card.


## Decision Outcome


📆 Date: 15.04.2025

There is a lot of great storage solutions but this project will be realised with **Supabase** because it is a trendy solution for private projects and it will be nice to learn its advantages and disadvantages. It is free and has many free usage credits that with this project will not be consumed. When database will be paused there will be another layer of protection against unwanted traffic and DoS attact. But after a long break of user activity there will be a need to turn on the database instance.


[Back to top](./readme.md)  
[Previous](./00-hosting.md)  
[Next](./02-authentication.md)