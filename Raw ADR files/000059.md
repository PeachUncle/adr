# Strategic Decision: Strategic-change reminder via guard

**Date**: 2025-12-24
**Status**: DECIDED (Option B)

## 1. Objective
ลดความเสี่ยงจากการเปลี่ยน policy / strategy / architecture โดยไม่ผ่านการคิดเชิงโครงสร้าง
โดยเพิ่ม WARN เตือนให้ใช้ DECISION_BOX ก่อนตัดสินใจ

## 2. Context
### Facts
- Runtime Guard สามารถตรวจ pattern จาก commit message ได้
- ปัจจุบันมีการตัดสินใจเชิงระบบหลายครั้งที่ “ข้ามขั้นคิด”
- DECISION_BOX และ LAC Mirror มีอยู่แล้ว แต่ไม่ได้ถูกใช้อย่างสม่ำเสมอ

### Unknowns
- WARN จะสร้าง noise มากเกินไปหรือไม่
- ผู้ใช้จะใช้ DECISION_BOX จริง หรือแค่ ignore

## 3. Options
- **Option A:** ไม่เตือน ปล่อยให้ใช้ดุลยพินิจล้วน
- **Option B:** เตือนแบบ WARN-only และชี้ไปที่ DECISION_BOX (ไม่ block)
- **Option C:** บังคับ BLOCK ถ้าไม่มี DECISION_BOX (เข้มมาก)

## 4. Trade-offs
| Option | Upside | Downside | Risk |
|---|---|---|---|
| A | ไม่มี friction | ตัดสินใจพลาดซ้ำ | Governance กลวง |
| B | เตือนแบบพอดี | อาจถูก ignore | Noise ถ้า pattern กว้าง |
| C | บังคับคิดจริง | ขัด flow สูง | คนหาทางเลี่ยง |

## 5. Assumptions
- A1: Strategic decisions ควรถูกแยกจาก routine
- A2: WARN ดีกว่า BLOCK สำหรับช่วงแรก
- A3: ผู้ใช้หลัก (Boss) ต้องการ clear box มากกว่า speed

## 6. Recommendation (Non-binding)
เลือก **Option B**: WARN-only + route ไป DECISION_BOX
ใช้เป็น “cognitive speed bump” ไม่ใช่ gate

## 7. Decision (Human)
- **Chosen Option:** Option B
- **Reason:** สมดุลระหว่างคุณภาพการตัดสินใจกับความลื่นของ workflow

## 8. Confidence & Next Check
- **Confidence:** High
- **Revisit Trigger:**
  - ถ้า WARN ถูก ignore เกิน 5 ครั้งติด
  - หรือเกิด false-positive มากกว่า 30%
