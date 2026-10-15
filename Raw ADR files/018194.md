### 1. Title
**002 : Managing Forms**

### 2. Context
The goal of the forms in the application is to collect data entered by the users. Various types of forms will be used, including contact forms, user data forms, authentication forms, account creation forms, and address entry forms. The forms must be easy to set up and should support real-time validation as well as validation upon submission.

The current architecture of the application is a monolithic Nuxt application. For managing forms on the front-end, the Formkit framework is being considered.

### 3. Decision
We have decided to manage forms on the Nuxt side to take advantage of real-time validation.

### 4. Options Considered
1. **Managing forms within the Sylius application, consumed by the Nuxt application via an API, with validation handled on the Sylius side**
2. **Managing forms on the Nuxt side, with validation handled on the Nuxt side**

### 5. Justification
**Managing forms within the Sylius application** :
- *Advantages* :
  - Utilization of existing Sylius features for form management.
  - Centralized validation on the Sylius side.
- *Disadvantages* :
  - Increased complexity due to communication between two applications.
  - Less flexibility for customizing forms on the Nuxt side.

**Managing forms on the Nuxt side** :
- *Advantages* :
  - Flexibility to customize forms on the Nuxt side.
  - Real-time validation on the Nuxt side.
- *Disadvantages* :
  - Requires specific setup and management of forms on the Nuxt side.

### 6. Consequences
- **Performance** : Managing forms on the Nuxt side may improve performance by reducing reliance on network requests.
- **Maintenance** : Maintenance could be simplified with centralized form management on the Nuxt side.
- **Development** : Development will be more flexible with form customization on the Nuxt side. Additionally, this will require learning a new way of generating forms and validating data, using the Formkit framework for form generation and validation with Zod.

### 7. Status
Accepted

### 8. Date
May 4, 2024