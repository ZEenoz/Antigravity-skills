---
name: pattern-generator
description: Use this skill for tasks that require a consistent, standardized output format, such as code reviews, technical reports, or documentation generation. | ใช้ Skill นี้สำหรับงานที่ต้องการผลลัพธ์ในรูปแบบที่เป็นมาตรฐานและสม่ำเสมอ เช่น การรีวิวโค้ด, การสร้างรายงาน หรือการทำเอกสาร รูปแบบนี้ช่วยประหยัด Token และคงคุณภาพงานตามมาตรฐาน
---

# Pattern: Generator | รูปแบบ: ตัวสร้างผลลัพธ์มาตรฐาน

This skill is designed to produce standardized results with consistent quality. | Skill นี้ถูกออกแบบมาเพื่อสร้างผลลัพธ์ที่เป็นมาตรฐานและมีคุณภาพสม่ำเสมอ

## Rules
- **Consistency**: Always adhere to the established output format or template.
- **Precision**: Focus strictly on the task requirements without unnecessary conversational filler.
- **Standardization**: Ensure every output meets the same high-quality bar.
- **Avoid Over-explanation**: Only provide explanations if requested or if they are part of the template.

## Steps
1. **Identify Input**: Review the provided code, data, or context to be processed.
2. **Select Template**: Choose the appropriate template for the task (e.g., Code Review, Bug Report, Documentation).
3. **Process and Generate**: Apply the rules and generate the final structured output.
4. **Final Review**: Ensure the output matches the required standard before delivering.

## Example
**Input**: A Java class with a potential memory leak in a loop.
**Output**:
# Code Review Report
## Summary
Potential memory leak identified in `PatternService.java`.
## Findings
- **Location**: Line 45, inside the `processSignals` method.
- **Issue**: Objects are added to a static list without ever being cleared.
## Recommendations
- Use a local list or implement a cleanup mechanism.
- Consider using a WeakHashMap if global access is necessary.
