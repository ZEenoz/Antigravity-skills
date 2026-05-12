---
name: precision-coding
description: ทักษะนี้กำหนดกระบวนการเขียนโค้ดที่เข้มงวดและมีหลายขั้นตอน ซึ่งรับประกันได้ว่าโค้ดที่ได้จะมีคุณภาพสูง เชื่อถือได้ และบำรุงรักษาได้ง่าย ต้องปฏิบัติตามทุกขั้นตอนตามลำดับ ห้ามข้ามขั้นตอนใดๆ
---

# 🧠 SKILL: Precision Coding Workflow

## Overview

This skill defines a **rigorous, multi-phase coding process** that ensures high-quality, reliable, and maintainable code output. Follow every phase in sequence — skipping steps is not permitted.

---

## ⚡ When to Trigger This Skill

- User requests building, writing, or modifying **any code**
- User asks to **fix a bug**, **refactor**, or **optimize** existing code
- User asks to **create a feature**, **API**, **script**, **component**, or **system**
- Any task that produces executable or deployable output

---

## 📋 Workflow Phases

---

### PHASE 1 — 🔍 VERIFY & CHECK CAREFULLY

**Goal:** Fully understand the request before touching any code.

**Actions:**

- Re-read the user's request at least **twice**
- Identify **ambiguities** — list them explicitly before proceeding
- Clarify the following:
  - What is the **expected input**?
  - What is the **expected output**?
  - What are the **constraints** (language, framework, performance, security)?
  - Are there **edge cases** mentioned or implied?
  - Is there **existing code** to integrate with?
- If any point is unclear → **ask the user before proceeding**
- Confirm the **scope**: what is in-scope and what is explicitly out-of-scope

**Checklist before moving on:**

- [ ] Request fully understood
- [ ] Ambiguities resolved
- [ ] Constraints identified
- [ ] Edge cases noted

---

### PHASE 2 — 🌐 SEARCH INFORMATION THOROUGHLY

**Goal:** Gather accurate, up-to-date, and relevant knowledge before writing a single line.

**Actions:**

- Search for **official documentation** of all libraries, APIs, and frameworks involved
- Search for **known pitfalls**, **deprecations**, and **breaking changes** in the relevant versions
- Search for **best practices** and **design patterns** applicable to this problem
- Search for **similar implementations** to understand common approaches
- Verify **version compatibility** between dependencies
- If security-sensitive: search for **CVEs**, **OWASP guidelines**, or **known vulnerabilities**

**Search Priority Order:**

1. Official docs (highest trust)
2. GitHub source code / changelogs
3. Reputable tech blogs (Vercel, Cloudflare, AWS, etc.)
4. Stack Overflow (cross-verify with multiple sources)
5. Community forums (lowest trust — always verify)

**Checklist before moving on:**

- [ ] All relevant docs reviewed
- [ ] Version/compatibility confirmed
- [ ] Best practices identified
- [ ] Pitfalls and anti-patterns noted

---

### PHASE 3 — 📚 LEARN FROM SEARCH RESULTS

**Goal:** Synthesize research into a solid understanding before coding.

**Actions:**

- Summarize key findings in your reasoning (internally or to the user if helpful)
- Identify the **most appropriate approach** based on research
- Choose libraries/tools only if they are:
  - Actively maintained
  - Widely adopted
  - Appropriate for the user's stack
- Discard approaches that are **deprecated**, **overly complex**, or **mismatched** to constraints
- Draft a **mental model** or **pseudocode outline** of the solution
- Identify which parts carry **risk** (complex logic, third-party dependencies, async flows)

**Output of this phase:**

- Chosen approach with rationale
- List of dependencies (name + version)
- High-level pseudocode or architecture sketch

---

### PHASE 4 — 🏗️ BUILD CODE

**Goal:** Write clean, correct, production-quality code.

**Coding Standards:**

- Follow **language-specific conventions** (PEP8 for Python, ESLint rules for JS/TS, etc.)
- Use **meaningful variable and function names** — no `x`, `tmp`, `foo` in production code
- Keep functions **small and single-purpose** (Single Responsibility Principle)
- Add **inline comments** for non-obvious logic
- Add **docstrings / JSDoc** for all public functions
- Handle **errors explicitly** — never silent failures
- Validate all **inputs** at boundaries
- Avoid **hardcoded values** — use constants or config

**Structure:**

```
1. Imports / Dependencies
2. Constants / Config
3. Helper Functions
4. Core Logic
5. Entry Point / Exports
6. Error Handlers
```

**Security Rules (non-negotiable):**

