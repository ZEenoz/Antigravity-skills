---
name: debug-precision
description: ทักษะนี้กำหนดกระบวนการวิจัยและการแก้บั๊กที่เข้มงวดและมีหลายขั้นตอน โดยมีจุดมุ่งหมายเพื่อทำความเข้าใจรากของปัญหา ระบุสาเหตุที่แท้จริง และแก้ไขอย่างถาวร ต้องปฏิบัติตามทุกขั้นตอนตามลำดับ ห้ามข้ามขั้นตอนใดๆ
---

# 🐛 SKILL: Deep Bug Research & Precision Debugging

## Overview

This skill defines a **surgical debugging process** — not guesswork, not trial-and-error.
Every bug has a **root cause**. This skill finds it, understands it at the language level, and eliminates it permanently.

> **Mindset:** A bug is never random. It is deterministic. Given the same inputs and state, it will always reproduce. Find the determinism. Kill the bug.

---

## ⚡ When to Trigger This Skill

- User reports a **bug**, **error**, **crash**, or **unexpected behavior**
- Code runs but produces **wrong output**
- Code works sometimes but **fails intermittently**
- User pastes an **error message**, **stack trace**, or **log output**
- User says: "ทำไมถึง error?", "แก้บัคนี้ให้หน่อย", "ทำไมไม่ทำงาน?", "มันพัง"

---

## 🧬 Core Debugging Philosophy

```
❌ WRONG approach: Change things until it works
✅ RIGHT approach: Understand WHY it breaks → fix the exact cause → verify it's gone
```

**Three Laws of Precision Debugging:**

1. **Never fix what you don't understand** — a fix without understanding is a time bomb
2. **One change at a time** — multiple simultaneous changes hide which fix actually worked
3. **Prove the fix** — reproduce the bug before fixing, confirm it's gone after fixing

---

## 📋 Debugging Phases

---

### PHASE 1 — 🎯 TRIAGE: Classify the Bug

**Goal:** Understand what KIND of bug this is before any investigation.

**Bug Classification Matrix:**

| Class | Symptom | Examples |
|---|---|---|
| **Syntax Error** | Won't compile/parse | Missing colon, bracket mismatch |
| **Type Error** | Wrong type at runtime | `str + int`, `None.method()` |
| **Logic Error** | Wrong output, no crash | Off-by-one, wrong operator |
| **State / Mutation Bug** | Works once, fails on retry | Shared mutable state, dirty data |
| **Async / Concurrency Bug** | Intermittent / race condition | Thread race, deadlock, event loop issue |
| **Null / Undefined Bug** | Crash on missing value | NullPointerException, `None` dereference |
| **Boundary / Edge Case** | Fails on specific input | Empty list, 0, negative number, max int |
| **Environment Bug** | Works locally, fails in prod | Missing env var, wrong Python/Java version |
| **Dependency / Import Bug** | Module not found, wrong version | Version conflict, circular import |
| **Memory Bug** | Crash after running a while | Memory leak, OOM, stack overflow |
| **Encoding Bug** | Garbled text / crash on special chars | UTF-8 vs Latin-1, BOM issues |
| **Timeout / Performance Bug** | Too slow, hangs | N+1 query, blocking I/O, infinite loop |

**Actions:**

- Read the error message **word by word** — it usually contains the answer
- Classify the bug type from the matrix above
- Note: **where** it fails (file, line, function)
- Note: **when** it fails (always? on specific input? after N calls? intermittently?)
- Note: **what changed** recently (new code? new dependency? new environment?)

**Checklist:**

- [ ] Bug classified by type
- [ ] Failure location identified (file + line if available)
- [ ] Failure condition identified (always vs conditional)
- [ ] Recent changes noted

---

### PHASE 2 — 🔬 REPRODUCE: Lock the Bug Down

**Goal:** Create a **minimal reproducible case** — the smallest code that triggers the bug.

**Why This Matters:**

