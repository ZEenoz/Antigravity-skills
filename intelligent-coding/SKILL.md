---
name: intelligent-coding
version: 1.0.0
description: A token-efficient skill for writing high-quality, maintainable, future-proof code. It enforces analysis before coding, DRY, KISS, Separation of Concerns, Clean Code, error handling, testing, and a strict no-hardcoding policy.
language_support: Thai, English, mixed technical writing
optimized_for: smart coding, clean code, enterprise code quality, token efficiency, maintainability, no hardcoding
---

# SKILL: Intelligent Clean Coding

## Mission
Write smart, clean, maintainable code with minimal token usage and maximum correctness.

Core rule:
> Analyze first. Plan briefly. Code simply. Avoid duplication. Handle errors. Never hardcode production values.

Use this skill for:
- writing new code
- fixing bugs
- refactoring
- reviewing code
- improving maintainability
- designing reusable functions/modules
- preparing production-quality code

---

## 1. Operating Mode

### Default Behavior
- Analyze the requirement before coding.
- Identify the smallest safe change.
- Prefer simple code over clever code.
- Reuse existing patterns in the project.
- Write code that is easy to read, test, debug, and extend.
- Keep answers concise to save tokens.
- Output only useful information: plan, changed files, code/diff, tests, risks.

### Token-Saving Rules
Always reduce unnecessary text:
- Do not repeat the user's full request.
- Do not explain basic concepts unless asked.
- Do not dump unrelated files.
- Do not over-document obvious code.
- Do not provide multiple solutions unless needed.
- Prefer short bullets over long paragraphs.
- Prefer patch/diff or focused snippets over full files.

Never remove important facts:
- file paths
- commands
- error messages
- test results
- assumptions
- risks
- config keys
- version numbers
- security warnings

---

## 2. Workflow

```text
Intelligent Clean Coding Workflow
├── 1. Analyze Requirement
├── 2. Plan Minimal Solution
├── 3. Design Clean Structure
├── 4. Implement Code
├── 5. Handle Errors
├── 6. Test / Verify
└── 7. Deliver Concise Summary
```

---

## 3. Step 1 — Analyze Requirement

Goal: understand what must be built or fixed before writing code.

Check:
- goal
- expected input
- expected output
- affected files/modules
- existing patterns
- edge cases
- constraints
- performance/security concerns
- whether the change should be reusable

If information is missing but not blocking, proceed with a clear assumption.
If information is blocking, ask only 1–3 questions.

Output only when useful:

```markdown
## Analysis
- Goal:
- Affected area:
- Assumption:
- Risk:
```

---

## 4. Step 2 — Plan Minimal Solution

Goal: create the smallest safe plan before implementation.

Planning rules:
- Choose the simplest approach that satisfies the requirement.
- Avoid large rewrites unless required.
- Prefer incremental change.
- Preserve existing architecture.
- Identify reusable logic before coding.
- Define how to verify the result.

Compact plan format:

```markdown
## Plan
1. <small step>
2. <small step>
3. Verify with `<command>`
```

Skip visible plan for very small tasks unless useful.

---

## 5. Design Principles

## DRY — Don't Repeat Yourself
Do not duplicate logic.

Rules:
- If similar logic appears more than once, extract a function/helper/module.
- If validation repeats, centralize validation.
- If constants repeat, move them to a named constant/config.
- If mapping logic repeats, create mapper/adapter/helper.
- If UI behavior repeats, create reusable component/style/helper.

Avoid:
- copy-paste blocks
- repeated conditions
- repeated magic strings
- repeated formatting logic
- repeated API/database calls

Good pattern:

```text
Repeated logic → function/helper/service
Repeated value → constant/config
Repeated UI style → CSS/theme/component
Repeated business rule → domain/service layer
```

---

## KISS — Keep It Simple
Write the simplest code that solves the problem.

Rules:
- Prefer readable code over clever code.
- Avoid unnecessary abstraction.
- Avoid over-engineering.
- Avoid complex inheritance when composition or functions are enough.
- Avoid adding dependencies for small tasks.
- Keep functions small and focused.

Ask before adding complexity:
- Is this needed now?
- Can this be simpler?
- Will a new developer understand this quickly?
- Does this abstraction reduce real duplication or only add indirection?

---

## Separation of Concerns
Each part of the code should have one clear responsibility.

Common separation:

```text
UI / Controller      → input, display, user events
Service / Domain     → business logic
Repository / Client  → data access / API calls
Model / DTO          → data structure
Config               → runtime values
Validation           → input/domain validation
Formatter / Mapper   → transformation logic
```

Rules:
- Do not put business logic in UI/controller.
- Do not put database/API logic in UI/controller.
- Do not put config values inside business logic.
- Do not mix formatting, validation, and persistence in one function.
- Keep modules independent where possible.

---

## 6. Clean Code Rules

### Naming
Use meaningful names.

Good:
```text
userAge
calculateTotalPrice
isEmailValid
loadCustomerOrders
```

Bad:
```text
ua
calc
flag
x
foo
```

Rules:
- Variables describe data.
- Functions describe actions.
- Classes describe responsibility.
- Booleans use `is`, `has`, `can`, `should` when appropriate.
- Avoid unclear abbreviations.

---

### Structure
Keep code organized.

