---
name: Folder Deep Study & Tree Workflow
description: วัตถุประสงค์ใช้ Skill นี้เพื่อให้ Agent ศึกษาโฟลเดอร์ที่ผู้ใช้ระบุอย่างละเอียด วิเคราะห์โครงสร้างไฟล์/โฟลเดอร์ อ่านไฟล์ที่สามารถอ่านได้ทุกไฟล์โดยไม่ข้ามไฟล์ และสรุปผลออกมาเป็น Tree Workflow พร้อมคำอธิบายขั้นตอนการทำงานของโปรเจกต์/โฟลเดอร์นั้น
---

# Skill: Folder Deep Study & Tree Workflow

## วัตถุประสงค์

ใช้ Skill นี้เพื่อให้ Agent ศึกษาโฟลเดอร์ที่ผู้ใช้ระบุอย่างละเอียด วิเคราะห์โครงสร้างไฟล์/โฟลเดอร์ อ่านไฟล์ที่สามารถอ่านได้ทุกไฟล์โดยไม่ข้ามไฟล์ และสรุปผลออกมาเป็น **Tree Workflow** พร้อมคำอธิบายขั้นตอนการทำงานของโปรเจกต์/โฟลเดอร์นั้น

---

## Trigger / คำสั่งตัวอย่าง

เมื่อผู้ใช้สั่งในลักษณะต่อไปนี้ ให้ใช้ Skill นี้ทันที:

```text
ศึกษา Folder: <path>
อ่านโฟลเดอร์นี้แล้วสรุปโครงสร้างให้หน่อย
วิเคราะห์โปรเจกต์ใน <path>
ทำ Tree Workflow จากโฟลเดอร์ <path>
อ่านไฟล์ทั้งหมดในโฟลเดอร์นี้ ห้ามข้ามไฟล์
```

ตัวอย่าง:

```text
อยากให้ศึกษา Folder /project/src แล้วบอกโครงสร้างของใน Folder นั้นว่าประกอบด้วยอะไรบ้าง ขั้นตอนเป็นยังไง ถ้ามีไฟล์ข้างในที่สามารถอ่านได้ก็ให้อ่านและทำการศึกษา อ่านอย่างละเอียดโดยห้ามข้ามไฟล์ หลังจากอ่านข้อมูลมาแล้วให้สรุปเป็น Tree Workflow
```

---

## Input ที่ต้องได้รับจากผู้ใช้

Agent ต้องได้รับข้อมูลอย่างน้อย 1 อย่าง:

```text
Folder Path: <path ของโฟลเดอร์ที่ต้องการศึกษา>
```

หากผู้ใช้ไม่ได้ระบุ path ให้ถามกลับอย่างสุภาพ:

```text
รบกวนระบุ path ของ Folder ที่ต้องการให้ศึกษาด้วยครับ เช่น /workspace/project/src
```

---

## หลักการทำงานสำคัญ

1. ต้องสำรวจโครงสร้างโฟลเดอร์ทั้งหมดก่อนเริ่มสรุป
2. ต้องอ่านไฟล์ที่สามารถอ่านได้ทุกไฟล์ภายในโฟลเดอร์ที่ระบุ
3. ห้ามข้ามไฟล์ที่อ่านได้ เว้นแต่มีเหตุผลชัดเจน เช่น binary file, permission denied, file ใหญ่เกินข้อจำกัด, corrupted file
4. ถ้าอ่านไฟล์ไม่ได้ ต้องบันทึกไว้ในหัวข้อ `Unreadable / Skipped Files` พร้อมเหตุผล
5. ต้องแยกไฟล์ที่เป็น binary, generated, dependency, cache, build output ออกจากไฟล์ source/documentation หากจำเป็น แต่ยังต้องรายงานว่าพบไฟล์เหล่านั้น
6. ต้องวิเคราะห์ความสัมพันธ์ของไฟล์ เช่น entry point, config, module, dependency, workflow, data flow
7. ผลลัพธ์สุดท้ายต้องมี Tree Workflow ที่เข้าใจง่าย
8. ห้ามเดาข้อมูลที่ไม่มีในไฟล์ หากไม่แน่ใจให้ระบุว่า `ไม่พบข้อมูลยืนยันจากไฟล์ที่อ่าน`

---

## File Reading Policy

### ไฟล์ที่ควรอ่านแบบละเอียด

อ่านไฟล์ประเภทต่อไปนี้ทั้งหมด:

```text
.md, .txt, .json, .yaml, .yml, .xml, .csv, .tsv,
.js, .jsx, .ts, .tsx, .py, .java, .cs, .go, .rs, .php, .rb,
.html, .css, .scss, .sql, .sh, .bat, .ps1,
.env.example, Dockerfile, docker-compose.yml,
package.json, requirements.txt, pyproject.toml, pom.xml,
build.gradle, Makefile, README, LICENSE
```

### ไฟล์ที่ควรระวัง

ไฟล์ต่อไปนี้ให้รายงานว่าพบ แต่ไม่จำเป็นต้องอ่านเนื้อหาทั้งหมดหากเป็น generated/dependency/cache:

