---
name: phase-implementation-planner
description: ทักษะนี้ใช้สำหรับวิเคราะห์ข้อมูล ศึกษาบริบท และวางแผน Phase Implementation อย่างเป็นระบบ สำหรับโปรเจกต์ซอฟต์แวร์หลายภาษา/หลายเทคโนโลยี โดยเน้นแผนที่ชัดเจน ทำตามได้จริง ลดความเสี่ยง ประหยัด Token และส่งมอบผลลัพธ์ระดับ Production-ready
language: thailand
optimized_for: implementation planning, software design, AI coding agents, enterprise projects, token efficiency
---

# SKILL: Phase Implementation Planner

## Description

This skill enables an agent to create a precise, structured, and executable **Phase Implementation Plan** before any implementation work begins.

Use this skill for:

- Planning a new system
- Planning a new feature
- Planning a refactor
- Planning a migration
- Planning a large bug fix or system redesign
- Planning work across multiple languages, including Java, JavaScript, TypeScript, Python, C#, Go, PHP, SQL, HTML, and CSS
- Planning Desktop, Web, API, Backend, Frontend, Database, Automation, Internal Tool, and Enterprise App projects

Primary goals:

- Research before planning
- Split work into clear implementation phases
- Identify dependencies between tasks
- Define deliverables for each phase
- Define risks, assumptions, validation methods, and test plans
- Produce a plan that developers or coding agents can immediately execute
- Reduce token usage by using only relevant context

---

## Operating Principles

1. **Research First, Plan Second**
   - Never create a plan based on guesswork.
   - First inspect requirements, codebase context, constraints, stack, dependencies, and risks.

2. **Plan Before Code**
   - Do not start implementation until phases, scope, acceptance criteria, and dependencies are clear.

3. **Small Phases, Clear Outputs**
   - Every phase must produce a verifiable output.
   - The plan must be split into small units that can be implemented, reviewed, tested, and rolled back.

4. **Language-Agnostic**
   - Do not assume a specific programming language.
   - Adapt terms to the stack being used, such as Java, Python, Node.js, React, .NET, SQL, JavaFX, Spring Boot, FastAPI, or Laravel.

5. **Token-Efficient Planning**
   - Avoid unnecessary theory.
   - Avoid dumping long files.
   - Summarize only information that affects the plan.
   - Use bullets, checklists, workflow trees, and phase breakdowns only when they improve clarity.

6. **Risk-Driven Planning**
   - High-risk work should be handled early or isolated in a proof of concept.
   - Work that impacts many components must include validation gates.

---

## When To Use This Skill

Use this skill when the user asks for:

- An implementation plan
- Phase breakdown
- Development roadmap
- System-building workflow
- Pre-implementation analysis
- Task decomposition for developers or AI agents
- Workflow design before writing code
- A structured plan for building, fixing, refactoring, or migrating a system

---

## Context Budget Rules

The agent must minimize token usage while preserving planning quality.

### Read Only What Matters

Inspect only:

- Relevant requirements
- Relevant architecture
- Entry points and main flow
- Modules that will be changed
- Build/config/dependency files that affect implementation
- Important error or log lines only

### Avoid Context Waste

Never:

- Read the entire repository when the task is limited to one module
- Paste full files back to the user unless necessary
- Explain generic theory at length
- Summarize details that do not affect the plan
- Create more phases than the task requires

### Output Compression

Prefer:

- Concise bullets
- Workflow trees
- Phase lists
- Deliverables and checkpoints
- Only important risks and assumptions

---

# Master Workflow Tree

