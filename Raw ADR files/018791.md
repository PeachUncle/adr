# 11. Forms in the Web Widget

Date: 2020-01-06

## Attendees

## Status

Accepted

## Context

A little while ago we decided to use React Final Form as our form library of choice. However when implementing the Support embed form we faced a few issues that has raised the question again about what is the best option moving forward for forms in the Web Widget.

This is the document where we wrote some of our findings https://docs.google.com/document/d/1bX3I3t6FmBoVCgsFGYfkppzx1efVUtmJZlMuI3T5fPc/edit#

## Possible Approaches

### 1. Use React Final Form

#### Pros

##### Not managed by us

Because the library is a popular, open source library we get documentation and updates all for free.

#### Cons

##### Adds 20KB non-gzipped and 7KB gzipped to the bundle

This is the nature of using a library, this is quite large if we were only going to be using it for the Support embed. But we expect to be using it throughout the whole widget, which makes the size easier to accept.

##### Requires us to generate a redundant id

React final form does not allow you to use ids that only contain numbers due to a library they are relying on for accessing nested fields. Because of that we have to create a string id (`key:${id}`) that we use for the form logic.

##### Requires us to generate fields in two locations

For our dynamic forms, we need to know what fields are currently visible in order to correctly validate the form. If a field is currently hidden due to not meeting a condition, then its values shouldn't be validated when the form updates.
React final form makes it impossible to determine which fields are currently visible in only one location due to how the library is set up.

To demonstrate this, here is a greatly simplified version of our implementation of React final form.

```jsx
<ReactFinalForm
  validate={currentValues = validateForm(currentValues)}
>
    {({values}) => (
      {getFieldsToRender(values)}
    )}
</ReactFinalForm>
```

What this means is that for every change, the form will re-calculate the fields at least twice.
I tried adding in memoization, but only managed to reduce it to re-calculate twice instead of three times.

##### Uses render props and context to provide data

Since it provides its values via render props and context, its impossible to keep everything in the one component, since we have to use its values in a child component.
This has resulted in us creating a top level component that just renders out the react final form component and then our own component inside of that.

```jsx
<ReactFinalForm>{props => <OurTicketFormComponent />}</ReactFinalForm>
```

Not a huge deal, but is a little more confusing and a little harder to test. I opted to just add tests for the top level component and test the child one through the top level one.

### 2. Use our own custom implementation

#### Pros

##### We can make it fit what we need

Most form libraries do what react final form does and has the validate function out of reach of the rendering logic. With out own implementation though it is trivial to regenerate the fields to display before the validation logic.

#### Cons

##### We would have to manage it

This is a huge con, hooks are great for simple things but start to get hard to reason about when things get complicated. When writing a POC hook I ran into infinite re-renders multiple times and I'm still not happy with the final result.
Once its done, it shouldn't need to be touched again and should work for other forms in the Web Widget. But

## Decision

Stick with the decision to use react final form. Even though it has its quirks and requires us to work around it, at least it is a well documentation library that covers most use cases.

## Consequences

- For support contact form, we will need to convert field ids to strings, so e.g. id 123 would become "key:123"
- For support contact form, we will need to work out what fields are currently displayed in two locations (validate and render). This might become a performance problem for really large forms. This will need to be something we keep an eye on
