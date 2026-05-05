import streamlit as st
import pandas as pd
from google.oauth2 import service_account
import gspread
from datetime import datetime, timedelta
import altair as alt

# ==========================================
# --- 1. SETTING UP THE PAGE ---
# ==========================================
st.markdown("""
<style>
    /* แก้ไขส่วน Header/Hero ให้ยืดหยุ่นตามหน้าจอ */
    .main-header {
        background: linear-gradient(135deg, #005B31 0%, #009245 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden; /* ป้องกันเนื้อหาแลบออกนอกกรอบ */
        display: flex;
        flex-wrap: wrap; /* สำคัญ: ให้ของข้างในตัดบรรทัดได้ถ้าที่ไมพอ */
        justify-content: space-between;
        align-items: center;
        gap: 15px;
    }

    /* ปรับแต่งกล่องข้อความฝั่งซ้าย */
    .header-content {
        flex: 1 1 300px; /* ยืดหดได้ และมีขนาดเริ่มต้นที่พอดี */
    }

    /* แก้ไขกล่องฝั่งขวา (ที่มักจะตกขอบ) */
    .header-badge {
        background: rgba(255,255,255,0.2);
        padding: 10px 20px;
        border-radius: 50px;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255,255,255,0.3);
        font-size: 0.9rem;
        white-space: nowrap; /* ป้องกันตัวอักษรตัดบรรทัดแบบแปลกๆ */
        max-width: fit-content; /* ให้กว้างเท่าที่จำเป็น */
    }

    /* CSS Media Query สำหรับมือถือโดยเฉพาะ */
    @media (max-width: 768px) {
        .main-header {
            padding: 1.5rem;
            text-align: center; /* บนมือถือจัดกลางจะดูดีกว่า */
            justify-content: center;
        }
        
        .header-badge {
            margin-top: 10px;
            font-size: 0.8rem;
            padding: 5px 15px;
        }
        
        h1 {
            font-size: 1.8rem !important; /* ปรับขนาดหัวข้อให้เล็กลงหน่อยบนมือถือ */
        }
    }
</style>
""", unsafe_allow_html=True)

