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
        margin-bottom: 15px;
    }

    /* تنسيق بصمة الاسم للبروفيسور */
    .designer-signature {
        color: #1e3c72;
        font-size: 1.2rem;
        font-weight: 700;
        text-align: center !important;
        margin-bottom: 35px;
        background: #ffffff;
        padding: 8px 20px;
        border-radius: 20px;
        display: table;
        margin-right: auto;
        margin-left: auto;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
        border: 1px solid #cbd5e1;
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
    
    /* تصميم صندوق النص المستخرج بخلفية كحلية داكنة ونص أبيض واضح جداً */
    .stTextArea textarea {
        border-radius: 12px !important;
        border: 2px solid #1e3c72 !important;
        font-size: 1.1rem !important;
        line-height: 1.7 !important;
        background-color: #0f172a !important;
        color: #ffffff !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1) !important;
    }
    
    /* تصميم منطقة التلخيص النهائي لتظهر داخل بطاقة بيضاء فخمة بنص داكن مقروء */
    .summary-card {
        background-color: #ffffff;
        border-right: 5px solid #2a5298;
        border-radius: 10px;
        padding: 20px;
        margin-top: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        color: #1e293b !important;
        font-size: 1.1rem;
        line-height: 1.8;
    }
    
    /* تنسيق العناوين الجانبية */
    h2, h3 {
        color: #1e3c72 !important;
        font-weight: 700 !important;
        border-bottom: 2px solid #2a5298;
        padding-bottom: 8px;
        margin-top: 25px !important;
    }
    
    /* إخفاء شريط المساعدة الافتراضي */
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 👑 واجهة المستخدم الرسومية الفخمة ---
st.markdown('<h1 class="main-title">🎙️🎬 منصة التلخيص الذكي والتحليل الصوتي</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">تتيح هذه المنصة رفع الملفات الصوتية (MP3) والمرئية (MP4) وتلخيصها فوراً بلمسات جمالية مريحة.</p>', unsafe_allow_html=True)

# 🏷️ إضافة بصمة تصميم الأستاذ عبد الله بن علي المطرفي
st.markdown('<div class="designer-signature">👨‍💻 برمجة وتصميم: أ/ عبد الله بن علي المطرفي</div>', unsafe_allow_html=True)

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
                
                # وضع التلخيص داخل حاوية بيضاء أنيقة مع نص داكن وواضح 100%
                st.markdown(f'<div class="summary-card">{summary_text}</div>', unsafe_allow_html=True)
            else:
                st.warning("⚠️ لم نتمكن من استخراج أي نص، تأكد من أن الملف يحتوي على صوت واضح ومفهوم.")
                
        except Exception as e:
            st.error(f"❌ حدث خطأ أثناء المعالجة والتلخيص: {str(e)}")
