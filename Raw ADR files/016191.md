# 11. Document Canvas

Date: 2025-05-27

## Status

Accepted

## Context

1. Creating a scrollable canvas view.
2. Having a “+”-button that presents a sheet with overlays from the endpoint.
3. Adding a selected overlay to the canvas.
4. Selecting items by tapping on them. Deselecting by tapping outside the item when it’s selected.
5. Moving items around in the canvas by panning while it’s selected.
6. While moving items around in the canvas, we want the items to snap (round off its position to 
  some appropriate but arbitrary precision) when the item is near the top, left, right or bottom 
  part of the canvas or other items on the canvas. It should also show yellow lines highlighting 
  when snapping occurs. (We have attached an example video from SCRL to show how it’s working in 
  our editor, please try it yourself in the app to see more precisely).

## Decision

1. required canvas that expanded to the right on each slide add
2. each slide should have "guide lines", that become visible when user dragging the image close to them
   1. center of: the cell, the layout, the slide 
   2. corners/side: top, bottom, left, right
3. "guide line" change color after several milliseconds pause of user input - debounce, activated snapping
   1. can be activated several guidelines at the same time (top-right corner as example)
4. Image during dragging can left the bounds of slide
   1. Image can be on top of several slides
5. limit selection to one image on a canvas (to simplify the task)
6. create a bottom sheet with overlays preview (grid view with 4 columns)
7. create BottomAppBar with edit controls: 
   1. edit background, 
   2. edit layers (add layer):
      1. add image
      2. add overlay
      3. add text
      4. add grid
   3. edit slides
   4. change ration (Skipped for simplicity)
8. Back to previous screen button is needed
9. Preview button is needed

## Consequences

1. make editor navigation/edit controls first
2. implement simplified canvas drawing on screen (from TemplateDocument instance)
3. use UI elements for composing the canvas layout, it will be easier for hit-test and selection
4. guide lines should be implemented as a UI compose element
