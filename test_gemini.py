import os
from dotenv import load_dotenv
from google import genai

# 1. อ่าน API Key จากไฟล์ .env
load_dotenv()

# 2. เชื่อมต่อไปยัง Google Gemini
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print("⏳ กำลังส่งคำถามไปถาม Gemini กรุณารอสักครู่...")

# 3. สั่งให้ Gemini ประมวลผลคำตอบ (ใช้โมเดล gemini-2.5-flash ที่ทั้งเร็วและฟรี)
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="ช่วยแนะนำเมนูอาหารคลีนง่ายๆ สำหรับมื้อเย็น 3 เมนู พร้อมบอกแคลอรี่โดยประมาณให้หน่อย",
)

# 4. แสดงผลลัพธ์ที่ Gemini ตอบกลับมา
print("\n🤖 คำตอบจาก Gemini:")
print("=" * 40)
print(response.text)
print("=" * 40)
