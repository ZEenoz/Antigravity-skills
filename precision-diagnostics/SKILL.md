---
name: precision-diagnostics
description: >
  Combines 'systematic-debugging' and 'diagnosing-bugs'. Strict multi-phase
  root-cause diagnosis protocol for hard bugs, intermittent failures, test
  breakages, and performance regressions. Enforces building a tight deterministic
  feedback loop (repro), multi-boundary instrumentation, ranked falsifiable
  hypotheses, and minimal root-cause fixes with regression tests before any code
  edits. Triggers on /precision-diagnostics, /diagnose, "diagnose bug", "debug hard bug",
  "systematic debug", or any persistent/intermittent software failure.
license: MIT
---

# Precision Diagnostics: Systematic Root-Cause Debugger

Combines the investigative rigor of **Systematic Debugging** with the tight-loop engineering of **Diagnosing Bugs**.

## The Iron Law

```text
NO FIXES WITHOUT A TIGHT FEEDBACK LOOP AND ROOT-CAUSE INVESTIGATION FIRST.
Symptom fixes are failure. Guess-and-check is forbidden.
```

---

## The 6 Diagnostic Phases

You MUST complete each phase in order before proceeding to the next.

```text
[Phase 1: Build Feedback Loop] → [Phase 2: Reproduce & Minimise] → [Phase 3: Ranked Hypotheses]
       ↓                                                                      ↓
[Phase 6: Cleanup & Verify] ← [Phase 5: Fix at Source & Test] ← [Phase 4: Targeted Probing]
```

---

### Phase 1: Build a Tight Feedback Loop (Signal First)

If you do not have an automated pass/fail signal that goes red on *this specific symptom*, no amount of code reading will save you.

**Ways to construct a feedback loop (in order of preference):**
1. **Failing test** at the closest seam: unit, integration, or e2e.
2. **Curl / HTTP script** against a running local server.
3. **CLI invocation** diffing stdout/stderr against a known-good snapshot.
4. **Headless script** (Playwright/Puppeteer) driving the UI and asserting on DOM/console.
5. **Replay a captured trace:** Save raw network payload or event log to disk and replay in isolation.
6. **Throwaway harness:** Minimal script running the bug path with a single call.
7. **Property / fuzz loop:** For intermittent bugs, run 100-1000 iterations to force failure.
8. **Bisection harness:** Automate `git bisect run <script>` between working and broken commits.
9. **HITL script:** Use `scripts/hitl-loop.template.sh` when a human action is mandatory.

**Tighten the loop:**
- **Fast:** Executes in seconds, not minutes.
- **Deterministic:** Same verdict every run (for race conditions/flaky bugs, raise reproduction rate by stressing/looping until reproducible).
- **Red-capable:** Specifically catches the user's exact symptom, not just "didn't crash".

> **Hard Gate:** Name **one command** you have run that reproducibly goes red on this bug. If no such command exists, DO NOT hypothesize or touch code.

---

### Phase 2: Reproduce & Minimise

1. **Verify Symptom:** Confirm the failure matches the user's report, not an unrelated adjacent error.
2. **Minimise the Surface:** Cut inputs, callers, config, and steps **one at a time**, re-running the loop after each cut.
3. **Load-bearing Check:** Keep only what is strictly necessary to trigger the failure. Removing any remaining element must make the loop pass (turn green).

*Benefit:* Minimising collapses the search space and produces a clean regression test.

---

### Phase 3: Form Ranked, Falsifiable Hypotheses

Do not anchor on the first plausible thought. Generate **3–5 ranked hypotheses** before testing any of them.

**Every hypothesis must be falsifiable with a concrete prediction:**
> Pattern: *"If [X] is the root cause, then [changing Y] will make the bug disappear, while [changing Z] will make it worse."*

* If you cannot state a prediction, discard the hypothesis.
* Present the ranked list to the user before testing (or proceed with ranking if user is away).

---

### Phase 4: Targeted Probing & Root-Cause Tracing

Test hypotheses by changing **one variable at a time**:

1. **Multi-Component Boundary Logging:**
   When data traverses layers (Workflow → Build → API → DB):
   - Instrument input and output at each boundary.
   - Run once to isolate *which layer* corrupts the state.
2. **Backward Data Flow Tracing:**
   - Where does the bad value originate? Trace backward up the call stack to the trigger source (see `references/root-cause-tracing.md`).
3. **Tagged Instrumentation:**
   - Tag every temporary log with a unique searchable prefix (e.g., `[DEBUG-f8a1]`).
   - Never use untagged temporary logs.
4. **Performance Issues:**
   - Never guess with logs. Establish a baseline benchmark (profiler, `performance.now()`, query explain plan) and bisect.

---

### Phase 5: Fix at Source & Regression Test

1. **Fix Root Cause, Not Symptom:**
   - Grep all callers of the function.
   - Fix the root issue where all callers route through. Never patch individual symptoms across callers.
2. **Regression Test First:**
   - Convert the minimised repro into a permanent test at the correct seam.
   - Watch it fail (RED).
3. **Apply Minimal Fix:**
   - Apply the single minimal change addressing the root cause.
   - Watch the regression test pass (GREEN).
4. **Verify Original Scope:**
   - Re-run the Phase 1 feedback loop against the original un-minimised scenario.
5. **Circuit Breaker (3-Fix Rule):**
   - If 2 fixes fail: STOP and re-examine Phase 1 evidence.
   - **If 3 fixes fail:** STOP completely. This is an **architectural problem**, not a bug. Discuss architectural refactoring with the user before attempting a 4th fix.

---

### Phase 6: Cleanup & Verification

Before declaring the task complete:
- [ ] Original bug scenario no longer reproduces.
- [ ] Regression test passes consistently.
- [ ] All `[DEBUG-...]` tags and temporary logs are completely removed (`grep` the prefix).
- [ ] Throwaway scripts deleted or moved to a dedicated debug folder.
- [ ] Summary report clearly states: Root cause mechanism, file changed, and verification proof.

---

## Red Flags & Anti-Patterns

STOP immediately and return to Phase 1 if you encounter:
- *"Just try changing this and see if it works."*
- *"Quick fix for now, investigate later."*
- Proposing code edits before seeing the feedback loop run red.
- Patching callers instead of fixing shared logic at the source.
- Attempting fix #4 without questioning the underlying architecture.
