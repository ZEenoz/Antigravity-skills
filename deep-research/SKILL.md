---
name: deep-research
description: Universal deep research, evidence gathering, and pre-execution reconnaissance skill. Use when you need to rigorously investigate a codebase, bug/error, architecture, technical documentation, or general domain BEFORE handing off findings to downstream steps (planning, coding, debugging, or decision making). Triggers on "deep research", "research this", "investigate", "gather facts", "code reconnaissance", "root cause research", or as a mandatory intake step before complex coding or debugging tasks.
---

# Deep Research & Evidence Dossier

A universal pre-execution investigation protocol. Collects ground truth, eliminates guesswork, verifies primary sources, and packages structured evidence for downstream consumers (planners, coders, debuggers, or decision makers).

---

## Core Principles

1. **Zero Unverified Assumptions**: Every assertion must link to verifiable evidence (exact file path + line number, official documentation URL + excerpt, or reproducible terminal output).
2. **Primary Sources First**: Prioritize raw code AST, live runtime behavior, official specifications, and vendor source over secondary blog posts or LLM pre-training intuition.
3. **Falsification & Negative Proof**: Active search for disconfirming evidence, edge cases, breaking changes, and constraint boundaries.
4. **Handoff-First Output**: Structure findings specifically for the next agent or step to consume without re-investigating.

---

## 4-Phase Research Protocol

```
[Phase 1: Framing & Scope] 
        ↓
[Phase 2: Multi-Source Gathering] (Code AST / Web / Runtime / Diffs)
        ↓
[Phase 3: Falsification & Triangulation] (Eliminate red herrings)
        ↓
[Phase 4: Downstream Handoff Dossier] (RESEARCH.md / Structured Artifact)
```

---

### Phase 1: Framing & Scope Definition

Before querying or reading files, establish:
1. **Target Question**: What precise unknown must be answered?
2. **Downstream Consumer**: Who or what uses this result next?
   - `Planning` (e.g. `phase-implementation-planner`, `writing-plans`)
   - `Implementation` (e.g. `intelligent-coding`, `tdd`, `caveman-coding`)
   - `Debugging` (e.g. `precision-diagnostics`, `systematic-debugging`)
   - `Decision / Architecture` (e.g. `stress-tested-architecture`, user review)
3. **Stop Criteria**: What specific evidence proves the research is complete?

---

### Phase 2: Multi-Source Deep Investigation

Select the appropriate research mode(s):

#### Mode A: Codebase Reconnaissance (Coding / Refactoring / Feature Intake)
- **Symbol & Contract Tracing**: Locate exact type definitions, function signatures, caller hierarchies, and lifecycle hooks.
- **Dependency & Config Inspection**: Check `package.json`, `pom.xml`, `build.gradle`, lockfiles, and environment config for exact versions and flags.
- **Pattern & Idiom Extraction**: Find existing conventions in the repo (naming, error handling, DI, immutability) to match style.
- **Blast Radius Mapping**: Identify all files and modules importing or touching the target boundaries.

#### Mode B: Diagnostic Investigation (Debugging / Regression / Failure Intake)
- **Failure Boundary**: Isolate exact failing file, line, method, and input payload.
- **Git Archaeology**: Check `git log -S` or `git blame` on affected lines to discover why it was originally written this way and what recent commits altered it.
- **State & Invariant Violation**: Document what state was expected vs what was observed.
- **Minimal Reproduction Vector**: Identify the smallest test case or command that demonstrates the issue.

#### Mode C: External & Technical Spike (Docs / Libraries / APIs / RFCs)
- **Official Specification / Docs**: Fetch primary doc pages, API reference, or GitHub source release notes.
- **Compatibility Matrix**: Verify platform, language version, and runtime constraints.
- **Breaking Changes / Deprecations**: Search official migration guides or issue trackers for known caveats.

#### Mode D: General & Multi-Domain Research (Strategy / System Evaluation / Open-ended)
- **Source Triangulation**: Cross-validate claims against at least 2-3 independent, reputable primary sources.
- **Trade-Off & Constraint Analysis**: Map pros, cons, operational overhead, and failure modes.

---

### Phase 3: Falsification & Triangulation

To prevent hallucinations and false assumptions:
1. **Challenge First Conclusions**: If a hypothesis seems obvious, actively search for code paths or documentation that contradict it.
2. **Rule Out Red Herrings**: Note rejected hypotheses and cite why they were eliminated so downstream steps do not re-explore dead ends.
3. **Explicit Unknowns**: If information is unobtainable (e.g., missing secrets, unreleased code), explicitly tag it as `[UNRESOLVED UNKNOWN]` instead of guessing.

---

### Phase 4: Downstream Handoff Dossier

Produce a clean Markdown report (optionally saved to `RESEARCH.md` or displayed directly). Always follow this structured layout:

```markdown
# Deep Research Dossier: [Topic / Problem Statement]

## 1. Executive Summary
- 2-3 concise bullet points summarizing the core findings and conclusion.

## 2. Ground Truth & Evidence Matrix
| Item / Claim | Primary Source / Location | Verified Facts |
| :--- | :--- | :--- |
| e.g. Auth Token Expiry | `src/auth/jwt.ts#L42-L58` | Verified: Tokens expire in 15m; refresh logic missing catch |
| e.g. Library Version | `package.json#L24` | `@tanstack/react-query@5.28.0` (v5 breaking changes apply) |

## 3. Invariants & Hard Constraints
- Constraints that MUST NOT be violated by downstream implementations (e.g. backward compatibility, performance budgets, lockfile pins).

## 4. Eliminated Hypotheses & Traps
- **Hypothesis X**: Rejected because [evidence/code path].
- **Pitfall Y**: Avoid doing [Z] because [reasons discovered in research].

## 5. Downstream Action Handoff
- **Recommended Next Step**: [e.g. Proceed to `phase-implementation-planner` / Run `tdd`]
- **Input Payload for Next Step**:
  - Target files: `[file1](file:///path/to/file1)`, `[file2](file:///path/to/file2)`
  - Exact symbols/functions to modify: `FunctionName()`, `ClassName`
  - Critical test vectors / reproduction commands: `<command>`
```

---

## Operational Guidelines

- **Conciseness over bloat**: Extract essence, citations, and actionable facts; omit rambling narrative.
- **Clickable links**: Always use markdown links (`[file.ext](file:///absolute/path)`) for local files and proper URLs for online sources.
- **Preserve evidence**: Quote verbatim critical error lines, API schemas, or code snippets (keep snippets under 20 lines).
- **Templates**: See `references/handoff-templates.md` for tailored output formats for specific downstream consumers.
