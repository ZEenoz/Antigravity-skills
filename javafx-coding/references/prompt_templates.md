# JavaFX Prompt Templates

## New Screen
```text
Use javafx-enterprise-coding-skill-agent.
Task: create a new JavaFX screen.
Screen: <name>
Stack: JavaFX / Java <version> / <Maven or Gradle>
Files/conventions: <similar FXML/controller if any>
Acceptance criteria:
- Screen loads
- Buttons work
- Validation works
- No UI freeze
Output: analysis + minimal files/diff + run command.
```

## Bugfix
```text
Use javafx-enterprise-coding-skill-agent.
Bug: <short symptom>
Error: <important LoadException/NPE lines only>
Files: <FXML + Controller snippets>
Expected: <what should happen>
Actual: <what happens>
Output: root cause + minimal diff + debug command.
```

## CRUD TableView
```text
Use javafx-enterprise-coding-skill-agent.
Task: implement/fix CRUD TableView screen.
Entity: <entity>
Fields: <fields>
Data source: <DB/API/in-memory>
Files: <FXML/controller/service snippets>
Output: concise plan + diff + validation + refresh behavior.
```
