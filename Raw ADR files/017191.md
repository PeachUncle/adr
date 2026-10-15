# 0009. Standard DOM Breakpoints

## Date

2023-04-12

## Approved By

@danascheider

## Decision

In developing SIM, we will use the following DOM breakpoints:

- 320px (minimum officially supported device width)
- 480px - 481px
- 600px - 601px
- 768px - 769px
- 1024px - 1025px
- 1200px - 1201px
- 1404px - 1405px (maximum officially supported device width)

All media queries should use these breakpoints unless extenuating circumstances demand a different breakpoint be used for a particular component.

## Glossary

- **DOM Breakpoint:** Also called a "breakpoint", a viewport width at which styles change due to the presence of a media query.
- **DOM Breakpoint:** Also just called "breakpoint", a particular viewport width at which a design changes due to the presence of a media query specifying CSS rules to be applied only to viewports over or under that width.
- **Media Query:** A CSS feature allowing rules to be scoped to specific devices, viewport sizes, orientations, user preferences, or other features.
- **Responsive Design:** A website design that changes at different viewport widths, so it looks good on any browser or device size.

## Context

SIM is a fully responsive site. As such, we use CSS media queries to ensure the styling looks right at any screen size. In order to keep the responsive design under control and avoid total chaos, we want to use standard DOM breakpoints so that elements change size or layout at the same time. This ensures that elements on the page continue to look good together, instead of some aspects of layout or appearance changing at different times, which risks clashing with other elements on the page.

## Considerations

Which breakpoints to use is an open question and there are no clear standards for what viewport widths should be used as breakpoints. The key point is that we want to support four main device types: smartphone, small tablet, large tablet, and desktop. While it would be nice to point to some existing standard, or at least a rationale, for our breakpoint choices, the reality is that the choices were somewhat arbitrary, and our continued use of these breakpoints is at least partly a function of path dependency.

## Summary

Our minimum officially supported viewport width is 320px, and our maximum is 1405px. Your mileage may vary at sizes outside this range. Within this range, our breakpoints are between the following widths:

- 480px and 481px
- 600px and 601px
- 768px and 769px
- 1024px and 1025px
- 1200px and 1201px
- 1404px and 1405px
