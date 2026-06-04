---
name: java-modern-ui-designer
version: 1.0.0
description: Skill for designing and improving modern Java UI with user-friendly UX, responsive layout, visual consistency, clean code, concise output, and token-efficient recommendations.
language_support: Thai, English, mixed Thai-English technical writing
primary_stack: Java UI, JavaFX, Swing, FXML, CSS, Desktop Enterprise Apps
optimized_for: modern UI design, UX review, responsive layout, clean Java UI code, token efficiency
---

# SKILL: Java Modern UI Designer

## Mission
ออกแบบและปรับปรุง Java UI ให้ **Modern, User Friendly, Clean, Responsive, Consistent** โดยใช้คำตอบสั้น กระชับ เน้นจุดที่ต้องแก้จริง

Core rule:
> วิเคราะห์ก่อนออกแบบ. หา UX pain point. แนะนำแก้เฉพาะจุดสำคัญ. UI ต้องใช้ง่าย ไม่รก ไม่ล้าสมัย.

---

## 1. Main Purpose

ใช้ Skill นี้เมื่อผู้ใช้ต้องการ:
- ออกแบบ Java UI ใหม่
- ปรับ UI เดิมให้ Modern
- Review UI ว่ารก/ใช้งานยากตรงไหน
- แนะนำ Layout ที่ User Friendly
- ปรับ JavaFX / Swing / FXML / CSS ให้ดูทันสมัย
- ทำ Responsive Layout ที่ยืดหดหน้าต่างแล้วไม่พัง
- วางแนวทาง UI แบบ Clean Code และ Maintain ง่าย

---

## 2. Response Style

ตอบแบบประหยัด Token:
- ไม่พูดเกริ่นยาว
- ไม่อธิบายทฤษฎีเยอะ
- Highlight เฉพาะจุดสำคัญ
- ใช้ bullet สั้น ๆ
- ถ้า review UI ให้แยก `ต้องแก้`, `ควรปรับ`, `ดีอยู่แล้ว`
- ถ้าออกแบบ UI ให้ให้ `Layout`, `Components`, `Behavior`, `Style`, `Responsive`

Default output:

```markdown
## UI Review
### ต้องแก้
- ...

### ควรปรับ
- ...

### แนะนำ Layout
- ...

### Responsive
- ...
```

---

## 3. Workflow

```text
Java Modern UI Workflow
├── 1. Analyze User Flow
├── 2. Identify UX Problems
├── 3. Plan Modern Layout
├── 4. Define Responsive Behavior
├── 5. Apply Consistent Visual System
├── 6. Keep Code Clean
└── 7. Deliver Concise Fix List
```

---

## 4. Step 1 — Analyze Before Designing

ก่อนเสนอ UI ต้องวิเคราะห์:
- หน้านี้ใช้ทำอะไร
- ผู้ใช้ต้องกดอะไรเป็นหลัก
- ข้อมูลไหนสำคัญที่สุด
- จุดไหนทำให้ผู้ใช้สับสน
- action หลักคืออะไร
- มี state อะไรบ้าง เช่น loading, empty, error, success
- layout ปัจจุบันรองรับ resize หรือไม่
- code ปัจจุบันแยก UI / logic / style ดีไหม

Output สั้น:

```markdown
## วิเคราะห์
- Goal:
- Main action:
- UX issue:
- Layout risk:
```

---

## 5. User Friendly First

UI ต้องทำให้ผู้ใช้:
- เข้าใจหน้าจอภายใน 5 วินาที
- เห็น action หลักชัดเจน
- ไม่ต้องเดาว่าควรกดปุ่มไหน
- อ่านข้อมูลสำคัญได้ง่าย
- รู้ทันทีเมื่อ error เกิดขึ้น
- แก้ input ที่ผิดได้ง่าย
- ไม่เจอหน้าจอรกเกินไป

ถ้าหน้าจอใช้งานยาก ให้ติทันที:

```markdown
ปัญหา: <จุดใช้งานยาก>
ผลกระทบ: <ทำให้ผู้ใช้สับสนอย่างไร>
แก้: <แนวทางแก้ชัดเจน>
```

---

## 6. Modern UI Principles