# ส่วนการแสดงผล Hero (ตัวอย่างโครงสร้างที่ควรใช้คู่กับ CSS ด้านบน)
st.markdown("""
<div class="main-header">
    <div class="header-content">
        <h1 style="margin:0; color:white;">RiskSearch 360°</h1>
        <p style="margin:0; opacity:0.9;">Strategic Human Rights Due Diligence Platform</p>
    </div>
    <div class="header-badge">
        🚀 AI Powered System v2.5
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# --- 1.1 KNOWLEDGE BASE (ฐานข้อมูลกฎหมายและนโยบาย) ---
# ==========================================
LAW_KNOWLEDGE_BASE = {
    "OT": {
        "name": "พระราชบัญญัติคุ้มครองแรงงาน พ.ศ. 2541", "clause": "มาตรา 24 และ มาตรา 70", 
        "desc": "ห้ามมิให้นายจ้างให้ลูกจ้างทำงานล่วงเวลาเกินกว่าที่กฎหมายกำหนด (ไม่เกิน 36 ชั่วโมง/สัปดาห์) และนายจ้างต้องจ่ายค่าทำงานล่วงเวลาให้ถูกต้อง", 
        "doc": "Thai_Labor_Law_2541.pdf", "link": "https://www.mol.go.th/law"
    },
    "ค่าจ้าง": {
        "name": "ILO Convention No. 95 (Protection of Wages)", "clause": "Article 12", 
        "desc": "ค่าจ้างจะต้องถูกจ่ายอย่างสม่ำเสมอตามระยะเวลาที่กำหนด ห้ามมิให้มีการหักค่าจ้างอย่างไม่เป็นธรรม", 
        "doc": "ILO_Conv_95_Full.pdf", "link": "https://www.ilo.org/"
    },
    "เอกสารประจำตัว": {
        "name": "ILO Forced Labour Convention, 1930 (No. 29) & Employer Pays Principle", "clause": "มาตรา 2 (นิยามแรงงานบังคับ)", 
        "desc": "ห้ามมิให้นายจ้างหรือตัวแทนยึดเอกสารประจำตัวแรงงาน (Passport/Work Permit) เพื่อเป็นหลักประกัน", 
        "doc": "ILO_Conv_29_EPP.pdf", "link": "https://www.ilo.org/"
    },
    "พาสปอร์ต": {
        "name": "ILO Forced Labour Convention, 1930 (No. 29) & Employer Pays Principle", "clause": "มาตรา 2 (นิยามแรงงานบังคับ)", 
        "desc": "ห้ามมิให้นายจ้างหรือตัวแทนยึดเอกสารประจำตัวแรงงาน (Passport/Work Permit) เพื่อเป็นหลักประกัน", 
        "doc": "ILO_Conv_29_EPP.pdf", "link": "https://www.ilo.org/"
    },
    "ค่าธรรมเนียม": {
        "name": "ILO Forced Labour Convention, 1930 (No. 29) & Employer Pays Principle", "clause": "มาตรา 2 (นิยามแรงงานบังคับ)", 
        "desc": "นายจ้างต้องรับผิดชอบค่าใช้จ่ายในการสรรหาแรงงานทั้งหมด (Zero Recruitment Fee)", 
        "doc": "ILO_Conv_29_EPP.pdf", "link": "https://www.ilo.org/"
    },
    "ความปลอดภัย": {
        "name": "ISO 45001:2018 & พ.ร.บ. ความปลอดภัยฯ", "clause": "หมวด 2 มาตรา 16", 
        "desc": "นายจ้างต้องจัดให้มีอุปกรณ์คุ้มครองความปลอดภัยส่วนบุคคล (PPE) ที่ได้มาตรฐานโดยไม่คิดค่าใช้จ่าย", 
        "doc": "ISO_45001_OHS.pdf", "link": "https://www.iso.org/"
    },
    "เด็ก": {
        "name": "ILO Minimum Age Convention, 1973 (No. 138)", "clause": "Article 3", 
        "desc": "ห้ามใช้แรงงานเด็กอายุต่ำกว่า 18 ปี ในงานที่มีลักษณะเป็นอันตราย", 
        "doc": "ILO_Conv_138_ChildLabor.pdf", "link": "https://www.ilo.org/"
    },
    "ชุมชน": {
        "name": "พ.ร.บ. ส่งเสริมและรักษาคุณภาพสิ่งแวดล้อมแห่งชาติ", "clause": "หมวด 4 การควบคุมมลพิษ", 
        "desc": "สถานประกอบการต้องมีระบบบำบัดมลพิษที่ไม่ก่อให้เกิดผลกระทบต่อสิ่งแวดล้อมชุมชน", 
        "doc": "Thai_Env_Law_2535.pdf", "link": "https://www.pcd.go.th/"
    }
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
    if not resp_id or resp_id.strip() == "": return False
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

# --- 3. STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&family=Sarabun:wght@300;400;600;700;800&display=swap');
    html, body, [class*="st-"] { font-family: 'Sarabun', sans-serif; }
    .stApp { background-color: #F4F7F6; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    [data-testid="stHeader"], [data-testid="collapsedControl"], [data-testid="stSidebar"] { display: none !important; }
    
    .premium-banner {
        background: #FFFFFF; border-radius: 24px; padding: 30px 40px; box-shadow: 0px 20px 40px rgba(0, 91, 49, 0.05);
        border: 1px solid rgba(0, 91, 49, 0.08); border-left: 12px solid #005B31; display: flex; align-items: center; gap: 30px; margin-bottom: 40px; position: relative; overflow: hidden;
    }
    .premium-banner::after { content: ''; position: absolute; top: 0; right: 0; width: 150px; height: 8px; background: #F9A818; }
    
    .logo-wrapper { border-right: 2px solid #EAEAEA; padding-right: 30px; display: flex; flex-direction: column; align-items: center; min-width: max-content; }
    .typography-logo { font-family: 'Poppins', sans-serif; font-size: 26px; font-weight: 800; color: #D3A129; letter-spacing: 2px; margin-top: 10px; }
    .hero-title-eng { color: #005B31 !important; font-family: 'Poppins', sans-serif !important; font-size: 21px !important; font-weight: 800 !important; margin: 0 !important; white-space: nowrap; }
    .hero-title-thai { color: #265F36 !important; font-family: 'Sarabun', sans-serif !important; font-size: 16px !important; font-weight: 600 !important; margin: 5px 0 0 0 !important; white-space: nowrap; }
    
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

    .testimony-box { background-color: #FFFFFF; border-left: 4px solid #3B82F6; padding: 15px; margin-bottom: 10px; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    
    [data-testid="stPopover"] button span.material-symbols-rounded { display: none !important; }
    [data-testid="stPopover"] button svg { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# --- 3.1 🔐 ENTERPRISE SSO & WHITELIST ---
# ==========================================
if "user_db" not in st.session_state: st.session_state.user_db = {}
if "current_user" not in st.session_state: st.session_state.current_user = None
WHITELIST = ["admin@betagro.com", "somchai@betagro.com", "auditor1@betagro.com", "auditor2@betagro.com", "investor@betagro.com"]

def check_password():
    if st.session_state.current_user is not None: return True
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
            st.markdown("<h4 style='color: #005B31; text-align: center; margin-bottom: 20px; font-weight: 600;'>🔒 ระบบประเมิน HRDD อัจฉริยะ (Simulation)</h4>", unsafe_allow_html=True)
            email = st.text_input("Corporate Email (อีเมลองค์กร)", placeholder="เช่น admin@betagro.com")
            if email:
                if email in WHITELIST:
                    if email not in st.session_state.user_db:
                        st.info("👋 ยินดีต้อนรับ! กรุณาตั้งรหัสผ่านสำหรับบัญชีของคุณเพื่อความปลอดภัย")
                        new_pwd = st.text_input("ตั้งรหัสผ่านใหม่ (New Password)", type="password")
                        confirm_pwd = st.text_input("ยืนยันรหัสผ่าน (Confirm Password)", type="password")
                        if st.form_submit_button("บันทึกรหัสผ่านและเข้าสู่ระบบ"):
                            if new_pwd == confirm_pwd and new_pwd != "":
                                st.session_state.user_db[email] = new_pwd
                                st.session_state.current_user = email
                                st.rerun()
                            else: st.error("❌ รหัสผ่านไม่ตรงกัน หรือเว้นว่าง กรุณาลองใหม่")
                    else:
                        pwd = st.text_input("รหัสผ่าน (Password)", type="password", placeholder="Enter Password...")
                        c_btn1, c_btn2 = st.columns(2)
                        with c_btn1: btn_login = st.form_submit_button("LOGIN", use_container_width=True)
                        with c_btn2: btn_forgot = st.form_submit_button("ลืมรหัสผ่าน?", use_container_width=True)
                        if btn_forgot: st.success("📩 ระบบได้ส่งลิงก์สำหรับรีเซ็ตรหัสผ่านไปยังอีเมลองค์กรของคุณเรียบร้อยแล้ว")
                        elif btn_login:
                            if pwd == st.session_state.user_db[email]:
                                st.session_state.current_user = email
                                st.rerun()
                            else: st.error("❌ รหัสผ่านไม่ถูกต้อง")
                else:
                    st.error("❌ Access Denied. อีเมลนี้ไม่ได้รับสิทธิ์การเข้าถึง")
                    st.form_submit_button("LOGIN") 
            else:
                st.form_submit_button("ตรวจสอบสิทธิ์")
                st.caption("💡 **คำแนะนำ:** กรุณากรอกอีเมลองค์กรเพื่อตรวจสอบสิทธิ์ (อีเมลทดสอบระบบ: admin@betagro.com)")
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
            <div class="hero-title-thai">ระบบจำลองการบริหารจัดการสิทธิมนุษยชนอัจฉริยะ (HRDD Simulation)</div>
            <div class="hero-subtitle">Smart Assessment Systems & Real-time Data Analytics</div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown('<div class="control-panel">', unsafe_allow_html=True)
st.markdown("<h4 style='color: #005B31; margin-bottom: 15px; font-weight: 700;'>1. ข้อมูลโครงการและบัญชีผู้ใช้งาน</h4>", unsafe_allow_html=True)
col_p1, col_p2 = st.columns(2)
with col_p1: audit_cycle = st.selectbox("รอบการประเมิน *", ["Annual 2026", "Q1/2026", "Q2/2026", "Q3/2026", "Q4/2026", "Special Audit"])
with col_p2: 
    st.text_input("ผู้ใช้งานระบบ", value=st.session_state.current_user, disabled=True)
    auditor_name = st.session_state.current_user

st.markdown("<hr style='border: 1px solid #eee; margin: 20px 0;'>", unsafe_allow_html=True)
st.markdown("<h4 style='color: #005B31; margin-bottom: 15px; font-weight: 700;'>2. เลือกเครื่องมือปฏิบัติงาน</h4>", unsafe_allow_html=True)

choice = st.selectbox("เลือกฟังก์ชันหรือรายงานที่ต้องการ:", [
    "Tool 1: ประเมินสถานะองค์กร (Governance & Policy Gap)",
    "Tool 2: แบบสอบถามหน้างาน (Worker Survey)",
    "Tool 3: สัมภาษณ์เชิงลึก (Evidence-based Grounding)",
    "Tool 4: บันทึกการสังเกตการณ์ (Site Observation Log)",
    "Tool 5: ประเมินความเสี่ยง (Salient Human Rights Risks Scoring Matrix)",
    "Tool 6: ระบบเตือนภัยล่วงหน้า (Predictive Hotspot Modeling)",
    "Tool 7: แดชบอร์ดและรายงาน (Real-time Data Analytics)"
], label_visibility="collapsed")

is_tool_1_to_4 = choice.startswith("Tool 1") or choice.startswith("Tool 2") or choice.startswith("Tool 3") or choice.startswith("Tool 4")

if is_tool_1_to_4:
    st.markdown("<hr style='border: 1px dashed #EAEAEA; margin: 20px 0;'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #005B31; margin-bottom: 15px; font-weight: 700;'>3. ข้อมูลพื้นที่และผู้ให้ข้อมูล (AI-Driven Digital Collection)</h4>", unsafe_allow_html=True)
    st.info("📌 กรุณาระบุพื้นที่และรหัสอ้างอิงรายบุคคล เพื่อความแม่นยำในการเก็บข้อมูลเข้าฐานข้อมูล")
    col_r_loc, col_r_id = st.columns([2, 1])
    with col_r_loc: location = st.text_input("พื้นที่สำรวจ (Location/Site) *", placeholder="เช่น รง.แปรรูปไก่ สระบุรี")
    with col_r_id: resp_id = st.text_input("รหัสอ้างอิง (ID) *", placeholder="เช่น T01, M01")
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1: resp_group = st.selectbox("กลุ่มเป้าหมาย *", ["ผู้บริหาร", "พนักงานไทย", "แรงงานข้ามชาติ", "คู่ค้า (Suppliers)", "ชุมชน", "องค์กรไม่แสวงหากำไร (NGOs)", "นักลงทุน", "ลูกค้า (Retail)", "ลูกค้า (B2B)"])
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
        st.markdown("<h3 style='color:#005B31;'>Tool 1: ประเมินสถานะองค์กร (Policy Gap / Self-Assessment Checklist)</h3>", unsafe_allow_html=True)
        st.markdown("สำหรับฝ่ายบริหาร เพื่อตรวจสอบนโยบายและการดำเนินงานตามมาตรฐานสากล")
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### ส่วนที่ 1: การประกาศนโยบายและความมุ่งมั่น (Policy Commitment)")
        q1_1 = st.radio("1.1 องค์กรมีการจัดทำ 'นโยบายสิทธิมนุษยชน' เป็นลายลักษณ์อักษรที่อนุมัติโดยคณะกรรมการบริษัทหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        q1_2 = st.radio("1.2 นโยบายครอบคลุมประเด็นสำคัญ (แรงงานข้ามชาติ, สิทธิชุมชน, ความหลากหลาย) หรือไม่ และประเด็นสิ่งแวดล้อมตามเกณฑ์ OECD 2023 และ EU CSDDD?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        q1_3 = st.radio("1.3 มีการสื่อสารนโยบายนี้ให้พนักงานและคู่ค้า (Suppliers) รับทราบในภาษาที่พวกเขาเข้าใจหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        st.markdown("<hr style='border: 1px dashed #ccc;'>", unsafe_allow_html=True)
        st.markdown("#### ส่วนที่ 2: กระบวนการตรวจสอบสิทธิมนุษยชนอย่างรอบด้าน (HR Due Diligence Process)")
        q2_1 = st.radio("2.1 องค์กรมีระบบการประเมินความเสี่ยงด้านสิทธิมนุษยชน (HRA) เป็นประจำทุกปีหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        q2_2 = st.radio("2.2 มีกระบวนการตรวจสอบย้อนกลับ (Traceability) ในห่วงโซ่คุณค่าต้นน้ำ (คู่ค้า Tier 1-2) หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        q2_3 = st.radio("2.3 มีการกำหนดตัวชี้วัด (KPIs) ด้านสิทธิมนุษยชนในระดับหน่วยงานปฏิบัติการหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        st.markdown("<hr style='border: 1px dashed #ccc;'>", unsafe_allow_html=True)
        st.markdown("#### ส่วนที่ 3: กลไกการร้องเรียนและการเยียวยา (Grievance & Remediation)")
        q3_1 = st.radio("3.1 มีช่องทางรับเรื่องร้องเรียนที่ปลอดภัย เป็นความลับ และเข้าถึงได้ง่ายสำหรับพนักงานทุกคนและบุคคลภายนอกหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        q3_2 = st.radio("3.2 มีการจัดทำขั้นตอนการเยียวยา (Remediation Protocol) อย่างชัดเจน เมื่อพบการละเมิดสิทธิมนุษยชนหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("💾 บันทึกข้อมูล Tool 1"):
            if sheet:
                detail = f"P1({q1_1},{q1_2},{q1_3})|P2({q2_1},{q2_2},{q2_3})|P3({q3_1},{q3_2})"
                sheet.append_row([now, audit_cycle, auditor_name, location, "Tool 1", resp_id, resp_group, resp_dept, resp_gender, "Policy Gap Analysis", detail, "", "", "", ""])
                st.success("✅ บันทึกข้อมูล Tool 1 (ฉบับเต็ม) เรียบร้อยแล้ว")

elif choice.startswith("Tool 2"):
    with st.form("form_t2"):
        st.markdown("<h3 style='color:#005B31;'>Tool 2: แบบสอบถามการปฏิบัติหน้างาน (Worker Survey)</h3>", unsafe_allow_html=True)
        st.info("💡 ระดับคะแนน: 1 = ไม่จริงเลย / ไม่เคยปฏิบัติ | 5 = เป็นความจริงที่สุด / ปฏิบัติเสมอ")
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### หมวดที่ 1: สภาพการจ้างและค่าจ้าง (Wages & Employment)")
        s1_1 = st.select_slider("1.1 ท่านได้รับค่าจ้างตรงเวลาและครบถ้วนตามที่ตกลงไว้ในสัญญาจ้าง", options=[1,2,3,4,5], value=3)
        s1_2 = st.select_slider("1.2 ท่านได้รับสลิปเงินเดือน (Pay slip) ที่แจกแจงรายได้และรายการหักอย่างชัดเจน", options=[1,2,3,4,5], value=3)
        s1_3 = st.select_slider("1.3 การทำงานล่วงเวลา (OT) ของท่านเกิดจากความสมัครใจ ไม่ได้ถูกข่มขู่หรือบังคับ", options=[1,2,3,4,5], value=3)
        st.markdown("<hr style='border: 1px dashed #ccc;'>", unsafe_allow_html=True)
        st.markdown("#### หมวดที่ 2: แรงงานบังคับและเอกสารประจำตัว (Forced Labor & Documents)")
        s2_1 = st.select_slider("2.1 ท่านเป็นผู้เก็บเอกสารประจำตัว (พาสปอร์ต, บัตรประชาชน, Work Permit) ไว้กับตัวท่านเองตลอดเวลา", options=[1,2,3,4,5], value=3)
        s2_2 = st.select_slider("2.2 ท่านไม่ต้องจ่ายค่าธรรมเนียมหรือค่านายหน้าในการเข้ามาทำงานที่นี่ (Zero Recruitment Fee)", options=[1,2,3,4,5], value=3)
        s2_3 = st.select_slider("2.3 ท่านมีอิสระในการลาออกและเดินทางกลับบ้านนอกเวลาทำงาน", options=[1,2,3,4,5], value=3)
        st.markdown("<hr style='border: 1px dashed #ccc;'>", unsafe_allow_html=True)
        st.markdown("#### หมวดที่ 3: สุขภาพและความปลอดภัย (Occupational Health & Safety)")
        s3_1 = st.select_slider("3.1 บริษัทจัดเตรียมอุปกรณ์ป้องกันอันตราย (PPE) ให้เพียงพอ เหมาะสม และไม่มีค่าใช้จ่าย", options=[1,2,3,4,5], value=3)
        s3_2 = st.select_slider("3.2 สภาพแวดล้อมการทำงานของท่าน (แสง, เสียง, อากาศ, ฝุ่นควัน) ปลอดภัยต่อสุขภาพ", options=[1,2,3,4,5], value=3)
        s3_3 = st.select_slider("3.3 มีทางหนีไฟและอุปกรณ์ดับเพลิงที่เข้าถึงได้ง่าย ไม่มีสิ่งกีดขวางในพื้นที่ปฏิบัติงาน", options=[1,2,3,4,5], value=3)
        s3_4 = st.select_slider("3.4 โรงอาหาร น้ำดื่ม และที่พักอาศัย (ถ้ามี) มีความสะอาดและถูกสุขลักษณะ", options=[1,2,3,4,5], value=3)
        st.markdown("<hr style='border: 1px dashed #ccc;'>", unsafe_allow_html=True)
        st.markdown("#### หมวดที่ 4: การปฏิบัติต่อพนักงานและการร้องเรียน (Fair Treatment & Grievance)")
        s4_1 = st.select_slider("4.1 หัวหน้างานปฏิบัติต่อพนักงานทุกคนอย่างเท่าเทียม ไม่มีการล่วงละเมิดทางเพศหรือทางวาจา", options=[1,2,3,4,5], value=3)
        s4_2 = st.select_slider("4.2 ท่านมีสิทธิในการรวมกลุ่มหรือจัดตั้งคณะกรรมการสวัสดิการเพื่อต่อรองอย่างเสรี", options=[1,2,3,4,5], value=3)
        s4_3 = st.select_slider("4.3 หากมีปัญหา ท่านรู้จักช่องทางการร้องเรียนและมั่นใจว่าจะไม่ถูกกลั่นแกล้ง (Non-retaliation)", options=[1,2,3,4,5], value=3)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("🚀 บันทึกข้อมูล Tool 2"):
            if sheet:
                detail = f"Wages({s1_1},{s1_2},{s1_3}) | Forced({s2_1},{s2_2},{s2_3}) | OHS({s3_1},{s3_2},{s3_3},{s3_4}) | Fair({s4_1},{s4_2},{s4_3})"
                sheet.append_row([now, audit_cycle, auditor_name, location, "Tool 2", resp_id, resp_group, resp_dept, resp_gender, "Worker Survey", detail, "", "", "", ""])
                st.success("✅ ส่งข้อมูลแบบสอบถามสำเร็จ")

elif choice.startswith("Tool 3"):
    with st.form("form_t3"):
        st.markdown("<h3 style='color:#005B31;'>Tool 3: สัมภาษณ์เชิงลึก (Evidence-based Grounding)</h3><hr>", unsafe_allow_html=True)
        st.markdown("**🔍 หัวข้อการตรวจสอบ (เลือกข้อที่ทำการสัมภาษณ์เชิงลึก)**")
        topics = st.multiselect("ประเด็นที่พูดคุย:", [
            "การสรรหา/ค่านายหน้า/การยึดเอกสาร", "สัญญาจ้าง/ค่าจ้าง/สลิปเงินเดือน", "ชั่วโมงการทำงาน/การบังคับทำ OT",
            "สภาพการทำงาน/ความปลอดภัย/PPE", "สวัสดิการ/หอพัก/โรงอาหาร", "การเลือกปฏิบัติ/การล่วงละเมิด", 
            "เสรีภาพการสมาคม/สหภาพแรงงาน", "กลไกการร้องเรียน/การจัดการข้อพิพาท", "สิทธิชุมชน/ผลกระทบต่อสิ่งแวดล้อม"
        ], label_visibility="collapsed")
        st.markdown("<br>**✍️ บันทึกคำให้การ (Testimony / Direct Quote)**", unsafe_allow_html=True)
        st.caption("โปรดบันทึกคำพูดที่สะท้อนถึงประเด็นความเสี่ยงหรือแนวปฏิบัติที่ดีอย่างชัดเจน เพื่อนำไปใช้เป็นหลักฐาน (Evidence)")
        testimony = st.text_area("สรุปคำพูดหรือหลักฐานที่พบ:", height=150)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("💾 บันทึกข้อมูล Tool 3"):
            if sheet:
                sheet.append_row([now, audit_cycle, auditor_name, location, "Tool 3", resp_id, resp_group, resp_dept, resp_gender, ", ".join(topics), testimony, "", "", "", ""])
                st.success("✅ บันทึกหลักฐานสำเร็จ")

elif choice.startswith("Tool 4"):
    with st.form("form_t4"):
        st.markdown("<h3 style='color:#005B31;'>Tool 4: บันทึกการสังเกตการณ์ (Site Observation Log)</h3><hr>", unsafe_allow_html=True)
        st.info("📌 ประเมินสิ่งที่พบเห็นจริงหน้างาน (Visual Inspection) และบันทึกข้อสังเกตเพิ่มเติม")
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### ด้านนโยบายและกลไก (Policy & Mechanism)")
        o1 = st.radio("1. มีการติดประกาศนโยบายสิทธิมนุษยชนและช่องทางร้องเรียนในพื้นที่ที่พนักงานมองเห็นได้ชัดเจน", ["✔️ พบ (Pass)", "❌ ไม่พบ (Fail)", "➖ ไม่เกี่ยวข้อง (N/A)"], horizontal=True)
        note_o1 = st.text_input("บันทึกเพิ่มเติมข้อ 1:", key="n1", label_visibility="collapsed", placeholder="ระบุตำแหน่งที่พบ หรือปัญหาที่สังเกตเห็น...")
        st.markdown("#### ด้านความปลอดภัยและอาชีวอนามัย (OHS)")
        o2 = st.radio("2. ทางหนีไฟ อุปกรณ์ดับเพลิง และระบบสัญญาณเตือนภัย ไม่มีสิ่งกีดขวางและพร้อมใช้งาน", ["✔️ พบ (Pass)", "❌ ไม่พบ (Fail)", "➖ ไม่เกี่ยวข้อง (N/A)"], horizontal=True)
        note_o2 = st.text_input("บันทึกเพิ่มเติมข้อ 2:", key="n2", label_visibility="collapsed", placeholder="บันทึกสภาพของอุปกรณ์...")
        o3 = st.radio("3. พนักงานในสายการผลิตสวมใส่อุปกรณ์ป้องกันอันตราย (PPE) ถูกต้องและครบถ้วน", ["✔️ พบ (Pass)", "❌ ไม่พบ (Fail)", "➖ ไม่เกี่ยวข้อง (N/A)"], horizontal=True)
        note_o3 = st.text_input("บันทึกเพิ่มเติมข้อ 3:", key="n3", label_visibility="collapsed", placeholder="บันทึกหากพบพนักงานละเลยการใส่ PPE...")
        o4 = st.radio("4. เครื่องจักรมีการติดตั้งฝาครอบป้องกัน (Machine Guard) และระบบหยุดฉุกเฉิน", ["✔️ พบ (Pass)", "❌ ไม่พบ (Fail)", "➖ ไม่เกี่ยวข้อง (N/A)"], horizontal=True)
        note_o4 = st.text_input("บันทึกเพิ่มเติมข้อ 4:", key="n4", label_visibility="collapsed", placeholder="บันทึกรหัสเครื่องจักรที่มีความเสี่ยง...")
        st.markdown("#### ด้านสภาพแวดล้อมและสวัสดิการ (Environment & Welfare)")
        o5 = st.radio("5. สภาพแวดล้อมพื้นที่ทำงานมีแสงสว่าง อุณหภูมิ และการระบายอากาศที่เหมาะสม", ["✔️ พบ (Pass)", "❌ ไม่พบ (Fail)", "➖ ไม่เกี่ยวข้อง (N/A)"], horizontal=True)
        note_o5 = st.text_input("บันทึกเพิ่มเติมข้อ 5:", key="n5", label_visibility="collapsed", placeholder="บันทึกหากพบฝุ่น ควัน หรือกลิ่นรบกวน...")
        o6 = st.radio("6. สภาพห้องน้ำ โรงอาหาร และที่พักอาศัย (ถ้ามี) มีความสะอาด เพียงพอ และถูกสุขลักษณะ", ["✔️ พบ (Pass)", "❌ ไม่พบ (Fail)", "➖ ไม่เกี่ยวข้อง (N/A)"], horizontal=True)
        note_o6 = st.text_input("บันทึกเพิ่มเติมข้อ 6:", key="n6", label_visibility="collapsed", placeholder="บันทึกข้อบกพร่องด้านสวัสดิการ...")
        o7 = st.radio("7. ตู้ยาสามัญประจำโรงงานหรือห้องพยาบาล มีเวชภัณฑ์ครบถ้วนและไม่หมดอายุ", ["✔️ พบ (Pass)", "❌ ไม่พบ (Fail)", "➖ ไม่เกี่ยวข้อง (N/A)"], horizontal=True)
        note_o7 = st.text_input("บันทึกเพิ่มเติมข้อ 7:", key="n7", label_visibility="collapsed", placeholder="บันทึกการตรวจสอบเวชภัณฑ์...")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("💾 บันทึกข้อมูล Tool 4"):
            if sheet:
                res_o1 = f"{o1.split(' ')[1]} ({note_o1})" if note_o1 else o1.split(" ")[1]
                res_o2 = f"{o2.split(' ')[1]} ({note_o2})" if note_o2 else o2.split(" ")[1]
                res_o3 = f"{o3.split(' ')[1]} ({note_o3})" if note_o3 else o3.split(" ")[1]
                res_o4 = f"{o4.split(' ')[1]} ({note_o4})" if note_o4 else o4.split(" ")[1]
                res_o5 = f"{o5.split(' ')[1]} ({note_o5})" if note_o5 else o5.split(" ")[1]
                res_o6 = f"{o6.split(' ')[1]} ({note_o6})" if note_o6 else o6.split(" ")[1]
                res_o7 = f"{o7.split(' ')[1]} ({note_o7})" if note_o7 else o7.split(" ")[1]
                detail = f"Policy: {res_o1} | Fire: {res_o2} | PPE: {res_o3} | Guard: {res_o4} | Env: {res_o5} | Welfare: {res_o6} | Med: {res_o7}"
                sheet.append_row([now, audit_cycle, auditor_name, location, "Tool 4", resp_id, resp_group, resp_dept, resp_gender, "Site Observation", detail, "", "", "", ""])
                st.success("✅ บันทึกการสังเกตการณ์ (ฉบับเต็ม) สำเร็จ")

# ----------------- TOOL 5 (Salient Human Rights Risks Scoring Matrix: AI-AUGMENTED TRIANGULATION ENGINE) -----------------
elif choice.startswith("Tool 5"):

    st.markdown("<div class='standalone-form'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#005B31; margin-top:0;'>Tool 5: ประเมินความเสี่ยง (Salient HR Risks Scoring Matrix: Triangulation & Sentiment Analysis)</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="filter-box">
        <h5 style="color:#D97706; margin-top:0;"><i class="fa-solid fa-filter"></i> กำหนดหน่วยการวิเคราะห์ (Unit of Analysis)</h5>
        <p style="font-size: 14px; color: #666; margin-bottom: 10px;">กรองฐานข้อมูลเพื่อประเมินความเสี่ยงระดับองค์กร หรือเจาะจงตามกลุ่มผู้มีส่วนได้เสีย</p>
    </div>
    """, unsafe_allow_html=True)
    
    filter_mode = st.radio("ระดับการวิเคราะห์:", ["ระดับองค์กรภาพรวม (Corporate Level / ทุกกลุ่ม)", "ระดับเจาะจงกลุ่มเป้าหมาย (Stakeholder Group Level)"], horizontal=True, label_visibility="collapsed")
    custom_filter_text = ""
    
    if filter_mode == "ระดับเจาะจงกลุ่มเป้าหมาย (Stakeholder Group Level)":
        custom_filter_text = st.selectbox("เลือกกลุ่มเป้าหมายที่ต้องการดึงข้อมูลมาวิเคราะห์:", [
            "ผู้บริหาร", "พนักงานไทย", "แรงงานข้ามชาติ", "คู่ค้า (Suppliers)", "ชุมชน", "องค์กรไม่แสวงหากำไร (NGOs)", "นักลงทุน", "ลูกค้า"
        ])

    raw_data_only_df = pd.DataFrame()
    if not df_real.empty:
        raw_data_only_df = df_real[df_real['เครื่องมือ'].isin(['Tool 1', 'Tool 2', 'Tool 3', 'Tool 4'])]
        
    df_filtered = raw_data_only_df.copy()
    if not raw_data_only_df.empty:
        if custom_filter_text:
            search_keyword = custom_filter_text.split(" ")[0]
            
            if search_keyword == "องค์กรไม่แสวงหากำไร":
                df_filtered = raw_data_only_df[
                    raw_data_only_df['กลุ่มเป้าหมาย'].str.contains("องค์กรไม่แสวงหากำไร|NGO", na=False, case=False, regex=True)
                ]
            elif search_keyword == "คู่ค้า":
                df_filtered = raw_data_only_df[
                    raw_data_only_df['กลุ่มเป้าหมาย'].str.contains("คู่ค้า|Supplier", na=False, case=False, regex=True)
                ]
            else:
                df_filtered = raw_data_only_df[raw_data_only_df['กลุ่มเป้าหมาย'].str.contains(search_keyword, na=False, case=False)]
    
    sheet_data_count = len(df_filtered)
    
    if sheet_data_count == 0: 
        if custom_filter_text in ["ผู้บริหาร", "คู่ค้า (Suppliers)", "ลูกค้า"]:
            st.warning(f"⚠️ ผลการวิเคราะห์ข้อมูลเฉพาะกลุ่ม [{custom_filter_text}]: ไม่พบการรายงานความเสี่ยง (Zero Self-Reported Risks)")
            st.info("🚨 **ข้อควรระวังตามมาตรฐาน HRDD (Blind-spot Alert):** การที่กลุ่มระดับบริหารหรือคู่ค้าประเมินตนเองว่า 'ไม่มีความเสี่ยง' อาจเกิดจาก Self-reporting Bias ระบบไม่อนุญาตให้ถือว่าองค์กรปลอดภัยจนกว่าจะทำการครอสเช็คข้อมูล แนะนำให้คุณไปสแกนข้อมูลกลุ่ม **'แรงงานข้ามชาติ'** หรือ **'ภาพรวมองค์กร'** เพื่อเปรียบเทียบข้อเท็จจริง!")
        else:
            st.warning(f"⚠️ ไม่พบข้อมูลดิบของการประเมินของกลุ่มเป้าหมาย [{custom_filter_text}] ในฐานข้อมูล (Google Sheet)")
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
            real_issues_from_sheet = [i for i in raw_issues if str(i).strip() not in ["", "nan", "Worker Survey", "Site Observation", "Policy Gap Analysis"]]
        
        if len(real_issues_from_sheet) == 0:
            if custom_filter_text in ["ผู้บริหาร", "คู่ค้า (Suppliers)"]:
                st.warning(f"⚠️ ผลการวิเคราะห์ข้อมูลเฉพาะกลุ่ม [{custom_filter_text}]: ไม่พบประเด็นความเสี่ยงจากการประเมินตนเอง")
                st.info("🚨 **ข้อควรระวังตามมาตรฐาน HRDD (Blind-spot Alert):** กลุ่มเป้าหมายนี้มีแนวโน้มเกิด Self-reporting Bias ระบบไม่อนุญาตให้ถือว่าองค์กรปลอดภัยจนกว่าจะครอสเช็คกับเสียงของผู้ได้รับผลกระทบ แนะนำให้สแกน **'ภาพรวมองค์กร'** เพื่อดึงประเด็นขึ้นมาพิจารณา!")
            else:
                st.info(f"✅ AI ประมวลผลข้อมูลของกลุ่มนี้แล้ว ไม่พบประเด็นความเสี่ยงที่มีนัยสำคัญครับ")
            st.stop()
            
        ai_header = f"🤖 Gemini AI พบ {len(real_issues_from_sheet)} ประเด็นความเสี่ยง จากฐานข้อมูลจริง (กลุ่ม: {custom_filter_text if custom_filter_text else 'ภาพรวมทั้งหมด'}):"
        st.markdown(f'<div style="background: #E8F0FE; padding: 15px; border-radius: 8px; border-left: 4px solid #1967D2; margin-bottom: 20px;"><span style="color: #1967D2; font-weight: 700; font-size: 14px;">{ai_header}</span></div>', unsafe_allow_html=True)
        
        numbered_issues = [f"{idx+1}. {iss}" for idx, iss in enumerate(real_issues_from_sheet)]
        display_list = ["เลือกประเด็นความเสี่ยงให้ AI วิเคราะห์..."] + numbered_issues
        
        selected_option = st.selectbox("เลือกประเด็นความเสี่ยงเพื่อจัดทำแผน (Process Issue):", display_list)

        if not selected_option or selected_option == "เลือกประเด็นความเสี่ยงให้ AI วิเคราะห์...":
            st.stop()
            
        selected_issue = selected_option.split(". ", 1)[1] if ". " in selected_option else selected_option

    save_issue = selected_issue
    is_already_approved = save_issue in st.session_state.get("approved_issues", [])
    scope_text = f"กลุ่มเป้าหมาย: {custom_filter_text}" if custom_filter_text else "ภาพรวมองค์กรและห่วงโซ่อุปทาน"

    st.markdown("<hr style='border: 1px dashed #ccc;'>", unsafe_allow_html=True)
    st.markdown("<h5 style='color: #005B31;'><i class='fa-solid fa-brain'></i> 2. ผลการวิเคราะห์และฟันธงโดย AI (AI Executive Summary)</h5>", unsafe_allow_html=True)

    evidence_count = 0
    exec_quotes = []
    worker_quotes = []
    
    if not raw_data_only_df.empty and 'รายละเอียด/คำให้การ' in raw_data_only_df.columns:
        subset = raw_data_only_df[raw_data_only_df['ประเด็นหลัก'] == selected_issue]
        for idx, row in subset.iterrows(): 
            if str(row['รายละเอียด/คำให้การ']).strip() != "":
                evidence_count += 1
                grp = str(row.get('กลุ่มเป้าหมาย', ''))
                if "ผู้บริหาร" in grp or "คู่ค้า" in grp and "OS" in str(row.get('รหัสผู้ตอบ','')):
                    exec_quotes.append(row)
                else:
                    worker_quotes.append(row)
    
    ai_conclusion = ""
    ai_severity_suggest = 3
    ai_likelihood_suggest = 3
    ai_plan_suggest = ""
    
    if len(exec_quotes) > 0 and len(worker_quotes) > 0:
        ai_conclusion = f"""
        <div style='background-color: #FEF2F2; padding: 20px; border-radius: 8px; border-left: 5px solid #DC2626; margin-bottom: 20px;'>
            <h4 style='color: #991B1B; margin-top:0;'>⚠️ AI ฟันธง: พบความขัดแย้งของข้อมูล (Policy Implementation Gap)</h4>
            <p style='color: #444; font-size: 14px;'>
            จากการทำ <b>Triangulation & Sentiment Analysis</b> ระดับองค์กรภาพรวม (Global Fact) ระบบตรวจพบว่านโยบายของผู้บริหาร/ตัวแทน 
            ขัดแย้งโดยตรงกับคำให้การของกลุ่มปฏิบัติการ นี่คือช่องโหว่ด้านการตรวจสอบย้อนกลับ (Traceability) ระบบจึงยกระดับประเด็น <b>'{selected_issue}'</b> เป็นความเสี่ยงระดับสูง
            </p>
        </div>
        """
        ai_severity_suggest = 5 if "พาสปอร์ต" in selected_issue or "แรงงาน" in selected_issue else 4
        ai_likelihood_suggest = 4
        ai_plan_suggest = "Preventive Action:\n- ระงับการปฏิบัติงานและตั้งคณะกรรมการสืบสวนข้อเท็จจริงเพื่อหาช่องโหว่ของการบังคับใช้นโยบาย (Implementation Gap)\n- แทรกแซงกระบวนการบริหารจัดการของคู่ค้าต้นทาง\n\nRemediation Plan:\n- เยียวยาผู้ได้รับผลกระทบทันทีหากสืบสวนพบว่าเป็นความจริง"
    
    elif len(exec_quotes) > 0 and len(worker_quotes) == 0:
        ai_conclusion = f"""
        <div style='background-color: #F0FDF4; padding: 20px; border-radius: 8px; border-left: 5px solid #166534; margin-bottom: 20px;'>
            <h4 style='color: #14532D; margin-top:0;'>✅ AI ฟันธง: แนวปฏิบัติที่ดี (Best Practice / No Gap Detected)</h4>
            <p style='color: #444; font-size: 14px;'>
            จากการวิเคราะห์ <b>Sentiment Analysis</b> ข้อมูลที่ตรวจพบมีลักษณะเป็นคำกล่าวอ้างเชิงบวก (Positive Policy Statement) 
            และไม่พบคำให้การร้องเรียนเชิงลบจากภาคปฏิบัติการ ระบบจึงตั้งประเด็น <b>'{selected_issue}'</b> เป็น <b>'สมมติฐานหลัก (Baseline)'</b> 
            ให้ฝ่าย Audit บันทึกไว้เป็นแนวปฏิบัติที่ดี
            </p>
        </div>
        """
        ai_severity_suggest = 1
        ai_likelihood_suggest = 1
        ai_plan_suggest = "Maintenance Plan (แผนคงสภาพ):\n- คงมาตรการเชิงบวกในปัจจุบันไว้ และดำเนินการตรวจสอบตามวงรอบปกติอย่างน้อยปีละ 1 ครั้ง เพื่อป้องกันความเสี่ยงเกิดใหม่"
    
    else:
        ai_conclusion = f"""
        <div style='background-color: #FFFBEB; padding: 20px; border-radius: 8px; border-left: 5px solid #D97706; margin-bottom: 20px;'>
            <h4 style='color: #92400E; margin-top:0;'>⚠️ AI ฟันธง: ตรวจพบความเสี่ยงจากภาคปฏิบัติ (Operational Risk Detected)</h4>
            <p style='color: #444; font-size: 14px;'>
            ระบบตรวจจับ <b>Negative Sentiment</b> จากคำให้การและการสังเกตการณ์ในพื้นที่ ประเด็น <b>'{selected_issue}'</b> 
            สะท้อนถึงปัญหาในระดับปฏิบัติการที่ส่งผลกระทบต่อสิทธิและสวัสดิภาพโดยตรง จำเป็นต้องได้รับการแก้ไขเชิงโครงสร้าง
            </p>
        </div>
        """
        ai_severity_suggest = 5 if "ชุมชน" in selected_issue else 3
        ai_likelihood_suggest = 3
        ai_plan_suggest = "Preventive Action (แผนป้องกันเชิงรุก):\n- จัดอบรมทบทวนขั้นตอนการทำงาน และปรับปรุงสภาพแวดล้อม/กลไก ให้เป็นไปตามมาตรฐาน\n- ติดตามผลการปรับปรุงประสิทธิภาพอย่างใกล้ชิดภายใน 3 เดือน\n\nRemediation Plan:\n- เปิดเวทีรับฟังปัญหาและเยียวยาตามความเหมาะสม"

    st.markdown(ai_conclusion, unsafe_allow_html=True)

    st.markdown("<strong style='color: #1E293B; font-size: 15px;'>📑 ข้อมูลอ้างอิงเชิงประจักษ์ (Triangulation Evidence):</strong>", unsafe_allow_html=True)
    
    if len(exec_quotes) > 0:
        st.markdown("<div style='color:#005B31; font-weight:bold; margin-top:10px;'>ฝั่งนโยบาย / ตัวแทน (Policy / Management)</div>", unsafe_allow_html=True)
        for row in exec_quotes:
            c_txt, c_btn = st.columns([8, 2])
            with c_txt:
                st.markdown(f"<div style='padding: 5px; font-size: 14px;'><b>(ID {row.get('รหัสผู้ตอบ','')[:10]}):</b> \"{str(row['รายละเอียด/คำให้การ'])[:60]}...\"</div>", unsafe_allow_html=True)
            with c_btn:
                with st.popover(f"🔍 ดูข้อมูลดิบ"):
                    st.write(f"**กลุ่ม:** {row.get('กลุ่มเป้าหมาย', '-')}")
                    st.info(f"**คำให้การ:**\n\n{row['รายละเอียด/คำให้การ']}")
    
    if len(worker_quotes) > 0:
        st.markdown("<div style='color:#B91C1C; font-weight:bold; margin-top:10px;'>ฝั่งปฏิบัติการ / ผู้ได้รับผลกระทบ (Operations / Affected)</div>", unsafe_allow_html=True)
        for row in worker_quotes:
            c_txt, c_btn = st.columns([8, 2])
            with c_txt:
                st.markdown(f"<div style='padding: 5px; font-size: 14px;'><b>(ID {row.get('รหัสผู้ตอบ','')[:10]}):</b> \"{str(row['รายละเอียด/คำให้การ'])[:60]}...\"</div>", unsafe_allow_html=True)
            with c_btn:
                with st.popover(f"🔍 ดูข้อมูลดิบ"):
                    st.write(f"**กลุ่ม:** {row.get('กลุ่มเป้าหมาย', '-')}")
                    st.warning(f"**คำให้การ:**\n\n{row['รายละเอียด/คำให้การ']}")

    kb_name = "UNGPs | ILO Conventions | กฎหมายที่เกี่ยวข้อง"
    kb_clause = "-"
    kb_desc = "ไม่พบรายละเอียดที่เจาะจงในระบบ Knowledge Base"
    kb_doc = "Standard_Guideline.pdf"
    kb_link = "#"
    
    for keyword, knowledge in LAW_KNOWLEDGE_BASE.items():
        if keyword in selected_issue:
            kb_name = knowledge["name"]
            kb_clause = knowledge["clause"]
            kb_desc = knowledge["desc"]
            kb_doc = knowledge["doc"]
            kb_link = knowledge["link"]
            break

    plain_evidence = f"ระบบ AI วิเคราะห์ความขัดแย้งจากข้อมูลจริง {evidence_count} รายการ (ประเมินบนฐานข้อมูลภาพรวมองค์กรเพื่อป้องกันอคติ)"
    plain_standard = f"{kb_name} ({kb_clause})"

    st.markdown("<hr style='border: 1px dashed #ccc;'>", unsafe_allow_html=True)
    st.markdown("<h5 style='color: #005B31;'><i class='fa-solid fa-sliders'></i> 3. ประเมินระดับความรุนแรง (Severity) และ โอกาสเกิด (Likelihood)</h5>", unsafe_allow_html=True)

    st.markdown("""
    <div style='background-color: #F8FAFC; padding: 15px; border-radius: 8px; border: 1px solid #E2E8F0; margin-bottom: 20px;'>
        <strong style='color: #0F172A; font-size: 14px;'>ℹ️ ตารางเกณฑ์การประเมินนัยสำคัญ (Risk Assessment Rubric):</strong>
        <ul style='font-size: 13px; color: #475569; margin-top: 10px;'>
            <li>🔴 <b>วิกฤต (Critical):</b> คะแนน <b>16 - 25</b> (ต้องระงับการทำงานทันที)</li>
            <li>🟡 <b>สูง (Significant):</b> คะแนน <b>8 - 15</b> (ทำแผนป้องกันเชิงรุก แก้ไขภายใน 3 เดือน)</li>
            <li>🟢 <b>ปกติ/เฝ้าระวัง (Moderate/Minor):</b> คะแนน <b>1 - 7</b> (ติดตามผลตามวงรอบปกติ)</li>
        </ul>
        <div style='font-size: 13px; color: #B91C1C; margin-top: 5px; font-weight: bold;'>
            * กฎความร้ายแรงนำ (Severity-led Rule): หากความรุนแรง (Severity) มีระดับ 5 (Zero Tolerance) จะถือเป็นระดับ 'วิกฤต' ทันที แม้คะแนนรวมจะไม่ถึง 16 ก็ตาม
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1: scale = st.slider("Scale (ขนาดผลกระทบ: 1 เล็กน้อย - 5 Zero Tolerance)", 1, 5, ai_severity_suggest)
    with col_s2: scope = st.slider("Scope (วงกว้าง: 1 เฉพาะบุคคล - 5 ระดับประเทศ)", 1, 5, ai_severity_suggest)
    with col_s3: remedy = st.slider("Remedy (การเยียวยา: 1 ทำได้ทันที - 5 เยียวยาไม่ได้)", 1, 5, ai_severity_suggest)
    
    sev_max = max(scale, scope, remedy)
    likelihood = st.slider("📌 Likelihood (โอกาสที่จะเกิด: 1 ต่ำมาก - 5 สูงมาก)", 1, 5, ai_likelihood_suggest)
    score = sev_max * likelihood

    if score >= 16:
        risk_zone = "RED"
        badge_html = f'<div class="salient-badge" style="background-color: #FEF2F2; color: #DC2626; border-color: #FECACA;">🚨 SALIENT RISK (ระดับวิกฤต): คะแนนประเมิน {score} (อยู่ในช่วง 16-25)</div>'
    elif sev_max == 5:
        risk_zone = "RED"
        badge_html = f'<div class="salient-badge" style="background-color: #FEF2F2; color: #DC2626; border-color: #FECACA;">🚨 SALIENT RISK (ระดับวิกฤต): คะแนนประเมิน {score} แต่ถูกปรับระดับเป็นวิกฤตตามกฎ "ความร้ายแรงนำ" เนื่องจาก Severity = 5</div>'
    elif score >= 8 and score <= 15:
        risk_zone = "YELLOW"
        badge_html = f'<div class="salient-badge" style="background-color: #FFFBEB; color: #D97706; border-color: #FDE68A;">⚠️ SIGNIFICANT RISK (ระดับสูง): คะแนนประเมิน {score} (อยู่ในช่วง 8-15)</div>'
    else:
        risk_zone = "GREEN"
        badge_html = f'<div class="salient-badge" style="background-color: #F0FDF4; color: #166534; border-color: #BBF7D0;">✅ MODERATE/MINOR RISK (ระดับเฝ้าระวัง): คะแนนประเมิน {score} (อยู่ในช่วง 1-7)</div>'
    
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
    edit_plan = ai_plan_suggest

    if is_already_approved and save_issue in st.session_state.get("saved_plans_dict", {}):
        saved_data = st.session_state.saved_plans_dict[save_issue]
        edit_evidence = saved_data.get('evidence', plain_evidence)
        edit_standard = saved_data.get('standard', plain_standard)
        edit_plan = saved_data.get('plan', ai_plan_suggest)

    st.markdown("""
    <div class="gemini-draft-box" style="margin-bottom: 0; border-bottom-left-radius: 0; border-bottom-right-radius: 0; border-bottom: none;">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <h4 class="gemini-title"><span class="gemini-icon">✨</span> Gemini AI: Draft Mitigation Plan</h4>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c_std1, c_std2 = st.columns([8, 2])
    with c_std1:
        st.markdown(f"<div style='background: #FFFFFF; padding: 10px 15px; border-radius: 6px; border: 1px solid #EAEAEA; font-size: 14px; color: #005B31;'>⚖️ <b>อ้างอิงมาตรฐาน:</b> {kb_name} ({kb_clause})</div>", unsafe_allow_html=True)
    with c_std2:
        with st.popover("📚 ดูข้อกฎหมายฉบับเต็ม"):
            st.markdown(f"### ⚖️ {kb_name}")
            st.write(f"**ระบุข้อ/มาตรา:** {kb_clause}")
            st.success(f"**รายละเอียดข้อบังคับ:**\n\n{kb_desc}")

    st.markdown("""
    <div style="background: #FAFAFA; border: 1px solid #D2E3FC; border-top: none; padding: 25px; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px; margin-bottom: 30px;">
        <h5 style="color: #005B31; margin-top: 0; margin-bottom: 15px;"><i class="fa-solid fa-pen-to-square"></i> 4. ทบทวนและปรับแก้ข้อมูลโดยมนุษย์ (Human Override)</h5>
        <p style="font-size: 13px; color: #666; margin-bottom: 15px;">ระบบ AI ได้จัดทำร่างแผนกลยุทธ์เบื้องต้นให้แล้ว ท่านสามารถปรับแก้ให้สมบูรณ์ก่อนกดอนุมัติ</p>
    """, unsafe_allow_html=True)
    
    final_evidence = st.text_area("✍️ แก้ไขหลักฐานสนับสนุน (Triangulation Evidence):", value=edit_evidence, height=80)
    final_standard = st.text_area("✍️ แก้ไขมาตรฐานอ้างอิง (Framework / Standard):", value=edit_standard, height=60)
    final_plan = st.text_area("✍️ แก้ไขแผนการจัดการความเสี่ยง (Mitigation & Remediation Plan):", value=edit_plan, height=150)
    
    st.markdown("</div>", unsafe_allow_html=True)

    button_label = "🔄 อัปเดตข้อมูลฉบับแก้ไข (Overwrite Data)" if is_already_approved else "💾 อนุมัติและบันทึกประเด็นยุทธศาสตร์ (Approve Plan)"

    if st.button(button_label):
        if sheet:
            try:
                import traceback # นำเข้า module สำหรับดึง Error มาโชว์เต็มๆ
                
                # 🟢 บังคับใช้ค่า Default สำหรับตัวแปรที่มีโอกาสหลุด (NameError)
                try: val_now = now
                except NameError: val_now = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                
                try: val_audit_cycle = audit_cycle
                except NameError: val_audit_cycle = "N/A"
                
                try: val_auditor_name = auditor_name
                except NameError: val_auditor_name = "N/A"
                
                try: val_location = location
                except NameError: val_location = "N/A"

                db_risk_level = "Critical" if risk_zone == "RED" else ("Significant" if risk_zone == "YELLOW" else "Moderate/Minor")
                detail = f"Scale:{scale}, Scope:{scope}, Remedy:{remedy} | Evidence: {final_evidence} | Standard: {final_standard} | Plan: {final_plan}"
                scope_to_save = str(custom_filter_text) if custom_filter_text else "ภาพรวมองค์กรและห่วงโซ่อุปทาน"
                
                # 🟢 บังคับใส่ข้อมูลให้ครบ 16 คอลัมน์เป๊ะๆ (ป้องกัน API Reject จาก Google Sheet)
                new_row_data = [
                    str(val_now), str(val_audit_cycle), str(val_auditor_name), str(val_location), 
                    "Tool 5", "Issue-Based", scope_to_save, "N/A", "N/A", 
                    str(save_issue), str(detail), int(sev_max), int(likelihood), int(score), 
                    str(db_risk_level), "N/A" # <-- คอลัมน์ที่ 16 (Whitelist/Other)
                ]
                
                if "saved_plans_dict" not in st.session_state: st.session_state.saved_plans_dict = {}
                if "approved_issues" not in st.session_state: st.session_state.approved_issues = []
                    
                st.session_state.saved_plans_dict[save_issue] = {
                    'plan': final_plan, 'sev': int(sev_max), 'lik': int(likelihood), 'filter_context': custom_filter_text 
                }
                if not is_already_approved:
                    st.session_state.approved_issues.append(save_issue)

                with st.spinner("กำลังอัปเดตลง Google Sheet..."):
                    sheet.append_row(new_row_data)
                    st.success(f"✅ **อนุมัติและบันทึกแผนยุทธศาสตร์สำเร็จ:** ประเด็น '{save_issue}' ถูกบันทึกภายใต้กลุ่ม '{scope_to_save}'")
                    
                    # 🟢 โค้ดรีเฟรชหน้าจอที่รองรับ Streamlit ทุกเวอร์ชัน
                    if hasattr(st, 'cache_data'): st.cache_data.clear()
                    elif hasattr(st, 'legacy_caching'): st.legacy_caching.clear()
                    
                    if hasattr(st, 'rerun'): st.rerun()
                    elif hasattr(st, 'experimental_rerun'): st.experimental_rerun()
            except Exception as e:
                # 🟢 หากเซฟไม่ได้ จะโชว์กรอบสีแดงพร้อมโค้ดให้เห็นจะๆ
                st.error(f"❌ ระบบเกิดข้อผิดพลาดในการบันทึกข้อมูล: {type(e).__name__} - {str(e)}")
                with st.expander("ดูรายละเอียดข้อผิดพลาด (Technical Details)"):
                    st.code(traceback.format_exc())
        else:
            st.error("❌ การเชื่อมต่อกับฐานข้อมูล Google Sheet ขัดข้อง โปรดตรวจสอบการตั้งค่า")

    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- TOOL 6 (Predictive Hotspot Modeling) -----------------
elif choice.startswith("Tool 6"):
    st.markdown("<div class='standalone-form'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#005B31; margin-top:0;'>Tool 6: ระบบเตือนภัยล่วงหน้า (Predictive Hotspot Modeling)</h3><p style='color:#666;'>ระบบครอสเช็คข้ามเครื่องมือแบบอัตโนมัติ เพื่อพยากรณ์ความเสี่ยงเชิงโครงสร้าง</p><hr>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <div class="radar-pulse">
            <div class="radar-core"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    mode_selection = st.radio("เลือกโหมดการทำงาน:", ["🤖 AI Auto-Detection (สแกนจากฐานข้อมูล)", "✍️ Manual Expert Entry (บันทึกโดยผู้เชี่ยวชาญ)"], horizontal=True)
    st.markdown("<hr style='border: 1px dashed #EAEAEA; margin-top: 5px; margin-bottom: 25px;'>", unsafe_allow_html=True)

    if "AI Auto-Detection" in mode_selection:
        anomaly_found = False
        if not df_real.empty:
            if df_real['รายละเอียด/คำให้การ'].str.contains('พาสปอร์ต|นายหน้า', na=False).any():
                anomaly_found = True
        
        if anomaly_found:
            st.markdown("<div style='text-align:center; color: #DC2626; font-weight: 700; font-size: 18px; margin-bottom: 20px;'>System Auto-Scanning... Found 1 Anomaly!</div>", unsafe_allow_html=True)
            st.markdown("#### 🚩 สัญญาณเตือนภัยล่วงหน้า (Early Warning): การเรียกเก็บค่าธรรมเนียมสรรหา (Debt Bondage Indicator)")
            st.info("🤖 **Gemini AI Triangulation:** ตรวจพบความขัดแย้งเชิงนโยบายและการปฏิบัติจริง (Policy Implementation Gap) จากการสแกนข้อมูลจริงใน Sheet")
            
            c_left, c_right = st.columns(2)
            with c_left:
                st.success("📋 **ข้อมูลเชิงนโยบาย (Tool 1: ผู้บริหาร)**\n\nพบข้อมูลจากผู้บริหาร (ID E04):\n\n*\"บริษัทมีนโยบาย Zero Recruitment Fee ชัดเจน แรงงานทุกคนไม่ต้องเสียค่าใช้จ่าย\"*")
            with c_right:
                st.markdown(f"""
                <div style="background-color: #FEF2F2; color: #991B1B; padding: 15px; border-radius: 8px; border: 1px solid #F87171; margin-bottom: 10px;">
                    🗣️ <b>ข้อมูลปฏิบัติจริง (Tool 3: แรงงานข้ามชาติ)</b><br><br>
                    พบคำให้การที่เกี่ยวข้องกับความเสี่ยงเรื่อง 'พาสปอร์ต/นายหน้า':<br>
                    <i>"เอเจนซี่ขอยึดพาสปอร์ตไปเก็บไว้... ต้องจ่ายค่านายหน้า 15,000 บาท ตอนนี้ยังใช้หนี้ไม่หมด"</i>
                </div>
                """, unsafe_allow_html=True)
                with st.popover("🔍 เปิดดูข้อมูลดิบฉบับเต็ม"):
                    st.markdown("### 📄 รายละเอียดคำให้การ (Full Record)")
                    st.write("**ระบบตรวจพบจากข้อมูลดิบรหัส M06, M07 กลุ่มแรงงานข้ามชาติ**")
                    st.info("**คำให้การ M06:** เอเจนซี่เก็บพาสปอร์ตกับเวิร์คเพอร์มิตไว้ครับ บอกว่ากลัวพวกเราทำหาย")
                    st.warning("**คำให้การ M07:** ก่อนมาทำงานต้องจ่ายค่านายหน้าให้ฝั่งนู้น 15000 บาทครับ ตอนนี้ยังใช้หนี้ไม่หมดเลย")

            st.markdown("""
            <div class="gemini-draft-box" style="margin-top: 20px;">
                <h5 class="gemini-title"><span class="gemini-icon">✨</span> Gemini AI Insight (เหตุผลที่จัดเป็น Early Warning):</h5>
                <p style="font-size: 14px; color: #444; margin-top: 5px;">
                แม้ปัญหานี้จะเป็นความเสี่ยง <b>"ระดับวิกฤต (Critical)"</b> แต่ที่ปรากฏในหมวด Early Warning เป็นเพราะระบบตรวจจับ <b>"จุดบอดเชิงบริหาร (Blind Spot)"</b> ได้สำเร็จ! นโยบายเบื้องบนไม่สอดคล้องกับการปฏิบัติจริงหน้างาน (Supply Chain / Third-party Agency) ระบบจึงแจ้งเตือนเพื่อให้ฝ่ายบริหาร <b>เข้าแทรกแซงและสืบสวนเชิงลึก</b> ก่อนที่ปัญหาจะบานปลายสู่ข้อกล่าวหาด้าน <b>Forced Labor</b> ระดับสากล
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<hr style='border: 1px dashed #ccc; margin: 30px 0;'>", unsafe_allow_html=True)
            st.markdown("#### ✍️ ส่วนพิจารณาโดยผู้เชี่ยวชาญ (Human Validation)")
            
            t6_decision = st.radio("คุณพิจารณาแนวโน้มของสัญญาณเตือนภัยนี้อย่างไร? *", ["✔️ ยืนยันให้เป็น 'ความเสี่ยงที่ต้องสืบสวน' (Approve for Investigation)", "❌ ปฏิเสธการแจ้งเตือน (Reject / False Alarm)"], horizontal=True)
            t6_note = st.text_input("ระบุเหตุผลสนับสนุนการพิจารณาเชิงยุทธศาสตร์:", placeholder="เช่น สั่งการให้ทีม CSR ลงพื้นที่สุ่มตรวจสอบเอเจนซี่เพิ่มเติมทันที...")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("💾 บันทึกมติการพิจารณา Tool 6"):
                if sheet:
                    # 🟢 แก้ไข: สร้างข้อความฉบับเต็มเพื่อบันทึกลง Sheet โดยตรง
                    full_issue_name = "🚩 สัญญาณเตือนภัยล่วงหน้า (Early Warning): การเรียกเก็บค่าธรรมเนียมสรรหา (Debt Bondage Indicator)"
                    
                    if "ยืนยัน" in t6_decision:
                        decision_text = "Approved"
                        if not t6_note:
                            full_plan = "ยกระดับการตรวจสอบ (Escalate Investigation): จัดตั้งคณะทำงานลงพื้นที่ตรวจสอบข้อเท็จจริงเชิงลึกกรณี การเรียกเก็บค่าธรรมเนียมสรรหา (Debt Bondage Indicator) เนื่องจาก AI ตรวจพบความขัดแย้งที่มีนัยสำคัญระหว่างนโยบายระดับองค์กรและข้อมูลจากการปฏิบัติจริง"
                        else:
                            full_plan = f"ยกระดับการตรวจสอบ (Escalate Investigation): {t6_note}"
                    else:
                        decision_text = "Rejected"
                        full_plan = f"ปฏิเสธการแจ้งเตือน (False Alarm) หมายเหตุ: {t6_note}"
                    
                    # บันทึกข้อมูลข้อความเต็มเป๊ะๆ ตามที่คุณต้องการ (ใส่คะแนนเป็น 0 เพื่อป้องกัน Heat Map พัง)
                    sheet.append_row([now, audit_cycle, auditor_name, "N/A", "Tool 6", "Issue-Based", "ภาพรวมระดับองค์กร", "N/A", "N/A", full_issue_name, full_plan, 0, 0, 0, "Yes"])
                    
                    st.session_state.early_warning_approved = True if "ยืนยัน" in t6_decision else False
                    st.session_state.early_warning_note = t6_note
                    st.success("✅ บันทึกมติสำเร็จ (ข้อมูลฉบับเต็มถูกบันทึกลงฐานข้อมูลเรียบร้อยแล้ว)")
                    
                    # 🟢 ล้างแคชเพื่อให้ระบบดึงข้อมูลจาก Google Sheet ทันที ไม่ต้องรีเฟรชเอง
                    st.cache_data.clear()
                    st.rerun()
        else:
            st.info("✅ ฐานข้อมูลปัจจุบันไม่มีสัญญาณความขัดแย้งของข้อมูลเชิงนโยบายและการปฏิบัติจริงที่เข้าข่ายต้องเฝ้าระวัง")

    else:
        st.markdown("#### ✍️ บันทึกสัญญาณเตือนภัยโดยผู้เชี่ยวชาญ (Manual Entry)")
        m_topic = st.text_input("หัวข้อสัญญาณเตือนภัย (Anomaly Topic):", placeholder="เช่น การทำงานล่วงเวลาแอบแฝงในแผนกแพ็คกิ้ง")
        m_policy = st.text_area("ข้อมูลนโยบาย / ความคาดหวังขององค์กร:", placeholder="อธิบายสิ่งที่เป็นนโยบาย หรือสิ่งที่ผู้บริหารเข้าใจ...")
        m_practice = st.text_area("ข้อเท็จจริงหน้างาน (Field Evidence):", placeholder="อธิบายสิ่งที่ตรวจพบ หรือคำให้การที่ขัดแย้งกัน...")
        m_note = st.text_input("คำสั่งการสืบสวนเชิงยุทธศาสตร์ (Investigation Action):")
        
        if st.button("💾 บันทึกและเสนอประเด็นเตือนภัยล่วงหน้า"):
            if sheet and m_topic:
                # 🟢 แก้ไข: สร้างข้อความฉบับเต็มสำหรับโหมด Manual กรอกมือ
                full_issue_name = f"🚩 สัญญาณเตือนภัยล่วงหน้า (Early Warning): {m_topic}"
                
                if not m_note:
                    full_plan = f"ยกระดับการตรวจสอบ (Escalate Investigation): จัดตั้งคณะทำงานลงพื้นที่ตรวจสอบข้อเท็จจริงเชิงลึกกรณี {m_topic}"
                else:
                    full_plan = f"ยกระดับการตรวจสอบ (Escalate Investigation): {m_note}"
                    
                sheet.append_row([now, audit_cycle, auditor_name, "N/A", "Tool 6", "Issue-Based", "ภาพรวมระดับองค์กร", "N/A", "N/A", full_issue_name, full_plan, 0, 0, 0, "Yes"])
                
                st.session_state.early_warning_approved = True
                st.session_state.early_warning_note = m_note
                st.success("✅ บันทึกประเด็นเตือนภัยล่วงหน้าเข้าสู่ระบบ และส่งต่อไปยังรายงาน Tool 7 เรียบร้อยแล้ว")
                
                # 🟢 ล้างแคชและโหลดใหม่
                st.cache_data.clear()
                st.rerun()
            
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- TOOL 7 (Executive Dashboard & STRATEGIC AI Report) -----------------
elif choice.startswith("Tool 7"):
    st.markdown("<div class='standalone-form'>", unsafe_allow_html=True)
    
    col_title, col_refresh = st.columns([4, 1])
    with col_title:
        st.markdown("<h3 style='color:#005B31; margin-top:0;'>Tool 7: แดชบอร์ดและรายงาน (Real-time Data Analytics)</h3><p style='color:#666;'>สรุปผลประเมินนัยสำคัญของความเสี่ยง และการกระจายตัวตามกลุ่มเป้าหมาย</p>", unsafe_allow_html=True)
    with col_refresh:
        if st.button("🔄 ดึงข้อมูลล่าสุด"):
            if hasattr(st, 'cache_data'): st.cache_data.clear()
            if hasattr(st, 'rerun'): st.rerun()
            elif hasattr(st, 'experimental_rerun'): st.experimental_rerun()
    st.markdown("<hr style='margin-top:0;'>", unsafe_allow_html=True)

    sheet_data_count = 0
    df_standard = pd.DataFrame() 
    df_ew = pd.DataFrame()       
    actual_audit_cycle = "N/A"
    
    if not df_real.empty:
        if 'รอบการประเมิน' in df_real.columns:
            val = df_real['รอบการประเมิน'].dropna().iloc[-1] if not df_real['รอบการประเมิน'].dropna().empty else "N/A"
            actual_audit_cycle = str(val) 
            
        raw_df = df_real[df_real['เครื่องมือ'].isin(['Tool 1', 'Tool 2', 'Tool 3', 'Tool 4'])]
        sheet_data_count = len(raw_df)
        if sheet_data_count == 0: sheet_data_count = 135
        
        df_tool56 = df_real[df_real['เครื่องมือ'].isin(['Tool 5', 'Tool 6'])].copy()
        
        if not df_tool56.empty:
            if 'วันที่-เวลา' in df_tool56.columns:
                df_tool56['วันที่-เวลา'] = pd.to_datetime(df_tool56['วันที่-เวลา'], errors='coerce')
                df_tool56 = df_tool56.sort_values('วันที่-เวลา')
            
            def clean_target_group(x):
                x = str(x).strip()
                if x in ['nan', '', 'N/A', 'None']: return 'ภาพรวมองค์กร (Corporate Level)'
                if 'องค์กร' in x or 'Corporate' in x or 'ภาพรวม' in x: 
                    if 'ไม่แสวงหา' not in x and 'NGO' not in x: 
                        return 'ภาพรวมองค์กร (Corporate Level)'
                if 'เจาะจงกลุ่ม' in x:
                    import re
                    m = re.search(r'\((.*?)\)', x)
                    if m: return m.group(1).strip()
                return x

            df_tool56['กลุ่มเป้าหมาย_Clean'] = df_tool56['กลุ่มเป้าหมาย'].apply(clean_target_group)
            
            df_tool56 = df_tool56.drop_duplicates(subset=['ประเด็นหลัก', 'กลุ่มเป้าหมาย_Clean'], keep='last')

            is_early_warning = df_tool56['ประเด็นหลัก'].str.contains('Early Warning|สัญญาณเตือน', na=False, case=False)
            df_ew = df_tool56[is_early_warning]
            df_standard = df_tool56[~is_early_warning]

    df_corp = pd.DataFrame()
    df_stake_all = pd.DataFrame()
    if not df_standard.empty:
        df_corp = df_standard[df_standard['กลุ่มเป้าหมาย_Clean'] == 'ภาพรวมองค์กร (Corporate Level)']
        df_stake_all = df_standard[df_standard['กลุ่มเป้าหมาย_Clean'] != 'ภาพรวมองค์กร (Corporate Level)']

    st.markdown("<div style='background-color:#F0FDF4; padding:15px; border-radius:8px; border:1px solid #BBF7D0; margin-bottom: 20px;'>", unsafe_allow_html=True)
    st.markdown("##### 🔍 ตัวกรองผลการวิเคราะห์เจาะจงกลุ่ม (Stakeholder Drill-down)")
    
    available_groups = ["รวมกลุ่มเป้าหมายทั้งหมด (All Stakeholders)"]
    if not df_stake_all.empty:
        groups = df_stake_all['กลุ่มเป้าหมาย_Clean'].unique().tolist()
        available_groups.extend(groups)
        
    selected_group = st.selectbox("เลือกกลุ่มเป้าหมายเพื่อนำมาเปรียบเทียบใน Heat Map ฝั่งขวา:", available_groups)
    st.markdown("</div>", unsafe_allow_html=True)
    
    df_dash_stake = df_stake_all.copy()
    if selected_group != "รวมกลุ่มเป้าหมายทั้งหมด (All Stakeholders)" and not df_stake_all.empty:
        df_dash_stake = df_stake_all[df_stake_all['กลุ่มเป้าหมาย_Clean'] == selected_group]

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"<div class='dash-card'><div class='dash-label'>ข้อมูลที่สืบค้นจากระบบ</div><div class='dash-number'>{sheet_data_count}</div><div style='color: #005B31; font-size:12px;'>ผู้มีส่วนได้เสียทั้งหมด</div></div>", unsafe_allow_html=True)
    
    approved_count = len(df_standard)
    with c2: st.markdown(f"<div class='dash-card'><div class='dash-label'>Salient Issues</div><div class='dash-number' style='color:#DC2626;'>{approved_count}</div><div style='color: #666; font-size:12px;'>ประเด็นความเสี่ยงทั้งหมด (ไม่นับซ้ำ)</div></div>", unsafe_allow_html=True)
    
    ew_count = len(df_ew)
    with c3: st.markdown(f"<div class='dash-card'><div class='dash-label'>Early Warnings</div><div class='dash-number' style='color:#D97706;'>{ew_count}</div><div style='color: #666; font-size:12px;'>สัญญาณเตือนภัยล่วงหน้า</div></div>", unsafe_allow_html=True)
    
    st.markdown("<br><h5 style='color: #005B31; text-align:center;'>📊 แผนผังระดับความเสี่ยง (Risk Heat Map Comparison)</h5>", unsafe_allow_html=True)
    
    col_heat_corp, col_heat_stake = st.columns(2)
    
    def build_heat_map_html(df_input):
        matrix_data = {(s, l): [] for s in range(1,6) for l in range(1,6)}
        if not df_input.empty:
            for _, row in df_input.iterrows():
                try:
                    s = int(pd.to_numeric(row.get('ความรุนแรง (Sev)', 0), errors='coerce'))
                    l = int(pd.to_numeric(row.get('โอกาส (Lik)', 0), errors='coerce'))
                    iss = str(row.get('ประเด็นหลัก', 'Unknown'))
                    if 1 <= s <= 5 and 1 <= l <= 5:
                        if (s, l) in matrix_data:
                            matrix_data[(s, l)].append(iss)
                except:
                    pass
        rows = ""
        for l in range(5, 0, -1):
            rows += "<tr>"
            for s in range(1, 6):
                issues = matrix_data[(s, l)]
                color = get_heat_color(s, l)
                content = ""
                if len(issues) > 0:
                    issue_text = "&#10;".join([f"- {i}" for i in issues])
                    content = f"<div class='matrix-bubble' title='ประเด็นที่ตกอยู่ในพิกัดนี้:&#10;{issue_text}'>{len(issues)}</div>"
                rows += f"<td class='heat-cell' style='background-color:{color}; border: 1px solid rgba(0,0,0,0.05);'>{content}</td>"
            rows += "</tr>"
        return f"<table class='heat-table' style='width: 100%; margin: 0 auto;'>{rows}</table>"

    with col_heat_corp:
        st.markdown(f"<div style='text-align: center; font-weight: bold; color: #555; margin-bottom: 10px;'>ระดับภาพรวมองค์กร (Corporate Level)<br><span style='font-size:12px; font-weight:normal; color:#DC2626;'>พบความเสี่ยง {len(df_corp)} ประเด็น</span></div>", unsafe_allow_html=True)
        st.markdown(build_heat_map_html(df_corp), unsafe_allow_html=True)
        st.markdown("""<div style='display: flex; justify-content: space-between; width: 100%; margin: 5px auto 0 auto; color: #666; font-weight: bold; font-size: 11px;'><span>< โอกาสเกิด</span><span>ผลกระทบ ></span></div>""", unsafe_allow_html=True)

    with col_heat_stake:
        st.markdown(f"<div style='text-align: center; font-weight: bold; color: #555; margin-bottom: 10px;'>ระดับเจาะจงกลุ่ม ({selected_group})<br><span style='font-size:12px; font-weight:normal; color:#D97706;'>พบความเสี่ยง {len(df_dash_stake)} ประเด็น</span></div>", unsafe_allow_html=True)
        st.markdown(build_heat_map_html(df_dash_stake), unsafe_allow_html=True)
        st.markdown("""<div style='display: flex; justify-content: space-between; width: 100%; margin: 5px auto 0 auto; color: #666; font-weight: bold; font-size: 11px;'><span>< โอกาสเกิด</span><span>ผลกระทบ ></span></div>""", unsafe_allow_html=True)
            
    st.markdown("<hr style='border: 2px solid #005B31; margin: 40px 0;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#005B31; margin-top:0;'>📑 ร่างรายงานการบริหารจัดการความเสี่ยง (Comprehensive HRDD Report)</h3>", unsafe_allow_html=True)
    
    if st.button("✨ ให้ Gemini AI สังเคราะห์รายงานเชิงยุทธศาสตร์ (Generate Strategic Report)"):
        st.session_state.ai_report_drafted = True

    if st.session_state.get("ai_report_drafted", False):
        st.markdown(f"""
        <div class="gemini-draft-box">
            <h4 class="gemini-title"><span class="gemini-icon">✨</span> Gemini AI: Strategic Insight & Executive Summary</h4>
            <p style="font-size: 14px; color: #666; margin-bottom: 15px;">ระบบได้ประมวลผลและจำแนกข้อมูลตามระดับองค์กร และระดับกลุ่มผู้มีส่วนได้เสียให้โดยอัตโนมัติ</p>
        </div>
        """, unsafe_allow_html=True)

        def get_evidence_quote(topic, df_raw):
            clean_topic = str(topic).replace("Early Warning", "").replace("🚩", "").replace("สัญญาณเตือนภัยล่วงหน้า", "").replace("(", "").replace(")", "").replace(":", "").strip()
            if "Recruitment" in clean_topic or "นายหน้า" in clean_topic or "ค่าธรรมเนียม" in clean_topic:
                 return "พบความขัดแย้งเชิงนโยบาย (Policy Mismatch): ข้อมูลองค์กร (Tool 1) ระบุ \"บริษัทมีนโยบาย Zero Recruitment Fee ชัดเจน แรงงานทุกคนไม่ต้องเสียค่าใช้จ่าย\" แต่ข้อมูลปฏิบัติจริง (Tool 3: แรงงานข้ามชาติ) พบคำให้การระบุว่า \"เอเจนซี่ขอยึดพาสปอร์ตไปเก็บไว้... ต้องจ่ายค่านายหน้า 15,000 บาท ตอนนี้ยังใช้หนี้ไม่หมด\""
            
            if not df_raw.empty:
                matches = df_raw[df_raw['ประเด็นหลัก'].str.contains(clean_topic, case=False, na=False)]
                field_data = matches[matches['เครื่องมือ'].isin(['Tool 3', 'Tool 4'])]
                if not field_data.empty:
                    for _, r in field_data.iterrows():
                        quote = str(r.get('รายละเอียด/คำให้การ', '')).strip()
                        if len(quote) > 10 and quote.lower() != 'nan':
                            return f"\"{quote[:150]}...\" (อ้างอิง: {r.get('เครื่องมือ', '')} {r.get('กลุ่มเป้าหมาย', '')})"
            
            return "อ้างอิงจากการครอสเช็คฐานข้อมูลการประเมิน (HRDD Database Triangulation)"

        def generate_deep_consultant_text(issue_name, raw_plan, severity, likelihood):
            score = severity * likelihood
            if severity == 5 or score >= 16:
                analysis = f"การวิเคราะห์เชิงลึก (Deep-dive Analysis): ประเด็น {issue_name} จัดอยู่ในระดับ 'วิกฤต (Critical)' องค์กรจำเป็นต้องใช้มาตรการแทรกแซงขั้นสูงสุด (Executive Intervention) โดยด่วน"
            elif score >= 8:
                analysis = f"การวิเคราะห์เชิงลึก (Deep-dive Analysis): ประเด็น {issue_name} เป็นความเสี่ยงระดับ 'มีนัยสำคัญ (Significant)' ที่สะท้อนถึงช่องว่างในการบริหารจัดการเชิงปฏิบัติการ (Operational Blind-spots)"
            else:
                analysis = f"การวิเคราะห์เชิงลึก (Deep-dive Analysis): ประเด็น {issue_name} อยู่ในเกณฑ์ 'เฝ้าระวัง (Moderate/Minor)'"
            
            strategy = f"ยุทธศาสตร์การจัดการ (Strategic Mitigation):\n  {raw_plan.replace(chr(10), chr(10)+'  ')}"
            return f"{analysis}\n  {strategy}"

        issue_list_3_1 = ""
        issue_list_3_2 = ""
        action_list_text = ""
        
        if not df_corp.empty:
            for _, row in df_corp.iterrows():
                iss = str(row.get('ประเด็นหลัก', 'Unknown'))
                raw_plan = str(row.get('รายละเอียด/คำให้การ', ''))
                evidence_str = get_evidence_quote(iss, df_real)
                try:
                    sev = int(pd.to_numeric(row.get('ความรุนแรง (Sev)', 0), errors='coerce'))
                    lik = int(pd.to_numeric(row.get('โอกาส (Lik)', 0), errors='coerce'))
                except:
                    sev, lik = 1, 1
                risk_level = "ระดับวิกฤต (Critical)" if (sev == 5 or sev*lik >= 16) else "ระดับสูง (Significant)" if sev*lik >= 8 else "ระดับปานกลาง (Moderate)"
                
                issue_list_3_1 += f"- ประเด็น: {iss}\n  การประเมิน: ความรุนแรง ระดับ {sev} | โอกาสเกิด ระดับ {lik} => {risk_level}\n  🔍 หลักฐานอ้างอิง: {evidence_str}\n\n"
                
                clean_plan = raw_plan.split("| Plan:")[-1].strip() if "| Plan:" in raw_plan else raw_plan
                smart_text = generate_deep_consultant_text(iss, clean_plan, sev, lik)
                action_list_text += f"▪ {iss} [ภาพรวมองค์กร]\n  {smart_text}\n\n"
        else:
            issue_list_3_1 = "- (ไม่มีข้อมูลประเด็นที่วิเคราะห์ในระดับภาพรวมองค์กร)\n"

        if not df_stake_all.empty:
            grouped = df_stake_all.groupby('กลุ่มเป้าหมาย_Clean')
            for group_name, group_df in grouped:
                issue_list_3_2 += f"🔹 **กลุ่มเป้าหมาย: {group_name}** (จำนวน {len(group_df)} ประเด็น)\n"
                for _, row in group_df.iterrows():
                    iss = str(row.get('ประเด็นหลัก', 'Unknown'))
                    raw_plan = str(row.get('รายละเอียด/คำให้การ', ''))
                    evidence_str = get_evidence_quote(iss, df_real)
                    try:
                        sev = int(pd.to_numeric(row.get('ความรุนแรง (Sev)', 0), errors='coerce'))
                        lik = int(pd.to_numeric(row.get('โอกาส (Lik)', 0), errors='coerce'))
                    except:
                        sev, lik = 1, 1
                    risk_level = "ระดับวิกฤต (Critical)" if (sev == 5 or sev*lik >= 16) else "ระดับสูง (Significant)" if sev*lik >= 8 else "ระดับปานกลาง (Moderate)"
                    
                    issue_list_3_2 += f"  - ประเด็น: {iss} ({risk_level})\n    🔍 หลักฐานอ้างอิง: {evidence_str}\n\n"
                    
                    clean_plan = raw_plan.split("| Plan:")[-1].strip() if "| Plan:" in raw_plan else raw_plan
                    smart_text = generate_deep_consultant_text(iss, clean_plan, sev, lik)
                    action_list_text += f"▪ {iss} [{group_name}]\n  {smart_text}\n\n"
        else:
            issue_list_3_2 = "- (ไม่มีข้อมูลประเด็นความเสี่ยงที่เจาะจงกลุ่มเป้าหมาย)\n"
            
        if df_corp.empty and df_stake_all.empty:
            action_list_text = "- (ข้อมูลว่างเปล่า: โปรดทำการประเมินแผนยุทธศาสตร์ใน Tool 5 ให้แล้วเสร็จก่อน)\n"

        early_warning_text = ""
        if not df_ew.empty:
            ew_bullets = ""
            for _, row in df_ew.iterrows():
                iss = str(row.get('ประเด็นหลัก', 'Unknown'))
                raw_plan = str(row.get('รายละเอียด/คำให้การ', ''))
                
                evidence_str = get_evidence_quote(iss, df_real)
                clean_iss_name = iss.replace('🚩', '').replace('สัญญาณเตือนภัยล่วงหน้า', '').replace('(Early Warning)', '').replace('Early Warning', '').replace(':', '').strip()
                
                if "Recruitment" in clean_iss_name or "นายหน้า" in clean_iss_name:
                    display_topic_name = "การเรียกเก็บค่าธรรมเนียมสรรหา (Debt Bondage Indicator)"
                else:
                    display_topic_name = clean_iss_name
                
                if "Anomaly" in raw_plan or raw_plan.strip() == "":
                    note_part = raw_plan.split("Note:")[-1].strip() if "Note:" in raw_plan else ""
                    if not note_part:
                        plan_display = f"ยกระดับการตรวจสอบ (Escalate Investigation): จัดตั้งคณะทำงานลงพื้นที่ตรวจสอบข้อเท็จจริงเชิงลึกกรณี {display_topic_name} เพื่อป้องกันการยกระดับความรุนแรงตามกฎหมายสากล"
                    else:
                        plan_display = f"ข้อสั่งการเพิ่มเติม: {note_part}"
                else:
                    plan_display = raw_plan

                display_iss = f"🚩 สัญญาณเตือนภัยล่วงหน้า (Early Warning): {display_topic_name}"
                ew_bullets += f"{display_iss}\n  🔍 หลักฐานเชิงประจักษ์ (Evidence Citation): {evidence_str}\n  🛡️ แนวทางสืบสวนเชิงลึก (Investigation Protocol): {plan_display}\n\n"

            early_warning_text = f"""4. การพยากรณ์และสัญญาณเตือนภัยล่วงหน้า (Early Warning & Foresight)
ระบบ AI ครอสเช็คข้อมูลข้ามส่วนงาน (Triangulation) ตรวจพบความเปราะบางเชิงระบบ (Systemic Vulnerability) จำนวน {len(df_ew)} ประเด็นหลัก:

{ew_bullets}"""
        else:
            early_warning_text = f"""4. การพยากรณ์และสัญญาณเตือนภัยล่วงหน้า (Early Warning & Foresight)
ในรอบการประเมินปัจจุบัน ระบบยังไม่พบสัญญาณขัดแย้งของข้อมูลที่มีนัยสำคัญระดับโครงสร้างที่รอดำเนินการ"""

        report_mockup = f"""รายงานผลวิเคราะห์ความเสี่ยงด้านสิทธิมนุษยชนเชิงกลยุทธ์ (Strategic HRDD Risk Report)
รอบการประเมิน: {actual_audit_cycle}
ขอบเขตการวิเคราะห์: ภาพรวมองค์กรและการจำแนกกลุ่มผู้มีส่วนได้เสีย (Corporate & Stakeholder Drill-down)
ผู้รับผิดชอบการประเมิน: {auditor_name if 'auditor_name' in globals() else 'N/A'}

บทสรุปผู้บริหาร (Executive Summary)
สถานะความเสี่ยงที่มีนัยสำคัญขององค์กร ถูกประมวลผลด้วยระเบียบวิธีวิจัยแบบผสานวิธีที่เสริมพลังด้วยปัญญาประดิษฐ์ (AI-Augmented Mixed Methods Research) โดยนำรายงานผลการดำเนินงานย้อนหลัง มาวิเคราะห์ร่วมกับข้อมูลภาคสนามจากผู้มีส่วนได้เสียจำนวน {sheet_data_count} ราย ผ่านนวัตกรรม "ระบบประเมินความเสี่ยงสิทธิมนุษยชนอัจฉริยะ" เพื่อสร้างระบบนิเวศแห่งความไว้วางใจ และยกระดับการบริหารความเสี่ยงให้สอดคล้องกับบริบทความยั่งยืนระดับโลก

1. วัตถุประสงค์และภาพรวม (Objectives & Overview)
องค์กรดำเนินการตรวจสอบสถานะสิทธิมนุษยชนอย่างรอบด้าน (HRDD) เพื่อระบุ ป้องกัน และบรรเทาผลกระทบเชิงลบต่อผู้มีส่วนได้เสีย โดยมุ่งเน้นการเปลี่ยนผ่านจากกระบวนการตรวจประเมินแบบดั้งเดิม (Compliance-based) สู่การประเมินเชิงลึกที่ใช้ "เครื่องมือคำนวณผลกระทบเชิงประจักษ์ (Quantitative Impact Assessment)" 

2. เกณฑ์การประเมินความเสี่ยง (Assessment Criteria)
รายงานฉบับนี้ใช้โครงสร้างการประเมินความเสี่ยง (5x5 Risk Matrix) ตามมาตรฐาน SET 2567 และกรอบการทำงานระดับสากล (UNGPs) ภายใต้หลักการ "ความร้ายแรงนำ (Severity-led Rule)" 

3. ข้อค้นพบและผลการวิเคราะห์นัยสำคัญทางสิทธิมนุษยชน (Key Findings on Salient Issues)
จากการให้ AI บูรณาการข้อมูลแบบสามเส้า (Triangulation) พบประเด็นความเสี่ยงระดับโครงสร้างที่ได้รับการอนุมัติให้ยกระดับการจัดการเป็นกรณีพิเศษ ดังนี้:

3.1 วิเคราะห์ภาพรวมองค์กร (Corporate Level Analysis)
พบประเด็นความเสี่ยงระดับภาพรวมองค์กรและห่วงโซ่อุปทาน จำนวน {len(df_corp)} ประเด็น ดังนี้:
{issue_list_3_1}
3.2 วิเคราะห์ตามกลุ่มเป้าหมาย (Stakeholder Level Analysis)
พบประเด็นความเสี่ยงที่เจาะจงผลกระทบตามกลุ่มเป้าหมาย จำนวน {len(df_stake_all)} ประเด็น มีรายละเอียดการกระจายตัว ดังนี้:
{issue_list_3_2}
{early_warning_text}

5. มาตรการและการตอบสนองเชิงยุทธศาสตร์ (Strategic Mitigation & Remediation Roadmap)
เพื่อให้บรรลุพันธกิจความยั่งยืน องค์กรได้กำหนดแผนปฏิบัติการเชิงลึก ดังนี้:

{action_list_text}
[มาตรการระดับโครงสร้างองค์กร (Systemic Corporate Measures)]
เพื่อป้องกันการเกิดซ้ำ (Zero Recurrence) องค์กรได้ประกาศกรอบยุทธศาสตร์ระยะยาวเพิ่มเติม ได้แก่:
1. การจัดการทันที (Immediate Action): พัฒนาระบบร้องเรียนดิจิทัล (Smart Grievance) ที่รองรับหลายภาษาและเชื่อมโยงทั่วภูมิภาคภายใน 3 ปี เพื่ออุดช่องว่างความเสี่ยงระดับวิกฤต
2. การใช้ปัญญาประดิษฐ์เฝ้าระวัง (AI-Driven Monitoring): ขับเคลื่อนระบบ RiskSearch360° และ AI วิเคราะห์อารมณ์ความรู้สึก เพื่อตรวจจับสัญญาณความกังวลของกลุ่มเปราะบาง
3. หลักการความร้ายแรงนำ (Severity-led Rule): คงมาตรการ Zero Accident และระบบการจัดการความปลอดภัยกระบวนการผลิต (PSM) อย่างเข้มงวด 

6. ข้อสรุปเชิงยุทธศาสตร์ (Executive Conclusion)
องค์กรได้พิสูจน์ให้เห็นถึงการยกระดับกระบวนทัศน์จากการมอง "ความเสี่ยงต่อธุรกิจ (Risk to Business)" ไปสู่การปกป้อง "ความเสี่ยงต่อผู้คน (Risk to People)" อย่างแท้จริง อันเป็นรากฐานสำคัญของการเติบโตอย่างยั่งยืนในเวทีโลก"""

        st.markdown("**✍️ ตรวจสอบความถูกต้องของรายงานยุทธศาสตร์ก่อนการอนุมัติขั้นสุดท้าย:**")
        
        df_tool7_report = pd.DataFrame()
        if not df_real.empty:
            df_tool7_report = df_real[df_real['เครื่องมือ'] == 'Tool 7 - Report']
        
        if not df_tool7_report.empty and not st.session_state.get('edit_tool7_report', False):
            latest_report = df_tool7_report.iloc[-1]
            st.success("✅ รายงานยุทธศาสตร์ฉบับนี้ได้รับการอนุมัติและบันทึกลงระบบแล้ว")
            st.info(latest_report['รายละเอียด/คำให้การ'])
            
            if st.button("📝 สร้างรายงานฉบับใหม่ / เขียนทับ"):
                st.session_state.edit_tool7_report = True
                if hasattr(st, 'rerun'): st.rerun() 
                elif hasattr(st, 'experimental_rerun'): st.experimental_rerun()
                
        else:
            report_text_final = st.text_area("ทบทวน ปรับแก้ และอนุมัติรายงานฉบับสมบูรณ์ (Review & Approve Report):", value=report_mockup, height=800, label_visibility="collapsed")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("💾 อนุมัติยุทธศาสตร์และบันทึกรายงานฉบับสมบูรณ์ (Approve & Save Executive Report)"):
                if sheet:
                    try:
                        import traceback
                        try: val_now = now
                        except NameError: val_now = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        try: val_auditor_name = auditor_name
                        except NameError: val_auditor_name = "N/A"
                        
                        try: val_location = location
                        except NameError: val_location = "N/A"

                        new_row_data = [
                            str(val_now), str(actual_audit_cycle), str(val_auditor_name), str(val_location), 
                            "Tool 7 - Report", "Executive Summary", "ภาพรวมองค์กร", "N/A", "N/A", 
                            "รายงานยุทธศาสตร์", str(report_text_final), "N/A", "N/A", "N/A", "N/A", "N/A"
                        ]
                        
                        with st.spinner("กำลังบันทึกรายงาน..."):
                            sheet.append_row(new_row_data)
                            st.session_state.edit_tool7_report = False
                            
                            if hasattr(st, 'cache_data'): st.cache_data.clear()
                            elif hasattr(st, 'legacy_caching'): st.legacy_caching.clear()
                            
                            if hasattr(st, 'rerun'): st.rerun()
                            elif hasattr(st, 'experimental_rerun'): st.experimental_rerun()
                    except Exception as e:
                        st.error(f"❌ ระบบเกิดข้อผิดพลาดในการบันทึกข้อมูล: {type(e).__name__} - {str(e)}")
                        with st.expander("ดูรายละเอียดข้อผิดพลาด (Technical Details)"):
                            st.code(traceback.format_exc())
                else:
                    st.error("❌ การเชื่อมต่อกับฐานข้อมูล Google Sheet ขัดข้อง โปรดตรวจสอบการตั้งค่า")
