---
name: javafx-precision-coding-no-hardcode
version: 2.2.0
description: Use for JavaFX/Java enterprise coding tasks. Optimized for minimal context, production-grade diffs, rigorous verification, and a strict zero-hard-code policy.
primary_stack: Java, JavaFX, FXML, Maven/Gradle, Enterprise Desktop Apps
---

# SKILL: JavaFX Enterprise Precision Coding

## Mission
Build, fix, refactor, and debug JavaFX enterprise code with **senior-level quality**, **low token usage**, and **zero hard-coded production logic**.

Default behavior:
- Analyze first, edit second.
- Use minimal relevant context only.
- Prefer minimal diffs over full-file rewrites.
- Preserve existing architecture unless a safer change requires otherwise.
- Keep final responses short: summary + files + verification + risks.
- Ask only when blocked by missing business rules, missing files, or unsafe assumptions.

---

## Non-Negotiable Rule: Zero Hard-Coding

Never hard-code values directly inside business logic, controllers, repositories, UI event handlers, build scripts, or deployment-related code.

### Prohibited Hard-Coding
Never inline:
- Credentials, tokens, API keys, passwords, certificates, secrets
- Database URLs, usernames, passwords, schema names, server names
- API base URLs, endpoints, ports, timeout values, retry counts
- File paths, OS-specific paths, user directories, export/import paths
- Business rules, limits, thresholds, tax rates, status codes, role names, permission names
- SQL strings scattered across UI/controller code
- UI labels/messages that should support localization
- Date/time formats, currency formats, locale-specific values
- Magic numbers, magic strings, magic booleans
- Test data inside production code
- Environment names such as `dev`, `uat`, `prod` inside logic

### Required Alternatives
Use the most appropriate externalized or centralized source:
- Environment variables for deployment-specific values
- `.properties`, `.yml`, `.json`, `.toml`, or equivalent config files
- Dependency injection or configuration provider classes
- Constants/enums only for stable domain vocabulary
- ResourceBundle for UI text and localization
- Database migration/config files for schema-related values
- Repository/query layer for SQL or persistence logic
- Test fixtures/factories for test data
- Build profiles for environment-specific behavior

### Hard-Code Review Gate
Before delivering code, verify:
- No new magic literals were introduced.
- Every configurable value has a named source.
- Every user-facing message is externalized or follows the existing localization pattern.
- Every secret/config value is loaded from a safe runtime configuration source.
- Every new constant has a clear reason and belongs in the correct layer.

If a hard-coded value already exists and must remain for compatibility, flag it as a risk and do not duplicate it.

---

## Smart Implementation Rules

### Configuration First
When adding behavior that depends on values, create or reuse:
- `AppConfig`, `ConfigService`, `SettingsProvider`, or equivalent existing pattern
- config files under project resources when appropriate
- environment variables for deployment/runtime values
- typed config objects instead of loose string lookups when possible

### Contract First
Before implementation, identify:
- input contract
- output contract
- validation rules
- error behavior
- data source
- ownership of each rule

### Single Source of Truth
A value or rule must live in exactly one authoritative place:
- validation rule → validation/domain layer
- business rule → service/domain layer
- UI text → resource bundle/localization layer
- database access → repository/API client layer
- environment value → config layer

### Defensive Enterprise Defaults
Prefer:
- explicit error handling
- structured logging without sensitive data
- safe fallbacks only when business-approved
- readable names over clever code
- small methods and small diffs
- rollback-friendly changes

---

## Token Budget Rules

Always:
- Read only relevant files/snippets.
- For Java controllers, inspect only imports, fields, `@FXML`, `initialize()`, event handlers, and called methods.
- For FXML, inspect only root, `fx:controller`, `fx:id`, handlers, relevant controls/layout.
- Inspect config/resource files when adding values, messages, paths, endpoints, rules, or environment-specific behavior.
- Summarize long logs before reasoning.
- Output patch/diff or key changes, not entire files unless requested.
- Avoid repeating the prompt, project facts, or obvious explanations.
- Ask max 3 questions only if implementation is blocked.

Never:
- Dump long docs.
- Rewrite unrelated code.
- Explain basic Java/JavaFX concepts unless asked.
- Claim tests passed unless actually run.

---

## Trigger
Use this skill for:
- JavaFX GUI creation or modification
- FXML/controller bugs
- TableView/form/CRUD screens
- Java service/repository logic used by JavaFX
- Debugging build/runtime errors
- Refactor, optimize, package, or review JavaFX apps
- Any change involving config, validation, localization, persistence, deployment, or enterprise rules

---

## Workflow

### 1. Analyze Files
Goal: locate the smallest safe edit scope.

Check:
- Build tool: `pom.xml`, `build.gradle`, `module-info.java`
- UI files: `*.fxml`, `*.css`, assets/resources
- Config/resources: `*.properties`, `*.yml`, `*.json`, `ResourceBundle`, logging config
- Java files: controller, model/viewmodel, service, repository/API client, config/provider classes
- JavaFX wiring: `fx:controller`, `fx:id`, `onAction`, `initialize()`
- Existing patterns: navigation, dialogs, validation, threading, TableView, logging, localization, dependency injection

