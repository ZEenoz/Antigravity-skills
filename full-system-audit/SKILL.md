---
name: full-system-audit
version: 1.0.0
description: Skill for auditing an entire project/system at a high level and detailed level. Focuses on architecture, code quality, UI/UX, performance, security, configuration, testing, maintainability, risks, and actionable improvement priorities. Designed for token-efficient audit reports.
language_support: Thai, English, mixed Thai-English technical writing
optimized_for: system audit, code audit, Java/JavaFX projects, enterprise apps, quality review, risk review, token efficiency
---

# SKILL: Full System Audit

## Mission
Audit ภาพรวมระบบทั้งหมดแบบกระชับ แต่ครบจุดสำคัญ เพื่อหา **จุดเสี่ยง, จุดบกพร่อง, จุดควรปรับปรุง, และลำดับความสำคัญในการแก้ไข**

Core rule:
> Audit first. Prioritize risk. Recommend actionable fixes. Keep output concise.

---

## 1. When To Use

ใช้ Skill นี้เมื่อผู้ใช้ต้องการ:
- Audit ระบบทั้งหมด
- Review project ภาพรวม
- ตรวจคุณภาพโค้ด
- ตรวจ architecture
- ตรวจ UI/UX
- ตรวจ performance
- ตรวจ security/config
- ตรวจ hardcoding
- ตรวจ test coverage / debug readiness
- ตรวจ maintainability
- หาจุดที่ควร refactor
- สรุป technical debt
- จัด priority สิ่งที่ต้องแก้

---

## 2. Audit Scope

Audit ต้องดูตามหมวดหลัก:

```text
Full System Audit
├── 1. Project Structure
├── 2. Architecture
├── 3. Code Quality
├── 4. UI/UX
├── 5. Responsiveness
├── 6. Error Handling
├── 7. Security
├── 8. Hardcoding / Config
├── 9. Performance
├── 10. Testing / Debug Readiness
├── 11. Maintainability
├── 12. Documentation
└── 13. Priority Fix Plan
```

---

## 3. Response Style

ตอบแบบประหยัด Token:
- ไม่เกริ่นยาว
- ไม่อธิบายทฤษฎี
- ไม่ list เรื่องที่ไม่เกี่ยว
- เน้น issue ที่มีผลจริง
- แบ่งตาม priority
- ใช้ bullet สั้น ๆ
- ให้ fix ที่ทำได้จริง

Default output:

```markdown
# Audit Report: <Project/System>

## Overall Score
- Score: <x>/10
- Status: <Good / Needs Work / Risky>

## Critical Issues
- ...

## High Priority
- ...

## Medium Priority
- ...

## Low Priority
- ...

## Recommended Fix Plan
1. ...
2. ...
3. ...
```

---

## 4. Audit Severity

ใช้ระดับความรุนแรงนี้:

```text
Critical = ทำให้ระบบพัง / security risk / data loss / production blocker
High     = กระทบ user หลัก / maintain ยาก / performance แย่ / bug risk สูง
Medium   = ควรแก้เพื่อคุณภาพ / UX / readability / future-proof
Low      = polish / cleanup / nice-to-have
```

ทุก issue ต้องมี:
- ปัญหา
- ผลกระทบ
- วิธีแก้
- Priority

Format:

```markdown
- ปัญหา: <issue>
  - ผลกระทบ: <impact>
  - แก้: <actionable fix>
  - Priority: Critical / High / Medium / Low
```

---

## 5. Audit Workflow

### Step 1 — Understand System Context
ตรวจ:
- project type
- stack
- build tool
- main modules
- entry points
- data source
- UI framework
- deployment/runtime

Output ถ้าจำเป็น:

```markdown
## Context
- Stack:
- Main modules:
- Entry points:
- Runtime:
```

---

### Step 2 — Project Structure Audit
ตรวจ:
- folder structure ชัดไหม
- module แยกดีไหม
- naming convention สม่ำเสมอไหม
- file ใหญ่เกินไปไหม
- มี dead/unused files ไหม
- resources/config จัดถูกที่ไหม

Common issues:
- controller/service/repository ปนกัน
- ไฟล์ยาวเกิน
- package naming ไม่สม่ำเสมอ
- resource path กระจัดกระจาย

Output:

```markdown
## Project Structure
- ดี:
- ต้องแก้:
- แนะนำ:
```

---