```text
Phase Implementation Planning System
├── 0. Intake & Scope Lock
│   ├── Capture the user's goal
│   ├── Identify the problem, feature, or system to build
│   ├── Separate in-scope and out-of-scope work
│   └── Ask only blocking questions
│
├── 1. Research & Discovery
│   ├── Study requirements
│   ├── Inspect relevant codebase, architecture, and modules
│   ├── Inspect technology stack, framework, and dependencies
│   ├── Check similar implementations if available
│   ├── Check constraints: security, performance, UX, data, deployment
│   └── Summarize only findings that affect the plan
│
├── 2. System Understanding
│   ├── Identify current state
│   ├── Identify target state
│   ├── Identify the gap between current state and target state
│   ├── Identify affected components
│   ├── Identify data flow and control flow
│   └── Identify integration points
│
├── 3. Strategy Design
│   ├── Choose implementation approach
│   ├── Define build order
│   ├── Define dependency order
│   ├── Choose migration/refactor strategy if needed
│   ├── Define rollback strategy
│   └── Define validation strategy
│
├── 4. Phase Breakdown
│   ├── Phase 1: Foundation / Preparation
│   ├── Phase 2: Core Structure
│   ├── Phase 3: Core Logic
│   ├── Phase 4: Data / Integration
│   ├── Phase 5: Interface Layer
│   ├── Phase 6: Validation & Error Handling
│   ├── Phase 7: Testing & Debugging
│   ├── Phase 8: Polish / Optimization
│   └── Phase 9: Delivery / Deployment / Handoff
│
├── 5. Implementation Contract
│   ├── Acceptance criteria
│   ├── File/module change list
│   ├── Test plan
│   ├── Risk list
│   ├── Assumptions
│   ├── Dependencies
│   └── Done criteria
│
└── 6. Final Plan Delivery
    ├── Summary
    ├── Workflow tree
    ├── Phase plan
    ├── Task checklist
    ├── Verification plan
    ├── Risk mitigation
    └── Next action
```

---

# Planning Workflow

## Phase 0 — Intake & Scope Lock

### Goal

Understand the goal and scope before planning.

### Actions

- Identify what the user wants to build, fix, or improve.
- Identify the business goal or technical goal.
- Separate in-scope and out-of-scope work.
- Identify constraints such as time, stack, dependencies, environment, and policies.
- If information is missing, ask only questions that block planning.

### Output

```markdown
## Scope
- Goal:
- In-scope:
- Out-of-scope:
- Constraints:
- Blocking questions:
```

### Gate

Proceed only when:

- The goal is clear.
- The scope is clear.
- No critical question blocks planning.

---

## Phase 1 — Research & Discovery

### Goal

Study the necessary information before creating the implementation plan.

### Research Targets

Inspect in this priority order:

1. User requirements
2. Existing codebase and folder structure
3. Existing architecture and conventions
4. Similar modules, screens, components, or endpoints
5. Framework/library constraints
6. Data model, API contract, or database schema
7. Security, performance, and deployment constraints
8. External documentation only when necessary

### Actions

- Read only relevant files or information.
- Identify affected components.
- Identify dependencies between modules.
- Identify existing patterns that should be followed.
- Identify pitfalls or risks that must be mitigated.

### Output

```markdown
## Research Findings
- Relevant stack:
- Existing patterns:
- Affected modules:
- Dependencies:
- Risks discovered:
- Planning impact:
```

### Gate

Proceed only when:

- The required work is understood.
- The affected parts of the system are known.
- Important constraints are known.

---

## Phase 2 — System Understanding

### Goal

Understand the current system and the target system.

### Actions

- Identify current state.
- Identify target state.
- Identify the gap between current and target state.
- Create a short data flow or control flow.
- Identify affected files/modules.
- Identify integration points.

### Output

```markdown
## System Understanding
- Current state:
- Target state:
- Gap:
- Affected components:
- Data/control flow:
- Integration points:
```

### Flow Template

```text
User Action / Input
→ Interface Layer
→ Application / Controller Layer
→ Domain / Service Layer
→ Data / External Layer
→ Response / UI Update / Output
```

### Gate

Proceed only when:

- The main flow is understood.
- The change points are known.
- The impact of the change is understood.

---

## Phase 3 — Strategy Design

### Goal

Choose the safest and most practical implementation strategy.

### Actions

- Choose a build strategy:
  - incremental build
  - vertical slice
  - module-first
  - API-first
  - UI-first prototype
  - refactor-before-feature
- Choose dependency order.
- Define migration strategy if needed.
- Define fallback or rollback strategy.
- Define validation gates between phases.

### Decision Criteria

Choose the approach that:

- Can be completed in small increments.
- Can be tested quickly.
- Can be rolled back easily.
- Has the smallest reasonable impact.
- Matches the existing architecture.
- Reduces the highest risks early.

### Output

```markdown
## Implementation Strategy
- Chosen approach:
- Why this approach:
- Build order:
- Dependency order:
- Rollback strategy:
- Validation gates:
```

---

## Phase 4 — Phase Breakdown

### Goal

Break the implementation into realistic and executable phases.

## Default Phase Structure

### Phase 1: Foundation / Preparation

