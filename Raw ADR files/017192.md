# 0010. Mobile-First Development

## Date

2023-04-12

## Approved By

@danascheider

## Decision

We will build the application using a mobile-first approach.

## Glossary

- **Aspect Ratio:** In graphic design, printing, and photography, the ratio between the width and height of an image or element, expressed as two numbers, with units, separated by an x (e.g., 390px x 844px); a ratio (e.g., 1:3); a fraction (e.g., 4/3); or a decimal (0.75). The standard is for the first number, or numerator, to be the width of the device, with height as the denominator. Like with all ratios, units cancel out - an aspect ratio of 4:3 maintains the value of 4:3 whether measured in pixels, em, rem, or other units.
- **DOM Breakpoint:** Also just called "breakpoint", a particular viewport width at which a design changes due to the presence of a media query specifying CSS rules to be applied only to viewports over or under that width.
- **Landscape Mode:** A "sideways" device orientation where the viewport is wider than it is tall.
- **Media Query:** A CSS feature allowing rules to be scoped to specific devices, viewport sizes, orientations, user preferences, or other features.
- **Mobile-First Development:** An approach to front-end development where pages and components are styled for mobile devices and media queries are used to modify the designs for larger viewports.
- **Portrait Mode:** A "right-side-up" device orientation where the viewport is taller than it is wide.
- **Viewport:** In web development, refers to the rectangular area currently visible on a device screen. Viewport width is commonly used to identify whether a user is using a smartphone or PDA as opposed to a tablet or desktop computer.

## Context

More and more users use smartphones as their primary means of accessing the Internet. According to [Perficient](https://www.perficient.com/insights/research-hub/mobile-vs-desktop-usage), in 2020, almost 70% of website visits came from mobile devices, compared to only 35.7% on desktop. Tablets accounted for the fewest visits, at under 4%. For this reason, optimising sites with mobile foremost in mind is logical.

One hallmark of mobile-first development is using media queries with a `min-width` instead of a `max-width`. This makes smaller viewports the default. For example, in this CSS code, the device viewport is presumed to be larger than 480px unless the media query dictates otherwise:

```css
.content {
  display: flex;
  flex-direction: row;
}

@media (max-width: 480px) {
  .content {
    flex-direction: column;
  }
}
```

In this CSS code, on the other hand, the device is presumed to be small and the media query kicks in on wider screens:

```css
.content {
  display: flex;
  flex-direction: column;
}

@media (min-width: 481px) {
  .content {
    flex-direction: row;
  }
}
```

While these CSS rules achieve the same thing, only the second would be considered mobile-first.

## Considerations

Statistics aside, it's important to make an educated guess about how users of one particular website are likely to consume it. Some websites continue to attract more desktop users, while others are almost exclusively mobile. In the case of SIM, users will be using the application while playing a video game. Skyrim is available for both PC and console. PC users may use the desktop version on their PCs alongside their game window(s). However, our primary users are likely to be console gamers. Having a laptop open while using a gaming console is inconvenient, so we expect these users to want to use their phones or tablets to access the site.

Another consideration is device orientation. Having a device in portrait vs. landscape mode affects the screen width as well as the aspect ratio of the device. For example, a device in landscape mode is wider than it is tall, meaning the top bar takes up more of the viewport than it would in a portrait orientation, which is taller than it is wide. We anticipate most users using smartphones in portrait mode, while tablets may be in portrait or landscape mode. Desktops are always landscape unless the user has resized the browser to not take up the full screen. We expect the use of smartphones in landscape mode to be much less common, owing to the small amount of content that will fit on the page in landscape mode. In light of this, we want to optimise the site in with the following priorities:

1. Smartphone - portrait
2. Tablet - portrait
3. Tablet - landscape
4. Desktop - landscape
5. Smartphone - landscape

### Why Standardise Approaches?

The reader may be wondering, if the two CSS examples given under "Context", above, produce identical results, why it's important to stick to a single approach (i.e., mobile-first over desktop-first). The answer to this is twofold.

First, in the most practical sense, consistency produces the most robust code and is less prone to bugs. Having a mixture of `min-width` and `max-width` media queries sets developers up for complex CSS rules that are likely to interfere with one another, causing issues that are often quite visible to users. While there are certain exceptions that can justify using a mixture of approaches, including one that [already exists](https://github.com/danascheider/skyrim_inventory_management_frontend/blob/a40f9e3558d2d769ec9efb5f469cee57916ffa3b/src/layouts/dashboardLayout/dashboardLayout.module.css#L45-L58) in SIM code, in general, it's best to use only one type of media query. (Note that the linked example includes a comment explaining why it was necessary to use `max-width` in this case.)

The second reason is the mentality that these different approaches encourage in developers. A desktop-first approach encourages developers to think of desktop viewports as the "base case", while tablet and mobile viewports are an aberration or afterthought. Mobile-first development has the opposite effect, since the base design is for mobile, and tablet and desktop designs are implemented as variations on the mobile design.

Note that SIM developers should also use [standard DOM breakpoints](./0009-standard-dom-breakpoints.md) to ensure smooth transitioning between different viewport widths. Like with other rules established in ADRs, there is some flexibility here if an element absolutely needs to change at a point that isn't one of our standard breakpoints.

## Summary

Because our users will primarily be using SIM on mobile devices, we will tailor our development approach to cater to these device widths first and foremost. This means using a mobile-first approach, entailing that all media queries, barring rare exceptions, should use `min-width` instead of `max-width`.