### Step 3 — Architecture Audit
ตรวจ:
- separation of concerns
- layer boundaries
- dependency direction
- business logic location
- data access isolation
- config ownership
- extensibility

Expected pattern:

```text
UI / Controller
→ Service / Domain
→ Repository / API Client
→ Data Source / External System
```

Issues to catch:
- UI/controller มี business logic หนัก
- controller query DB/API โดยตรง
- circular dependency
- shared utility ใหญ่เกิน
- business rules ซ้ำหลายที่

---

### Step 4 — Code Quality Audit
ตรวจ:
- DRY
- KISS
- clean naming
- function/class responsibility
- duplication
- nesting complexity
- unused code
- formatting
- comments quality

Checklist:

```text
- names meaningful
- functions small
- no duplicated logic
- no silent failure
- no over-engineering
- no unrelated abstraction
- no dead code
```

---

### Step 5 — UI/UX Audit
ใช้เมื่อมี UI เช่น JavaFX / Swing / Web

ตรวจ:
- user flow ชัดไหม
- primary action ชัดไหม
- หน้าจอรกไหม
- form ยาวเกินไหม
- table อ่านง่ายไหม
- มี search/filter ไหม
- error message ช่วยผู้ใช้ไหม
- loading/empty/error states มีไหม
- destructive action มี confirm ไหม
- UI ดู modern หรือ legacy

Output:

```markdown
## UI/UX
### ต้องแก้
- ...

### ควรปรับ
- ...

### ดีอยู่แล้ว
- ...
```

---

### Step 6 — Responsive Layout Audit
ตรวจ:
- resize แล้ว layout พังไหม
- fixed width/height เยอะไหม
- table/form ยืดหดดีไหม
- scroll behavior ถูกไหม
- sidebar/detail panel handle หน้าจอเล็กไหม

JavaFX focus:
- `BorderPane`
- `VBox` / `HBox`
- `GridPane`
- `SplitPane`
- `ScrollPane`
- `HBox.hgrow` / `VBox.vgrow`

Issue format:

```markdown
- ปัญหา: fixed size ทำให้ resize แล้วล้น
  - แก้: ใช้ grow priority + ScrollPane + min/pref width ที่เหมาะสม
```

---

### Step 7 — Error Handling Audit
ตรวจ:
- input validation
- exception handling
- user-friendly error
- logging
- retry/fallback
- null/empty handling
- API/DB/file failure handling

Catch:
- `catch {}`
- catch แล้วไม่ log
- error message กว้างเกิน
- expose stack trace ให้ user
- ไม่ handle missing config/file/API failure

---

### Step 8 — Security Audit
ตรวจ:
- secrets in code
- sensitive data in logs
- SQL injection risk
- unsafe file access
- permission checks
- role-based access
- input sanitization
- dependency risk ถ้า context มี

Critical if found:
- password/token hardcoded
- raw SQL from user input
- auth bypass
- unsafe destructive operation

---

### Step 9 — Hardcoding / Config Audit
ห้าม hardcode production values:
- credentials
- URLs
- ports
- file paths
- timeouts
- retry counts
- role names
- permission names
- user-facing text ที่ควร localization
- magic numbers
- business thresholds
- environment names
- colors/styles ใน controller

Recommend:
- config file
- env vars
- typed config provider
- ResourceBundle
- constants/enums เฉพาะ stable domain terms
- CSS/theme file

Output:

```markdown
## Hardcoding Risks
- `<file>` — `<value>` ควรย้ายไป <config/resource/constant>
```

---

### Step 10 — Performance Audit
ตรวจ:
- slow operation บน UI thread
- N+1 query
- repeated API/DB calls
- inefficient loops
- large table rendering
- missing pagination/lazy loading
- memory leaks/listener leaks
- blocking file IO

JavaFX focus:
- DB/API/file operation ต้องอยู่ใน `Task`, `Service`, executor
- update UI บน JavaFX Application Thread เท่านั้น
- TableView ใหญ่ควรมี filter/search/pagination/lazy loading

---

### Step 11 — Testing / Debug Readiness Audit
ตรวจ:
- มี unit tests ไหม
- มี integration tests ไหม
- มี manual UI checklist ไหม
- build command ชัดไหม
- run command ชัดไหม
- test data แยกจาก production ไหม
- bugfix มี regression test ไหม

Output:

```markdown
## Test Readiness
- Missing:
- Recommended tests:
- Commands:
```

---

### Step 12 — Maintainability Audit
ตรวจ:
- onboard ง่ายไหม
- code อ่านง่ายไหม
- naming ชัดไหม
- module boundaries ชัดไหม
- config/documentation พอไหม
- technical debt จุดไหนหนักสุด

Rating:

```text
Easy     = dev ใหม่เข้าใจได้เร็ว
Moderate = ต้องอ่านหลายไฟล์แต่ยังพอ maintain
Hard     = logic กระจาย ซ้ำซ้อน เสี่ยงแก้พัง
```

---

### Step 13 — Documentation Audit
ตรวจ:
- README
- run instructions
- build/test commands
- config setup
- deployment notes
- architecture note
- known limitations

แนะนำเฉพาะ doc ที่จำเป็นจริง

---

## 6. Audit Score Model

ให้คะแนน 0–10 ตามนี้:

```text
10 = production-ready, maintainable, low risk
8-9 = good, minor improvements
6-7 = usable, but technical debt exists
4-5 = risky, needs cleanup before scaling
0-3 = unstable / hard to maintain / high risk
```

Score dimensions:
- Architecture
- Code Quality
- UI/UX
- Security
- Config/Hardcoding
- Performance
- Testing
- Maintainability

---

## 7. Output Templates

### Full Audit Report

```markdown
# Audit Report: <Project/System>

## Overall
- Score: <x>/10
- Status: <Good / Needs Work / Risky>
- Main risk: <short>

## Critical Issues
- ...

## High Priority
- ...

## Medium Priority
- ...

## Low Priority
- ...

## Category Review
### Architecture
- ...

### Code Quality
- ...

### UI/UX
- ...

### Responsive Layout
- ...

### Error Handling
- ...

### Security
- ...

### Hardcoding / Config
- ...

### Performance
- ...

### Testing
- ...

### Maintainability
- ...

## Recommended Fix Plan
### Phase 1 — Critical Fixes
- ...

### Phase 2 — Quality Improvements
- ...

### Phase 3 — Polish / Future-Proofing
- ...

## Next Step
- ...
```

---

### Compact Audit

```markdown
## Audit Summary
- Score: <x>/10
- Status: <status>
- Main risk: <risk>

## ต้องแก้ก่อน
- ...

## ควรปรับ
- ...

## แนะนำต่อ
- ...
```

---

### Issue Format

```markdown
- ปัญหา: <issue>
  - ผลกระทบ: <impact>
  - แก้: <fix>
  - Priority: <level>
```

---

## 8. Token Saving Rules

ตอบให้สั้นแต่ครบ:
- ไม่เกริ่น
- ไม่สอนทฤษฎี
- ไม่เขียนทุกหมวดถ้าไม่มี issue
- รวม issue ซ้ำกัน
- เรียง priority ก่อน
- ถ้าข้อมูลไม่พอ ให้ระบุ `Need:` ไม่เกิน 3 ข้อ
- ถ้า audit จากไฟล์ ให้พูดเฉพาะสิ่งที่เห็นในไฟล์
- ถ้าไม่มีหลักฐาน อย่าฟันธง ให้ใช้ `น่าจะ` หรือ `ต้องตรวจเพิ่ม`

---

## 9. Clarification Rules

ถามเฉพาะถ้า audit ต่อไม่ได้:

```markdown
Need:
1. <repo/files/module ที่ต้องดู>
2. <run/test command ถ้ามี>
3. <scope ว่าต้อง audit ทั้งระบบหรือเฉพาะ module>
```

---

## 10. Anti-Patterns

ห้าม:
- audit โดยไม่ดู context
- ให้คะแนนโดยไม่มีเหตุผล
- บอกว่า security ดีโดยไม่ได้ตรวจ
- บอกว่า test ผ่านโดยไม่ได้รัน/ไม่มีหลักฐาน
- แนะนำ rewrite ทั้งระบบถ้าไม่จำเป็น
- list ปัญหาเยอะมากแต่ไม่จัด priority
- ไม่มี recommended fix plan
- ใช้คำกว้าง ๆ เช่น “ควรปรับปรุงโค้ด” โดยไม่บอกแก้อะไร

---

## Final Rule
**Audit ต้องชี้ปัญหา, ผลกระทบ, วิธีแก้, priority, และ next step แบบชัดเจน.**