Rules:
- Follow language/framework formatting conventions.
- Keep related code close together.
- Group imports clearly.
- Remove unused imports/variables.
- Avoid long functions.
- Avoid deeply nested conditions.
- Prefer early return for invalid cases when it improves readability.

Function guideline:
```text
One function = one responsibility
Input clear
Output clear
Errors handled
No hidden side effects unless expected
```

---

### Comments
Use comments only when useful.

Comment when:
- logic is non-obvious
- business rule needs context
- workaround exists for known constraint
- warning prevents future bugs

Do not comment obvious code.

Bad:
```java
// increment i by 1
 i++;
```

Good:
```java
// Required by legacy export format; changing this breaks old reports.
```

---

## 7. Error Handling

Always handle expected failure cases.

Check:
- null / empty input
- invalid format
- missing file
- missing config
- API failure
- database failure
- permission failure
- timeout
- duplicate record
- not found
- unexpected state

Rules:
- Fail clearly.
- Do not swallow exceptions silently.
- Provide useful error messages.
- Log technical details when appropriate.
- Do not expose secrets or sensitive data in logs/errors.
- Convert low-level errors into user/domain-friendly errors where needed.

Bad:
```java
try {
    saveUser(user);
} catch (Exception e) {
}
```

Good:
```java
try {
    saveUser(user);
} catch (DuplicateUserException e) {
    throw new UserAlreadyExistsException(user.getEmail(), e);
}
```

---

## 8. Strict No-Hardcoding Policy

Never hardcode production values.

Do not hardcode:
- credentials
- API keys
- tokens
- URLs
- ports
- file paths
- timeouts
- retry counts
- role names
- permission names
- business thresholds
- status values that may change
- user-facing messages that should support localization
- date/time/currency formats
- environment names such as `dev`, `uat`, `prod`
- SQL scattered in UI/controller code
- magic numbers or magic strings

Use instead:
- config files
- environment variables
- typed config providers
- constants/enums for stable domain terms
- ResourceBundle/localization files for UI text
- CSS/theme files for styling
- repository/query layer for SQL
- test fixtures for test data

Review gate:
```text
No new hardcoded production value
No secret in code/log
No duplicated magic string
Config ownership clear
```

If hardcoding is found, output:

```text
Hardcode risk: `<value>` in `<file>` → move to <config/constant/resource>
```

Thai:

```text
เสี่ยง hardcode: `<value>` ใน `<file>` → ย้ายไป <config/constant/resource>
```

---

## 9. Testing & Verification

Every meaningful change should be verifiable.

Test types:
- unit test for isolated logic
- integration test for API/database/service interaction
- UI/manual test for UI behavior
- regression test for bugfix
- build/lint/typecheck for syntax and style

Verification rules:
- Run targeted tests first.
- Run full tests when reasonable.
- If tests cannot be run, state why and give exact command.
- Do not claim tests passed unless verified.

Common commands:

```bash
# Java / Maven
mvn test
mvn clean test

# Java / Gradle
./gradlew test
./gradlew clean test

# JavaFX
mvn javafx:run
./gradlew run

# Node.js
npm test
npm run build
npm run lint

# Python
python -m py_compile <file>
pytest
python -m pytest

# .NET
dotnet build
dotnet test

# Go
go test ./...
```

---

## 10. Code Review Checklist

Before delivery, verify:

- [ ] Requirement is satisfied
- [ ] Code is simple
- [ ] No duplicate logic
- [ ] Names are meaningful
- [ ] Responsibilities are separated
- [ ] Errors are handled
- [ ] No hardcoded production values
- [ ] No secrets in code/logs
- [ ] Existing style is preserved
- [ ] Tests or verification steps are provided
- [ ] No unrelated changes

---

## 11. Output Format

### For Small Coding Tasks

```markdown
## Result
- Changed: `<file>` — <short change>
- Verify: `<command>` — <passed/failed/not run>
- Risk: <only if real>
```

### For Bugfix

```markdown
## Fix
- Cause: <short>
- Change: `<file>` — <short>
- Verify: `<command>` — <result>
```

### For Code Review

```markdown
## Review
### Must Fix
- `<file>` — <issue>

### Should Improve
- `<file>` — <issue>

### Hardcode Risk
- `<file>` — <value/rule>
```

### For Planning Before Coding

```markdown
## Plan
1. Analyze affected files/modules
2. Extract/reuse shared logic if duplication exists
3. Implement minimal clean change
4. Add error handling
5. Verify with `<command>`
```

---

## 12. Token-Efficient Final Style

Prefer short final answers:

```text
Changed:
- `<file>` — <what changed>

Verify:
- `<command>` — <result>

Risk:
- <only if needed>
```

Do not add extra explanation unless asked.

---

## 13. Anti-Patterns

Never:
- write code before understanding the requirement
- duplicate logic instead of extracting reusable code
- create unnecessary abstraction
- mix UI, business logic, and data access
- use unclear names
- ignore error cases
- swallow exceptions silently
- hardcode production values
- add unrelated changes
- claim tests passed without running or verifying
- return long explanations when a short result is enough

---

## Final Rule
**Analyze. Plan. Keep simple. Reuse. Separate concerns. Handle errors. No hardcoding. Verify. Keep output short.**
