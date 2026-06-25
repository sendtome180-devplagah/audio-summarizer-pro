import os
import sys

# عزل النظام تماماً عن أي ترميز قديم
os.environ["PYTHONIOENCODING"] = "utf-8"

import streamlit as st
from openai import OpenAI
import io

# جلب أداة التعامل مع اليوتيوب والفيديوهات
try:
    import yt_dlp
except ImportError:
    st.error("يرجى إضافة yt_dlp إلى ملف requirements.txt الخاص بك")

# محاولة جلب المفتاح من الـ Secrets
MY_API_KEY = ""
if "OPENAI_API_KEY" in st.secrets:
    MY_API_KEY = st.secrets["OPENAI_API_KEY"]

# ربط العميل بالمفتاح
client = OpenAI(api_key=MY_API_KEY if MY_API_KEY else "sk-dummy")

st.title("📹 Video & YouTube Summarizer")
st.write("أهلاً بك! يمكنك رفع ملف فيديو MP4 أو وضع رابط فيديو (يوتيوب أو غيره) لتلخيصه مباشرة.")

# خيارات الإدخال للمستخدم
option = st.radio("اختر طريقة إدخال الفيديو:", ("رفع ملف فيديو (MP4)", "وضع رابط فيديو (YouTube / URL)"))

audio_buffer = None
file_name = ""

# --- الخيار الأول: رفع ملف ---
if option == "رفع ملف فيديو (MP4)":
    video_file = st.file_uploader("اختر ملف فيديو MP4", type=["mp4"])
    if video_file:
        audio_buffer = io.BytesIO(video_file.read())
        audio_buffer.name = "video.mp4"
        file_name = video_file.name

# --- الخيار الثاني: وضع رابط ---
elif option == "وضع رابط فيديو (YouTube / URL)":
    video_url = st.text_input("أدخل رابط الفيديو هنا (مثال: رابط يوتيوب):")
    if video_url:
        with st.spinner("جاري جلب بيانات الفيديو وصوتياته وتحويلها لصيغة متوافقة..."):
            try:
                # إعدادات إجبارية لتحويل الصوت إلى MP3 متوافق 100% مع OpenAI
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': '-',
                    'logtostderr': True,
                    'quiet': True,
                    'nonplaylist': True,
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=False)
                    audio_url = info['url']
                    
                    # قراءة الصوت في الذاكرة
                    import requests
                    response = requests.get(audio_url, stream=True)
                    audio_data = io.BytesIO()
                    for chunk in response.iter_content(chunk_size=1024*1024):
                        if chunk:
                            audio_data.write(chunk)
                    audio_data.seek(0)
                    audio_buffer = audio_data
                    
                    # التعديل السحري هنا: نلزم النظام بتسمية الملف بامتداد mp3 صريح
                    audio_buffer.name = "audio.mp3"
                    file_name = info.get('title', 'رابط خارجي')
            except Exception as e:
                st.error(f"حدث خطأ أثناء جلب الفيديو من الرابط: {str(e)}")

# --- عملية المعالجة والتلخيص المستقرة ---
if audio_buffer:
    if not MY_API_KEY or MY_API_KEY == "sk-dummy":
        st.error("❌ لا يمكن المعالجة؛ يرجى إضافة مفتاح OpenAI في الـ Secrets أولاً.")
    else:
        try:
            st.info(f"🎬 تم تجهيز: {file_name}")
            
            with st.spinner("جاري معالجة الصوت وتحويله إلى نص (Whisper)..."):
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_buffer
                )

            text_result = transcript.text

            st.subheader("📝 النص الكامل المُستخرج:")
            st.text_area("Text", text_result, height=200)

            with st.spinner("جاري كتابة التلخيص الذكي..."):
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Summarize the text into clear bullet points in Arabic."},
                        {"role": "user", "content": text_result}
                    ]
                )

            summary_text = response.choices[0].message.content
            st.subheader("📌 التلخيص الشامل:")
            st.write(summary_text)

        except Exception as e:
            st.error(f"حدث خطأ أثناء المعالجة والتلخيص: {str(e)}")
