---
name: pattern-chained-inversion
description: Use this skill for highly complex or multi-stage tasks like large-scale refactoring or multi-module system architecture. | ใช้ Skill นี้สำหรับงานที่ซับซ้อนสูงหรือมีหลายขั้นตอน เช่น การ Refactor ขนาดใหญ่ โดยจะแบ่งงานเป็นเฟสและตั้งคำถามไปพร้อมกับการลงมือทำทีละส่วน
---

# Pattern: Chained Inversion | รูปแบบ: การถามตอบแบบต่อเนื่อง

This skill is for complex, iterative workflows. | Skill นี้สำหรับกระบวนการทำงานที่ซับซ้อนและต้องทำซ้ำแบบต่อเนื่อง

## Rules
- **One Step at a Time**: Focus on the immediate next sub-task.
- **Contextual Questioning**: Only ask questions relevant to the current phase.
- **Validate and Move**: Confirm the completion of one step before starting the next.
- **Maintain State**: Keep track of the overall progress and what has already been decided/built.

## Steps
1. **Decompose Task**: Break the large request into smaller, manageable sub-tasks.
2. **Current Sub-task Phase**:
    a. Ask necessary questions for the *current* sub-task.
    b. Wait for user feedback.
    c. Execute the sub-task.
3. **Transition**: Summarize the current progress and identify the next sub-task.
4. **Repeat**: Loop back to Step 2 until the entire project is complete.

## Example
**Input**: "Refactor this entire legacy monolithic Java application into a microservices architecture."
**Output**:
This is a large task. Let's start with the first phase:
**Phase 1: Identify Service Boundaries**
I've analyzed the codebase and identified 3 potential services: `UserAuth`, `SignalProcessor`, and `Reporting`.
- Do these service boundaries align with your vision?
- Which service would you like to decouple first?

Once we decide on this, I will proceed to create the folder structure for the first service.
