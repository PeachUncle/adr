# ADR-0001 CRUD Functionality

Status: Accepted <br>
Date: 2023-05-08 <br>
Deciders: Andrew Onozuka <br>
Consulted: Malcolm McSwain <br>
Informed: Merrick Qiu, Abhimanyu Srivastava, Alex Tahan, Joseph Del Val, Vivin Vinil, Julia Poon, Jacob Felts, Yuantian Zhou, Leo Lee

## Context and Problem Statement

We decided to implent a side bar that allows you to store previous horoscopes from your current session, after talking with our TA Malcolm and receiving feedback that our app needed to be more clear and focused on the CRUD functionality - (Create, Read, Update, and Delete).

## Decision Drivers

* Users would not be able to see horoscopes for previous days, which is an important element of a daily horoscope app
* The existing app did not have full CRUD app functionality

## Considered Options

* Sidebar showing previous horoscopes 
* Login/accounts for individual users to view their horoscopes

## Decision Outcome

Chosen option: "Past horoscopes sidebar", because it more clearly meets the CRUD requirements and would be much more feasible in the given timeframe of the project.


## Pros and Cons of the Options

### Past Horoscopes Sidebar

Like the ChatGPT sidebar, users can view their past horoscope entries.

* Good, because it meets CRUD requirements of the project.
* Good, because the data is stored locally, achieving our desired local first development.
* Good, because users can view their past horoscopes.
* Bad, because anyone using a particular device might be able to see a user's horoscope entries.

### Login/Account system

Users would log in to their account to view their daily horoscopes.

* Good, because it meets CRUD requirements of the project.
* Good, because users can view their own past horoscopes.
* Good, because users can keep their horoscopes private to their account, and access it from multiple devices/locations.
* Neutral, because it likely requires a implementation similar to Option A in order to view past horoscopes.
* Bad, because this feature would likely cause the project to become too complicated for the short time frame, reducing the overall quality of the app. 
* Bad, because when implemented poorly, a login/account system may introduce security issues for user data.

<!-- This is an optional element. Feel free to remove. -->
## More Information

Github issue [#12](https://github.com/cse110-sp23-group5/cse110-sp23-group5/issues/12)  
The login/account system is recorded as a possible future feature of the app.