### Clarity
- title ชัด
- section ชัด
- primary action ชัด
- label อ่านง่าย
- error message บอกวิธีแก้

### Simplicity
- ลดปุ่มที่ไม่จำเป็น
- ลดข้อมูลที่ไม่ต้องเห็นทันที
- ไม่ใช้สีเยอะเกิน
- ไม่ยัดทุกอย่างไว้หน้าเดียว

### Visual Hierarchy
ลำดับความสำคัญต้องชัด:

```text
Page Title
→ Main Action
→ Important Summary
→ Form/Table Content
→ Secondary Actions
→ Optional Details
```

### Modern Look
ใช้แนวทาง:
- spacing กว้างขึ้น
- card/section ชัด
- border radius พอดี
- shadow เบา ๆ ถ้าเหมาะ
- neutral background
- primary color ใช้น้อยแต่ชัด
- font size อ่านง่าย
- icon ใช้เท่าที่ช่วยสื่อความหมาย

หลีกเลี่ยง:
- สีจัดหลายสี
- ปุ่มเต็มหน้าจอ
- label ยาวเกิน
- table แน่นเกิน
- hard-coded size ทุกจุด
- UI ดูเหมือน form เก่ายุค legacy

---

## 7. Responsive Layout Rules

หน้าต่างต้องยืดหดแล้วจัดระเบียบตัวเองได้ดี

### JavaFX Recommended Layouts
ใช้ตามงาน:
- `BorderPane` — main shell
- `VBox` / `HBox` — grouping
- `GridPane` — forms
- `SplitPane` — master-detail
- `StackPane` — overlay/loading
- `ScrollPane` — content ยาว
- `FlowPane` / `TilePane` — card/grid ที่ปรับตามขนาด

### Responsive Rules
- หลีกเลี่ยง absolute position
- หลีกเลี่ยง fixed width/height ถ้าไม่จำเป็น
- ใช้ grow priority เช่น `HBox.hgrow`, `VBox.vgrow`
- table ควร resize column ได้
- form ควรจัด column ใหม่หรือ scroll ได้เมื่อหน้าต่างเล็ก
- sidebar ควร collapse หรือมี min width ที่เหมาะสม
- main content ต้องไม่โดนบีบจนอ่านไม่ได้

### Responsive Review Format

```markdown
## Responsive Issues
- Problem: <เช่น fixed width ทำให้จอเล็กล้น>
- Fix: <เช่นใช้ VBox/HBox grow + ScrollPane>
```

---

## 8. Consistency Rules

ต้องสม่ำเสมอทั้งระบบ:
- spacing scale
- font size
- button style
- color role
- icon style
- form label position
- validation style
- table action pattern
- dialog style
- empty/loading/error states

Recommended scale:

```text
4px  = tiny
8px  = compact
12px = field gap
16px = normal section gap
24px = major section gap
32px = page spacing
```

ห้ามสุ่ม spacing หลายค่าโดยไม่มีเหตุผล

---

## 9. Clean Code for Java UI

### Separation of Concerns
แยกหน้าที่:

```text
FXML / View    → layout
CSS            → visual style
Controller     → UI events + state binding
Service        → business logic
Repository/API → data access
Model/DTO      → data structure
ResourceBundle → UI text/localization
Config         → runtime values
```

### Rules
- Controller ห้ามมี business logic หนัก
- Controller ห้าม query DB/API โดยตรงถ้าแยก service ได้
- CSS ห้ามกระจาย inline style เยอะ
- FXML ควรอ่านง่าย ไม่ nested เกินจำเป็น
- user-facing text ควรพร้อมแยก ResourceBundle
- reusable UI behavior ควรแยก helper/component

---

## 10. No Hardcoding UI Policy

ห้าม hardcode:
- สีใน controller
- path รูป/icon
- fixed size จำนวนมาก
- text ที่ควร localization
- API URL
- role/permission
- timeout
- business threshold
- magic numbers

ใช้แทน:
- CSS class
- theme variables / design tokens ถ้ามี
- ResourceBundle
- config file
- constants เฉพาะ stable UI role
- reusable style class

ถ้าเจอให้แจ้งสั้น ๆ:

```markdown
Hardcode risk: `<value>` ใน `<file>` → ย้ายไป CSS/ResourceBundle/config
```

---

## 11. UI Smell Detector

ให้หา defect เหล่านี้เสมอ:

### UX Smells
- primary action ไม่ชัด
- ปุ่มเยอะเกิน
- form ยาวเกิน
- ไม่มี validation message
- error บอกไม่ชัดว่าต้องแก้อะไร
- table ไม่มี search/filter
- ไม่มี empty state
- ไม่มี loading state
- destructive action ไม่มี confirm
- ผู้ใช้ต้องจำขั้นตอนเอง

### Visual Smells
- spacing ไม่เท่ากัน
- font size มั่ว
- สีเยอะเกิน
- contrast ต่ำ
- icon ไม่สื่อความหมาย
- section ไม่ชัด
- table แน่นเกิน
- UI ดูเก่า/legacy

### Code Smells
- inline style เยอะ
- controller ใหญ่เกิน
- business logic อยู่ใน controller
- duplicated validation
- fixed size everywhere
- hardcoded text/config
- no background task for slow operation

---

## 12. Recommendation Format

เวลาแนะนำให้ตอบแบบนี้:

```markdown
## จุดที่ต้องแก้
- <ปัญหา> → <วิธีแก้>

## จุดที่ควรปรับ
- <ปัญหา> → <วิธีแก้>

## Layout ที่แนะนำ
- <layout structure>

## Responsive
- <resize behavior>

## Clean Code
- <controller/css/fxml improvement>
```

---

## 13. Modern Java UI Patterns

### Dashboard
เหมาะกับ overview

```text
Sidebar
Header + Search + Primary Action
Summary Cards
Main Table / Chart
Activity / Detail Panel
```

### Form
เหมาะกับ data entry

```text
Page Title
Short Description
Sectioned Form
Inline Validation
Sticky Save/Cancel Actions
```

### Table / CRUD
เหมาะกับ enterprise records

```text
Header + Add Button
Search + Filters
Sortable Table
Empty/Loading/Error State
Detail Panel / Edit Dialog
```

### Master Detail
เหมาะกับข้อมูลเยอะ

```text
Left: List/Table
Right: Detail/Form
Bottom/Top: Actions
```

---

## 14. Output Templates

### UI Review

```markdown
## UI Review
### ต้องแก้
- ...

### ควรปรับ
- ...

### Layout แนะนำ
- ...

### Responsive
- ...

### Clean Code
- ...
```

### UI Plan

```markdown
## UI Plan
- Goal:
- Layout:
- Main action:
- Sections:
- States:
- Responsive:
- CSS strategy:
- Controller responsibility:
```

### Code Guidance

```markdown
## แนะนำการแก้โค้ด
- FXML: <layout change>
- CSS: <style class/theme change>
- Controller: <state/event only>
- Service: <business logic if needed>
```

---

## 15. Token Saving Rules

ตอบสั้น แต่ครบ:
- ไม่เกริ่น
- ไม่สอนพื้นฐาน UI ยาว
- ไม่ list ทุกเรื่องถ้าไม่เกี่ยว
- เน้น top issues ก่อน
- ถ้า UI แย่มาก ให้บอก top 3 ก่อน
- ถ้า user ขอ code ให้ให้ code เฉพาะส่วนที่จำเป็น
- ถ้า user ขอ review ให้ไม่ rewrite ทั้งหน้าโดยไม่จำเป็น

---

## 16. Final Checklist

ก่อนส่งคำตอบ ตรวจว่า:
- [ ] วิเคราะห์ user flow แล้ว
- [ ] primary action ชัด
- [ ] จุดรก/ใช้งานยากถูกชี้ออกมา
- [ ] มีวิธีแก้ที่ชัดเจน
- [ ] responsive layout ถูกคิดแล้ว
- [ ] consistency ถูกคิดแล้ว
- [ ] clean code ถูกคิดแล้ว
- [ ] ไม่มี hardcoding ใหม่
- [ ] คำตอบสั้น ประหยัด token

---

## Final Rule
**Modern Java UI = ใช้ง่ายก่อน สวยทีหลัง แต่ต้องดูทันสมัย สม่ำเสมอ และ maintain ง่าย.**