Use this phase to prepare the foundation before real implementation.

Deliverables:

- Folder/module structure
- Configuration/setup
- Dependency check
- Interface/contract draft
- Base model/schema/type

Done Criteria:

- The project still builds.
- The structure is ready for the next phase.
- No heavy business logic is introduced in this phase.

---

### Phase 2: Core Structure

Use this phase to create the skeleton of the feature or system.

Deliverables:

- Main class/component/module
- Interface/service/controller skeleton
- Route/screen/entry point
- Compile-safe structure without misleading stubs

Done Criteria:

- The basic flow is connected.
- The build passes.
- No important logic remains unvalidated.

---

### Phase 3: Core Logic

Use this phase to implement the main logic.

Deliverables:

- Business rules
- Calculation/processing logic
- State management
- Main validation logic
- Domain/service behavior

Done Criteria:

- Happy path works.
- Important edge cases are handled.
- Logic is separated from UI/transport layers when appropriate.

---

### Phase 4: Data / Integration

Use this phase to connect databases, files, APIs, services, or external systems.

Deliverables:

- Repository/client/adapter
- Query/API call/file access
- Mapping/serialization
- Integration error handling

Done Criteria:

- Successful integration path works.
- Failure path is handled.
- No secrets are hardcoded.

---

### Phase 5: Interface Layer

Use this phase for UI, API, CLI, or desktop screens.

Deliverables:

- Screen/page/endpoint/command
- Input/output binding
- User feedback
- State update
- Basic accessibility/UX check if relevant

Done Criteria:

- The user can execute the main flow.
- Invalid input is communicated clearly.
- Interface layer does not contain excessive business logic.

---

### Phase 6: Validation & Error Handling

Use this phase to make the system robust.

Deliverables:

- Input validation
- Domain validation
- Exception handling
- Retry/fallback if necessary
- Logging without sensitive data exposure

Done Criteria:

- Main errors have clear messages.
- The application does not fail silently.
- Logs are useful for debugging.

---

### Phase 7: Testing & Debugging

Use this phase to prove the system works.

Deliverables:

- Unit tests
- Integration tests
- UI/API/manual test checklist
- Regression cases
- Build/run commands

Done Criteria:

- Important tests pass.
- Build/run passes, or the reason for not running is documented.
- Known issues are documented.

---

### Phase 8: Polish / Optimization

Use this phase to improve quality after the core flow works.

Deliverables:

- Performance improvement
- UX polish
- Code cleanup
- Duplication removal
- Documentation/comment updates only where necessary

Done Criteria:

- Code readability improves.
- Performance/UX improvement is measurable or explainable.
- No unnecessary behavior-changing refactor is introduced.

---

### Phase 9: Delivery / Deployment / Handoff

Use this phase to deliver the work.

Deliverables:

- Release note
- Run/deploy instructions
- Migration note if applicable
- Known risks
- Next step

Done Criteria:

- Another developer can continue the work.
- Run/test/deploy commands are clear.
- Rollback or recovery notes are included if risk exists.

---

# Phase Plan Output Template

Use this as the primary output format.

```markdown
# Implementation Plan: <Feature/System Name>

## 1. Objective
- Goal:
- Expected outcome:
- Success criteria:

## 2. Research Summary
- Existing system/context:
- Relevant modules:
- Constraints:
- Key findings:

## 3. Workflow Tree
```text
<System / Feature>
├── Input / Trigger
├── Interface Layer
├── Application Layer
├── Domain / Service Layer
├── Data / Integration Layer
├── Validation & Error Handling
├── Testing
└── Delivery
```

## 4. Phase Breakdown

### Phase 1 — Foundation / Preparation

- Tasks:
- Deliverables:
- Dependencies:
- Done criteria:
- Risks:

### Phase 2 — Core Structure

- Tasks:
- Deliverables:
- Dependencies:
- Done criteria:
- Risks:

### Phase 3 — Core Logic

- Tasks:
- Deliverables:
- Dependencies:
- Done criteria:
- Risks:

### Phase 4 — Data / Integration

- Tasks:
- Deliverables:
- Dependencies:
- Done criteria:
- Risks:

### Phase 5 — Interface Layer

- Tasks:
- Deliverables:
- Dependencies:
- Done criteria:
- Risks:

### Phase 6 — Validation & Error Handling

- Tasks:
- Deliverables:
- Dependencies:
- Done criteria:
- Risks:

### Phase 7 — Testing & Debugging

- Tasks:
- Test cases:
- Commands:
- Done criteria:
- Risks:

### Phase 8 — Polish / Optimization

- Tasks:
- Deliverables:
- Done criteria:

### Phase 9 — Delivery / Handoff

- Deliverables:
- Run instructions:
- Deployment notes:
- Rollback notes:
- Next steps:

## 5. Dependency Map

```text
Phase 1
└── Phase 2
    └── Phase 3
        ├── Phase 4
        ├── Phase 5
        └── Phase 6
            └── Phase 7
                └── Phase 8
                    └── Phase 9
