# Architecture Decision Record: Navigation Strategy

Contents:

- Summary
    - Issue
    - Decision
    - Status
- Details
    - Assumptions
    - Constraints
    - Positions
    - Argument
    - Implications
- Related
    - Related decisions
    - Related requirements
    - Related artifacts
    - Related principles
- Notes

## Summary
This ADR aims to determine the most suitable navigation method for the mobile game called Cyber Strike with a focus on user experience. Cyber Strike is a side-scrolling dungeon crawler with turn based combat.

### Issue
The development team needs to decide between three navigation methods:
1.  Tab Navigation
2.  Drawer Navigation
3.  Stack Navigation

### Decision
After evaluating the overall user experience and requirements of the project the development team has decided to use Stack Navigation as the navigation method.

### Status
Accepted

## Details

### Assumptions
1. The user will be playing the game with the phone orientated horizontally
2. The user will not be using external hardware to navigate the game (keyboard, mouse)

### Constraints
1. The game must provide a seamless and intuitive experience while playing the game.

### Positions
1. Tab Navigation: Commonly used for top-level navigation in mobile apps. Each tab represents a distinct functionality within the application.

2. Drawer Navigation: Allows for efficient use of screen space by revealing a hidden panel with a button or icon. This panel provides access to features of the application.

3. Stack Navigation: Linear flow of screens. Commonly used for tasks that involve step-by-step processing.

### Argument
Stack navigation would be a suitable choice for Cyber Strike due to its linear flow and step-by-step nature. The game's side-scrolling dungeon crawler design benefits from stack navigation as it allows players to progress through levels or stages in a sequential manner, providing a clear sense of progression. Additionally, the ability to go back by popping screens off the stack enables players to revisit previous areas or make strategic decisions during turn-based combat, enhancing the overall user experience.

### Implications
1. Stack navigation maximizes screen space utilization in Cyber Strike, allowing for a more immersive game play experience.
2. Stack navigation provides a consistent user interface throughout Cyber Strike creating familiarity for players.
3. Complex menu structures in Cyber Strike may pose limitations for stack navigation, and alternative navigation methods could be considered in such cases.

## Related

### Related Decisions 
Architecture Decision Record - UI Toolkit.

### Related Requirements
User interface design.

### Related Artifacts
UI wire frames, design mockups.

### Related Principles
Overall game play, Game design and feel.

## Notes
Further analysis and testing may reveal the need to combine two methods of navigation.