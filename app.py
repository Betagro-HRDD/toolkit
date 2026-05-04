import streamlit as st
import pandas as pd
from google.oauth2 import service_account
import gspread
from datetime import datetime, timedelta
import altair as alt

# ==========================================
# --- 1. SETTING UP THE PAGE ---
# ==========================================
st.set_page_config(page_title="Betagro Smart HRDD Simulation", page_icon="🟢", layout="wide")

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
    "Tool 5: ประเมินความเสี่ยง (AI-Augmented Triangulation & Sentiment Analysis)",
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

# ----------------- TOOL 5 (AI-AUGMENTED TRIANGULATION ENGINE) -----------------
elif choice == "Tool 5 (Matrix)":
    st.markdown("<div class='standalone-form'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#005B31; margin-top:0;'>Tool 5: ประเมินความเสี่ยง (AI-Augmented Triangulation & Sentiment Analysis)</h3>", unsafe_allow_html=True)
    
    # --- ส่วนการกรองข้อมูล (Filter Section) ---
    st.markdown("<div class='filter-box'><h5 style='color:#D97706; margin-top:0;'><i class='fa-solid fa-filter'></i> กำหนดหน่วยการวิเคราะห์ (Unit of Analysis)</h5></div>", unsafe_allow_html=True)
    
    filter_mode = st.radio("ระดับการวิเคราะห์:", ["ระดับองค์กรภาพรวม (Corporate Level / ทุกกลุ่ม)", "ระดับเจาะจงกลุ่มเป้าหมาย (Stakeholder Group Level)"], horizontal=True)
    custom_filter_text = ""
    if filter_mode == "ระดับเจาะจงกลุ่มเป้าหมาย (Stakeholder Group Level)":
        custom_filter_text = st.selectbox("เลือกกลุ่มเป้าหมาย:", ["ผู้บริหาร", "พนักงานไทย", "แรงงานข้ามชาติ", "คู่ค้า (Suppliers)", "ชุมชน", "ลูกค้า"])

    # --- การดึงข้อมูลจากฐานข้อมูลจริง (Data Preparation) ---
    raw_data_only_df = pd.DataFrame()
    if not df_real.empty:
        # กรองเฉพาะ Tool 1-4 เพื่อมาวิเคราะห์ใน Tool 5
        raw_data_only_df = df_real[df_real['เครื่องมือ'].isin(['Tool 1', 'Tool 2', 'Tool 3', 'Tool 4'])]
        if custom_filter_text:
            raw_data_only_df = raw_data_only_df[raw_data_only_df['กลุ่มเป้าหมาย'].str.contains(custom_filter_text, na=False)]
    
    data_count = len(raw_data_only_df)
    
    # --- ปุ่มกระตุ้นการวิเคราะห์ (Trigger) ---
    # ใช้ Session State เพื่อล็อกหน้าจอให้คงอยู่หลังจากกดปุ่ม
    if st.button(f"✨ สกัดประเด็นความเสี่ยงจากฐานข้อมูล ({data_count} รายการ)"):
        st.session_state.tool5_scanned = True

    # --- ส่วนการแสดงผลผลลัพธ์ (Result Section) ---
    if st.session_state.get("tool5_scanned", False):
        # ดึงประเด็นหลักที่พบจริงใน Sheet
        real_issues = []
        if not raw_data_only_df.empty and 'ประเด็นหลัก' in raw_data_only_df.columns:
            real_issues = [i for i in raw_data_only_df['ประเด็นหลัก'].unique().tolist() if str(i).strip() not in ["", "nan"]]
        
        if not real_issues:
            st.warning("⚠️ ไม่พบประเด็นความเสี่ยงในฐานข้อมูลสำหรับกลุ่มที่เลือก")
        else:
            st.markdown("<h5 style='color: #005B31; margin-top: 20px;'><i class='fa-solid fa-wand-magic-sparkles'></i> 1. เลือกประเด็นที่ AI ตรวจพบเพื่อประเมินความเสี่ยง</h5>", unsafe_allow_html=True)
            
            # Dropdown สำหรับเลือกประเด็น
            selected_issue = st.selectbox("รายการความเสี่ยงที่พบ (Process Issue):", ["-- โปรดเลือกประเด็น --"] + real_issues)

            if selected_issue != "-- โปรดเลือกประเด็น --":
                # --- AI Triangulation Logic ---
                subset = raw_data_only_df[raw_data_only_df['ประเด็นหลัก'] == selected_issue]
                
                # แยกข้อมูลแบบสามเส้า (Triangulation)
                policy_side = subset[subset['กลุ่มเป้าหมาย'].str.contains("ผู้บริหาร|คู่ค้า", na=False)]
                worker_side = subset[~subset['กลุ่มเป้าหมาย'].str.contains("ผู้บริหาร|คู่ค้า", na=False)]
                
                # แสดงผลการฟันธงของ AI
                if not policy_side.empty and not worker_side.empty:
                    st.error("⚠️ **AI ฟันธง: พบ Implementation Gap (ข้อมูลขัดแย้งกัน)**\n\nฝ่ายบริหารระบุว่ามีนโยบาย แต่ภาคสนามพบการปฏิบัติที่ขัดแย้ง ระบบยกระดับความรุนแรงเป็น 'วิกฤต'")
                    ai_sev = 5
                elif policy_side.empty and not worker_side.empty:
                    st.warning("⚠️ **AI ฟันธง: Operational Risk**\n\nตรวจพบปัญหาจากหน้างานโดยไม่มีนโยบายรองรับชัดเจน")
                    ai_sev = 3
                else:
                    st.success("✅ **AI ฟันธง: Managed Risk**\n\nประเด็นนี้อยู่ภายใต้การบริหารจัดการตามนโยบาย")
                    ai_sev = 1

                # --- 3. Risk Matrix (Severity-led Rule) ---
                st.markdown("<hr>", unsafe_allow_html=True)
                st.subheader("2. ประเมินความรุนแรง (Risk Matrix)")
                
                col1, col2, col3 = st.columns(3)
                with col1: s_scale = st.slider("Scale (ความหนักหน่วง)", 1, 5, ai_sev)
                with col2: s_scope = st.slider("Scope (ขอบเขต)", 1, 5, ai_sev)
                with col3: s_remedy = st.slider("Remediability (การเยียวยา)", 1, 5, ai_sev)
                
                # กฎ "ความร้ายแรงนำ" (Severity-led): ใช้ค่าที่สูงที่สุด
                severity_final = max(s_scale, s_scope, s_remedy)
                likelihood = st.slider("Likelihood (โอกาสเกิด)", 1, 5, 3)
                risk_score = severity_final * likelihood
                
                # แสดงสถานะความเสี่ยง (Salient Risk Check)
                if risk_score >= 15 or severity_final == 5:
                    st.error(f"🚨 **SALIENT RISK (ระดับวิกฤต): คะแนน {risk_score}**")
                    risk_level = "Critical"
                elif risk_score >= 8:
                    st.warning(f"⚠️ **SIGNIFICANT RISK (ระดับสูง): คะแนน {risk_score}**")
                    risk_level = "Significant"
                else:
                    st.success(f"✅ **MODERATE RISK: คะแนน {risk_score}**")
                    risk_level = "Moderate"

                # --- 4. Mitigation Plan ---
                st.markdown("<hr>", unsafe_allow_html=True)
                st.subheader("3. แผนบริหารจัดการ (Mitigation Plan)")
                
                final_evidence = st.text_area("หลักฐานเชิงประจักษ์ (Evidence):", value=f"วิเคราะห์ข้อมูลจากกลุ่ม {custom_filter_text if custom_filter_text else 'ทั้งหมด'} จำนวน {len(subset)} รายการ")
                final_plan = st.text_area("แผนการจัดการ (Action Plan):", placeholder="ระบุแผนการป้องกันและการเยียวยา...")

                if st.button("💾 อนุมัติและบันทึกประเด็นยุทธศาสตร์"):
                    if sheet:
                        try:
                            # บันทึกข้อมูลลง Google Sheet ตามโครงสร้างเดิม
                            detail_full = f"Evidence: {final_evidence} | Plan: {final_plan}"
                            new_row = [
                                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                audit_cycle, 
                                auditor_name, 
                                "N/A", 
                                "Tool 5", 
                                "Issue-Based", 
                                custom_filter_text if custom_filter_text else "ภาพรวม", 
                                "N/A", "N/A", 
                                selected_issue, 
                                detail_full, 
                                severity_final, 
                                likelihood, 
                                risk_score, 
                                risk_level
                            ]
                            sheet.append_row(new_row)
                            st.balloons()
                            st.success(f"บันทึกประเด็น '{selected_issue}' เรียบร้อยแล้ว")
                        except Exception as e:
                            st.error(f"เกิดข้อผิดพลาดในการบันทึก: {e}")

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
                    decision_text = "Approved" if "ยืนยัน" in t6_decision else "Rejected"
                    detail = f"Anomaly: Recruitment Fee | Decision: {decision_text} | Note: {t6_note}"
                    sheet.append_row([now, audit_cycle, auditor_name, "N/A", "Tool 6", "Issue-Based", "ภาพรวมระดับองค์กร", "N/A", "N/A", "Early Warning (Recruitment Fee)", detail, "", "", "", ""])
                    st.session_state.early_warning_approved = True if "ยืนยัน" in t6_decision else False
                    st.session_state.early_warning_note = t6_note
                    st.success("✅ บันทึกมติสำเร็จ (หมายเหตุ: หากกด 'ปฏิเสธ' สัญญาณเตือนนี้จะถูกลบออกจากรายงาน Executive Report ใน Tool 7 อัตโนมัติ)")
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
                detail = f"Anomaly: {m_topic} | Decision: Approved (Manual) | Note: {m_note}"
                sheet.append_row([now, audit_cycle, auditor_name, "N/A", "Tool 6", "Issue-Based", "ภาพรวมระดับองค์กร", "N/A", "N/A", f"Early Warning ({m_topic})", detail, "", "", "", ""])
                st.session_state.early_warning_approved = True
                st.session_state.early_warning_note = m_note
                st.success("✅ บันทึกประเด็นเตือนภัยล่วงหน้าเข้าสู่ระบบ และส่งต่อไปยังรายงาน Tool 7 เรียบร้อยแล้ว")
            
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- TOOL 7 (Executive Dashboard & STRATEGIC AI Report) -----------------
elif choice.startswith("Tool 7"):
    st.markdown("<div class='standalone-form'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#005B31; margin-top:0;'>Tool 7: แดชบอร์ดและรายงาน (Real-time Data Analytics)</h3><p style='color:#666;'>สรุปผลประเมินนัยสำคัญของความเสี่ยง (Salient Risk) ระดับองค์กร</p><hr>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    
    sheet_data_count = 0
    if not df_real.empty:
        raw_df = df_real[df_real['เครื่องมือ'].isin(['Tool 1', 'Tool 2', 'Tool 3', 'Tool 4'])]
        sheet_data_count = len(raw_df)
            
    if sheet_data_count == 0: sheet_data_count = 135
    
    with c1: st.markdown(f"<div class='dash-card'><div class='dash-label'>ข้อมูลที่สืบค้นจากระบบ</div><div class='dash-number'>{sheet_data_count}</div><div style='color: #005B31; font-size:12px;'>ผู้มีส่วนได้เสีย (Stakeholders)</div></div>", unsafe_allow_html=True)
    
    approved_count = len(st.session_state.get("approved_issues", []))
    with c2: st.markdown(f"<div class='dash-card'><div class='dash-label'>Salient Issues</div><div class='dash-number' style='color:#DC2626;'>{approved_count}</div><div style='color: #666; font-size:12px;'>ประเด็นที่ได้รับการอนุมัติแผนจัดการ</div></div>", unsafe_allow_html=True)
    
    ew_count = 1 if st.session_state.get("early_warning_approved", False) else 0
    with c3: st.markdown(f"<div class='dash-card'><div class='dash-label'>Early Warnings</div><div class='dash-number' style='color:#D97706;'>{ew_count}</div><div style='color: #666; font-size:12px;'>สัญญาณเตือนภัยที่รอการสอบสวน</div></div>", unsafe_allow_html=True)
    
    st.markdown("<br><h5 style='color: #005B31; text-align:center;'>📊 แผนผังการกระจายตัวความเสี่ยง (Human Rights Risk Heat Map)</h5>", unsafe_allow_html=True)
    
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
    
    if st.button("✨ ให้ Gemini AI สังเคราะห์รายงานเชิงยุทธศาสตร์ (Generate Strategic Report)"):
        st.session_state.ai_report_drafted = True

    if st.session_state.get("ai_report_drafted", False):
        st.markdown("""
        <div class="gemini-draft-box">
            <h4 class="gemini-title"><span class="gemini-icon">✨</span> Gemini AI: Strategic Insight & Executive Summary</h4>
            <p style="font-size: 14px; color: #666; margin-bottom: 15px;">ระบบได้ประมวลผลและสร้างรายงานภาษาที่ปรึกษา (Consulting Language) เพื่อนำเสนอระดับผู้บริหารระดับสูง</p>
        </div>
        """, unsafe_allow_html=True)

        def generate_deep_consultant_text(issue_name, raw_plan, severity, likelihood):
            score = severity * likelihood
            if severity == 5 or score >= 16:
                analysis = f"การวิเคราะห์เชิงลึก (Deep-dive Analysis): ประเด็น {issue_name} จัดอยู่ในระดับ 'วิกฤต (Critical)' ซึ่งมีนัยยะสำคัญต่อความเสี่ยงด้านการปฏิบัติตามกฎหมายสากล (Regulatory Non-compliance) และอาจส่งผลกระทบโดยตรงต่อเสถียรภาพของห่วงโซ่อุปทาน (Supply Chain Disruption) องค์กรจำเป็นต้องใช้มาตรการแทรกแซงขั้นสูงสุด (Executive Intervention)"
            elif score >= 8:
                analysis = f"การวิเคราะห์เชิงลึก (Deep-dive Analysis): ประเด็น {issue_name} เป็นความเสี่ยงระดับ 'มีนัยสำคัญ (Significant)' ที่สะท้อนถึงช่องว่างในการบริหารจัดการเชิงปฏิบัติการ (Operational Blind-spots) หากละเลยอาจลุกลามเป็นความท้าทายระดับโครงสร้าง"
            else:
                analysis = f"การวิเคราะห์เชิงลึก (Deep-dive Analysis): ประเด็น {issue_name} อยู่ในเกณฑ์ 'เฝ้าระวัง (Moderate/Minor)' ซึ่งระบบยังคงสามารถควบคุมสถานการณ์ได้ตามมาตรฐาน (Under Control) แต่ต้องอาศัยการประเมินซ้ำตามวงรอบ"
            
            strategy = f"ยุทธศาสตร์การจัดการ (Strategic Mitigation):\n  {raw_plan.replace(chr(10), chr(10)+'  ')}"
            return f"{analysis}\n  {strategy}"

        issue_list_text = ""
        action_list_text = ""
        saved_dict = st.session_state.get("saved_plans_dict", {})
        
        has_data = False
        for iss, data in saved_dict.items():
            has_data = True
            risk_level = "ระดับวิกฤต (Critical)" if (data['sev'] == 5 or data['sev']*data['lik'] >= 16) else "ระดับสูง (Significant)" if data['sev']*data['lik'] >= 8 else "ระดับปานกลาง (Moderate)"
            
            filter_context = data.get('filter_context', '')
            scope_label = f"ผู้ได้รับผลกระทบหลัก: {filter_context}" if filter_context else "ผลกระทบระดับองค์กรภาพรวม"
            
            issue_list_text += f"- ประเด็น: {iss}\n  ({scope_label})\n  การประเมิน: ความรุนแรง (Severity) ระดับ {data['sev']} | โอกาสเกิด (Likelihood) ระดับ {data['lik']}\n  การจัดระดับความเสี่ยง: {risk_level}\n\n"
            
            smart_text = generate_deep_consultant_text(iss, data['plan'], data['sev'], data['lik'])
            action_list_text += f"▪ {iss}\n  {smart_text}\n\n"
            
        if not has_data:
            issue_list_text = "- (ข้อมูลว่างเปล่า: ยังไม่มีประเด็นที่ได้รับการอนุมัติเชิงยุทธศาสตร์จาก Tool 5)\n"
            action_list_text = "- (ข้อมูลว่างเปล่า: โปรดทำการประเมินแผนยุทธศาสตร์ใน Tool 5 ให้แล้วเสร็จก่อน)\n"

        early_warning_text = ""
        if st.session_state.get("early_warning_approved", False):
            ew_note = st.session_state.get("early_warning_note", "ให้ทีมตรวจสอบภายใน (Internal Audit) ลงพื้นที่ตรวจสอบคู่ค้าและเอเจนซี่ทั้งหมดทันที")
            early_warning_text = f"""4. การพยากรณ์และสัญญาณเตือนภัยล่วงหน้า (Early Warning & Foresight)
ระบบ AI ครอสเช็คข้อมูลข้ามส่วนงาน (Triangulation) ตรวจพบความเปราะบางเชิงระบบ (Systemic Vulnerability) 1 ประเด็นหลัก:
- สัญญาณเตือนภัย: พบช่องว่างการนำนโยบายไปปฏิบัติจริง (Policy Implementation Gap) 
- แนวทางสืบสวนเชิงลึก (Investigation Resolution): อนุมัติดำเนินการตรวจสอบข้อเท็จจริง โดยมีมติสั่งการเชิงยุทธศาสตร์ว่า "{ew_note}" เพื่อป้องกันการยกระดับความรุนแรงตามกฎหมายสากล"""
        else:
            early_warning_text = """4. การพยากรณ์และสัญญาณเตือนภัยล่วงหน้า (Early Warning & Foresight)
ในรอบการประเมินปัจจุบัน ระบบยังไม่พบสัญญาณขัดแย้งของข้อมูลที่มีนัยสำคัญระดับโครงสร้างที่ต้องจัดตั้งคณะกรรมการสืบสวนฉุกเฉิน"""

        report_mockup = f"""รายงานผลวิเคราะห์ความเสี่ยงด้านสิทธิมนุษยชนเชิงกลยุทธ์ (Strategic HRDD Risk Report)
รอบการประเมิน: {audit_cycle}
ขอบเขตพื้นที่: ภาพรวมระดับองค์กรและห่วงโซ่คุณค่า (Corporate & Value Chain Overview)
ผู้รับผิดชอบการประเมิน: {auditor_name}

บทสรุปผู้บริหาร (Executive Summary)
สถานะความเสี่ยงที่มีนัยสำคัญขององค์กร ถูกประมวลผลด้วยระเบียบวิธีวิจัยแบบผสานวิธีที่เสริมพลังด้วยปัญญาประดิษฐ์ (AI-Augmented Mixed Methods Research) โดยนำรายงานผลการดำเนินงานย้อนหลัง มาวิเคราะห์ร่วมกับข้อมูลภาคสนามจากผู้มีส่วนได้เสียจำนวน {sheet_data_count} ราย ผ่านนวัตกรรม "ระบบประเมินความเสี่ยงสิทธิมนุษยชนอัจฉริยะ" เพื่อสร้างระบบนิเวศแห่งความไว้วางใจ และยกระดับการบริหารความเสี่ยงตลอดห่วงโซ่คุณค่าให้สอดคล้องกับบริบทความยั่งยืนระดับโลก

1. วัตถุประสงค์และภาพรวม (Objectives & Overview)
องค์กรดำเนินการตรวจสอบสถานะสิทธิมนุษยชนอย่างรอบด้าน (HRDD) เพื่อระบุ ป้องกัน และบรรเทาผลกระทบเชิงลบต่อผู้มีส่วนได้เสียตลอดห่วงโซ่คุณค่า โดยมุ่งเน้นการเปลี่ยนผ่านจากกระบวนการตรวจประเมินแบบดั้งเดิม (Compliance-based) สู่การประเมินเชิงลึกที่ใช้ "เครื่องมือคำนวณผลกระทบเชิงประจักษ์ (Quantitative Impact Assessment)" เพื่อตอบสนองต่อกฎระเบียบการค้าระดับโลก อาทิ EU CSDDD, มาตรฐาน OECD (2023) และรักษาความเป็นผู้นำด้านความยั่งยืนระดับ AAA

2. เกณฑ์การประเมินความเสี่ยง (Assessment Criteria)
รายงานฉบับนี้ใช้โครงสร้างการประเมินความเสี่ยง (5x5 Risk Matrix) ตามมาตรฐาน SET 2567 และกรอบการทำงานระดับสากล (UNGPs) ภายใต้หลักการ "ความร้ายแรงนำ (Severity-led Rule)" ซึ่งให้น้ำหนักสูงสุดกับประเด็นที่กระทบต่อศักดิ์ศรีความเป็นมนุษย์เหนือความเสี่ยงทางธุรกิจ

3. ข้อค้นพบและผลการวิเคราะห์นัยสำคัญทางสิทธิมนุษยชน (Key Findings on Salient Issues)
จากการให้ AI บูรณาการข้อมูลแบบสามเส้า (Triangulation) ระหว่างนโยบาย, แบบสอบถาม และคำให้การเชิงลึก พบประเด็นความเสี่ยงระดับโครงสร้างที่ได้รับการอนุมัติให้ยกระดับการจัดการเป็นกรณีพิเศษ ดังนี้:

{issue_list_text}
{early_warning_text}

5. มาตรการและการตอบสนองเชิงยุทธศาสตร์ (Strategic Mitigation & Remediation Roadmap)
เพื่อให้บรรลุพันธกิจความยั่งยืน (Sustainable Life) องค์กรได้กำหนดแผนปฏิบัติการเชิงลึกสำหรับประเด็นความเสี่ยงข้างต้น ดังนี้:

{action_list_text}
[มาตรการระดับโครงสร้างองค์กร (Systemic Corporate Measures)]
เพื่อป้องกันการเกิดซ้ำ (Zero Recurrence) องค์กรได้ประกาศกรอบยุทธศาสตร์ระยะยาวเพิ่มเติม ได้แก่:
1. การจัดการทันที (Immediate Action): พัฒนาระบบร้องเรียนดิจิทัล (Smart Grievance) ที่รองรับหลายภาษาและเชื่อมโยงทั่วภูมิภาคภายใน 3 ปี เพื่ออุดช่องว่างความเสี่ยงระดับวิกฤต
2. การใช้ปัญญาประดิษฐ์เฝ้าระวัง (AI-Driven Monitoring): ขับเคลื่อนระบบ RiskSearch360° และ AI วิเคราะห์อารมณ์ความรู้สึก (Sentiment Analysis) เพื่อตรวจจับสัญญาณความกังวลของกลุ่มเปราะบางที่ไม่ปรากฏในเอกสารตรวจสอบทั่วไป
3. การยกระดับคู่ค้า (Supplier Engagement): ขยายผลการทำ HRDD แบบ 100% ครอบคลุมธุรกิจที่มีความเสี่ยงสูงตลอดห่วงโซ่คุณค่า ภายในปี 2571
4. หลักการความร้ายแรงนำ (Severity-led Rule): คงมาตรการ Zero Accident และระบบการจัดการความปลอดภัยกระบวนการผลิต (PSM) อย่างเข้มงวด แม้ในประเด็นที่สถิติการเกิดต่ำ เพื่อป้องกันความเสียหายระดับที่ไม่อาจเยียวยาได้

6. ข้อสรุปเชิงยุทธศาสตร์ (Executive Conclusion)
องค์กรได้พิสูจน์ให้เห็นถึงการยกระดับกระบวนทัศน์จากการมอง "ความเสี่ยงต่อธุรกิจ (Risk to Business)" ไปสู่การปกป้อง "ความเสี่ยงต่อผู้คน (Risk to People)" อย่างแท้จริง การบูรณาการเทคโนโลยี AI เข้ากับกระบวนการ HRDD ทำให้องค์กรสามารถดักจับความเสี่ยงที่มองไม่เห็น (Invisible Risks) เพิ่มขีดความสามารถในการตรวจสอบย้อนกลับ (Traceability) และยกระดับคุณภาพชีวิตของผู้มีส่วนได้เสียตลอดห่วงโซ่อุปทาน อันเป็นรากฐานสำคัญของการเติบโตอย่างยั่งยืนในเวทีโลก"""

        st.markdown("**✍️ ตรวจสอบความถูกต้องของรายงานยุทธศาสตร์ก่อนการอนุมัติขั้นสุดท้าย:**")
        report_text_final = st.text_area("ทบทวน ปรับแก้ และอนุมัติรายงานฉบับสมบูรณ์ (Review & Approve Report):", value=report_mockup, height=800, label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 อนุมัติยุทธศาสตร์และบันทึกรายงานฉบับสมบูรณ์ (Approve & Save Executive Report)"):
            if sheet:
                sheet.append_row([now, audit_cycle, auditor_name, location, "Tool 7 - Report", "Executive Summary", "ภาพรวมองค์กร", "N/A", "N/A", f"Strategic HRDD Report: {audit_cycle}", report_text_final, "", "", "", "Approved"])
                st.success("✅ อนุมัติยุทธศาสตร์องค์กรและบันทึกรายงานประเมินความเสี่ยงฉบับสมบูรณ์เข้าสู่ฐานข้อมูลเรียบร้อยแล้ว!")
                
    st.markdown("</div>", unsafe_allow_html=True)
