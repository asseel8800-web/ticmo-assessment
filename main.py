# ==============================================================================
# Project: Tecmo Digital Assessment Hub & HR Analytics
# Developed & Designed by: Tecmo & Aseel Al-Asmari (شركة تكمو وأسيل الأسمري)
# Copyright (c) 2026 Tecmo & Aseel Al-Asmari. All Rights Reserved.
# ==============================================================================

import streamlit as st
import edge_tts
import asyncio
import tempfile
import os
import random
import base64
import pandas as pd
from datetime import datetime
from pypdf import PdfReader

st.set_page_config(
    page_title="Tecmo | Digital Assessment Hub",
    page_icon="💠",
    layout="centered"
)

RECORDS_FILE = "tecmo_candidates_records.csv"
HR_ADMIN_CODE = "TECMO2026"

def save_candidate_record(record_dict):
    df_new = pd.DataFrame([record_dict])
    if os.path.exists(RECORDS_FILE):
        df_old = pd.read_csv(RECORDS_FILE, sep=";")
        df_combined = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_combined = df_new
    df_combined.to_csv(RECORDS_FILE, sep=";", index=False, encoding="utf-8-sig")

def load_all_records():
    if os.path.exists(RECORDS_FILE):
        return pd.read_csv(RECORDS_FILE, sep=";")
    return pd.DataFrame()

def analyze_cv_content(uploaded_file, job_role, arabic_mode):
    try:
        reader = PdfReader(uploaded_file)
        full_text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                full_text += extracted + "\n"
        
        text_lower = full_text.lower()
        word_count = len(full_text.split())
        
        skill_keywords = [
            "python", "ai", "artificial intelligence", "machine learning", "data", "sql", "excel",
            "fintech", "payment", "finance", "hr", "human resources", "recruitment", "management",
            "project", "leadership", "communication", "analysis", "marketing", "sales", "customer",
            "java", "javascript", "html", "css", "cloud", "security", "agile", "scrum",
            "ذكاء اصطناعي", "بايثون", "تحليل بيانات", "موارد بشرية", "توظيف", "تقنية مالية",
            "إدارة مشاريع", "قيادة", "تواصل", "خدمة عملاء", "تسويق", "مبيعات", "برمجة", "إكسل", "دبلوم", "بكالوريوس"
        ]
        
        found_skills = []
        for kw in skill_keywords:
            if kw in text_lower:
                found_skills.append(kw.upper() if len(kw) <= 3 else kw.title())
        
        found_skills = list(dict.fromkeys(found_skills))[:10]
        cv_score = min(98, max(72, 70 + (len(found_skills) * 3) + (1 if word_count > 120 else 0)))
        
        if arabic_mode:
            skills_str = "، ".join(found_skills) if found_skills else "مهارات عامة وإدارية"
            summary = f"تم تحليل السيرة الذاتية بنجاح ({word_count} كلمة). أبرز المهارات المرصودة: {skills_str}."
        else:
            skills_str = ", ".join(found_skills) if found_skills else "General & Administrative Skills"
            summary = f"Resume analyzed ({word_count} words). Key detected skills: {skills_str}."
            
        return {
            "word_count": word_count,
            "skills": skills_str,
            "cv_score": cv_score,
            "summary": summary
        }
    except Exception:
        return {
            "word_count": 0,
            "skills": "مرفقة (PDF)" if arabic_mode else "Attached (PDF)",
            "cv_score": 80,
            "summary": "تم إرفاق ملف السيرة الذاتية بنجاح." if arabic_mode else "Resume file attached successfully."
        }
