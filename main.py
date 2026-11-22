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
import requests
import re
import pandas as pd
from datetime import datetime
from pypdf import PdfReader

st.set_page_config(
    page_title="Tecmo | Digital Assessment Hub",
    page_icon="💠",
    layout="centered"
)

GOOGLE_SHEETS_WEBHOOK_URL = "https://google.com"

RECORDS_FILE = "tecmo_candidates_records.csv"
HR_ADMIN_CODE = "TECMO2026"

def save_candidate_record(record_dict):
    if GOOGLE_SHEETS_WEBHOOK_URL.startswith("https://"):
        try:
            requests.post(GOOGLE_SHEETS_WEBHOOK_URL, json=record_dict, timeout=8)
        except Exception:
            pass
            
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

def check_email_already_submitted(email_to_check):
    df = load_all_records()
    if not df.empty and "البريد الإلكتروني / Email" in df.columns:
        submitted_emails = df["البريد الإلكتروني / Email"].astype(str).str.lower().str.strip().tolist()
        return email_to_check.lower().strip() in submitted_emails
    return False

def analyze_cv_by_specialty(uploaded_file, target_role, arabic_mode):
    try:
        reader = PdfReader(uploaded_file)
        full_text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                full_text += extracted + "\n"
        
        text_lower = full_text.lower()
        word_count = len(full_text.split())
        
        specialties_db = {
            "الهندسة المدنية والمعمارية والمقاولات (Civil & Construction)": [
                "civil", "architectural", "construction", "autocad", "revit", "structural", "site engineer",
                "quantity surveyor", "contracting", "primavera", "surveying", "concrete",
                "هندسة مدنية", "معماري", "مقاولات", "مهندس موقع", "أوتوكاد", "حساب كميات", "إنشائي", "بناء"
            ],
            "الهندسة الكهربائية والميكانيكية والمصانع (MEP & Manufacturing)": [
                "mechanical", "electrical", "industrial", "manufacturing", "factory", "production", "maintenance",
                "hvac", "plc", "automation", "machinery", "plant", "power",
                "هندسة ميكانيكية", "كهربائية", "صناعية", "مصنع", "إنتاج", "صيانة", "تشغيل", "تكييف", "معدات"
            ],
            "الأمن والسلامة المهنية والجودة (HSE & QA/QC)": [
                "safety", "hse", "osha", "nebosh", "qa", "qc", "quality", "iso", "inspection", "risk assessment",
                "سلامة", "أمن وسلامة", "جودة", "فحص", "أوشا", "نيبوش", "مخاطر", "إيزو"
            ],
            "الموارد البشرية وشؤون الموظفين (HR & Recruitment)": [
                "hr", "human resources", "recruitment", "talent", "payroll", "qiwa", "mudad", "gosi", "personnel",
                "onboarding", "employee relations", "labor law", "saudization", "hrdf",
                "موارد بشرية", "توظيف", "شؤون موظفين", "رواتب", "قوى", "مدد", "تأمينات", "استقطاب", "نظام العمل", "طاقات"
            ],
            "المالية والمحاسبة وسلاسل الإمداد (Finance & Supply Chain)": [
                "finance", "accounting", "supply chain", "procurement", "warehouse", "logistics", "inventory",
                "erp", "sap", "excel", "audit", "costing", "sales", "business development",
                "مالية", "محاسبة", "مشتريات", "مستودعات", "سلاسل إمداد", "لوجستيات", "مخزون", "مبيعات", "عقود"
            ]
        }
        
        specialty_scores = {}
        matched_skills_by_spec = {}
        
        for spec_name, keywords in specialties_db.items():
            matches = []
            for kw in keywords:
                if kw in text_lower:
                    matches.append(kw.upper() if len(kw) <= 4 else kw.title())
            matches = list(dict.fromkeys(matches))
            specialty_scores[spec_name] = len(matches)
            matched_skills_by_spec[spec_name] = matches

        best_specialty = max(specialty_scores, key=specialty_scores.get)
        max_hits = specialty_scores[best_specialty]
        
        if max_hits == 0:
            detected_specialty = "تخصص إداري / ميداني عام (General)" if arabic_mode else "General Admin / Field"
            top_skills = ["مهارات عمل وتنظيم"] if arabic_mode else ["Work & Organization Skills"]
        else:
            detected_specialty = best_specialty
            top_skills = matched_skills_by_spec[best_specialty][:8]

        edu_level = "غير محدد" if arabic_mode else "Not Specified"
        if any(w in text_lower for w in ["master", "mba", "ماجستير"]):
            edu_level = "ماجستير (Master's)" if arabic_mode else "Master's Degree"
        elif any(w in text_lower for w in ["bachelor", "bsc", "ba", "بكالوريوس", "هندسة"]):
            edu_level = "بكالوريوس (Bachelor's)" if arabic_mode else "Bachelor's Degree"
        elif any(w in text_lower for w in ["diploma", "دبلوم", "تقنية"]):
            edu_level = "دبلوم / تقني (Diploma)" if arabic_mode else "Diploma / Technical"

        years_found = re.findall(r'(\d+)\+?\s*(?:years|year|سنة|سنوات)', text_lower)
        exp_years = f"{max([int(y) for y in years_found])} سنوات" if years_found else ("حديث تخرج / غير محدد" if arabic_mode else "Entry / Not Specified")

        cv_score = min(98, max(74, 72 + (max_hits * 4) + (2 if word_count > 150 else 0)))
        skills_str = "، ".join(top_skills) if arabic_mode else ", ".join(top_skills)

        if arabic_mode:
            summary = f"**التصنيف التلقائي للتخصص:** {detected_specialty} | **المؤهل:** {edu_level} | **الخبرة:** {exp_years}\n\n**أبرز المهارات المستخرجة:** {skills_str}"
        else:
            summary = f"**Auto-Detected Specialty:** {detected_specialty} | **Education:** {edu_level} | **Experience:** {exp_years}\n\n**Key Extracted Skills:** {skills_str}"

        return {
            "detected_specialty": detected_specialty,
            "edu_level": edu_level,
            "exp_years": exp_years,
            "skills": skills_str,
            "cv_score": cv_score,
            "summary": summary
        }
    except Exception:
        return {
            "detected_specialty": "مرفقة (PDF)",
            "edu_level": "غير محدد",
            "exp_years": "غير محدد",
            "skills": "ملف PDF مرفق",
            "cv_score": 80,
            "summary": "تم إرفاق السيرة الذاتية بنجاح."
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
    st.markdown(f'<div class="modern-top-card">{logo_html}<h1>بوابة تكمو للتقييم الرقمي</h1><p>منصة ذكية لتحليل وتصنيف السير الذاتية واستقطاب الكفاءات في المملكة</p></div>', unsafe_allow_html=True)
else:
    st.markdown("<style>.main { direction: ltr; text-align: left; }</style>", unsafe_allow_html=True)
    st.markdown(f'<div class="modern-top-card">{logo_html}<h1>Tecmo Digital Assessment Hub</h1><p>Smart Resume Classification & Talent Screening Platform across Saudi Arabia</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"<div style='text-align:center;'>{logo_html}</div>", unsafe_allow_html=True)
    st.divider()
    st.header("📋 بيانات التقديم" if is_ar else "📋 Application Details")
    
    roles_ar = [
        "أخصائي / موظف موارد بشرية وشؤون موظفين (HR)",
        "مسؤول استقطاب وتوظيف وعلاقات حكومية (قوى / مدد)",
        "مهندس مدني / معماري / موقع (مقاولات)",
        "مهندس ميكانيكي / كهربائي / صيانة",
        "مشرف إنتاج وتشغيل",
        "مشرف أمن وسلامة مهنية (HSE / Safety)",
        "مهندس ضبط جودة (QA/QC)",
        "أمين مستودع / مشتريات وسلاسل إمداد",
        "محاسب / مالية وتكاليف",
        "تطوير أعمال وعقود ومبيعات",
        "تدريب تعاوني (Co-op Training)",
        "أخرى (مسمى مخصص)"
    ]
    roles_en = [
        "HR & Personnel Specialist",
        "Talent Acquisition & Gov Relations (Qiwa / Mudad)",
        "Civil / Architectural / Site Engineer",
        "Mechanical / Electrical / Maintenance Engineer",
        "Production & Operations Supervisor",
        "Health & Safety Officer (HSE / Safety)",
        "Quality Assurance / Control Engineer (QA/QC)",
        "Warehouse / Procurement & Supply Chain",
        "Accountant / Finance & Costing",
        "Business Development & Contracts",
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
    uploaded_cv = st.file_uploader("📎 إرفاق السيرة الذاتية للتحليل والتصنيف (إجباري - PDF) *:" if is_ar else "📎 Upload Resume for Analysis (Mandatory - PDF) *:", type=["pdf"])
    st.divider()

    with st.expander("🔐 بوابة الموارد البشرية (HR Portal)" if is_ar else "🔐 HR Admin Portal"):
        hr_pass = st.text_input("رمز الإدارة:" if is_ar else "Admin Code:", type="password", key="hr_pass_input")
        if hr_pass == HR_ADMIN_CODE:
            st.session_state.hr_mode = True
            st.success("تم تفعيل وضع الإدارة" if is_ar else "Admin Mode Active")
        elif hr_pass:
            st.error("رمز غير صحيح" if is_ar else "Invalid Code")
if st.session_state.get("hr_mode", False):
    st.subheader("📊 لوحة متابعة وتصنيف المرشحين حسب التخصص (HR Dashboard)" if is_ar else "📊 Candidate Analytics & Top Picks by Specialty (HR)")
    df_records = load_all_records()
    if df_records.empty:
        st.info("لا توجد استجابات في الجلسة الحالية. جميع الاستجابات السابقة محفوظة في Google Sheets." if is_ar else "No session responses yet. All past submissions are safely stored in Google Sheets.")
    else:
        if "التخصص المكتشف / Detected Specialty" in df_records.columns and "النتيجة / Score" in df_records.columns:
            df_records = df_records.sort_values(
                by=["التخصص المكتشف / Detected Specialty", "النتيجة / Score"],
                ascending=[True, False]
            ).reset_index(drop=True)
            
            df_records["الترتيب في التخصص / Rank"] = df_records.groupby("التخصص المكتشف / Detected Specialty")["النتيجة / Score"].rank(ascending=False, method="min").astype(int)
            df_records["حالة الترشيح / Nomination"] = df_records["الترتيب في التخصص / Rank"].apply(
                lambda r: "🏆 أفضل ترشيح للتخصص (Top Pick)" if r == 1 else f"المركز #{r} في التخصص"
            )

        c1, c2 = st.columns(2)
        c1.metric("متقدمو الجلسة الحالية" if is_ar else "Current Session Candidates", len(df_records))
        avg_score = round(df_records["النتيجة / Score"].mean(), 1) if "النتيجة / Score" in df_records.columns else 0
        c2.metric("متوسط التقييم العام" if is_ar else "Average Readiness", f"{avg_score}%")
        
        if "التخصص المكتشف / Detected Specialty" in df_records.columns:
            spec_filter = st.selectbox("تصفية وعرض الأفضل حسب التخصص:" if is_ar else "Filter & View Top Picks by Specialty:", ["الكل (مرتب حسب التخصص) / All"] + df_records["التخصص المكتشف / Detected Specialty"].unique().tolist())
            if spec_filter != "الكل (مرتب حسب التخصص) / All":
                df_display = df_records[df_records["التخصص المكتشف / Detected Specialty"] == spec_filter]
            else:
                df_display = df_records
        else:
            df_display = df_records
                
        st.dataframe(df_display, use_container_width=True)
        
        csv_data = df_display.to_csv(sep=";", index=False).encode("utf-8-sig")
        st.download_button(
            label="📥 تحميل ملف الإكسل المرتب بأفضل الترشيحات (Excel CSV)" if is_ar else "📥 Download Ranked Excel by Specialty (CSV)",
            data=csv_data,
            file_name=f"Tecmo_Top_Candidates_By_Specialty_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

    if st.button("إغلاق لوحة الإدارة والعودة للبوابة" if is_ar else "Close Admin Dashboard"):
        st.session_state.hr_mode = False
        st.rerun()
    st.stop()

def get_tecmo_questions(level, count, arabic_mode):
    if arabic_mode:
        bank = [
            "من واقع سيرتك الذاتية، ما هو أبرز مشروع أو إنجاز تعتز به ويعكس إمكاناتك المهنية؟",
            "حدثنا بإيجاز عن أبرز نقاط قوتك المهنية، وكيف ترى مساهمتك في نجاح فرق العمل في تكمو؟",
            "شاركنا تجربة عملية واجهت فيها تحدياً غير متوقع، وكيف تعاملت معه للوصول إلى نتيجة ناجحة؟",
            "كيف تنظم أولوياتك وتضمن دقة الإنجاز عند العمل في بيئة سريعة ومتعددة المهام؟",
            "في قطاع المقاولات الهندسية وإدارة الكوادر، ما هي طريقتك في تطوير مهاراتك ومواكبة أحدث المعايير المهنية؟",
            "حدثنا عن موقف اضطررت فيه لاتخاذ قرار سريع دون توفر كافة المعلومات، وكيف تصرفت؟",
            "ما هو أسلوبك في التعامل مع الملاحظات النقدية أو التغييرات المفاجئة في خطط العمل؟",
            "اذكر مهارة جديدة تعلمتها مؤخراً وكيف ساعدتك في تحسين جودة أو سرعة إنجازك؟",
            "كيف توازن بين الإبداع في طرح الأفكار والالتزام بالمعايير والأنظمة المعتمدة؟",
            "صف لنا بيئة العمل المثالية التي تساعدك على تقديم أفضل ما لديك من إنتاجية؟",
            "عندما تختلف في الرأي مع أحد أعضاء الفريق حول حل معين، كيف تدير النقاش للوصول لأفضل نتيجة؟",
            "ما الذي يحفزك مهنياً ويجعلك شغوفاً بالانضمام إلى شركة رائدة مثل تكمو؟"
        ]
    else:
        bank = [
            "Based on your resume, what is the key project or achievement that best demonstrates your capabilities?",
            "Briefly highlight your core professional strengths and how you can contribute to team success at Tecmo.",
            "Share a real-world situation where you faced an unexpected challenge and how you resolved it effectively.",
            "How do you prioritize tasks and maintain high accuracy in a fast-paced, dynamic environment?",
            "In the engineering contracting and workforce management sector, how do you upgrade your skills and stay current?",
            "Tell us about a time you had to make a quick decision with incomplete information, and what the outcome was.",
            "How do you handle constructive feedback or sudden shifts in project requirements?",
            "Describe a new skill or tool you recently mastered and how it improved your workflow.",
            "How do you balance innovative thinking with strict adherence to operational standards and quality?",
            "What type of work environment enables you to perform at your highest potential?",
            "When you disagree with a teammate on an approach, how do you navigate the discussion toward the best solution?",
            "What drives your professional ambition and excites you about joining a leading company like Tecmo?"
        ]
    return random.sample(bank, min(count, len(bank)))

async def generate_voice(text, arabic_mode):
    voice = "ar-SA-ZariyahNeural" if arabic_mode else "en-GB-SoniaNeural"
    communicate = edge_tts.Communicate(str(text), voice)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    await communicate.save(temp_file.name)
    return temp_file.name

for key, default in [("questions", []), ("current_q", 0), ("audio_files", {}), ("evaluations", []), ("candidate_note", ""), ("note_submitted", False), ("record_saved", False), ("cv_analysis", None), ("user_email", "")]:
    if key not in st.session_state:
        st.session_state[key] = default

if not st.session_state.questions:
    st.markdown(f"<div class='prompt-card'><h4 style='color:#091e42; margin-top:0;'>{'جاهز لبدء التقييم التفاعلي؟' if is_ar else 'Ready to Begin Your Interactive Assessment?'}</h4><p style='color:#42526e; margin-bottom:0;'>{'حدد المسمى الوظيفي والمنطقة وأرفق سيرتك الذاتية (PDF) في القائمة الجانبية ليقوم النظام بتحليلها وتصنيف تخصصك تلقائياً، ثم أدخل بريدك الإلكتروني أدناه للبدء.' if is_ar else 'Select your job title, region, and upload your Resume (PDF) in the sidebar for automated specialty classification, then enter your email below.'}</p></div>", unsafe_allow_html=True)
    
    email_input = st.text_input("البريد الإلكتروني للمرشح (إجباري - يُسمح بالتقديم مرة واحدة) *:" if is_ar else "Candidate Email Address (Mandatory - One attempt only) *:", placeholder="name@example.com")
    
    if uploaded_cv is None:
        st.warning("⚠️ حقل السيرة الذاتية (PDF) إجباري في القائمة الجانبية لتفعيل زر بدء التقييم." if is_ar else "⚠️ Uploading your Resume / CV (PDF) in the sidebar is mandatory to start the assessment.")
    else:
        if st.session_state.cv_analysis is None:
            st.session_state.cv_analysis = analyze_cv_by_specialty(uploaded_cv, final_job_role, is_ar)
        
        cv_info = st.session_state.cv_analysis
        st.success(f"✅ {'تم تحليل وتصنيف السيرة الذاتية:' if is_ar else 'Resume Analyzed & Classified:'} **{uploaded_cv.name}**")
        st.info(f"{cv_info['summary']}\n\n📌 **{'المسمى المستهدف:' if is_ar else 'Target Role:'}** {final_job_role} | 📍 **{'المنطقة:' if is_ar else 'Region:'}** {selected_region}")
        
        if st.button("ابدأ التقييم الآن ➔" if is_ar else "Begin Assessment Now ➔"):
            clean_email = email_input.strip()
            if "@" not in clean_email or "." not in clean_email.split("@")[-1] or len(clean_email) < 5:
                st.error("⚠️ يرجى إدخال بريد إلكتروني صحيح في الحقل أعلاه قبل البدء." if is_ar else "⚠️ Please enter a valid email address above before starting.")
            elif check_email_already_submitted(clean_email):
                st.error("⚠️ عذراً، لقد قمت بإجراء هذا التقييم مسبقاً بهذا البريد الإلكتروني." if is_ar else "⚠️ You have already completed this assessment with this email.")
            else:
                st.session_state.user_email = clean_email
                with st.spinner("جاري تجهيز محاور التقييم العشوائية..." if is_ar else "Preparing randomized assessment topics..."):
                    q_list = get_tecmo_questions(experience_level, num_questions, is_ar)
                    st.session_state.questions = q_list
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
