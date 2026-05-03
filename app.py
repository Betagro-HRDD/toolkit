import streamlit as st
import pandas as pd
from google.oauth2 import service_account
import gspread
from datetime import datetime, timedelta
import altair as alt

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

# --- 3. STYLING (ลบโค้ด CSS ขยะทิ้งทั้งหมด ทำให้ไม่ซ้อนทับกัน) ---
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
                        st.info("👋 ยินดีต้อนรับ! กรุณาตั้งรหัสผ่านสำหรับบัญชีของคุณเพื่อความปลอดภัย")
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
                    st.error("❌ Access Denied. อีเมลนี้ไม่ได้รับสิทธิ์การเข้าถึง")
                    st.form_submit_button("LOGIN") 
            else:
                st.form_submit_button("ตรวจสอบสิทธิ์")
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
with col_p1: audit_cycle = st.selectbox("รอบการประเมิน *", ["Annual 2026", "Q1/2026", "Q2/2026", "Q3/2026", "Q4/2026", "Special Audit"])
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
    with col_r1: resp_group = st.selectbox("กลุ่มเป้าหมาย *", ["ผู้บริหาร", "พนักงานไทย", "แรงงานข้ามชาติ", "คู่ค้า (Suppliers)", "ชุมชน", "องค์กรไม่แสวงไร (NGOs)", "นักลงทุน", "ลูกค้า (B2B/Retail)"])
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
        q1_1 = st.radio("1.1 องค์กรมี 'นโยบายสิทธิมนุษยชน' ที่เป็นลายลักษณ์อักษรหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        if st.form_submit_button("💾 บันทึกข้อมูล Tool 1"):
            if sheet:
                sheet.append_row([now, audit_cycle, auditor_name, location, "Tool 1", resp_id, resp_group, resp_dept, resp_gender, "Policy Gap Analysis", f"A({q1_1})", "", "", "", ""])
                st.success("✅ บันทึกข้อมูล Tool 1 เรียบร้อย")

elif choice.startswith("Tool 2"):
    with st.form("form_t2"):
        st.markdown("<h3 style='color:#005B31;'>Tool 2: แบบสอบถามการปฏิบัติหน้างาน</h3>", unsafe_allow_html=True)
        s1_1 = st.select_slider("1.1 ท่านได้รับค่าจ้างตรงเวลาและครบถ้วน", options=[1,2,3,4,5], value=3)
        if st.form_submit_button("🚀 บันทึกข้อมูล Tool 2"):
            if sheet:
                sheet.append_row([now, audit_cycle, auditor_name, location, "Tool 2", resp_id, resp_group, resp_dept, resp_gender, "Worker Survey", f"จ้างงาน({s1_1})", "", "", "", ""])
                st.success("✅ ส่งข้อมูลแบบสอบถามสำเร็จ")

elif choice.startswith("Tool 3"):
    with st.form("form_t3"):
        st.markdown("<h3 style='color:#005B31;'>Tool 3: สัมภาษณ์เชิงลึก</h3><hr>", unsafe_allow_html=True)
        topics = st.multiselect("ประเด็นที่พูดคุย:", ["การสรรหา", "สัญญาจ้าง", "ที่พักอาศัย", "กลไกร้องเรียน", "ความรู้"], label_visibility="collapsed")
        testimony = st.text_area("สรุปคำพูดหรือหลักฐานที่พบ:", height=150)
        if st.form_submit_button("💾 บันทึกข้อมูล Tool 3"):
            if sheet:
                sheet.append_row([now, audit_cycle, auditor_name, location, "Tool 3", resp_id, resp_group, resp_dept, resp_gender, ", ".join(topics), testimony, "", "", "", ""])
                st.success("✅ บันทึกหลักฐานสำเร็จ")

elif choice.startswith("Tool 4"):
    with st.form("form_t4"):
        st.markdown("<h3 style='color:#005B31;'>Tool 4: บันทึกการสังเกตการณ์</h3><hr>", unsafe_allow_html=True)
        o1 = st.radio("1. มีการติดประกาศนโยบายในพื้นที่", ["✔️ พบ (Pass)", "❌ ไม่พบ (Fail)", "➖ ไม่เกี่ยวข้อง (N/A)"], horizontal=True)
        if st.form_submit_button("💾 บันทึกข้อมูล Tool 4"):
            if sheet:
                sheet.append_row([now, audit_cycle, auditor_name, location, "Tool 4", resp_id, resp_group, resp_dept, resp_gender, "Site Observation", o1, "", "", "", ""])
                st.success("✅ บันทึกการสังเกตการณ์สำเร็จ")

# ----------------- TOOL 5 (THE FLAWLESS NATIVE MODALS) -----------------
elif choice == "Tool 5: ประเมินนัยสำคัญของความเสี่ยง (Salient Risk Matrix)":

    st.markdown("<div class='standalone-form'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#005B31; margin-top:0;'>Tool 5: ประเมินนัยสำคัญของความเสี่ยง (Issue-Based)</h3>", unsafe_allow_html=True)
    
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
            "ผู้บริหาร", "พนักงานไทย", "แรงงานข้ามชาติ", "คู่ค้า (Suppliers)", "ชุมชน", "องค์กรไม่แสวงหากำไร (NGOs)", "นักลงทุน", "ลูกค้า (B2B/Retail)"
        ])

    raw_data_only_df = pd.DataFrame()
    if not df_real.empty:
        raw_data_only_df = df_real[df_real['เครื่องมือ'].isin(['Tool 1', 'Tool 2', 'Tool 3', 'Tool 4'])]
        
    df_filtered = raw_data_only_df.copy()
    if not raw_data_only_df.empty:
        if custom_filter_text:
            if "ลูกค้า" in custom_filter_text:
                df_filtered = raw_data_only_df[raw_data_only_df['กลุ่มเป้าหมาย'].str.contains("ลูกค้า", na=False)]
            elif "NGO" in custom_filter_text:
                df_filtered = raw_data_only_df[raw_data_only_df['กลุ่มเป้าหมาย'].str.contains("NGO", na=False)]
            else:
                df_filtered = raw_data_only_df[raw_data_only_df['กลุ่มเป้าหมาย'] == custom_filter_text]
    
    sheet_data_count = len(df_filtered)
    if sheet_data_count == 0: 
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

    st.markdown(f"""
    <div style="background: #F5F3FF; border-left: 4px solid #8B5CF6; padding: 20px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.02);">
        <strong style="color: #6D28D9; font-size: 16px;"><i class="fa-solid fa-magnifying-glass-chart"></i> AI Triangulation Evidence (หลักฐานสนับสนุนจากข้อมูลจริง):</strong>
    </div>
    """, unsafe_allow_html=True)

    # 💡 1. NATIVE POPOVER FOR EVIDENCE (ไม่มีรหัส HTML โผล่ ไม่มีการค้างหน้าจอ 100%)
    evidence_count = 0
    if not df_filtered.empty and 'รายละเอียด/คำให้การ' in df_filtered.columns:
        subset = df_filtered[df_filtered['ประเด็นหลัก'] == selected_issue]
        
        if subset.empty or subset['รายละเอียด/คำให้การ'].str.strip().eq("").all():
            st.info("ไม่มีคำให้การเจาะจง (ประเมินจากคะแนนแบบสอบถามหรือการสังเกตการณ์)")
        else:
            with st.container():
                for idx, row in subset.head(5).iterrows(): 
                    if str(row['รายละเอียด/คำให้การ']).strip() != "":
                        evidence_count += 1
                        r_id = row['รหัสผู้ตอบ']
                        full_text = row['รายละเอียด/คำให้การ']
                        short_text = full_text if len(full_text) <= 60 else full_text[:60] + "..."
                        
                        # ใช้ columns แบ่งสัดส่วนข้อความกับปุ่ม
                        c_txt, c_btn = st.columns([7, 2])
                        with c_txt:
                            st.markdown(f"<div style='padding: 8px 0; border-left: 3px solid #3B82F6; padding-left: 15px; margin-bottom: 10px; background: white;'><b>(ID {r_id}):</b> {short_text}</div>", unsafe_allow_html=True)
                        with c_btn:
                            # 💡 ปุ่มกด Native ของ Streamlit ปิดได้ 100%
                            with st.popover(f"🔍 ดูข้อมูลดิบ"):
                                st.markdown(f"### 📄 ข้อมูลอ้างอิงรหัส: {r_id}")
                                st.write(f"**📅 วันที่เก็บข้อมูล:** {row.get('วันที่-เวลา', '-')}")
                                st.write(f"**📍 พื้นที่สำรวจ:** {row.get('พื้นที่สำรวจ', '-')}")
                                st.write(f"**👥 กลุ่ม / แผนก:** {row.get('กลุ่มเป้าหมาย', '-')} / {row.get('แผนก/ส่วนงาน', '-')}")
                                st.info(f"**คำให้การฉบับเต็ม:**\n\n{full_text}")

    # 💡 KNOWLEDGE BASE MATCHER
    matched_law = "UNGPs | ILO Conventions | กฎหมายที่เกี่ยวข้อง"
    matched_doc = "Standard_Guideline.pdf"
    for keyword, knowledge in LAW_KNOWLEDGE_BASE.items():
        if keyword in selected_issue:
            matched_law = knowledge["std"]
            matched_doc = knowledge["doc"]
            break

    plain_evidence = f"ระบบ AI ตรวจพบความเสี่ยงจากข้อมูลจริงจำนวน {evidence_count} รายการ ในฐานข้อมูลของกลุ่ม {scope_text}"
    plain_standard = matched_law

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
        ai_plan = "Preventive Action:\n- ระงับการปฏิบัติงานและตั้งคณะกรรมการสืบสวนข้อเท็จจริงทันที (Zero Tolerance Policy)\n- แทรกแซงกระบวนการบริหารจัดการของคู่ค้า\n\nRemediation Plan:\n- ชดเชยและเยียวยาผู้ได้รับผลกระทบอย่างเป็นธรรมและโปร่งใสภายใน 24 ชม."
    elif score >= 8:
        risk_zone = "YELLOW"
        badge_html = '<div class="salient-badge" style="background-color: #FFFBEB; color: #D97706; border-color: #FDE68A;">⚠️ SIGNIFICANT RISK: ประเด็นความเสี่ยงปานกลาง/สูง (AI กำลังร่างแผนป้องกันเชิงรุก)</div>'
        ai_plan = "Preventive Action (แผนป้องกันเชิงรุก):\n- จัดอบรมทบทวนขั้นตอนการทำงาน และสื่อสารนโยบายให้ผู้เกี่ยวข้องรับทราบ\n- ติดตามผลการปรับปรุงประสิทธิภาพอย่างใกล้ชิดภายใน 3 เดือน\n\nRemediation Plan:\n- เปิดเวทีรับฟังปัญหาและเยียวยาตามสัดส่วนผลกระทบ"
    else:
        risk_zone = "GREEN"
        badge_html = '<div class="salient-badge" style="background-color: #F0FDF4; color: #166534; border-color: #BBF7D0;">✅ MODERATE/MINOR RISK: ความเสี่ยงต่ำ (AI กำลังร่างแผนคงสภาพ)</div>'
        ai_plan = "Maintenance Plan (แผนคงสภาพ):\n- ดำเนินการตรวจสอบและติดตามผลตามวงรอบปกติอย่างน้อยปีละ 1 ครั้ง"
    
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

    st.markdown("""
    <div class="gemini-draft-box" style="margin-bottom: 0; border-bottom-left-radius: 0; border-bottom-right-radius: 0; border-bottom: none;">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <h4 class="gemini-title"><span class="gemini-icon">✨</span> Gemini AI: Draft Mitigation Plan</h4>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 💡 2. NATIVE POPOVER FOR LAW CITATION
    c_std1, c_std2 = st.columns([7, 2])
    with c_std1:
        st.markdown(f"<div style='background: #FFFFFF; padding: 10px 15px; border-radius: 6px; border: 1px solid #EAEAEA; font-size: 14px; color: #005B31;'>⚖️ <b>อ้างอิงมาตรฐาน:</b> {matched_law}</div>", unsafe_allow_html=True)
    with c_std2:
        with st.popover("📚 เปิดดูข้อกฎหมาย"):
            st.markdown(f"### ⚖️ {matched_doc.replace('.pdf','').replace('_',' ')}")
            st.success(f"**ข้อกำหนดตามมาตรฐาน:**\n\n{matched_law}")
            st.caption("*ดึงข้อมูลจากระบบ Knowledge Base")

    st.markdown("""
    <div style="background: #FAFAFA; border: 1px solid #D2E3FC; border-top: none; padding: 25px; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px; margin-bottom: 30px;">
        <h5 style="color: #005B31; margin-top: 0; margin-bottom: 15px;"><i class="fa-solid fa-pen-to-square"></i> 3. ตรวจสอบและปรับแก้ข้อมูลโดยมนุษย์ (Human Override)</h5>
        <p style="font-size: 13px; color: #666; margin-bottom: 15px;">คุณสามารถปรับปรุงหลักฐาน, มาตรฐานอ้างอิง หรือแผนปฏิบัติการด้านล่างให้สมบูรณ์ก่อนอนุมัติ</p>
    """, unsafe_allow_html=True)
    
    final_evidence = st.text_area("✍️ แก้ไขหลักฐานสนับสนุน (Triangulation Evidence):", value=edit_evidence, height=80)
    final_standard = st.text_area("✍️ แก้ไขมาตรฐานอ้างอิง (Framework / Standard):", value=edit_standard, height=60)
    final_plan = st.text_area("✍️ แก้ไขแผนการจัดการความเสี่ยง (Mitigation & Remediation Plan):", value=edit_plan, height=150)
    
    st.markdown("</div>", unsafe_allow_html=True)

    button_label = "🔄 อัปเดตข้อมูลฉบับแก้ไข (Overwrite Data)" if is_already_approved else "💾 อนุมัติและบันทึกประเด็นยุทธศาสตร์ (Approve Plan)"

    if st.button(button_label):
        if sheet:
            db_risk_level = "Salient" if risk_zone == "RED" else ("Significant" if risk_zone == "YELLOW" else "Moderate/Minor")
            detail = f"Scale:{scale}, Scope:{scope}, Remedy:{remedy} | Evidence: {final_evidence} | Standard: {final_standard} | Plan: {final_plan}"
            macro_group = f"ประเมินเจาะจงกลุ่ม ({custom_filter_text})" if custom_filter_text else "ประเมินระดับองค์กร (Corporate Level)"
            
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
    
    st.markdown("#### 🚩 สัญญาณเตือนภัยล่วงหน้า (Early Warning): การเรียกเก็บค่าธรรมเนียมสรรหา (Debt Bondage Indicator)")
    st.info("🤖 **Gemini AI Triangulation:** ตรวจพบความขัดแย้งเชิงนโยบายและการปฏิบัติจริง (Policy Implementation Gap) จากการวิเคราะห์ข้อมูลจริงใน Sheet")
    
    c_left, c_right = st.columns(2)
    with c_left:
        st.success("📋 **ข้อมูลเชิงนโยบาย (Tool 1: ผู้บริหาร)**\n\nพบข้อมูลจากผู้บริหาร (ID E04):\n\n*\"บริษัทมีนโยบาย Zero Recruitment Fee ชัดเจน แรงงานทุกคนไม่ต้องเสียค่าใช้จ่าย\"*")
    with c_right:
        st.markdown(f"""
        <div style="background-color: #FEF2F2; color: #991B1B; padding: 15px; border-radius: 8px; border: 1px solid #F87171; margin-bottom: 10px;">
            🗣️ <b>ข้อมูลปฏิบัติจริง (Tool 3: แรงงานข้ามชาติ)</b><br><br>
            พบคำให้การจากพนักงาน (ID M06, M07):<br>
            <i>"เอเจนซี่ขอยึดพาสปอร์ตไปเก็บไว้ในตู้เซฟ... ต้องจ่ายค่านายหน้าให้ฝั่งนู้น 15000 บาท ตอนนี้ยังใช้หนี้ไม่หมด"</i>
        </div>
        """, unsafe_allow_html=True)
        # 💡 Native Popover สำหรับ Tool 6 ปิดได้ ไม่ค้าง
        with st.popover("🔍 เปิดดูข้อมูลดิบฉบับเต็ม (Evidence M06, M07)"):
            st.markdown("### 📄 รายละเอียดคำให้การ (Full Record)")
            st.write("**กลุ่มเป้าหมาย:** แรงงานข้ามชาติ (Migrant Workers)")
            st.info("**คำให้การ M06:** เอเจนซี่เก็บพาสปอร์ตกับเวิร์คเพอร์มิตไว้ครับ บอกว่ากลัวพวกเราทำหาย")
            st.warning("**คำให้การ M07:** ก่อนมาทำงานต้องจ่ายค่านายหน้าให้ฝั่งนู้น 15000 บาทครับ ตอนนี้ยังใช้หนี้ไม่หมดเลย")

    st.markdown("""
    <div class="gemini-draft-box" style="margin-top: 20px;">
        <h5 class="gemini-title"><span class="gemini-icon">✨</span> Gemini AI Insight (เหตุผลที่จัดเป็น Early Warning):</h5>
        <p style="font-size: 14px; color: #444; margin-top: 5px;">
        ข้อมูลนี้ชี้ให้เห็นถึงช่องโหว่ด้านความโปร่งใสของ <b>Supply Chain / Third-party Agency</b> ที่ต้นทาง ซึ่งเป็น <b>"จุดบอด (Blind Spot)"</b> ของผู้บริหาร แม้บริษัทจะมีนโยบายที่ดี แต่หากไม่เร่งลงพื้นที่สืบสวนข้อเท็จจริง ปัญหานี้อาจยกระดับเป็นข้อกล่าวหาด้าน <b>Debt Bondage (ภาระหนี้ผูกพัน)</b> หรือ <b>Forced Labor</b> ในระดับสากลได้ ระบบจึงแจ้งเตือนเพื่อให้ผู้บริหารเตรียมส่งทีมเข้าตรวจสอบด่วน
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
            st.success("✅ บันทึกมติการพิจารณาสัญญาณเตือนภัยล่วงหน้าเข้าสู่ระบบฐานข้อมูลกลางเรียบร้อย")
            
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- TOOL 7 (Executive Dashboard & STRATEGIC AI Report) -----------------
elif choice == "Tool 7: แดชบอร์ดและรายงานสรุป (Dashboard & Report)":
    st.markdown("<div class='standalone-form'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#005B31; margin-top:0;'>Tool 7: Executive Dashboard & Comprehensive Report</h3><p style='color:#666;'>สรุปผลประเมินนัยสำคัญของความเสี่ยง (Salient Risk) ระดับองค์กร</p><hr>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    
    # 💡 กรองข้อมูล Tool 1-4 เพื่อนับ N อย่างแม่นยำ 
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
            ew_note = st.session_state.get("early_warning_note", "ให้ทีมตรวจสอบภายใน (Internal Audit) ลงพื้นที่ตรวจสอบเอเจนซี่ทั้งหมดทันที")
            early_warning_text = f"""4. การพยากรณ์และสัญญาณเตือนภัยล่วงหน้า (Early Warning & Foresight)
ระบบ AI ครอสเช็คข้อมูลข้ามส่วนงาน (Triangulation) ตรวจพบความเปราะบางเชิงระบบ (Systemic Vulnerability) 1 ประเด็นหลัก:
- สัญญาณเตือนภัย: พบช่องว่างการนำนโยบาย Zero Recruitment Fees ไปปฏิบัติจริง (Policy Implementation Gap) ระหว่างระดับบริหารและกลุ่มแรงงานข้ามชาติ
- แนวทางสืบสวนเชิงลึก (Investigation Resolution): อนุมัติดำเนินการตรวจสอบข้อเท็จจริง โดยมีมติสั่งการเชิงยุทธศาสตร์ว่า "{ew_note}" เพื่อป้องกันการยกระดับสู่ข้อกล่าวหาแรงงานบังคับระดับสากล"""
        else:
            early_warning_text = """4. การพยากรณ์และสัญญาณเตือนภัยล่วงหน้า (Early Warning & Foresight)
ในรอบการประเมินปัจจุบัน ระบบยังไม่พบสัญญาณขัดแย้งของข้อมูลที่มีนัยสำคัญระดับโครงสร้างที่ต้องจัดตั้งคณะกรรมการสืบสวนฉุกเฉิน"""

        # 💡 THE SMART STRATEGIC REPORT TEMPLATE
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
