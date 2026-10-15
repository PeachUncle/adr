# OSDOP-237: Case events rendering

* Status: APPROVED
* Approved by: Dan Ashworth, Chris Tasker, Danny Betts

## Context and problem statement

We need a way to display the following stored information:

- Event type
- Event date
- Added by
- Nomination version
- Comment
- Files uploaded

The scope of this document will be to continue from the [previous document](0004-case-events-functionality.md)
to determine the most suitable method for displaying case events.

## Case events rendering

### Option 1: Multi-macro

**Note:** This approach removes the need for prompt overrides to be included in
the [functionality implementations](0004-case-events-functionality.md).

One potential method of rendering case events could be to have a base macro of the following:

```injectedfreemarker
<#macro _baseCaseEvent displayableCaseEvent dateSubmittedPrompt="Date submitted" ...>
    <@fdsTimeline.timelineSection sectionHeading=displayableCaseEvent.type.displayText>
        <@fdsTimeline.timelineEvent>
            <@fdsDataItems.dataItem>
                <@fdsDataItems.dataValues key=dateSubmittedPrompt value=displayableCaseEvent.dateSubmitted/>
                ...
            </@fdsDataItems.dataItem>
        </@fdsTimeline.timelineEvent>
    </@fdsTimeline.timelineSection>
</#macro>
```

Any implementations could then wrap this base macro with their own implementations:

```injectedfreemarker
<#macro _nominationDecisionEvent displayableCaseEvent>
    <@_caseEvent displayableCaseEvent=displayableCaseEvent dateSubmittedPrompt="Decision date"/>
</#macro>
```

We'd then have a final wrapping macro that determines which macro to use based on the case event:

```injectedfreemarker
<#macro caseEvent displayableCaseEvent>
    <#if displayableCaseEvent.type.name == "NOMINATION_DECISION">
        <@_nominationDecisionEvent displayableCaseEvent=displayableCaseEvent/>
    ...
    </#if>
</#macro>
```

#### Positives

- Each case event display can be updated independently
- No need for the [functionality implementations](0004-case-events-functionality.md) to include prompt override values
- Updates adding additional items wouldn't need to be cascaded back to macros that wouldn't need them assuming defaults
  are provided

#### Negatives

- Verbose - Could result in a lot of macros. If any types get renamed then they'd need to be cascaded down to prevent
  confusion.
    - Mitigated in annoyance slightly having the overall wrapper to determine which to call. This means it would only
      need updating in two places (macro definition and wrapper)
    - Renames are usually handled fine with IntelliJ refactoring
- Prompts aren't testable and rely on manually checking the screen to ensure changes are accurate

### Option 2: Single generic template

As an alternative there would be a single template which takes a DisplayableCaseEvent as mentioned in
the [functionality implementations](0004-case-events-functionality.md) document.

The DisplayableCaseEvent would contain all prompt overrides which could be used to determine the output:

```injectedfreemarker
<#macro caseEvent displayableCaseEvent>
    <@fdsTimeline.timelineSection sectionHeading=displayableCaseEvent.type.displayText>
        <@fdsTimeline.timelineEvent>
            <@fdsDataItems.dataItem>
                <@fdsDataItems.dataValues key=displayableCaseEvent.dateSubmittedPrompt value=displayableCaseEvent.dateSubmitted/>
                ...
            </@fdsDataItems.dataItem>
        </@fdsTimeline.timelineEvent>
    </@fdsTimeline.timelineSection>
</#macro>
```

#### Positives

- Less to manage
- Prompt changes can be tested as they'd be defined via Java

#### Negatives

- Any edits would affect all templates unless modified copies were created
- If an additional component is required then we either have to edit the table or split out the macro anyway.

## Decision

Option 2, single generic template, will be used as we don't expect the content to change in the near future.

This approach is quicker to implement than option 1 and we can use an approach similar to option 1 by using nested
content within the generic template to allow for custom wrappers.

The negative related to edits is minor as we don't expect to have to expand this template anymore. If the change is a
solely to add a new section then ?has_content checks would prevent the need for any callers to have to support this.

Anything that is expected to be added to all templates could have a builder modification which requires the caller to
supply the new content, also preventing the need to modify the template callers themselves.

#### Note
Both implementations would require a wrapper macro to make them valid timeline components: 
```injectedfreemarker
<@fdsTimeline.timeline>
  <#nested/>
</@fdsTimeline.timeline>
```