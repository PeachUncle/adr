# 9. Global Styles

Date: 2019-08-20

## Attendees

- Lucas Hills
- Briana Coppard
- David Allen
- Wayne See
- Daniel Bradford
- Alex Robinson
- Levi Serebryanski
- Adrian Yong

## Status

Pending

## Context

Determining and applying color in the Web Widget is very complex at the moment. Once we determine the root colour object from our complex selector chain, we supply it to our `Frame` component. The `Frame` component will then generate the relevant color CSS code by calling `generateUser{WebWidget/Launcher}` (function located in `src/util/color/styles.js`) when it is mounted or whenever the root colour object prop changes. Once the CSS is generated, it is passed into `EmbedWrapper` which will simply render the CSS (globally inside the hosted `iFrame`).

We need a way to get the values we set in the color mixer such as `u-userHighlightColour` inside the components. Right now we are composing global CSS classes but we want to stop composing from globals. This ADR aims to select an appropriate method of handling colour CSS code and not how to manage our colour selectors.

## Possible Approaches

### 1. CSS Modules

Right now we handle global colours using CSS Modules. We inject a style tag into the iframe containing all the mixed colours and then compose them from global in all the files we need the colour in.

Unfortunately there isn't really a better way to handle dynamic variables with CSS modules. Many solutions involve doing something similar and to us composing from global state. The only other solution was to use post-CSS-loader to inject values into CSS files at build time, however this won't work for us as we don't know the values until runtime.

### 2. Styled components

#### Context

When deciding how we will handle globals, I think it is important to also consider how we are handling styles in general.

I believe these are the problems we currently face

- Have to manually concatenate all files, to manually inject into the dom
- Unable to access CSS variables in JS, leading to some duplication of variables
- More than one way to style components
  - global styles
  - CSS modules
  - styled components for Garden components
- Unable to dynamically load in CSS - important for when we start lazy loading components in the web widget

#### Proposal

styled-components I believe solves all of these solutions, for the most part in an elegant way, therefore I propose that we completely move to styled-components to handle all css in the web widget.

#### Helpful Links

- [styled-components](https://www.styled-components.com/)
- [Garden's ADR for CSS in js](https://github.com/zendesk/techmenu/blob/master/content/adrs/garden-CSS-in-js.md)
- [Garden's PR for ADR for CSS in js](https://github.com/zendesk/techmenu/pull/184)

#### Pros

##### No longer need to manually import styles

Since styled components handles injecting the styles for us, we no longer need to concatenate all of our styles together to manually inject into the dom.

This will also benefit us when it comes to dynamically importing components, since all of our styles will be dynamically imported as well.

##### Use same styling package as Garden

Although we shouldn't always aim to be consistent with Garden and should make our own decisions for whats best for the team. Using the same package for styling that Garden uses comes with a few benefits.

- Only one library used for styling, since we sometimes need to customise Garden components (at the moment we have two, CSS modules and styled components)
- Since we do have to customise Garden components, it will be done with a tool we will be comfortable with, rather than something we only touch sometimes
- Garden can assist with usage of `styled-components` ([and are happy to](https://zendesk.slack.com/archives/C0AANB3HS/p1565588767085700?thread_ts=1565588127.083400&cid=C0AANB3HS))

##### Variables are accessible in JavaScript

Although this isn't supported directly by the library, we can create a simple custom hook to access theme variables in our components

https://github.com/styled-components/styled-components/issues/2340#issuecomment-485527921

This means we won't have to worry about some variables being in CSS and some being in js when it comes to styling and theming components.

##### Cleaner components

Styled components in my opinion makes our non-style components far cleaner and gives each one semantic meaning.

For example

```jsx
const Container = styled.div`
  padding: 10px;
`;
const Header = styled.h1`
  color: blue;
`;
const Image = styled.img`
  border: 1px solid black;
  height: ${props => {
    switch (props.size) {
      case 'large':
        return 500;
      case 'small':
        return 100;
      default:
        return 250;
    }
  }}px;
`;

const Example = ({ size }) => {
  return (
    <Container>
      <Header>Some header</Header>

      <Image src="funnt-cat-picture.png" size={size} />
    </Container>
  );
};
```

VS

```CSS
.container {
  padding: 10px;
}

.header {
  color: blue;
}

.image {
  border: 1px solid black;
  height: 250px;
}

.imageLarge {
  height: 500px;
}

.imageSmall {
  height: 250px;
}
```

```jsx
const Example = () => {
  return (
    <div className={styles.container}>
      <h1 className-={styles.header}>Some header</h1>
      <img
        src="funnt-cat-picture.png"
        className={classNames(styles.image, {
          [styles.imageLarge]: props.size === 'large',
          [styles.imageSmall]: props.size === 'small'
        })}
      />
    </div>
  );
};
```

#### Cons

##### Upgrade to v4 (optional)

At the moment we are on version 3 of styled components. The newer versions of Garden have a dependency on version 4.

Although not much has changed between the two versions, it might be worth considering upgrading garden packages and moving to version 4 before we start using it ourselves, to avoid accumulating tech debt.

##### It's a little bit ugly

When it comes to advanced styles that might have a few conditionals around it, the template literal can get quite hard to read.

E.g.

```jsx
const Example = styled.div`
  padding: ${props => {
    if (props.small) {
      return 5;
    }

    if (props.large) {
      return 20;
    }

    return 10;
  }}px;
`;
```

A simple solution could be to extract this out

```jsx
const padding = props => {
  if (props.small) {
    return 5;
  }

  if (props.large) {
    return 20;
  }

  return 10;
};

const Example = styled.div`
  padding: ${padding}px;
`;
```

But this might take time to find what feels right.

## Decision

We will use `styled-components` for all CSS inside the Web Widget going forward. This means that we will replace all sass `.scss` files as we migrate them across into their new `src/embeds` location.

The migration path will roughly look like:

1. Add information to the `GUIDELINES.md` for a simple outline of how to use `styled-components` in the repo
2. Setup a `styled-components` `ThemeProvider` to provide global variables at the top of the app
3. Migrate the `Talk` embed over to use `styled-components` for styling
4. All future components that are migrated into the `src/embeds` directory must use `styled-components` for **all** styles going forward.

## Consequences

- We will be using an outdated version of `styled-components` initially
- As no one in the team has experience using `styled-components` we expect there to be regular updates to the `GUIDELINES.md` as we get comfortable with the library
