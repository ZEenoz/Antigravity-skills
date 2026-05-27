---
name: javafx-modern-ui-designer
description: Use this skill to design, review, and implement modern, user-friendly JavaFX UI screens for enterprise desktop applications. The primary rule is user friendliness, reduce friction, remove clutter, improve clarity, and make every screen easy to understand and operate.
---

# SKILL: JavaFX Modern UI Designer

## Mission

Create JavaFX desktop UI that feels modern, clean, fast, easy to use, and enterprise-ready.

Primary rule:
> **User Friendly First. If a UI is confusing, cluttered, slow, inconsistent, hard to scan, or difficult to operate, identify the issue and fix it before adding more features.**

Default behavior:

- Analyze the user's task and current screen before designing.
- Prioritize usability, clarity, accessibility, and maintainability.
- Prefer simple layouts over visually noisy layouts.
- Use consistent spacing, typography, color, component behavior, and interaction patterns.
- Keep JavaFX architecture clean: FXML for layout, CSS for styling, Controller for UI events, Service for business logic.
- Never hard-code theme values, user-facing messages, paths, business rules, or environment-specific values inside controllers.
- Produce implementation-ready UI plans, FXML/CSS guidance, and review notes.

---

## Core UX Principles

### 1. User Friendly First

Every screen must answer these questions immediately:

- What is this screen for?
- What should the user do first?
- What information is most important?
- What action is primary?
- What changed after the user clicked something?
- What went wrong and how can the user fix it?

If the answer is not obvious, redesign the UI flow.

### 2. Clarity Over Decoration

Modern UI is not about adding gradients, shadows, icons, and animations everywhere.
Modern UI is about:

- Clear hierarchy
- Predictable layout
- Comfortable spacing
- Readable text
- Obvious actions
- Fast feedback
- Low cognitive load

### 3. Reduce Cognitive Load

Avoid showing everything at once.
Use:

- grouped sections
- collapsible panels when appropriate
- tabs only when categories are truly separate
- search/filter for large datasets
- progressive disclosure for advanced options
- clear empty states

### 4. Consistency

Keep consistent:

- button styles
- primary/secondary/destructive actions
- spacing scale
- font sizes
- table behavior
- validation style
- dialog style
- navigation pattern
- status colors

### 5. Enterprise Readiness

Enterprise UI must support:

- large data tables
- search and filtering
- form validation
- role/permission visibility
- clear error states
- audit-friendly actions
- keyboard navigation
- accessibility
- localization
- responsive resizing
- long-running operations without freezing the UI

---

## Modern JavaFX UI Style Guide

### Layout

Prefer:

- `BorderPane` for main application shell
- `VBox` / `HBox` for simple vertical/horizontal grouping
- `GridPane` for forms
- `SplitPane` for master-detail screens
- `StackPane` for overlays/loading states
- `ScrollPane` for content that may exceed viewport height

Avoid:

- deeply nested layouts without reason
- absolute positioning unless required
- hard-coded widths/heights everywhere
- mixing layout responsibilities inside controllers

### Visual Hierarchy

Use hierarchy levels:

- App title / module title
- Page title
- Section heading
- Field label
- Helper text
- Error text

Rules:

- Primary action must be visually obvious.
- Destructive action must not look like a normal action.
- Secondary actions should not compete with the primary action.
- Tables should not dominate the screen unless data review is the main task.

### Spacing

Use a consistent spacing scale:

- 4px: tiny spacing
- 8px: compact spacing
- 12px: field spacing
- 16px: section spacing
- 24px: major section spacing
- 32px+: page-level spacing

Do not randomly mix spacing values.
If a value is reused, define it in CSS variables or a theme convention when supported by the project.

### Typography

Prefer:

- readable base font size
- clear page titles
- short labels
- helper text for complex fields
- sentence-case labels

Avoid:

- long button labels
- all-caps labels everywhere
- tiny table text
- low-contrast text
- inconsistent font sizes

### Color

Use color intentionally:

- primary color: main actions and selection
- neutral colors: background, borders, surfaces
- success color: completed/saved states
- warning color: recoverable issues
- danger color: destructive or blocking errors

Avoid:

- too many accent colors
- relying only on color to communicate status
- hard-coded color values inside FXML or controllers
- low contrast text/background combinations

### Components

Recommended component behavior:

- Button: clear primary/secondary/destructive hierarchy
- TextField: label + placeholder + validation message if needed
- ComboBox: clear default/empty state
- DatePicker: validate date range and format
- TableView: search, filter, sort, empty state, row action policy
- Dialog: short title, clear body, obvious confirm/cancel buttons
- ProgressIndicator: show for long-running tasks
- Toast/status message: use for non-blocking success feedback if project has pattern

---

## JavaFX Architecture Rules For UI

### FXML

FXML should define:

- layout structure
- UI controls
- `fx:id`
- event handler wiring
- style classes

FXML should not contain:

- business logic
- environment-specific values
- hard-coded copy that should be localized
- excessive inline styles

### CSS

CSS should define:

