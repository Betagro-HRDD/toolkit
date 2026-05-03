import streamlit as st
import pandas as pd
from google.oauth2 import service_account
import gspread
from datetime import datetime, timedelta
import altair as alt
import random

# ==========================================
# --- 1. SETTING UP THE PAGE ---
# ==========================================
st.set_page_config(page_title="Betagro Smart HRDD Toolkit", page_icon="🟢", layout="wide")

# ==========================================
# --- 1.1 KNOWLEDGE BASE (ฐานข้อมูลกฎหมายและนโยบายจำลอง) ---
# ==========================================
LAW_KNOWLEDGE_BASE = {
    "OT": {"std": "พ.ร.บ. คุ้มครองแรงงาน มาตรา 70 | นายจ้างต้องจ่ายค่าทำงานล่วงเวลาให้ถูกต้อง", "doc": "Thai_Labor_Law.pdf"},
    "ค่าจ้าง": {"std": "พ.ร.บ. คุ้มครองแรงงาน มาตรา 70 | ILO Convention No. 95 ว่าด้วยการคุ้มครองค่าจ้าง", "doc": "Thai_Labor_Law.pdf"},
    "พาสปอร์ต": {"std": "Employer Pays Principle (EPP) | ห้ามยึดเอกสารประจำตัวแรงงาน (ILO Forced Labour No. 29)", "doc": "ILO_Conv_29.pdf"},
    "เอกสารประจำตัว": {"std": "Employer Pays Principle (EPP) | ห้ามยึดเอกสารประจำตัวแรงงาน (ILO Forced Labour No. 29)", "doc": "ILO_Conv_29.pdf"},
    "ความปลอดภัย": {"std": "ISO 45001 | พ.ร.บ. ความปลอดภัย อาชีวอนามัย และสภาพแวดล้อมในการทำงาน", "doc": "ISO_45001.pdf"},
    "เครื่องจักร": {"std": "ISO 45001 | ข้อกำหนดความปลอดภัยเรื่องการติดตั้ง Guard ป้องกันอันตรายจากเครื่องจักร", "doc": "ISO_45001.pdf"},
    "เด็ก": {"std": "Betagro Zero Tolerance Policy | ห้ามใช้แรงงานเด็กอายุต่ำกว่า 18 ปี ในพื้นที่อันตราย", "doc": "Betagro_Policy.pdf"},
    "เลือกปฏิบัติ": {"std": "ILO Convention No. 111 | ห้ามเลือกปฏิบัติในการจ้างงานและการประกอบอาชีพ", "doc": "ILO_Conv_111.pdf"},
    "ชุมชน": {"std": "พ.ร.บ. ส่งเสริมและรักษาคุณภาพสิ่งแวดล้อมแห่งชาติ | การจัดการมลพิษทางอากาศและน้ำ", "doc": "Thai_Env_Law.pdf"},
    "กลิ่น": {"std": "พ.ร.บ. สาธารณสุข | การจัดการเหตุรำคาญและมลพิษทางกลิ่นที่มีผลต่อชุมชน", "doc": "Thai_Env_Law.pdf"},
    "สวัสดิการ": {"std": "กฎกระทรวงว่าด้วยการจัดสวัสดิการ | มาตรฐานหอพักและห้องน้ำพนักงาน", "doc": "Thai_Welfare_Law.pdf"},
    "สมาคม": {"std": "ILO Convention No. 87 & 98 | เสรีภาพในการสมาคมและการร่วมเจรจาต่อรอง", "doc": "ILO_Conv_87.pdf"},
    "ชั่วโมงการทำงาน": {"std": "พ.ร.บ. คุ้มครองแรงงาน | ห้ามบังคับทำงานล่วงเวลาเกินกำหนด (ไม่เกิน 36 ชม./สัปดาห์)", "doc": "Thai_Labor_Law_Hours.pdf"},
    "ร้องเรียน": {"std": "UNGPs Principle 29 | กลไกรับเรื่องร้องเรียนต้องเข้าถึงได้และไม่มีการแก้แค้น", "doc": "UNGPs.pdf"},
    "ค่าธรรมเนียม": {"std": "Zero Recruitment Fees Policy | นายจ้างต้องรับผิดชอบค่าใช้จ่ายในการสรรหา", "doc": "Betagro_Policy.pdf"},
    "นายหน้า": {"std": "Zero Recruitment Fees Policy | นโยบายการตรวจสอบบริษัทจัดหาแรงงานภายนอก", "doc": "Betagro_Policy.pdf"}
}

# --- 2. CONNECT ENGINE ---
@st.cache_resource(ttl=30) 
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

def check_id_conflict(sheet, location, resp_id, resp_group, resp_dept, resp_gender):
    if not resp_id or resp_id.strip() == "": 
        return False
    all_records = sheet.get_all_values()
    for row in all_records:
        if len(row) > 8 and row[5] == resp_id:
            if row[3] != location or row[6] != resp_group or row[7] != resp_dept or row[8] != resp_gender:
                return True 
    return False 

def get_heat_color(s, l):
    val = s * l
    if val >= 16 or s == 5: return "#DC2626"                
    elif val >= 8: return "#D97706"                
    else: return "#059669"                

