# Reliabilty

## Context and Problem Statement
How will we improve our website's reliability by providing offline access? The goal of our project is to build a highly responsive web application that can benefit users. The application should work across various devices and platforms, ensuring a pleasant user experience even with intermittent or no internet connectivity. Given these requirements, we need to choose a technology that best supports these features while maintaining simplicity in deployment and maintenance.  

We are making the decision of selecting the best technology to implement offline capabilities and other background functionalities in our web application. The two primary options under consideration are Service Workers and ElectronJS.

## Considered options:
- Electron JS
- Service Workers

### Summary and Reasoning of Options

#### Electron JS

**Advantages:**  
- ElectronJS allows developers to create applications that run on Windows, macOS, and Linux using a single codebase, which simplifies development and maintenanc
- Developers can use familiar web technologies like HTML, CSS, and JavaScript to build desktop applications, reducing the learning curve for web developers
- Electron provides access to native operating system APIs, allowing developers to create more integrated and feature-rich desktop applications
- There are a lot of resources to learn about ElectronJS


**Disadvantages:**  
- Larger in size
- More resource dependent leading to higher memory and CPU usage which can reduce speed and functionality
- If not properly managed, there can be security risks and web content can be accidentally exploited
- Distributing Electron applications can be more complex compared to web applications, as it involves packaging and signing the app for different operating systems

#### Service Workers

**Advantages:** 
- Everyone in our group has used Service Workers
- We are familiar with it, so it will not take too much time

**Disadvantages:**
-  We are missing out on the opportunity to learn how to use Electron JS
-  Electron JS may have other benficial features
## Decision Outcome:
**Chosen option:** Service Workers
1. **Reliabilty:** We wanted our website to have an added layer of reliability, so we decided to provide online access.
2. **Familiarity:** We as a group are more familiar with service workers as we used it during the lab.
3. **Time:** By using Service Workers instead of Electron JS we save time on familiarizing ourselevs with Electron JS.