- colors
- spacing classes
- typography
- component states
- light/dark theme if supported

CSS should not define:

- business meaning without a semantic class name
- random one-off style values without reason

### Controller

Controller should handle:

- UI initialization
- event handling
- binding UI state
- calling services
- showing validation and feedback

Controller should not handle:

- database queries
- business rules
- heavy computations
- hard-coded config values
- direct long-running operations on the JavaFX Application Thread

### Service / ViewModel

Use service/viewmodel for:

- business logic
- data preparation for UI
- state transformation
- validation rules that are not purely visual
- async task orchestration when appropriate

---

## Zero Hard-Code UI Policy

Never hard-code:

- colors inside controllers
- repeated spacing values in FXML
- user-facing messages inside controllers
- API URLs or file paths
- business thresholds
- role/permission names
- table column labels if localization is required
- date/time/currency formats

Use instead:

- CSS classes for visual styling
- ResourceBundle for user-facing text
- config providers for runtime values
- constants/enums for stable domain vocabulary
- theme files for colors and spacing
- formatter services/utilities for locale-sensitive formatting

Before delivery, run a hard-code review.

---

## UI Review Workflow

### Step 1 — Understand The User Flow

Identify:

- target user task
- first user action
- main completion action
- failure states
- success feedback
- required data
- optional data
- user frequency: daily / occasional / admin-only

Output:

```markdown
Flow: <trigger> → <input> → <action> → <result> → <feedback>
```

### Step 2 — Inspect Current Screen Or Requirement

Check:

- screen purpose
- layout structure
- visual hierarchy
- number of visible actions
- form length
- table density
- validation behavior
- loading behavior
- empty/error states
- keyboard accessibility
- responsiveness on resize

### Step 3 — Identify UX Problems

Look for:

- cluttered layout
- too many buttons
- unclear primary action
- duplicate fields
- weak labels
- missing helper text
- hidden important status
- noisy colors
- inconsistent spacing
- unreadable table
- no search/filter
- no empty state
- no loading state
- no confirmation for destructive action
- UI freeze during slow operations

### Step 4 — Recommend Fixes

For each issue, provide:

```markdown
Issue: <what is wrong>
Impact: <why it hurts users>
Fix: <specific UI/UX change>
Priority: High / Medium / Low
```

### Step 5 — Produce Modern UI Plan

Include:

- layout structure
- component hierarchy
- primary/secondary actions
- state design
- validation design
- empty/loading/error states
- CSS class strategy
- implementation notes

### Step 6 — Deliver Implementation Guidance

Output:

```markdown
## UI Plan
- Layout:
- Sections:
- Primary action:
- Secondary actions:
- Validation:
- States:
- CSS classes:
- Implementation notes:

## UX Fix List
- High:
- Medium:
- Low:
```

---

## Modern UI Workflow Tree

```text
Modern JavaFX UI Design System
├── 1. User Flow Analysis
│   ├── Identify user goal
│   ├── Identify primary task
│   ├── Identify required inputs
│   ├── Identify success/failure feedback
│   └── Identify usage frequency
│
├── 2. Screen Structure Planning
│   ├── Choose layout container
│   ├── Define page header
│   ├── Group related fields/actions
│   ├── Place primary action
│   ├── Add secondary/destructive actions
│   └── Define responsive resizing behavior
│
├── 3. Visual Design System
│   ├── Typography scale
│   ├── Spacing scale
│   ├── Color roles
│   ├── Button hierarchy
│   ├── Form styling
│   ├── Table styling
│   └── Dialog/feedback styling
│
├── 4. Interaction Design
│   ├── Input validation
│   ├── Loading states
│   ├── Empty states
│   ├── Error states
│   ├── Success feedback
│   ├── Keyboard navigation
│   └── Confirmation flows
│
├── 5. JavaFX Implementation Plan
│   ├── FXML layout
│   ├── CSS classes/theme
│   ├── Controller bindings
│   ├── ViewModel/Service state
│   ├── ResourceBundle text
│   └── Async task handling
│
└── 6. UX Quality Review
    ├── Clutter check
    ├── Accessibility check
    ├── Hard-code check
    ├── Responsiveness check
    ├── Error handling check
    └── Final usability score
```

---

## Screen Patterns

### Dashboard Pattern

Best for overview screens.

Use:

- top summary cards
- main chart/table area
- recent activity panel
- quick actions
- filters only when needed

Avoid:

- too many charts
- too many colors
- unclear metrics
- actions scattered everywhere

### Form Pattern

Best for data entry.

Use:

- clear title and description
- grouped fields
- required field indicators
- inline validation
- sticky action bar for long forms
- primary Save/Create button
- secondary Cancel/Clear button

Avoid:

- long ungrouped forms
- Save button hidden at the bottom without context
- validation only after submit when live validation is easy
- unclear required fields

### Table / CRUD Pattern

Best for enterprise records.

Use:

- search field
- filter controls
- sortable columns
- clear empty state
- row selection state
- Add/Edit/Delete actions with clear hierarchy
- destructive confirmation dialog
- pagination or lazy loading for large datasets

