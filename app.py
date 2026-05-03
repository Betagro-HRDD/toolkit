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

# --- ฟังก์ชันตรวจสอบรหัสซ้ำ (Consistency Check) ---
def check_id_conflict(sheet, resp_id, resp_group, resp_dept, resp_gender):
    if not resp_id or resp_id.strip() == "": 
        return False
    all_records = sheet.get_all_values()
    for row in all_records:
        # เช็คคอลัมน์ [5]=ID, [6]=Group, [7]=Dept, [8]=Gender
        if len(row) > 8 and row[5] == resp_id:
            if row[6] != resp_group or row[7] != resp_dept or row[8] != resp_gender:
                return True # ขัดแย้ง! รหัสซ้ำแต่ข้อมูลบุคคลไม่ตรงกัน
    return False # ผ่าน! รหัสใหม่ หรือ รหัสเดิมแต่เป็นคนเดียวกัน

# --- ฟังก์ชันคำนวณสีไล่เฉดสี Heat Map (Gradient) ---
def get_heat_color(s, l):
    val = s * l
    if val >= 16 or s == 5:  # RED ZONE
        if val <= 5: return "#FCA5A5"   # แดงอ่อน
        if val <= 10: return "#F87171"  # แดงกลาง
        if val <= 15: return "#EF4444"  # แดงสด
        if val <= 20: return "#DC2626"  # แดงเข้ม
        return "#991B1B"                # แดงเข้มเดือด
    elif val >= 8:  # YELLOW ZONE
        if val <= 9: return "#FDE047"   # เหลืองสว่าง
        if val <= 12: return "#F59E0B"  # เหลืองทอง
        return "#D97706"                # ทองอร่าม
    else:  # GREEN ZONE
        if val <= 2: return "#A7F3D0"   # เขียวอ่อน
        if val <= 4: return "#34D399"   # เขียวกลาง
        return "#059669"                # เขียวเข้มสุด

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
    
    .premium-banner {
        background: #FFFFFF; border-radius: 24px; padding: 30px 40px;
        box-shadow: 0px 20px 40px rgba(0, 91, 49, 0.05);
        border: 1px solid rgba(0, 91, 49, 0.08); border-left: 12px solid #005B31; 
        display: flex; align-items: center; gap: 30px; margin-bottom: 40px;
        position: relative; overflow: hidden;
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

    .salient-badge { padding: 15px; border-radius: 12px; font-weight: 700; text-align: center; display: block; margin-top: 15px; border: 1px solid transparent;}
    .gemini-draft-box { background: linear-gradient(135deg, #F0F4FF 0%, #FFFFFF 100%); border-left: 6px solid #4285F4; padding: 20px; border-radius: 10px; margin-top: 20px; border: 1px solid #D2E3FC; box-shadow: 0 4px 15px rgba(66, 133, 244, 0.05);}
    .gemini-title { color: #1967D2; font-family: 'Poppins', sans-serif; font-weight: 700; margin-top: 0; font-size: 16px; display: flex; align-items: center; gap: 8px;}
    
    .heat-table { width: 100%; border-collapse: separate; border-spacing: 4px; margin-top: 15px;}
    .heat-cell { height: 60px; text-align: center; font-weight: bold; color: white; border-radius: 8px; font-size: 18px; transition: 0.3s; position: relative;}
    .matrix-bubble { width: 34px; height: 34px; background: #FFFFFF; border-radius: 50%; color: #333; display: flex; align-items: center; justify-content: center; margin: 0 auto; font-weight: 800; cursor: pointer; box-shadow: 0 4px 10px rgba(0,0,0,0.3); font-size: 16px;}
    .matrix-bubble:hover { transform: scale(1.2); }
    
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
    
    .control-panel label { font-size: 14px !important; color: #444 !important; font-weight: 600 !important; }
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

# ประกาศตัวแปรเก็บสถานะ
if "approved_issues" not in st.session_state: st.session_state.approved_issues = []
if "saved_plans_dict" not in st.session_state: st.session_state.saved_plans_dict = {}

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
with col_p1: audit_cycle = st.selectbox("รอบการประเมิน (Audit Cycle) *", ["Annual 2026", "Q1/2026", "Q2/2026", "Q3/2026", "Q4/2026", "Special Audit"])
with col_p2: auditor_name = st.text_input("ชื่อผู้บันทึกข้อมูล (Auditor) *", placeholder="เช่น สมชาย ใจดี")
with col_p3: location = st.text_input("พื้นที่สำรวจ (Location/Site) *", placeholder="เช่น โรงงานลพบุรี")

st.markdown("<hr style='border: 1px dashed #EAEAEA; margin: 20px 0;'>", unsafe_allow_html=True)
st.markdown("<h4 style='color: #005B31; margin-bottom: 15px; font-weight: 700;'><i class='fa-solid fa-users'></i> 2. ข้อมูลผู้ให้ข้อมูล (Respondent Info)</h4>", unsafe_allow_html=True)
col_r1, col_r2, col_r3, col_r4 = st.columns(4)
with col_r1: resp_id = st.text_input("รหัสอ้างอิง (ID)", placeholder="เช่น 001, 002 (สำหรับ Tool 1-4)")
with col_r2: resp_group = st.selectbox("กลุ่มเป้าหมาย", ["ไม่ระบุ/ภาพรวม", "ฝ่ายบริหาร", "แรงงานไทย", "แรงงานข้ามชาติ", "ชุมชน", "คู่ค้า"])
with col_r3: resp_dept = st.text_input("แผนก/ส่วนงาน", placeholder="เช่น ฝ่ายตัดแต่ง")
with col_r4: resp_gender = st.selectbox("เพศ (Gender)", ["ไม่ระบุ", "ชาย", "หญิง", "อื่นๆ"])

st.markdown("<hr style='border: 1px solid #eee; margin: 20px 0;'>", unsafe_allow_html=True)
st.markdown("<h4 style='color: #005B31; margin-bottom: 15px; font-weight: 700;'><i class='fa-solid fa-screwdriver-wrench'></i> 3. เลือกเครื่องมือประเมิน</h4>", unsafe_allow_html=True)
choice = st.selectbox("เลือกแบบฟอร์มด้านล่างนี้:", [
    "Tool 1: ประเมินสถานะองค์กร (Governance & Policy Gap)",
    "Tool 2: แบบสอบถามหน้างาน (Worker Survey)",
    "Tool 3: สัมภาษณ์เชิงลึก (Evidence Base)",
    "Tool 4: บันทึกการสังเกตการณ์ (Site Observation Log)",
    "Tool 5: ประเมินนัยสำคัญของความเสี่ยง (Salient Risk Matrix)",
    "Tool 6: ระบบเตือนภัยล่วงหน้า (AI Triangulation & Early Warning)",
    "Tool 7: แดชบอร์ดและรายงานสรุป (Dashboard & Report)"
], label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

if not auditor_name or not location:
    st.info("📌 กรุณาระบุข้อมูล **ชื่อผู้บันทึก** และ **พื้นที่สำรวจ** ให้ครบถ้วน เพื่อเริ่มใช้งานระบบ")
    st.stop()

# อัปเดตเวลาให้ตรงกับประเทศไทย (UTC+7)
now = (datetime.utcnow() + timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")

# ==========================================
# --- 5. EARLY VALIDATION & ENGINE CONNECTION ---
# ==========================================
# โหลดข้อมูล Google Sheet เพียงครั้งเดียวเพื่อความรวดเร็วและใช้ตรวจรหัสซ้ำ
sheet = connect_to_sheet()

is_tool_1_to_4 = choice.startswith("Tool 1") or choice.startswith("Tool 2") or choice.startswith("Tool 3") or choice.startswith("Tool 4")

if is_tool_1_to_4:
    if not resp_id:
        st.warning("⚠️ กรุณากรอก **รหัสอ้างอิง (ID)** ด้านบนให้เรียบร้อย เพื่อปลดล็อกแบบฟอร์มการประเมิน")
        st.stop()
    elif sheet:
        with st.spinner("กำลังตรวจสอบความถูกต้องของรหัสอ้างอิง..."):
            # 💡 ระบบเช็ครหัสซ้ำทันที (Fail Fast) โดยไม่ต้องรอให้ทำแบบฟอร์มจนเสร็จ!
            if check_id_conflict(sheet, resp_id, resp_group, resp_dept, resp_gender):
                st.error(f"❌ ไม่อนุญาตให้ทำรายการ: รหัสอ้างอิง '{resp_id}' ถูกใช้งานไปแล้วกับบุคคลอื่น!")
                st.info("💡 **สาเหตุ:** กลุ่มเป้าหมาย, แผนก หรือ เพศ ไม่ตรงกับข้อมูลเดิมในฐานข้อมูล\n\n**คำแนะนำ:** กรุณาเปลี่ยนรหัสอ้างอิงใหม่ หรือแก้ไขข้อมูลด้านบนให้ตรงกับบุคคลเดิมก่อน")
                st.stop() # หยุดการทำงานตรงนี้เลย จะไม่แสดงแบบสอบถาม

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
        topics = st.multiselect("ประเด็นที่พูดคุย:", ["การสรรหา/ค่านายหน้า (Recruitment Fees)", "ความเข้าใจในสัญญาจ้าง", "สภาพที่พักอาศัย/โรงอาหาร", "กลไกการร้องเรียน", "การเลือกปฏิบัติ"], label_visibility="collapsed")
        
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

# ----------------- TOOL 5 -----------------
elif choice == "Tool 5: ประเมินนัยสำคัญของความเสี่ยง (Salient Risk Matrix)":

    st.markdown("<div class='standalone-form'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#005B31; margin-top:0;'>Tool 5: ประเมินนัยสำคัญของความเสี่ยง (Issue-Based)</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: #F8FAFB; padding: 20px; border-radius: 8px; border: 1px solid #EAEAEA; margin-bottom: 20px;">
        <h5 style="color:#005B31; margin-top:0;">💡 เกณฑ์การประเมินนัยสำคัญ (Risk Criteria):</h5>
        <ul style="font-size: 14px; color: #444; margin-bottom: 0;">
            <li>ความร้ายแรง (Severity) ใช้ค่าสูงสุดระหว่าง: <b>Scale</b> (ขนาดผลกระทบ), <b>Scope</b> (จำนวนผู้ได้รับผลกระทบ), และ <b>Remedy</b> (ระดับความยากในการเยียวยา)</li>
            <li><span style="color:#DC2626; font-weight:700;">🔴 วิกฤต (Critical/Salient):</span> คะแนน 16-25 <b>หรือ ความรุนแรงระดับ 5 (Zero Tolerance)</b></li>
            <li><span style="color:#D97706; font-weight:700;">🟡 สูง (Significant):</span> คะแนน 8-15 (เฝ้าระวังและจัดทำแผนป้องกัน)</li>
            <li><span style="color:#059669; font-weight:700;">🟢 ปานกลาง/ต่ำ (Moderate/Minor):</span> คะแนน 1-7 (บริหารจัดการและจัดทำแผนคงสภาพ)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<h5 style='color: #005B31; margin-top: 20px;'><i class='fa-solid fa-wand-magic-sparkles'></i> 1. สกัดประเด็นความเสี่ยงจากฐานข้อมูลทั้งหมด</h5>", unsafe_allow_html=True)
    if st.button("✨ ให้ Gemini AI วิเคราะห์ประเด็นจากข้อมูลที่สำรวจได้ (Mock: 135 Records)"):
        st.session_state.ai_scanned_issues = True
    
    selected_issue = ""
    if st.session_state.get("ai_scanned_issues", False):
        st.markdown('<div style="background: #E8F0FE; padding: 15px; border-radius: 8px; border-left: 4px solid #1967D2; margin-bottom: 20px;"><span style="color: #1967D2; font-weight: 700; font-size: 14px;">🤖 Gemini AI พบประเด็นที่ต้องจัดทำแผน:</span></div>', unsafe_allow_html=True)
        selected_issue = st.selectbox("เลือกประเด็นความเสี่ยงเพื่อจัดทำแผน (Process Issue):", [
            "เลือกประเด็นความเสี่ยงเพื่อจัดการ...",
            "[สิทธิแรงงาน] พนักงาน 35% ร้องเรียนเรื่องการจ่ายเงิน OT ไม่ครบ/ล่าช้า",
            "[แรงงานบังคับ] พบกลุ่มแรงงานข้ามชาติ 12 คน ถูกยึดพาสปอร์ตโดยเอเจนซี่",
            "[อาชีวอนามัย] พบเครื่องจักรโซน B ไม่มีฝาครอบป้องกันอันตราย 3 จุด",
            "[การใช้แรงงานเด็ก] พบการจ้างงานผู้ที่อายุต่ำกว่า 18 ปี ในพื้นที่อันตราย"
        ])

    save_issue = selected_issue if selected_issue and "เลือกประเด็น" not in selected_issue else "ประเด็นที่ระบุเอง (Manual)"
    is_already_approved = save_issue in st.session_state.approved_issues

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
    
    st.markdown("""
    <div class="gemini-draft-box">
        <h4 class="gemini-title"><span class="gemini-icon">✨</span> Gemini AI: Draft Mitigation Plan</h4>
        <p style="font-size: 14px; color: #666; margin-bottom: 10px;">โปรดตรวจสอบและปรับแก้แผนปฏิบัติการด้านล่างก่อนอนุมัติ <i>(หากคุณเคยบันทึกประเด็นนี้ไว้แล้ว ระบบจะดึงข้อความแก้ไขล่าสุดของคุณมาแสดงอัตโนมัติ)</i></p>
    </div>
    """, unsafe_allow_html=True)
    
    ai_draft = ""
    if is_already_approved and save_issue in st.session_state.saved_plans_dict:
        ai_draft = st.session_state.saved_plans_dict[save_issue]['plan']
        
    if not ai_draft or ai_draft.strip() == "" or "พิมพ์แผนบรรเทาผลกระทบ" in ai_draft:
        if risk_zone == "GREEN":
            ai_draft = "Maintenance Plan (แผนคงสภาพ):\n- Monitoring: ระดับความเสี่ยงปกติ ให้ทำการตรวจสอบซ้ำและติดตามผลตามวงรอบอย่างน้อยปีละ 1 ครั้ง เพื่อให้มั่นใจว่าคู่ค้ายังรักษามาตรฐานไว้ได้ตลอดไป"
        elif risk_zone == "YELLOW":
            if "OT" in selected_issue or "โอที" in selected_issue or "หักค่าจ้าง" in selected_issue: 
                ai_draft = "Preventive Action (แผนป้องกันเชิงรุก):\n- Proactive Measures: จัดอบรมเรื่องกฎหมายแรงงาน (เวลาทำงาน/ค่าจ้าง) ให้หัวหน้างาน และสุ่มตรวจ Pay slip ทุกไตรมาส\n- Timeline: ติดตามผลการปรับปรุงภายใน 3 เดือน เพื่อดึงระดับความเสี่ยงกลับมาสีเขียว"
            elif "พาสปอร์ต" in selected_issue or "หนี้ผูกพัน" in selected_issue or "บังคับ" in selected_issue: 
                ai_draft = "Preventive Action (แผนป้องกันเชิงรุก):\n- Proactive Measures: ตรวจสอบกระบวนการจ้างงานผ่านเอเจนซี่ และย้ำนโยบาย Employer Pays Principle (EPP)\n- Timeline: ติดตามผลการปรับปรุงภายใน 3 เดือน เพื่อดึงระดับความเสี่ยงกลับมาสีเขียว"
            elif "เครื่องจักร" in selected_issue or "สารเคมี" in selected_issue or "สภาพแวดล้อม" in selected_issue: 
                ai_draft = "Preventive Action (แผนป้องกันเชิงรุก):\n- Proactive Measures: เพิ่มความถี่ในการทำ Safety Patrol และซ่อมบำรุงเครื่องมือ/PPE ให้อยู่ในสภาพพร้อมใช้เสมอ\n- Timeline: ติดตามผลการปรับปรุงภายใน 1-3 เดือน เพื่อดึงระดับความเสี่ยงกลับมาสีเขียว"
            else:
                ai_draft = "Preventive Action (แผนป้องกันเชิงรุก):\n- Proactive Measures: จัดอบรมให้ความรู้เพิ่มเติม ทบทวนขั้นตอนการทำงาน และสื่อสารนโยบายให้แก่ผู้เกี่ยวข้องอย่างเคร่งครัด\n- Timeline: กำหนดระยะเวลาติดตามผลการปรับปรุงภายใน 3-6 เดือน"
        else: # RED
            if "OT" in selected_issue or "โอที" in selected_issue or "หักค่าจ้าง" in selected_issue: 
                ai_draft = "Preventive: ตรวจสอบระบบ Time Attendance และ Pay slip อย่างเข้มงวด\nRemediation: จ่ายค่าจ้าง/OT ค้างชำระย้อนหลังพร้อมดอกเบี้ยในงวดถัดไปทันที"
            elif "พาสปอร์ต" in selected_issue or "หนี้ผูกพัน" in selected_issue or "บังคับ" in selected_issue: 
                ai_draft = "Preventive: สื่อสารนโยบาย EPP ให้เอเจนซี่ และจัดเตรียมตู้ล็อกเกอร์ให้แรงงานเก็บเอกสารเอง\nRemediation: คืนพาสปอร์ตให้พนักงานทุกคนทันที (ภายใน 24 ชม.) และจ่ายคืนค่าธรรมเนียม"
            elif "เครื่องจักร" in selected_issue or "สารเคมี" in selected_issue or "สภาพแวดล้อม" in selected_issue: 
                ai_draft = "Preventive: กำหนดรอบตรวจสอบความปลอดภัย (Safety Patrol) ประจำสัปดาห์อย่างเคร่งครัด\nRemediation: หยุดการทำงานจุดเสี่ยงทันที แจก PPE ใหม่ และรับผิดชอบค่ารักษาพยาบาลหากเกิดเหตุ"
            elif "เด็ก" in selected_issue: 
                ai_draft = "Preventive: ตรวจสอบบัตร ปชช. ต้นทางร่วมกับ Supplier อย่างเข้มงวด (Zero Tolerance)\nRemediation: โยกย้ายพนักงานอายุต่ำกว่า 18 ปีออกจากงานอันตรายทันที พร้อมจ่ายค่าชดเชยตามกฎหมาย"
            elif "เลือกปฏิบัติ" in selected_issue or "คุกคาม" in selected_issue:
                ai_draft = "Preventive: อบรมเรื่องความหลากหลายและการคุกคาม (Harassment Zero Tolerance)\nRemediation: ตั้งกรรมการสอบสวนข้อเท็จจริง และเยียวยาจิตใจ/ชดเชยผู้ถูกกระทำ"
            else: 
                ai_draft = "Preventive: [ระบุมาตรการป้องกันเชิงระบบ]\nRemediation: [ระบุมาตรการเยียวยาผู้ได้รับผลกระทบเร่งด่วน]"

    st.markdown("**✍️ แผนการจัดการความเสี่ยง (Mitigation & Remediation Plan):**")
    plan_text = st.text_area("แผนการจัดการ", value=ai_draft, height=150, label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    
    button_label = "🔄 อัปเดตแผนกลยุทธ์ (Overwrite Data)" if is_already_approved else "💾 อนุมัติและบันทึกประเด็น (Approve & Update Database)"

    if st.button(button_label):
        if sheet:
            db_risk_level = "Salient" if risk_zone == "RED" else ("Significant" if risk_zone == "YELLOW" else "Moderate/Minor")
            detail = f"Scale:{scale}, Scope:{scope}, Remedy:{remedy} | Plan: {plan_text}"
            new_row_data = [now, audit_cycle, auditor_name, location, "Tool 5", "Issue-Based", resp_group, resp_dept, "N/A", save_issue, detail, sev_max, likelihood, score, db_risk_level]
            
            st.session_state.saved_plans_dict[save_issue] = {
                'plan': plan_text, 'sev': sev_max, 'lik': likelihood
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
            sheet.append_row([now, audit_cycle, auditor_name, location, "Tool 6", "Issue-Based", "N/A", "N/A", "N/A", "Early Warning (Recruitment Fee)", detail, "", "", "", ""])
            
            st.session_state.early_warning_approved = True if "ยืนยัน" in t6_decision else False
            st.session_state.early_warning_note = t6_note
            
            st.success("✅ บันทึกมติการพิจารณาสัญญาณเตือนภัยล่วงหน้าเข้าสู่ระบบฐานข้อมูลกลางเรียบร้อย")
            
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- TOOL 7 (Executive Dashboard & AI Report) -----------------
elif choice == "Tool 7: แดชบอร์ดและรายงานสรุป (Dashboard & Report)":
    st.markdown("<div class='standalone-form'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#005B31; margin-top:0;'>Tool 7: Executive Dashboard & Comprehensive Report</h3><p style='color:#666;'>สรุปภาพรวมความเสี่ยงบน Risk Matrix และการจัดทำรายงานระดับบริหาร (Executive Summary)</p><hr>", unsafe_allow_html=True)
    
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
    
    # =========================================================
    # 🌟 UPGRADED SECTION: Profound AI Report Generation
    # =========================================================
    st.markdown("<hr style='border: 2px solid #005B31; margin: 40px 0;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#005B31; margin-top:0;'>📑 ร่างรายงานการบริหารจัดการความเสี่ยง (Comprehensive HRDD Report)</h3>", unsafe_allow_html=True)
    st.info("💡 ระบบปัญญาประดิษฐ์ (AI) จะสังเคราะห์และประมวลผลข้อมูลเชิงลึกทั้งหมดในรอบปี ทั้งประเด็นที่มีนัยสำคัญ (Salient) และการพยากรณ์ความเสี่ยงล่วงหน้า (Foresight) เพื่อจัดทำร่างยุทธศาสตร์ให้ผู้บริหารพิจารณา")

    if st.button("✨ ให้ Gemini AI วิเคราะห์เชิงลึกและร่างรายงานฉบับสมบูรณ์ (Generate Comprehensive Report)"):
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
        
        if len(saved_dict) > 0:
            for iss, data in saved_dict.items():
                risk_level = "วิกฤต (Critical)" if (data['sev'] == 5 or data['sev']*data['lik'] >= 16) else "สูง (Significant)" if data['sev']*data['lik'] >= 8 else "ปานกลาง/ต่ำ (Moderate)"
                issue_list_text += f"- {iss}\n  (พิกัดประเมิน: ความรุนแรง {data['sev']} / โอกาสเกิด {data['lik']} / ระดับความเสี่ยง: {risk_level})\n"
                
                action_text = data['plan'].replace('\n', '\n  ')
                action_list_text += f"▪ สำหรับยุทธศาสตร์การจัดการประเด็น {iss}:\n  {action_text}\n\n"
        else:
            issue_list_text = "- (ข้อมูลว่างเปล่า: ยังไม่มีประเด็นที่ได้รับการอนุมัติเชิงยุทธศาสตร์จาก Tool 5)\n"
            action_list_text = "- (ข้อมูลว่างเปล่า: โปรดระบุมาตรการตอบสนองเชิงระบบใน Tool 5)\n"

        early_warning_text = ""
        if st.session_state.get("early_warning_approved", False):
            ew_note = st.session_state.get("early_warning_note", "ให้ทีมสอบสวนลงพื้นที่ตรวจสอบข้อเท็จจริงในห่วงโซ่อุปทานต้นน้ำ")
            early_warning_text = f"""4. การพยากรณ์และสัญญาณเตือนภัยล่วงหน้า (Early Warning & Foresight)
ระบบ AI ครอสเช็คข้อมูลข้ามส่วนงาน (Triangulation) ตรวจพบความเปราะบางเชิงระบบ (Systemic Vulnerability) 1 ประเด็นหลัก:
- ประเด็นเตือนภัย: พบช่องว่างการนำนโยบาย Zero Recruitment Fees ไปปฏิบัติจริง (Policy Implementation Gap) ระหว่างระดับบริหารและกลุ่มแรงงานข้ามชาติ
- แนวทางสืบสวน (Investigation Resolution): อนุมัติดำเนินการตรวจสอบเชิงลึก โดยระบุเหตุผลเชิงยุทธศาสตร์ว่า "{ew_note}" เพื่อตัดไฟแต่ต้นลมก่อนยกระดับเป็นข้อกล่าวหา Forced Labor"""
        else:
            early_warning_text = """4. การพยากรณ์และสัญญาณเตือนภัยล่วงหน้า (Early Warning & Foresight)
ในรอบการประเมินปัจจุบัน ระบบยังไม่พบสัญญาณขัดแย้งของข้อมูลที่มีนัยสำคัญระดับโครงสร้างที่ต้องจัดตั้งคณะกรรมการสืบสวนฉุกเฉิน"""

        report_mockup = f"""รายงานการประเมินและการบริหารจัดการความเสี่ยงด้านสิทธิมนุษยชนอย่างรอบด้าน (Comprehensive HRDD Report)
รอบการประเมิน: {audit_cycle}
ขอบเขตพื้นที่: ภาพรวมระดับองค์กรและห่วงโซ่อุปทาน (Corporate & Value Chain Overview)
ผู้รับผิดชอบการประเมิน: {auditor_name}

1. วัตถุประสงค์และบริบทเชิงยุทธศาสตร์ (Strategic Context & Overview)
เอกสารฉบับนี้จัดทำขึ้นเพื่อระบุ วิเคราะห์ และพยากรณ์ความเสี่ยงด้านสิทธิมนุษยชนที่อาจซ่อนเร้นอยู่ในห่วงโซ่คุณค่าขององค์กร โดยใช้เครื่องมือประเมินเชิงรุกผสมผสานระบบปัญญาประดิษฐ์ เพื่อให้มั่นใจว่าองค์กรมีการปฏิบัติตามมาตรฐานสากล (UNGPs, ILO, EU CSDDD) และสามารถคุ้มครองสิทธิของกลุ่มเปราะบางได้อย่างเป็นรูปธรรม

2. เกณฑ์การพิจารณานัยสำคัญของความเสี่ยง (Salient Risk Assessment Criteria)
องค์กรใช้หลักการ "ความร้ายแรงนำ (Severity-led Principle)" ในการระบุประเด็นที่ต้องให้ความสำคัญสูงสุด โดยพิจารณาน้ำหนักเชิงประจักษ์จาก 3 มิติหลัก ได้แก่:
- ขนาดและผลกระทบ (Scale): ระดับความรุนแรงต่อการใช้ชีวิตและศักดิ์ศรีความเป็นมนุษย์
- ขอบเขตความเสียหาย (Scope): ปริมาณผู้ที่อาจตกเป็นเหยื่อในโครงสร้างธุรกิจ
- ความท้าทายในการเยียวยา (Remediability): ความสามารถขององค์กรในการฟื้นฟูสภาพให้กลับคืนดังเดิม

3. ข้อค้นพบและผลการวิเคราะห์นัยสำคัญทางสิทธิมนุษยชน (Key Findings on Salient Issues)
จากการบูรณาการข้อมูลผ่านแบบสอบถามพนักงานและหลักฐานเชิงประจักษ์ พบประเด็นความเสี่ยงเชิงโครงสร้างที่ได้รับการอนุมัติให้ยกระดับการเฝ้าระวัง จำนวน {len(saved_dict)} ประเด็น ดังนี้:
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
        report_text = st.text_area("ทบทวน ปรับแก้ และอนุมัติรายงานฉบับสมบูรณ์ (Review & Approve Report):", value=report_mockup, height=700, label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 อนุมัติยุทธศาสตร์และบันทึกรายงานฉบับสมบูรณ์ (Approve & Save Executive Report)"):
            if sheet:
                sheet.append_row([now, audit_cycle, auditor_name, "ภาพรวมทุกพื้นที่ (Corporate)", "Tool 7 - Report", "Executive Summary", "N/A", "N/A", "N/A", f"Comprehensive Report: {audit_cycle}", report_text, "", "", "", "Approved"])
                st.success("✅ อนุมัติยุทธศาสตร์องค์กรและบันทึกรายงานประเมินความเสี่ยงฉบับสมบูรณ์เข้าสู่ฐานข้อมูลเรียบร้อยแล้ว! (ข้อมูลพร้อมสำหรับการจัดทำรายงานความยั่งยืนของบริษัทต่อไป)")
                
    st.markdown("</div>", unsafe_allow_html=True)
