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

# --- 🎨 لمسات التصميم الإبداعي والـ CSS المطور ---
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Almarai:wght@400;700&display=swap" rel="stylesheet">
    
    <style>
    /* تغيير الخط لكامل المنصة وجعل الاتجاه من اليمين لليسار */
    * {
        font-family: 'Almarai', sans-serif !important;
        direction: rtl;
        text-align: right;
    }
    
    /* تصميم الحاوية الرئيسية للتطبيق */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
    }
    
    /* تنسيق الهيدر والعنوان الرئيسي */
    .main-title {
        background: linear-gradient(45deg, #1e3c72, #2a5298);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem !important;
        font-weight: 700;
        text-align: center !important;
        margin-bottom: 5px;
        padding-top: 10px;
    }
    
    .sub-title {
        color: #556080;
        font-size: 1.1rem;
        text-align: center !important;
        margin-bottom: 30px;
    }
    
    /* تصميم بطاقة رفع الملفات (File Uploader) */
    div[data-testid="stFileUploader"] {
        background-color: #ffffff;
        border: 2px dashed #2a5298 !important;
        border-radius: 15px !important;
        padding: 20px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: #1e3c72 !important;
        box-shadow: 0 6px 20px rgba(42, 82, 152, 0.15);
    }
    
    /* تصميم صناديق النصوص المستخرجة والتلخيص */
    .stTextArea textarea {
        border-radius: 12px !important;
        border: 1px solid #cbd5e1 !important;
        font-size: 1.05rem !important;
        line-height: 1.6 !important;
        background-color: #ffffff !important;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.02) !important;
    }
    
    /* تنسيق العناوين الجانبية */
    h2, h3 {
        color: #1e3c72 !important;
        font-weight: 700 !important;
        border-bottom: 2px solid #2a5298;
        padding-bottom: 8px;
        margin-top: 25px !important;
    }
    
    /* إخفاء شريط المساعدة الافتراضي الصغير لـ Streamlit لتنظيف الواجهة */
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 👑 واجهة المستخدم الرسومية الفخمة ---
st.markdown('<h1 class="main-title">🎙️🎬 منصة التلخيص الذكي والتحليل الصوتي</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">أهلاً بك يا بروفيسور! تتيح هذه المنصة لطلابك رفع الملفات الصوتية (MP3) والمرئية (MP4) لتلخيصها فوراً بلمسات جمالية مريحة.</p>', unsafe_allow_html=True)

# خانة الرفع الأنيقة
uploaded_file = st.file_uploader(
    "اسحب وأفلت ملف الصوت أو الفيديو هنا، أو تصفح من جهازك:", 
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
            
            st.success(f"📁 تم استلام وتحميل الملف بنجاح: {uploaded_file.name}")
            
            # 1. مرحلة تفكيك الصوت/الفيديو وتحويله إلى نص (Whisper)
            with st.spinner("⏳ جاري تفكيك محتوى الملف واستخراج النص بدقة متناهية..."):
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_buffer
                )
            
            text_result = transcript.text
            
            if text_result.strip():
                st.subheader("📝 النص الكامل المُستخرج من المادة:")
                st.text_area("", text_result, height=220)
                
                # 2. مرحلة التلخيص الذكي وتحويله لنقاط
                with st.spinner("🧠 جاري صياغة التلخيص الشامل واستخراج الفوائد في نقاط واضحة..."):
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Summarize the text into clear, beautifully structured bullet points in Arabic with emojis."},
                            {"role": "user", "content": text_result}
                        ]
                    )
                
                summary_text = response.choices[0].message.content
                st.subheader("📌 التلخيص الشامل والفوائد المستخرجة:")
                st.markdown(summary_text)
            else:
                st.warning("⚠️ لم نتمكن من استخراج أي نص، تأكد من أن الملف يحتوي على صوت واضح ومفهوم.")
                
        except Exception as e:
            st.error(f"❌ حدث خطأ أثناء المعالجة والتلخيص: {str(e)}")