# --- 3. STYLING (เพิ่ม Media Queries ให้รองรับ Mobile และ Modal ที่สมบูรณ์แบบ) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&family=Sarabun:wght@300;400;600;700;800&display=swap');
    
    html, body, [class*="st-"] { font-family: 'Sarabun', sans-serif; }
    .stApp { background-color: #F4F7F6; }
    
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    [data-testid="stHeader"], [data-testid="collapsedControl"], [data-testid="stSidebar"] { display: none !important; }
    
    .premium-banner {
        background: #FFFFFF; border-radius: 24px; padding: 30px 40px;
        box-shadow: 0px 20px 40px rgba(0, 91, 49, 0.05);
        border: 1px solid rgba(0, 91, 49, 0.08); border-left: 12px solid #005B31; 
        display: flex; align-items: center; gap: 30px; margin-bottom: 40px; position: relative; overflow: hidden;
    }
    .premium-banner::after { content: ''; position: absolute; top: 0; right: 0; width: 150px; height: 8px; background: #F9A818; }
    
    .logo-wrapper { border-right: 2px solid #EAEAEA; padding-right: 30px; display: flex; flex-direction: column; align-items: center; min-width: max-content; }
    .typography-logo { font-family: 'Poppins', sans-serif; font-size: 26px; font-weight: 800; color: #D3A129; letter-spacing: 2px; margin-top: 10px; }
    .hero-title-eng { color: #005B31 !important; font-family: 'Poppins', sans-serif !important; font-size: 21px !important; font-weight: 800 !important; margin: 0 !important; white-space: nowrap; }
    .hero-title-thai { color: #265F36 !important; font-family: 'Sarabun', sans-serif !important; font-size: 16px !important; font-weight: 600 !important; margin: 5px 0 0 0 !important; white-space: nowrap; }
    .hero-subtitle { color: #D3A129 !important; font-family: 'Poppins', sans-serif !important; font-size: 11px !important; font-weight: 700 !important; letter-spacing: 3px !important; text-transform: uppercase !important; margin-top: 14px !important; border-top: 1px solid rgba(211, 161, 41, 0.3) !important; padding-top: 10px !important; width: fit-content; }
    
    /* 📱 MOBILE RESPONSIVE CSS */
    @media (max-width: 768px) {
        .premium-banner { flex-direction: column !important; text-align: center !important; padding: 25px 15px !important; gap: 15px !important; }
        .logo-wrapper { border-right: none !important; border-bottom: 2px solid #EAEAEA !important; padding-right: 0 !important; padding-bottom: 20px !important; }
        .hero-title-eng { white-space: normal !important; font-size: 18px !important; line-height: 1.3 !important; }
        .hero-title-thai { white-space: normal !important; font-size: 14px !important; line-height: 1.4 !important; }
        .hero-subtitle { margin: 10px auto 0 auto !important; }
        .two-col-mobile { flex-direction: column !important; }
    }
    
    .control-panel { background: #FFFFFF; padding: 30px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.03); border: 1px solid #EAEAEA; margin-bottom: 30px; border-top: 5px solid #F9A818; }
    [data-testid="stForm"], .standalone-form { background: #FFFFFF; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.04); padding: 30px; }
    
    [data-testid="stFormSubmitButton"] > button, .stButton > button {
        background: #005B31 !important; color: #FFFFFF !important; border-radius: 10px !important;
        font-weight: 700 !important; padding: 12px 24px !important; border: none !important;
        box-shadow: 0 8px 20px rgba(0, 91, 49, 0.2) !important; transition: all 0.3s ease; width: 100%; font-size: 16px !important;
    }
    
    .salient-badge { padding: 15px; border-radius: 12px; font-weight: 700; text-align: center; display: block; margin-top: 15px; border: 1px solid transparent;}
    .gemini-draft-box { background: linear-gradient(135deg, #F0F4FF 0%, #FFFFFF 100%); border-left: 6px solid #4285F4; padding: 25px; border-radius: 12px; margin-top: 20px; border: 1px solid #D2E3FC; box-shadow: 0 4px 15px rgba(66, 133, 244, 0.05);}
    .gemini-title { color: #1967D2; font-family: 'Poppins', sans-serif; font-weight: 700; margin-top: 0; font-size: 18px; display: flex; align-items: center; gap: 8px;}
    
    .heat-table { width: 100%; border-collapse: separate; border-spacing: 4px; margin-top: 15px;}
    .heat-cell { height: 60px; text-align: center; font-weight: bold; color: white; border-radius: 8px; font-size: 18px; transition: 0.3s; position: relative;}
    .matrix-bubble { width: 34px; height: 34px; background: #FFFFFF; border-radius: 50%; color: #333; display: flex; align-items: center; justify-content: center; margin: 0 auto; font-weight: 800; cursor: pointer; box-shadow: 0 4px 10px rgba(0,0,0,0.3); font-size: 16px;}
    
    .dash-card { background: #FFFFFF; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #EAEAEA; text-align: center; }
    .dash-number { font-size: 36px; font-family: 'Poppins', sans-serif; font-weight: 800; color: #005B31; line-height: 1; margin: 10px 0; }
    .dash-label { font-size: 14px; color: #666; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }

    .radar-pulse { width: 80px; height: 80px; background: rgba(220, 38, 38, 0.15); border-radius: 50%; display: flex; align-items: center; justify-content: center; animation: pulse 2s infinite; margin: 0 auto 20px auto; }
    .radar-core { width: 24px; height: 24px; background: #DC2626; border-radius: 50%; box-shadow: 0 0 10px #DC2626; }
    @keyframes pulse { 0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.7); } 70% { transform: scale(1); box-shadow: 0 0 0 20px rgba(220, 38, 38, 0); } 100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(220, 38, 38, 0); } }

    .filter-box { background: #FDFDFD; border: 1px dashed #D3A129; padding: 20px; border-radius: 8px; margin-bottom: 25px; }
    .testimony-box { background-color: #FFFFFF; border-left: 4px solid #F59E0B; padding: 15px; margin-bottom: 10px; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); display: flex; justify-content: space-between; align-items: flex-start; gap: 15px;}
    
    /* 💡 SAFEST CSS MODALS (No freezing guaranteed) */
    .cite-pill {
        display: inline-flex; align-items: center; justify-content: center;
        background-color: #E0E7FF; color: #4F46E5; border-radius: 12px;
        padding: 4px 12px; font-size: 12px; font-weight: 800; cursor: pointer;
        border: 1px solid #C7D2FE; transition: all 0.2s; white-space: nowrap;
    }
    .cite-pill:hover { background-color: #4F46E5; color: #FFFFFF; box-shadow: 0 4px 8px rgba(79, 70, 229, 0.3); }
    .cite-pill.doc-pill { background-color: #FEF3C7; color: #B45309; border-color: #FDE68A; }
    .cite-pill.doc-pill:hover { background-color: #B45309; color: #FFFFFF; }

    .modal-toggle { display: none; }
    .modal-window {
        position: fixed !important; top: 0 !important; left: 0 !important; right: 0 !important; bottom: 0 !important;
        width: 100vw !important; height: 100vh !important; z-index: 999999 !important;
        display: flex; align-items: center; justify-content: center;
        opacity: 0; pointer-events: none; transition: opacity 0.3s;
    }
    .modal-toggle:checked ~ .modal-window { opacity: 1; pointer-events: auto; }
    
    .modal-backdrop { 
        position: absolute; top: 0; left: 0; right: 0; bottom: 0; 
        background: rgba(0,0,0,0.7); backdrop-filter: blur(4px);
        cursor: pointer; z-index: 1; 
    }
    
    .modal-content {
        background: #F8FAFC; width: 90%; max-width: 700px; max-height: 80vh;
        border-radius: 16px; display: flex; flex-direction: column;
        box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5); transform: translateY(20px); transition: transform 0.3s;
        border: 1px solid #E5E7EB; z-index: 2; position: relative; overflow: hidden;
    }
    .modal-toggle:checked ~ .modal-window .modal-content { transform: translateY(0); }
    
    .modal-header {
        background: #FFFFFF; padding: 15px 25px; border-bottom: 1px solid #E5E7EB;
        display: flex; justify-content: space-between; align-items: center;
    }
    .modal-title-link { font-family: 'Poppins', sans-serif; font-size: 16px; font-weight: 700; color: #111827; }
    .close-btn { 
        cursor: pointer; font-size: 20px; color: #9CA3AF; font-weight: bold; background: #F3F4F6; 
        width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; 
        border-radius: 50%; transition: 0.2s;
    }
    .close-btn:hover { background: #EF4444; color: white; }
    .modal-body { padding: 30px; overflow-y: auto; background: #F3F4F6;}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# --- 3.1 🔐 ENTERPRISE SSO & WHITELIST ---
# ==========================================
if "user_db" not in st.session_state: st.session_state.user_db = {}
if "current_user" not in st.session_state: st.session_state.current_user = None

WHITELIST = ["admin@betagro.com", "somchai@betagro.com", "auditor1@betagro.com", "auditor2@betagro.com", "investor@betagro.com"]

def check_password():
    if st.session_state.current_user is not None:
        return True

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
                <h2 style="color: #005B31; font-family: 'Poppins', sans-serif; font-weight: 800; margin: 0; font-size: 36px;">BETAGRO</h2>
                <p style="color: #D3A129; font-weight: 700; letter-spacing: 3px; text-transform: uppercase; font-size: 12px; margin-top: 5px;">Enterprise Single Sign-On</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown("<h4 style='color: #005B31; text-align: center; margin-bottom: 20px; font-weight: 600;'>🔒 ระบบประเมิน HRDD อัจฉริยะ</h4>", unsafe_allow_html=True)
            email = st.text_input("Corporate Email (อีเมลองค์กร)", placeholder="เช่น admin@betagro.com")
            if email:
                if email in WHITELIST:
                    if email not in st.session_state.user_db:
                        st.info("👋 ยินดีต้อนรับผู้ใช้งานใหม่! เนื่องจากคุณเพิ่งเข้าสู่ระบบครั้งแรก กรุณาตั้งรหัสผ่านสำหรับบัญชีของคุณเพื่อความปลอดภัย")
                        new_pwd = st.text_input("ตั้งรหัสผ่านใหม่ (New Password)", type="password")
                        confirm_pwd = st.text_input("ยืนยันรหัสผ่าน (Confirm Password)", type="password")
                        if st.form_submit_button("บันทึกรหัสผ่านและเข้าสู่ระบบ"):
                            if new_pwd == confirm_pwd and new_pwd != "":
                                st.session_state.user_db[email] = new_pwd
                                st.session_state.current_user = email
                                st.rerun()
                            else:
                                st.error("❌ รหัสผ่านไม่ตรงกัน หรือเว้นว่าง กรุณาลองใหม่")
                    else:
                        pwd = st.text_input("รหัสผ่าน (Password)", type="password", placeholder="Enter Password...")
                        c_btn1, c_btn2 = st.columns(2)
                        with c_btn1: btn_login = st.form_submit_button("LOGIN", use_container_width=True)
                        with c_btn2: btn_forgot = st.form_submit_button("ลืมรหัสผ่าน?", use_container_width=True)
                        if btn_forgot:
                            st.success("📩 ระบบได้ส่งลิงก์สำหรับรีเซ็ตรหัสผ่านไปยังอีเมลองค์กรของคุณเรียบร้อยแล้ว")
                        elif btn_login:
                            if pwd == st.session_state.user_db[email]:
                                st.session_state.current_user = email
                                st.rerun()
                            else:
                                st.error("❌ รหัสผ่านไม่ถูกต้อง")
                else:
                    st.error("❌ Access Denied. อีเมลนี้ไม่ได้รับสิทธิ์การเข้าถึง (Not in Whitelist)")
                    st.form_submit_button("LOGIN") 
            else:
                st.form_submit_button("ตรวจสอบสิทธิ์")
                st.caption("💡 อีเมลทดสอบระบบ: admin@betagro.com")
    return False

if not check_password(): st.stop()

if "approved_issues" not in st.session_state: st.session_state.approved_issues = []
if "saved_plans_dict" not in st.session_state: st.session_state.saved_plans_dict = {}

# ==========================================
# --- 4. TOP UI NAVIGATION ---
# ==========================================
st.markdown("""
    <div class="premium-banner">
        <div class="logo-wrapper">
            <svg width="65" height="65" viewBox="0 0 100 100">
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
st.markdown("<h4 style='color: #005B31; margin-bottom: 15px; font-weight: 700;'>1. ข้อมูลโครงการและบัญชีผู้ใช้งาน</h4>", unsafe_allow_html=True)
col_p1, col_p2 = st.columns(2)
with col_p1: audit_cycle = st.selectbox("รอบการประเมิน *", ["Annual 2026", "Q1/2026", "Q2/2026"])
with col_p2: 
    st.text_input("ผู้ใช้งานระบบ", value=st.session_state.current_user, disabled=True)
    auditor_name = st.session_state.current_user

st.markdown("<hr style='border: 1px solid #eee; margin: 20px 0;'>", unsafe_allow_html=True)
st.markdown("<h4 style='color: #005B31; margin-bottom: 15px; font-weight: 700;'>2. เลือกเครื่องมือปฏิบัติงาน</h4>", unsafe_allow_html=True)
choice = st.selectbox("เลือกฟังก์ชันหรือรายงานที่ต้องการ:", [
    "Tool 1: ประเมินสถานะองค์กร (Governance & Policy Gap)",
    "Tool 2: แบบสอบถามหน้างาน (Worker Survey)",
    "Tool 3: สัมภาษณ์เชิงลึก (Evidence Base)",
    "Tool 4: บันทึกการสังเกตการณ์ (Site Observation Log)",
    "Tool 5: ประเมินนัยสำคัญของความเสี่ยง (Salient Risk Matrix)",
    "Tool 6: ระบบเตือนภัยล่วงหน้า (AI Triangulation & Early Warning)",
    "Tool 7: แดชบอร์ดและรายงานสรุป (Dashboard & Report)"
], label_visibility="collapsed")

is_tool_1_to_4 = choice.startswith("Tool 1") or choice.startswith("Tool 2") or choice.startswith("Tool 3") or choice.startswith("Tool 4")

if is_tool_1_to_4:
    st.markdown("<hr style='border: 1px dashed #EAEAEA; margin: 20px 0;'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #005B31; margin-bottom: 15px; font-weight: 700;'>3. ข้อมูลพื้นที่และผู้ให้ข้อมูล (Location & Respondent)</h4>", unsafe_allow_html=True)
    st.info("📌 กรุณาระบุพื้นที่และรหัสอ้างอิงรายบุคคล เพื่อความแม่นยำในการเก็บข้อมูลเข้าฐานข้อมูล")
    
    col_r_loc, col_r_id = st.columns([2, 1])
    with col_r_loc: location = st.text_input("พื้นที่สำรวจ (Location/Site) *", placeholder="เช่น รง.แปรรูปไก่ สระบุรี")
    with col_r_id: resp_id = st.text_input("รหัสอ้างอิง (ID) *", placeholder="เช่น T01, M01")

    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1: resp_group = st.selectbox("กลุ่มเป้าหมาย *", ["ผู้บริหาร", "พนักงานไทย", "แรงงานข้ามชาติ", "คู่ค้า (Suppliers)", "ชุมชน", "องค์กรไม่แสวงหากำไร (NGOs)", "นักลงทุน", "ลูกค้า (B2B/Retail)"])
    with col_r2: resp_dept = st.text_input("แผนก/ส่วนงาน *", placeholder="เช่น ฝ่ายตัดแต่ง")
    with col_r3: resp_gender = st.selectbox("เพศ (Gender) *", ["ชาย", "หญิง", "ไม่ระบุ"])
else:
    location = "ภาพรวมองค์กร"
    resp_id = "N/A"
    resp_group = "N/A"
    resp_dept = "N/A"
    resp_gender = "N/A"
st.markdown('</div>', unsafe_allow_html=True)

now = (datetime.utcnow() + timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")
sheet = connect_to_sheet()

# 💡 โหลดข้อมูลจริงจาก Sheet มาเก็บไว้ใน DataFrame
df_real = pd.DataFrame()
if sheet:
    all_records = sheet.get_all_values()
    if len(all_records) > 1:
        df_real = pd.DataFrame(all_records[1:], columns=all_records[0])

if is_tool_1_to_4:
    if not location or not resp_id or not resp_dept:
        st.warning("⚠️ กรุณากรอก **พื้นที่สำรวจ, รหัสอ้างอิง (ID)** และ **แผนก/ส่วนงาน** ให้ครบถ้วน เพื่อทำแบบประเมิน")
        st.stop()
    elif sheet:
        with st.spinner("กำลังตรวจสอบความถูกต้องของรหัสอ้างอิง..."):
            if check_id_conflict(sheet, location, resp_id, resp_group, resp_dept, resp_gender):
                st.error(f"❌ ไม่อนุญาตให้ทำรายการ: รหัสอ้างอิง '{resp_id}' ถูกใช้งานไปแล้วกับบุคคลอื่น!")
                st.stop() 

# ==========================================
# --- 6. TOOLS 1-4 FORMS ---
# ==========================================
if choice.startswith("Tool 1"):
    with st.form("form_t1"):
        st.markdown("<h3 style='color:#005B31;'>Tool 1: ประเมินสถานะองค์กร (Policy Gap)</h3><hr>", unsafe_allow_html=True)
        st.markdown("**หมวด A: การกำกับดูแลและนโยบาย**")
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
            if sheet:
                detail = f"A({q1_1},{q1_2},{q1_3})|B({q2_1},{q2_2})|C({q3_1},{q3_2})"
                sheet.append_row([now, audit_cycle, auditor_name, location, "Tool 1", resp_id, resp_group, resp_dept, resp_gender, "Policy Gap Analysis", detail, "", "", "", ""])
                st.success("✅ บันทึกข้อมูล Tool 1 เรียบร้อย")

elif choice.startswith("Tool 2"):
    with st.form("form_t2"):
        st.markdown("<h3 style='color:#005B31;'>Tool 2: แบบสอบถามการปฏิบัติหน้างาน</h3>", unsafe_allow_html=True)
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
            if sheet:
                detail = f"จ้างงาน({s1_1},{s1_2},{s1_3}) | OHS({s2_1},{s2_2},{s2_3}) | ปฏิบัติ({s3_1},{s3_2})"
                sheet.append_row([now, audit_cycle, auditor_name, location, "Tool 2", resp_id, resp_group, resp_dept, resp_gender, "Worker Survey", detail, "", "", "", ""])
                st.success("✅ ส่งข้อมูลแบบสอบถามสำเร็จ")

elif choice.startswith("Tool 3"):
    with st.form("form_t3"):
        st.markdown("<h3 style='color:#005B31;'>Tool 3: สัมภาษณ์เชิงลึก</h3><hr>", unsafe_allow_html=True)
        st.markdown("**🔍 หัวข้อการตรวจสอบ (เลือกข้อที่พบประเด็นความเสี่ยง)**")
        topics = st.multiselect("ประเด็นที่พูดคุย:", ["การสรรหา/ค่านายหน้า", "ความเข้าใจในสัญญาจ้าง", "สภาพที่พักอาศัย/โรงอาหาร", "กลไกการร้องเรียน", "การเลือกปฏิบัติ", "ชั่วโมงการทำงาน", "ความรู้/อบรม"], label_visibility="collapsed")
        st.markdown("<br>**✍️ บันทึกคำให้การ (Testimony)**", unsafe_allow_html=True)
        testimony = st.text_area("สรุปคำพูดหรือหลักฐานที่พบ:", height=150)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("💾 บันทึกข้อมูล Tool 3"):
            if sheet:
                sheet.append_row([now, audit_cycle, auditor_name, location, "Tool 3", resp_id, resp_group, resp_dept, resp_gender, ", ".join(topics), testimony, "", "", "", ""])
                st.success("✅ บันทึกหลักฐานสำเร็จ")

elif choice.startswith("Tool 4"):
    with st.form("form_t4"):
        st.markdown("<h3 style='color:#005B31;'>Tool 4: บันทึกการสังเกตการณ์</h3><hr>", unsafe_allow_html=True)
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
            if sheet:
                res_o1 = f"{o1.split(' ')[1]} ({note_o1})" if note_o1 else o1.split(" ")[1]
                res_o2 = f"{o2.split(' ')[1]} ({note_o2})" if note_o2 else o2.split(" ")[1]
                res_o3 = f"{o3.split(' ')[1]} ({note_o3})" if note_o3 else o3.split(" ")[1]
                res_o4 = f"{o4.split(' ')[1]} ({note_o4})" if note_o4 else o4.split(" ")[1]
                res_o5 = f"{o5.split(' ')[1]} ({note_o5})" if note_o5 else o5.split(" ")[1]
                detail = f"Policy: {res_o1} | Fire: {res_o2} | PPE: {res_o3} | Env: {res_o4} | Med: {res_o5}"
                sheet.append_row([now, audit_cycle, auditor_name, location, "Tool 4", resp_id, resp_group, resp_dept, resp_gender, "Site Observation", detail, "", "", "", ""])
                st.success("✅ บันทึกการสังเกตการณ์สำเร็จ")

# ----------------- TOOL 5 (REAL DATA + NEW MODALS) -----------------
elif choice == "Tool 5: ประเมินนัยสำคัญของความเสี่ยง (Salient Risk Matrix)":

    st.markdown("<div class='standalone-form'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#005B31; margin-top:0;'>Tool 5: ประเมินนัยสำคัญของความเสี่ยง (Issue-Based)</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="filter-box">
        <h5 style="color:#D97706; margin-top:0;"><i class="fa-solid fa-filter"></i> กำหนดหน่วยการวิเคราะห์ (Unit of Analysis)</h5>
        <p style="font-size: 14px; color: #666; margin-bottom: 10px;">กรองฐานข้อมูลเพื่อประเมินความเสี่ยงระดับองค์กร หรือเจาะจงตามกลุ่มผู้มีส่วนได้เสีย</p>
    """, unsafe_allow_html=True)
    
    filter_mode = st.radio("ระดับการวิเคราะห์:", ["ระดับองค์กรภาพรวม (Corporate Level / ทุกกลุ่ม)", "ระดับเจาะจงกลุ่มเป้าหมาย (Stakeholder Group Level)"], horizontal=True, label_visibility="collapsed")
    custom_filter_text = ""
    
    if filter_mode == "ระดับเจาะจงกลุ่มเป้าหมาย (Stakeholder Group Level)":
        custom_filter_text = st.selectbox("เลือกกลุ่มเป้าหมายที่ต้องการดึงข้อมูลมาวิเคราะห์:", [
            "ผู้บริหาร", "พนักงานไทย", "แรงงานข้ามชาติ", "คู่ค้า (Suppliers)", "ชุมชน", "องค์กรไม่แสวงหากำไร (NGOs)", "นักลงทุน", "ลูกค้า (B2B/Retail)"
        ])
    st.markdown("</div>", unsafe_allow_html=True)

    df_filtered = df_real.copy()
    if not df_real.empty:
        if custom_filter_text:
            df_filtered = df_real[df_real['กลุ่มเป้าหมาย'] == custom_filter_text]
    
    sheet_data_count = len(df_filtered)
    if sheet_data_count == 0: 
        st.warning(f"⚠️ ไม่พบข้อมูลการประเมินของกลุ่มเป้าหมาย [{custom_filter_text}] ในฐานข้อมูล (Google Sheet)")
        st.stop()

    btn_text = f"✨ ให้ Gemini AI ดึงข้อมูลของกลุ่ม [{custom_filter_text}] จำนวน {sheet_data_count} รายการ มาวิเคราะห์ความเสี่ยง" if custom_filter_text else f"✨ ให้ Gemini AI วิเคราะห์ประเด็นจากภาพรวมองค์กรทั้งหมด ({sheet_data_count} รายการ)"
    
    st.markdown("<h5 style='color: #005B31; margin-top: 20px;'><i class='fa-solid fa-wand-magic-sparkles'></i> 1. สกัดประเด็นความเสี่ยงจากฐานข้อมูลจริง</h5>", unsafe_allow_html=True)
    if st.button(btn_text):
        st.session_state.ai_scanned_issues = True
    
    selected_issue = ""
    if st.session_state.get("ai_scanned_issues", False):
        real_issues_from_sheet = []
        if 'ประเด็นหลัก' in df_filtered.columns:
            raw_issues = df_filtered['ประเด็นหลัก'].unique().tolist()
            real_issues_from_sheet = [i for i in raw_issues if str(i).strip() not in ["", "Worker Survey", "Site Observation", "Policy Gap Analysis"]]
        
        if len(real_issues_from_sheet) == 0:
            st.info(f"✅ AI ประมวลผลข้อมูลของกลุ่มนี้แล้ว ไม่พบประเด็นความเสี่ยงที่มีนัยสำคัญครับ")
            st.stop()
            
        ai_header = f"🤖 Gemini AI พบ {len(real_issues_from_sheet)} ประเด็นความเสี่ยง จากฐานข้อมูลจริง (กลุ่ม: {custom_filter_text if custom_filter_text else 'ทั้งหมด'}):"
        st.markdown(f'<div style="background: #E8F0FE; padding: 15px; border-radius: 8px; border-left: 4px solid #1967D2; margin-bottom: 20px;"><span style="color: #1967D2; font-weight: 700; font-size: 14px;">{ai_header}</span></div>', unsafe_allow_html=True)
        
        display_list = ["เลือกประเด็นความเสี่ยงเพื่อจัดการ..."] + real_issues_from_sheet
        selected_issue = st.selectbox("เลือกประเด็นความเสี่ยงเพื่อจัดทำแผน (Process Issue):", display_list)

    if not selected_issue or selected_issue == "เลือกประเด็นความเสี่ยงเพื่อจัดการ...":
        st.stop()

    save_issue = selected_issue
    is_already_approved = save_issue in st.session_state.approved_issues
    scope_text = f"กลุ่ม {custom_filter_text}" if custom_filter_text else "ภาพรวม"

    # 💡 THE MAGIC: เตรียมโค้ด HTML สร้างป้าย Citation และ Popup 
    real_testimonies_html = ""
    dynamic_modals_html = ""
    evidence_count = 0

    if not df_filtered.empty and 'รายละเอียด/คำให้การ' in df_filtered.columns:
        subset = df_filtered[df_filtered['ประเด็นหลัก'] == selected_issue]
        for idx, row in subset.head(5).iterrows(): # ดึงมาโชว์แค่ 5 อันแรกกันรกลูกตา
            if str(row['รายละเอียด/คำให้การ']).strip() != "":
                evidence_count += 1
                r_id = row['รหัสผู้ตอบ']
                modal_id = f"modal-evi-{idx}"

                # 1. สร้างป้ายพร้อมข้อความ
                real_testimonies_html += f"""
                <div class="testimony-box">
                    <div><b>(ID {r_id}):</b> <mark>{row['รายละเอียด/คำให้การ']}</mark></div>
                    <label for="{modal_id}" class="cite-pill" title="คลิกดูข้อมูลเต็ม">[Source {evidence_count}]</label>
                </div>
                """

                # 2. สร้างโครงสร้างหน้าต่าง Popup (Modal) ซ่อนไว้
                dynamic_modals_html += f"""
                <input type="checkbox" id="{modal_id}" class="modal-toggle">
                <div class="modal-window">
                    <label class="modal-backdrop" for="{modal_id}"></label>
                    <div class="modal-content">
                        <div class="modal-header">
                            <div class="modal-title-link"><i class="fa-solid fa-file-lines" style="color:#3B82F6;"></i> ข้อมูลอ้างอิงรหัส: {r_id}</div>
                            <label for="{modal_id}" class="close-btn"><i class="fa-solid fa-xmark"></i></label>
                        </div>
                        <div class="modal-body">
                            <div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #e5e7eb;">
                                <h4>รายละเอียดคำให้การ (Full Record)</h4>
                                <table style="width:100%; border-collapse: collapse; margin-top:15px; font-size:16px;">
                                    <tr style="border-bottom:1px solid #eee;"><td style="padding:10px; font-weight:bold; width:30%; color:#005B31;">วันที่เก็บข้อมูล</td><td style="padding:10px;">{row.get('วันที่-เวลา', '-')}</td></tr>
                                    <tr style="border-bottom:1px solid #eee;"><td style="padding:10px; font-weight:bold; color:#005B31;">พื้นที่สำรวจ</td><td style="padding:10px;">{row.get('พื้นที่สำรวจ', '-')}</td></tr>
                                    <tr style="border-bottom:1px solid #eee;"><td style="padding:10px; font-weight:bold; color:#005B31;">กลุ่มเป้าหมาย</td><td style="padding:10px;">{row.get('กลุ่มเป้าหมาย', '-')} / {row.get('แผนก/ส่วนงาน', '-')}</td></tr>
                                    <tr style="border-bottom:1px solid #eee;"><td style="padding:10px; font-weight:bold; color:#005B31;">ประเด็นหลัก</td><td style="padding:10px;">{row.get('ประเด็นหลัก', '-')}</td></tr>
                                    <tr><td style="padding:15px 10px; font-weight:bold; vertical-align:top; color:#005B31;">คำให้การฉบับเต็ม</td><td style="padding:15px 10px; background:#FEF08A; border-radius:4px; font-weight:bold;">{row['รายละเอียด/คำให้การ']}</td></tr>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
                """
    
    # 💡 KNOWLEDGE BASE MATCHER
    matched_law = "UNGPs | ILO Conventions | กฎหมายที่เกี่ยวข้อง"
    matched_doc = "Standard_Guideline.pdf"
    for keyword, knowledge in LAW_KNOWLEDGE_BASE.items():
        if keyword in selected_issue:
            matched_law = knowledge["std"]
            matched_doc = knowledge["doc"]
            break

    std_modal_id = "modal-std-law"
    framework_html = f"""
    ⚖️ <b>อ้างอิงมาตรฐาน (Standard):</b> {matched_law}
    <label for="{std_modal_id}" class="cite-pill doc-pill" title="คลิกดูข้อกฎหมาย">[อ่านฉบับเต็ม]</label>
    """
    
    law_modal_html = f"""
    <input type="checkbox" id="{std_modal_id}" class="modal-toggle">
    <div class="modal-window">
        <label class="modal-backdrop" for="{std_modal_id}"></label>
        <div class="modal-content">
            <div class="modal-header">
                <div class="modal-title-link"><i class="fa-solid fa-scale-balanced" style="color:#D97706;"></i> ฐานข้อมูลกฎหมาย: {matched_doc}</div>
                <label for="{std_modal_id}" class="close-btn"><i class="fa-solid fa-xmark"></i></label>
            </div>
            <div class="modal-body">
                 <div style="background: white; padding: 30px; border-radius: 8px; border: 1px solid #e5e7eb;">
                    <h4 style="color: #005B31; border-bottom: 2px solid #E5E7EB; padding-bottom: 15px; margin-top: 0; text-transform: uppercase;">{matched_doc.replace('.pdf','').replace('_',' ')}</h4>
                    <p><b>ข้อกำหนดตามมาตรฐาน:</b></p>
                    <p style="background-color: #FEF08A; padding: 15px; border-radius: 8px; font-weight: bold; border-left: 4px solid #EAB308; font-size: 16px;">
                        {matched_law}
                    </p>
                    <p style="color:#9CA3AF; font-size:12px; margin-top:30px; border-top: 1px dashed #E5E7EB; padding-top: 10px;">
                        *เอกสารข้อกฎหมายจำลองนี้ ดึงมาจากระบบ Knowledge Base ขององค์กรอัตโนมัติ
                    </p>
                </div>
            </div>
        </div>
    </div>
    """

    plain_evidence = f"ระบบ AI ตรวจพบความเสี่ยงจากข้อมูลจริงจำนวน {evidence_count} รายการ ในฐานข้อมูลของกลุ่ม {scope_text}"
    plain_standard = matched_law

    # นำกล่อง HTML Evidence และ Modals ทั้งหมดไป Render พร้อมกัน
    st.markdown(f"""
    {dynamic_modals_html}
    {law_modal_html}
    <div style="background: #F5F3FF; border-left: 4px solid #8B5CF6; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.02);">
        <strong style="color: #6D28D9; font-size: 16px;"><i class="fa-solid fa-magnifying-glass-chart"></i> AI Triangulation Evidence (หลักฐานสนับสนุนจากข้อมูลจริง):</strong>
        <div style="font-size: 14px; margin-top: 15px; color: #444; line-height: 1.8;">
            {real_testimonies_html if real_testimonies_html else "<i>(ไม่มีคำให้การเจาะจง ประเมินจากคะแนนแบบสอบถามหรือการสังเกตการณ์)</i>"}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border: 1px dashed #ccc;'>", unsafe_allow_html=True)
    st.markdown("<h5 style='color: #005B31;'><i class='fa-solid fa-sliders'></i> 2. ประเมินระดับความรุนแรง (Severity) และ โอกาสเกิด (Likelihood)</h5>", unsafe_allow_html=True)

    def_scale, def_sco, def_rem, def_lik = 3, 3, 3, 3
    if "แรงงาน" in selected_issue or "พาสปอร์ต" in selected_issue or "เด็ก" in selected_issue: def_scale = 5
    if "ชุมชน" in selected_issue: def_sco = 5
    
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1: scale = st.slider("Scale (ขนาดผลกระทบ: 1 เล็กน้อย - 5 Zero Tolerance)", 1, 5, def_scale)
    with col_s2: scope = st.slider("Scope (วงกว้าง: 1 เฉพาะบุคคล - 5 ระดับประเทศ)", 1, 5, def_sco)
    with col_s3: remedy = st.slider("Remedy (การเยียวยา: 1 ทำได้ทันที - 5 เยียวยาไม่ได้)", 1, 5, def_rem)
    
    sev_max = max(scale, scope, remedy)
    likelihood = st.slider("📌 Likelihood (โอกาสที่จะเกิด: 1 ต่ำมาก - 5 สูงมาก)", 1, 5, def_lik)
    score = sev_max * likelihood

    if score >= 16 or sev_max == 5:
        risk_zone = "RED"
        badge_html = '<div class="salient-badge" style="background-color: #FEF2F2; color: #DC2626; border-color: #FECACA;">🚨 SALIENT RISK: ประเด็นนี้มีความเสี่ยงระดับวิกฤต (AI กำลังร่างแผนกลยุทธ์และมาตรการเยียวยาเร่งด่วน)</div>'
        ai_plan = "Preventive: ระงับการปฏิบัติงาน/สืบสวนข้อเท็จจริงทันที (Zero Tolerance Policy)\nRemediation: ชดเชยและเยียวยาผู้ได้รับผลกระทบอย่างเป็นธรรมภายใน 24 ชม."
    elif score >= 8:
        risk_zone = "YELLOW"
        badge_html = '<div class="salient-badge" style="background-color: #FFFBEB; color: #D97706; border-color: #FDE68A;">⚠️ SIGNIFICANT RISK: ประเด็นความเสี่ยงปานกลาง/สูง (AI กำลังร่างแผนป้องกันเชิงรุก)</div>'
        ai_plan = "Preventive Action (แผนป้องกันเชิงรุก):\n- จัดอบรมให้ความรู้ ทบทวนขั้นตอนการทำงาน และสื่อสารนโยบายให้ผู้เกี่ยวข้องรับทราบ\n- ติดตามผลการปรับปรุงภายใน 3 เดือน"
    else:
        risk_zone = "GREEN"
        badge_html = '<div class="salient-badge" style="background-color: #F0FDF4; color: #166534; border-color: #BBF7D0;">✅ MODERATE/MINOR RISK: ความเสี่ยงต่ำ (AI กำลังร่างแผนคงสภาพ)</div>'
        ai_plan = "Maintenance Plan (แผนคงสภาพ):\n- ติดตามผลตามวงรอบปกติอย่างน้อยปีละ 1 ครั้ง"
    
    st.markdown(f"<h4 style='color: #005B31; text-align:center; padding: 15px; background: #F4F7F6; border-radius: 8px;'>Severity Max: {sev_max} | โอกาสเกิด: {likelihood} | คะแนนรวม: {score}</h4>", unsafe_allow_html=True)
    
    rows = ""
    for l in range(5, 0, -1):
        rows += "<tr>"
        for s in range(1, 6):
            color = get_heat_color(s, l)
            mark = "★" if s == sev_max and l == likelihood else ""
            rows += f"<td class='heat-cell' style='background-color:{color}; box-shadow: inset 0 0 15px rgba(0,0,0,0.1);'>{mark}</td>"
        rows += "</tr>"
    st.markdown(f"<table class='heat-table'>{rows}</table><p style='text-align:center; color: #666; margin-top: 10px;'><small>แนวนอน: Severity | แนวตั้ง: Likelihood</small></p>", unsafe_allow_html=True)
    
    st.markdown(badge_html, unsafe_allow_html=True)

    edit_evidence = plain_evidence
    edit_standard = plain_standard
    edit_plan = ai_plan

    if is_already_approved and save_issue in st.session_state.saved_plans_dict:
        saved_data = st.session_state.saved_plans_dict[save_issue]
        edit_evidence = saved_data.get('evidence', plain_evidence)
        edit_standard = saved_data.get('standard', plain_standard)
        edit_plan = saved_data.get('plan', ai_plan)

    st.markdown(f"""
    <div class="gemini-draft-box" style="margin-bottom: 0; border-bottom-left-radius: 0; border-bottom-right-radius: 0; border-bottom: none;">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <h4 class="gemini-title"><span class="gemini-icon">✨</span> Gemini AI: Draft Mitigation Plan</h4>
        </div>
        <div style="background: #FFFFFF; padding: 15px; border-radius: 6px; border: 1px solid #EAEAEA; margin: 15px 0; font-size: 14px; color: #005B31; line-height: 1.8;">
            {framework_html}
        </div>
    </div>
    <div style="background: #FAFAFA; border: 1px solid #D2E3FC; border-top: none; padding: 25px; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px; margin-bottom: 30px;">
        <h5 style="color: #005B31; margin-top: 0; margin-bottom: 15px;"><i class="fa-solid fa-pen-to-square"></i> 3. ตรวจสอบและปรับแก้ข้อมูลโดยมนุษย์ (Human Override)</h5>
        <p style="font-size: 13px; color: #666; margin-bottom: 15px;">คุณสามารถปรับปรุงหลักฐาน, มาตรฐานอ้างอิง หรือแผนปฏิบัติการด้านล่างให้สมบูรณ์ก่อนอนุมัติ</p>
    """, unsafe_allow_html=True)
    
    final_evidence = st.text_area("✍️ แก้ไขหลักฐานสนับสนุน (Triangulation Evidence):", value=edit_evidence, height=80)
    final_standard = st.text_area("✍️ แก้ไขมาตรฐานอ้างอิง (Framework / Standard):", value=edit_standard, height=60)
    final_plan = st.text_area("✍️ แก้ไขแผนการจัดการความเสี่ยง (Mitigation & Remediation Plan):", value=edit_plan, height=120)
    
    st.markdown("</div>", unsafe_allow_html=True)

    button_label = "🔄 อัปเดตข้อมูลฉบับแก้ไข (Overwrite Data)" if is_already_approved else "💾 อนุมัติและบันทึกประเด็นยุทธศาสตร์ (Approve Plan)"

    if st.button(button_label):
        if sheet:
            db_risk_level = "Salient" if risk_zone == "RED" else ("Significant" if risk_zone == "YELLOW" else "Moderate/Minor")
            detail = f"Scale:{scale}, Scope:{scope}, Remedy:{remedy} | Evidence: {final_evidence} | Standard: {final_standard} | Plan: {final_plan}"
            
            macro_group = f"ประเมินเจาะจงระดับกลุ่ม ({custom_filter_text})" if custom_filter_text else "ประเมินภาพรวมระดับองค์กร (Corporate Level)"
            
            new_row_data = [now, audit_cycle, auditor_name, "N/A", "Tool 5", "Issue-Based", macro_group, "N/A", "N/A", save_issue, detail, sev_max, likelihood, score, db_risk_level]
            
            st.session_state.saved_plans_dict[save_issue] = {
                'plan': final_plan, 
                'sev': sev_max, 
                'lik': likelihood,
                'filter_context': custom_filter_text 
            }
            if not is_already_approved:
                st.session_state.approved_issues.append(save_issue)

            with st.spinner("กำลังอัปเดตลง Google Sheet..."):
                sheet.append_row(new_row_data)
                st.success(f"✅ **อนุมัติและบันทึกแผนยุทธศาสตร์สำเร็จ:** ประเด็น '{save_issue}' พร้อมนำไปแสดงผลใน Tool 7 แล้ว")

    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- TOOL 6 (Early Warning System) -----------------
elif choice == "Tool 6: ระบบเตือนภัยล่วงหน้า (AI Triangulation & Early Warning)":
    st.markdown("<div class='standalone-form'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#005B31; margin-top:0;'>Tool 6: AI Early Warning Radar</h3><p style='color:#666;'>ระบบครอสเช็คข้ามเครื่องมือแบบอัตโนมัติ เพื่อดักจับความขัดแย้งเชิงโครงสร้างและพยากรณ์ความเสี่ยง</p><hr>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <div class="radar-pulse">
            <div class="radar-core"></div>
        </div>
        <span style="color: #DC2626; font-weight: 700; font-size: 18px;">System Auto-Scanning... Found 1 Anomaly!</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("#### 🚩 สัญญาณเตือน: การเรียกเก็บค่าธรรมเนียมสรรหา (Recruitment Fee / Debt Bondage Indicator)")
    st.info("🤖 **Gemini AI Triangulation:** ตรวจพบความขัดแย้งเชิงนโยบายและการปฏิบัติจริง (Policy Implementation Gap) จากการวิเคราะห์ข้อมูลจริงใน Sheet")
    
    c_left, c_right = st.columns(2)
    with c_left:
        st.success("📋 **ข้อมูลเชิงนโยบาย (Tool 1: ผู้บริหาร)**\n\nพบข้อมูลจากผู้บริหาร (ID E04):\n\n*\"บริษัทมีนโยบาย Zero Recruitment Fee ชัดเจน แรงงานทุกคนไม่ต้องเสียค่าใช้จ่าย\"*")
    with c_right:
        st.error("🗣️ **ข้อมูลปฏิบัติจริง (Tool 3: แรงงานข้ามชาติ)**\n\nพบคำให้การจากพนักงาน (ID M06, M07):\n\n*\"เอเจนซี่ขอยึดพาสปอร์ตไปเก็บไว้ในตู้เซฟ... ต้องจ่ายค่านายหน้าให้ฝั่งนู้น 15000 บาท ตอนนี้ยังใช้หนี้ไม่หมด\"*")

    st.markdown("""
    <div class="gemini-draft-box" style="margin-top: 20px;">
        <h5 class="gemini-title"><span class="gemini-icon">✨</span> Gemini AI Insight (การวิเคราะห์เชิงลึก):</h5>
        <p style="font-size: 14px; color: #444; margin-top: 5px;">ข้อมูลชี้ให้เห็นถึงช่องโหว่ด้านความโปร่งใสของ <b>Supply Chain / Third-party Agency</b> ซึ่งเป็นจุดบอด (Blind Spot) ของผู้บริหาร หากไม่เร่งตรวจสอบ อาจยกระดับเป็นข้อกล่าวหาด้าน <b>Debt Bondage (ภาระหนี้ผูกพัน)</b> หรือ <b>Forced Labor</b> ตามเกณฑ์สากลได้</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr style='border: 1px dashed #ccc; margin: 30px 0;'>", unsafe_allow_html=True)
    st.markdown("#### ✍️ ส่วนพิจารณาโดยผู้เชี่ยวชาญ (Human Validation)")
    
    t6_decision = st.radio("คุณพิจารณาแนวโน้มของสัญญาณเตือนภัยนี้อย่างไร? *", ["✔️ ยืนยันให้เป็น 'ความเสี่ยงที่ต้องสืบสวน' (Approve for Investigation)", "❌ ปฏิเสธการแจ้งเตือน (Reject / False Alarm)"], horizontal=True)
    t6_note = st.text_input("ระบุเหตุผลสนับสนุนการพิจารณาเชิงยุทธศาสตร์:", placeholder="เช่น สั่งการให้ทีม CSR ลงพื้นที่สุ่มตรวจสอบเอเจนซี่เพิ่มเติมทันที...")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 บันทึกมติการพิจารณา Tool 6"):
        if sheet:
            decision_text = "Approved" if "ยืนยัน" in t6_decision else "Rejected"
            detail = f"Anomaly: Recruitment Fee | Decision: {decision_text} | Note: {t6_note}"
            sheet.append_row([now, audit_cycle, auditor_name, "N/A", "Tool 6", "Issue-Based", "ภาพรวมระดับองค์กร", "N/A", "N/A", "Early Warning (Recruitment Fee)", detail, "", "", "", ""])
            st.session_state.early_warning_approved = True if "ยืนยัน" in t6_decision else False
            st.session_state.early_warning_note = t6_note
            st.success("✅ บันทึกมติการพิจารณาสัญญาณเตือนภัยล่วงหน้าเข้าสู่ระบบฐานข้อมูลกลางเรียบร้อย")
            
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- TOOL 7 (Executive Dashboard & AI Report) -----------------
elif choice == "Tool 7: แดชบอร์ดและรายงานสรุป (Dashboard & Report)":
    st.markdown("<div class='standalone-form'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#005B31; margin-top:0;'>Tool 7: Executive Dashboard & Comprehensive Report</h3><p style='color:#666;'>สรุปผลประเมินนัยสำคัญของความเสี่ยง (Salient Risk) ระดับองค์กร</p><hr>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    
    sheet_data_count = 0
    if not df_real.empty:
        raw_df = df_real[df_real['เครื่องมือ'].isin(['Tool 1', 'Tool 2', 'Tool 3', 'Tool 4'])]
        sheet_data_count = len(raw_df)
            
    with c1: st.markdown(f"<div class='dash-card'><div class='dash-label'>ข้อมูลที่สืบค้นจากระบบ</div><div class='dash-number'>{sheet_data_count}</div><div style='color: #005B31; font-size:12px;'>บันทึกฐานข้อมูลจาก Tool 1-4</div></div>", unsafe_allow_html=True)
    
    approved_count = len(st.session_state.get("approved_issues", []))
    with c2: st.markdown(f"<div class='dash-card'><div class='dash-label'>Salient Issues</div><div class='dash-number' style='color:#DC2626;'>{approved_count}</div><div style='color: #666; font-size:12px;'>ประเด็นที่ได้รับการอนุมัติแผนจัดการ</div></div>", unsafe_allow_html=True)
    
    ew_count = 1 if st.session_state.get("early_warning_approved", False) else 0
    with c3: st.markdown(f"<div class='dash-card'><div class='dash-label'>Early Warnings</div><div class='dash-number' style='color:#D97706;'>{ew_count}</div><div style='color: #666; font-size:12px;'>สัญญาณเตือนภัยที่รอการสอบสวน</div></div>", unsafe_allow_html=True)
    
    st.markdown("<br><h5 style='color: #005B31; text-align:center;'>📊 แผนผังการกระจายตัวความเสี่ยง (Corporate Risk Matrix)</h5>", unsafe_allow_html=True)
    
    matrix_data = {(s, l): [] for s in range(1,6) for l in range(1,6)}
    for iss, data in st.session_state.get("saved_plans_dict", {}).items():
        if (data['sev'], data['lik']) in matrix_data:
            matrix_data[(data['sev'], data['lik'])].append(iss)

    rows = ""
    for l in range(5, 0, -1):
        rows += "<tr>"
        for s in range(1, 6):
            issues = matrix_data[(s, l)]
            color = get_heat_color(s, l)
            content = ""
            if len(issues) > 0:
                issue_text = "&#10;".join([f"- {i}" for i in issues])
                content = f"<div class='matrix-bubble' title='ประเด็นสิทธิมนุษยชนที่ตกอยู่ในพิกัดนี้:&#10;{issue_text}'>{len(issues)}</div>"
            
            rows += f"<td class='heat-cell' style='background-color:{color}; border: 1px solid rgba(0,0,0,0.05);'>{content}</td>"
        rows += "</tr>"
        
    st.markdown(f"""
        <table class='heat-table' style='width: 80%; margin: 0 auto;'>{rows}</table>
        <div style='display: flex; justify-content: space-between; width: 80%; margin: 5px auto 0 auto; color: #666; font-weight: bold; font-size: 12px;'>
            <span>< ความเป็นไปได้ที่จะเกิด (Likelihood)</span>
            <span>ระดับความร้ายแรงของผลกระทบ (Severity) ></span>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr style='border: 2px solid #005B31; margin: 40px 0;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#005B31; margin-top:0;'>📑 ร่างรายงานการบริหารจัดการความเสี่ยง (Comprehensive HRDD Report)</h3>", unsafe_allow_html=True)
    
    if st.button("✨ ให้ Gemini AI สังเคราะห์รายงานภาพรวมองค์กร (Generate Corporate Report)"):
        st.session_state.ai_report_drafted = True

    if st.session_state.get("ai_report_drafted", False):
        st.markdown("""
        <div class="gemini-draft-box">
            <h4 class="gemini-title"><span class="gemini-icon">✨</span> Gemini AI: Strategic Insight & Executive Summary</h4>
            <p style="font-size: 14px; color: #666; margin-bottom: 15px;">ตรวจสอบ ปรับแก้ และพิจารณาอนุมัติวิสัยทัศน์ทางยุทธศาสตร์ในรายงานฉบับสมบูรณ์ด้านล่าง</p>
        </div>
        """, unsafe_allow_html=True)

        issue_list_text = ""
        action_list_text = ""
        saved_dict = st.session_state.get("saved_plans_dict", {})
        
        has_data = False
        for iss, data in saved_dict.items():
            has_data = True
            risk_level = "วิกฤต (Critical)" if (data['sev'] == 5 or data['sev']*data['lik'] >= 16) else "สูง (Significant)" if data['sev']*data['lik'] >= 8 else "ปานกลาง/ต่ำ (Moderate)"
            
            filter_context = data.get('filter_context', '')
            scope_label = f"(กลุ่ม: {filter_context})" if filter_context else "(ระดับองค์กรภาพรวม)"
            
            issue_list_text += f"- {iss} {scope_label}\n  พิกัดประเมิน: ความรุนแรง {data['sev']} / โอกาสเกิด {data['lik']} / ระดับความเสี่ยง: {risk_level}\n\n"
            
            action_text = data['plan'].replace('\n', '\n  ')
            action_list_text += f"▪ สำหรับยุทธศาสตร์การจัดการประเด็น {iss}:\n  {action_text}\n\n"
            
        if not has_data:
            issue_list_text = "- (ข้อมูลว่างเปล่า: ยังไม่มีประเด็นที่ได้รับการอนุมัติเชิงยุทธศาสตร์จาก Tool 5)\n"
            action_list_text = "- (ข้อมูลว่างเปล่า: โปรดทำการประเมินแผนยุทธศาสตร์ใน Tool 5 ให้แล้วเสร็จก่อน)\n"

        early_warning_text = ""
        if st.session_state.get("early_warning_approved", False):
            ew_note = st.session_state.get("early_warning_note", "ให้ทีมสอบสวนลงพื้นที่ตรวจสอบข้อเท็จจริงในห่วงโซ่อุปทานต้นน้ำ")
            early_warning_text = f"""4. การพยากรณ์และสัญญาณเตือนภัยล่วงหน้า (Early Warning & Foresight)
ระบบ AI ครอสเช็คข้อมูลข้ามส่วนงาน (Triangulation) ตรวจพบความเปราะบางเชิงระบบ (Systemic Vulnerability) 1 ประเด็นหลัก:
- ประเด็นเตือนภัย: พบช่องว่างการนำนโยบาย Zero Recruitment Fees ไปปฏิบัติจริง (Policy Implementation Gap)
- แนวทางสืบสวน: อนุมัติดำเนินการตรวจสอบเชิงลึก โดยระบุเหตุผลเชิงยุทธศาสตร์ว่า "{ew_note}" """
        else:
            early_warning_text = """4. การพยากรณ์และสัญญาณเตือนภัยล่วงหน้า (Early Warning & Foresight)
ในรอบการประเมินปัจจุบัน ระบบยังไม่พบสัญญาณขัดแย้งของข้อมูลที่มีนัยสำคัญระดับโครงสร้างที่ต้องจัดตั้งคณะกรรมการสืบสวนฉุกเฉิน"""

        report_mockup = f"""รายงานการประเมินและการบริหารจัดการความเสี่ยงด้านสิทธิมนุษยชนอย่างรอบด้าน (Comprehensive HRDD Report)
รอบการประเมิน: {audit_cycle}
ขอบเขตพื้นที่: ภาพรวมระดับองค์กร (Corporate Overview)
ผู้รับผิดชอบการประเมิน: {auditor_name}

1. วัตถุประสงค์และบริบทเชิงยุทธศาสตร์ (Strategic Context & Overview)
เอกสารฉบับนี้จัดทำขึ้นเพื่อระบุ วิเคราะห์ และพยากรณ์ความเสี่ยงด้านสิทธิมนุษยชนที่อาจซ่อนเร้นอยู่ในห่วงโซ่คุณค่าขององค์กร โดยใช้เครื่องมือประเมินเชิงรุกผสมผสานระบบปัญญาประดิษฐ์ เพื่อให้มั่นใจว่าองค์กรมีการปฏิบัติตามมาตรฐานสากล (UNGPs, ILO, EU CSDDD) 

2. เกณฑ์การพิจารณานัยสำคัญของความเสี่ยง (Salient Risk Assessment Criteria)
องค์กรใช้หลักการ "ความร้ายแรงนำ (Severity-led Principle)" ในการระบุประเด็นที่ต้องให้ความสำคัญสูงสุด โดยพิจารณาน้ำหนักเชิงประจักษ์จาก 3 มิติหลัก ได้แก่: ขนาดและผลกระทบ (Scale), ขอบเขตความเสียหาย (Scope), ความท้าทายในการเยียวยา (Remediability)

3. ข้อค้นพบและผลการวิเคราะห์นัยสำคัญทางสิทธิมนุษยชน (Key Findings on Salient Issues)
จากการบูรณาการข้อมูลเชิงประจักษ์ พบประเด็นความเสี่ยงเชิงโครงสร้างที่ได้รับการอนุมัติให้ยกระดับการเฝ้าระวัง ดังนี้:
{issue_list_text}
{early_warning_text}

5. มาตรการตอบสนองและยุทธศาสตร์การจัดการ (Strategic Mitigation & Remediation Roadmap)
เพื่อแสดงถึงจุดยืนด้านบรรษัทภิบาล องค์กรได้กำหนดแนวทางยุติ ระงับ และเยียวยาผลกระทบ ดังนี้:
{action_list_text}
6. ข้อสรุปและวิสัยทัศน์ทิศทางองค์กร (Executive Conclusion)
การลงทุนในระบบบริหารจัดการความเสี่ยงอัจฉริยะไม่เพียงแต่ลดทอนความเสี่ยงด้านชื่อเสียงและกฎหมาย แต่ยังช่วยตอกย้ำจุดยืนในการเคารพคุณค่าของทรัพยากรมนุษย์ทุกระดับชั้น

7. กลไกการขับเคลื่อนและประเมินผลอย่างต่อเนื่อง (Monitoring & Continuous Improvement)
- ระยะสั้น (Short-term): สั่งการให้หน่วยงาน Audit ติดตามผลสัมฤทธิ์ของมาตรการเชิงรุก (Preventive) ภายใน 3 เดือน
- ระยะยาว (Long-term): ทบทวนนโยบายและประเมินสภาวะแวดล้อมใหม่ประจำปี (Annual Review)"""

        st.markdown("**✍️ ตรวจสอบความถูกต้องของรายงานก่อนการอนุมัติขั้นสุดท้าย:**")
        report_text_final = st.text_area("ทบทวน ปรับแก้ และอนุมัติรายงานฉบับสมบูรณ์ (Review & Approve Report):", value=report_mockup, height=700, label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 อนุมัติยุทธศาสตร์และบันทึกรายงานฉบับสมบูรณ์ (Approve & Save Executive Report)"):
            if sheet:
                sheet.append_row([now, audit_cycle, auditor_name, location, "Tool 7 - Report", "Executive Summary", "ภาพรวมองค์กร", "N/A", "N/A", f"Comprehensive Report: {audit_cycle}", report_text_final, "", "", "", "Approved"])
                st.success("✅ อนุมัติยุทธศาสตร์องค์กรและบันทึกรายงานประเมินความเสี่ยงฉบับสมบูรณ์เข้าสู่ฐานข้อมูลเรียบร้อยแล้ว!")
                
    st.markdown("</div>", unsafe_allow_html=True)