```text
node_modules/, vendor/, dist/, build/, .next/, .nuxt/, target/,
.git/, .cache/, __pycache__/, coverage/, logs/, tmp/, temp/
```

หากผู้ใช้สั่งว่า `อ่านทุกไฟล์จริง ๆ` ให้พยายามอ่าน metadata และตัวอย่างเนื้อหาเท่าที่ปลอดภัย/เป็นไปได้ พร้อมรายงานข้อจำกัด

### ไฟล์ที่ไม่ควรพยายามอ่านเป็น text เต็ม

ให้ตรวจจับและรายงาน:

```text
รูปภาพ, วิดีโอ, ไฟล์เสียง, binary, archive, executable,
.pdf, .docx, .xlsx, .pptx หาก environment ไม่มีเครื่องมืออ่าน
```

หากมีเครื่องมืออ่านไฟล์เหล่านี้ได้ ให้ extract text/metadata แล้วนำมาวิเคราะห์

---

## ขั้นตอนการทำงานของ Agent

### Step 1: Validate Folder Path

- ตรวจสอบว่า path มีอยู่จริงหรือไม่
- ตรวจสอบว่าเป็น folder หรือไม่
- หากไม่มีสิทธิ์เข้าถึง ให้แจ้งผู้ใช้ทันที

### Step 2: Scan Directory Recursively

- สำรวจไฟล์และโฟลเดอร์ทั้งหมดแบบ recursive
- เก็บข้อมูล:
  - path
  - type: file/folder
  - extension
  - file size
  - readable status
  - last modified ถ้าดึงได้

### Step 3: Create Raw Folder Tree

สร้าง tree เริ่มต้น เช่น:

```text
/project
├── README.md
├── package.json
├── src
│   ├── main.ts
│   ├── app.ts
│   └── utils
│       └── parser.ts
└── tests
    └── app.test.ts
```

### Step 4: Classify Files

จัดกลุ่มไฟล์ เช่น:

```text
- Documentation
- Source Code
- Configuration
- Environment / Deployment
- Test Files
- Data Files
- Build / Generated Files
- Dependency / Vendor Files
- Assets / Binary Files
- Unknown
```

### Step 5: Read Every Readable File

สำหรับไฟล์ที่อ่านได้ทุกไฟล์:

- อ่านเนื้อหาอย่างละเอียด
- สรุปหน้าที่ของไฟล์
- ตรวจจับ import/export, function, class, route, command, config, dependency
- บันทึกความสัมพันธ์กับไฟล์อื่น
- ห้ามสรุปแบบเหมารวมโดยไม่ได้อ่านไฟล์

รูปแบบบันทึกภายใน:

```text
File: <path>
Purpose: <ไฟล์นี้ทำหน้าที่อะไร>
Key Elements:
- <function/class/config/section สำคัญ>
Dependencies:
- <ไฟล์หรือ package ที่เกี่ยวข้อง>
Notes:
- <ข้อสังเกต>
```

### Step 6: Identify Project Workflow

หลังจากอ่านครบ ให้หา workflow เช่น:

- จุดเริ่มต้นของระบบคือไฟล์ใด
- config ถูกโหลดจากที่ไหน
- flow การทำงานหลักผ่านไฟล์ใดบ้าง
- input เข้ามาทางไหน
- processing อยู่ที่ไฟล์ใด
- output ถูกส่งออกอย่างไร
- test/deployment ทำงานอย่างไร

### Step 7: Build Tree Workflow

สร้าง Tree Workflow ที่ไม่ใช่แค่ folder tree แต่เป็น workflow การทำงาน เช่น:

```text
Project Workflow
├── 1. Entry Point
│   └── src/main.ts
│       ├── โหลด config จาก config/app.ts
│       └── เรียกใช้งาน app.ts
├── 2. Application Core
│   └── src/app.ts
│       ├── ลงทะเบียน routes
│       ├── เชื่อมต่อ middleware
│       └── ส่งต่อ request ไป controller
├── 3. Business Logic
│   └── src/services
│       ├── user.service.ts
│       └── auth.service.ts
├── 4. Data Layer
│   └── src/repositories
│       └── user.repository.ts
└── 5. Output / Response
    └── controllers ส่ง response กลับไปยัง client
```

### Step 8: Produce Final Report

รายงานสุดท้ายต้องมีหัวข้อต่อไปนี้เสมอ:

1. `Summary`
2. `Folder Scope`
3. `Folder Structure`
4. `File Classification`
5. `Readable Files Studied`
6. `Unreadable / Skipped Files`
7. `Important Files and Roles`
8. `Detected Dependencies / Relationships`
9. `Step-by-Step Workflow`
10. `Tree Workflow`
11. `Observations / Risks / Missing Information`
12. `Recommended Next Steps`

---

## Output Format

ให้ตอบเป็น Markdown เสมอ

### Template

