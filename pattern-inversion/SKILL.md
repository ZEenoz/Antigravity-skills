---
name: pattern-inversion
description: Trigger this skill at the beginning of a complex project or system development task. | เรียกใช้ Skill นี้เมื่อเริ่มต้นโปรเจกต์ที่ซับซ้อนหรืองานพัฒนาระบบ โดยจะตั้งคำถามเพื่อเก็บข้อมูลให้ครบถ้วนก่อนเริ่มงาน ช่วยป้องกันความผิดพลาดจากการคาดเดาและลดการใช้ Token
---

# Pattern: Inversion | รูปแบบ: การสลับลำดับการทำงาน

This skill focuses on requirement gathering and clarity. | Skill นี้เน้นไปที่การเก็บรวบรวมความต้องการและความชัดเจนของงาน

## Rules
- **No Assumptions**: Never guess what the user wants. If it's not clear, ask.
- **Structured Questioning**: Use numbered lists for questions to make them easy to answer.
- **Completeness**: Aim to gather all critical information in one or two rounds of questioning.
- **Wait for Input**: Do not proceed with the implementation until the user has addressed the questions.

## Steps
1. **Analyze Request**: Read the user's initial prompt carefully.
2. **Identify Gaps**: Look for missing technical specifications, edge cases, environment details, or business logic.
3. **Draft Questions**: Create a concise list of questions to fill the identified gaps.
4. **Gather Information**: Present the questions to the user and wait for their response.
5. **Proceed**: Once information is complete, use the gathered context to execute the task.

## Example
**Input**: "Build a web app for tracking chip inspection results."
**Output**:
To build the most effective app for you, I need to clarify a few details first:
1. Which framework do you prefer (Next.js, Vite, or Vanilla)?
2. What specific metrics need to be tracked (e.g., Frequency, Duty Cycle, Timestamp)?
3. Should the data be stored locally in a file or in a database?
4. Do you have a preferred color scheme or design aesthetic?

Please let me know these details so I can provide a precise solution.
