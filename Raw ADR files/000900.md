# 003: Gradio for UI Framework

## Status

Accepted

## Date

2025-12-15

## Context

The application needed a user interface to collect input (user interests, genre preferences, model settings) and display recommendations with visual appeal. Several Python UI frameworks were considered:

Alternatives:
1. **Gradio** - ML-focused UI framework
   - ✅ Designed for ML demos
   - ✅ Quick prototyping
   - ✅ Built-in components (Textbox, Dropdown, Slider)
   - ✅ CSS customization support
   - ✅ Auto-generated sharing links
   - ⚠️ Less control than web frameworks

2. **Streamlit** - Data app framework
   - ✅ Popular for data apps
   - ✅ Good for dashboards
   - ❌ Less suited for conversational UX
   - ❌ Rerun model less intuitive

3. **Flask/FastAPI + React** - Full web app
   - ✅ Maximum control
   - ❌ Much more complex
   - ❌ Slower development
   - ❌ Requires frontend expertise

4. **CLI only** - Command-line interface
   - ❌ Poor user experience
   - ❌ No visual polish
   - ❌ Harder to demo

## Decision

Use **Gradio 6.0+** as the UI framework with extensive CSS customization for a polished, human-centered design.

Key features utilized:
- **Input components**: Textbox, Dropdown, Slider, Radio, Accordion
- **Output components**: Markdown, HTML for custom card rendering
- **State management**: gr.State for session history
- **Events**: .click(), .change(), .submit() handlers
- **JavaScript integration**: Custom JS for copy, export, share, theme toggle
- **CSS customization**: Custom properties for theming, animations, responsive design

Design philosophy:
- Mobile-first responsive layout
- Dark/light theme support
- Smooth transitions and hover effects
- Clear visual hierarchy
- Accessibility features (keyboard shortcuts, contrast)

## Consequences

### Positive
- **Rapid development**: Built UI in hours, not days
- **Focus on ML**: UI code doesn't distract from recommendation logic
- **Good defaults**: Components look professional out-of-the-box
- **Easy customization**: CSS injection for brand styling
- **Python-native**: No context switching to JavaScript
- **Deployment**: Simple to deploy (local, HuggingFace Spaces, Gradio Cloud)
- **Demos**: Easy to share with public links

### Negative
- **Limited control**: Some UI patterns hard to implement
- **Component constraints**: Stuck with Gradio's component set
- **Version changes**: Gradio 6.0 broke some patterns (e.g., Component.update())
- **CSS specificity**: Fighting with Gradio's internal styles requires !important
- **Performance**: Full page updates can be slower than SPA

### Neutral
- Learning curve for Gradio-specific patterns
- Documentation sometimes lags behind releases

### Risks
- **Breaking changes**: Gradio updates may break UI
  - Mitigation: Pin version in requirements.txt, test after upgrades
- **Customization limits**: May hit ceiling for complex UX
  - Mitigation: Gradio supports custom components if needed
- **Mobile support**: Gradio mobile support improving but not perfect
  - Mitigation: Extensive CSS for responsive design

## Implementation Notes

Key UI features:
- **Theming**: CSS custom properties with data-theme attribute
- **Cards**: Custom HTML rendering for Google Books results
- **Toolbar**: Multiple action buttons (recommend, refresh, copy, export, share)
- **Session history**: Dropdown to reload previous queries
- **Advanced options**: Collapsible accordion for model/temperature
- **Keyboard shortcuts**: Enter to submit, tooltips for shortcuts
- **LocalStorage**: Browser storage for reading list and ratings

CSS strategy:
- Define CSS in config.py as a constant
- Pass to demo.launch(css=css) (Gradio 6.0+ pattern)
- Use CSS custom properties for easy theming
- Target Gradio's internal classes with !important where needed

Gradio 6.0 migration:
- Changed from `gr.Component.update()` to direct component instantiation
- Moved CSS from Blocks constructor to launch() method
- Updated event handler patterns

## References

- [Gradio Documentation](https://www.gradio.app/docs)
- [Gradio GitHub](https://github.com/gradio-app/gradio)
- [CSS Custom Properties](https://developer.mozilla.org/en-US/docs/Web/CSS/--*)
- [Human-Centered Design Principles](https://www.interaction-design.org/literature/topics/human-centered-design)
