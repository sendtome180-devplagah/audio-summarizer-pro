import os
import sys

# عزل النظام تماماً عن أي ترميز قديم
os.environ["PYTHONIOENCODING"] = "utf-8"

import streamlit as st
from openai import OpenAI
import io

# محاولة قراءة المفتاح من الإعدادات السرية بأكثر من طريقة لضمان التوافق
if "OPENAI_API_KEY" in st.secrets:
    MY_API_KEY = st.secrets["OPENAI_API_KEY"]
elif "openai_api_key" in st.secrets:
    MY_API_KEY = st.secrets["openai_api_key"]
else:
    # إذا لم يجد المفتاح في الـ Secrets، سيبحث في السطر الأسفل (إذا أردت وضعه يدوياً مستقبلاً بشكل آمن)
    MY_API_KEY = ""

# التحقق من وجود المفتاح قبل تشغيل العميل لئلا تظهر الشاشة الزرقاء المزعجة للطلاب
if not MY_API_KEY:
    st.warning("⚙️ النظام في طور التجهيز خلف الكواليس، يرجى التحقق من إعدادات الـ Secrets في منصة Streamlit.")
    st.stop()

# ربط العميل بالمفتاح المباشر
client = OpenAI(api_key=MY_API_KEY)

st.title("MP3 Summarizer")

audio_file = st.file_uploader(
    "Choose MP3 File",
    type=["mp3"]
)

if audio_file:
    try:
        # قراءة الصوت مباشرة في الذاكرة كبيانات ثنائية خالص بدون مسارات
        audio_bytes = audio_file.read()
        buffer = io.BytesIO(audio_bytes)
        buffer.name = "audio.mp3" 

        with st.spinner("جاري رفع الصوت وتحليله..."):
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=buffer
            )

        text_result = transcript.text

        st.subheader("النص الكامل (Transcript)")
        st.text_area("Text", text_result, height=200)

        with st.spinner("جاري التلخيص..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Summarize the text into clear bullet points in Arabic."},
                    {"role": "user", "content": text_result}
                ]
            )

        summary_text = response.choices[0].message.content
        st.subheader("التلخيص (Summary)")
        st.write(summary_text)

    except Exception as e:
        st.error(f"حدث خطأ أثناء المعالجة: {str(e)}")