```markdown
# Folder Study Report: <folder path>

## 1. Summary
<สรุปภาพรวมของโฟลเดอร์/โปรเจกต์>

## 2. Folder Scope
- Target folder: `<path>`
- Total folders: <number>
- Total files: <number>
- Readable files studied: <number>
- Unreadable/skipped files: <number>

## 3. Folder Structure
```text
<raw folder tree>
```

## 4. File Classification

### Documentation

- `<path>` — <description>

### Source Code

- `<path>` — <description>

### Configuration

- `<path>` — <description>

### Tests

- `<path>` — <description>

### Assets / Binary / Others

- `<path>` — <description>

## 5. Readable Files Studied

### `<file path>`

**Purpose:** <หน้าที่ของไฟล์>

**Key Content:**

- <ประเด็นสำคัญ>
- <ประเด็นสำคัญ>

**Relationships:**

- <เกี่ยวข้องกับไฟล์ใด / package ใด>

## 6. Unreadable / Skipped Files

- `<path>` — <reason>

ถ้าไม่มี ให้เขียน:

ไม่มีไฟล์ที่อ่านไม่ได้หรือถูกข้าม

## 7. Important Files and Roles

- `<path>` — <บทบาทสำคัญ>

## 8. Detected Dependencies / Relationships

- `<file A>` → imports/uses → `<file B>`
- `<config>` → controls → `<runtime behavior>`

## 9. Step-by-Step Workflow

1. <ขั้นตอนที่ 1>
2. <ขั้นตอนที่ 2>
3. <ขั้นตอนที่ 3>

## 10. Tree Workflow

```text
<tree workflow>
```

## 11. Observations / Risks / Missing Information

- <ข้อสังเกต>
- <ความเสี่ยง>
- <ข้อมูลที่ยังไม่พบ>

## 12. Recommended Next Steps

- <คำแนะนำถัดไป>

```

---

## Rules / ข้อบังคับ

- ห้ามข้ามไฟล์ที่อ่านได้
- ห้ามสรุปก่อนอ่านไฟล์ครบ
- ห้ามเดาโครงสร้างหรือ workflow โดยไม่มีหลักฐานจากไฟล์
- หากไฟล์เยอะมาก ให้แบ่งการอ่านเป็นรอบ ๆ และรายงาน progress
- หากพบ secret เช่น password, token, API key ให้ไม่แสดงค่าเต็ม และแจ้งว่า `พบข้อมูลลับ ควรย้ายไป environment variable หรือ secret manager`
- หากพบไฟล์ซ้ำหรือ generated file ให้ระบุในรายงาน
- หากมี dependency folder ขนาดใหญ่ เช่น `node_modules` ให้รายงานจำนวน/ตำแหน่ง แต่ไม่ต้องอ่านทุกไฟล์ ยกเว้นผู้ใช้สั่งชัดเจน
- ต้องทำ secondary consistency check ก่อนตอบเสมอ:
  - จำนวนไฟล์ที่รายงานตรงกับที่ scan ได้หรือไม่
  - ไฟล์ readable ถูกอ่านครบหรือไม่
  - skipped files มีเหตุผลครบหรือไม่
  - Tree Workflow สอดคล้องกับไฟล์ที่อ่านจริงหรือไม่

---

## Progress Reporting สำหรับโฟลเดอร์ขนาดใหญ่
ถ้าโฟลเดอร์มีไฟล์มากกว่า 100 ไฟล์ ให้รายงานเป็นช่วง:

```markdown
## Progress
- Scanned: <number> files
- Readable files found: <number>
- Files studied so far: <number>
- Remaining: <number>
- Current folder: `<path>`
```

จากนั้นค่อยทำต่อจนจบ หรือขออนุญาตผู้ใช้หากมีข้อจำกัดเรื่องเวลา/context

---

## Example Final Tree Workflow

```text
Folder /project
├── Documentation Layer
│   ├── README.md
│   │   └── อธิบายวิธีติดตั้งและใช้งานโปรเจกต์
│   └── docs/
│       └── เก็บรายละเอียดเพิ่มเติม
├── Configuration Layer
│   ├── package.json
│   │   ├── กำหนด scripts
│   │   └── กำหนด dependencies
│   └── tsconfig.json
│       └── กำหนด TypeScript compiler options
├── Runtime Layer
│   └── src/main.ts
│       └── เป็น entry point ของระบบ
├── Application Layer
│   └── src/app.ts
│       ├── สร้าง application instance
│       ├── โหลด middleware
│       └── เชื่อม routes
├── Business Logic Layer
│   └── src/services/
│       └── ประมวลผล logic หลัก
├── Data Layer
│   └── src/repositories/
│       └── ติดต่อฐานข้อมูลหรือ data source
└── Testing Layer
    └── tests/
        └── ตรวจสอบการทำงานของระบบ
```

---

## Minimal User-Facing Response When Starting

เมื่อเริ่มทำงาน ให้ตอบสั้น ๆ ว่า:

```text
รับทราบครับ ผมจะศึกษาโฟลเดอร์ `<path>` โดยจะ scan โครงสร้างทั้งหมด อ่านไฟล์ที่สามารถอ่านได้ทุกไฟล์โดยไม่ข้ามไฟล์ จากนั้นจะสรุปเป็น Folder Structure และ Tree Workflow ให้ครับ
```

จากนั้นเริ่มดำเนินการทันที
