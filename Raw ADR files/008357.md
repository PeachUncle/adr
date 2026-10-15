# Incorporating Projects Page into Homepage

## Context and Problem Statement

Initially, our Dev Journal application featured a separate Projects page that displayed all current and past projects with titles, descriptions, and GitHub links. However, given our time constraints and the limited number of developers on the team, styling and maintaining this separate page is challenging. We need to decide whether to keep the Projects page or integrate its functionality into the homepage's dashboard.

## Considered Options
* Maintain a separate Projects page
* Integrate the Projects view into the homepage dashboard

## Decision Outcome

**Chosen option**: Integrate the Projects view into the homepage dashboard

### Description of Options

#### Maintain a Separate Projects Page
A dedicated Projects page where users can view all their current and past projects with detailed information, including titles, descriptions, and GitHub links.

**Advantages:**
- Clear segregation of projects, making it easier to manage and view them in detail.
- Can provide a comprehensive overview of all projects in one place.
- Potential for more detailed and tailored features specific to projects.

**Disadvantages:**
- Increased development and maintenance effort.
- Requires significant styling and UI/UX work, which is challenging with our limited resources.
- Adds another layer of navigation, potentially complicating the user experience.

#### Integrate the Projects View into the Homepage Dashboard
Display the projects on the homepage dashboard, combining the overview and detailed view into a single page. The dashboard will include CRUD functionality for managing projects.

**Advantages:**
- Simplifies the application's navigation by reducing the number of pages.
- Easier and faster to implement and maintain, given our resource constraints.
- Provides a unified view of projects along with other essential features on the homepage.
- Reduces the overall complexity and workload for the development team.
- Enhances the user experience by making all necessary information accessible from one place.

**Disadvantages:**
- Potentially less detailed view of projects compared to a dedicated page.
- May require careful design to ensure the dashboard does not become cluttered.

## Decision Outcome

**Chosen option**: Integrate the Projects view into the homepage dashboard

### Reasons for Choosing to Integrate into the Homepage Dashboard

1. **Resource Constraints**: With limited time and a small development team, focusing on a single, comprehensive dashboard is more feasible than maintaining a separate, detailed Projects page.
2. **Simplified Navigation**: Integrating the Projects view into the homepage dashboard streamlines navigation, making the application easier to use.
3. **Unified View**: Users can manage all aspects of their projects from one central location, enhancing usability and accessibility.
4. **Reduced Development Effort**: By consolidating the projects functionality into the homepage, we save significant time and effort on styling and maintaining an additional page.
5. **Priority of Features**: Given that a dedicated Projects page is a "nice to have" rather than a "must have" feature, it is more efficient to integrate its functionality into the homepage dashboard.

We decided that integrating the Projects view into the homepage dashboard is the best option given our current constraints. It aligns with our goal of creating a user-friendly, maintainable application while optimizing our limited resources.