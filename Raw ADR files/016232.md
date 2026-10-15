---
ID: umd-whpool-0003
Status: Accepted
Date: 2023-08-04
Author: Tim Kanke <tkanke@umd.edu>

---

# CKEditor installation

## Context

We need to decide how to install CKEditor in a way that stuck a balance bewteen ease of development and flexibity to make changes in the future. Our purposes requires a custom CKEditor plugin that adds complications.

## Decision Drivers

* Be easy to modify when future major changes are needed
* Be straightforward to develop

## Considered Options

1. Clone Django-CKEditor-5 in the app static directory, then add custom plugin
2. Clone Django-CKEditor-5 in a similar manner as other Django apps, then add custom plugin
3. Fork Django-CKEditor-5, add custom plugin to the fork, and pip install

## Decision

Chosen option: Clone Django-CKEditor-5 in a similar manner as other Django apps, then add custom plugin, because it provides the easiest setup for dev work. That is it is simplier to make changes to CKEDitor and the custom plugin in one repo then to have two (or three)separate repos. Also, having the CKEditor directory at the same level as the app and project makes it more visible, as well as, easier to update/remove in the future.

## Pros and Cons of the Options

### Clone Django-CKEditor-5 in the app static directory, then add custom plugin

* Good, because it does not require 2 or more repos to be maintained
* Good, because it is easier/faster to modify
* Bad, because it is hiddened in the app directory and causes some issues with project settings
* Bad, because it requires more effort to update Django-CKEditor-5

### Clone Django-CKEditor-5 in a similar manner as other Django apps, then add custom plugin

* Good, because it does not require 2 or more repos to be maintained
* Good, because it is easier/faster to modify
* Bad, because it requires more effort to update Django-CKEditor-5

### Fork Django-CKEditor-5, add custom plugin to the fork, and pip install

* Good, because it requires less effort to update Django-CKEditor-5
* Bad, because it requires 2 or more repos to be maintained
