import os
import sys

# عزل النظام لضمان اللغة العربية والترميز السليم
os.environ["PYTHONIOENCODING"] = "utf-8"

import streamlit as st
from openai import OpenAI
import io

# جلب المفتاح السري من الـ Secrets
MY_API_KEY = st.secrets.get("OPENAI_API_KEY", "")
client = OpenAI(api_key=MY_API_KEY if MY_API_KEY else "sk-dummy")

st.title("🎙️🎬 منصة رفع وتلخيص المحتوى الصوتي والمرئي")
st.write("مرحباً بك يا بروفيسور! هنا يمكن لطلابك رفع أي ملف صوتي (MP3) أو فيديو (MP4) مباشرة من الجوال أو الكمبيوتر ليقوم الموقع بتلخيصه فوراً.")

# إعداد خانة الرفع لتقبل ملفات الصوت والفيديو مباشرة
uploaded_file = st.file_uploader(
    "اختر ملف الصوت (MP3) أو ملف الفيديو (MP4) المُراد تلخيصه:", 
    type=["mp3", "mp4", "m4a", "wav"]
)

if uploaded_file:
    if not MY_API_KEY or MY_API_KEY == "sk-dummy":
        st.error("❌ يرجى إضافة مفتاح OpenAI في الـ Secrets أولاً.")
    else:
        try:
            # تجهيز الملف في الذاكرة ومطابقة اسمه وامتداده
            audio_buffer = io.BytesIO(uploaded_file.read())
            audio_buffer.name = uploaded_file.name
            
            st.info(f"📁 تم تحميل الملف بنجاح: {uploaded_file.name}")
            
            # 1. مرحلة تفكيك الصوت/الفيديو وتحويله إلى نص (Whisper)
            with st.spinner("⏳ جاري معالجة الملف واستخراج النص بدقة عالية..."):
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_buffer
                )
            
            text_result = transcript.text
            
            if text_result.strip():
                st.subheader("📝 النص الكامل المُستخرج:")
                st.text_area("النص المستخرج", text_result, height=200)
                
                # 2. مرحلة التلخيص الذكي وتحويله لنقاط
                with st.spinner("🧠 جاري صياغة التلخيص الشامل في نقاط واضحة..."):
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Summarize the text into clear, structured bullet points in Arabic."},
                            {"role": "user", "content": text_result}
                        ]
                    )
                
                summary_text = response.choices[0].message.content
                st.subheader("📌 التلخيص الشامل لطلابك:")
                st.write(summary_text)
            else:
                st.warning("⚠️ لم نتمكن من استخراج أي نص، تأكد من أن الملف يحتوي على صوت واضح.")
                
        except Exception as e:
            st.error(f"❌ حدث خطأ أثناء المعالجة والتلخيص: {str(e)}")