- Reproduction isolates the bug from unrelated code
- Minimal case reveals the exact condition causing failure
- Gives you a test to verify the fix worked

**Reproduction Steps:**

1. Run the failing code exactly as-is → confirm the bug exists
2. Remove unrelated code bit by bit until only the failing core remains
3. Create a **Minimal Reproducible Example (MRE)**:
   - No database calls if not needed
   - No API calls if not needed
   - Hardcoded inputs that trigger the bug
4. Document the MRE:

   ```
   Input:  [exact input that triggers the bug]
   Expected: [what should happen]
   Actual:   [what actually happens]
   Error:    [exact error message / stack trace]
   ```

**If the bug is intermittent:**

- Identify the pattern: time-based? load-based? sequence-based?
- Add logging to capture state at the moment of failure
- Increase run count to force reproduction

**Checklist:**

- [ ] Bug confirmed reproducible
- [ ] MRE created
- [ ] Input/Expected/Actual/Error documented

---

### PHASE 3 — 🧠 DEEP RESEARCH: Language-Level Investigation

**Goal:** Understand the bug at the **language internals level** — not surface-level.

---

#### 🐍 PYTHON — Deep Internals to Search

**Memory & Object Model:**

- Python uses **reference counting + cyclic GC** → search for `gc` module behavior if memory-related
- Everything is an object → `id()`, `is` vs `==` — search CPython object identity rules
- **Mutable default arguments** (`def f(x=[])`) — one of Python's most common hidden bugs

**Scope & Closure:**

- **LEGB rule** (Local → Enclosing → Global → Built-in) — search if variable resolution unexpected
- Late binding closures in loops → `lambda: i` captures reference, not value
- `global` vs `nonlocal` — search when inner function mutation fails

**Type System:**

- Duck typing pitfalls — `isinstance()` vs `type()` vs `hasattr()`
- `None` vs `False` vs `0` vs `""` vs `[]` — all falsy but NOT equal → search truthiness rules
- Integer interning: `a = 256; b = 256; a is b` → True. `a = 257; b = 257; a is b` → False (CPython impl detail)

**Concurrency:**

- **GIL (Global Interpreter Lock)** — search if threading not speeding up CPU tasks
- `threading` vs `asyncio` vs `multiprocessing` → wrong choice causes race conditions
- `asyncio` event loop — `await` only suspends the current coroutine; blocking code still blocks the loop

**Common Python Bug Hotspots to Search:**

```
- Mutable default argument bug
- Late-binding closure in lambda/loop
- List vs generator exhaustion (generator can only be iterated once)
- shallow copy vs deep copy (copy.copy vs copy.deepcopy)
- Exception swallowing (bare `except:` or `except Exception:`)
- Integer division Python 2 vs Python 3 (/ vs //)
- Encoding: open() default encoding differs by OS
- __dunder__ method resolution order (MRO) in multiple inheritance
- Circular imports
- Global state in modules (module-level variables shared across imports)
```

---

#### ☕ JAVA — Deep Internals to Search

**Memory Model:**

- **JVM Heap vs Stack** — objects on heap, primitives/references on stack
- **Garbage Collection** — GC pauses can cause timeout bugs; search G1GC, ZGC, CMS behavior
- **Memory Leaks in Java** — common causes: static collections, listeners not removed, ThreadLocal not cleared
- **String interning** — `"a" == "a"` (true, interned) vs `new String("a") == new String("a")` (false)

**Null Handling:**

- `NullPointerException` — #1 Java bug; search: uninitialized fields, null returns from methods, autoboxing null (`Integer i = null; int x = i;` → NPE)
- Use `Optional<T>` search if NPE patterns suspected

**Concurrency:**

- **Java Memory Model (JMM)** — visibility guarantees; search `volatile`, `synchronized`, `happens-before`
- **Race conditions** — `synchronized` vs `ReentrantLock` vs `AtomicInteger`
- **Deadlock** — two threads waiting on each other's locks; search lock ordering
- **ThreadLocal** — not cleaned up in thread pools causes data leakage between requests

