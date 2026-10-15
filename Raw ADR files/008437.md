# ADR2: Implementation of Collector Features and Card-Grid Style 

## Date: May 22th, 2025. (ADR Was not created until just now due to personal issues. Apologies for the delay.)

## Context
With our MVP (Minimum Viable Product) being complete and having all of our professor data obtained, we have officially agreed on moving forward with implementing features in relation to the "card collecting" aspect of the project. These include implementing features for increased user engagement and updating our current components to provide better usability and accessibility to the users.

## Decisions

### Implementing Collector Features
With the MVP completed, we have decided to move forward with implementing collector related featues for our project. These include:
- Adding card rarities: Cards will have different types of rarities to increase quantity of cards and add engagement
- A Shop Page: A shop page that allows user to acquire cards wtih a custom currency for the page
- Clicker Minigame: Creating a "Cookie-Clicker" type minigame in which you obtain more currency to be used on cards.
- Wallet System: Users will have a custom currency that will be stored and tracked in order to obtain cards.

### Card-Grid

Our MVP of the project had a card-deck style showcase of the collected cards, letting you go left or right. However, in order to make the obtained cards more accessible and to improve our UI Golf, we have decided to implement a Card-Grid system instead:
- User Accessibility: User will be able to see all cards at once, as opposed to flipping through them one by one.
- Scalability: The grid can scale much more efficiently as more cards are obtained, as opposed to the card deck style we originally had.
The grid will initially be implmeneted and accessed alongside the existing card-deck, but for the final project, it will completely replace the card-deck in the end.

### Project Hosting

With the help of Ali, we decided to host our project using HerokuApp:
- Github Integration: Heroku's Github integration allows for easy and automatic deployment from our repo, especially when it comes to making new changes and pushing them to our branch.
- Simple and Efficient: Heroku provides a faster and easier method of deployment of our project and no setup involved, making it run faster than it was running locally or through Github Pages.

## Final Note
These are all of the major team decisions that have been made in regards to the scale and context of our project moving forward. Once all features have been implemented, or implemented to the point of working efficiently for our scope, the team will move forward in either polishing those features, or implementing the flashcards idea as well, regarding the status of the assginments after this sprint.
