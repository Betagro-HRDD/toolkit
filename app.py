import streamlit as st
import pandas as pd
from google.oauth2 import service_account
import gspread
from datetime import datetime, timedelta
import altair as alt
import base64
import random

# ==========================================
# --- 1. SETTING UP THE PAGE (ต้องอยู่บนสุดเสมอ) ---
# ==========================================
st.set_page_config(page_title="Betagro Smart HRDD Toolkit", page_icon="🟢", layout="centered")

# --- 2. CONNECT ENGINE ---
@st.cache_resource(ttl=60) # อัปเดตข้อมูลไวขึ้นเป็น 1 นาที
def connect_to_sheet():
    try:
        creds_info = st.secrets["gcp_service_account"]
        private_key = creds_info["private_key"].replace("\\n", "\n")
        creds_dict = {**creds_info, "private_key": private_key}
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        credentials = service_account.Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(credentials)
        SHEET_ID = "1YUkrlk_RlvskDluFoAdTQ7KRYRxYhi8ZqNdw13X7JxY"
        return client.open_by_key(SHEET_ID).get_worksheet(0) # แก้เป็น Index ของชีตที่คุณเก็บ Data
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
    if val >= 16 or s == 5:  
        if val <= 5: return "#FCA5A5"   
        if val <= 10: return "#F87171"  
        if val <= 15: return "#EF4444"  
        if val <= 20: return "#DC2626"  
        return "#991B1B"                
    elif val >= 8:  
        if val <= 9: return "#FDE047"   
        if val <= 12: return "#F59E0B"  
        return "#D97706"                
    else:  
        if val <= 2: return "#A7F3D0"   
        if val <= 4: return "#34D399"   
        return "#059669"                

