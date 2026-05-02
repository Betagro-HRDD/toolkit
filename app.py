import streamlit as st
import pandas as pd
from google.oauth2 import service_account
import gspread
from datetime import datetime

# ==========================================
# --- 1. SETTING UP THE PAGE (ต้องอยู่บนสุดเสมอ) ---
# ==========================================
st.set_page_config(page_title="Betagro Smart HRDD Toolkit", page_icon="🟢", layout="centered")

# --- 2. CONNECT ENGINE ---
def connect_to_sheet():
    try:
        creds_info = st.secrets["gcp_service_account"]
        private_key = creds_info["private_key"].replace("\\n", "\n")
        creds_dict = {**creds_info, "private_key": private_key}
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        credentials = service_account.Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(credentials)
        SHEET_ID = "1YUkrlk_RlvskDluFoAdTQ7KRYRxYhi8ZqNdw13X7JxY"
        return client.open_by_key(SHEET_ID).get_worksheet(0)
    except Exception as e:
        st.error(f"❌ การเชื่อมต่อล้มเหลว: {e}")
        return None

# --- 3. ULTRA-PREMIUM STYLING & HIDE STREAMLIT MENU ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&family=Sarabun:wght@300;400;600;700;800&display=swap');
    
    html, body, [class*="st-"] { font-family: 'Sarabun', sans-serif; }
    .stApp { background-color: #F4F7F6; }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stHeader"], [data-testid="collapsedControl"], [data-testid="stSidebar"] { display: none !important; }
    a.header-anchor { display: none !important; }
    
    [data-testid="stDecoration"], [data-testid="stToolbar"] { display: none !important; }
    div[class^="viewerBadge_"], .viewerBadge_container__1QSob, .styles_viewerBadge__1yB5_ { display: none !important; }

    .premium-banner {
        background: #FFFFFF; border-radius: 24px; padding: 30px 40px;
        box-shadow: 0px 20px 40px rgba(0, 91, 49, 0.05);
        border: 1px solid rgba(0, 91, 49, 0.08); border-left: 12px solid #005B31; 
        display: flex; align-items: center; gap: 30px; margin-bottom: 40px;
        position: relative; overflow: hidden;
    }
    .premium-banner::after { content: ''; position: absolute; top: 0; right: 0; width: 150px; height: 8px; background: #F9A818; }
    
    .logo-wrapper {
        display: flex; flex-direction: column; align-items: center;
        border-right: 2px solid #EAEAEA; padding-right: 30px;
    }
    .typography-logo {
        font-family: 'Poppins', sans-serif; font-size: 26px; font-weight: 800;
        color: #D3A129; letter-spacing: 2px; line-height: 1; margin-top: 10px;
    }

    .banner-text { display: flex; flex-direction: column; justify-content: center; }
    .hero-title-eng { color: #005B31 !important; font-family: 'Poppins', sans-serif !important; font-size: 21px !important; font-weight: 800 !important; margin: 0 !important; line-height: 1.1 !important; letter-spacing: 1px !important; white-space: nowrap !important; }
    .hero-title-thai { color: #265F36 !important; font-family: 'Sarabun', sans-serif !important; font-size: 16px !important; font-weight: 600 !important; margin: 5px 0 0 0 !important; line-height: 1.3 !important; white-space: nowrap !important; }
    .hero-subtitle { color: #D3A129 !important; font-family: 'Poppins', sans-serif !important; font-size: 11px !important; font-weight: 700 !important; letter-spacing: 3px !important; text-transform: uppercase !important; margin-top: 14px !important; margin-bottom: 0 !important; padding-top: 10px !important; border-top: 1px solid rgba(211, 161, 41, 0.3) !important; width: fit-content; }
    
    @media (max-width: 768px) {
        .premium-banner { flex-direction: column; text-align: center; padding: 35px 20px; gap: 20px; border-left: none; border-top: 12px solid #005B31; }
        .logo-wrapper { border-right: none; padding-right: 0; border-bottom: 2px solid #EAEAEA; padding-bottom: 25px; }
        .hero-title-eng { font-size: 18px !important; white-space: normal !important; letter-spacing: 0.5px !important;}
        .hero-title-thai { font-size: 15px !important; white-space: normal !important;}
        .hero-subtitle { font-size: 10px !important; letter-spacing: 1.5px !important; margin: 15px auto 0 auto !important;}
    }

    .control-panel {
        background: #FFFFFF; padding: 30px; border-radius: 16px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.03); border: 1px solid #EAEAEA;
        margin-bottom: 30px; border-top: 5px solid #F9A818;
    }

    [data-testid="stForm"], .standalone-form { background: #FFFFFF; border-radius: 20px; border: none; box-shadow: 0 10px 30px rgba(0,0,0,0.04); padding: 30px; }
    
    [data-testid="stFormSubmitButton"] > button, .stButton > button {
        background: #005B31 !important; color: #FFFFFF !important; border-radius: 10px !important;
        font-weight: 700 !important; padding: 12px 24px !important; border: none !important;
        box-shadow: 0 8px 20px rgba(0, 91, 49, 0.2) !important; transition: all 0.3s ease; width: 100%; font-size: 16px !important;
    }
    [data-testid="stFormSubmitButton"] > button:hover, .stButton > button:hover {
        background: #004222 !important; transform: translateY(-2px) !important; box-shadow: 0 12px 25px rgba(0, 91, 49, 0.3) !important;
    }

    .salient-badge { background-color: #FEF2F2; color: #DC2626; padding: 15px; border-radius: 12px; border: 1px solid #FECACA; font-weight: 700; text-align: center; display: block; margin-top: 15px;}
    .strategic-box { background: #F8FAFB; border-left: 6px solid #D3A129; padding: 20px; border-radius: 10px; margin-top: 20px; border-top: 1px solid #EAEAEA; border-right: 1px solid #EAEAEA; border-bottom: 1px solid #EAEAEA; }
    
    /* 🌟 สไตล์กล่องข้อความจาก Gemini AI */
    .gemini-draft-box { background: linear-gradient(135deg, #F0F4FF 0%, #FFFFFF 100%); border-left: 6px solid #4285F4; padding: 20px; border-radius: 10px; margin-top: 20px; border: 1px solid #D2E3FC; box-shadow: 0 4px 15px rgba(66, 133, 244, 0.05);}
    .gemini-title { color: #1967D2; font-family: 'Poppins', sans-serif; font-weight: 700; margin-top: 0; font-size: 16px; display: flex; align-items: center; gap: 8px;}
    .gemini-icon { font-size: 20px; }

    .citation-box { background-color: #FFFFFF; padding: 25px; border-left: 6px solid #DC2626; border-radius: 12px; margin: 20px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #F3F4F6;}
    
    .heat-table { width: 100%; border-collapse: separate; border-spacing: 4px; margin-top: 15px;}
    .heat-cell { height: 50px; text-align: center; font-weight: bold; color: white; border-radius: 8px; font-size: 14px;}
    
    .control-panel label { font-size: 14px !important; color: #444 !important; font-weight: 600 !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# --- 3.1 SECURITY ACCESS GATE ---
# ==========================================
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
                <div style="text-align: center; margin-top: 60px; margin-bottom: 30px;">
                    <svg width="90" height="90" viewBox="0 0 100 100" style="margin-bottom: 15px; filter: drop-shadow(0 6px 15px rgba(0,91,49,0.15));">
                        <circle cx="36" cy="38" r="23" fill="#005B31"/>
                        <circle cx="64" cy="38" r="23" fill="#005B31"/>
                        <circle cx="50" cy="62" r="23" fill="#005B31"/>
                        <path d="M 50,42 Q 54,54 62,60 Q 50,56 38,60 Q 46,54 50,42 Z" fill="#FFFFFF" stroke="#FFFFFF" stroke-width="2" stroke-linejoin="round"/>
                    </svg>
                    <h2 style="color: #005B31; font-family: 'Poppins', sans-serif; font-weight: 800; margin: 0; font-size: 36px; letter-spacing: 2px;">BETAGRO</h2>
                    <p style="color: #D3A129; font-weight: 700; letter-spacing: 3px; text-transform: uppercase; font-size: 12px; margin-top: 5px;">Secure Access Only</p>
                </div>
            """, unsafe_allow_html=True)
            
            with st.form("login_form"):
                st.markdown("<h4 style='color: #005B31; text-align: center; margin-bottom: 20px; font-weight: 600;'>🔒 ระบบประเมิน HRDD อัจฉริยะ</h4>", unsafe_allow_html=True)
                pwd = st.text_input("Security Access Key", type="password", placeholder="Enter Password...", label_visibility="collapsed")
                submitted = st.form_submit_button("LOGIN")
                
                if submitted:
                    correct_password = st.secrets.get("APP_PASSWORD", "Betagro@2026")
                    if pwd == correct_password:
                        st.session_state["password_correct"] = True
                        st.rerun()
                    else:
                        st.error("❌ Access Denied. รหัสผ่านไม่ถูกต้อง")
        return False
    return True

if not check_password():
    st.stop()


# ==========================================
# --- 4. TOP-DOWN UI (เนื้อหาหลักหลัง Login) ---
# ==========================================
st.markdown("""
    <div class="premium-banner">
        <div class="logo-wrapper">
            <svg width="65" height="65" viewBox="0 0 100 100" style="margin-bottom: 5px; filter: drop-shadow(0 6px 15px rgba(0,91,49,0.15));">
                <circle cx="36" cy="38" r="23" fill="#005B31"/>
                <circle cx="64" cy="38" r="23" fill="#005B31"/>
                <circle cx="50" cy="62" r="23" fill="#005B31"/>
                <path d="M 50,42 Q 54,54 62,60 Q 50,56 38,60 Q 46,54 50,42 Z" fill="#FFFFFF" stroke="#FFFFFF" stroke-width="2" stroke-linejoin="round"/>
            </svg>
            <div class="typography-logo">BETAGRO</div>
        </div>
        <div class="banner-text">
            <div class="hero-title-eng">BETAGRO STRATEGIC HRDD TOOLKIT</div>
            <div class="hero-title-thai">ระบบยุทธศาสตร์บริหารจัดการสิทธิมนุษยชนอัจฉริยะ</div>
            <div class="hero-subtitle">Smart Assessment Systems & Analytics</div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown('<div class="control-panel">', unsafe_allow_html=True)

st.markdown("<h4 style='color: #005B31; margin-bottom: 15px; font-weight: 700;'><i class='fa-solid fa-folder-open'></i> 1. ข้อมูลโครงการ (Project Info)</h4>", unsafe_allow_html=True)
col_p1, col_p2, col_p3 = st.columns(3)
with col_p1:
    audit_cycle = st.selectbox("รอบการประเมิน (Audit Cycle) *", ["Annual 2026", "Q1/2026", "Q2/2026", "Q3/2026", "Q4/2026", "Special Audit"])
with col_p2:
    auditor_name = st.text_input("ชื่อผู้บันทึกข้อมูล (Auditor) *", placeholder="เช่น สมชาย ใจดี")
with col_p3:
    location = st.text_input("พื้นที่สำรวจ (Location/Site) *", placeholder="เช่น โรงงานลพบุรี")

st.markdown("<hr style='border: 1px dashed #EAEAEA; margin: 20px 0;'>", unsafe_allow_html=True)

st.markdown("<h4 style='color: #005B31; margin-bottom: 15px; font-weight: 700;'><i class='fa-solid fa-users'></i> 2. ข้อมูลผู้ให้ข้อมูล (Respondent Info)</h4>", unsafe_allow_html=True)
col_r1, col_r2, col_r3, col_r4 = st.columns(4)
with col_r1:
    resp_id = st.text_input("รหัสอ้างอิง (ID) *", placeholder="เช่น EMP-001")
with col_r2:
    resp_group = st.selectbox("กลุ่มเป้าหมาย *", ["ฝ่ายบริหาร", "แรงงานไทย", "แรงงานข้ามชาติ", "ชุมชน", "คู่ค้า"])
with col_r3:
    resp_dept = st.text_input("แผนก/ส่วนงาน", placeholder="เช่น ฝ่ายตัดแต่ง")
with col_r4:
    resp_gender = st.selectbox("เพศ (Gender)", ["ไม่ระบุ", "ชาย", "หญิง", "อื่นๆ"])

st.markdown("<hr style='border: 1px solid #eee; margin: 20px 0;'>", unsafe_allow_html=True)
st.markdown("<h4 style='color: #005B31; margin-bottom: 15px; font-weight: 700;'><i class='fa-solid fa-screwdriver-wrench'></i> 3. เลือกเครื่องมือประเมิน</h4>", unsafe_allow_html=True)
choice = st.selectbox("เลือกแบบฟอร์มด้านล่างนี้:", [
    "Tool 1: ประเมินสถานะองค์กร",
    "Tool 2: แบบสอบถามหน้างาน (อัปเดตใหม่)",
    "Tool 3: สัมภาษณ์เชิงลึก (Evidence)",
    "Tool 4: บันทึกการสังเกตการณ์ (อัปเดตใหม่)",
    "Tool 5: ประเมินนัยสำคัญ (Salient Rule & Gemini AI Plan)",
    "Tool 6: ระบบวิเคราะห์ AI Triangulation"
], label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

if not resp_id or not auditor_name or not location:
    st.info("📌 กรุณาระบุ 'ข้อมูลโครงการ' และ 'รหัสอ้างอิง (ID)' ให้ครบถ้วน เพื่อปลดล็อกแบบฟอร์มการประเมิน")
    st.stop()

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ==========================================
# --- 5. TOOLS LOGIC ---
# ==========================================

if choice == "Tool 1: ประเมินสถานะองค์กร":
    with st.form("form_t1"):
        st.markdown("<h3 style='color:#005B31;'>Tool 1: ประเมินสถานะองค์กร (Policy Gap)</h3><hr>", unsafe_allow_html=True)
        st.markdown("**หมวด A: การกำกับดูแลและนโยบาย (Governance & Policy)**")
        q1_1 = st.radio("1.1 องค์กรมี 'นโยบายสิทธิมนุษยชน' ที่เป็นลายลักษณ์อักษรหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        q1_2 = st.radio("1.2 นโยบายครอบคลุมประเด็นสำคัญ (แรงงานข้ามชาติ, ชุมชน, สิ่งแวดล้อม) หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        q1_3 = st.radio("1.3 มีการสื่อสารนโยบายในภาษาที่พนักงานและคู่ค้าเข้าใจหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        st.markdown("<hr style='border: 1px dashed #ccc;'>", unsafe_allow_html=True)
        
        st.markdown("**หมวด B: กระบวนการตรวจสอบอย่างรอบด้าน (Due Diligence)**")
        q2_1 = st.radio("2.1 มีการประเมินความเสี่ยงด้านสิทธิมนุษยชน (HRA) ประจำปีหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        q2_2 = st.radio("2.2 มีระบบการตรวจสอบย้อนกลับ (Traceability) ในห่วงโซ่อุปทานหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        st.markdown("<hr style='border: 1px dashed #ccc;'>", unsafe_allow_html=True)
        
        st.markdown("**หมวด C: กลไกการร้องเรียนและการเยียวยา (Grievance & Remediation)**")
        q3_1 = st.radio("3.1 มีช่องทางรับเรื่องร้องเรียนที่ปลอดภัย เป็นความลับ และเข้าถึงได้ง่ายหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        q3_2 = st.radio("3.2 มีขั้นตอนการเยียวยา (Remediation) แก่ผู้ได้รับผลกระทบเมื่อเกิดการละเมิดหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("💾 บันทึกข้อมูล Tool 1"):
            sheet = connect_to_sheet()
            if sheet:
                detail = f"A({q1_1},{q1_2},{q1_3})|B({q2_1},{q2_2})|C({q3_1},{q3_2})"
                sheet.append_row([now, audit_cycle, auditor_name, location, "Tool 1", resp_id, resp_group, resp_dept, resp_gender, "Policy Gap Analysis", detail, "", "", "", ""])
                st.success("✅ บันทึกข้อมูล Tool 1 เรียบร้อย")

elif choice == "Tool 2: แบบสอบถามหน้างาน (อัปเดตใหม่)":
    with st.form("form_t2"):
        st.markdown("<h3 style='color:#005B31;'>Tool 2: แบบสอบถามการปฏิบัติหน้างาน (Worker Survey)</h3>", unsafe_allow_html=True)
        st.info("💡 ระดับคะแนน: 1 = ไม่จริงเลย/ไม่เคยปฏิบัติ | 5 = เป็นความจริงที่สุด/ปฏิบัติเสมอ")
        st.markdown("<hr>", unsafe_allow_html=True)

        st.markdown("**หมวดที่ 1: สภาพการจ้างและค่าจ้าง (Wages & Employment)**")
        s1_1 = st.select_slider("1.1 ท่านได้รับค่าจ้างตรงเวลาและครบถ้วนตามที่ตกลงไว้", options=[1,2,3,4,5], value=3)
        s1_2 = st.select_slider("1.2 ท่านเป็นผู้เก็บเอกสารประจำตัว (เช่น พาสปอร์ต, บัตร ปชช.) ไว้เอง", options=[1,2,3,4,5], value=3)
        s1_3 = st.select_slider("1.3 การทำล่วงเวลา (OT) ของท่าน เกิดจากความสมัครใจ ไม่ได้ถูกบังคับ", options=[1,2,3,4,5], value=3)
        st.markdown("<hr style='border: 1px dashed #ccc;'>", unsafe_allow_html=True)
        
        st.markdown("**หมวดที่ 2: ความปลอดภัยและสุขอนามัย (Occupational Health & Safety)**")
        s2_1 = st.select_slider("2.1 บริษัทจัดเตรียมอุปกรณ์ป้องกันอันตราย (PPE) ให้เพียงพอและฟรี", options=[1,2,3,4,5], value=3)
        s2_2 = st.select_slider("2.2 สภาพแวดล้อมการทำงานของท่าน (แสง, เสียง, อากาศ) ปลอดภัยต่อสุขภาพ", options=[1,2,3,4,5], value=3)
        s2_3 = st.select_slider("2.3 โรงอาหารและที่พักอาศัย (ถ้ามี) สะอาดและถูกสุขลักษณะ", options=[1,2,3,4,5], value=3)
        st.markdown("<hr style='border: 1px dashed #ccc;'>", unsafe_allow_html=True)

        st.markdown("**หมวดที่ 3: การปฏิบัติต่อพนักงานและการร้องเรียน (Fair Treatment & Grievance)**")
        s3_1 = st.select_slider("3.1 หัวหน้างานปฏิบัติต่อพนักงานทุกคนอย่างเท่าเทียม ไม่เลือกปฏิบัติ", options=[1,2,3,4,5], value=3)
        s3_2 = st.select_slider("3.2 หากมีปัญหาหรือถูกเอาเปรียบ ท่านทราบช่องทางและกล้าร้องเรียน", options=[1,2,3,4,5], value=3)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("🚀 บันทึกข้อมูล Tool 2"):
            sheet = connect_to_sheet()
            if sheet:
                detail = f"จ้างงาน({s1_1},{s1_2},{s1_3}) | OHS({s2_1},{s2_2},{s2_3}) | ปฏิบัติ({s3_1},{s3_2})"
                sheet.append_row([now, audit_cycle, auditor_name, location, "Tool 2", resp_id, resp_group, resp_dept, resp_gender, "Worker Survey", detail, "", "", "", ""])
                st.success("✅ ส่งข้อมูลแบบสอบถามสำเร็จ")

elif choice == "Tool 3: สัมภาษณ์เชิงลึก (Evidence)":
    with st.form("form_t3"):
        st.markdown("<h3 style='color:#005B31;'>Tool 3: สัมภาษณ์เชิงลึก (In-depth Interview)</h3><hr>", unsafe_allow_html=True)
        st.markdown("**🔍 หัวข้อการตรวจสอบ (เลือกข้อที่พบประเด็นความเสี่ยง)**")
        topics = st.multiselect("ประเด็นที่พูดคุย:", 
            ["การสรรหา/ค่านายหน้า (Recruitment Fees)", "ความเข้าใจในสัญญาจ้าง", "สภาพที่พักอาศัย/โรงอาหาร", "กลไกการร้องเรียน", "การเลือกปฏิบัติ"], label_visibility="collapsed")
             
        st.markdown("<br>**✍️ บันทึกคำให้การ (Testimony)**", unsafe_allow_html=True)
        testimony = st.text_area("สรุปคำพูดหรือหลักฐานที่พบ:", height=150)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("💾 บันทึกข้อมูล Tool 3"):
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([now, audit_cycle, auditor_name, location, "Tool 3", resp_id, resp_group, resp_dept, resp_gender, ", ".join(topics), testimony, "", "", "", ""])
                st.success("✅ บันทึกหลักฐานสำเร็จ")

elif choice == "Tool 4: บันทึกการสังเกตการณ์ (อัปเดตใหม่)":
    with st.form("form_t4"):
        st.markdown("<h3 style='color:#005B31;'>Tool 4: บันทึกการสังเกตการณ์หน้างาน (Site Observation)</h3>", unsafe_allow_html=True)
        st.info("📌 ประเมินสิ่งที่พบเห็นจริงหน้างาน และสามารถบันทึกข้อสังเกตเพิ่มเติมในแต่ละข้อได้ทันที")
        st.markdown("<hr>", unsafe_allow_html=True)
        
        o1 = st.radio("1. มีการติดประกาศนโยบายและช่องทางร้องเรียนในพื้นที่ที่พนักงานมองเห็นได้ชัดเจน", ["✔️ พบ (Pass)", "❌ ไม่พบ (Fail)", "➖ ไม่เกี่ยวข้อง (N/A)"], horizontal=True)
        note_o1 = st.text_input("บันทึกเพิ่มเติมข้อ 1:", key="n1", label_visibility="collapsed", placeholder="พิมพ์บันทึกเพิ่มเติมสำหรับข้อ 1 (ถ้ามี)...")
        st.markdown("<br>", unsafe_allow_html=True)

        o2 = st.radio("2. ทางหนีไฟ อุปกรณ์ดับเพลิง ไม่มีสิ่งกีดขวางและพร้อมใช้งาน", ["✔️ พบ (Pass)", "❌ ไม่พบ (Fail)", "➖ ไม่เกี่ยวข้อง (N/A)"], horizontal=True)
        note_o2 = st.text_input("บันทึกเพิ่มเติมข้อ 2:", key="n2", label_visibility="collapsed", placeholder="พิมพ์บันทึกเพิ่มเติมสำหรับข้อ 2 (ถ้ามี)...")
        st.markdown("<br>", unsafe_allow_html=True)

        o3 = st.radio("3. พนักงานในสายการผลิตสวมใส่อุปกรณ์ป้องกัน (PPE) ถูกต้อง", ["✔️ พบ (Pass)", "❌ ไม่พบ (Fail)", "➖ ไม่เกี่ยวข้อง (N/A)"], horizontal=True)
        note_o3 = st.text_input("บันทึกเพิ่มเติมข้อ 3:", key="n3", label_visibility="collapsed", placeholder="พิมพ์บันทึกเพิ่มเติมสำหรับข้อ 3 (ถ้ามี)...")
        st.markdown("<br>", unsafe_allow_html=True)

        o4 = st.radio("4. สภาพแวดล้อมพื้นที่ทำงานมีแสงสว่างและการระบายอากาศที่เหมาะสม", ["✔️ พบ (Pass)", "❌ ไม่พบ (Fail)", "➖ ไม่เกี่ยวข้อง (N/A)"], horizontal=True)
        note_o4 = st.text_input("บันทึกเพิ่มเติมข้อ 4:", key="n4", label_visibility="collapsed", placeholder="พิมพ์บันทึกเพิ่มเติมสำหรับข้อ 4 (ถ้ามี)...")
        st.markdown("<br>", unsafe_allow_html=True)

        o5 = st.radio("5. ตู้ยาสามัญประจำโรงงานมีเวชภัณฑ์ครบถ้วนและไม่หมดอายุ", ["✔️ พบ (Pass)", "❌ ไม่พบ (Fail)", "➖ ไม่เกี่ยวข้อง (N/A)"], horizontal=True)
        note_o5 = st.text_input("บันทึกเพิ่มเติมข้อ 5:", key="n5", label_visibility="collapsed", placeholder="พิมพ์บันทึกเพิ่มเติมสำหรับข้อ 5 (ถ้ามี)...")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("💾 บันทึกข้อมูล Tool 4"):
            sheet = connect_to_sheet()
            if sheet:
                # จัดรูปแบบข้อมูลให้กระชับ เช่น พบ (บันทึกเพิ่มเติม) หรือ พบ เฉยๆถ้าไม่มีบันทึก
                res_o1 = f"{o1.split(' ')[1]} ({note_o1})" if note_o1 else o1.split(" ")[1]
                res_o2 = f"{o2.split(' ')[1]} ({note_o2})" if note_o2 else o2.split(" ")[1]
                res_o3 = f"{o3.split(' ')[1]} ({note_o3})" if note_o3 else o3.split(" ")[1]
                res_o4 = f"{o4.split(' ')[1]} ({note_o4})" if note_o4 else o4.split(" ")[1]
                res_o5 = f"{o5.split(' ')[1]} ({note_o5})" if note_o5 else o5.split(" ")[1]
                
                detail = f"Policy: {res_o1} | Fire: {res_o2} | PPE: {res_o3} | Env: {res_o4} | Med: {res_o5}"
                sheet.append_row([now, audit_cycle, auditor_name, location, "Tool 4", resp_id, resp_group, resp_dept, resp_gender, "Site Observation", detail, "", "", "", ""])
                st.success("✅ บันทึกการสังเกตการณ์สำเร็จ")

# ==========================================
# TOOL 5: ประเมินนัยสำคัญ & GEMINI AI PLAN
# ==========================================
elif choice == "Tool 5: ประเมินนัยสำคัญ (Salient Rule & Gemini AI Plan)":
    st.markdown("<div class='standalone-form'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#005B31; margin-top:0;'>Tool 5: HR Risk Matrix & Gemini AI Plan</h3>", unsafe_allow_html=True)
    
    # 💡 อธิบายเกณฑ์การประเมิน
    st.info("💡 **เกณฑ์การประเมิน:** ไม่จำเป็นต้องประเมิน Tool นี้กับทุก ID แต่ให้ใช้ประเมิน **'ประเด็นปัญหา (Issue)'** เมื่อพบการร้องเรียนจาก Tool 1-4 ที่มีแนวโน้มรุนแรง หรือพบปัญหาเดิมซ้ำๆ ในหลายพื้นที่ เพื่อหามาตรการจัดการเชิงระบบ")
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # 🌟 จำลองการทำงานของ AI (Pre-fill Data)
    if st.button("✨ ให้ Gemini AI ประมวลผลและระบุความเสี่ยงอัตโนมัติ"):
        st.session_state.ai_analyzed = True
        st.session_state.t5_issue = "[สิทธิแรงงาน] การจ่ายเงินล่าช้า / ไม่จ่ายโอที"
        st.session_state.t5_scale = 4
        st.session_state.t5_scope = 3
        st.session_state.t5_remedy = 3
        st.session_state.t5_likelihood = 4
        st.rerun()

    if st.session_state.get("ai_analyzed", False):
        st.success("🤖 Gemini AI ได้ดึงข้อมูลจาก Tool 1-4 มาวิเคราะห์และระบุความเสี่ยงให้แล้ว (คุณสามารถปรับแก้คะแนนด้านล่างได้ก่อนอนุมัติ)")

    # ตั้งค่าตัวเลือกเริ่มต้นจาก AI (ถ้ามีการกดปุ่ม) หรือค่าเริ่มต้นปกติ
    def_issue = st.session_state.get("t5_issue", "[แรงงานบังคับ] ภาระหนี้ผูกพัน / การเรียกเก็บค่าธรรมเนียมสรรหา")
    def_scale = st.session_state.get("t5_scale", 1)
    def_scope = st.session_state.get("t5_scope", 1)
    def_remedy = st.session_state.get("t5_remedy", 1)
    def_likelihood = st.session_state.get("t5_likelihood", 1)

    issue_options = [
        "[แรงงานบังคับ] ภาระหนี้ผูกพัน / การเรียกเก็บค่าธรรมเนียมสรรหา",
        "[แรงงานบังคับ] การยึดเอกสารประจำตัว (พาสปอร์ต/บัตร)",
        "[สิทธิแรงงาน] การจ่ายเงินล่าช้า / ไม่จ่ายโอที",
        "[อาชีวอนามัย] สภาพแวดล้อมการทำงานอันตราย / ขาด PPE",
        "[ชุมชน] ผลกระทบต่อสิ่งแวดล้อมและชุมชนโดยรอบ",
        "อื่นๆ"
    ]
    issue_idx = issue_options.index(def_issue) if def_issue in issue_options else 0

    st.markdown("**📌 1. ระบุประเด็นความเสี่ยง (อ้างอิงมาตรฐาน ILO)**")
    issue = st.selectbox("หมวดหมู่ความเสี่ยง:", issue_options, index=issue_idx, label_visibility="collapsed")
    
    st.markdown("<hr style='border: 1px dashed #ccc;'>", unsafe_allow_html=True)
    st.markdown("**📌 2. คำนวณ Severity (ใช้ค่าสูงสุด)**")
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1: scale = st.slider("Scale (ความรุนแรง)", 1, 5, def_scale)
    with col_s2: scope = st.slider("Scope (จำนวนผู้ได้รับผลกระทบ)", 1, 5, def_scope)
    with col_s3: remedy = st.slider("Remediability (การเยียวยา)", 1, 5, def_remedy)
    
    sev_max = max(scale, scope, remedy)
    st.markdown("<hr style='border: 1px dashed #ccc;'>", unsafe_allow_html=True)
    likelihood = st.slider("📌 3. Likelihood (โอกาสที่จะเกิด)", 1, 5, def_likelihood)
    score = sev_max * likelihood

    is_salient = "YES" if sev_max >= 4 else "NO"
    
    st.markdown(f"<h4 style='color: #005B31; text-align:center; padding: 15px; background: #F4F7F6; border-radius: 8px;'>Severity Max: {sev_max} | โอกาสเกิด: {likelihood} | คะแนนรวม: {score}</h4>", unsafe_allow_html=True)
    
    # 🌟 สร้าง Heat Map (สีแดง เหลือง เขียว พร้อมตำแหน่ง ★)
    rows = ""
    for l in range(5, 0, -1):
        rows += "<tr>"
        for s in range(1, 6):
            val = s * l
            # กำหนดเกณฑ์สี: แดง (>=16 หรือ Severity เป็น 5), เหลือง (>=8), เขียว (ที่เหลือ)
            color = "#EF4444" if val >= 16 or s == 5 else ("#F9A818" if val >= 8 else "#005B31")
            mark = "★" if s == sev_max and l == likelihood else ""
            rows += f"<td class='heat-cell' style='background-color:{color}; box-shadow: inset 0 0 10px rgba(0,0,0,0.1);'>{mark}</td>"
        rows += "</tr>"
    st.markdown(f"<table class='heat-table'>{rows}</table><p style='text-align:center; color: #666; margin-top: 10px;'><small>แนวนอน: Severity (ความรุนแรง) | แนวตั้ง: Likelihood (โอกาสเกิด)</small></p>", unsafe_allow_html=True)
    
    # 🌟 ฟังก์ชันจำลอง Gemini AI ร่างข้อความ
    ai_drafts = {
        "[แรงงานบังคับ] ภาระหนี้ผูกพัน / การเรียกเก็บค่าธรรมเนียมสรรหา": "Preventive: ทบทวนนโยบาย Employer Pays Principle (EPP) ร่วมกับเอเจนซี่\nMitigation: ระงับการใช้บริการเอเจนซี่ที่กระทำผิดชั่วคราว\nRemediation: คืนเงินค่าธรรมเนียมสรรหาให้แรงงานเต็มจำนวนภายใน 30 วัน",
        "[แรงงานบังคับ] การยึดเอกสารประจำตัว (พาสปอร์ต/บัตร)": "Preventive: จัดหาตู้ล็อกเกอร์นิรภัยให้พนักงานเก็บเอกสารของตนเอง\nMitigation: สื่อสารสิทธิการครอบครองเอกสารให้พนักงานทราบผ่านล่ามประจำชาติ\nRemediation: คืนเอกสารประจำตัวให้พนักงานทุกคนทันที (ภายใน 24 ชม.)",
        "[สิทธิแรงงาน] การจ่ายเงินล่าช้า / ไม่จ่ายโอที": "Preventive: ตรวจสอบระบบบันทึกเวลาทำงาน (Time Attendance) แบบสุ่มทุกเดือน\nMitigation: อบรมหัวหน้างานเรื่องกฎหมายแรงงานและระเบียบการทำ OT\nRemediation: จ่ายค่าจ้างและ OT ค้างจ่ายย้อนหลังพร้อมดอกเบี้ยตามกฎหมายในงวดถัดไป",
        "[อาชีวอนามัย] สภาพแวดล้อมการทำงานอันตราย / ขาด PPE": "Preventive: กำหนดรอบการตรวจสอบ PPE และความปลอดภัยของเครื่องจักรประจำสัปดาห์\nMitigation: หยุดการทำงานในจุดที่เสี่ยงอันตรายทันทีจนกว่าจะปรับปรุงเสร็จ\nRemediation: จัดหา PPE ใหม่ให้พนักงานทันที และรับผิดชอบค่ารักษาพยาบาลหากมีผู้บาดเจ็บ",
        "[ชุมชน] ผลกระทบต่อสิ่งแวดล้อมและชุมชนโดยรอบ": "Preventive: ติดตั้งและซ่อมบำรุงระบบบำบัดมลพิษให้ได้มาตรฐานสากล\nMitigation: จัดตั้งทีมมวลชนสัมพันธ์ (CSR) ลงพื้นที่รับฟังปัญหาและผลกระทบทันที\nRemediation: ชดเชยความเสียหายให้ชุมชนที่ได้รับผลกระทบ และจัดทำแผนฟื้นฟูสิ่งแวดล้อม",
        "อื่นๆ": "Preventive: [ระบุมาตรการป้องกันไม่ให้เกิดซ้ำ]\nMitigation: [ระบุมาตรการบรรเทาผลกระทบระยะสั้น]\nRemediation: [ระบุมาตรการเยียวยาผู้ได้รับผลกระทบ]"
    }
    
    plan_text = ""
    if is_salient == "YES":
        st.markdown('<div class="salient-badge">🚨 SALIENT ISSUE: ความเสี่ยงระดับสูง (เข้าสู่กระบวนการอนุมัติแผน)</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="gemini-draft-box">
            <h4 class="gemini-title"><span class="gemini-icon">✨</span> Gemini AI: Strategic Mitigation & Remediation Plan</h4>
            <p style="font-size: 14px; color: #666; margin-bottom: 5px;">ระบบ AI ได้ประมวลผลและร่างแผนปฏิบัติการเบื้องต้นจากฐานข้อมูลแนวปฏิบัติสากล (UNGPs)</p>
            <p style="font-size: 14px; color: #1967D2; font-weight: 600; margin-bottom: 15px;">👉 ผู้ตรวจประเมินสามารถแก้ไขข้อความด้านล่าง และกดบันทึกเพื่อ "อนุมัติ (Approve)"</p>
        </div>
        """, unsafe_allow_html=True)
        
        default_ai_text = ai_drafts.get(issue, ai_drafts["อื่นๆ"])
        plan_text = st.text_area("กล่องข้อความปรับแก้ (Edit & Approve):", value=default_ai_text, height=140, label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 ยืนยันและบันทึกแผนกลยุทธ์ (Approve & Submit)"):
        sheet = connect_to_sheet()
        if sheet:
            detail = f"Scale:{scale}, Scope:{scope}, Remedy:{remedy} | Action Plan: {plan_text}"
            sheet.append_row([now, audit_cycle, auditor_name, location, "Tool 5", resp_id, resp_group, resp_dept, resp_gender, issue, detail, sev_max, likelihood, score, is_salient])
            
            # เคลียร์สถานะ AI ออกเพื่อพร้อมใช้งานในเคสต่อไป
            st.session_state.ai_analyzed = False
            
            st.success("✅ อนุมัติและบันทึกแผนกลยุทธ์เข้าสู่ระบบเรียบร้อยแล้ว")
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# TOOL 6: AI Triangulation & AI STRATEGY
# ==========================================
elif choice == "Tool 6: ระบบวิเคราะห์ AI Triangulation":
    st.markdown("<div class='standalone-form'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#005B31; margin-top:0;'>Tool 6: Gemini AI Triangulation & Proposal</h3><hr>", unsafe_allow_html=True)
    
    st.info("💡 ระบบ Gemini AI ทำการเปรียบเทียบข้อมูล (Triangulation) และเสนอแนะแผนกลยุทธ์ (Strategic Recommendations) อัตโนมัติ")
    
    st.markdown("""
    <div class="citation-box">
        <h4 style="color: #DC2626; margin-top: 0;">🚩 พบความขัดแย้งเชิงนโยบาย (Policy vs Practice)</h4>
        <b>ประเด็น:</b> สัญญาจ้างไม่เป็นภาษาที่พนักงานเข้าใจ<br><br>
        <div style="background: #F9FAFB; padding: 15px; border-radius: 8px; border: 1px solid #E5E7EB;">
            <span style="color: #6B7280; font-size: 14px;">🗣️ <b>อ้างอิงหลักฐาน (ID: EMP-045):</b></span><br>
            <span style="color: #111827; font-style: italic;">"ผมเซ็นสัญญาไปโดยไม่ได้มีล่ามแปลให้ฟัง..."</span>
        </div>
        <p style="color: #005B31; font-size: 14px; font-weight: 600; margin-top: 15px;">
            ❌ ขัดแย้งกับข้อมูลบริหาร (Tool 1 ข้อ 1.3): ระบุว่าสื่อสารเข้าใจแล้ว
        </p>
        
        <div class="gemini-draft-box" style="margin-top: 20px;">
            <h5 class="gemini-title"><span class="gemini-icon">✨</span> Gemini AI Strategic Recommendation:</h5>
            <ol style="margin-bottom: 0; font-size: 14px; color: #444; padding-left: 20px;">
                <li><b>Preventive:</b> จัดทำสัญญาจ้างแบบ 2 ภาษา (Bilingual) และบังคับใช้กับ Supplier ทุกราย</li>
                <li><b>Mitigation:</b> จัดหาล่ามอิสระ (Third-party Translator) ในวันปฐมนิเทศพนักงานใหม่</li>
                <li><b>Timeline:</b> ทบทวนกระบวนการและจัดทำสัญญาฉบับแก้ไขภายใน 30 วัน (Short-term action)</li>
            </ol>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 บันทึกสรุปผล Gemini AI Analysis ลงระบบ"):
        sheet = connect_to_sheet()
        if sheet:
            sheet.append_row([now, audit_cycle, auditor_name, location, "Tool 6", resp_id, resp_group, resp_dept, resp_gender, "AI Triangulation", "พบข้อขัดแย้งสัญญาจ้าง พร้อมจัดทำแผนแก้ไข 30 วัน", "", "", "", ""])
            st.success("✅ บันทึกข้อมูลการวิเคราะห์เชิงลึกและแผนกลยุทธ์เสร็จสิ้น")
    st.markdown("</div>", unsafe_allow_html=True)
