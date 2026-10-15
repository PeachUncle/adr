# 2. Terraform folder structure

Date: 2022-10-11

## Status

Accepted

## Context

We need to define a model that meets good Infrastructure as Code development practices.

## Decision

The defined model is following some premises that are important to be clarified:

```
📦terraform (1)
 ┣ 📂.devcontainer (2)
 ┃ ┣ 📂library-scripts
 ┃ ┃ ┣ 📜azcli-debian.sh
 ┃ ┃ ┣ 📜common-debian.sh
 ┃ ┃ ┣ 📜docker-debian.sh
 ┃ ┃ ┣ 📜node-debian.sh
 ┃ ┃ ┗ 📜terraform-debian.sh
 ┃ ┣ 📜Dockerfile
 ┃ ┣ 📜devcontainer.env
 ┃ ┗ 📜devcontainer.json
 ┣ 📂 assets (3)
 ┃ ┣ 📂 images
 ┣ 📂cicd (4)
 ┃ ┣ 📂stages
 ┃ ┃ ┣ 📜stages-cd.yml
 ┃ ┃ ┗ 📜stages-ci.yml
 ┃ ┣ 📜cd.yml
 ┃ ┗ 📜ci.yml
 ┣ 📂modules (5)
 ┣ 📂stacks (6)
 ┃ ┣ 📂env (6.1)
 ┃ ┃ ┣ 📜dev.tfvars
 ┃ ┃ ┣ 📜prd.tfvars
 ┃ ┃ ┗ 📜qa.tfvars
 ┃ ┗ 📂stack1 (6.2)
 ┃ ┃ ┣ 📜locals.tf
 ┃ ┃ ┣ 📜main.tf
 ┃ ┃ ┣ 📜outputs.tf
 ┃ ┃ ┣ 📜providers.tf
 ┃ ┃ ┗ 📜variables.tf
 ┃ ┃ ┗ 📜versions.tf
 ┣ 📂templates (7)
 ┃ ┗ 📜.tf-docs-readme.yml
 ┣ 📜.gitignore
 ┣ 📜Makefile 
 ┗ 📜README.md
```

### 1. terraform
This folder will contain all the documents related to Terraform.

### 2. .devcontainer

To learn more about this feature, access the link [VsCode Dev Container](https://code.visualstudio.com/docs/remote/create-dev-container)

This repository has a DevContainer definition that allows the same experience for the development tools used:
- Terraform `[1.3.2]`
- TFLint `[0.41.0]`
- AZ Cli `[latest]`
- Terraform-docs `[0.16.0]`

> Note: The use of Dev Container is not mandatory

Extension:

If you want to use it, you must have the following extension installed in Visual Studio Code, in addition to having [**Docker**](https://docs.docker.com/get-docker/).

[Remote Containers Extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

### 3. assets

This folder will contain all the images related to the project.

### 4. cicd
It contains the `.yml` file structure that will be responsible for the CI and CD stages of the environment.

### 5. modules
It contains the generalized construction of the components to be provisioned. All the codes for creating the Infrastructure as Code will be provisioned by recycling the modules contained here. More information about how modules work in Terraform can be found [**by clicking this link**](https://www.terraform.io/docs/language/modules/develop/index.html).

### 6. stacks
Here we will present the folder structure that will be used to effectively create the environment.

#### 6.1 env
The `env` folder will contain files with environment variables in this model:
- `dev.tfvars`
- `prd.tfvars`

These files will be consulted on demand through the deployment pipeline.

#### 6.2 stack1
Stacks are organizational structures that contain the business logic used to build the environment. Here, there may be 1 or more directories, each specifying an independent organizational structure.

> Do not confuse the **stack** directory with **env**

### 7. templates
Here, all reference templates used for the entire environment are stored. Here, we will have the freedom to create subdirectories that contain the necessary template files to avoid repeating references.

## Consequences

By maintaining a centralized and standardized usage model, development becomes much more structured and clear. If a new team takes over the development of the infrastructure, they will clearly know the purpose of each of the important directories of this project.