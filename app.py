import streamlit as st
import pandas as pd
from google.oauth2 import service_account
import gspread
from datetime import datetime, timedelta

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

    .salient-badge { background-color: #FEF2F2; color: #DC2626; padding: 15px; border-radius: 12px; border: 1px solid #FECACA; font-weight: 700; text-align: center; display: block; margin-top: 15px;}
    .gemini-draft-box { background: linear-gradient(135deg, #F0F4FF 0%, #FFFFFF 100%); border-left: 6px solid #4285F4; padding: 20px; border-radius: 10px; margin-top: 20px; border: 1px solid #D2E3FC; box-shadow: 0 4px 15px rgba(66, 133, 244, 0.05);}
    .gemini-title { color: #1967D2; font-family: 'Poppins', sans-serif; font-weight: 700; margin-top: 0; font-size: 16px; display: flex; align-items: center; gap: 8px;}
    
    .heat-table { width: 100%; border-collapse: separate; border-spacing: 4px; margin-top: 15px;}
    .heat-cell { height: 60px; text-align: center; font-weight: bold; color: white; border-radius: 8px; font-size: 18px; transition: 0.3s; position: relative;}
    .matrix-bubble { width: 34px; height: 34px; background: #FFFFFF; border-radius: 50%; color: #333; display: flex; align-items: center; justify-content: center; margin: 0 auto; font-weight: 800; cursor: pointer; box-shadow: 0 4px 10px rgba(0,0,0,0.3); font-size: 16px;}
    .matrix-bubble:hover { transform: scale(1.2); }
    
    .dash-card { background: #FFFFFF; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #EAEAEA; text-align: center; }
    .dash-number { font-size: 36px; font-family: 'Poppins', sans-serif; font-weight: 800; color: #005B31; line-height: 1; margin: 10px 0; }
    .dash-label { font-size: 14px; color: #666; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }

    /* Radar Animation CSS for Tool 6 */
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
# --- 3.1 SECURITY ACCESS GATE ---
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
with col_r1: resp_id = st.text_input("รหัสอ้างอิง (ID)", placeholder="เช่น EMP-001 (สำหรับ Tool 1-4)")
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
    "Tool 5: ประเมินนัยสำคัญ (Salient Risk & AI Mitigation Plan)",
    "Tool 6: ระบบเตือนภัยล่วงหน้า (AI Triangulation & Early Warning)",
    "Tool 7: แดชบอร์ดสรุปผลภาพรวม (Executive Dashboard)"
], label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

if not auditor_name or not location:
    st.info("📌 กรุณาระบุข้อมูล **ชื่อผู้บันทึก** และ **พื้นที่สำรวจ** ให้ครบถ้วน เพื่อเริ่มใช้งานระบบ")
    st.stop()

# อัปเดตเวลาให้ตรงกับประเทศไทย (UTC+7)
now = (datetime.utcnow() + timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")

# ==========================================
# --- 5. TOOLS LOGIC ---
# ==========================================

# ----------------- TOOL 1 -----------------
if choice == "Tool 1: ประเมินสถานะองค์กร (Governance & Policy Gap)":
    if not resp_id: st.warning("กรุณากรอกรหัสอ้างอิง ID ด้านบนสำหรับ Tool 1-4"); st.stop()
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
            sheet = connect_to_sheet()
            if sheet:
                detail = f"A({q1_1},{q1_2},{q1_3})|B({q2_1},{q2_2})|C({q3_1},{q3_2})"
                sheet.append_row([now, audit_cycle, auditor_name, location, "Tool 1", resp_id, resp_group, resp_dept, resp_gender, "Policy Gap Analysis", detail, "", "", "", ""])
                st.success("✅ บันทึกข้อมูล Tool 1 เรียบร้อย")

# ----------------- TOOL 2 -----------------
elif choice == "Tool 2: แบบสอบถามหน้างาน (Worker Survey)":
    if not resp_id: st.warning("กรุณากรอกรหัสอ้างอิง ID ด้านบนสำหรับ Tool 1-4"); st.stop()
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
            sheet = connect_to_sheet()
            if sheet:
                detail = f"จ้างงาน({s1_1},{s1_2},{s1_3}) | OHS({s2_1},{s2_2},{s2_3}) | ปฏิบัติ({s3_1},{s3_2})"
                sheet.append_row([now, audit_cycle, auditor_name, location, "Tool 2", resp_id, resp_group, resp_dept, resp_gender, "Worker Survey", detail, "", "", "", ""])
                st.success("✅ ส่งข้อมูลแบบสอบถามสำเร็จ")

# ----------------- TOOL 3 -----------------
elif choice == "Tool 3: สัมภาษณ์เชิงลึก (Evidence Base)":
    if not resp_id: st.warning("กรุณากรอกรหัสอ้างอิง ID ด้านบนสำหรับ Tool 1-4"); st.stop()
    with st.form("form_t3"):
        st.markdown("<h3 style='color:#005B31;'>Tool 3: สัมภาษณ์เชิงลึก</h3><hr>", unsafe_allow_html=True)
        st.markdown("**🔍 หัวข้อการตรวจสอบ (เลือกข้อที่พบประเด็นความเสี่ยง)**")
        topics = st.multiselect("ประเด็นที่พูดคุย:", ["การสรรหา/ค่านายหน้า (Recruitment Fees)", "ความเข้าใจในสัญญาจ้าง", "สภาพที่พักอาศัย/โรงอาหาร", "กลไกการร้องเรียน", "การเลือกปฏิบัติ"], label_visibility="collapsed")
        
        st.markdown("<br>**✍️ บันทึกคำให้การ (Testimony)**", unsafe_allow_html=True)
        testimony = st.text_area("สรุปคำพูดหรือหลักฐานที่พบ:", height=150)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("💾 บันทึกข้อมูล Tool 3"):
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([now, audit_cycle, auditor_name, location, "Tool 3", resp_id, resp_group, resp_dept, resp_gender, ", ".join(topics), testimony, "", "", "", ""])
                st.success("✅ บันทึกหลักฐานสำเร็จ")

# ----------------- TOOL 4 -----------------
elif choice == "Tool 4: บันทึกการสังเกตการณ์ (Site Observation Log)":
    if not resp_id: st.warning("กรุณากรอกรหัสอ้างอิง ID ด้านบนสำหรับ Tool 1-4"); st.stop()
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
            sheet = connect_to_sheet()
            if sheet:
                res_o1 = f"{o1.split(' ')[1]} ({note_o1})" if note_o1 else o1.split(" ")[1]
                res_o2 = f"{o2.split(' ')[1]} ({note_o2})" if note_o2 else o2.split(" ")[1]
                res_o3 = f"{o3.split(' ')[1]} ({note_o3})" if note_o3 else o3.split(" ")[1]
                res_o4 = f"{o4.split(' ')[1]} ({note_o4})" if note_o4 else o4.split(" ")[1]
                res_o5 = f"{o5.split(' ')[1]} ({note_o5})" if note_o5 else o5.split(" ")[1]
                
                detail = f"Policy: {res_o1} | Fire: {res_o2} | PPE: {res_o3} | Env: {res_o4} | Med: {res_o5}"
                sheet.append_row([now, audit_cycle, auditor_name, location, "Tool 4", resp_id, resp_group, resp_dept, resp_gender, "Site Observation", detail, "", "", "", ""])
                st.success("✅ บันทึกการสังเกตการณ์สำเร็จ")

# ----------------- TOOL 5 (อัปเดตระบบ Overwrite ใน Google Sheet) -----------------
elif choice == "Tool 5: ประเมินนัยสำคัญ (Salient Risk & AI Mitigation Plan)":

    st.markdown("<div class='standalone-form'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#005B31; margin-top:0;'>Tool 5: HR Risk Matrix (Issue-Based)</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: #F8FAFB; padding: 20px; border-radius: 8px; border: 1px solid #EAEAEA; margin-bottom: 20px;">
        <h5 style="color:#005B31; margin-top:0;">💡 เกณฑ์การประเมินนัยสำคัญ (Risk Criteria):</h5>
        <ul style="font-size: 14px; color: #444; margin-bottom: 0;">
            <li><span style="color:#DC2626; font-weight:700;">🔴 วิกฤต (Critical/Salient):</span> คะแนน 16-25 <b>หรือ ความรุนแรงระดับ 5</b> (AI บังคับร่างแผนกลยุทธ์ทันที)</li>
            <li><span style="color:#D97706; font-weight:700;">🟡 สูง (Significant):</span> คะแนน 8-15 (ต้องเฝ้าระวังและแก้ไข)</li>
            <li><span style="color:#059669; font-weight:700;">🟢 ปานกลาง/ต่ำ (Moderate/Minor):</span> คะแนน 1-7 (ยอมรับได้ / บริหารจัดการตามปกติ)</li>
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

    st.markdown("<hr style='border: 1px dashed #ccc;'>", unsafe_allow_html=True)
    st.markdown("<h5 style='color: #005B31;'><i class='fa-solid fa-sliders'></i> 2. ประเมินระดับความรุนแรง (Severity) และ โอกาสเกิด (Likelihood)</h5>", unsafe_allow_html=True)
    
    def_scale, def_scope, def_remedy, def_lik = 1, 1, 1, 1
    if "โอที" in selected_issue: def_scale, def_scope, def_remedy, def_lik = 3, 4, 2, 4
    elif "พาสปอร์ต" in selected_issue: def_scale, def_scope, def_remedy, def_lik = 5, 2, 3, 3 # Severity = 5
    elif "เครื่องจักร" in selected_issue: def_scale, def_scope, def_remedy, def_lik = 4, 2, 2, 4
    elif "เด็ก" in selected_issue: def_scale, def_scope, def_remedy, def_lik = 5, 1, 4, 1 # Severity = 5, Likelihood = 1

    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1: scale = st.slider("Scale (ความรุนแรง)", 1, 5, def_scale)
    with col_s2: scope = st.slider("Scope (จำนวนผู้ได้รับผลกระทบ)", 1, 5, def_scope)
    with col_s3: remedy = st.slider("Remediability (ความยากในการเยียวยา)", 1, 5, def_remedy)
    
    sev_max = max(scale, scope, remedy)
    likelihood = st.slider("📌 Likelihood (โอกาสที่จะเกิด)", 1, 5, def_lik)
    score = sev_max * likelihood

    is_salient = "YES" if (score >= 16 or sev_max == 5) else "NO"
    
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
    
    plan_text = ""
    if is_salient == "YES":
        st.markdown('<div class="salient-badge">🚨 SALIENT RISK: ประเด็นนี้มีความเสี่ยงระดับวิกฤต (AI กำลังร่างแผนกลยุทธ์)</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="gemini-draft-box">
            <h4 class="gemini-title"><span class="gemini-icon">✨</span> Gemini AI: Draft Mitigation Plan</h4>
            <p style="font-size: 14px; color: #666; margin-bottom: 15px;">คุณสามารถปรับแก้แผนปฏิบัติการด้านล่างก่อนกด "อนุมัติ"</p>
        </div>
        """, unsafe_allow_html=True)
        
        ai_draft = ""
        if "โอที" in selected_issue: ai_draft = "Preventive: ตรวจสอบระบบ Time Attendance และ Pay slip\nRemediation: จ่ายค่าจ้าง/OT ค้างชำระย้อนหลังพร้อมดอกเบี้ยในงวดถัดไป"
        elif "พาสปอร์ต" in selected_issue: ai_draft = "Preventive: สื่อสารนโยบาย EPP ให้เอเจนซี่ และทำตู้ล็อกเกอร์ให้แรงงาน\nRemediation: คืนพาสปอร์ตให้พนักงานทันที (ภายใน 24 ชม.)"
        elif "เครื่องจักร" in selected_issue: ai_draft = "Preventive: กำหนดรอบตรวจสอบความปลอดภัย (Safety Patrol) ประจำสัปดาห์\nRemediation: หยุดการทำงานจุดเสี่ยง แจก PPE ใหม่"
        elif "เด็ก" in selected_issue: ai_draft = "Preventive: ตรวจสอบบัตร ปชช. ต้นทางร่วมกับ Supplier อย่างเข้มงวด\nRemediation: โยกย้ายพนักงานอายุต่ำกว่า 18 ปีออกจากงานอันตรายทันที"
        else: ai_draft = "[พิมพ์แผนบรรเทาผลกระทบและการเยียวยาที่นี่...]"

        plan_text = st.text_area("กล่องข้อความปรับแก้ (Edit & Approve):", value=ai_draft, height=100, label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    save_issue = selected_issue if selected_issue and "เลือกประเด็น" not in selected_issue else "ประเด็นที่ระบุเอง (Manual)"
    
    # 🌟 ปุ่ม Save (ระบบจะเช็คและเขียนทับใน Google Sheet โดยอัตโนมัติ)
    if st.button("💾 อนุมัติและบันทึกข้อมูล (Approve & Update Database)"):
        sheet = connect_to_sheet()
        if sheet:
            detail = f"Scale:{scale}, Scope:{scope}, Remedy:{remedy} | Plan: {plan_text}"
            new_row_data = [now, audit_cycle, auditor_name, location, "Tool 5", "Issue-Based", resp_group, resp_dept, "N/A", save_issue, detail, sev_max, likelihood, score, is_salient]
            
            # --- ระบบเขียนทับข้อมูลเดิม (UPSERT Logic) ---
            with st.spinner("กำลังซิงค์ข้อมูลกับฐานข้อมูล..."):
                all_records = sheet.get_all_values()
                row_to_update = -1
                
                # ค้นหาว่ามีประเด็นนี้ ในพื้นที่นี้ รอบประเมินนี้ หรือยัง (ค้นจากล่างขึ้นบน จะได้เจอล่าสุด)
                for i in range(len(all_records)-1, -1, -1):
                    row = all_records[i]
                    # เช็คคอลัมน์: [1]Audit Cycle, [3]Location, [4]Tool, [9]Issue
                    if len(row) >= 10 and row[1] == audit_cycle and row[3] == location and row[4] == "Tool 5" and row[9] == save_issue:
                        row_to_update = i + 1  # Index ของ Google Sheet เริ่มที่ 1
                        break
                
                if row_to_update != -1:
                    # ถ้าเจอของเดิม ให้อัปเดตทับบรรทัดนั้นเลย (ป้องกันข้อมูลซ้ำซ้อน)
                    try:
                        sheet.update(f"A{row_to_update}:O{row_to_update}", [new_row_data])
                        st.success(f"🔄 **อัปเดตข้อมูลสำเร็จ:** ทับข้อมูลเดิมของประเด็น '{save_issue}' เรียบร้อยแล้ว (ไม่เกิดบรรทัดซ้ำในระบบ)")
                    except TypeError:
                        # รองรับ gspread version ใหม่
                        sheet.update(values=[new_row_data], range_name=f"A{row_to_update}:O{row_to_update}")
                        st.success(f"🔄 **อัปเดตข้อมูลสำเร็จ:** ทับข้อมูลเดิมของประเด็น '{save_issue}' เรียบร้อยแล้ว")
                else:
                    # ถ้ายังไม่เคยมี ให้เพิ่มบรรทัดใหม่
                    sheet.append_row(new_row_data)
                    st.success(f"✅ **อนุมัติและบันทึกใหม่สำเร็จ:** เพิ่มประเด็น '{save_issue}' เข้าสู่ระบบเรียบร้อยแล้ว")
            
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- TOOL 6 (อัปเดต UI และ Human Approval) -----------------
elif choice == "Tool 6: ระบบเตือนภัยล่วงหน้า (AI Triangulation & Early Warning)":
    st.markdown("<div class='standalone-form'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#005B31; margin-top:0;'>Tool 6: AI Early Warning Radar</h3><p style='color:#666;'>ระบบครอสเช็คข้ามเครื่องมือแบบอัตโนมัติ พร้อมส่วนการพิจารณาโดยมนุษย์ (Human Validation)</p><hr>", unsafe_allow_html=True)
    
    # 🌟 หน้าปัดเรดาร์สแกนหาปัญหาอัตโนมัติ
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <div class="radar-pulse">
            <div class="radar-core"></div>
        </div>
        <span style="color: #DC2626; font-weight: 700; font-size: 18px;">System Auto-Scanning... Found 1 Anomaly!</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("#### 🚩 สัญญาณเตือน: การเรียกเก็บค่าธรรมเนียมสรรหา (Recruitment Fee)")
    st.info("🤖 **Gemini AI Triangulation:** ระบบตรวจพบข้อมูลที่ขัดแย้งกัน (Contradiction) ระหว่าง 'นโยบายฝ่ายบริหาร' และ 'คำให้การพนักงาน'")
    
    # 🌟 ใช้ Streamlit UI แทน HTML ดิบ เพื่อป้องกันบั๊กการแสดงผลโค้ด
    c_left, c_right = st.columns(2)
    with c_left:
        st.success("📋 **ข้อมูลนโยบาย (Tool 1)**\n\nฝ่ายบริหารยืนยันว่า:\n\n*\"บริษัทใช้กลยุทธ์ Zero Recruitment Fees และออกค่าใช้จ่ายในการเดินทางให้พนักงานทั้งหมดโดยเด็ดขาด\"*")
    with c_right:
        st.error("🗣️ **ข้อมูลปฏิบัติจริง (Tool 3: EMP-012, 018)**\n\nคำให้การพนักงาน:\n\n*\"พวกเราต้องจ่ายเงินให้เอเจนซี่ฝั่งพม่าไปคนละ 15,000 บาท ก่อนที่จะเข้ามาทำงานในโรงงาน...\"*")

    st.markdown("""
    <div class="gemini-draft-box" style="margin-top: 20px;">
        <h5 class="gemini-title"><span class="gemini-icon">✨</span> Gemini AI Suggestion (คำแนะนำเชิงป้องกัน):</h5>
        <p style="font-size: 14px; color: #444; margin-top: 5px;">มีความเสี่ยงสูงด้าน <b>Debt Bondage (ภาระหนี้ผูกพัน)</b> แนะนำให้ทีม Audit สุ่มสัมภาษณ์กลุ่มแรงงานข้ามชาติจากเอเจนซี่ต้นทางเพิ่มเติมโดยด่วน เพื่อตรวจสอบเส้นทางการเงิน (Traceability)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 🌟 ส่วนการพิจารณาโดยมนุษย์ (Human Validation)
    st.markdown("<hr style='border: 1px dashed #ccc; margin: 30px 0;'>", unsafe_allow_html=True)
    st.markdown("#### ✍️ ส่วนพิจารณาโดยผู้เชี่ยวชาญ (Human Validation)")
    
    t6_decision = st.radio("คุณเห็นด้วยกับการเตือนภัยของ AI หรือไม่? *", 
                           ["✔️ ยืนยันความเสี่ยง (Approve & Flag for Investigation)", 
                            "❌ ปฏิเสธ (Reject - False Alarm)"], 
                           horizontal=True)
    
    t6_note = st.text_input("บันทึกความเห็นเพิ่มเติม (เหตุผลที่อนุมัติ/ปฏิเสธ):", placeholder="พิมพ์บันทึกการพิจารณาของคุณที่นี่...")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 บันทึกผลการพิจารณา Tool 6"):
        sheet = connect_to_sheet()
        if sheet:
            decision_text = "Approved" if "ยืนยัน" in t6_decision else "Rejected"
            detail = f"Anomaly: Recruitment Fee | Decision: {decision_text} | Note: {t6_note}"
            sheet.append_row([now, audit_cycle, auditor_name, location, "Tool 6", "Issue-Based", "N/A", "N/A", "N/A", "Early Warning (Recruitment Fee)", detail, "", "", "", ""])
            st.success("✅ บันทึกผลการพิจารณาสัญญาณเตือนภัยเข้าสู่ฐานข้อมูลเรียบร้อย")
            
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- TOOL 7 (Executive Dashboard) -----------------
elif choice == "Tool 7: แดชบอร์ดสรุปผลภาพรวม (Executive Dashboard)":
    st.markdown("<div class='standalone-form'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#005B31; margin-top:0;'>Tool 7: Executive Dashboard</h3><p style='color:#666;'>สรุปภาพรวมและกระจายตัวของความเสี่ยงทั้งหมดบน Risk Matrix</p><hr>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("<div class='dash-card'><div class='dash-label'>สำรวจทั้งหมด</div><div class='dash-number'>135</div><div style='color: #005B31; font-size:12px;'>ตัวอย่างพนักงาน</div></div>", unsafe_allow_html=True)
    with c2: st.markdown("<div class='dash-card'><div class='dash-label'>Salient Issues</div><div class='dash-number' style='color:#DC2626;'>4</div><div style='color: #666; font-size:12px;'>ประเด็นระดับวิกฤต</div></div>", unsafe_allow_html=True)
    with c3: st.markdown("<div class='dash-card'><div class='dash-label'>Early Warnings</div><div class='dash-number' style='color:#D97706;'>2</div><div style='color: #666; font-size:12px;'>จุดขัดแย้งข้อมูล</div></div>", unsafe_allow_html=True)
    
    st.markdown("<br><h5 style='color: #005B31; text-align:center;'>📊 แผนผังกระจายตัวความเสี่ยง (Interactive Dashboard Matrix)</h5>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#666; font-size:14px; margin-bottom: 20px;'>👉 เอาเมาส์ชี้ที่วงกลม (Bubble) เพื่อดูรายชื่อประเด็นความเสี่ยงที่ตกอยู่ในจุดนั้น</p>", unsafe_allow_html=True)
    
    matrix_data = {(s, l): [] for s in range(1,6) for l in range(1,6)}
    matrix_data[(4, 4)].append("[แรงงาน] การจ่ายเงินล่าช้า / ไม่จ่ายโอที")
    matrix_data[(4, 4)].append("[อาชีวอนามัย] ขาดอุปกรณ์ PPE")
    matrix_data[(5, 3)].append("[แรงงานบังคับ] การยึดพาสปอร์ต")
    matrix_data[(5, 1)].append("[แรงงานเด็ก] จ้างแรงงานอายุต่ำกว่า 18 ปี")
    matrix_data[(3, 4)].append("[อาชีวอนามัย] สภาพแวดล้อมอันตราย (โซน B)")
    matrix_data[(2, 2)].append("[แรงงาน] ไม่มีที่พักผ่อนเพียงพอ")
    matrix_data[(4, 2)].append("[การเลือกปฏิบัติ] ความไม่เท่าเทียมด้านค่าจ้าง")
    
    rows = ""
    for l in range(5, 0, -1):
        rows += "<tr>"
        for s in range(1, 6):
            issues = matrix_data[(s, l)]
            color = get_heat_color(s, l)
            content = ""
            if len(issues) > 0:
                issue_text = "&#10;".join([f"- {i}" for i in issues])
                content = f"<div class='matrix-bubble' title='ประเด็นในจุดนี้:&#10;{issue_text}'>{len(issues)}</div>"
            
            rows += f"<td class='heat-cell' style='background-color:{color}; border: 1px solid rgba(0,0,0,0.05);'>{content}</td>"
        rows += "</tr>"
        
    st.markdown(f"""
        <table class='heat-table' style='width: 80%; margin: 0 auto;'>{rows}</table>
        <div style='display: flex; justify-content: space-between; width: 80%; margin: 5px auto 0 auto; color: #666; font-weight: bold; font-size: 12px;'>
            <span>< Likelihood (โอกาสเกิด)</span>
            <span>Severity (ความรุนแรง) ></span>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
