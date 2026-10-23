---
name: stress-tested-architecture
description: >
  Combines 'brainstorming' and 'grilling'. Interactive design, RFC, and system
  architecture workflow that couples collaborative exploration with adversarial
  stress-testing. Features Three-Path Classification (Spike, Bounded, Architectural),
  a branching Design Tree, structured Grilling Rounds (The Frontier) with recommended
  answers, and rigorous scrutiny on failure modes, scale, and trade-offs before
  locking specifications. Triggers on /stress-tested-architecture, /grill-architecture,
  "design architecture", "brainstorm and grill", "stress test plan", or "system design RFC".
license: MIT
---

# Stress-Tested Architecture: Brainstorm & Grill

Turn ideas into resilient, production-ready system architectures through collaborative ideation combined with adversarial stress-testing.

## The Core Principle

> **Explore openly, grill ruthlessly, lock before building.**  
> Never rubber-stamp user assumptions. Never debate without presenting clear recommendations.

<HARD-GATE>
Do NOT write code, generate boilerplate, or take implementation actions until your human partner has explicitly approved the design.
</HARD-GATE>

---

## 1. Request Classification

Before asking your first question, classify the request and state it out loud:

* **Spike:** Feasibility question (*"Is it possible to..."*, *"Can we test if..."*). Present question + 2-3 sentence probe plan, get approval, test as cheaply as possible, report recommendation. Everything built remains throwaway.
* **Bounded:** Well-scoped change to existing flow in this repository (e.g. new flag, one endpoint). Ask clarifying questions, present a short design in chat (approach, affected files, tests), and STOP until explicit approval is granted.
* **Architectural:** New subsystems, multi-module features, altered API boundaries, or complex refactoring. Follow the full Design Tree & Grilling process below.

*Rule:* When in doubt, choose the heavier path. Hidden complexity discovered mid-task immediately upgrades the path.

---

## 2. The Design Tree & Grilling Protocol

Architectures are trees of decisions: foundational choices branch into secondary implementation details.

### The Frontier & Structured Rounds
Ask only questions on the **frontier** (decisions whose prerequisites are already settled). Do not ask questions that depend on unanswered questions.

Format each round clearly with options and recommendations:

```markdown
❓ **Q1 - [Decision Title]**: [Context and concrete trade-offs between Option A and Option B]
➡️ **Recommendation**: [Recommended choice and why, noting edge case / scale trade-offs]

---

❓ **Q2 - [Decision Title]**: [Context and options]
➡️ **Recommendation**: [Recommended choice]
```

### Fact-Finding vs. Decision-Making
* **Agent's Job (Facts):** Inspect existing codebase, search documentation, review dependencies, and check environment constraints. Never ask the user for facts you can discover yourself.
* **User's Job (Decisions):** Decide business priorities, risk tolerance, and directional choices from your recommended options.

---

## 3. The 5 Grilling Vectors (Adversarial Scrutiny)

Every proposed architecture must be stress-tested against these 5 failure vectors before finalizing:

1. **Failure Modes & Resilience:** What happens if the network drops, third-party API times out, DB locks, or partial writes occur? Where is the circuit breaker / retry policy?
2. **Scale & Concurrency:** How does this behave at 10x or 100x volume? Are there race conditions, memory leaks, or N+1 query bottlenecks?
3. **Seams & Isolation:** Can each unit be tested in total isolation without booting the universe? Are internal implementation details leaking across boundaries?
4. **YAGNI & Simplicity (Ponytail Lens):** Are there unrequested abstractions (interfaces with 1 implementation, speculative factories)? What can be deleted?
5. **Rollback & Blast Radius:** If a deployment fails or data is corrupted, how is state restored safely?

---

## 4. Architectural Spec & Self-Review

When the frontier is resolved, write the design specification to:
`docs/specs/YYYY-MM-DD-<topic>-design.md`

### Mandatory Spec Sections:
1. **Context & Goals:** Problem statement, in-scope, and explicit out-of-scope.
2. **System Architecture & Data Flow:** Component boundaries, contracts, sequence.
3. **Failure Handling & Edge Cases:** Fallbacks, retries, and data consistency.
4. **Testing Strategy:** Unit seams, integration harnesses, and verification plan.
5. **Alternative Approaches Rejected:** Why simpler or competing designs were discarded.

### Spec Self-Review Gate:
Before showing the spec to the user, execute an inline self-review:
* [ ] **Placeholder scan:** No "TODO", "TBD", or vague requirements.
* [ ] **Consistency check:** Architecture matches data flow and component responsibilities.
* [ ] **Ambiguity check:** All critical requirements are unambiguous and verifiable.
* [ ] **Scope check:** Sized appropriately for an implementation plan (or decomposed into sub-phases).

---

## 5. Handoff to Implementation

Once the user approves the written specification:
* Invoke `writing-plans` (or `phase-implementation-planner`) to generate a step-by-step implementation plan.
* Transition cleanly from architecture mode to execution mode.
