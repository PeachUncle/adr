# Layout / Week 10 Decisions

## Context and Problem Statement

As we approached Week 10, we got feedback from our TA and Professor Powell on what to focus on for the final week.

Our TA recommended the following:
- Change "Budget Remaining" to Amount Remaining
- Make the tool tips more concise
- Center the Visualization and Budget Words
- Somewhat cluttered see if you can separate budget and visualization
- Change the colors a bit make it a bit less green
- The frog is cute, potentially keep it on the screen longer
- Have a way to rank priority of reminders


Professor Powell reccomended the following:
- The eye moves from top left corner along the top and then down the bottom right, be mindful of this
- Move the input data feature to the top corner
- Make it so the default view for visualization is a text view showing average per day and amount remaining and then you can change it to pie chart, line chart using a toggle button
- Good you have a lot of features, but make it so that you can toggle on and off so the features are not overwhelmed


## Considered Options

* Considered all the feedback above and had to chooose what we implemented and what we would not have time for.

## Decision Outcome
After weighing all the feedback, we made the following changes.

Considering both the TA's and Professor Powell's feedback:
- We changed the visualization to default view to a text view that shows the amount remaining and average left per day considerining the amount remaining. This incorporated the wording feedback as well as the clutering feedback between budget and visualization. If we had more time, we would have prefered make it scrollable horizontally instead of using a drop down selector. This way the user can choose what visualization they wanted to see.
- We made it so you can toggle to be able to see the reminders or calendar by clicking a button in order to make it less clutered on entering
- Changed the tool tips to be less descriptive and added a full tutorial on the README to make up for it
- Reminders can be ranked by priority if needed
- Changed the colors to be less green overall and be nice visually on the eyes

What we did not change:
- We did not move the input for the expense table to the top because we decided to focus on testing and other features over this. If we had more time, we would have done it!