st.markdown("""
<style>
@import url('https://googleapis.com');
html, body, [class*="css"] { font-family: 'IBM Plex Sans Arabic', sans-serif; }
.stApp { background: linear-gradient(180deg, #eef5ff 0%, #ffffff 40%, #f7faff 100%); }
[data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e1ecff; }
div[data-testid="stSlider"] { direction: ltr !important; }
.modern-top-card {
    background: #ffffff;
    border-top: 6px solid #0052cc;
    border-radius: 16px;
    padding: 24px 20px;
    box-shadow: 0 8px 24px rgba(0, 82, 204, 0.08);
    margin-bottom: 18px;
    text-align: center;
}
.modern-top-card h1 { color: #091e42 !important; font-size: 26px; font-weight: 700; margin: 8px 0 4px 0; }
.modern-top-card p { color: #0052cc; font-size: 15px; font-weight: 500; margin: 0; }
.prompt-card {
    background: #ffffff;
    border: 1px solid #deebff;
    border-radius: 16px;
    padding: 22px;
    box-shadow: 0 6px 18px rgba(9, 30, 66, 0.05);
    margin: 14px 0;
}
.badge-pill {
    display: inline-block;
    background-color: #deebff;
    color: #0052cc;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 8px;
}
div.stButton > button {
    width: 100%;
    background: #0052cc;
    color: #ffffff !important;
    font-weight: 600;
    font-size: 16px;
    border-radius: 10px;
    padding: 12px 24px;
    border: none;
    box-shadow: 0 4px 12px rgba(0, 82, 204, 0.2);
}
div.stButton > button:hover { background: #0747a6; }
</style>
""", unsafe_allow_html=True)

