---
status: accepted
date: 2025-05-10 
decision-makers: Whole Group
consulted: Whole Group
informed: Whole Group
---

# {HTML and CSS Validators for Maintaining Code Quality via Tools}

## Context and Problem Statement

 To ensure code quality automatically, it is prevelant to implement HTML and CSS validators as part of our development process. These tools will be useful in identifying clear issues early on. As a result it will mitigate and reduce the risk of errors in production. Additionaly we aim to automate this process using GitHub Actions to integrate validation checks into the CI pipline 


<!-- This is an optional element. Feel free to remove. -->
## Decision Drivers

* improve code reliability and consistency
* enhance developer productivity through early error catching
* ensure compliance with best practuices and standards
* automate the validation process to reduce manual effort and human error
* … <!-- numbers of drivers can vary -->

## Considered Options

* Implement HTML and CSS validators with GitHub Actions
* Manual code review without validators
* Use automated testing tools only
* … <!-- numbers of options can vary -->

## Decision Outcome

Chosen option: "Implement HTML and CSS validators with GitHub Actions}", because it automates the process of code quality checks, ensures adherence to standards, and integrates seamlessly with the CI/CD pipeline, supporting early bug detecting and imporving development efficency"

<!-- This is an optional element. Feel free to remove. -->
### Consequences

* Good, because it automates HTML and CSS validation checks during the development process
* Good, because we save time not having to manually identify trivial errors
* Good, because it ensures we consistently adhere to defined coding standards
* Bad, because it requires time and effort for inital setup and configuration for GitHub actions
* Neutral, because devs will need to address any flagged errors by the validators but ensures cleaner code
* … <!-- numbers of consequences can vary -->

<!-- This is an optional element. Feel free to remove. -->
### Confirmation

The implementation fo HTML and CSS validators with GitHub actions will be confirmed through automated checks in each pull request. We will configure the GitHub actions workflow to trigger validation whenever new code is pushed to the repository. This setup will ensure that code quality checks are automaticallicaly performed and any isssues are reported immediately. Regular reviews of the configuration will ensure that the validators remain aligned with project standards

<!-- This is an optional element. Feel free to remove. -->
## Pros and Cons of the Options

### Implement HTML and CSS validators with GitHub Actions

* Good, because it automates HTML and CSS validation checks during the development process
* Good, because we save time not having to manually identify trivial errors
* Good, because it ensures we consistently adhere to defined coding standards
* Bad, because it requires time and effort for inital setup and configuration for GitHub actions
* Neutral, because devs will need to address any flagged errors by the validators but ensures cleaner code

### Manual Code Review Without Validators

* Good, because we do not have the spend time setting up and automatic validation pipeline
* Good, because we might be able to spot greater errors that these validators miss
* Neutral, because we rely on human inspection which can be subjective
* Bad, because we may miss more subtle errors and consistencies
* Bad, because it consumes more time and effort compared to automatic tooling

### Use automated testing tools only

* Good, because it automates testing process
* Neutral, because it may not cover specific HTML and CSS validation needs
* Bad, because it primarily focuses on functional testing rather than code quality
<!-- This is an optional element. Feel free to remove. -->
## More Information

This decision aligns with industry best practices for maintaining code quality in web development. Integrating the validation process into GitHub Actions will ensure that each developer's contribution is automatically checked, preventing invalid code from being merged. The team will recieve immediate feedback on validation erros, which helps prevent any issues from reaching production.

### GitHub Actions SetUp Overview:
1. Action Setup: We will created a  {.github/workflows/validate.yml} file to define GitHub Actions workflow
2. Validators: We will use open-source tools like [W3 HTML Validation Service](https://validator.w3.org) and [W3 CSS Validation Service](https://jigsaw.w3.org/css-validator/)
3. Trigger: The workflow will be triggered on every push or pull request to the repository to ensure the code validation is automatic
4. Notifications: if erros are found during validation, GitHub actions will report them in the pull request checks, providing immediate feedback.
