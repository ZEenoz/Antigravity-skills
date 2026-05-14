---
name: javafx-precision-coding
description: Use for JavaFX/Java enterprise coding tasks. Optimize for minimal context, minimal output, rigorous verification, runnable code, and production-grade diffs.
version: 2.0.0
primary_stack: Java, JavaFX, FXML, Maven/Gradle, Enterprise Desktop Apps
---

# SKILL: JavaFX Enterprise Precision Coding

## Mission
Build, fix, refactor, and debug JavaFX enterprise code with **senior-level quality** and **low token usage**.

Default behavior:
- Analyze first, edit second.
- Use minimal relevant context only.
- Prefer minimal diffs over full-file rewrites.
- Keep final responses short: summary + files + tests + risks.
- Ask only when blocked by missing business rules or missing files.

---

## Token Budget Rules

Always:
1. Read only relevant files/snippets.
2. For Java controllers, inspect only imports, fields, `@FXML`, `initialize()`, event handlers, and called methods.
3. For FXML, inspect only root, `fx:controller`, `fx:id`, handlers, relevant controls/layout.
4. Summarize long logs before reasoning.
5. Output patch/diff or key changes, not entire files unless requested.
6. Avoid repeating the prompt, project facts, or obvious explanations.
7. Ask max 3 questions only if implementation is blocked.

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

---

## Workflow

### 1. Analyze Files
Goal: locate the smallest safe edit scope.

Check:
- Build tool: `pom.xml`, `build.gradle`, `module-info.java`
- UI files: `*.fxml`, `*.css`, assets/resources
- Java files: controller, model/viewmodel, service, repository/API client
- JavaFX wiring: `fx:controller`, `fx:id`, `onAction`, `initialize()`
- Existing patterns: navigation, dialogs, validation, threading, TableView, logging

Output only if useful:
```markdown
Analysis: <project type>, <relevant files>, <current flow>, <risks>
```

### 2. Check / Verify
Goal: prevent wrong implementation.

Verify:
- Task type: feature / bugfix / refactor / UI / CRUD / packaging
- Expected behavior and acceptance criteria
- Inputs, outputs, validation, edge cases
- Enterprise constraints: permissions, audit, DB/API, localization, performance
- Run/test command: `mvn test`, `mvn javafx:run`, `./gradlew test`, `./gradlew run`

If unclear but not blocking, proceed with explicit assumption.
If blocking, ask only essential questions.

### 3. Research Minimally
Goal: fill only missing knowledge.

Priority:
1. Existing codebase patterns
2. Similar screens/controllers in repo
3. Official docs / known JavaFX behavior
4. Build config and dependency versions

Summarize research in max 5 bullets only when it affects implementation.

### 4. Implement
Goal: smallest production-grade change.

Rules:
- Preserve architecture and naming style.
- FXML = layout only.
- Controller = UI state/events only.
- Service = business logic.
- Repository/API client = data access.
- No SQL/business-heavy logic in controllers unless project already does this and scope is small.
- Avoid blocking JavaFX Application Thread.
- Use `Task`, JavaFX `Service`, or executor for slow DB/API/file work.
- Update UI only on FX Application Thread.
- Validate input before service calls.
- Show user-friendly errors; log technical errors if logger exists.
- Use `ObservableList` for TableView data.
- Refresh TableView/form state after CRUD operations.
- Use `java.time` for dates and `BigDecimal` for money.
- Avoid hardcoded secrets, credentials, and environment-specific paths.

### 5. Debug / Recheck
Goal: ensure code compiles, loads, and behaves correctly.

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
- Risks: <only if any>

## Next
- <one concrete next step>
```

For bugfix:
```markdown
Root cause: <short>
Fix: <short>
Verification: <command/result>
```

For review:
```markdown
Must fix:
- ...
Should improve:
- ...
```

---

## JavaFX Enterprise Quality Gate
Before final answer, confirm:
- [ ] Relevant files only
- [ ] FXML-controller bindings valid
- [ ] UI thread not blocked
- [ ] Controller not overloaded with business/data logic
- [ ] Inputs validated
- [ ] Errors user-friendly and debug-friendly
- [ ] TableView/form state refreshes correctly
- [ ] Security: no secrets, no sensitive logs
- [ ] Build/run/test command included
- [ ] Final response concise

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

---

## Quick Prompt Contract
If user input is too broad, request this minimal context:
```text
Stack: JavaFX / Java version / Maven or Gradle
Goal: what to build/fix
Screen: screen name
Files: FXML + Controller + Service snippets
Error: important stack trace lines, if any
Expected: desired behavior
```

## One-Line Operating Rule
**Small context → verify → minimal researched change → run/debug → concise delivery.**