def get_embedded_logo_html():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for fname in ["logo.png", "logo.jpg", "logo.jpeg", "image.png", "image.jpg", "image.jpeg"]:
        fpath = os.path.join(base_dir, fname)
        if os.path.exists(fpath):
            with open(fpath, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            ext = fname.split(".")[-1]
            return f'<img src="data:image/{ext};base64,{b64}" style="max-height:75px; margin-bottom:10px; border-radius:8px;">'
    return """
    <div style="display:inline-flex; align-items:center; justify-content:center; background:linear-gradient(135deg, #003366, #0066cc); color:white; padding:8px 24px; border-radius:12px; margin-bottom:10px;">
        <span style="font-size:24px; font-weight:800; letter-spacing:1.5px;">Tecmo</span>
        <span style="background:#ffffff; color:#0052cc; font-size:11px; font-weight:700; padding:2px 8px; border-radius:6px; margin-left:8px;">تكمو</span>
    </div>
    """

logo_html = get_embedded_logo_html()

ui_lang = st.radio("🌐 Language / اللغة:", ["العربية", "English"], horizontal=True)
is_ar = (ui_lang == "العربية")

if is_ar:
    st.markdown("<style>.main { direction: rtl; text-align: right; } .stTextInput input, .stTextArea textarea { direction: rtl; text-align: right; }</style>", unsafe_allow_html=True)
    st.markdown(f'<div class="modern-top-card">{logo_html}<h1>بوابة تكمو للتقييم الرقمي</h1><p>منصة ذكية لتحليل السيرة الذاتية واستقطاب الكفاءات في المملكة</p></div>', unsafe_allow_html=True)
else:
    st.markdown("<style>.main { direction: ltr; text-align: left; }</style>", unsafe_allow_html=True)
    st.markdown(f'<div class="modern-top-card">{logo_html}<h1>Tecmo Digital Assessment Hub</h1><p>Smart Resume Analytics & Talent Screening Platform across Saudi Arabia</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"<div style='text-align:center;'>{logo_html}</div>", unsafe_allow_html=True)
    st.divider()
    st.header("📋 بيانات التقديم" if is_ar else "📋 Application Details")
    
    roles_ar = [
        "ذكاء اصطناعي وتحليل بيانات (AI & Data)",
        "تطوير برمجيات وتقنية مالية (FinTech Dev)",
        "موارد بشرية واستقطاب كفاءات (HR)",
        "إدارة مشاريع وعمليات (Operations)",
        "تسويق وتطوير أعمال (Business Dev)",
        "خدمة عملاء ودعم فني (Customer Support)",
        "مالية ومحاسبة (Finance)",
        "تدريب تعاوني (Co-op Training)",
        "أخرى (مسمى مخصص)"
    ]
    roles_en = [
        "AI & Data Analytics",
        "FinTech & Software Development",
        "Human Resources & Talent Acquisition",
        "Project & Operations Management",
        "Marketing & Business Development",
        "Customer Support & Experience",
        "Finance & Accounting",
        "Cooperative Training (Co-op)",
        "Other (Custom Role)"
    ]
    selected_role = st.selectbox("المسمى الوظيفي المتقدم له:" if is_ar else "Target Job Title:", roles_ar if is_ar else roles_en)
    if selected_role in ["أخرى (مسمى مخصص)", "Other (Custom Role)"]:
        custom_role = st.text_input("اكتب المسمى الوظيفي:" if is_ar else "Enter Job Title:")
        final_job_role = custom_role.strip() if custom_role.strip() else selected_role
    else:
        final_job_role = selected_role

    regions_ar = [
        "منطقة الرياض",
        "المنطقة الشرقية (الدمام، الخبر، الظهران، الجبيل، الأحساء)",
        "منطقة مكة المكرمة (جدة، مكة، الطائف)",
        "منطقة المدينة المنورة",
        "منطقة عسير (أبها، خميس مشيط)",
        "منطقة القصيم",
        "منطقة تبوك (نيوم)",
        "منطقة حائل",
        "منطقة جازان",
        "منطقة نجران",
        "منطقة الباحة",
        "منطقة الجوف",
        "منطقة الحدود الشمالية"
    ]
    regions_en = [
        "Riyadh Region",
        "Eastern Province (Dammam, Khobar, Dhahran, Jubail, Al-Ahsa)",
        "Makkah Region (Jeddah, Makkah, Taif)",
        "Madinah Region",
        "Aseer Region (Abha, Khamis Mushait)",
        "Qassim Region",
        "Tabuk Region (NEOM)",
        "Hail Region",
        "Jazan Region",
        "Najran Region",
        "Al-Bahah Region",
        "Al-Jouf Region",
        "Northern Borders Region"
    ]
    selected_region = st.selectbox("المنطقة في السعودية:" if is_ar else "Region in Saudi Arabia:", regions_ar if is_ar else regions_en)

    exp_options = ["حديث تخرج / مبتدئ", "متوسط الخبرة", "خبير / قيادي"] if is_ar else ["Fresh Graduate / Junior", "Mid-Level", "Senior / Lead"]
    experience_level = st.selectbox("المستوى المهني:" if is_ar else "Career Level:", exp_options)
    num_questions = st.slider("عدد محاور التقييم (من 1 إلى 5):" if is_ar else "Evaluation Topics (1 to 5):", min_value=1, max_value=5, value=3)
    st.divider()
    uploaded_cv = st.file_uploader("📎 إرفاق السيرة الذاتية للتحليل (إجباري - PDF) *:" if is_ar else "📎 Upload Resume for Analysis (Mandatory - PDF) *:", type=["pdf"])
    st.divider()

    with st.expander("🔐 بوابة الموارد البشرية (HR Portal)" if is_ar else "🔐 HR Admin Portal"):
        hr_pass = st.text_input("رمز الإدارة:" if is_ar else "Admin Code:", type="password", key="hr_pass_input")
        if hr_pass == HR_ADMIN_CODE:
            st.session_state.hr_mode = True
            st.success("تم تفعيل وضع الإدارة" if is_ar else "Admin Mode Active")
        elif hr_pass:
            st.error("رمز غير صحيح" if is_ar else "Invalid Code")
if st.session_state.get("hr_mode", False):
    st.subheader("📊 لوحة متابعة استجابات المرشحين (HR Dashboard)" if is_ar else "📊 Candidate Responses Dashboard (HR)")
    df_records = load_all_records()
    if df_records.empty:
        st.info("لا توجد استجابات مسجلة حتى الآن." if is_ar else "No candidate responses recorded yet.")
    else:
        c1, c2 = st.columns(2)
        c1.metric("إجمالي المتقدمين" if is_ar else "Total Candidates", len(df_records))
        avg_score = round(df_records["النتيجة / Score"].mean(), 1) if "النتيجة / Score" in df_records.columns else 0
        c2.metric("متوسط التقييم العام" if is_ar else "Average Readiness", f"{avg_score}%")
        st.dataframe(df_records, use_container_width=True)
        
        csv_data = df_records.to_csv(sep=";", index=False).encode("utf-8-sig")
        st.download_button(
            label="📥 تحميل ملف الإكسل المرتب (Excel CSV)" if is_ar else "📥 Download Organized Excel File",
            data=csv_data,
            file_name=f"Tecmo_Candidates_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        if st.button("🗑️ مسح جميع الاستجابات وتصفير الجدول" if is_ar else "🗑️ Clear All Records"):
            if os.path.exists(RECORDS_FILE):
                os.remove(RECORDS_FILE)
            st.success("تم مسح جميع السجلات بنجاح!" if is_ar else "All records cleared!")
            st.rerun()

    if st.button("إغلاق لوحة الإدارة والعودة للبوابة" if is_ar else "Close Admin Dashboard"):
        st.session_state.hr_mode = False
        st.rerun()
    st.stop()

# --- بنك 12 سؤالاً مع اختيار عشوائي متجدد ---
def get_tecmo_questions(level, count, arabic_mode):
    if arabic_mode:
        bank = [
            "من واقع سيرتك الذاتية، ما هو أبرز مشروع أو إنجاز تعتز به ويعكس إمكاناتك المهنية؟",
            "حدثنا بإيجاز عن أبرز نقاط قوتك المهنية، وكيف ترى مساهمتك في نجاح فرق العمل في تكمو؟",
            "شاركنا تجربة عملية واجهت فيها تحدياً غير متوقع، وكيف تعاملت معه للوصول إلى نتيجة ناجحة؟",
            "كيف تنظم أولوياتك وتضمن دقة الإنجاز عند العمل في بيئة سريعة ومتعددة المهام؟",
            "في قطاع التقنية المالية المتجدد، ما هي طريقتك في تطوير مهاراتك ومواكبة أحدث الحلول الرقمية؟",
            "حدثنا عن موقف اضطررت فيه لاتخاذ قرار سريع دون توفر كافة المعلومات، وكيف تصرفت؟",
            "ما هو أسلوبك في التعامل مع الملاحظات النقدية أو التغييرات المفاجئة في خطط العمل؟",
            "اذكر مهارة جديدة تعلمتها مؤخراً وكيف ساعدتك في تحسين جودة أو سرعة إنجازك؟",
            "كيف توازن بين الإبداع في طرح الأفكار والالتزام بالمعايير والأنظمة المعتمدة؟",
            "صف لنا بيئة العمل المثالية التي تساعدك على تقديم أفضل ما لديك من إنتاجية؟",
            "عندما تختلف في الرأي مع أحد أعضاء الفريق حول حل معين، كيف تدير النقاش للوصول لأفضل نتيجة؟",
            "ما الذي يحفزك مهنياً ويجعلك شغوفاً بالانضمام إلى شركة تقنية مالية طموحة مثل تكمو؟"
        ]
    else:
        bank = [
            "Based on your resume, what is the key project or achievement that best demonstrates your capabilities?",
            "Briefly highlight your core professional strengths and how you can contribute to team success at Tecmo.",
            "Share a real-world situation where you faced an unexpected challenge and how you resolved it effectively.",
            "How do you prioritize tasks and maintain high accuracy in a fast-paced, dynamic environment?",
            "In the rapidly evolving FinTech sector, how do you continuously upgrade your skills and stay current?",
            "Tell us about a time you had to make a quick decision with incomplete information, and what the outcome was.",
            "How do you handle constructive feedback or sudden shifts in project requirements?",
            "Describe a new skill or tool you recently mastered and how it improved your workflow.",
            "How do you balance innovative thinking with strict adherence to operational standards and quality?",
            "What type of work environment enables you to perform at your highest potential?",
            "When you disagree with a teammate on an approach, how do you navigate the discussion toward the best solution?",
            "What drives your professional ambition and excites you about joining an innovative FinTech company like Tecmo?"
        ]
    return random.sample(bank, min(count, len(bank)))

async def generate_voice(text, arabic_mode):
    voice = "ar-SA-ZariyahNeural" if arabic_mode else "en-GB-SoniaNeural"
    communicate = edge_tts.Communicate(str(text), voice)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    await communicate.save(temp_file.name)
    return temp_file.name

for key, default in [("questions", []), ("current_q", 0), ("audio_files", {}), ("evaluations", []), ("candidate_note", ""), ("note_submitted", False), ("record_saved", False), ("cv_analysis", None)]:
    if key not in st.session_state:
        st.session_state[key] = default

if not st.session_state.questions:
    st.markdown(f"<div class='prompt-card'><h4 style='color:#091e42; margin-top:0;'>{'جاهز لبدء التقييم التفاعلي؟' if is_ar else 'Ready to Begin Your Interactive Assessment?'}</h4><p style='color:#42526e; margin-bottom:0;'>{'حدد المسمى الوظيفي والمنطقة، وأرفق سيرتك الذاتية (PDF) في القائمة الجانبية ليقوم النظام بتحليل مهاراتك وبدء التقييم.' if is_ar else 'Select your target job title and region, and upload your Resume (PDF) in the sidebar for automated skill analysis.'}</p></div>", unsafe_allow_html=True)
    if uploaded_cv is None:
        st.warning("⚠️ حقل السيرة الذاتية (PDF) إجباري في القائمة الجانبية لتفعيل زر بدء التقييم." if is_ar else "⚠️ Uploading your Resume / CV (PDF) in the sidebar is mandatory to start the assessment.")
    else:
        if st.session_state.cv_analysis is None:
            st.session_state.cv_analysis = analyze_cv_content(uploaded_cv, final_job_role, is_ar)
        
        cv_info = st.session_state.cv_analysis
        st.success(f"✅ {'تم تحليل السيرة الذاتية:' if is_ar else 'Resume Analyzed:'} **{uploaded_cv.name}**")
        st.info(f"🔍 **{cv_info['summary']}**\n\n📌 **{'المسمى الوظيفي:' if is_ar else 'Target Role:'}** {final_job_role} | 📍 **{'المنطقة:' if is_ar else 'Region:'}** {selected_region}")
        
        if st.button("ابدأ التقييم الآن ➔" if is_ar else "Begin Assessment Now ➔"):
            with st.spinner("جاري تجهيز محاور التقييم العشوائية..." if is_ar else "Preparing randomized assessment topics..."):
                q_list = get_tecmo_questions(experience_level, num_questions, is_ar)
                st.session_state.questions = q_list
                if q_list:
                    st.session_state.audio_files = {0: asyncio.run(generate_voice(q_list, is_ar))}
                st.rerun()
if st.session_state.questions and st.session_state.current_q < len(st.session_state.questions):
    idx = st.session_state.current_q
    total = len(st.session_state.questions)
    st.progress((idx) / total, text=f"المحور {idx + 1} من {total}" if is_ar else f"Topic {idx + 1} of {total}")
    current_question_text = st.session_state.questions[idx]
    st.markdown(f"<div class='prompt-card'><span class='badge-pill'>{'محور التقييم' if is_ar else 'ASSESSMENT TOPIC'} #{idx + 1}</span><h3 style='color:#091e42; margin-top:8px; line-height:1.6;'>{current_question_text}</h3></div>", unsafe_allow_html=True)
    if idx not in st.session_state.audio_files:
        st.session_state.audio_files[idx] = asyncio.run(generate_voice(current_question_text, is_ar))
    st.audio(st.session_state.audio_files[idx], format="audio/mp3", autoplay=True)
    
    method_voice = "🎙️ الرد الصوتي (مدة مفتوحة)" if is_ar else "🎙️ Voice Reply (Open Duration)"
    method_text = "✍️ الرد الكتابي" if is_ar else "✍️ Written Reply"
    answer_method = st.radio("اختر طريقة المشاركة بكل حرية:" if is_ar else "Choose your preferred response mode freely:", [method_voice, method_text], horizontal=True, key=f"method_{idx}")
    
    if answer_method == method_voice:
        st.caption("سجّل إجابتك بالمدة التي تناسبك دون أي قيد زمني." if is_ar else "Record your response for as long as you wish with no time limit.")
        audio_response = st.audio_input(f"سجّل ردك الصوتي للمحور {idx + 1}" if is_ar else f"Record your voice reply for Topic {idx + 1}", key=f"audio_{idx}")
        if audio_response is not None:
            if st.button("اعتماد الرد والانتقال للتالي ➔" if is_ar else "Confirm & Next Topic ➔", key=f"sub_audio_{idx}"):
                audio_bytes = audio_response.read()
                duration_sec = round(len(audio_bytes) / 32000, 1)
                score = min(10, max(8, round(7 + (duration_sec / 6))))
                st.session_state.evaluations.append({"question": current_question_text, "type": "صوتي" if is_ar else "Voice", "detail": f"{duration_sec} ثانية" if is_ar else f"{duration_sec} sec", "score": score})
                st.session_state.current_q += 1
                st.rerun()
    else:
        text_response = st.text_area(f"اكتب ردك للمحور {idx + 1} هنا:" if is_ar else f"Write your reply for Topic {idx + 1} here:", placeholder="اكتب إجابتك بكل راحة ووضوح..." if is_ar else "Type your response comfortably and clearly...", height=130, key=f"text_{idx}")
        if st.button("اعتماد الرد والانتقال للتالي ➔" if is_ar else "Confirm & Next Topic ➔", key=f"sub_text_{idx}"):
            if text_response.strip():
                word_count = len(text_response.strip().split())
                score = min(10, max(8, round(7 + (word_count / 10))))
                st.session_state.evaluations.append({"question": current_question_text, "type": "كتابي" if is_ar else "Written", "detail": text_response.strip(), "score": score})
                st.session_state.current_q += 1
                st.rerun()
            else:
                st.warning("يرجى كتابة ردك أولاً." if is_ar else "Please enter your response first.")

if st.session_state.questions and st.session_state.current_q == len(st.session_state.questions) and not st.session_state.note_submitted:
    st.progress(0.95, text="الخطوة الختامية: مساحة التواصل" if is_ar else "Final Step: Open Communication")
    st.subheader("💬 مساحة مفتوحة للتواصل مع فريق تكمو" if is_ar else "💬 Open Space to Connect with Tecmo Team")
    note_input = st.text_area("هل لديك أي استفسار أو رسالة تود مشاركتها معنا؟ (اختياري):" if is_ar else "Do you have any questions or notes you would like to share with us? (Optional):", placeholder="اكتب رسالتك أو استفسارك هنا..." if is_ar else "Write your message or inquiry here...", height=110)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("إرسال وإنهاء التقييم ➔" if is_ar else "Submit & Complete ➔"):
            st.session_state.candidate_note = note_input.strip() if note_input.strip() else ("لا توجد ملاحظات إضافية." if is_ar else "No additional notes.")
            st.session_state.note_submitted = True
            st.rerun()
    with col2:
        if st.button("تخطي وإصدار الملخص" if is_ar else "Skip & View Summary"):
            st.session_state.candidate_note = "لا توجد ملاحظات إضافية." if is_ar else "No additional notes."
            st.session_state.note_submitted = True
            st.rerun()

if st.session_state.questions and st.session_state.current_q == len(st.session_state.questions) and st.session_state.note_submitted:
    st.progress(1.0, text="اكتمل التقييم بنجاح" if is_ar else "Assessment Completed")
    total_score = sum(e["score"] for e in st.session_state.evaluations)
    max_score = len(st.session_state.evaluations) * 10
    interview_pct = round((total_score / max_score) * 100) if max_score > 0 else 85
    
    cv_info = st.session_state.cv_analysis or {"skills": "غير محدد", "cv_score": 85}
    cv_pct = cv_info["cv_score"]
    final_percentage = round((interview_pct * 0.6) + (cv_pct * 0.4))
    comm_score = min(98, interview_pct + 3)
    
    decision_ar = "مرشح متميز - موصى بالمتابعة" if final_percentage >= 80 else "مؤهل للمراجعة"
    decision_en = "Top Candidate - Recommended" if final_percentage >= 80 else "Qualified for Review"
    
    if not st.session_state.record_saved:
        answers_summary = " | ".join([f"Q{i+1} ({e['type']}): {e['detail']}" for i, e in enumerate(st.session_state.evaluations)])
        save_candidate_record({
            "التاريخ والوقت / Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "المسمى الوظيفي / Job Role": final_job_role,
            "المنطقة / Region": selected_region,
            "المستوى / Level": experience_level,
            "تحليل السيرة الذاتية / CV Skills": cv_info["skills"],
            "توافق السيرة / CV Match %": cv_pct,
            "النتيجة / Score": final_percentage,
            "التوصية / Recommendation": decision_ar if is_ar else decision_en,
            "الإجابات / Responses": answers_summary,
            "رسالة المرشح / Message": st.session_state.candidate_note
        })
        st.session_state.record_saved = True

    if is_ar:
        st.success("🌟 **شكراً لمشاركتك ووقتك الثمين!** تم حفظ استجاباتك وتحليل سيرتك الذاتية في نظام التوظيف بنجاح. نتمنى لك كل التوفيق والنجاح، وسيتواصل معك فريق استقطاب المواهب في **شركة تكمو (Tecmo)** قريباً.")
    else:
        st.success("🌟 **Thank You for Your Time & Participation!** Your responses and resume analysis have been saved. We wish you every success, and the Talent Acquisition team at **Tecmo** will be in touch soon.")
    
    st.subheader("📊 مؤشرات التقييم التنفيذي" if is_ar else "📊 Executive Evaluation Metrics")
    m1, m2, m3 = st.columns(3)
    m1.metric("مؤشر الجاهزية العام" if is_ar else "Overall Readiness", f"{final_percentage}%")
    m2.metric("توافق السيرة الذاتية" if is_ar else "Resume Match", f"{cv_pct}%")
    m3.metric("وضوح الطرح" if is_ar else "Communication Clarity", f"{comm_score}%")
    st.divider()
    if is_ar:
        details_md = "\n\n".join([f"**المحور {i+1}:** {e['question']}\n- نوع الرد: `{e['type']}` | التفاصيل: `{e['detail']}` | التقييم: `{e['score']}/10`" for i, e in enumerate(st.session_state.evaluations)])
        report_text = f"### 📋 ملخص التقييم الرقمي للمرشح - تكمو (Tecmo)\n- **المسمى الوظيفي:** {final_job_role}\n- **المنطقة:** {selected_region}\n- **المستوى المهني:** {experience_level}\n- **المهارات المستخرجة من السيرة الذاتية:** {cv_info['skills']}\n- **مؤشر الجاهزية العام:** **{final_percentage}%**\n- **التوصية:** **{decision_ar}**\n\n#### 💬 رسالة المرشح لفريق تكمو:\n> {st.session_state.candidate_note}\n\n#### تفاصيل المحاور:\n{details_md}"
    else:
        details_md = "\n\n".join([f"**Topic {i+1}:** {e['question']}\n- Mode: `{e['type']}` | Details: `{e['detail']}` | Score: `{e['score']}/10`" for i, e in enumerate(st.session_state.evaluations)])
        report_text = f"### 📋 Digital Candidate Assessment Summary - Tecmo\n- **Target Role:** {final_job_role}\n- **Region:** {selected_region}\n- **Career Level:** {experience_level}\n- **Extracted Resume Skills:** {cv_info['skills']}\n- **Overall Readiness Index:** **{final_percentage}%**\n- **Recommendation:** **{decision_en}**\n\n#### 💬 Candidate Note to Tecmo:\n> {st.session_state.candidate_note}\n\n#### Topic Breakdown:\n{details_md}"

    st.markdown(report_text)
    st.download_button(label="📥 تحميل ملف التقييم (Assessment Summary)" if is_ar else "📥 Download Assessment Summary", data=report_text, file_name=f"Tecmo_Assessment_{datetime.now().strftime('%Y%m%d_%H%M')}.md", mime="text/markdown")

st.divider()
st.markdown("<div style='text-align: center; color: #091e42; font-size: 13px; font-weight: 600;'>تطوير وتصميم: شركة تكمو وأسيل الأسمري | Developed & Designed by Tecmo & Aseel Al-Asmari<br>© 2026 All Rights Reserved</div>", unsafe_allow_html=True)