- Never expose secrets, API keys, or credentials in code
- Sanitize all user inputs
- Use parameterized queries for any DB interaction
- Apply principle of least privilege

**Checklist before moving on:**

- [ ] Code follows language conventions
- [ ] Error handling implemented
- [ ] Input validation in place
- [ ] No hardcoded secrets
- [ ] Code is readable without explanation

---

### PHASE 5 — 🔁 RECHECK CODE

**Goal:** Catch bugs, logic errors, and vulnerabilities before delivery.

**Recheck Sequence:**

#### 5A — Logic Correctness

- Trace through the code **manually** with at least 2 example inputs
- Include a **happy path** case and at least one **edge case**
- Verify **return values** match what consumers expect
- Check all **conditional branches** — are all paths handled?
- Verify **loop termination** conditions

#### 5B — Error & Exception Handling

- What happens if an API call fails?
- What happens if input is `null`, `undefined`, empty, or malformed?
- Are errors **caught** and handled gracefully?
- Are errors **logged** appropriately?

#### 5C — Performance

- Are there **N+1 query** problems?
- Are there **unnecessary re-renders** (React)?
- Are there **blocking operations** that should be async?
- Is data being **fetched multiple times** when it could be cached?

#### 5D — Security Scan

- SQL injection risk?
- XSS risk (if web)?
- Unvalidated redirects?
- Sensitive data in logs?

#### 5E — Syntax & Typos

- Re-read every line for typos, missing brackets, wrong operators
- Check imports — are they all used? Are any missing?
- Check for unused variables (dead code)

**Checklist before moving on:**

- [ ] Manual trace completed (happy path + edge case)
- [ ] All branches handled
- [ ] Errors handled gracefully
- [ ] No performance anti-patterns
- [ ] Security scan passed
- [ ] No dead code or unused imports

---

### PHASE 6 — 📊 REVIEW & DELIVER

**Goal:** Final quality gate before presenting output to the user.

**Actions:**

- Read the full code output **from top to bottom** one final time
- Verify it **solves the original request** (compare against Phase 1 checklist)
- Ensure **no placeholder code** remains (`TODO`, `FIXME`, `...`, `pass`, `// implement this`)
- Confirm the code is **complete and runnable** as-is
- Write a **clear delivery note** that includes:
  - What was built
  - How to run / integrate it
  - Any assumptions made
  - Any known limitations
  - Suggested next steps (if applicable)

**Delivery Format:**

```
## ✅ What Was Built
[Short description]

## 🚀 How to Run
[Commands or integration instructions]

## ⚠️ Assumptions
[List any assumptions made during implementation]

## 🔮 Suggested Next Steps
[Optional improvements or follow-ups]
```

**Final Checklist:**

- [ ] Code solves the original request
- [ ] No placeholder or stub code
- [ ] Delivery note written
- [ ] User can run this without needing to ask follow-up questions

---

## 🚫 Anti-Patterns to Never Do

| Anti-Pattern | Why It's Banned |
|---|---|
| Skip Phase 1 and assume intent | Causes wrong output, wasted effort |
| Copy-paste code without understanding it | Introduces hidden bugs |
| Write code before searching docs | Leads to deprecated API usage |
| Silent error handling (`catch {}`) | Hides failures, impossible to debug |
| Deliver incomplete / stub code | Wastes user's time |
| Hardcode secrets or credentials | Critical security vulnerability |
| Skip edge case testing in Phase 5 | Bugs reach production |
| Use deprecated packages | Breaks in future, security risk |

---

## 🏆 Quality Bar

Every code delivery must meet this bar:

| Criterion | Standard |
|---|---|
| **Correctness** | Works on happy path AND edge cases |
| **Readability** | A new developer can understand it in 5 minutes |
| **Robustness** | Handles errors gracefully, never crashes silently |
| **Security** | No obvious vulnerabilities introduced |
| **Completeness** | Runnable as-is, no stubs or TODOs |
| **Relevance** | Directly solves what the user asked |

---

## 📌 Quick Reference Card

```
Phase 1 → VERIFY     : Understand fully before starting
Phase 2 → SEARCH     : Find official docs, best practices, pitfalls  
Phase 3 → LEARN      : Synthesize research into a plan
Phase 4 → BUILD      : Write clean, standards-compliant code
Phase 5 → RECHECK    : Logic trace + error check + security scan
Phase 6 → REVIEW     : Final gate → deliver with clear notes
```

> **Rule:** If any phase reveals a problem that invalidates a previous phase, **loop back** — never push forward with a known issue unresolved.
