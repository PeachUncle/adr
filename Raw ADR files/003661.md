# External API

## Context and Problem Statement

We need to integrate an external API to fetch movie quotes for our application. 
The API should be simple to use, match our requirements, and preferably be free of charge. 
However, we also need to consider the quality of documentation and the availability of the API.

## Decision Drivers

* Simplicity and ease of use
* Matching our requirements for movie quotes
* Cost-effectiveness (preferably free)
* Quality of documentation
* Availability and reliability

## Considered Options

* Using the Quotable API (https://api.quotable.io/)
* Using the MovieQuotes API (https://moviequotesapi.com/)
* Using the Open Movie Database API (http://www.omdbapi.com/)

## Decision Outcome

Chosen option: "Using the Quotable API (https://api.quotable.io/)", because it matches our requirements for movie quotes, is free of charge, and is simple to use. Although it has poor documentation and no guarantee of availability, these drawbacks are outweighed by its simplicity and cost-effectiveness.

### Consequences

* Good, because the Quotable API is simple to use and matches our requirements for movie quotes.
* Good, because the Quotable API is free of charge, which is cost-effective for our project.
* Bad, because the Quotable API has poor documentation, which may make it more difficult to integrate and troubleshoot.
* Bad, because there is no guarantee of availability for the Quotable API, which may affect the reliability of our application.

### Confirmation

The implementation will be confirmed through comprehensive integration testing to ensure that the Quotable API meets our requirements for movie quotes. Additionally, we will monitor the availability and performance of the API to ensure it meets our standards for reliability.

## Pros and Cons of the Options

### Using the Quotable API (https://api.quotable.io/)

The Quotable API is a simple and free API for fetching movie quotes. It matches our requirements for movie quotes and is cost-effective for our project.

* Good, because the Quotable API is simple to use and matches our requirements for movie quotes.
* Good, because the Quotable API is free of charge, which is cost-effective for our project.
* Neutral, because the Quotable API has poor documentation, which may make it more difficult to integrate and troubleshoot.
* Bad, because there is no guarantee of availability for the Quotable API, which may affect the reliability of our application.

### Using the MovieQuotes API (https://moviequotesapi.com/)

The MovieQuotes API is a dedicated API for fetching movie quotes. It has good documentation and a guarantee of availability, but it may not be as cost-effective as the Quotable API.

* Good, because the MovieQuotes API has good documentation, which makes it easier to integrate and troubleshoot.
* Good, because there is a guarantee of availability for the MovieQuotes API, which ensures the reliability of our application.
* Neutral, because the MovieQuotes API may not be as cost-effective as the Quotable API, which could increase the cost of our project.
* Bad, because the MovieQuotes API may not be as simple to use as the Quotable API, which could slow down development.

### Using the Open Movie Database API (http://www.omdbapi.com/)

The Open Movie Database API is a comprehensive API for fetching movie data, including quotes. It has good documentation and a guarantee of availability, but it may not be as cost-effective or simple to use as the Quotable API.

* Good, because the Open Movie Database API has good documentation, which makes it easier to integrate and troubleshoot.
* Good, because there is a guarantee of availability for the Open Movie Database API, which ensures the reliability of our application.
* Neutral, because the Open Movie Database API may not be as cost-effective as the Quotable API, which could increase the cost of our project.
* Bad, because the Open Movie Database API may not be as simple to use as the Quotable API, which could slow down development.

## More Information

The decision to use the Quotable API is based on its simplicity, cost-effectiveness, and match with our requirements for movie quotes. The implementation will be monitored and reviewed regularly to ensure it meets our standards for reliability and performance. Future revisits to this decision may be necessary if the project requirements change or if new APIs become available.
