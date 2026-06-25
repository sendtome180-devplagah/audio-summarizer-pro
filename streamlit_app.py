import os
import sys
import re

# عزل النظام
os.environ["PYTHONIOENCODING"] = "utf-8"

import streamlit as st
from openai import OpenAI
import io

try:
    import yt_dlp
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    st.error("يرجى التأكد من تحديث ملف requirements.txt")

MY_API_KEY = st.secrets.get("OPENAI_API_KEY", "")
client = OpenAI(api_key=MY_API_KEY if MY_API_KEY else "sk-dummy")

st.title("📹 Video & YouTube Summarizer")
st.write("أهلاً بك يا بروفيسور! يمكنك رفع ملف MP4 أو وضع رابط يوتيوب لتلخيصه مباشرة عبر النصوص المستخرجة ذكياً.")

option = st.radio("اختر طريقة إدخال الفيديو:", ("وضع رابط فيديو (YouTube / URL)", "رفع ملف فيديو (MP4)"))

text_to_summarize = ""
file_name = ""

# دالة ذكية لاستخراج رقم الفيديو من رابط اليوتيوب
def get_youtube_id(url):
    pattern = r'(?:https?://)?(?:www\.)?(?:youtube\.com/(?:[^/]+/.+/|(?:v|e(?:mbed)?)|.*[?&]v=)|youtu\.be/)([^"&?/\s]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

# --- الخيار الأول: رابط يوتيوب (الحل الذكي والسريع) ---
if option == "وضع رابط فيديو (YouTube / URL)":
    video_url = st.text_input("أدخل رابط فيديو اليوتيوب هنا:")
    if video_url:
        video_id = get_youtube_id(video_url)
        if video_id:
            with st.spinner("⏳ جاري سحب النص المكتوب من اليوتيوب مباشرة (لمح لمح البصر)..."):
                try:
                    # محاولة جلب النص باللغة العربية أولاً، ثم الإنجليزية كخيار بديل
                    try:
                        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['ar', 'en'])
                    except:
                        # إذا لم يجد لغة محددة، يجلب قائمة النصوص المتاحة تلقائياً
                        transcript_pieces = YouTubeTranscriptApi.list_transcripts(video_id)
                        transcript_list = transcript_pieces.find_transcript(['ar', 'en']).fetch()
                    
                    # تجميع النص كاملاً
                    text_to_summarize = " ".join([item['text'] for item in transcript_list])
                    file_name = "فيديو يوتيوب"
                except Exception as e:
                    st.warning("⚠️ لم نتمكن من سحب النص التلقائي لليوتيوب مباشرة. سنحاول جلب ملف الصوت الآن...")
                    
                    # حل احتياطي: إذا فشل سحب النص، نستخدم الطريقة التقليدية بالجلب
                    try:
                        ydl_opts = {'format': 'bestaudio/best', 'outtmpl': '-', 'quiet': True}
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            info = ydl.extract_info(video_url, download=False)
                            import requests
                            res = requests.get(info['url'], stream=True)
                            audio_data = io.BytesIO(res.content)
                            audio_data.name = "audio.mp3"
                            
                            with st.spinner("جاري تفكيك صوت الرابط عبر Whisper..."):
                                trans = client.audio.transcriptions.create(model="whisper-1", file=audio_data)
                                text_to_summarize = trans.text
                                file_name = info.get('title', 'فيديو خارجي')
                    except Exception as err:
                        st.error(f"حدث خطأ في جلب الصوت أيضاً: {str(err)}")
        else:
            st.error("الرجاء التأكد من صحة رابط اليوتيوب.")

# --- الخيار الثاني: رفع ملف MP4 عادي ---
elif option == "رفع ملف فيديو (MP4)":
    video_file = st.file_uploader("اختر ملف فيديو MP4", type=["mp4"])
    if video_file:
        audio_buffer = io.BytesIO(video_file.read())
        audio_buffer.name = "video.mp4"
        file_name = video_file.name
        with st.spinner("جاري تفكيك صوت ملف الـ MP4 واستخراج النص..."):
            try:
                trans = client.audio.transcriptions.create(model="whisper-1", file=audio_buffer)
                text_to_summarize = trans.text
            except Exception as e:
                st.error(f"خطأ أثناء تفكيك ملف الـ MP4: {str(e)}")

# --- مرحلة التلخيص النهائية الموحدة ---
if text_to_summarize:
    if not MY_API_KEY or MY_API_KEY == "sk-dummy":
        st.error("❌ يرجى إضافة مفتاح OpenAI في الـ Secrets أولاً.")
    else:
        try:
            st.success(f"✅ تم تجهيز النص بنجاح!")
            st.subheader("📝 النص الكامل المُستخرج:")
            st.text_area("النص", text_to_summarize, height=200)

            with st.spinner("جاري كتابة التلخيص الذكي في نقاط واضحة..."):
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Summarize the text into clear, structured bullet points in Arabic."},
                        {"role": "user", "content": text_to_summarize}
                    ]
                )
            st.subheader("📌 التلخيص الشامل لطلابك:")
            st.write(response.choices[0].message.content)
        except Exception as e:
            st.error(f"حدث خطأ أثناء التلخيص: {str(e)}")