**Collections:**

- `ConcurrentModificationException` — modifying collection while iterating
- `HashMap` vs `ConcurrentHashMap` — never use HashMap in concurrent code
- `ArrayList` vs `LinkedList` — wrong choice causes O(n²) performance bugs
- `equals()` + `hashCode()` contract — must override both or HashMap/Set breaks

**Common Java Bug Hotspots to Search:**

```
- Integer overflow (int max 2,147,483,647 → wraps to negative)
- Autoboxing NPE (Integer → int unboxing null)
- equals() vs == for String and Object comparison
- Exception handling: catch block swallowing stack trace (catch(e){log(e.getMessage())} loses root cause)
- Static mutable state in multi-threaded apps
- Resource leak: streams/connections not closed (use try-with-resources)
- Unchecked cast ClassCastException
- Reflection bypassing access modifiers causing unexpected behavior
- Spring Bean scope mismatch (singleton using prototype-scoped dependency)
- JPA/Hibernate LazyInitializationException (accessing lazy-loaded relation outside session)
```

---

#### 🌐 JAVASCRIPT / TYPESCRIPT — Deep Internals to Search

**Type Coercion & Equality:**

- `==` vs `===` — never use `==` in production code
- `typeof null === "object"` — historical JS bug
- `NaN !== NaN` — use `Number.isNaN()` not `=== NaN`

**Async:**

- Promise microtask queue vs macrotask queue — determines execution order
- `async/await` error handling — unhandled rejections crash Node.js
- `Promise.all` vs `Promise.allSettled` — all fails fast, allSettled waits for all

**Closures & `this`:**