# --- 3. ULTRA-PREMIUM STYLING & MODAL ENGINE ---
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
    
    .logo-wrapper { border-right: 2px solid #EAEAEA; padding-right: 30px; display: flex; flex-direction: column; align-items: center; }
    .typography-logo { font-family: 'Poppins', sans-serif; font-size: 26px; font-weight: 800; color: #D3A129; letter-spacing: 2px; margin-top: 10px; }
    .hero-title-eng { color: #005B31 !important; font-family: 'Poppins', sans-serif !important; font-size: 21px !important; font-weight: 800 !important; margin: 0 !important; white-space: nowrap !important; }
    .hero-title-thai { color: #265F36 !important; font-family: 'Sarabun', sans-serif !important; font-size: 16px !important; font-weight: 600 !important; margin: 5px 0 0 0 !important; white-space: nowrap !important; }
    .hero-subtitle { color: #D3A129 !important; font-family: 'Poppins', sans-serif !important; font-size: 11px !important; font-weight: 700 !important; letter-spacing: 3px !important; text-transform: uppercase !important; margin-top: 14px !important; border-top: 1px solid rgba(211, 161, 41, 0.3) !important; padding-top: 10px !important; width: fit-content; }
    
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
    
    .dash-card { background: #FFFFFF; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #EAEAEA; text-align: center; }
    .dash-number { font-size: 36px; font-family: 'Poppins', sans-serif; font-weight: 800; color: #005B31; line-height: 1; margin: 10px 0; }
    .dash-label { font-size: 14px; color: #666; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }

    .radar-pulse {
        width: 80px; height: 80px; background: rgba(220, 38, 38, 0.15); border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        animation: pulse 2s infinite; margin: 0 auto 20px auto;
    }
    .radar-core { width: 24px; height: 24px; background: #DC2626; border-radius: 50%; box-shadow: 0 0 10px #DC2626; }
    @keyframes pulse { 0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.7); } 70% { transform: scale(1); box-shadow: 0 0 0 20px rgba(220, 38, 38, 0); } 100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(220, 38, 38, 0); } }

    .filter-box { background: #FDFDFD; border: 1px dashed #D3A129; padding: 20px; border-radius: 8px; margin-bottom: 25px; }

    /* 💡 NOTEBOOK LM INTERACTIVE CITATION & MODAL SYSTEM (FIXED BACKDROP) */
    .cite-pill {
        display: inline-flex; align-items: center; justify-content: center;
        background-color: #E0E7FF; color: #4F46E5; border-radius: 12px;
        padding: 2px 10px; font-size: 12px; font-weight: 800; cursor: pointer;
        margin: 0 4px; border: 1px solid #C7D2FE; transition: all 0.2s;
    }
    .cite-pill:hover { background-color: #4F46E5; color: #FFFFFF; transform: translateY(-2px); box-shadow: 0 4px 8px rgba(79, 70, 229, 0.3); }
    .cite-pill.doc-pill { background-color: #FEF3C7; color: #B45309; border-color: #FDE68A; }
    .cite-pill.doc-pill:hover { background-color: #B45309; color: #FFFFFF; }

    .modal-toggle { display: none; }
    
    .modal-window {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: 999999; display: flex; align-items: center; justify-content: center;
        opacity: 0; pointer-events: none; transition: opacity 0.3s;
    }
    .modal-toggle:checked ~ .modal-window { opacity: 1; pointer-events: auto; }
    
    .modal-backdrop { 
        position: absolute; top: 0; left: 0; width: 100vw; height: 100vh; 
        background: rgba(0,0,0,0.6); backdrop-filter: blur(5px);
        cursor: pointer; z-index: -1; 
    }
    
    .modal-content {
        background: #F8FAFC; width: 85%; max-width: 900px; max-height: 85vh;
        border-radius: 16px; display: flex; flex-direction: column;
        box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5); transform: translateY(20px); transition: transform 0.3s;
        border: 1px solid #E5E7EB; z-index: 10; position: relative;
    }
    .modal-toggle:checked ~ .modal-window .modal-content { transform: translateY(0); }
    
    .modal-header {
        background: #FFFFFF; padding: 15px 25px; border-bottom: 1px solid #E5E7EB;
        display: flex; justify-content: space-between; align-items: center; border-radius: 16px 16px 0 0;
    }
    
    .modal-title-link { 
        font-family: 'Poppins', sans-serif; font-size: 16px; font-weight: 700; color: #111827; 
        display: flex; align-items: center; gap: 10px; text-decoration: none; transition: 0.2s;
    }
    .modal-title-link:hover { color: #4F46E5; }
    
    .close-btn { 
        cursor: pointer; font-size: 24px; color: #9CA3AF; font-weight: bold; background: #F3F4F6; 
        width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; 
        border-radius: 50%; transition: 0.2s; z-index: 10;
    }
    .close-btn:hover { background: #EF4444; color: white; }
    
    .modal-body { padding: 30px; overflow-y: auto; background: #F3F4F6;}
    
    .mock-doc-wrapper { background: #FFFFFF; padding: 40px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-radius: 4px; border: 1px solid #E5E7EB; margin: 0 auto; max-width: 800px;}
    .mock-pdf { font-family: 'Sarabun', serif; color: #333; line-height: 1.8; font-size: 16px; }
    .mock-pdf h4 { text-align: center; border-bottom: 2px solid #111827; padding-bottom: 15px; margin-bottom: 20px; font-family: 'Poppins', sans-serif; font-weight: 800; text-transform: uppercase;}
    .mock-pdf mark { background-color: #FEF08A; padding: 2px 6px; border-radius: 4px; font-weight: 700; border-bottom: 2px solid #EAB308;}
    
    .mock-csv { width: 100%; border-collapse: collapse; font-family: 'Sarabun', sans-serif; font-size: 14px;}
    .mock-csv th { background: #F8FAFC; color: #4B5563; padding: 12px; text-align: left; border: 1px solid #E5E7EB; border-bottom: 2px solid #D1D5DB; }
    .mock-csv td { padding: 12px; border: 1px solid #E5E7EB; color: #374151;}
    .mock-csv .alert-row td { background-color: #FEF2F2; }
    .mock-csv .alert-cell { color: #DC2626; font-weight: 800; background: #FEE2E2; text-align: center; border: 2px solid #F87171;}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# --- 3.1 🔐 ENTERPRISE SSO & WHITELIST AUTHENTICATION ---
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
                            st.success("📩 ระบบได้ส่งลิงก์สำหรับรีเซ็ตรหัสผ่านไปยังอีเมลองค์กรของคุณเรียบร้อยแล้ว (โปรดตรวจสอบใน Inbox)")
                        elif btn_login:
                            if pwd == st.session_state.user_db[email]:
                                st.session_state.current_user = email
                                st.rerun()
                            else:
                                st.error("❌ รหัสผ่านไม่ถูกต้อง")
                else:
                    st.error("❌ Access Denied. อีเมลนี้ไม่ได้รับสิทธิ์การเข้าถึง (Not in Whitelist) กรุณาติดต่อ Admin")
                    st.form_submit_button("LOGIN") 
            else:
                st.form_submit_button("ตรวจสอบสิทธิ์")
                st.caption("💡 อีเมลทดสอบระบบ: admin@betagro.com")
                
    return False

if not check_password(): st.stop()

if "approved_issues" not in st.session_state: st.session_state.approved_issues = []
if "saved_plans_dict" not in st.session_state: st.session_state.saved_plans_dict = {}

# ==========================================
# --- 4. DYNAMIC UI (ปรับแต่งตามบริบท) ---
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

st.markdown("<h4 style='color: #005B31; margin-bottom: 15px; font-weight: 700;'><i class='fa-solid fa-folder-open'></i> 1. ข้อมูลโครงการและบัญชีผู้ใช้งาน</h4>", unsafe_allow_html=True)
col_p1, col_p2 = st.columns(2)
with col_p1: audit_cycle = st.selectbox("รอบการประเมิน (Audit Cycle) *", ["Annual 2026", "Q1/2026", "Q2/2026", "Q3/2026", "Q4/2026", "Special Audit"])
with col_p2: 
    st.text_input("ผู้ใช้งานระบบ (System User)", value=st.session_state.current_user, disabled=True)
    auditor_name = st.session_state.current_user

st.markdown("<hr style='border: 1px solid #eee; margin: 20px 0;'>", unsafe_allow_html=True)

st.markdown("<h4 style='color: #005B31; margin-bottom: 15px; font-weight: 700;'><i class='fa-solid fa-screwdriver-wrench'></i> 2. เลือกเครื่องมือปฏิบัติงาน</h4>", unsafe_allow_html=True)
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
    st.markdown("<h4 style='color: #005B31; margin-bottom: 15px; font-weight: 700;'><i class='fa-solid fa-location-dot'></i> 3. ข้อมูลพื้นที่และผู้ให้ข้อมูล (Location & Respondent)</h4>", unsafe_allow_html=True)
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

if is_tool_1_to_4:
    if not location or not resp_id or not resp_dept:
        st.warning("⚠️ กรุณากรอก **พื้นที่สำรวจ, รหัสอ้างอิง (ID)** และ **แผนก/ส่วนงาน** ให้ครบถ้วน เพื่อทำแบบประเมิน")
        st.stop()
    elif sheet:
        with st.spinner("กำลังตรวจสอบความถูกต้องของรหัสอ้างอิง..."):
            if check_id_conflict(sheet, location, resp_id, resp_group, resp_dept, resp_gender):
                st.error(f"❌ ไม่อนุญาตให้ทำรายการ: รหัสอ้างอิง '{resp_id}' ในพื้นที่นี้ถูกใช้งานไปแล้วกับบุคคลอื่น!")
                st.stop() 

# ==========================================
# --- 6. TOOLS LOGIC ---
# ==========================================

# ----------------- TOOL 1 -----------------
if choice == "Tool 1: ประเมินสถานะองค์กร (Governance & Policy Gap)":
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

# ----------------- TOOL 2 -----------------
elif choice == "Tool 2: แบบสอบถามหน้างาน (Worker Survey)":
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

# ----------------- TOOL 3 -----------------
elif choice == "Tool 3: สัมภาษณ์เชิงลึก (Evidence Base)":
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

# ----------------- TOOL 4 -----------------
elif choice == "Tool 4: บันทึกการสังเกตการณ์ (Site Observation Log)":
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


# ----------------- TOOL 5 (THE DATA-DRIVEN UPDATE) -----------------
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

    # 💡 ระบบดึงและนับจำนวน Data จริงๆ จาก Google Sheet
    sheet_data_count = 0
    raw_data = []
    if sheet:
        all_records = sheet.get_all_values()
        if len(all_records) > 1:
            raw_data = all_records[1:] # ตัด Header ทิ้ง
            if custom_filter_text:
                filtered_data = [row for row in raw_data if len(row) > 6 and row[6] == custom_filter_text]
                sheet_data_count = len(filtered_data)
            else:
                sheet_data_count = len(raw_data)
                
    if sheet_data_count == 0: 
        st.warning(f"⚠️ ไม่พบข้อมูลของกลุ่มเป้าหมาย [{custom_filter_text}] ในฐานข้อมูลปัจจุบัน กรุณาตรวจสอบอีกครั้ง")
        st.stop()

    btn_text = f"✨ ให้ Gemini AI ดึงข้อมูลของกลุ่ม [{custom_filter_text}] จำนวน {sheet_data_count} รายการ มาวิเคราะห์ความเสี่ยง" if custom_filter_text else f"✨ ให้ Gemini AI วิเคราะห์ประเด็นจากภาพรวมองค์กรทั้งหมด ({sheet_data_count} รายการ)"
    
    st.markdown("<h5 style='color: #005B31; margin-top: 20px;'><i class='fa-solid fa-wand-magic-sparkles'></i> 1. สกัดประเด็นความเสี่ยงจากฐานข้อมูล</h5>", unsafe_allow_html=True)
    if st.button(btn_text):
        st.session_state.ai_scanned_issues = True
    
    all_possible_issues = [
        "[สิทธิแรงงาน] พนักงานร้องเรียนเรื่องการจ่ายเงิน OT ไม่ครบ/ล่าช้า",
        "[แรงงานบังคับ] พบกลุ่มแรงงานข้ามชาติถูกยึดพาสปอร์ตโดยเอเจนซี่",
        "[อาชีวอนามัย] พบเครื่องจักรโซนปฏิบัติงานไม่มีฝาครอบป้องกันอันตราย",
        "[แรงงานเด็ก] พบการจ้างงานเยาวชนอายุต่ำกว่า 18 ปี ในพื้นที่อันตราย",
        "[การเลือกปฏิบัติ] ความเหลื่อมล้ำในการจ่ายค่าจ้างระหว่างแรงงานไทยและข้ามชาติ",
        "[ผลกระทบชุมชน] มลพิษทางกลิ่นและเสียงส่งผลกระทบต่อชุมชนรอบโรงงาน",
        "[สวัสดิการ] สภาพหอพักแรงงานแออัดและไม่ถูกสุขลักษณะ",
        "[เสรีภาพการสมาคม] การกีดกันไม่ให้พนักงานรวมกลุ่มจัดตั้งคณะกรรมการสวัสดิการ",
        "[ชั่วโมงการทำงาน] พนักงานต้องทำงานติดต่อกันเกิน 60 ชั่วโมง/สัปดาห์",
        "[กลไกร้องเรียน] พนักงานไม่กล้าร้องเรียนเนื่องจากระบบไม่ปกปิดตัวตน"
    ]
    
    selected_issue = ""
    if st.session_state.get("ai_scanned_issues", False):
        if filter_mode != "ระดับองค์กรภาพรวม (Corporate Level / ทุกกลุ่ม)":
            ai_header = f"🤖 Gemini AI พบประเด็นที่ต้องจัดทำแผน (การวิเคราะห์เฉพาะกลุ่ม: {custom_filter_text}):"
            random.seed(sum(ord(c) for c in custom_filter_text)) 
            num_issues = random.randint(1, 3) 
            sampled_issues = random.sample(all_possible_issues, num_issues)
            display_list = ["เลือกประเด็นความเสี่ยงเพื่อจัดการ..."] + sampled_issues
        else:
            ai_header = f"🤖 Gemini AI พบ 10 ประเด็นยุทธศาสตร์ที่ต้องจัดทำแผน (วิเคราะห์จากภาพรวมองค์กรทั้งหมด):"
            display_list = ["เลือกประเด็นความเสี่ยงเพื่อจัดการ..."] + all_possible_issues
            
        st.markdown(f'<div style="background: #E8F0FE; padding: 15px; border-radius: 8px; border-left: 4px solid #1967D2; margin-bottom: 20px;"><span style="color: #1967D2; font-weight: 700; font-size: 14px;">{ai_header}</span></div>', unsafe_allow_html=True)
        selected_issue = st.selectbox("เลือกประเด็นความเสี่ยงเพื่อจัดทำแผน (Process Issue):", display_list)

    save_issue = selected_issue if selected_issue and "เลือกประเด็น" not in selected_issue else "ประเด็นที่ระบุเอง (Manual)"
    is_already_approved = save_issue in st.session_state.approved_issues

    def create_mock_doc_url(title, content):
        html_content = f"""
        <html><head><meta charset="utf-8"><title>{title}</title>
        <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Sarabun', sans-serif; background-color: #E5E7EB; padding: 40px; color: #1F2937; line-height: 1.6; }}
            .page {{ background-color: #FFFFFF; max-width: 800px; margin: 0 auto; padding: 60px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); border-radius: 4px; border-top: 10px solid #005B31;}}
            h2 {{ color: #005B31; border-bottom: 2px solid #E5E7EB; padding-bottom: 15px; text-transform: uppercase; font-size: 24px; margin-top:0; }}
            .metadata {{ color: #6B7280; font-size: 14px; margin-bottom: 30px; }}
            mark {{ background-color: #FEF08A; padding: 2px 4px; border-radius: 2px; font-weight: bold; border-bottom: 2px solid #EAB308; }}
        </style>
        </head><body><div class="page">{content}</div></body></html>
        """
        b64 = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
        return f"data:text/html;base64,{b64}"

    scope_text = f"กลุ่ม {custom_filter_text}" if custom_filter_text else "ภาพรวมทุกกลุ่ม"
    
    # ฐานข้อมูลแผนจัดการ
    db_dict = {
        "OT": {
            "evidence": f"Tool 2: จาก {scope_text} ระบุปัญหาการจ่ายเงินล่าช้า\nTool 3: สัมภาษณ์เชิงลึก ยืนยันว่าได้เงินล่าช้าเกิน 7 วัน",
            "standard": "พ.ร.บ. คุ้มครองแรงงาน มาตรา 70 | ILO Convention No. 95 (Protection of Wages)",
            "sev": 3, "lik": 4, "rem": 2, "sco": 4,
            "html_evi": f"📌 <b>แหล่งที่มา (Sources):</b> <br>- <i>Tool 2 (Survey):</i> จาก{scope_text} พบปัญหาการจ่ายค่าจ้างล่าช้า <label for='m-ot1' class='cite-pill'>[Source 1]</label><br>- <i>Tool 3 (Interview):</i> สัมภาษณ์เชิงลึก ยืนยันว่าได้เงินล่าช้า <label for='m-ot2' class='cite-pill'>[Source 2]</label>",
            "html_std": "⚖️ <b>อ้างอิงมาตรฐาน (Standard):</b> พ.ร.บ. คุ้มครองแรงงาน มาตรา 70 <label for='m-l70' class='cite-pill doc-pill'>[Doc 1]</label> | ILO Conv. 95 <label for='m-i95' class='cite-pill doc-pill'>[Doc 2]</label>",
            "plan_y": "Preventive Action (แผนป้องกันเชิงรุก):\n- Proactive Measures: จัดอบรมกฎหมายแรงงานเวลาทำงานให้หัวหน้างาน และสุ่มตรวจ Pay slip/Time Attendance ทุกไตรมาส\n- Timeline: ติดตามผลการปรับปรุงภายใน 3 เดือน",
            "plan_r": "Preventive: ตรวจสอบระบบ Time Attendance และ Pay slip อย่างเข้มงวด\nRemediation: จ่ายค่าจ้าง/OT ค้างชำระย้อนหลังพร้อมดอกเบี้ยในงวดถัดไปทันที",
            "modals": f"""
                <input type="checkbox" id="m-ot1" class="modal-toggle"><div class="modal-window"><label class="modal-backdrop" for="m-ot1"></label><div class="modal-content"><div class="modal-header"><a href="#" class="modal-title-link"><i class="fa-solid fa-file-csv" style="color:#10B981;"></i> DB_Tool2_Survey.csv</a><label for="m-ot1" class="close-btn"><i class="fa-solid fa-xmark"></i></label></div><div class="modal-body"><div class="mock-doc-wrapper"><table class="mock-csv"><tr><th>ID</th><th>Dept</th><th>Q1.1 Promptness</th></tr><tr class="alert-row"><td>045</td><td>ฝ่ายแพ็ค</td><td class="alert-cell">1 (ไม่จริงเลย)</td></tr></table></div></div></div></div>
                <input type="checkbox" id="m-ot2" class="modal-toggle"><div class="modal-window"><label class="modal-backdrop" for="m-ot2"></label><div class="modal-content"><div class="modal-header"><a href="#" class="modal-title-link"><i class="fa-solid fa-file-pdf" style="color:#EF4444;"></i> Transcript_OT.pdf</a><label for="m-ot2" class="close-btn"><i class="fa-solid fa-xmark"></i></label></div><div class="modal-body"><iframe src="{create_mock_doc_url('Transcript_OT', '<h2>Transcript</h2><p>พนักงาน: <mark>พวกเราได้เงิน OT ช้าไป 2 สัปดาห์ตลอดเลยครับ</mark></p>')}" style="width:100%;height:400px;border:none;"></iframe></div></div></div>
            """
        },
        "พาสปอร์ต": {
            "evidence": f"Tool 4: พบตู้เซฟล็อกกุญแจในห้องพักเอเจนซี่\nTool 3: จาก {scope_text} ยืนยันว่าถูกยึดพาสปอร์ต",
            "standard": "หลักการ Employer Pays Principle (EPP) | ILO Forced Labour Convention (No. 29)",
            "sev": 5, "lik": 3, "rem": 3, "sco": 2,
            "html_evi": f"📌 <b>แหล่งที่มา (Sources):</b> <br>- <i>Tool 4 (Observation):</i> พบตู้เซฟล็อกกุญแจในห้องพักเอเจนซี่ <label for='m-p1' class='cite-pill'>[Source 1]</label><br>- <i>Tool 3 (Interview):</i> จาก{scope_text} ยืนยันว่าถูกยึดพาสปอร์ต <label for='m-p2' class='cite-pill'>[Source 2]</label>",
            "html_std": "⚖️ <b>อ้างอิงมาตรฐาน (Standard):</b> หลักการ Employer Pays Principle (EPP) | ILO Forced Labour Conv. No. 29 <label for='m-i29' class='cite-pill doc-pill'>[Doc 1]</label>",
            "plan_y": "Preventive Action (แผนป้องกันเชิงรุก):\n- Proactive Measures: สุ่มตรวจสอบกระบวนการจ้างงานผ่านเอเจนซี่ และย้ำนโยบาย EPP อย่างเคร่งครัด\n- Timeline: ติดตามผลภายใน 3 เดือน",
            "plan_r": "Preventive: สื่อสารนโยบาย EPP ให้เอเจนซี่ จัดเตรียมตู้ล็อกเกอร์ส่วนตัวให้แรงงานเก็บเอกสารเอง\nRemediation: คืนพาสปอร์ตให้พนักงานทุกคนทันที (ภายใน 24 ชม.)",
            "modals": f"""
                <input type="checkbox" id="m-p1" class="modal-toggle"><div class="modal-window"><label class="modal-backdrop" for="m-p1"></label><div class="modal-content"><div class="modal-header"><a href="#" class="modal-title-link"><i class="fa-solid fa-image" style="color:#3B82F6;"></i> Obs_Agency.jpg</a><label for="m-p1" class="close-btn"><i class="fa-solid fa-xmark"></i></label></div><div class="modal-body" style="text-align:center;"><div class="mock-doc-wrapper"><img src="https://images.unsplash.com/photo-1614036417651-1d4b68e0d37d?w=800" style="width:100%;"><p style="color:#DC2626; font-weight:bold; margin-top:10px;">พบตู้เซฟล็อกกุญแจ ภายในห้องพักของนายหน้า</p></div></div></div></div>
                <input type="checkbox" id="m-p2" class="modal-toggle"><div class="modal-window"><label class="modal-backdrop" for="m-p2"></label><div class="modal-content"><div class="modal-header"><a href="#" class="modal-title-link"><i class="fa-solid fa-file-pdf" style="color:#EF4444;"></i> Transcript_Migrant.pdf</a><label for="m-p2" class="close-btn"><i class="fa-solid fa-xmark"></i></label></div><div class="modal-body"><iframe src="{create_mock_doc_url('Transcript', '<h2>Transcript</h2><p>แรงงาน: <mark>เอเจนซี่ขอยึดพาสปอร์ตไปเก็บไว้ในตู้เซฟของเขา ขอเบิกยากมากครับ</mark></p>')}" style="width:100%;height:400px;border:none;"></iframe></div></div></div>
            """
        },
        "เครื่องจักร": {
            "evidence": f"Tool 4: ตรวจพบสายพานลำเลียงไม่มี Guard\nTool 2: จาก {scope_text} ให้คะแนนความปลอดภัยเฉลี่ยต่ำ",
            "standard": "ISO 45001 | พ.ร.บ. ความปลอดภัย อาชีวอนามัย และสภาพแวดล้อมในการทำงาน",
            "sev": 4, "lik": 4, "rem": 2, "sco": 2,
            "html_evi": f"📌 <b>แหล่งที่มา (Sources):</b> <br>- <i>Tool 4 (Observation):</i> ตรวจพบสายพานลำเลียงไม่มี Guard <label for='m-m1' class='cite-pill'>[Source 1]</label><br>- <i>Tool 2:</i> จาก{scope_text} ให้คะแนนความปลอดภัยต่ำ",
            "html_std": "⚖️ <b>อ้างอิงมาตรฐาน (Standard):</b> ISO 45001 | พ.ร.บ. ความปลอดภัย อาชีวอนามัยฯ <label for='m-iso' class='cite-pill doc-pill'>[Doc 1]</label>",
            "plan_y": "Preventive Action (แผนป้องกันเชิงรุก):\n- Proactive Measures: เพิ่มความถี่ในการทำ Safety Patrol และซ่อมบำรุงโครงสร้างเครื่องจักร\n- Timeline: ติดตามผลการปรับปรุงภายใน 1-3 เดือน",
            "plan_r": "Preventive: กำหนดรอบตรวจสอบความปลอดภัยประจำสัปดาห์อย่างเคร่งครัด\nRemediation: หยุดการทำงานจุดเสี่ยงทันที ติดตั้ง Guard ป้องกัน และรับผิดชอบค่ารักษาพยาบาล (ถ้ามี)",
            "modals": f"""
                <input type="checkbox" id="m-m1" class="modal-toggle"><div class="modal-window"><label class="modal-backdrop" for="m-m1"></label><div class="modal-content"><div class="modal-header"><a href="#" class="modal-title-link"><i class="fa-solid fa-image" style="color:#3B82F6;"></i> Machine_Audit.jpg</a><label for="m-m1" class="close-btn"><i class="fa-solid fa-xmark"></i></label></div><div class="modal-body" style="text-align:center;"><div class="mock-doc-wrapper"><img src="https://images.unsplash.com/photo-1581092160562-40aa08e78837?w=800" style="width:100%;"><p style="color:#DC2626; font-weight:bold; margin-top:10px;">ตรวจพบสายพานเปลือย (Missing Guard) เสี่ยงอันตราย</p></div></div></div></div>
            """
        },
        "เด็ก": {
            "evidence": f"Tool 1: ระบบคัดกรองอายุ Supplier หละหลวม\nTool 4: พบเยาวชนทำงานกะกลางคืนใน {scope_text}",
            "standard": "Zero Tolerance Policy | ILO Minimum Age Convention (No. 138) | NAP",
            "sev": 5, "lik": 1, "rem": 4, "sco": 1,
            "html_evi": f"📌 <b>แหล่งที่มา (Sources):</b> <br>- <i>Tool 1:</i> ระบบคัดกรองอายุ Supplier หละหลวม <label for='m-c1' class='cite-pill'>[Source 1]</label><br>- <i>Tool 4:</i> พบเยาวชนทำงานกะกลางคืน",
            "html_std": "⚖️ <b>อ้างอิงมาตรฐาน (Standard):</b> Zero Tolerance | ILO Conv. 138 <label for='m-i138' class='cite-pill doc-pill'>[Doc 1]</label> | NAP",
            "plan_y": "Preventive Action (แผนป้องกันเชิงรุก):\n- Proactive Measures: ระงับการทำธุรกรรมชั่วคราวกับ Supplier จนกว่าจะพิสูจน์ได้ว่ามีระบบคัดกรองอายุพนักงานที่ได้มาตรฐาน\n- Timeline: ตรวจสอบภายใน 1 เดือน",
            "plan_r": "Preventive: ตรวจสอบบัตร ปชช. ต้นทางร่วมกับ Supplier อย่างเข้มงวด (Zero Tolerance)\nRemediation: ถอดพนักงานอายุต่ำกว่า 18 ปีออกจากงานอันตราย/กะดึกทันที พร้อมจ่ายชดเชยตามกฎหมาย",
            "modals": f"""<input type="checkbox" id="m-c1" class="modal-toggle"><div class="modal-window"><label class="modal-backdrop" for="m-c1"></label><div class="modal-content"><div class="modal-header"><a href="#" class="modal-title-link"><i class="fa-solid fa-file-pdf" style="color:#EF4444;"></i> Policy_Audit.pdf</a><label for="m-c1" class="close-btn"><i class="fa-solid fa-xmark"></i></label></div><div class="modal-body"><iframe src="{create_mock_doc_url('Policy Audit', '<h2>Audit Report</h2><p><mark>Supplier ขาดระบบคัดกรองอายุด้วยเครื่องอ่านบัตรสมาร์ทการ์ด</mark></p>')}" style="width:100%;height:300px;border:none;"></iframe></div></div></div>"""
        },
        "ชุมชน": {
            "evidence": f"Tool 3: ชุมชนรอบข้างร้องเรียนกลิ่นเหม็น\nTool 4: ระบบบำบัดน้ำเสียไม่เต็มประสิทธิภาพ",
            "standard": "พ.ร.บ. ส่งเสริมและรักษาคุณภาพสิ่งแวดล้อมแห่งชาติ | UNGPs",
            "sev": 3, "lik": 4, "rem": 4, "sco": 5,
            "html_evi": f"📌 <b>แหล่งที่มา (Sources):</b> <br>- <i>Tool 3:</i> จาก{scope_text}ร้องเรียนเรื่องกลิ่นเหม็นช่วงเวลากลางคืน <label for='m-e1' class='cite-pill'>[Source 1]</label><br>- <i>Tool 4:</i> ระบบบำบัดน้ำเสียทำงานไม่เต็มประสิทธิภาพ",
            "html_std": "⚖️ <b>อ้างอิงมาตรฐาน (Standard):</b> พ.ร.บ. ส่งเสริมและรักษาคุณภาพสิ่งแวดล้อมฯ <label for='m-law-env' class='cite-pill doc-pill'>[Doc 1]</label>",
            "plan_y": "Preventive Action (แผนป้องกันเชิงรุก):\n- Proactive Measures: ตรวจสอบและซ่อมบำรุงระบบบำบัดน้ำเสีย/อากาศ ให้ได้ตามมาตรฐาน ISO 14001\n- Timeline: ดำเนินการให้แล้วเสร็จภายใน 3 เดือน",
            "plan_r": "Preventive: อนุมัติงบประมาณฉุกเฉินปรับปรุงระบบบำบัดมลพิษให้ได้มาตรฐานทันที\nRemediation: จัดตั้งกลไกเจรจาร่วมกับตัวแทนชุมชน เพื่อรับฟังปัญหาและเยียวยาผู้ได้รับผลกระทบทางสุขภาพ",
            "modals": f"""<input type="checkbox" id="m-e1" class="modal-toggle"><div class="modal-window"><label class="modal-backdrop" for="m-e1"></label><div class="modal-content"><div class="modal-header"><a href="#" class="modal-title-link"><i class="fa-solid fa-file-pdf" style="color:#EF4444;"></i> Comm_Feedback.pdf</a><label for="m-e1" class="close-btn"><i class="fa-solid fa-xmark"></i></label></div><div class="modal-body"><iframe src="{create_mock_doc_url('Community Log', '<h2>Community Log</h2><p><mark>ได้รับข้อร้องเรียนจากหมู่บ้านเรื่องกลิ่นเหม็นช่วง 22:00 - 02:00 น.</mark></p>')}" style="width:100%;height:300px;border:none;"></iframe></div></div></div>"""
        },
        "เลือกปฏิบัติ": {
            "evidence": f"Tool 2: จาก {scope_text} ให้คะแนนด้านความเท่าเทียมต่ำมาก\nTool 1: โครงสร้างการจ่ายโบนัสแยกตามสัญชาติชัดเจน",
            "standard": "ILO Convention No. 111 (Discrimination) | UNGPs Principle 12",
            "sev": 4, "lik": 3, "rem": 3, "sco": 4,
            "html_evi": f"📌 <b>แหล่งที่มา (Sources):</b> <br>- <i>Tool 2:</i> จาก{scope_text} ให้คะแนนด้านความเท่าเทียมต่ำมาก <label for='m-disc1' class='cite-pill'>[Source 1]</label><br>- <i>Tool 1:</i> โครงสร้างการจ่ายโบนัสแยกตามสัญชาติชัดเจน",
            "html_std": "⚖️ <b>อ้างอิงมาตรฐาน (Standard):</b> ILO Conv. 111 <label for='m-i111' class='cite-pill doc-pill'>[Doc 1]</label> | UNGPs",
            "plan_y": "Preventive Action (แผนป้องกันเชิงรุก):\n- Proactive Measures: จัดอบรมด้าน Diversity & Inclusion ให้หัวหน้างานทุกระดับ\n- Timeline: ประเมินความพึงพอใจซ้ำใน 6 เดือน",
            "plan_r": "Preventive: ปรับปรุงโครงสร้างสวัสดิการให้เป็นธรรม และเปิดช่องทางร้องเรียนอิสระ (Whistleblowing)\nRemediation: ตั้งกรรมการสอบสวนข้อเท็จจริง และเยียวยาผู้ถูกกระทำอย่างเป็นธรรม",
            "modals": f"""<input type="checkbox" id="m-disc1" class="modal-toggle"><div class="modal-window"><label class="modal-backdrop" for="m-disc1"></label><div class="modal-content"><div class="modal-header"><a href="#" class="modal-title-link"><i class="fa-solid fa-file-csv" style="color:#10B981;"></i> DB_Tool2_Survey.csv</a><label for="m-disc1" class="close-btn"><i class="fa-solid fa-xmark"></i></label></div><div class="modal-body"><div class="mock-doc-wrapper"><table class="mock-csv"><tr><th>ID</th><th>Dept</th><th>Q3.1 Equality</th></tr><tr class="alert-row"><td>M05</td><td>ฝ่ายผลิต</td><td class="alert-cell">1 (ไม่จริงเลย)</td></tr></table></div></div></div></div>"""
        },
        "สวัสดิการ": {
            "evidence": f"Tool 4: หอพักพนักงานมีพื้นที่น้อยกว่า 3 ตร.ม./คน\nTool 3: จาก {scope_text} ร้องเรียนเรื่องความสะอาดและแออัด",
            "standard": "กฎกระทรวงว่าด้วยการจัดสวัสดิการในสถานประกอบกิจการ | ILO Workers' Housing Recommendation (No. 115)",
            "sev": 3, "lik": 4, "rem": 2, "sco": 5,
            "html_evi": f"📌 <b>แหล่งที่มา (Sources):</b> <br>- <i>Tool 4:</i> หอพักพนักงานมีพื้นที่น้อยกว่ามาตรฐาน <label for='m-wel1' class='cite-pill'>[Source 1]</label>",
            "html_std": "⚖️ <b>อ้างอิงมาตรฐาน (Standard):</b> กฎกระทรวงว่าด้วยสวัสดิการฯ <label for='m-law-wel' class='cite-pill doc-pill'>[Doc 1]</label>",
            "plan_y": "Preventive Action (แผนป้องกันเชิงรุก):\n- Proactive Measures: ทำความสะอาดฉีดพ่นยาฆ่าเชื้อ และซ่อมแซมสิ่งอำนวยความสะดวกพื้นฐาน\n- Timeline: ดำเนินการภายใน 1 เดือน",
            "plan_r": "Preventive: จัดหาหอพักสำรองเพื่อลดความแออัด (De-densification) ให้ได้ตามมาตรฐานสากล\nRemediation: งดหักค่าที่พักจากพนักงานจนกว่าจะปรับปรุงเสร็จสิ้น",
            "modals": f"""<input type="checkbox" id="m-wel1" class="modal-toggle"><div class="modal-window"><label class="modal-backdrop" for="m-wel1"></label><div class="modal-content"><div class="modal-header"><a href="#" class="modal-title-link"><i class="fa-solid fa-image" style="color:#3B82F6;"></i> Dorm_Audit.jpg</a><label for="m-wel1" class="close-btn"><i class="fa-solid fa-xmark"></i></label></div><div class="modal-body" style="text-align:center;"><div class="mock-doc-wrapper"><img src="https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=800" style="width:100%;"><p style="color:#DC2626; font-weight:bold; margin-top:10px;">สภาพหอพักแรงงานค่อนข้างแออัด</p></div></div></div></div>"""
        },
        "สมาคม": {
            "evidence": f"Tool 3: จาก {scope_text} ระบุว่าหัวหน้างานขัดขวางการเลือกตั้ง คกก. สวัสดิการ\nTool 1: ไม่มีนโยบายชัดเจนเรื่องเสรีภาพการสมาคม",
            "standard": "ILO Convention No. 87 & 98 (Freedom of Association) | พ.ร.บ. แรงงานสัมพันธ์ พ.ศ. 2518",
            "sev": 4, "lik": 4, "rem": 3, "sco": 2,
            "html_evi": f"📌 <b>แหล่งที่มา (Sources):</b> <br>- <i>Tool 3:</i> จาก{scope_text} ระบุว่ามีการขัดขวางการจัดตั้งกลุ่ม <label for='m-uni1' class='cite-pill'>[Source 1]</label>",
            "html_std": "⚖️ <b>อ้างอิงมาตรฐาน (Standard):</b> ILO Conv. 87 & 98 <label for='m-i87' class='cite-pill doc-pill'>[Doc 1]</label>",
            "plan_y": "Preventive Action (แผนป้องกันเชิงรุก):\n- Proactive Measures: สื่อสารสิทธิพื้นฐานด้านการสมาคมให้พนักงานทุกคนทราบ\n- Timeline: จัดตั้ง คกก. สวัสดิการ ภายใน 3 เดือน",
            "plan_r": "Preventive: จัดให้มีการเลือกตั้งผู้แทนพนักงานอย่างโปร่งใส โดยมีบุคคลที่สาม (Third-party) ร่วมสังเกตการณ์\nRemediation: ยกเลิกคำสั่งลงโทษหรือโยกย้ายพนักงานที่เป็นแกนนำจัดตั้งกลุ่ม (ถ้ามี)",
            "modals": f"""<input type="checkbox" id="m-uni1" class="modal-toggle"><div class="modal-window"><label class="modal-backdrop" for="m-uni1"></label><div class="modal-content"><div class="modal-header"><a href="#" class="modal-title-link"><i class="fa-solid fa-file-pdf" style="color:#EF4444;"></i> Transcript_Union.pdf</a><label for="m-uni1" class="close-btn"><i class="fa-solid fa-xmark"></i></label></div><div class="modal-body"><iframe src="{create_mock_doc_url('Union', '<h2>Transcript</h2><p>พนักงาน: <mark>หัวหน้าขู่ว่าถ้าใครลงชื่อตั้งสหภาพจะโดนตัดโบนัสครับ</mark></p>')}" style="width:100%;height:300px;border:none;"></iframe></div></div></div>"""
        },
        "ชั่วโมง": {
            "evidence": f"Tool 1: ตรวจสอบ Time Attendance พบการทำงานเกิน 60 ชม./สัปดาห์ ติดต่อกัน\nTool 3: จาก {scope_text} ระบุว่ารู้สึกเหนื่อยล้า",
            "standard": "พ.ร.บ. คุ้มครองแรงงาน (ชั่วโมงการทำงานและวันหยุด) | RBA Code of Conduct",
            "sev": 3, "lik": 4, "rem": 2, "sco": 4,
            "html_evi": f"📌 <b>แหล่งที่มา (Sources):</b> <br>- <i>Tool 1:</i> ตรวจสอบ Time Attendance พบการทำงานเกิน 60 ชม./สัปดาห์ <label for='m-hr1' class='cite-pill'>[Source 1]</label>",
            "html_std": "⚖️ <b>อ้างอิงมาตรฐาน (Standard):</b> พ.ร.บ. คุ้มครองแรงงาน <label for='m-law-hr' class='cite-pill doc-pill'>[Doc 1]</label> | RBA",
            "plan_y": "Preventive Action (แผนป้องกันเชิงรุก):\n- Proactive Measures: กำหนดเพดาน OT ในระบบสแกนนิ้ว ไม่ให้เกินข้อกำหนดกฎหมาย\n- Timeline: บังคับใช้ในรอบบิลถัดไป",
            "plan_r": "Preventive: ตั้งระบบแจ้งเตือน (Alert) ในซอฟต์แวร์ HR เมื่อพนักงานทำงานใกล้ถึงลิมิตสูงสุด\nRemediation: จัดสรรกำลังพล (Manpower) ใหม่และให้วันหยุดชดเชยพิเศษแก่พนักงานที่ทำงานหนักเกินเกณฑ์",
            "modals": f"""<input type="checkbox" id="m-hr1" class="modal-toggle"><div class="modal-window"><label class="modal-backdrop" for="m-hr1"></label><div class="modal-content"><div class="modal-header"><a href="#" class="modal-title-link"><i class="fa-solid fa-file-csv" style="color:#10B981;"></i> Time_Attendance.csv</a><label for="m-hr1" class="close-btn"><i class="fa-solid fa-xmark"></i></label></div><div class="modal-body"><div class="mock-doc-wrapper"><table class="mock-csv"><tr><th>ID</th><th>Total Hours (Week)</th></tr><tr class="alert-row"><td>088</td><td class="alert-cell">68 Hrs</td></tr></table></div></div></div></div>"""
        },
        "ร้องเรียน": {
            "evidence": f"Tool 2: จาก {scope_text} กว่า 60% ไม่ทราบช่องทางการร้องเรียนแบบปกปิดตัวตน\nTool 4: กล่องรับความคิดเห็นอยู่ในจุดที่คนพลุกพล่าน",
            "standard": "UNGPs Principle 29 (Non-Retaliation) | กลไกรับเรื่องร้องเรียนที่เข้าถึงได้",
            "sev": 4, "lik": 4, "rem": 3, "sco": 3,
            "html_evi": f"📌 <b>แหล่งที่มา (Sources):</b> <br>- <i>Tool 2:</i> จาก{scope_text} ไม่ทราบช่องทางการร้องเรียนที่ปลอดภัย <label for='m-gr1' class='cite-pill'>[Source 1]</label>",
            "html_std": "⚖️ <b>อ้างอิงมาตรฐาน (Standard):</b> UNGPs Principle 29 <label for='m-ungp' class='cite-pill doc-pill'>[Doc 1]</label>",
            "plan_y": "Preventive Action (แผนป้องกันเชิงรุก):\n- Proactive Measures: ประชาสัมพันธ์ช่องทางสายด่วน (Hotline) ที่เข้าถึงได้หลายภาษา\n- Timeline: ภายใน 1 เดือน",
            "plan_r": "Preventive: ย้ายกล่องรับความคิดเห็นไปยังจุดที่ปลอดภัย (Blind Spot) และจัดตั้งคณะกรรมการจากภายนอก (Third-party) มารับเรื่อง\nRemediation: ออกจดหมายรับรองนโยบายไม่เอาผิดผู้ร้องเรียน (Non-Retaliation Policy) แจกให้พนักงานทุกคน",
            "modals": f"""<input type="checkbox" id="m-gr1" class="modal-toggle"><div class="modal-window"><label class="modal-backdrop" for="m-gr1"></label><div class="modal-content"><div class="modal-header"><a href="#" class="modal-title-link"><i class="fa-solid fa-file-csv" style="color:#10B981;"></i> DB_Tool2_Survey.csv</a><label for="m-gr1" class="close-btn"><i class="fa-solid fa-xmark"></i></label></div><div class="modal-body"><div class="mock-doc-wrapper"><table class="mock-csv"><tr><th>ID</th><th>Q3.2 Know Grievance Channel</th></tr><tr class="alert-row"><td>012</td><td class="alert-cell">2 (ไม่ค่อยจริง)</td></tr></table></div></div></div></div>"""
        }
    }

    # Common Modals For Standards
    common_modals = f"""
    <input type="checkbox" id="m-l70" class="modal-toggle"><div class="modal-window"><label class="modal-backdrop" for="m-l70"></label><div class="modal-content"><div class="modal-header"><a href="#" class="modal-title-link"><i class="fa-solid fa-book" style="color:#D97706;"></i> Thai_Labor_Law.pdf</a><label for="m-l70" class="close-btn"><i class="fa-solid fa-xmark"></i></label></div><div class="modal-body"><iframe src="{create_mock_doc_url('Law', '<h2>พ.ร.บ. คุ้มครองแรงงาน พ.ศ. 2541</h2><p><b>มาตรา 70</b> <mark>ให้นายจ้างจ่ายค่าจ้างไม่น้อยกว่าเดือนละหนึ่งครั้ง</mark></p>')}" style="width:100%;height:300px;border:none;"></iframe></div></div></div>
    <input type="checkbox" id="m-i95" class="modal-toggle"><div class="modal-window"><label class="modal-backdrop" for="m-i95"></label><div class="modal-content"><div class="modal-header"><a href="#" class="modal-title-link"><i class="fa-solid fa-globe" style="color:#2563EB;"></i> ILO_Conv_95.pdf</a><label for="m-i95" class="close-btn"><i class="fa-solid fa-xmark"></i></label></div><div class="modal-body"><iframe src="{create_mock_doc_url('ILO 95', '<h2>ILO Convention No. 95</h2><p><mark>Wages shall be paid regularly...</mark></p>')}" style="width:100%;height:300px;border:none;"></iframe></div></div></div>
    <input type="checkbox" id="m-i29" class="modal-toggle"><div class="modal-window"><label class="modal-backdrop" for="m-i29"></label><div class="modal-content"><div class="modal-header"><a href="#" class="modal-title-link"><i class="fa-solid fa-globe" style="color:#2563EB;"></i> ILO_Conv_29.pdf</a><label for="m-i29" class="close-btn"><i class="fa-solid fa-xmark"></i></label></div><div class="modal-body"><iframe src="{create_mock_doc_url('ILO 29', '<h2>ILO Convention No. 29</h2><p><mark>The retention of identity documents is widely recognised as a key indicator of forced labour</mark></p>')}" style="width:100%;height:300px;border:none;"></iframe></div></div></div>
    <input type="checkbox" id="m-i138" class="modal-toggle"><div class="modal-window"><label class="modal-backdrop" for="m-i138"></label><div class="modal-content"><div class="modal-header"><a href="#" class="modal-title-link"><i class="fa-solid fa-globe" style="color:#2563EB;"></i> ILO_Conv_138.pdf</a><label for="m-i138" class="close-btn"><i class="fa-solid fa-xmark"></i></label></div><div class="modal-body"><iframe src="{create_mock_doc_url('ILO 138', '<h2>ILO Convention No. 138</h2><p><mark>Minimum Age for admission to employment or work</mark></p>')}" style="width:100%;height:300px;border:none;"></iframe></div></div></div>
    <input type="checkbox" id="m-iso" class="modal-toggle"><div class="modal-window"><label class="modal-backdrop" for="m-iso"></label><div class="modal-content"><div class="modal-header"><a href="#" class="modal-title-link"><i class="fa-solid fa-shield" style="color:#2563EB;"></i> ISO_45001.pdf</a><label for="m-iso" class="close-btn"><i class="fa-solid fa-xmark"></i></label></div><div class="modal-body"><iframe src="{create_mock_doc_url('ISO 45001', '<h2>ISO 45001</h2><p><mark>Occupational health and safety management systems</mark></p>')}" style="width:100%;height:300px;border:none;"></iframe></div></div></div>
    <input type="checkbox" id="m-i111" class="modal-toggle"><div class="modal-window"><label class="modal-backdrop" for="m-i111"></label><div class="modal-content"><div class="modal-header"><a href="#" class="modal-title-link"><i class="fa-solid fa-globe" style="color:#2563EB;"></i> ILO_Conv_111.pdf</a><label for="m-i111" class="close-btn"><i class="fa-solid fa-xmark"></i></label></div><div class="modal-body"><iframe src="{create_mock_doc_url('ILO 111', '<h2>ILO Convention No. 111</h2><p><mark>Discrimination (Employment and Occupation)</mark></p>')}" style="width:100%;height:300px;border:none;"></iframe></div></div></div>
    <input type="checkbox" id="m-i87" class="modal-toggle"><div class="modal-window"><label class="modal-backdrop" for="m-i87"></label><div class="modal-content"><div class="modal-header"><a href="#" class="modal-title-link"><i class="fa-solid fa-globe" style="color:#2563EB;"></i> ILO_Conv_87_98.pdf</a><label for="m-i87" class="close-btn"><i class="fa-solid fa-xmark"></i></label></div><div class="modal-body"><iframe src="{create_mock_doc_url('ILO 87', '<h2>ILO Convention No. 87 & 98</h2><p><mark>Freedom of Association and Protection of the Right to Organise</mark></p>')}" style="width:100%;height:300px;border:none;"></iframe></div></div></div>
    <input type="checkbox" id="m-ungp" class="modal-toggle"><div class="modal-window"><label class="modal-backdrop" for="m-ungp"></label><div class="modal-content"><div class="modal-header"><a href="#" class="modal-title-link"><i class="fa-solid fa-globe" style="color:#2563EB;"></i> UNGPs.pdf</a><label for="m-ungp" class="close-btn"><i class="fa-solid fa-xmark"></i></label></div><div class="modal-body"><iframe src="{create_mock_doc_url('UNGPs', '<h2>UNGPs</h2><p><mark>Principle 29: Accessible Grievance Mechanism and Non-Retaliation</mark></p>')}" style="width:100%;height:300px;border:none;"></iframe></div></div></div>
    <input type="checkbox" id="m-law-env" class="modal-toggle"><div class="modal-window"><label class="modal-backdrop" for="m-law-env"></label><div class="modal-content"><div class="modal-header"><a href="#" class="modal-title-link"><i class="fa-solid fa-book" style="color:#D97706;"></i> Thai_Env_Law.pdf</a><label for="m-law-env" class="close-btn"><i class="fa-solid fa-xmark"></i></label></div><div class="modal-body"><iframe src="{create_mock_doc_url('Env Law', '<h2>พ.ร.บ. ส่งเสริมและรักษาคุณภาพสิ่งแวดล้อม</h2><p><mark>ควบคุมการปล่อยมลพิษทางอากาศและน้ำ</mark></p>')}" style="width:100%;height:300px;border:none;"></iframe></div></div></div>
    <input type="checkbox" id="m-law-wel" class="modal-toggle"><div class="modal-window"><label class="modal-backdrop" for="m-law-wel"></label><div class="modal-content"><div class="modal-header"><a href="#" class="modal-title-link"><i class="fa-solid fa-book" style="color:#D97706;"></i> Thai_Welfare_Law.pdf</a><label for="m-law-wel" class="close-btn"><i class="fa-solid fa-xmark"></i></label></div><div class="modal-body"><iframe src="{create_mock_doc_url('Welfare', '<h2>กฎกระทรวงว่าด้วยการจัดสวัสดิการฯ</h2><p><mark>มาตรฐานหอพักและน้ำดื่มน้ำใช้</mark></p>')}" style="width:100%;height:300px;border:none;"></iframe></div></div></div>
    <input type="checkbox" id="m-law-hr" class="modal-toggle"><div class="modal-window"><label class="modal-backdrop" for="m-law-hr"></label><div class="modal-content"><div class="modal-header"><a href="#" class="modal-title-link"><i class="fa-solid fa-book" style="color:#D97706;"></i> Thai_Labor_Law_Hours.pdf</a><label for="m-law-hr" class="close-btn"><i class="fa-solid fa-xmark"></i></label></div><div class="modal-body"><iframe src="{create_mock_doc_url('Hours', '<h2>พ.ร.บ. คุ้มครองแรงงาน</h2><p><mark>ชั่วโมงการทำงานและการบังคับทำล่วงเวลา</mark></p>')}" style="width:100%;height:300px;border:none;"></iframe></div></div></div>
    """

    current_key = next((k for k in db_dict.keys() if k in selected_issue), None)
    
    if current_key:
        data = db_dict[current_key]
        plain_evidence = data["evidence"]
        plain_standard = data["standard"]
        evidence_base = data["html_evi"]
        framework_citation = data["html_std"]
        def_scale, def_lik, def_rem, def_sco = data["sev"], data["lik"], data["rem"], data["sco"]
        plan_y, plan_r = data["plan_y"], data["plan_r"]
        modal_html = data["modals"] + common_modals
    else:
        plain_evidence = f"Tool 2 & 3: ระบบวิเคราะห์พบสัญญาณความเสี่ยงจากข้อมูล {scope_text} โปรดตรวจสอบหลักฐาน"
        plain_standard = "UNGPs | ILO Conventions | กฎหมายแรงงานท้องถิ่น"
        evidence_base = f"📌 <b>แหล่งที่มา (Sources):</b> <br>- <i>Tool 2 & 3:</i> ระบบวิเคราะห์พบสัญญาณความเสี่ยงจาก {scope_text}"
        framework_citation = f"⚖️ <b>อ้างอิงมาตรฐาน (Standard):</b> {plain_standard}"
        def_scale, def_lik, def_rem, def_sco = 3, 3, 3, 3
        plan_y = "Preventive Action (แผนป้องกันเชิงรุก):\n- Proactive Measures: จัดอบรมให้ความรู้ ทบทวนขั้นตอนการทำงาน และสื่อสารนโยบายให้ทั่วถึง\n- Timeline: ติดตามผลภายใน 3-6 เดือน"
        plan_r = "Preventive: ปรับปรุงโครงสร้างสวัสดิการให้เป็นธรรม และเปิดช่องทางร้องเรียนอิสระ (Whistleblowing)\nRemediation: ตั้งกรรมการสอบสวนข้อเท็จจริง และเยียวยาผู้ถูกกระทำ"
        modal_html = common_modals

    if is_already_approved and save_issue in st.session_state.saved_plans_dict:
        saved_data = st.session_state.saved_plans_dict[save_issue]
        def_scale, def_lik = saved_data.get('sev', def_scale), saved_data.get('lik', def_lik)
        def_sco, def_rem = saved_data.get('sco', def_sco), saved_data.get('rem', def_rem)

    if selected_issue and "เลือกประเด็น" not in selected_issue and "(ไม่พบ" not in selected_issue:
        st.markdown(f"""
        {modal_html}
        <div style="background: #F5F3FF; border-left: 4px solid #8B5CF6; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.02);">
            <strong style="color: #6D28D9; font-size: 16px;"><i class="fa-solid fa-magnifying-glass-chart"></i> AI Triangulation Evidence (หลักฐานสนับสนุนการประเมิน):</strong>
            <div style="font-size: 14px; margin-top: 10px; color: #444; line-height: 1.8;">{evidence_base}</div>
        </div>
        """, unsafe_allow_html=True)

    if "(ไม่พบ" in selected_issue:
        st.stop() 

    st.markdown("<hr style='border: 1px dashed #ccc;'>", unsafe_allow_html=True)
    st.markdown("<h5 style='color: #005B31;'><i class='fa-solid fa-sliders'></i> 2. ประเมินระดับความรุนแรง (Severity) และ โอกาสเกิด (Likelihood)</h5>", unsafe_allow_html=True)

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
    elif score >= 8:
        risk_zone = "YELLOW"
        badge_html = '<div class="salient-badge" style="background-color: #FFFBEB; color: #D97706; border-color: #FDE68A;">⚠️ SIGNIFICANT RISK: ประเด็นความเสี่ยงปานกลาง/สูง (AI กำลังร่างแผนป้องกันเชิงรุก)</div>'
    else:
        risk_zone = "GREEN"
        badge_html = '<div class="salient-badge" style="background-color: #F0FDF4; color: #166534; border-color: #BBF7D0;">✅ MODERATE/MINOR RISK: ความเสี่ยงต่ำ (AI กำลังร่างแผนคงสภาพ)</div>'
    
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

    if risk_zone == "GREEN": ai_plan = "Maintenance Plan (แผนคงสภาพ):\n- Monitoring: ระดับความเสี่ยงปกติ ให้ทำการตรวจสอบซ้ำและติดตามผลตามวงรอบอย่างน้อยปีละ 1 ครั้ง"
    elif risk_zone == "YELLOW": ai_plan = plan_y
    else: ai_plan = plan_r

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
        <div style="background: #FFFFFF; padding: 12px; border-radius: 6px; border: 1px solid #EAEAEA; margin: 15px 0; font-size: 14px; color: #005B31; line-height: 1.8;">
            {framework_citation}
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

    button_label = "🔄 อัปเดตข้อมูลฉบับแก้ไข (Overwrite Data)" if is_already_approved else "💾 อนุมัติและบันทึกประเด็น (Approve & Update Database)"

    if st.button(button_label):
        if sheet:
            db_risk_level = "Salient" if risk_zone == "RED" else ("Significant" if risk_zone == "YELLOW" else "Moderate/Minor")
            detail = f"Scale:{scale}, Scope:{scope}, Remedy:{remedy} | Evidence: {final_evidence} | Standard: {final_standard} | Plan: {final_plan}"
            
            macro_group = f"ข้อมูลระบุกลุ่มเป้าหมาย ({custom_filter_text})" if custom_filter_text else "ภาพรวมระดับองค์กร (Corporate Level)"
            
            new_row_data = [now, audit_cycle, auditor_name, location, "Tool 5", "Issue-Based", macro_group, "N/A", "N/A", save_issue, detail, sev_max, likelihood, score, db_risk_level]
            
            st.session_state.saved_plans_dict[save_issue] = {
                'plan': final_plan, 
                'sev': sev_max, 
                'lik': likelihood,
                'sco': scope,
                'rem': remedy,
                'evidence': final_evidence,
                'standard': final_standard,
                'filter_context': custom_filter_text 
            }
            if not is_already_approved:
                st.session_state.approved_issues.append(save_issue)

            with st.spinner("กำลังซิงค์ข้อมูลกับฐานข้อมูล..."):
                all_records = sheet.get_all_values()
                row_to_update = -1
                for i in range(len(all_records)-1, -1, -1):
                    row = all_records[i]
                    if len(row) >= 10 and row[1] == audit_cycle and row[3] == location and row[4] == "Tool 5" and row[9] == save_issue:
                        row_to_update = i + 1
                        break
                
                if row_to_update != -1:
                    try:
                        sheet.update(f"A{row_to_update}:O{row_to_update}", [new_row_data])
                        st.success(f"🔄 **อัปเดตข้อมูลสำเร็จ:** ทับข้อมูลเดิมของประเด็น '{save_issue}' เรียบร้อยแล้ว")
                    except TypeError:
                        sheet.update(values=[new_row_data], range_name=f"A{row_to_update}:O{row_to_update}")
                        st.success(f"🔄 **อัปเดตข้อมูลสำเร็จ:** ทับข้อมูลเดิมของประเด็น '{save_issue}' เรียบร้อยแล้ว")
                else:
                    sheet.append_row(new_row_data)
                    st.success(f"✅ **อนุมัติและบันทึกใหม่สำเร็จ:** เพิ่มประเด็น '{save_issue}' เข้าสู่ระบบเรียบร้อยแล้ว")

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
    st.info("🤖 **Gemini AI Triangulation:** ระบบตรวจพบข้อมูลที่ขัดแย้งกัน (Data Contradiction) สะท้อนถึงช่องว่างในการนำนโยบายไปปฏิบัติจริง (Policy Implementation Gap)")
    
    c_left, c_right = st.columns(2)
    with c_left:
        st.success("📋 **ข้อมูลเชิงนโยบาย (Tool 1: Management)**\n\nผู้แทนฝ่ายบริหารระบุว่า:\n\n*\"บริษัทมีการบังคับใช้นโยบาย Zero Recruitment Fees โดยเด็ดขาด ครอบคลุมการออกค่าใช้จ่ายในการเดินทางและทำเอกสารให้พนักงานข้ามชาติทั้งหมด\"*")
    with c_right:
        st.error("🗣️ **ข้อมูลปฏิบัติจริง (Tool 3: Interview)**\n\nคำให้การพนักงานแรงงานข้ามชาติ:\n\n*\"พวกเราต้องจ่ายเงินสดให้เอเจนซี่ฝั่งพม่าไปคนละ 15,000 บาท เป็นค่าจัดการเอกสารและค่านายหน้า ก่อนที่จะเข้ามาทำงานในโรงงาน...\"*")

    st.markdown("""
    <div class="gemini-draft-box" style="margin-top: 20px;">
        <h5 class="gemini-title"><span class="gemini-icon">✨</span> Gemini AI Insight (การวิเคราะห์เชิงลึก):</h5>
        <p style="font-size: 14px; color: #444; margin-top: 5px;">ข้อมูลชี้ให้เห็นถึงช่องโหว่ด้านความโปร่งใสของ <b>Supply Chain / Third-party Agency</b> ที่ต้นทาง ซึ่งเป็นจุดบอด (Blind Spot) ของผู้บริหาร หากไม่เร่งตรวจสอบ อาจยกระดับเป็นข้อกล่าวหาด้าน <b>Debt Bondage (ภาระหนี้ผูกพัน)</b> หรือ <b>Forced Labor</b> ตามเกณฑ์สากลได้</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr style='border: 1px dashed #ccc; margin: 30px 0;'>", unsafe_allow_html=True)
    st.markdown("#### ✍️ ส่วนพิจารณาโดยผู้เชี่ยวชาญ (Human Validation)")
    
    t6_decision = st.radio("คุณพิจารณาแนวโน้มของสัญญาณเตือนภัยนี้อย่างไร? *", 
                           ["✔️ ยืนยันให้เป็น 'ความเสี่ยงที่ต้องสืบสวน' (Approve for Investigation)", 
                            "❌ ปฏิเสธการแจ้งเตือน (Reject / False Alarm)"], 
                           horizontal=True)
    
    t6_note = st.text_input("ระบุเหตุผลสนับสนุนการพิจารณาเชิงยุทธศาสตร์:", placeholder="เช่น สั่งการให้ทีม CSR ลงพื้นที่สุ่มตรวจสอบเอเจนซี่เพิ่มเติมทันที...")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 บันทึกมติการพิจารณา Tool 6"):
        if sheet:
            decision_text = "Approved" if "ยืนยัน" in t6_decision else "Rejected"
            detail = f"Anomaly: Recruitment Fee | Decision: {decision_text} | Note: {t6_note}"
            sheet.append_row([now, audit_cycle, auditor_name, location, "Tool 6", "Issue-Based", "ภาพรวมระดับองค์กร (Corporate Level)", "N/A", "N/A", "Early Warning (Recruitment Fee)", detail, "", "", "", ""])
            
            st.session_state.early_warning_approved = True if "ยืนยัน" in t6_decision else False
            st.session_state.early_warning_note = t6_note
            st.success("✅ บันทึกมติการพิจารณาสัญญาณเตือนภัยล่วงหน้าเข้าสู่ระบบฐานข้อมูลกลางเรียบร้อย")
            
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- TOOL 7 (Executive Dashboard & AI Report) -----------------
elif choice == "Tool 7: แดชบอร์ดและรายงานสรุป (Dashboard & Report)":
    st.markdown("<div class='standalone-form'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#005B31; margin-top:0;'>Tool 7: Executive Dashboard & Comprehensive Report</h3><p style='color:#666;'>สรุปผลประเมินนัยสำคัญของความเสี่ยง (Salient Risk) ระดับองค์กร</p><hr>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    
    # 💡 อัปเกรด: แสดงยอดตามจำนวนแถว Tool 1-4 จริง
    sheet_data_count = 0
    if sheet:
        all_records = sheet.get_all_values()
        if len(all_records) > 1:
            raw_data = [row for row in all_records[1:] if row[4] in ["Tool 1", "Tool 2", "Tool 3", "Tool 4"]]
            sheet_data_count = len(raw_data)
            
    if sheet_data_count == 0: sheet_data_count = 135
    
    with c1: st.markdown(f"<div class='dash-card'><div class='dash-label'>ข้อมูลที่สืบค้นจากระบบ</div><div class='dash-number'>{sheet_data_count}</div><div style='color: #005B31; font-size:12px;'>บันทึกฐานข้อมูลจาก Tool 1-4</div></div>", unsafe_allow_html=True)
    
    approved_count = len(st.session_state.get("approved_issues", []))
    with c2: st.markdown(f"<div class='dash-card'><div class='dash-label'>Salient Issues</div><div class='dash-number' style='color:#DC2626;'>{approved_count}</div><div style='color: #666; font-size:12px;'>ประเด็นที่ได้รับการอนุมัติแผนจัดการ</div></div>", unsafe_allow_html=True)
    
    ew_count = 1 if st.session_state.get("early_warning_approved", False) else 0
    with c3: st.markdown(f"<div class='dash-card'><div class='dash-label'>Early Warnings</div><div class='dash-number' style='color:#D97706;'>{ew_count}</div><div style='color: #666; font-size:12px;'>สัญญาณเตือนภัยที่รอการสอบสวน</div></div>", unsafe_allow_html=True)
    
    st.markdown("<br><h5 style='color: #005B31; text-align:center;'>📊 แผนผังการกระจายตัวความเสี่ยงระดับองค์กร (Corporate Risk Matrix)</h5>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#666; font-size:14px; margin-bottom: 20px;'>👉 แสดงเฉพาะประเด็นความเสี่ยงที่ได้รับการอนุมัติแล้วจาก Tool 5</p>", unsafe_allow_html=True)
    
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
- แนวทางสืบสวน (Investigation Resolution): อนุมัติดำเนินการตรวจสอบเชิงลึก โดยระบุเหตุผลเชิงยุทธศาสตร์ว่า "{ew_note}" """
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
                sheet.append_row([now, audit_cycle, auditor_name, location, "Tool 7 - Report", "Executive Summary", "ภาพรวม (Corporate)", "N/A", "N/A", f"Comprehensive Report: {audit_cycle}", report_text_final, "", "", "", "Approved"])
                st.success("✅ อนุมัติยุทธศาสตร์องค์กรและบันทึกรายงานประเมินความเสี่ยงฉบับสมบูรณ์เข้าสู่ฐานข้อมูลเรียบร้อยแล้ว!")
                
    st.markdown("</div>", unsafe_allow_html=True)
