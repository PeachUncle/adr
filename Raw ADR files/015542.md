# ADR-0018 — Component Part Schema: Capabilities, Policies, Behaviors, and UI States

Status: Proposed
Date: 2025-08-18
Related: ADR-0011 (UI subscriptions policy), ADR-0013 (Visual tools in component schema), ADR-0014 (Panel slot plugins), ADR-0017 (StageCrew DOM mutation facade)

## Context

We want component-driven orchestration where each component declares:
- What it can do (capabilities/plugins)
- How those powers are constrained (policies)
- When and how it should act (behaviors/cues that play sequences)
- How the UI should present affordances and runtime visual states (ui.tools, ui.states)

This aligns with CIA/SPA: plugins are discovered from manifests and orchestrated via Conductor.play(); DOM touching remains inside StageCrew. ADR-0013 proposed `ui.tools`. This ADR consolidates the full “Part” schema for components and introduces Option B (state names mapped to CSS classes) to keep CSS/UI synchronized with behavior.

## Decision

- Introduce a Part JSON per component type (the “sheet music” for a performer):
  - Location: `components/<Type>/part.json` (recommended)
  - Library index: `components/parts.manifest.json`
- Standardize these sections:
  1) `metadata` — id/type/version/name/description
  2) `ui` — `template`, `styles`, `tools` (ADR-0013), and `states` (Option B)
  3) `capabilities` — which plugins and sequences are used
  4) `policies` — constraints/config shaping capability use
  5) `behaviors` — declarative cue → play bindings
- Use Option B for UI states:
  - Define named states in `ui.states`, mapping to CSS classes
  - Behaviors activate/deactivate states by calling a StageCrew `ui-state` sequence; StageCrew resolves states to class add/remove
- Preserve SPA rules: plugins do not touch EventBus or DOM directly; Conductor coordinates; StageCrew performs DOM mutations

## Part schema (v1) — shape

Note: representative shape (not a full JSON Schema).

{
  "$schema": "musical-conductor://schemas/component-part-v1.json",
  "id": string,
  "type": string,
  "version": string,
  "metadata": {
    "name": string,
    "author"?: string,
    "description"?: string,
    "tags"?: string[]
  },
  "ui": {
    "template": string,              // markup with tokens (e.g., Mustache/Handlebars)
    "styles"?: { "css"?: string },   // optional inline CSS
    "tools"?: {                       // ADR-0013 visual tools
      // e.g., drag/resize/rotate with handles and constraints
    },
    "states"?: {                      // Option B: state → CSS classes
      [stateName: string]: {
        "classes": string[],          // classes to add when active
        "unset"?: string[]            // classes to remove when active
      }
    }
  },
  "capabilities": [                  // plugin techniques this component can use
    { "pluginId": string, "sequences": string[] }
  ],
  "policies"?: {                      // constraints/config shaping behavior
    // free-form per capability; examples:
    "drag"?: { "enabled"?: boolean, "snap"?: { "grid"?: number }, "bounds"?: "canvas" | "parent" },
    "resize"?: { "min"?: { "w": number, "h": number }, "max"?: { "w": number, "h": number }, "maintainAspectRatio"?: boolean },
    "rotation"?: { "stepDegrees"?: number },
    "validation"?: { "required"?: any, "pattern"?: { "regex": string | null }, "minLength"?: number | null, "maxLength"?: number | null, "validateOn"?: string[] },
    "state"?: { "disabledWhen"?: { "prop": string, "equals": any } }
  },
  "behaviors": {
    "cues": [
      {
        "on": string,                 // event/cue name (e.g., pointer.over, input, validation:passed)
        "if"?: any,                   // simple guards; may reference state/policies/props
        "play": [
          {
            "pluginId": string,
            "sequenceId": string,
            "args"?: any,
            "priority"?: number
          }
        ]
      }
    ]
  }
}

### StageCrew sequence contract (ui-state)

- pluginId: "StageCrew"
- sequenceId: "ui-state"
- args: { "activate"?: string | string[], "deactivate"?: string | string[] }
- Effect: adds/removes classes according to `ui.states` for the targeted element

## Examples (curated from current RenderX JSON components)

### Button — refined Part

