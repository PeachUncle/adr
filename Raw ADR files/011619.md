# Image Processing for Long Term Exposure

|          |                                                                                                      |
| -------- | ---------------------------------------------------------------------------------------------------- |
| status   | accepted |
| date     | 2024-04-27                                                      |
| deciders | [Joshua Gawenda](https://github.com/gutentag2012)                                                    |

## Context and Problem Statement

After the frames of a video have been extracted, they have to be processed and combined into a single output image that shows the long term exposure.

## Decision Drivers

* How long does it take to implement?
* How easy is it to integrate into the application?
* Can this be deployed?
* How performant is it?

## Considered Options

* Imagemagick
* Custom solution

## Decision Outcome

Chosen option: "Custom solution", because image processing is part of a lot of programming languages and can be done without a lot of effort, furthermore this reduces the depdencies of this project.

### Consequences

* Good, because the image processing unit can be integrated without any external dependencies
* Good, because performance can be controlled through the custom implemenetation
* Bad, because this solution has to be maintained

## Pros and Cons of the Options

### Imagemagick

Is an open source tool for image manipulation with various features.

* Good, because it supports the required feature of blending images together with a mean blend mode
* Neutral, because its documentation is not easy to understand
* Neutral, because has to be shipped as a separate binary
* Neutral, because is limited to the implemented features and configuration options
* Bad, because a custom binary was not found, just an installation script
* Bad, because it is not very performant

### Custom Solution

This option wants to create a custom solution that reads images from a folder and creates a new output image based on those.

* Good, because it is fine tuned to the desired operations
* Good, because it can be optimized for performance
* Good, because new features can be implemented as needed
* Neutral, because it can be easily shipped with the application
* Neutral, because it can be debugged if errors occur
* Neutral, because it is a common use case to do image processing and a lot of resources are available
* Bad, because it has to be maintained with the rest of the application
