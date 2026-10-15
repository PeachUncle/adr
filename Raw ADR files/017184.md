# 0001. Use Firebase

## Date

2023-02-20

## Approved By

@danascheider

## Decision

We will use Firebase to build the new front end, and deploy to Firebase hosting instead of Heroku. The back end will stay on Heroku for now.

## Glossary

- **Firebase:** An [SDK and hosting platform](https://firebase.google.com) for web and mobile apps offered by Google
- **Google Cloud Platform (GCP):** A [suite](https://cloud.google.com/) of cloud services offered by Google; competes with AWS and Microsoft Azure
- **Google Sign-In:** A legacy identity service formerly offered by Google, used by SIM for authentication and recently replaced with Sign in with Google
- **Heroku:** An [app hosting platform](https://heroku.com) on which the SIM back end and legacy front end are deployed\
- **OAuth:** An [authorization protocol](https://oauth.net/2/) underlying most third-party identity services, such as those offered by Google
- **Sign in with Google:** A new [identity service](https://developers.google.com/identity) offered by Google, replacing Google sign-in

## Context

Several challenges have recently converged, pushing us to implement a full rewrite of the SIM front end. Most relevantly to this ADR, Google has deprecated its legacy Google Sign-In API, which SIM was using for authentication, and support for that API ends in March of 2023. Months of research into the new Sign in with Google API and a deep dive into the underlying OAuth 2.0 protocol still left us with doubts about our ability to implement the identity features we required.

Google's Firebase SDK and hosting platform provide an out-of-the-box solution to this problem. Apps that use Firebase are able to easily integrate with Sign in with Google, providing a relatively easy solution to a problem that had been plaguing us for over a year.

## Considerations

In deciding whether to make the change, we considered the following factors:

- Whether we would be able to use React and TypeScript (other tools we've chosen for our tech stack) with Firebase
- Whether we could (or should) deploy a Firebase app to Heroku
- The cost of using Firebase and its hosting services
- Ease of integrating with a Heroku-hosted API (if using Firebase hosting)

### Use of React and TypeScript

Firebase integrates easily with React and TypeScript projects.

### Deployment to Heroku

While it looks like it is possible to deploy a Firebase project to Heroku, hosting it on GCP seemed easiest and provided a suite of deployment tools that wouldn't be available if we hosted elsewhere.

### Cost

Like many cloud providers, Google doesn't make the actual cost of running a Firebase app particularly clear. However, back of the envelope, it appears that Firebase's free tier is fairly generous, whereas Heroku no longer has a free tier at all.

### Integration with a Heroku-Hosted API

While it's possible there would be benefits to hosting both the API and the front end on GCP, Google doesn't appear to do anything that would make integrating with a non-GCP-hosted back end more difficult.

## Summary

Because of its plug-and-play approach to Google identity services, Firebase was a very attractive option for SIM's new front end. Combined with its generous free tier, there seemed little disadvantage in using both its SDK and hosting services.