- `this` binding in callbacks (arrow functions inherit `this`, regular functions don't)
- Closure capturing loop variable — use `let` not `var` in loops

---

#### 🦀 OTHER LANGUAGES — Universal Hotspots

**Go:** goroutine leaks, channel deadlock, nil pointer dereference, data race (`go run -race`)  
**Rust:** borrow checker violations, lifetime issues, `unwrap()` on None/Err in production  
**C/C++:** buffer overflow, use-after-free, dangling pointer, undefined behavior  
**SQL:** N+1 query, index not used, NULL comparison (`= NULL` vs `IS NULL`), transaction isolation level

---

### PHASE 4 — 🕵️ ROOT CAUSE ANALYSIS (RCA)

**Goal:** Find the **exact line and reason** the bug exists.

**RCA Toolkit:**

#### Tool 1 — Stack Trace Dissection

```
Read stack trace BOTTOM UP → bottom = origin, top = where it crashed
- Identify the FIRST line in YOUR code (not library code)
- That line is your entry point for investigation
- The line above it is where the bad value came from
```

#### Tool 2 — Binary Search Debugging

```
If you can't pinpoint the bug:
1. Add a checkpoint at the midpoint of the code
2. If midpoint is correct → bug is in second half
3. If midpoint is wrong → bug is in first half
4. Repeat until you isolate the exact line
(This is O(log n) debugging — fast even in large codebases)
```

#### Tool 3 — State Interrogation

```python
# Python — interrogate state at every boundary
print(f"[DEBUG] var={var!r} type={type(var).__name__}")  # !r shows repr, reveals None vs "None"

# Java
System.out.println("[DEBUG] var=" + var + " class=" + (var != null ? var.getClass() : "NULL"));

# JS
console.log('[DEBUG]', { var, type: typeof var, isNull: var === null });
```

#### Tool 4 — Assumption Audit

```
List every assumption the code makes:
- "This value is never null"  → Is it actually guaranteed?
- "This list always has items" → What if it's empty?
- "This runs sequentially"    → Is there async code involved?
- "This env var is set"       → Is it set in ALL environments?
- "This library works as documented" → Is the version correct?

Challenge each assumption. The bug lives where an assumption is false.
```

#### Tool 5 — Diff Analysis

```
If bug appeared after a change:
git diff HEAD~1  (or review the recent change)
Look for:
- Changed variable names
- Changed function signatures  
- New dependency version
- Removed null check
- Changed configuration value
```

**RCA Output Template:**

```
Root Cause: [One clear sentence — WHY the bug exists at the code level]
Location:   [File → Function → Line]
Trigger:    [The exact condition that causes it to fail]
Evidence:   [The specific code/output that proves this is the cause]
```

**Checklist:**

- [ ] Root cause identified (not just symptom)
- [ ] Exact location (file + function + line)
- [ ] Trigger condition understood
- [ ] Evidence documented

---

### PHASE 5 — 🔧 SURGICAL FIX

**Goal:** Apply the **minimal, correct fix** that eliminates the root cause.

**Fix Principles:**

#### Minimal Change Rule

```
Fix ONLY what is broken.
Do NOT:
- Refactor unrelated code
- Add "just in case" null checks everywhere
- Change working logic "while you're in there"
Each extra change is a risk. Keep the diff small.
```

#### Fix Strategy by Bug Class

| Bug Class | Fix Strategy |
|---|---|
| **Null / NPE** | Guard clause at entry point, not scattered checks |
| **Type Error** | Fix at the SOURCE of wrong type, not at the usage site |
| **Logic Error** | Rewrite the condition with truth table verification |
| **State Bug** | Isolate state — make it local, or use immutable patterns |
| **Race Condition** | Add proper synchronization at the shared resource, not at callers |
| **Async Bug** | Ensure all async paths are awaited; add error boundaries |
| **Boundary Bug** | Add explicit boundary checks at function entry |
| **Env Bug** | Add startup validation that fails fast with clear error message |
| **Dependency Bug** | Pin the correct version; add version assertion in code |
| **Memory Leak** | Find the reference keeping the object alive; remove it |

#### Fix Template

```
BEFORE (broken):
[original code]

WHY IT'S BROKEN:
[one-sentence explanation]

AFTER (fixed):
[corrected code]

WHY THIS FIXES IT:
[one-sentence explanation of what changed and why it's correct]
```

**Checklist:**

- [ ] Fix targets root cause (not symptom)
- [ ] Minimal change applied
- [ ] Fix explained clearly
- [ ] No unrelated changes included

---

### PHASE 6 — ✅ VERIFY: Prove the Bug is Dead

**Goal:** Confirm the fix works AND hasn't broken anything else.

**Verification Steps:**

#### Step 1 — Reproduce the Original Failure

```
Run the exact MRE from Phase 2.
Expected: It now passes.
If it still fails → RCA was wrong → return to Phase 4.
```

#### Step 2 — Test Edge Cases

```
Test inputs around the fix:
- The exact failing input (must pass now)
- Inputs just above/below the boundary
- Empty / null / zero inputs
- Maximum / minimum valid inputs
- Inputs that were working before (regression check)
```

#### Step 3 — Regression Check

```
Run all existing tests.
If no tests exist, manually test the 3 most common use cases.
Look for: did the fix break something that was working?
```

#### Step 4 — Code Review the Fix

```
Re-read the fixed code as if you're reviewing someone else's PR:
- Does it handle all the edge cases now?
- Is it readable — will the next developer understand why this check exists?
- Should a comment be added explaining the non-obvious fix?
- Should a test be added to prevent regression?
```

#### Verification Sign-off

```
✅ Original bug: [description] → FIXED
✅ Edge cases tested: [list]
✅ Regression check: PASSED
✅ Code review: CLEAN
```

---

### PHASE 7 — 📝 POST-MORTEM: Prevent Recurrence

**Goal:** Make sure this class of bug cannot silently return.

**Actions:**

- Write a **regression test** that would have caught this bug
- Add a **comment** in the code explaining the non-obvious constraint
- If it was a systemic issue → document the pattern in the team's coding guide
- Ask: **What allowed this bug to be written in the first place?**
  - Missing type hint / static analysis?
  - No null check convention?
  - Missing test coverage for this path?
  - Misleading variable name?
- Recommend **one preventive improvement** (linting rule, type annotation, code review checklist item)

---

## 🩺 Quick Diagnosis — Error Message Decoder

| Error Message Pattern | Likely Root Cause | Where to Look |
|---|---|---|
| `NullPointerException` / `AttributeError: 'NoneType'` | Value is None/null unexpectedly | Trace back WHERE the value came from |
| `IndexError` / `ArrayIndexOutOfBoundsException` | List shorter than expected | Check loop bounds + list population |
| `KeyError` | Key doesn't exist in dict/map | Use `.get()` / `containsKey()` — check data source |
| `RecursionError` / `StackOverflowError` | Missing base case or infinite recursion | Check termination condition |
| `TypeError: unsupported operand` | Wrong type passed to function | Trace the type at the call site |
| `ImportError` / `ClassNotFoundException` | Missing or misnamed module/class | Check spelling, installed packages, classpath |
| `TimeoutError` / thread hangs | Blocking call in async, or deadlock | Check for blocking I/O in async context |
| `UnicodeDecodeError` | File/stream encoding mismatch | Specify encoding explicitly (`encoding='utf-8'`) |
| `MemoryError` / OOM | Data too large, or memory leak | Profile memory; check for retention of large objects |
| `PermissionError` / `AccessDeniedException` | File/socket/OS permissions | Check file ownership and process permissions |
| `ConnectionRefusedError` | Service not running or wrong port | Verify the service is up and port config |
| `ConcurrentModificationException` | Iterating while modifying | Use iterator's remove() or copy the collection first |

---

## 🚫 Debugging Anti-Patterns — Never Do These

| Anti-Pattern | Why It's Dangerous |
|---|---|
| **Fixing the symptom, not the cause** | Bug reappears in a different form |
| **Adding `try/except` everywhere to silence errors** | Hides bugs, makes future debugging impossible |
| **Changing multiple things at once** | Can't know which change fixed it |
| **"It works on my machine"** | Must investigate the environment difference |
| **Assuming without verifying** | "It should be a string" — prove it with a log |
| **Fixing without reproducing first** | Can't confirm the fix worked |
| **Skipping regression tests** | Fix breaks something else undetected |
| **Googling the error and copy-pasting the first answer** | May fix a different version of the same error |
| **Reverting the fix when it seems "too simple"** | Simple fixes are often correct — trust the RCA |

---

## 📌 Quick Reference — Debugging Command Card

```bash
# Python — run with verbose traceback
python -W all -v script.py 2>&1

# Python — drop into debugger at crash point
python -m pdb script.py

# Python — memory profiling
pip install memory-profiler
python -m memory_profiler script.py

# Java — thread dump (find deadlocks)
jstack <pid>

# Java — heap dump (find memory leaks)
jmap -dump:format=b,file=heap.hprof <pid>

# Java — run with assertions enabled
java -ea MainClass

# Node.js — inspect async stack traces
node --async-stack-traces script.js

# Go — race condition detector
go run -race main.go

# General — check if env var is set
echo $VARIABLE_NAME   # Unix
echo %VARIABLE_NAME%  # Windows
```

---

## 📌 Phase Summary

```
Phase 1 → TRIAGE      : Classify bug type before touching anything
Phase 2 → REPRODUCE   : Create minimal reproducible example
Phase 3 → RESEARCH    : Dig into language internals (Python/Java/JS/etc.)
Phase 4 → ROOT CAUSE  : Find the EXACT line and WHY using RCA tools
Phase 5 → FIX         : Minimal surgical change targeting root cause only
Phase 6 → VERIFY      : Prove the bug is dead + regression check
Phase 7 → POST-MORTEM : Prevent the same bug from ever coming back
```

> **Final Rule:** If you cannot explain in one sentence **why** the bug exists at the code/language level, you have not finished Phase 4. Do not proceed to Phase 5.
