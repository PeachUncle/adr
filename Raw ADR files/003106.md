---
title: DemoSetup
date: 2025-04-14
time: 22:00 UTC+1 (UK DST)
attendees: 
- '@kilasuit'
#apologies:
outcome:
- Accepted
- Deferred
- Declined
impactedAreas: 
- Context 
- Demo Planning 
- Documentation
- Marketing
- Future Work
- Notes
- Project Scope
---
<!-- markdownlint-disable MD025 -->
# 002 - 2025-Apr-14 - DemoSetup 

## Status

Accepted 
See more in the Accepted, Declined & Deferred sections

## Context

There was a need to rework the repo, in order to get things ready for demoing at the PowerShell Community call on April 17th 2025.
This needed to include a number of items including docs like these and introducing IIN's

## Decision

### Decided by

@kilasuit - Ryan Yates

### Accepted

The following were accepted

#### Documentation 

What documents we are including in this first pass release.
In future to spend time in authoring these via vscode speech ext / Dictation built into Windows 

#### Project Scope

This project will only have items relating to all things that you may want to run within your PowerShell Profiles, and serves as living research for multi-device & multi-platform use of PowerShell Profiles.

As such it will make use of project tracking tooling to make this more useful in future.

The end goal of this project is to show different and useful items & discuss 

#### Demo Setup

We are going to try and make use of the [VsCode DemoTime extension](https://demotime.elio.dev/) to keep the demo on track, depending on time to integrate this.

This may end up being setup and deferred for a future demo


#### Used Technologies

As per last ADR



#### Long term plans - Post initial release

- [] - Build compiled scripts as a repo artifact
    - [] - Have these signed in the build process
    - [] - Have the build process be able to be run locally
- [] - Publish as a module (Maybe)

 

#### Project Marketing Plan

Talk about it in the PowerShell Discord
Show it at the Community Call on April 17th & as part of it ,ake the repo public during the call using GH Cli 
Post about it to Bsky, Twitter (X), LinkedIn, Mastadon & add a blog post about this after the community call.
Potentially publish about it on Reddit & PowerShell.org & also to PowerShell.org.uk once I release the new version of that site too. 


### Contributing

We will accept the following contributions

- Minor Spellings as long as they are in EN-GB
- Any PR's of [IIN's](https://github.com/kilasuit/InitialInteractionNotes) into the Docs/IINs folder in this repo
- Alternatively, IIN's can be added as a PR into the https://GitHub.com/kilasuit/IINs/ project under the public-projects/PSProfile folder
- Issues around any suggested code changes

### Declined

Declined accepting major code change PR's at this time, however any issues that are raised may be met with "Could you please raise a PR for this"

### Deferred

When & how we will work on a build script to output combined scripts
When to add tests for this that aren't mental "I do or should test this"
When & how we may publish this as a Module in the Gallery
When & how we may add a Profile Configuration Object that can control how the parts of a profile get loaded
and when/if they are invoked automatically for us, are invoked in the background, or are delayed for either a set time, 
or until you choose to invoke them, allowing a different "start from Minimal Profile and work up"

When to look into the work needed to add -profileScript as a new cmdline option so that we can in future bypass loading of the profile scripts
from the hardcoded locations & only run a single script which was a recommended potential when I raised about the addition of a -minprofile option

### Notes

This will in time be publish and linked to my [public ORCiD profile](https://orcid.org/0009-0009-6030-3517) and will allow for [blog posts](https://blog.kilasuit.org) as well as a number of future presentations on this wider topic.
