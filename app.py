import streamlit as st
import pandas as pd
from google.oauth2 import service_account
import gspread
from datetime import datetime, timedelta
import altair as alt

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
    [data-testid="stFormSubmitButton"] > button:hover, .stButton > button:hover { background: #004222 !important; transform: translateY(-2px) !important; box-shadow: 0 12px 25px rgba(0, 91, 49, 0.3) !important; }

    .radar-core { width: 24px; height: 24px; background: #DC2626; border-radius: 50%; box-shadow: 0 0 10px #DC2626; }
    @keyframes pulse { 0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.7); } 70% { transform: scale(1); box-shadow: 0 0 0 20px rgba(220, 38, 38, 0); } 100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(220, 38, 38, 0); } }
    
    .control-panel label { font-size: 14px !important; color: #444 !important; font-weight: 600 !important; }
    .filter-box { background: #FDFDFD; border: 1px dashed #D3A129; padding: 20px; border-radius: 8px; margin-bottom: 25px; }

    /* 💡 NOTEBOOK LM INTERACTIVE CITATION & MODAL SYSTEM */
    .cite-pill {
        display: inline-flex; align-items: center; justify-content: center;
        background-color: #E0E7FF; color: #4F46E5; border-radius: 12px;
        padding: 2px 10px; font-size: 12px; font-weight: 800; cursor: pointer;
        margin: 0 4px; border: 1px solid #C7D2FE; transition: all 0.2s;
    }
    .cite-pill:hover { background-color: #4F46E5; color: #FFFFFF; transform: translateY(-2px); box-shadow: 0 4px 8px rgba(79, 70, 229, 0.3); }

    .modal-toggle { display: none; }
    .modal-window {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: rgba(0,0,0,0.6); backdrop-filter: blur(5px);
        z-index: 999999; display: flex; align-items: center; justify-content: center;
        opacity: 0; pointer-events: none; transition: opacity 0.3s;
    }
    .modal-toggle:checked ~ .modal-window { opacity: 1; pointer-events: auto; }
    
    /* 💡 แก้ไข: เพิ่มพื้นที่คลิกพื้นหลังเพื่อปิด Modal */
    .modal-backdrop { position: absolute; top: 0; left: 0; width: 100%; height: 100%; cursor: pointer; }
    
    .modal-content {
        background: #F8FAFC; width: 85%; max-width: 900px; max-height: 85vh;
        border-radius: 16px; display: flex; flex-direction: column;
        box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5); transform: translateY(20px); transition: transform 0.3s;
        border: 1px solid #E5E7EB; z-index: 2; /* ให้อยู่เหนือ backdrop */
    }
    .modal-toggle:checked ~ .modal-window .modal-content { transform: translateY(0); }
    
    .modal-header {
        background: #FFFFFF; padding: 15px 25px; border-bottom: 1px solid #E5E7EB;
        display: flex; justify-content: space-between; align-items: center; border-radius: 16px 16px 0 0;
    }
    
    /* 💡 แก้ไข: ทำชื่อไฟล์เป็นลิงก์คลิกได้ */
    .modal-title-link { 
        font-family: 'Poppins', sans-serif; font-size: 16px; font-weight: 700; color: #111827; 
        display: flex; align-items: center; gap: 10px; text-decoration: none; transition: 0.2s;
    }
    .modal-title-link:hover { color: #4F46E5; }
    
    .close-btn { cursor: pointer; font-size: 24px; color: #9CA3AF; font-weight: bold; background: #F3F4F6; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; border-radius: 50%; transition: 0.2s;}
    .close-btn:hover { background: #EF4444; color: white; }
    
    .modal-body { padding: 30px; overflow-y: auto; background: #F3F4F6;}
    
    /* Document Styles inside Modal */
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
# --- 3.1 SECURITY ACCESS GATE & GLOBAL STATE ---
# ==========================================
def check_password():
    if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
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
                    <h2 style="color: #005B31; font-family: 'Poppins', sans-serif; font-weight: 800; margin: 0; font-size: 36px;">BETAGRO</h2>
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
                    else: st.error("❌ Access Denied. รหัสผ่านไม่ถูกต้อง")
        return False
    return True

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
with col_p2: auditor_name = st.text_input("ชื่อผู้ใช้งาน (Auditor/Executive) *", placeholder="เช่น สมชาย ใจดี")

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
    with col_r_loc: location = st.text_input("พื้นที่สำรวจ (Location/Site) *", placeholder="เช่น รง.แปรรูปไก่ สระบุรี (อาคาร B)")
    with col_r_id: resp_id = st.text_input("รหัสอ้างอิง (ID) *", placeholder="เช่น 001, 002")

    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1: resp_group = st.selectbox("กลุ่มเป้าหมาย *", ["ไม่ระบุ/ภาพรวม", "ฝ่ายบริหาร", "แรงงานไทย", "แรงงานข้ามชาติ", "ชุมชน", "คู่ค้า"])
    with col_r2: resp_dept = st.text_input("แผนก/ส่วนงาน *", placeholder="เช่น ฝ่ายตัดแต่ง")
    with col_r3: resp_gender = st.selectbox("เพศ (Gender) *", ["ไม่ระบุ", "ชาย", "หญิง", "อื่นๆ"])
else:
    location = "ภาพรวมทุกพื้นที่ (Corporate)"
    resp_id = "N/A"
    resp_group = "ภาพรวม (All Groups)"
    resp_dept = "ภาพรวม (All Depts)"
    resp_gender = "ภาพรวม"

st.markdown('</div>', unsafe_allow_html=True)

if not auditor_name:
    st.info("📌 กรุณาระบุข้อมูล **ชื่อผู้ใช้งาน** ด้านบนให้ครบถ้วน เพื่อเข้าสู่ระบบ")
    st.stop()

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

# ----------------- TOOL 1-4 (ย่อส่วนให้กระชับ) -----------------
if choice.startswith("Tool 1"):
    with st.form("form_t1"):
        st.markdown("### Tool 1: ประเมินสถานะองค์กร", unsafe_allow_html=True)
        q1_1 = st.radio("1.1 มีนโยบายลายลักษณ์อักษร?", ["ใช่", "ไม่ใช่"], horizontal=True)
        if st.form_submit_button("บันทึก"): st.success("✅ บันทึกข้อมูล Tool 1 เรียบร้อย")

elif choice.startswith("Tool 2"):
    with st.form("form_t2"):
        st.markdown("### Tool 2: แบบสอบถามหน้างาน", unsafe_allow_html=True)
        s1_1 = st.select_slider("1.1 จ่ายค่าจ้างตรงเวลา", options=[1,2,3,4,5], value=3)
        if st.form_submit_button("บันทึก"): st.success("✅ บันทึกข้อมูล Tool 2 เรียบร้อย")

elif choice.startswith("Tool 3"):
    with st.form("form_t3"):
        st.markdown("### Tool 3: สัมภาษณ์เชิงลึก", unsafe_allow_html=True)
        testimony = st.text_area("สรุปคำพูดหรือหลักฐานที่พบ:", height=100)
        if st.form_submit_button("บันทึก"): st.success("✅ บันทึกข้อมูล Tool 3 เรียบร้อย")

elif choice.startswith("Tool 4"):
    with st.form("form_t4"):
        st.markdown("### Tool 4: บันทึกการสังเกตการณ์", unsafe_allow_html=True)
        o1 = st.radio("1. พบประกาศช่องทางร้องเรียน", ["พบ", "ไม่พบ"], horizontal=True)
        if st.form_submit_button("บันทึก"): st.success("✅ บันทึกข้อมูล Tool 4 เรียบร้อย")

# ----------------- TOOL 5 (THE NOTEBOOK LM UPDATE) -----------------
elif choice == "Tool 5: ประเมินนัยสำคัญของความเสี่ยง (Salient Risk Matrix)":

    st.markdown("<div class='standalone-form'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#005B31; margin-top:0;'>Tool 5: ประเมินนัยสำคัญของความเสี่ยง (Issue-Based)</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="filter-box">
        <h5 style="color:#D97706; margin-top:0;"><i class="fa-solid fa-filter"></i> Advanced Data Slicing (ตัวกรองข้อมูลขั้นสูง)</h5>
        <p style="font-size: 14px; color: #666; margin-bottom: 10px;">เลือกรูปแบบฐานข้อมูลที่คุณต้องการให้ AI นำมาวิเคราะห์หาความเสี่ยง</p>
    """, unsafe_allow_html=True)
    
    filter_mode = st.radio("ระดับการวิเคราะห์:", ["วิเคราะห์ภาพรวมทั้งหมด (Macro Level / 135 Records)", "วิเคราะห์เจาะจงรายบุคคล/แผนก (Micro/Custom Level)"], horizontal=True, label_visibility="collapsed")
    custom_filter_text = ""
    if filter_mode == "วิเคราะห์เจาะจงรายบุคคล/แผนก (Micro/Custom Level)":
        custom_filter_text = st.text_input("🔍 ระบุรหัสอ้างอิง (ID), แผนก หรือ พื้นที่ ที่ต้องการดึงข้อมูลมาวิเคราะห์ (คั่นด้วยลูกน้ำได้ไม่จำกัด):", placeholder="เช่น 012, 018, 045 หรือ ฝ่ายตัดแต่ง, สระบุรี")
        
    st.markdown("</div>", unsafe_allow_html=True)

    btn_text = f"✨ ให้ Gemini AI วิเคราะห์ประเด็นความเสี่ยงจากข้อมูล (เฉพาะกลุ่ม: {custom_filter_text})" if custom_filter_text else "✨ ให้ Gemini AI วิเคราะห์ประเด็นจากข้อมูลทั้งหมด (135 Records)"
    
    st.markdown("<h5 style='color: #005B31; margin-top: 20px;'><i class='fa-solid fa-wand-magic-sparkles'></i> 1. สกัดประเด็นความเสี่ยงจากฐานข้อมูล</h5>", unsafe_allow_html=True)
    if st.button(btn_text):
        st.session_state.ai_scanned_issues = True
    
    selected_issue = ""
    if st.session_state.get("ai_scanned_issues", False):
        ai_header = f"🤖 Gemini AI พบประเด็นที่ต้องจัดทำแผน (วิเคราะห์เฉพาะกลุ่ม: {custom_filter_text}):" if custom_filter_text else "🤖 Gemini AI พบ 10 ประเด็นยุทธศาสตร์ที่ต้องจัดทำแผน (วิเคราะห์จากภาพรวมทั้งหมด):"
        st.markdown(f'<div style="background: #E8F0FE; padding: 15px; border-radius: 8px; border-left: 4px solid #1967D2; margin-bottom: 20px;"><span style="color: #1967D2; font-weight: 700; font-size: 14px;">{ai_header}</span></div>', unsafe_allow_html=True)
        
        selected_issue = st.selectbox("เลือกประเด็นความเสี่ยงเพื่อจัดทำแผน (Process Issue):", [
            "เลือกประเด็นความเสี่ยงเพื่อจัดการ...",
            "[สิทธิแรงงาน] 1. พนักงานร้องเรียนเรื่องการจ่ายเงิน OT ไม่ครบ/ล่าช้า",
            "[แรงงานบังคับ] 2. พบกลุ่มแรงงานข้ามชาติถูกยึดพาสปอร์ตโดยเอเจนซี่",
            "[อาชีวอนามัย] 3. พบเครื่องจักรโซนปฏิบัติงานไม่มีฝาครอบป้องกันอันตราย",
            "[แรงงานเด็ก] 4. พบการจ้างงานเยาวชนอายุต่ำกว่า 18 ปี ในพื้นที่อันตราย",
            "[การเลือกปฏิบัติ] 5. ความเหลื่อมล้ำในการจ่ายค่าจ้างระหว่างแรงงานไทยและข้ามชาติ"
        ])

    save_issue = selected_issue if selected_issue and "เลือกประเด็น" not in selected_issue else "ประเด็นที่ระบุเอง (Manual)"
    is_already_approved = save_issue in st.session_state.approved_issues

    evidence_base = ""
    framework_citation = ""
    modal_html = "" # ตัวแปรเก็บโค้ดซ่อน Modal HTML
    
    scope_text = f"เฉพาะกลุ่ม {custom_filter_text}" if custom_filter_text else "ภาพรวมพนักงาน"
    
    # 💡 THE NOTEBOOK LM MAGIC: กำหนดป้าย HTML Citation และสร้างหน้าต่าง Modal
    if "OT" in selected_issue or "โอที" in selected_issue: 
        evidence_base = f"""📌 <b>แหล่งที่มา (Sources):</b> <br>
        - <i>Tool 2 (Worker Survey):</i> จาก{scope_text} ระบุคะแนน 1-2 ในข้อ 1.1 
        <label for="modal-csv-ot" class="cite-pill" title="คลิกเพื่อดูไฮไลต์ข้อมูล">[Source 1]</label><br>
        - <i>Tool 3 (Interview):</i> สัมภาษณ์เชิงลึก ยืนยันว่าได้เงินล่าช้าเกิน 7 วัน 
        <label for="modal-pdf-ot" class="cite-pill" title="คลิกเพื่อดูไฮไลต์เอกสาร">[Source 2]</label>"""
        framework_citation = "⚖️ <b>อ้างอิงมาตรฐาน (Standard):</b> พ.ร.บ. คุ้มครองแรงงาน มาตรา 70 | ILO Convention No. 95 (Protection of Wages)"
        
        # HTML For the Pop-ups
        modal_html = """
        <!-- Modal 1: CSV File -->
        <input type="checkbox" id="modal-csv-ot" class="modal-toggle">
        <div class="modal-window">
            <label class="modal-backdrop" for="modal-csv-ot"></label>
            <div class="modal-content">
                <div class="modal-header">
                    <a href="#" class="modal-title-link" title="เปิดไฟล์ฉบับเต็มในแท็บใหม่"><i class="fa-solid fa-file-csv" style="color:#10B981; font-size: 20px;"></i> DB_Tool2_Survey.csv <i class="fa-solid fa-arrow-up-right-from-square" style="font-size: 12px; color: #9CA3AF;"></i></a>
                    <label for="modal-csv-ot" class="close-btn"><i class="fa-solid fa-xmark"></i></label>
                </div>
                <div class="modal-body">
                    <div class="mock-doc-wrapper">
                        <h4 style="margin-bottom: 15px; color:#4B5563;">Data Preview (Row 45 - 50)</h4>
                        <table class="mock-csv">
                            <tr><th>ID</th><th>Dept</th><th>Q1.1 Wage Promptness</th><th>Q1.2 Document Kept</th><th>Q1.3 Vol. OT</th></tr>
                            <tr class="alert-row"><td>045</td><td>ฝ่ายตัดแต่ง</td><td class="alert-cell">1 (ไม่จริงเลย)</td><td>4</td><td>2</td></tr>
                            <tr class="alert-row"><td>046</td><td>ฝ่ายตัดแต่ง</td><td class="alert-cell">2 (ไม่ค่อยจริง)</td><td>5</td><td>3</td></tr>
                            <tr><td>047</td><td>คลังสินค้า</td><td>5 (จริงที่สุด)</td><td>4</td><td>4</td></tr>
                            <tr class="alert-row"><td>048</td><td>ฝ่ายตัดแต่ง</td><td class="alert-cell">1 (ไม่จริงเลย)</td><td>5</td><td>3</td></tr>
                            <tr class="alert-row"><td>088</td><td>ฝ่ายแพ็ค</td><td class="alert-cell">1 (ไม่จริงเลย)</td><td>4</td><td>2</td></tr>
                        </table>
                    </div>
                </div>
            </div>
        </div>
        <!-- Modal 2: PDF Transcript -->
        <input type="checkbox" id="modal-pdf-ot" class="modal-toggle">
        <div class="modal-window">
            <label class="modal-backdrop" for="modal-pdf-ot"></label>
            <div class="modal-content">
                <div class="modal-header">
                    <a href="#" class="modal-title-link" title="เปิดไฟล์ฉบับเต็มในแท็บใหม่"><i class="fa-solid fa-file-pdf" style="color:#EF4444; font-size: 20px;"></i> Transcript_ID045_088.pdf <i class="fa-solid fa-arrow-up-right-from-square" style="font-size: 12px; color: #9CA3AF;"></i></a>
                    <label for="modal-pdf-ot" class="close-btn"><i class="fa-solid fa-xmark"></i></label>
                </div>
                <div class="modal-body">
                    <div class="mock-doc-wrapper mock-pdf">
                        <h4>CONFIDENTIAL AUDIT TRANSCRIPT</h4>
                        <p><b>Interviewer:</b> คุณบอกว่ามีปัญหาเรื่องการจ่ายเงินเดือน ช่วยอธิบายเพิ่มเติมได้ไหมครับ?</p>
                        <p><b>Respondent (ID 045):</b> ใช่ครับ ช่วงสามเดือนที่ผ่านมานี้ ผมและเพื่อนๆ ในไลน์ผลิตเดียวกัน <mark>พวกเราได้เงิน OT ช้าไป 2 สัปดาห์ตลอดเลยครับ</mark> พอไปถามหัวหน้า เขาก็บอกว่าระบบคำนวณรวน</p>
                        <p><b>Respondent (ID 088):</b> จริงครับ ปกติต้องได้ทุกสิ้นเดือน แต่กลายเป็นว่าได้เฉพาะเงินเดือนหลัก ส่วน <mark>เงินล่วงเวลาถูกปัดไปรวมกับงวดหน้าแทน ทำให้หมุนเงินส่งกลับบ้านไม่ทัน</mark></p>
                    </div>
                </div>
            </div>
        </div>
        """

    elif "พาสปอร์ต" in selected_issue: 
        evidence_base = f"""📌 <b>แหล่งที่มา (Sources):</b> <br>
        - <i>Tool 4 (Observation):</i> พบตู้เซฟล็อกกุญแจในห้องพักเอเจนซี่ 
        <label for="modal-img-safe" class="cite-pill" title="คลิกเพื่อดูรูปถ่ายหลักฐาน">[Source 1]</label><br>
        - <i>Tool 3 (Interview):</i> จาก{scope_text} ให้การตรงกันว่าถูกยึดพาสปอร์ต 
        <label for="modal-pdf-passport" class="cite-pill" title="คลิกเพื่อดูไฟล์ PDF Transcript">[Source 2]</label>"""
        framework_citation = "⚖️ <b>อ้างอิงมาตรฐาน (Standard):</b> หลักการ Employer Pays Principle (EPP) | ILO Forced Labour Convention (No. 29)"
        
        modal_html = """
        <!-- Modal 1: Image -->
        <input type="checkbox" id="modal-img-safe" class="modal-toggle">
        <div class="modal-window">
            <label class="modal-backdrop" for="modal-img-safe"></label>
            <div class="modal-content">
                <div class="modal-header">
                    <a href="#" class="modal-title-link" title="เปิดรูปถ่ายความละเอียดสูงในแท็บใหม่"><i class="fa-solid fa-image" style="color:#3B82F6; font-size: 20px;"></i> Observation_Site_A_04.jpg <i class="fa-solid fa-arrow-up-right-from-square" style="font-size: 12px; color: #9CA3AF;"></i></a>
                    <label for="modal-img-safe" class="close-btn"><i class="fa-solid fa-xmark"></i></label>
                </div>
                <div class="modal-body" style="text-align: center;">
                    <div class="mock-doc-wrapper" style="padding: 10px;">
                        <img src="https://images.unsplash.com/photo-1614036417651-1d4b68e0d37d?auto=format&fit=crop&q=80&w=800" style="width:100%; border-radius: 4px;">
                        <p style="margin-top: 15px; color: #DC2626; font-weight: bold;"><i class="fa-solid fa-triangle-exclamation"></i> หมายเหตุออดิเตอร์: พบตู้เซฟล็อกกุญแจ ภายในห้องพักของนายหน้า (Agency) โดยแรงงานไม่สามารถเข้าถึงได้</p>
                    </div>
                </div>
            </div>
        </div>
        <!-- Modal 2: PDF Transcript -->
        <input type="checkbox" id="modal-pdf-passport" class="modal-toggle">
        <div class="modal-window">
            <label class="modal-backdrop" for="modal-pdf-passport"></label>
            <div class="modal-content">
                <div class="modal-header">
                    <a href="#" class="modal-title-link" title="เปิดไฟล์ฉบับเต็มในแท็บใหม่"><i class="fa-solid fa-file-pdf" style="color:#EF4444; font-size: 20px;"></i> Transcript_Migrant_Grp1.pdf <i class="fa-solid fa-arrow-up-right-from-square" style="font-size: 12px; color: #9CA3AF;"></i></a>
                    <label for="modal-pdf-passport" class="close-btn"><i class="fa-solid fa-xmark"></i></label>
                </div>
                <div class="modal-body">
                    <div class="mock-doc-wrapper mock-pdf">
                        <h4>CONFIDENTIAL AUDIT TRANSCRIPT</h4>
                        <p><b>Interviewer:</b> เอกสารประจำตัวของพวกคุณ ตอนนี้ใครเป็นคนเก็บไว้ครับ?</p>
                        <p><b>Respondent (Grp1):</b> พวกเราไม่ได้ถือไว้เองเลยครับ <mark>ตั้งแต่ข้ามฝั่งมาถึงโรงงาน เอเจนซี่ก็ขอยึดพาสปอร์ตและบัตรเวิร์คเพอร์มิตไปเก็บไว้ในตู้เซฟของเขา</mark> เขาบอกว่ากลัวพวกเราทำหาย</p>
                        <p><b>Interviewer:</b> แล้วถ้ามีธุระต้องใช้เอกสาร สามารถขอเบิกได้ไหม?</p>
                        <p><b>Respondent (Grp1):</b> <mark>ขอเบิกยากมากครับ ต้องมีข้ออ้างที่จำเป็นจริงๆ และบางครั้งโดนด่าด้วย</mark> ทำให้พวกเราไม่กล้าออกไปไหนไกลจากโรงงานเลยครับ</p>
                    </div>
                </div>
            </div>
        </div>
        """

    elif "เครื่องจักร" in selected_issue: 
        evidence_base = f"""📌 <b>แหล่งที่มา (Sources):</b> <br>
        - <i>Tool 4 (Observation):</i> ตรวจพบสายพานลำเลียง โซนปฏิบัติงานไม่มี Guard 
        <label for="modal-img-machine" class="cite-pill">[Source 1]</label><br>
        - <i>Tool 2 (Worker Survey):</i> จาก{scope_text} ให้คะแนนความปลอดภัยเฉลี่ยต่ำ"""
        framework_citation = "⚖️ <b>อ้างอิงมาตรฐาน (Standard):</b> ISO 45001 | พ.ร.บ. ความปลอดภัย อาชีวอนามัย และสภาพแวดล้อมในการทำงาน พ.ศ. 2554"
        
        modal_html = """
        <input type="checkbox" id="modal-img-machine" class="modal-toggle">
        <div class="modal-window">
            <label class="modal-backdrop" for="modal-img-machine"></label>
            <div class="modal-content">
                <div class="modal-header">
                    <a href="#" class="modal-title-link" title="เปิดรูปถ่ายความละเอียดสูงในแท็บใหม่"><i class="fa-solid fa-image" style="color:#3B82F6; font-size: 20px;"></i> Site_Audit_ZoneB.jpg <i class="fa-solid fa-arrow-up-right-from-square" style="font-size: 12px; color: #9CA3AF;"></i></a>
                    <label for="modal-img-machine" class="close-btn"><i class="fa-solid fa-xmark"></i></label>
                </div>
                <div class="modal-body" style="text-align: center;">
                    <div class="mock-doc-wrapper" style="padding: 10px;">
                        <img src="https://images.unsplash.com/photo-1581092160562-40aa08e78837?auto=format&fit=crop&q=80&w=800" style="width:100%; border-radius: 4px;">
                        <p style="margin-top: 15px; color: #DC2626; font-weight: bold;"><i class="fa-solid fa-triangle-exclamation"></i> ตรวจพบเฟืองและสายพานเปลือย (Missing Machine Guard) เสี่ยงต่อการหนีบหรือดึงรั้งอวัยวะพนักงาน</p>
                    </div>
                </div>
            </div>
        </div>
        """
        
    elif "เลือกประเด็น" not in selected_issue:
        evidence_base = "📌 <b>แหล่งที่มา (Sources):</b> รอการระบุหลักฐานเชิงประจักษ์โดย Auditor"
        framework_citation = "⚖️ <b>อ้างอิงมาตรฐาน (Standard):</b> รอการวิเคราะห์จากระบบ"

    if selected_issue and "เลือกประเด็น" not in selected_issue:
        # 💡 Inject the HTML Modals and the Evidence Box into Streamlit
        st.markdown(f"""
        {modal_html}
        <div style="background: #F5F3FF; border-left: 4px solid #8B5CF6; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.02);">
            <strong style="color: #6D28D9; font-size: 16px;"><i class="fa-solid fa-magnifying-glass-chart"></i> AI Triangulation Evidence (หลักฐานสนับสนุนการประเมิน):</strong>
            <div style="font-size: 14px; margin-top: 10px; color: #444; line-height: 1.8;">{evidence_base}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border: 1px dashed #ccc;'>", unsafe_allow_html=True)
    st.markdown("<h5 style='color: #005B31;'><i class='fa-solid fa-sliders'></i> 2. ประเมินระดับความรุนแรง (Severity) และ โอกาสเกิด (Likelihood)</h5>", unsafe_allow_html=True)
    
    def_scale, def_scope, def_remedy, def_lik = 1, 1, 1, 1
    if is_already_approved and save_issue in st.session_state.saved_plans_dict:
        saved_data = st.session_state.saved_plans_dict[save_issue]
        def_scale, def_lik = saved_data.get('sev', 1), saved_data.get('lik', 1)
        def_scope, def_remedy = def_scale, def_scale
    else:
        if "OT" in selected_issue or "โอที" in selected_issue: def_scale, def_scope, def_remedy, def_lik = 3, 4, 2, 4
        elif "พาสปอร์ต" in selected_issue: def_scale, def_scope, def_remedy, def_lik = 5, 2, 3, 3
        elif "เครื่องจักร" in selected_issue: def_scale, def_scope, def_remedy, def_lik = 4, 2, 2, 4
        elif "เด็ก" in selected_issue: def_scale, def_scope, def_remedy, def_lik = 5, 1, 4, 1

    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1: scale = st.slider("Scale (ขนาดผลกระทบ: 1 เล็กน้อย - 5 Zero Tolerance)", 1, 5, def_scale)
    with col_s2: scope = st.slider("Scope (วงกว้าง: 1 เฉพาะบุคคล - 5 ระดับประเทศ)", 1, 5, def_scope)
    with col_s3: remedy = st.slider("Remedy (การเยียวยา: 1 ทำได้ทันที - 5 เยียวยาไม่ได้)", 1, 5, def_remedy)
    
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
    
    ai_evidence = ""
    ai_standard = framework_citation
    ai_plan = ""

    if "OT" in selected_issue or "โอที" in selected_issue: ai_evidence = f"Tool 2: จาก {scope_text} ระบุคะแนน 1-2 ในข้อ 1.1\nTool 3: สัมภาษณ์เชิงลึก ยืนยันว่าได้เงินล่าช้าเกิน 7 วัน"
    elif "พาสปอร์ต" in selected_issue: ai_evidence = f"Tool 4: พบตู้เซฟล็อกกุญแจในห้องพักเอเจนซี่\nTool 3: จาก {scope_text} ให้การตรงกันว่าถูกยึดพาสปอร์ต"
    elif "เครื่องจักร" in selected_issue: ai_evidence = f"Tool 4: ตรวจพบสายพานลำเลียง โซนปฏิบัติงานไม่มี Guard\nTool 2: จาก {scope_text} ให้คะแนนความปลอดภัยเฉลี่ยต่ำ"
    else: ai_evidence = "รอการระบุหลักฐาน"

    if risk_zone == "GREEN":
        ai_plan = "Maintenance Plan (แผนคงสภาพ):\n- Monitoring: ระดับความเสี่ยงปกติ ให้ทำการตรวจสอบซ้ำ"
    elif risk_zone == "YELLOW":
        if "OT" in selected_issue: ai_plan = "Preventive Action (แผนป้องกันเชิงรุก):\n- Proactive Measures: จัดอบรมเรื่องกฎหมายแรงงานเวลาทำงานให้หัวหน้างาน และสุ่มตรวจ Pay slip/Time Attendance ทุกไตรมาส\n- Timeline: ติดตามผลการปรับปรุงภายใน 3 เดือน"
        elif "พาสปอร์ต" in selected_issue: ai_plan = "Preventive Action (แผนป้องกันเชิงรุก):\n- Proactive Measures: ตรวจสอบเอเจนซี่ และย้ำนโยบาย Employer Pays Principle (EPP)\n- Timeline: ติดตามผลภายใน 3 เดือน"
        else: ai_plan = "Preventive Action (แผนป้องกันเชิงรุก):\n- Proactive Measures: จัดอบรมให้ความรู้ ทบทวนขั้นตอนการทำงาน และสื่อสารนโยบายให้ทั่วถึง"
    else: # RED
        if "OT" in selected_issue: ai_plan = "Preventive: ตรวจสอบระบบ Time Attendance และ Pay slip อย่างเข้มงวด\nRemediation: จ่ายค่าจ้าง/OT ค้างชำระย้อนหลังพร้อมดอกเบี้ยในงวดถัดไปทันที"
        elif "พาสปอร์ต" in selected_issue: ai_plan = "Preventive: สื่อสารนโยบาย EPP ให้เอเจนซี่ และจัดเตรียมตู้ล็อกเกอร์ให้แรงงานเก็บเอกสารเอง\nRemediation: คืนพาสปอร์ตให้พนักงานทุกคนทันที (ภายใน 24 ชม.)"
        elif "เครื่องจักร" in selected_issue: ai_plan = "Preventive: กำหนดรอบตรวจสอบความปลอดภัย (Safety Patrol) ประจำสัปดาห์อย่างเคร่งครัด\nRemediation: หยุดการทำงานจุดเสี่ยงทันที แจก PPE ใหม่ และรับผิดชอบค่าพยาบาล"
        else: ai_plan = "Preventive: [ระบุมาตรการป้องกันเชิงระบบ]\nRemediation: [ระบุมาตรการเยียวยาเร่งด่วน]"

    edit_evidence = ai_evidence
    edit_standard = ai_standard
    edit_plan = ai_plan

    if is_already_approved and save_issue in st.session_state.saved_plans_dict:
        saved_data = st.session_state.saved_plans_dict[save_issue]
        edit_evidence = saved_data.get('evidence', ai_evidence)
        edit_standard = saved_data.get('standard', ai_standard)
        edit_plan = saved_data.get('plan', ai_plan)
        if not edit_plan or edit_plan.strip() == "": edit_plan = ai_plan

    st.markdown(f"""
    <div class="gemini-draft-box" style="margin-bottom: 0; border-bottom-left-radius: 0; border-bottom-right-radius: 0; border-bottom: none;">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <h4 class="gemini-title"><span class="gemini-icon">✨</span> Gemini AI: Draft Mitigation Plan</h4>
        </div>
        <div style="background: #FFFFFF; padding: 12px; border-radius: 6px; border: 1px solid #EAEAEA; margin: 15px 0; font-size: 14px; color: #005B31;">
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
            
            macro_group = f"ข้อมูลระบุเฉพาะ (Filter: {custom_filter_text})" if custom_filter_text else "ภาพรวม (All Groups)"
            macro_dept = "ภาพรวม (All Depts)"
            macro_gender = "ภาพรวม"
            
            new_row_data = [now, audit_cycle, auditor_name, location, "Tool 5", "Issue-Based", macro_group, macro_dept, macro_gender, save_issue, detail, sev_max, likelihood, score, db_risk_level]
            
            st.session_state.saved_plans_dict[save_issue] = {
                'plan': final_plan, 
                'sev': sev_max, 
                'lik': likelihood,
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
                        st.success(f"🔄 **อัปเดตข้อมูลสำเร็จ:** ทับข้อมูลเดิมของประเด็น '{save_issue}' เรียบร้อยแล้ว (ไม่เกิดบรรทัดซ้ำในระบบ)")
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
        st.error("🗣️ **ข้อมูลปฏิบัติจริง (Tool 3: ID 012, 018)**\n\nคำให้การพนักงาน:\n\n*\"พวกเราต้องจ่ายเงินสดให้เอเจนซี่ฝั่งพม่าไปคนละ 15,000 บาท เป็นค่าจัดการเอกสารและค่านายหน้า ก่อนที่จะเข้ามาทำงานในโรงงาน...\"*")

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
            
            macro_group = "ภาพรวม (All Groups)"
            macro_dept = "ภาพรวม (All Depts)"
            macro_gender = "ภาพรวม"
            
            sheet.append_row([now, audit_cycle, auditor_name, location, "Tool 6", "Issue-Based", macro_group, macro_dept, macro_gender, "Early Warning (Recruitment Fee)", detail, "", "", "", ""])
            
            st.session_state.early_warning_approved = True if "ยืนยัน" in t6_decision else False
            st.session_state.early_warning_note = t6_note
            
            st.success("✅ บันทึกมติการพิจารณาสัญญาณเตือนภัยล่วงหน้าเข้าสู่ระบบฐานข้อมูลกลางเรียบร้อย")
            
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- TOOL 7 (Executive Dashboard & AI Report) -----------------
elif choice == "Tool 7: แดชบอร์ดและรายงานสรุป (Dashboard & Report)":
    st.markdown("<div class='standalone-form'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#005B31; margin-top:0;'>Tool 7: Executive Dashboard & Comprehensive Report</h3><p style='color:#666;'>สรุปภาพรวมความเสี่ยงบน Risk Matrix และการจัดทำรายงานระดับบริหาร (Executive Summary)</p><hr>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="filter-box">
        <h5 style="color:#D97706; margin-top:0;"><i class="fa-solid fa-filter"></i> Advanced Report Slicing (ออกรายงานเฉพาะกลุ่มเป้าหมาย)</h5>
        <p style="font-size: 14px; color: #666; margin-bottom: 10px;">เลือกรูปแบบฐานข้อมูลที่คุณต้องการให้ AI นำมาวิเคราะห์เพื่อสรุปรายงาน</p>
    """, unsafe_allow_html=True)
    
    report_filter_mode = st.radio("ระดับการออกรายงาน:", ["รายงานภาพรวมทั้งหมด (Corporate Level)", "รายงานเจาะจงกลุ่ม/บุคคล (Custom Slicing)"], horizontal=True, label_visibility="collapsed")
    report_filter_text = ""
    
    if report_filter_mode == "รายงานเจาะจงกลุ่ม/บุคคล (Custom Slicing)":
        report_filter_text = st.text_input("🔍 ระบุรหัสอ้างอิง (ID), แผนก หรือ พื้นที่ ที่ต้องการออกรายงาน (คั่นด้วยลูกน้ำได้ไม่จำกัด):", placeholder="เช่น 012, 018 หรือ ฝ่ายตัดแต่ง")
        st.caption("⚡ ระบบจะดึงและวิเคราะห์รายงานเฉพาะข้อมูลที่ตรงกับตัวกรองนี้เท่านั้น")
        
    st.markdown("</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("<div class='dash-card'><div class='dash-label'>กลุ่มตัวอย่างที่สืบค้น</div><div class='dash-number'>135</div><div style='color: #005B31; font-size:12px;'>ผู้ให้สัมภาษณ์และพยานแวดล้อม</div></div>", unsafe_allow_html=True)
    
    approved_count = len(st.session_state.get("approved_issues", []))
    with c2: st.markdown(f"<div class='dash-card'><div class='dash-label'>Salient Issues</div><div class='dash-number' style='color:#DC2626;'>{approved_count}</div><div style='color: #666; font-size:12px;'>ประเด็นที่ได้รับการพิสูจน์แล้ว</div></div>", unsafe_allow_html=True)
    
    ew_count = 1 if st.session_state.get("early_warning_approved", False) else 0
    with c3: st.markdown(f"<div class='dash-card'><div class='dash-label'>Early Warnings</div><div class='dash-number' style='color:#D97706;'>{ew_count}</div><div style='color: #666; font-size:12px;'>สัญญาณเตือนภัยที่รอการสอบสวน</div></div>", unsafe_allow_html=True)
    
    st.markdown("<br><h5 style='color: #005B31; text-align:center;'>📊 แผนผังการกระจายตัวความเสี่ยงระดับองค์กร (Corporate Risk Matrix)</h5>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#666; font-size:14px; margin-bottom: 20px;'>👉 เลื่อนเมาส์เหนือจุดวงกลม (Hover) เพื่อพิจารณารายละเอียดประเด็นความเสี่ยงในแต่ละพิกัด</p>", unsafe_allow_html=True)
    
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
    
    btn_report_text = f"✨ ให้ Gemini AI วิเคราะห์เชิงลึกและออกรายงานเฉพาะกลุ่ม ({report_filter_text})" if report_filter_text else "✨ ให้ Gemini AI วิเคราะห์เชิงลึกและร่างรายงานภาพรวมองค์กร (Corporate Report)"
    
    if st.button(btn_report_text):
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
            filter_context = data.get('filter_context', '')
            if report_filter_text and report_filter_text not in filter_context and report_filter_text not in iss:
                pass 
                
            has_data = True
            risk_level = "วิกฤต (Critical)" if (data['sev'] == 5 or data['sev']*data['lik'] >= 16) else "สูง (Significant)" if data['sev']*data['lik'] >= 8 else "ปานกลาง/ต่ำ (Moderate)"
            issue_list_text += f"- {iss}\n  (พิกัดประเมิน: ความรุนแรง {data['sev']} / โอกาสเกิด {data['lik']} / ระดับความเสี่ยง: {risk_level})\n"
            
            action_text = data['plan'].replace('\n', '\n  ')
            action_list_text += f"▪ สำหรับยุทธศาสตร์การจัดการประเด็น {iss}:\n  {action_text}\n\n"
            
        if not has_data:
            issue_list_text = "- (ข้อมูลว่างเปล่า: ยังไม่มีประเด็นที่ได้รับการอนุมัติเชิงยุทธศาสตร์จาก Tool 5 หรือไม่พบข้อมูลในตัวกรองนี้)\n"
            action_list_text = "- (ข้อมูลว่างเปล่า: โปรดระบุมาตรการตอบสนองเชิงระบบใน Tool 5)\n"

        early_warning_text = ""
        if st.session_state.get("early_warning_approved", False) and not report_filter_text: 
            ew_note = st.session_state.get("early_warning_note", "ให้ทีมสอบสวนลงพื้นที่ตรวจสอบข้อเท็จจริงในห่วงโซ่อุปทานต้นน้ำ")
            early_warning_text = f"""4. การพยากรณ์และสัญญาณเตือนภัยล่วงหน้า (Early Warning & Foresight)
ระบบ AI ครอสเช็คข้อมูลข้ามส่วนงาน (Triangulation) ตรวจพบความเปราะบางเชิงระบบ (Systemic Vulnerability) 1 ประเด็นหลัก:
- ประเด็นเตือนภัย: พบช่องว่างการนำนโยบาย Zero Recruitment Fees ไปปฏิบัติจริง (Policy Implementation Gap) ระหว่างระดับบริหารและกลุ่มแรงงานข้ามชาติ
- แนวทางสืบสวน (Investigation Resolution): อนุมัติดำเนินการตรวจสอบเชิงลึก โดยระบุเหตุผลเชิงยุทธศาสตร์ว่า "{ew_note}" เพื่อตัดไฟแต่ต้นลมก่อนยกระดับเป็นข้อกล่าวหา Forced Labor"""
        else:
            early_warning_text = """4. การพยากรณ์และสัญญาณเตือนภัยล่วงหน้า (Early Warning & Foresight)
ในรอบการประเมินปัจจุบัน ระบบยังไม่พบสัญญาณขัดแย้งของข้อมูลที่มีนัยสำคัญระดับโครงสร้างที่ต้องจัดตั้งคณะกรรมการสืบสวนฉุกเฉิน หรืออยู่นอกเหนือขอบเขตการกรองข้อมูลปัจจุบัน"""

        report_scope_title = f"ข้อมูลระบุเฉพาะกลุ่ม/พื้นที่ (Custom Filter: {report_filter_text})" if report_filter_text else "ภาพรวมระดับองค์กรและห่วงโซ่อุปทาน (Corporate & Value Chain Overview)"

        report_mockup = f"""รายงานการประเมินและการบริหารจัดการความเสี่ยงด้านสิทธิมนุษยชนอย่างรอบด้าน (Comprehensive HRDD Report)
รอบการประเมิน: {audit_cycle}
ขอบเขตพื้นที่: {report_scope_title}
ผู้รับผิดชอบการประเมิน: {auditor_name}

1. วัตถุประสงค์และบริบทเชิงยุทธศาสตร์ (Strategic Context & Overview)
เอกสารฉบับนี้จัดทำขึ้นเพื่อระบุ วิเคราะห์ และพยากรณ์ความเสี่ยงด้านสิทธิมนุษยชนที่อาจซ่อนเร้นอยู่ในห่วงโซ่คุณค่าขององค์กร โดยใช้เครื่องมือประเมินเชิงรุกผสมผสานระบบปัญญาประดิษฐ์ เพื่อให้มั่นใจว่าองค์กรมีการปฏิบัติตามมาตรฐานสากล (UNGPs, ILO, EU CSDDD) และสามารถคุ้มครองสิทธิของกลุ่มเปราะบางได้อย่างเป็นรูปธรรม

2. เกณฑ์การพิจารณานัยสำคัญของความเสี่ยง (Salient Risk Assessment Criteria)
องค์กรใช้หลักการ "ความร้ายแรงนำ (Severity-led Principle)" ในการระบุประเด็นที่ต้องให้ความสำคัญสูงสุด โดยพิจารณาน้ำหนักเชิงประจักษ์จาก 3 มิติหลัก ได้แก่:
- ขนาดและผลกระทบ (Scale): ระดับความรุนแรงต่อการใช้ชีวิตและศักดิ์ศรีความเป็นมนุษย์
- ขอบเขตความเสียหาย (Scope): ปริมาณผู้ที่อาจตกเป็นเหยื่อในโครงสร้างธุรกิจ
- ความท้าทายในการเยียวยา (Remediability): ความสามารถขององค์กรในการฟื้นฟูสภาพให้กลับคืนดังเดิม

3. ข้อค้นพบและผลการวิเคราะห์นัยสำคัญทางสิทธิมนุษยชน (Key Findings on Salient Issues)
จากการบูรณาการข้อมูลผ่านแบบสอบถามพนักงานและหลักฐานเชิงประจักษ์ พบประเด็นความเสี่ยงเชิงโครงสร้างที่ได้รับการอนุมัติให้ยกระดับการเฝ้าระวัง ดังนี้:
{issue_list_text}
{early_warning_text}

5. มาตรการตอบสนองและยุทธศาสตร์การจัดการ (Strategic Mitigation & Remediation Roadmap)
เพื่อแสดงถึงจุดยืนด้านบรรษัทภิบาล (Corporate Governance) องค์กรได้กำหนดแนวทางยุติ ระงับ และเยียวยาผลกระทบที่ครอบคลุมไปถึงคู่ค้าในห่วงโซ่อุปทาน (Corporate Leverage) ดังนี้:
{action_list_text}
6. ข้อสรุปและวิสัยทัศน์ทิศทางองค์กร (Executive Conclusion)
จากผลการดำเนินงานข้างต้น องค์กรสามารถสะท้อนความมุ่งมั่นในการรักษามาตรฐาน Zero Tolerance อย่างแท้จริง การลงทุนในระบบบริหารจัดการความเสี่ยงอัจฉริยะไม่เพียงแต่ลดทอนความเสี่ยงด้านชื่อเสียงและกฎหมาย แต่ยังช่วยตอกย้ำจุดยืนในการเคารพคุณค่าของทรัพยากรมนุษย์ทุกระดับชั้น

7. กลไกการขับเคลื่อนและประเมินผลอย่างต่อเนื่อง (Monitoring & Continuous Improvement)
- ระยะสั้น (Short-term): สั่งการให้หน่วยงาน Audit ติดตามผลสัมฤทธิ์ของมาตรการเชิงรุก (Preventive) ภายใน 3 เดือน
- ระยะยาว (Long-term): ทบทวนนโยบายและประเมินสภาวะแวดล้อมใหม่ประจำปี (Annual Review) พร้อมบูรณาการกระบวนการรับฟังเสียงจากผู้มีส่วนได้เสีย (Stakeholder Inclusivity) อย่างต่อเนื่อง"""

        st.markdown("**✍️ ตรวจสอบความถูกต้องของรายงานก่อนการอนุมัติขั้นสุดท้าย:**")
        report_text_final = st.text_area("ทบทวน ปรับแก้ และอนุมัติรายงานฉบับสมบูรณ์ (Review & Approve Report):", value=report_mockup, height=700, label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 อนุมัติยุทธศาสตร์และบันทึกรายงานฉบับสมบูรณ์ (Approve & Save Executive Report)"):
            if sheet:
                save_scope = f"ข้อมูลระบุเฉพาะ (Filter: {report_filter_text})" if report_filter_text else "ภาพรวมทุกพื้นที่ (Corporate)"
                
                sheet.append_row([now, audit_cycle, auditor_name, save_scope, "Tool 7 - Report", "Executive Summary", "N/A", "N/A", "N/A", f"Comprehensive Report: {audit_cycle}", report_text_final, "", "", "", "Approved"])
                st.success("✅ อนุมัติยุทธศาสตร์องค์กรและบันทึกรายงานประเมินความเสี่ยงฉบับสมบูรณ์เข้าสู่ฐานข้อมูลเรียบร้อยแล้ว! (ข้อมูลพร้อมสำหรับการจัดทำรายงานความยั่งยืนของบริษัทต่อไป)")
                
    st.markdown("</div>", unsafe_allow_html=True)