Avoid:

- too many columns visible at once
- tiny text
- actions repeated noisily in every row if not needed
- deleting without confirmation

### Master-Detail Pattern

Best for record management.

Use:

- left table/list
- right detail panel/form
- clear selected record state
- disabled actions when no record is selected
- unsaved changes warning

Avoid:

- opening too many modal dialogs
- hiding selected item context

### Wizard Pattern

Best for complex multi-step processes.

Use:

- step indicator
- one goal per step
- Back/Next/Cancel controls
- summary before final submit

Avoid:

- many unrelated fields on one screen
- no progress indicator

---

## Good Modern UI Checklist

A good JavaFX modern UI should have:

- Clear page title
- Clear primary action
- Consistent spacing
- Consistent typography
- Clean grouping of related controls
- Search/filter for large tables
- Empty state when no data exists
- Loading state for slow work
- Inline validation for forms
- Clear error messages
- Non-blocking success feedback
- Destructive confirmation
- Keyboard-friendly navigation
- Reasonable resize behavior
- No UI freeze
- No hard-coded UI copy/config values
- CSS-based styling
- ResourceBundle-ready text
- Controller kept clean

---

## Bad UI Smells And Fixes

### Smell: Too many buttons

Fix:

- Keep one primary action.
- Move secondary actions to a toolbar or overflow menu.
- Group destructive actions separately.

### Smell: Form looks too long

Fix:

- Group fields into sections.
- Move advanced fields into collapsible area.
- Use helper text only where needed.

### Smell: Table is hard to read

Fix:

- Reduce columns.
- Add search/filter.
- Use consistent row height.
- Align numbers/dates consistently.
- Add empty state.

### Smell: User does not know what happened

Fix:

- Add success message.
- Add error message with recovery instruction.
- Disable buttons during processing.
- Show progress indicator for slow tasks.

### Smell: Screen feels cluttered

Fix:

- Increase spacing.
- Remove duplicate labels/actions.
- Use cards/sections.
- Reduce color count.
- Move low-frequency options away from the main path.

### Smell: UI freezes

Fix:

- Move slow operations into `Task`, JavaFX `Service`, or executor.
- Bind loading state to controls.
- Update UI only on the JavaFX Application Thread.

---

## UI Scoring Rubric

Score each screen from 1 to 5:

- Clarity: Can the user understand the screen in 5 seconds?
- Simplicity: Is unnecessary clutter removed?
- Efficiency: Can frequent tasks be completed quickly?
- Feedback: Does every action provide clear feedback?
- Error Recovery: Can the user fix mistakes easily?
- Accessibility: Is keyboard/contrast/readability acceptable?
- Consistency: Does it match the rest of the app?
- Maintainability: Are FXML/CSS/controller responsibilities clean?

If any category is below 4, recommend fixes before calling the UI modern.

---

## Output Templates

### UI Design Plan

```markdown
## Modern UI Plan
- Screen goal:
- User flow:
- Layout pattern:
- Main sections:
- Primary action:
- Secondary actions:
- Data display:
- Validation:
- Loading state:
- Empty state:
- Error state:
- CSS/theme notes:
- JavaFX implementation notes:
```

### UX Review

```markdown
## UX Review
Score: <x>/40

### Must Fix
- Issue:
  - Impact:
  - Fix:

### Should Improve
- Issue:
  - Impact:
  - Fix:

### Nice To Have
- ...
```

### Implementation Checklist

```markdown
## JavaFX Implementation Checklist
- [ ] FXML layout uses clear containers
- [ ] CSS classes define visual style
- [ ] Controller only handles UI events/state
- [ ] User-facing text is ResourceBundle-ready
- [ ] Primary action is obvious
- [ ] Validation is clear
- [ ] Loading/error/empty states exist
- [ ] Table/search/filter behavior is usable
- [ ] Long tasks do not block UI thread
- [ ] No hard-coded UI/config values
```

---

## Example: Good Modern Enterprise UI

A good JavaFX enterprise screen usually includes:

- Left navigation sidebar with clear module names
- Top header with page title, search, and user/system status
- Main content using cards or clean sections
- One strong primary action, such as `Create`, `Save`, or `Export`
- Table area with search, filters, sortable columns, and empty state
- Detail panel or form grouped into clear sections
- Inline validation and clear recovery instructions
- Progress indicator for background operations
- Minimal colors, strong contrast, and consistent spacing
- Responsive resizing behavior for desktop window sizes

Visual direction:

```text
Modern Enterprise Dashboard
├── Sidebar Navigation
├── Header
│   ├── Page Title
│   ├── Search
│   └── Primary Action
├── Summary Cards
├── Main Table / Content Area
│   ├── Filters
│   ├── Sortable Table
│   └── Empty/Loading/Error State
└── Detail / Activity Panel
```

---

## Final Rule

**A modern UI is not finished when it looks beautiful. A modern UI is finished when users can complete their task quickly, confidently, and without confusion.**
