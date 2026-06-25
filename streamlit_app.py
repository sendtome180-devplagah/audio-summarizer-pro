import os
import sys
import re

# عزل النظام لضمان اللغة العربية
os.environ["PYTHONIOENCODING"] = "utf-8"

import streamlit as st
from openai import OpenAI
import io
import requests

try:
    import yt_dlp
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    st.error("يرجى التأكد من تحديث ملف requirements.txt")

# جلب المفتاح السري
MY_API_KEY = st.secrets.get("OPENAI_API_KEY", "")
client = OpenAI(api_key=MY_API_KEY if MY_API_KEY else "sk-dummy")

st.title("📹 Video & YouTube Summarizer")
st.write("أهلاً بك يا بروفيسور! هنا الحل الأكيد والنهائي لتلخيص الفيديوهات وروابط اليوتيوب.")

option = st.radio("اختر طريقة إدخال الفيديو:", ("وضع رابط فيديو (YouTube / URL)", "رفع ملف فيديو (MP4)"))

text_to_summarize = ""
file_name = ""

def get_youtube_id(url):
    pattern = r'(?:https?://)?(?:www\.)?(?:youtube\.com/(?:[^/]+/.+/|(?:v|e(?:mbed)?)|.*[?&]v=)|youtu\.be/)([^"&?/\s]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

# --- الخيار الأول: رابط يوتيوب بالأمر المباشر ---
if option == "وضع رابط فيديو (YouTube / URL)":
    video_url = st.text_input("أدخل رابط فيديو اليوتيوب هنا:")
    if video_url:
        video_id = get_youtube_id(video_url)
        
        # المرحلة 1: جلب النص التلقائي لو وجد (فوري وسريع)
        if video_id:
            with st.spinner("⏳ جاري فحص النصوص البرمجية للفيديو..."):
                try:
                    try:
                        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['ar', 'en'])
                    except:
                        transcript_pieces = YouTubeTranscriptApi.list_transcripts(video_id)
                        transcript_list = transcript_pieces.find_transcript(['ar', 'en']).fetch()
                    text_to_summarize = " ".join([item['text'] for item in transcript_list])
                    file_name = "فيديو يوتيوب (نص جاهز)"
                except:
                    pass

        # المرحلة 2: اقتناص رابط الـ m4a الخام مباشرة وإرساله لـ OpenAI
        if not text_to_summarize:
            with st.spinner("🎬 جاري استخلاص الصوت الخام بنجاح والتحويل لـ Whisper..."):
                try:
                    # إعدادات جلب خفيفة جداً ومباشرة لصوت m4a مدعوم 100%
                    ydl_opts = {
                        'format': 'bestaudio[ext=m4a]/bestaudio', 
                        'quiet': True,
                        'no_warnings': True,
                        'nonplaylist': True
                    }
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(video_url, download=False)
                        audio_url = info['url']
                        
                        # تحميل الملف مباشرة إلى الذاكرة كملف m4a صافي
                        res = requests.get(audio_url)
                        audio_data = io.BytesIO(res.content)
                        audio_data.name = "audio.m4a" # الصيغة الذهبية المدعومة في OpenAI
                        
                        # إرسال الملف فوراً للتفكيك
                        trans = client.audio.transcriptions.create(model="whisper-1", file=audio_data)
                        text_to_summarize = trans.text
                        file_name = info.get('title', 'صوت يوتيوب مستخلص')
                except Exception as err:
                    st.error(f"خطأ في معالجة خادم يوتيوب: {str(err)}")

# --- الخيار الثاني: رفع ملف MP4 عادي ---
elif option == "رفع ملف فيديو (MP4)":
    video_file = st.file_uploader("اختر ملف فيديو MP4", type=["mp4"])
    if video_file:
        audio_buffer = io.BytesIO(video_file.read())
        audio_buffer.name = "video.mp4"
        with st.spinner("جاري تفكيك صوت ملف الـ MP4..."):
            try:
                trans = client.audio.transcriptions.create(model="whisper-1", file=audio_buffer)
                text_to_summarize = trans.text
            except Exception as e:
                st.error(f"خطأ أثناء تفكيك ملف الـ MP4: {str(e)}")

# --- مرحلة التلخيص النهائية ---
if text_to_summarize:
    if not MY_API_KEY or MY_API_KEY == "sk-dummy":
        st.error("❌ يرجى إضافة مفتاح OpenAI في الـ Secrets أولاً.")
    else:
        try:
            st.success("✅ تم تجهيز النص بنجاح!")
            st.subheader("📝 النص الكامل المُستخرج:")
            st.text_area("النص", text_to_summarize, height=200)

            with st.spinner("جاري كتابة التلخيص الذكي لطلابك..."):
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Summarize the text into clear, structured bullet points in Arabic."},
                        {"role": "user", "content": text_to_summarize}
                    ]
                )
            st.subheader("📌 التلخيص الشامل:")
            st.write(response.choices[0].message.content)
        except Exception as e:
            st.error(f"حدث خطأ أثناء التلخيص: {str(e)}")
