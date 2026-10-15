# Architecture Decision Record: UI Toolkit

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
    - Conclusion
- Related
    - Related decisions
    - Related requirements
    - Related artifacts
    - Related principles
- Notes

## Summary
This ADR aims to determine the most suitable UI toolkit for the mobile game called Cyber Strike with a focus on user experience. Cyber Strike is a side-scrolling dungeon crawler with turn based combat.

### Issue
The development team needs to decide on a UI toolkit to use from the numerous available options. As such, it has been narrowed down to the following:
1. React Native Elements
2. Native Base
3. Shoutem UI
4. Ant Design Mobile
5. UI Kitten

### Decision
After evaluating the overall user experience and requirements of the project the development team has decided to use Native Base as the UI toolkit.

### Status
Accepted

## Details

### Assumptions
1. The game will be developed exclusively for Android devices using React Native.
2. Initial animations will be simple, but there is a desire to expand the complexity of animations in the future.
3. Customizability and ease of use are prioritized to adhere to time and budget constraints.
4. The development team is familiar with React Native.

### Constraints
1. The game's development is limited by time and budget.
2. Initial UI requirements include simple animations but may require more complex animations in the future.
3. The UI toolkit must offer scalability and easy integration with React Native specifically for Android.
4. There is a need for a balance between out-of-the-box components and customization capabilities.

### Positions
1. React Native Elements:
   - Pros: Highly customizable, large community, and comprehensive documentation.
   - Cons: May require additional work for complex animations and game-specific UI components.
2. Native Base
   - Pros: Wide range of pre-built components, extensive theming capabilities, and strong community support.
   - Cons: Performance may be an issue for highly animated and dynamic UIs.
3. Shoutem UI
   - Pros: Beautiful pre-built components with good theming options, integrates well with other Shoutem services.
   - Cons: Smaller community and potentially limited flexibility for highly custom designs.
4. Ant Design Mobile
   - Pros: Large set of enterprise-level components, consistent design language, and good performance.
   - Cons: The design may be too rigid for a game UI, requiring significant customization.
5. UI Kitten
   - Pros: Highly themeable, good performance, and a focus on visual consistency.
   - Cons: May have a steeper learning curve for developers unfamiliar with its design principles.

### Argument
Considering the project scope and constraints, Native Base and React Native Elements are strong contenders. Native Base offers a comprehensive suite of pre-built components that can significantly speed up development time, which is crucial given the time and budget limitations. Its focus on extendibility makes it a viable option for future enhancements, including more complex animations.

React Native Elements stands out for its customization capabilities and strong community support. Its flexibility makes it a good fit for projects that may need to evolve over time, aligning well with the potential expansion of animations and UI complexity.

### Implications
Choosing between Native Base and React Native Elements will come down to the development team's specific needs:
   - Native Base is well-suited for teams looking for a wide array of ready-to-use components that can be easily extended or adapted as the project grows.
   - React Native Elements offers a more flexible foundation that can be tailored to the game's evolving UI and animation requirements, especially beneficial if the team anticipates significant UI customization or expansion in the future.

### Conclusion
Given the specific focus on Android development with React Native, and considering the simplicity of initial animations with potential for future expansion, Native Base emerges as a slightly more favorable choice due to its balance of ready-made components and extensibility. While React Native Elements remains a strong candidate due to its superior customization capabilities, an overall preference for out-of-the-box functionality, versus the need for customization, allows the team to focus on developing the core functionality and unique features of the game.

## Related

### Related Decisions 
Architecture Decision Record - Navigation Strategy.

### Related Requirements
User interface design.

### Related Artifacts
UI wire frames, design mockups.

### Related Principles
Overall game play, game design and feel.
