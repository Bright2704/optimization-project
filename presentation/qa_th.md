# Q&A ภาษาไทย

คำตอบผูกกับ configuration และผล 180 runs ที่ส่งมอบ; Q&A อยู่นอกเวลา 12 นาที

## 1. ทำไมเลือก Sphere และ Rosenbrock?

Sphere เป็นชามเรียบใช้ตรวจว่าค้นหา minimum ได้หรือไม่ ส่วน Rosenbrock มีหุบเขาแคบโค้ง ใช้สังเกตการติดตามหุบเขา ทั้งคู่มี optimum ที่ทราบและแสดงตำแหน่งใน 2D ได้ แต่ยังไม่ครอบคลุม multimodal หรือปัญหาจริง

## 2. best-so-far ต่างจาก population mean อย่างไร?

best-so-far เป็น minimum ของ objective ที่เคยประเมินทั้งหมดจนถึงรอบนั้น จึงไม่แย่ลง ส่วน population mean เป็นค่าเฉลี่ยของประชากรปัจจุบันและอาจเพิ่มขึ้นได้ กราฟ mean convergence หลักคือการเฉลี่ย best-so-far ข้าม independent runs ไม่ใช่ population mean

## 3. ทำไมต้องรันซ้ำ?

ตำแหน่งเริ่มต้นและ operators ของ GA/RLS เป็นการสุ่ม GOA ใน variant นี้สุ่มที่ initialization ผลครั้งเดียวไม่บอกความแปรปรวน เราจึงเก็บ 30 runs ต่อคู่ method/function และใช้ข้อมูลทุก run ใน mean median SD best worst และ boxplot

## 4. การเปรียบเทียบยุติธรรมหรือไม่?

ใช้ dimensions bounds agents iterations และ seed schedule เดียวกันข้าม methods และวัด objective calls จริง หลัง caching ทุก method ใช้ 3030 calls พารามิเตอร์ไม่ได้ปรับจูน ความยุติธรรมยังจำกัดเพราะ operators และต้นทุนภายในต่างกัน และ RLS sigma เป็น absolute step ขณะที่ GA mutation ผูกกับ bound width

## 5. GOA ติด local optimum ได้หรือไม่?

ได้ การมีแรงผลักและลด c ไม่รับประกัน global optimum ใน multimodal อาจติด local minimum ส่วน Rosenbrock 2D ชุดนี้อาจหยุดในหุบเขาหรือแถว target ที่ยังไม่ถึง optimum โดยไม่จำเป็นต้องเรียกว่า local minimum

## 6. ผลต่างจาก paper เพราะอะไร?

เราใช้ 2D bounds agents iterations และ baseline parameters ตาม workshop ไม่เหมือนชุดทดลองทั้งหมดใน paper อีกทั้งใช้ normalization รายพิกัดเทียบ bound width, synchronous update, PCG64 และ c ของ updates 1..T ที่ระบุชัด จึงไม่อ้างว่าเป็น exact replication แม้เก็บโครงสร้าง Eq. 2.7/2.8

## 7. ความซับซ้อนของ GOA?

ปฏิสัมพันธ์ทุกคู่เป็น O(N²D) ต่อ update รวม O(TN²D) บวก (T+1)N objective calls การ vectorize ไม่เปลี่ยนลำดับความซับซ้อน กรณีเก็บ trace ทั้งหมดใช้ O(TND) และตัวคำนวณ pairwise ใช้หน่วยความจำชั่วคราว O(N²D)

## 8. ข้อจำกัดของผลทดลองนี้?

เพียงสอง smooth functions ใน 2D และ 30 runs ต่อ method/function พารามิเตอร์คงที่ ไม่มี tuning, significance test หรือ constrained application results จึงไม่สรุปว่า GOA ดีที่สุดเสมอ

## 9. ทำไมดาวเขียวกับ best-so-far ไม่ตรงกัน?

ดาวเขียวเป็น known optimum จากสูตร ไม่ส่งให้อัลกอริทึมใช้ค้นหา ส่วนสีส้มเป็นคำตอบที่หาได้จนถึง frame นั้น ความต่างสะท้อน error ที่ยังเหลือ และ archive ไม่จำเป็นต้องเป็นหนึ่งใน current agents ของ GOA/GA

## 10. ค่าศูนย์บน log scale จัดการอย่างไร?

เก็บค่าจริงใน JSON CSV NPZ โดยไม่เปลี่ยน ใช้ max(value, 1e-16) เฉพาะพิกัดที่วาดบน log axis พร้อมบอก floor ใน label ข้อมูล Rosenbrock contour ใช้ log10(1+f) เพื่อสีเท่านั้น ส่วน title และผลทดลองใช้ f จริง

## 11. ตัวอย่าง animation ถูกเลือกให้ดูดีที่สุดหรือไม่?

ไม่ seed 424242 ถูกกำหนดและเขียนใน config ก่อนเริ่มสถิติ ชุด animation แยกอยู่ใน examples/ ไม่รวมใน 180 statistical runs และไม่ใช้เพื่อประกาศผู้ชนะ

## 12. GOA ชนะในงานนี้หรือไม่?

มี median ต่ำสุดทั้งสอง functions ภายใต้ setup นี้ แต่ RLS เร็วกว่า และ worst Rosenbrock ของ GOA 4.526e-02 มากกว่า RLS 1.101e-02 ไม่ได้ทดสอบนัยสำคัญและไม่สรุป universal superiority

## 13. จำนวน evaluations เท่ากันแล้วทำไมเวลาไม่เท่ากัน?

GOA คำนวณ social interactions ทุกคู่ GA ทำ selection crossover mutation ส่วน RLS เสนอและตรวจการขยับเป็นราย agent objective ของเรามีราคาถูก จึงเห็นต้นทุนภายในชัด เวลา runtime ไม่รวมการ export และเป็นผลบนเครื่องนี้

## 14. seed เดียวกันข้าม methods แปลว่ารันไม่ independent หรือไม่?

รันภายในแต่ละ method ใช้ seed ที่แตกต่างกัน ระหว่าง methods จับคู่ initial state ด้วย seed เดียวกันเพื่อควบคุมสภาพเริ่มต้น ดังนั้นข้อมูลข้าม methods มีการจับคู่ ไม่ควรใช้วิธีวิเคราะห์ทางสถิติที่สมมติว่าทุกกลุ่มอิสระต่อกันโดยไม่พิจารณาเรื่องนี้