{
  "id": "button",
  "type": "ui:button",
  "version": "1.0.0",
  "metadata": { "name": "Button", "author": "RenderX Team", "description": "Interactive button component with click handling" },
  "ui": {
    "template": "<button class=\"rx-button rx-button--{{variant}} rx-button--{{size}}\" type=\"button\" {{#if disabled}}disabled{{/if}}>{{content}}</button>",
    "styles": { "css": "/* existing rx-button CSS retained */" },
    "states": {
      "hovered": { "classes": ["rx-hovered"] },
      "pressed": { "classes": ["rx-pressed"], "unset": ["rx-hovered"] },
      "focused": { "classes": ["rx-focused"] },
      "disabled": { "classes": ["rx-disabled"] }
    },
    "tools": {
      "drag": { "enabled": true },
      "resize": { "enabled": true, "handles": ["nw","n","ne","e","se","s","sw","w"], "constraints": { "min": { "w": 80, "h": 30 }, "max": { "w": 400, "h": 100 } } }
    }
  },
  "capabilities": [
    { "pluginId": "Selection", "sequences": ["select-symphony"] },
    { "pluginId": "Drag", "sequences": ["drag-symphony"] },
    { "pluginId": "Resize", "sequences": ["resize-symphony"] },
    { "pluginId": "Button", "sequences": ["click-symphony"] }
  ],
  "policies": {
    "drag": { "enabled": true, "snap": { "grid": 8 }, "bounds": "canvas" },
    "resize": { "min": { "w": 80, "h": 30 }, "max": { "w": 400, "h": 100 } },
    "button": { "allowSpacePress": true, "allowEnterPress": true },
    "state": { "disabledWhen": { "prop": "disabled", "equals": true } }
  },
  "behaviors": { "cues": [
    { "on": "pointer.over", "if": { "not": { "state": "disabled" } }, "play": [ { "pluginId": "StageCrew", "sequenceId": "ui-state", "args": { "activate": "hovered" } } ] },
    { "on": "pointer.out", "play": [ { "pluginId": "StageCrew", "sequenceId": "ui-state", "args": { "deactivate": ["hovered","pressed"] } } ] },
    { "on": "pointer.down", "if": { "not": { "state": "disabled" } }, "play": [ { "pluginId": "StageCrew", "sequenceId": "ui-state", "args": { "activate": "pressed", "deactivate": "hovered" } } ] },
    { "on": "pointer.up", "if": { "not": { "state": "disabled" } }, "play": [ { "pluginId": "StageCrew", "sequenceId": "ui-state", "args": { "deactivate": "pressed" } }, { "pluginId": "Button", "sequenceId": "click-symphony" } ] },
    { "on": "focus", "play": [ { "pluginId": "StageCrew", "sequenceId": "ui-state", "args": { "activate": "focused" } } ] },
    { "on": "blur",  "play": [ { "pluginId": "StageCrew", "sequenceId": "ui-state", "args": { "deactivate": "focused" } } ] },
    { "on": "keydown", "if": { "key": ["Enter"," "] }, "play": [ { "pluginId": "Button", "sequenceId": "click-symphony" } ] }
  ] }
}

### Input — refined Part

{
  "id": "input",
  "type": "ui:input",
  "version": "1.0.0",
  "metadata": { "name": "Input", "author": "RenderX Team", "description": "Text input with validation and focus handling" },
  "ui": {
    "template": "<input class=\"rx-input rx-input--{{variant}}\" type=\"{{inputType}}\" placeholder=\"{{placeholder}}\" value=\"{{value}}\" {{#if disabled}}disabled{{/if}} {{#if required}}required{{/if}} />",
    "styles": { "css": "/* existing rx-input CSS retained */" },
    "states": {
      "hovered": { "classes": ["rx-hovered"] },
      "focused": { "classes": ["rx-focused"] },
      "valid":   { "classes": ["rx-valid"],   "unset": ["rx-invalid"] },
      "invalid": { "classes": ["rx-invalid"], "unset": ["rx-valid"] },
      "disabled": { "classes": ["rx-disabled"] }
    },
    "tools": {
      "resize": { "enabled": true, "handles": ["e","w"], "constraints": { "min": { "w": 100, "h": 30 }, "max": { "w": 600, "h": 60 } } }
    }
  },
  "capabilities": [
    { "pluginId": "Selection", "sequences": ["select-symphony"] },
    { "pluginId": "Resize", "sequences": ["resize-symphony"] },
    { "pluginId": "Validation", "sequences": ["validate-input"] }
  ],
  "policies": {
    "resize": { "min": { "w": 100, "h": 30 }, "max": { "w": 600, "h": 60 } },
    "validation": { "required": { "enabled": { "prop": "required", "equals": true } }, "pattern": { "regex": null }, "minLength": null, "maxLength": null, "validateOn": ["input","blur"] },
    "state": { "disabledWhen": { "prop": "disabled", "equals": true } }
  },
  "behaviors": { "cues": [
    { "on": "pointer.over", "if": { "not": { "state": "disabled" } }, "play": [ { "pluginId": "StageCrew", "sequenceId": "ui-state", "args": { "activate": "hovered" } } ] },
    { "on": "pointer.out", "play": [ { "pluginId": "StageCrew", "sequenceId": "ui-state", "args": { "deactivate": "hovered" } } ] },
    { "on": "focus", "play": [ { "pluginId": "StageCrew", "sequenceId": "ui-state", "args": { "activate": "focused" } } ] },
    { "on": "blur",  "play": [ { "pluginId": "StageCrew", "sequenceId": "ui-state", "args": { "deactivate": "focused" } } ] },
    { "on": "input", "play": [ { "pluginId": "Validation", "sequenceId": "validate-input" } ] },
    { "on": "validation:passed", "play": [ { "pluginId": "StageCrew", "sequenceId": "ui-state", "args": { "activate": "valid", "deactivate": "invalid" } } ] },
    { "on": "validation:failed", "play": [ { "pluginId": "StageCrew", "sequenceId": "ui-state", "args": { "activate": "invalid", "deactivate": "valid" } } ] }
  ] }
}

## Migration notes from current RenderX JSON

- `ui.template` and `styles.css`: keep as-is
- `integration.canvasIntegration` → `capabilities` + `policies.resize/drag` + `ui.tools`
- `integration.events` → `behaviors.cues`
- `musicalSequences` → explicit cue-to-sequence plays; sequences still live in plugins
- Property schemas/defaults remain where you store them; policies like `state.disabledWhen` and `validation` can reference props

## Consequences

- Pros: declarative, component-driven orchestration; consistent StageCrew UI class toggling; clear separation of concerns
- Cons: requires schema validation and loaders; introduces a small contract for StageCrew `ui-state`

## Implementation checklist

- Define and publish the JSON Schema for Part v1 (types + examples)
- Add a loader for `components/parts.manifest.json` and individual `part.json`
- Implement StageCrew `ui-state` sequence using ADR-0017 DOM facade
- Update Canvas/UI to render `ui.tools` (ADR-0013) and wire pointer cues to Conductor
- Provide sample Parts (Button, Input) and unit tests (SPA validator, cue routing, class toggling)
- Write a guide referencing callbacks-first symphonies and state mapping

