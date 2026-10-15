# UI Technolohy Decision

## Context and Problem Statement
With a frontend application things need to be laid out in a neat flow, visually satisfy users, and accessible. CSS is what you use for websites to create UI's, 
however there are frameworks to make it quicker and easier to read and not need 300 lines of CSS and loading these files again and again.

## Descision Drivers
- Need for large CSS files.
- Time spent writing CSS

## Considered Options
- Vanilla CSS
- [Tailwind CSS](https://tailwindcss.com)
- [Bootsrap CSS](https://getbootstrap.com)
- [Materiaize](https://materializecss.com)

## Pros and Cons of Options

### Vanilla Css

#### Pros
- Full Control; No constraints of a framework, freedom to design and strucutre the style of the page.
- Lightweight; No bloat from additional files leading to faster load times.
- Cusotmisable; Create your own components
- No dependancies; No breaking updates or changes from third-party frameworks.
- Lowest level of website UI; You have the control, and understanding of how the the UI is being displayed.

#### Cons
- Time consuming; More time to create complext layouts, more time creating custom components. 
- No pre-built components; No pre-designed components, so you need to style and create components like buttons and modals.
- Consistency; Harder to keep the consistency through different pages.
- Responsiveness; Requires manual design of the responsiveness of the pages, this can cause inconsistency to the responsiveness
  of the UI
- Maintainability; large custom CSS files can be difficult to maintain over time.
- Cross-Browser Issues; you need to make sure your features are available across all platforms.

### [Tailwind CSS](https://tailwindcss.com)

#### Pros
- Utility-First Approach; Allows for inline HTML styling
- Customisation; All utilities are customiseable, no specific design or look to it.
- Small File Size; Removes unused CSS in production builds reducing final file size.
- Responsive Design; Built in mobile-first responsive design, creating complex responsive layouts quickly.

#### Cons
- Verbose HTML; Clutter can be created by numerous utility classes, making the HTML harder to maintain.
- Learning curve; it's a diffrent framework and style of creating a UI, and customising the configuration file
- No pre-built components; You have to build everything from scratch as there are no pre-built components
- Potentially repetitive; styles can repeat across if not careful

### [Bootsrap CSS](https://getbootstrap.com)

#### Pros
- Quick Setup; Easy to get started with, with it's pre-built components and responsive grid system.
- Responsive Design; Mobile-first framework with a 12-column grid system making it simple to create a responsive website.
- Pre-Built Components; Easy to use components, saving on time on common UI elements.
- Cross Browser Compatibility; Handles many cross-browser issues ensuring consistency across different browserss.
- Extensive Documentation; Easy for beginners and experienced developers to use.
- Large Community; Bootstrap has many community, tutorials, plugins and troubleshoots.
- Customisable; Can customisable bootstrap variables, components and styles.

#### Cons
- Bloat; Comes with an intensive library of mnay built-in styles and components, which can lead to larger files sizes if not optimised.
- Design Similarity; Many websites are using default bootstrap so will look extremely similar.
- Overriding Styles; Sometimes to customise bootstrap it leads to an excessive use of ```important``` or writing a lot of custom CSS.
- Learning Curve; If you want to customise anymore, there is the need to learn how to customise it deeper.
- Dependent on JQuery; this isn't ideal as the application will be dependent on it.
- Not utility first; rather than using customisable utility classes, it is just pre-defined components.

### [Materiaize](https://materializecss.com)

#### Pros
- Material Design; offers a clean, modern style.
- Pre-Built Components; Comes with a vartiety of ready to use components.
- Responsive Grid System; Like bootstrap it has a built-in responsive design with a 12-column grid system like bootstrap.
- Mobile-First Design; Optimised for mobile devices.
- JavaScripts Components; Includes interactive Javascript components.
- Consistent UI; Ensures a uniform and consistent style across devices and pages.
- Extensive Documentation; Well-documented easy for all developers to use.

#### Cons 
- Lack of Flexibility; Not much customisation as it follows Google's Material Design principles.
- Bloat; Includes a library of custom components, increasing load times and file sizes.
- Customisation; Challenging customising components.
- Learning Curve; We haven't used it before, so it would take longer to learn.
- JavaScript Dependency; Some components rely hevaily on Materialise's JavaScript.
- Smaller Community; It doesn't have a community like bootstrap but it has a little one.

## Descision Outcome
[Tailwind CSS](https://tailwindcss.com) was the final decision based on it's high customisation, no pre-built components
creating less shared data between the server and client. Responsive mobile first design with it's utilities being responsive
as well creating well optimised and responsive designs. It's also extremely easy to use with it's shorthand and is well
adpated to [SvelteKit](https://kit.svelte.dev).

## Consequences
- 2 others in the group will have to learn, 2 others will have to refresh on it.
- Can lead to repeated use of classes unless we put it in custom utility classes.
- Can spead up development.
- Responsive design.
- Smaller file sizes, with potential increase in file size.
- More cusomisation to the page.

