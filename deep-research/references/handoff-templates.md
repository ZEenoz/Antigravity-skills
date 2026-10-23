# Downstream Handoff Templates

Use these templates in Phase 4 of `deep-research` to tailor the dossier for the specific downstream consumer.

---

## 1. Coding & Feature Handoff Template
*Use when handing off to `intelligent-coding`, `tdd`, `implement`, or standard developer implementation.*

```markdown
### Downstream Handoff: Implementation Ready
- **Primary Objective**: [What needs to be implemented/refactored]
- **Target Files & Locations**:
  - `[filepath](file:///path/to/file)#L10-L45` — [Modification purpose]
- **Exact Signatures & Contracts**:
  ```typescript
  // Verified contract to follow
  interface TargetService { ... }
  ```
- **Repo Idioms & Patterns to Match**:
  - DI pattern: [e.g. constructor injection in Spring / NestJS]
  - Error handling: [e.g. custom AppResult<T> or checked exceptions]
- **Verification Command**:
  - `<command to test specific component>`
```

---

## 2. Debugging & Diagnostic Handoff Template
*Use when handing off to `precision-diagnostics`, `systematic-debugging`, or bug fixing.*

```markdown
### Downstream Handoff: Diagnostic Proof
- **Symptom**: [Error message, stack trace, or incorrect output]
- **Verified Root Cause Line**:
  - `[filepath](file:///path/to/file)#L120` — [Root cause explanation]
- **Falsified Possibilities (Do Not Re-investigate)**:
  - Ruled out DB lock: verified connection pool healthy at timestamp.
  - Ruled out missing headers: verified gateway forwards all cookies.
- **Minimal Repro Vector**:
  - Command: `<command>`
  - Payload: `{ "id": 999, "status": "PENDING" }`
- **Recommended Minimal Fix Seam**:
  - [Smallest safe point of modification to resolve without side effects]
```

---

## 3. Planning & Architecture Handoff Template
*Use when handing off to `phase-implementation-planner`, `writing-plans`, or `stress-tested-architecture`.*

```markdown
### Downstream Handoff: Architectural Baseline
- **System Boundaries & Touchpoints**:
  - Module A: `[src/module-a](file:///path/to/module-a)`
  - Module B: `[src/module-b](file:///path/to/module-b)`
- **Hard Constraints & Non-Negotiables**:
  - Backward compatibility: [e.g. API v1 clients still active]
  - Latency / SLA: [< 50ms p99]
- **Dependencies & Tools Required**:
  - `[package@version]`
- **Suggested Phasing Segments**:
  - Phase 1: Foundation & Data Migration
  - Phase 2: Core Domain Logic
  - Phase 3: Integration & Cutover
```

---

## 4. General / Decision-Making Handoff Template
*Use when presenting comprehensive findings to the user or team leads for strategic/technical decisions.*

```markdown
### Downstream Handoff: Decision Dossier
- **Options Researched**:
  1. **Option A**: [Name] — Pros: [...], Cons: [...], Risk: [Low/Med/High]
  2. **Option B**: [Name] — Pros: [...], Cons: [...], Risk: [Low/Med/High]
- **Triangulated Evidence**:
  - Source 1: [Official Documentation](URL)
  - Source 2: [Production Incident / Benchmark](URL or file)
- **Definitive Recommendation**:
  - [Recommended choice with explicit rationale and trade-off justification]
- **Decision Required From User**:
  - [Question or choice prompt]
```