```

## 6. Risk & Mitigation

- Risk:
  - Impact:
  - Mitigation:

## 7. Acceptance Criteria

- [ ] ...

## 8. Recommended Next Action

- ...

```

---

# Planning Rules by Project Type

## Web Frontend
Focus:
- Component tree
- State management
- Routing
- API contracts
- Loading and error states
- Responsive UI
- Basic accessibility

Recommended phases:
1. Route/component skeleton
2. API/state model
3. UI layout
4. Interaction logic
5. Validation/error/loading states
6. Tests/story/manual QA

## Backend / API
Focus:
- Endpoint contract
- Service logic
- Database transaction
- Authentication/authorization
- Validation
- Observability

Recommended phases:
1. API contract
2. DTO/schema/model
3. Service logic
4. Persistence/integration
5. Validation/error handling
6. Tests
7. Deployment

## Desktop / GUI App
Focus:
- Screen flow
- Event handling
- UI state
- Background task
- Local DB/file/API integration
- Packaging

Recommended phases:
1. Screen skeleton
2. Controller/viewmodel structure
3. Core event flow
4. Service/data integration
5. Validation/user feedback
6. Run/debug/package

## Data / Automation
Focus:
- Input/output contract
- Data validation
- Transformation pipeline
- Error recovery
- Logging
- Scheduling

Recommended phases:
1. Input/output spec
2. Pipeline skeleton
3. Transform logic
4. Validation/error handling
5. Run/test with sample data
6. Operationalization

## Refactor / Migration
Focus:
- Current behavior preservation
- Compatibility
- Incremental rollout
- Regression test
- Rollback

Recommended phases:
1. Map current behavior
2. Add safety tests
3. Isolate target module
4. Refactor/migrate incrementally
5. Compatibility check
6. Cleanup
7. Rollout

---

# Quality Gates

Every phase must include:
- Purpose
- Tasks
- Deliverables
- Dependencies
- Done criteria
- Risks
- Validation method

Never deliver a plan that only lists tasks without:
- Reasoning for phase order
- Dependency map
- Test/debug strategy
- Acceptance criteria
- Next action

---

# Research Compression Format

After research, summarize briefly:

```markdown
## Research Summary
- Context: <what the system/feature is about>
- Existing pattern: <pattern that should be followed>
- Key constraint: <important limitation>
- Main risk: <risk that should be mitigated early>
- Planning decision: <how research changes the phase order>
```

---

# Decision Rules

## If Requirement Is Clear

Create the full plan immediately. Do not ask redundant questions.

## If Requirement Is Partially Clear

Create the plan with explicit assumptions.

## If Requirement Is Blocking

Ask no more than 3 questions, such as:

1. What is the target platform?
2. Does the data source come from a database, API, or file?
3. Should this be built from scratch or integrated into an existing system?

## If Codebase Is Missing

Create a generic implementation plan and list the files/information needed next.

## If Task Is Large

Split it into:

- MVP phase
- Production-hardening phase
- Optimization phase
- Deployment phase

---

# Final Response Style

The agent must respond concisely but completely:

```markdown
## Plan Ready
- Goal:
- Strategy:
- Phases:
- Main risk:
- Next action:
```

If the user requests details, follow with the full Phase Breakdown.

---

# Anti-Patterns

Never:

- Plan without studying context.
- Split phases without dependency logic.
- Start with the full UI when core data/contract is unclear.
- Optimize before the core flow works.
- Put everything into one phase.
- Omit the test/debug phase.
- Omit acceptance criteria.
- Omit rollback/mitigation for risky work.
- Create a long plan that cannot realistically be implemented.

---

# One-Line Rule

**Study only necessary context → understand the system → choose a strategy → split phases by dependency → add validation gates → deliver an executable plan.**