Output only if useful:

```markdown
Analysis: <project type>, <relevant files>, <current flow>, <config pattern>, <risks>
```

### 2. Check / Verify
Goal: prevent wrong implementation.

Verify:
- Task type: feature / bugfix / refactor / UI / CRUD / packaging / config / localization
- Expected behavior and acceptance criteria
- Inputs, outputs, validation, edge cases
- Config ownership for every new value
- Enterprise constraints: permissions, audit, DB/API, localization, performance
- Run/test command: `mvn test`, `mvn javafx:run`, `./gradlew test`, `./gradlew run`

If unclear but not blocking, proceed with explicit assumption.
If the assumption could create hard-coded behavior or unsafe production behavior, ask first.

### 3. Research Minimally
Goal: fill only missing knowledge.

Priority:
- Existing codebase patterns
- Existing config/localization/resource patterns
- Similar screens/controllers/services in repo
- Official docs / known JavaFX behavior
- Build config and dependency versions

Summarize research in max 5 bullets only when it affects implementation.

### 4. Implement
Goal: smallest production-grade change with zero hard-coded behavior.

Rules:
- Preserve architecture and naming style.
- FXML = layout only.
- Controller = UI state/events only.
- Service = business logic.
- Repository/API client = data access.
- Config provider = runtime/environment/configurable values.
- ResourceBundle/localization layer = user-facing text.
- No SQL/business-heavy logic in controllers.
- Avoid blocking JavaFX Application Thread.
- Use `Task`, JavaFX `Service`, or executor for slow DB/API/file work.
- Update UI only on FX Application Thread.
- Validate input before service calls.
- Show user-friendly errors; log technical errors if logger exists.
- Use `ObservableList` for TableView data.
- Refresh TableView/form state after CRUD operations.
- Use `java.time` for dates and `BigDecimal` for money.
- Do not introduce hard-coded values. Use config, constants, enums, or resources according to ownership.

### 5. Debug / Recheck
Goal: ensure code compiles, loads, behaves correctly, and contains no new hard-coded production values.

Check:
- Compilation/build result
- FXML loads without `LoadException`
- `fx:id` matches `@FXML`
- `onAction` method exists with valid signature
- No `NullPointerException` in `initialize()`
- No `Not on FX application thread`
- UI does not freeze on long tasks
- Form validation and error dialogs work
- TableView data appears and refreshes
- Config/resource values load correctly
- No new magic literals, paths, endpoints, credentials, business thresholds, or user-facing messages are hard-coded
- Tests/build/run commands are recorded

Common commands:

```bash
mvn clean test
mvn javafx:run
./gradlew clean test
./gradlew run
```

If a command was not run, state `not run` with reason and exact recommended command.

### 6. Deliver
Default final format:

```markdown
## Done
- Summary: <1-2 lines>
- Files: `<file>` — <change>
- Verification: `<command>` — <passed/failed/not run>
- Hard-code check: <passed/issues found>
- Risks: <only if any>

## Next
- <one concrete next step>
```

For bugfix:

```markdown
Root cause: <short>
Fix: <short>
Verification: <command/result>
Hard-code check: <passed/issues found>
```

For review:

```markdown
Must fix:
- ...
Should improve:
- ...
Hard-code risks:
- ...
```

---

## JavaFX Enterprise Quality Gate
Before final answer, confirm:
- Relevant files only
- FXML-controller bindings valid
- UI thread not blocked
- Controller not overloaded with business/data/config logic
- Inputs validated
- Errors user-friendly and debug-friendly
- TableView/form state refreshes correctly
- Configurable values are externalized
- User-facing messages follow localization/resource pattern
- Security: no secrets, no sensitive logs
- Build/run/test command included
- Hard-code check completed
- Final response concise

---

## Anti-Patterns
Never do these:
- Change code before understanding relevant FXML/controller flow.
- Load or rewrite unrelated files.
- Use `catch {}` or swallow exceptions.
- Put slow DB/API/file calls directly in button handlers.
- Update UI controls from background thread.
- Break public behavior without warning.
- Add dependencies without clear need.
- Leave TODO/stub/placeholder code in delivered output.
- Hard-code credentials, paths, URLs, messages, thresholds, roles, permissions, or environment names.
- Duplicate business rules across UI, service, and repository layers.
- Store config values in controllers.

---

## Quick Prompt Contract
If user input is too broad, request this minimal context:

```text
Stack: JavaFX / Java version / Maven or Gradle
Goal: what to build/fix
Screen: screen name
Files: FXML + Controller + Service + Config snippets
Config pattern: properties/yml/env/ResourceBundle/etc.
Error: important stack trace lines, if any
Expected: desired behavior
```

---

## One-Line Operating Rule
**Small context → verify → identify config ownership → minimal researched change → no hard-code check → run/debug → concise delivery.**
