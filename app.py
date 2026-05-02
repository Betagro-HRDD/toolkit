import streamlit as st
import pandas as pd
from google.oauth2 import service_account
import gspread
from datetime import datetime
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
    
    .gemini-draft-box { background: linear-gradient(135deg, #F0F4FF 0%, #FFFFFF 100%); border-left: 6px solid #4285F4; padding: 20px; border-radius: 10px; margin-top: 20px; border: 1px solid #D2E3FC; box-shadow: 0 4px 15px rgba(66, 133, 244, 0.05);}
    .gemini-title { color: #1967D2; font-family: 'Poppins', sans-serif; font-weight: 700; margin-top: 0; font-size: 16px; display: flex; align-items: center; gap: 8px;}
    .gemini-icon { font-size: 20px; }

    .citation-box { background-color: #FFFFFF; padding: 25px; border-left: 6px solid #D3A129; border-radius: 12px; margin: 20px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #F3F4F6;}
    
    .heat-table { width: 100%; border-collapse: separate; border-spacing: 4px; margin-top: 15px;}
    .heat-cell { height: 50px; text-align: center; font-weight: bold; color: white; border-radius: 8px; font-size: 14px;}
    
    .control-panel label { font-size: 14px !important; color: #444 !important; font-weight: 600 !important; }
    
    /* Dashboard Cards */
    .dash-card { background: #FFFFFF; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #EAEAEA; text-align: center; }
    .dash-number { font-size: 36px; font-family: 'Poppins', sans-serif; font-weight: 800; color: #005B31; line-height: 1; margin: 10px 0; }
    .dash-label { font-size: 14px; color: #666; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
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
    resp_id = st.text_input("รหัสอ้างอิง (ID)", placeholder="เช่น EMP-001 (สำหรับ Tool 1-4)")
with col_r2:
    resp_group = st.selectbox("กลุ่มเป้าหมาย", ["ไม่ระบุ/ภาพรวม", "ฝ่ายบริหาร", "แรงงานไทย", "แรงงานข้ามชาติ", "ชุมชน", "คู่ค้า"])
with col_r3:
    resp_dept = st.text_input("แผนก/ส่วนงาน", placeholder="เช่น ฝ่ายตัดแต่ง")
with col_r4:
    resp_gender = st.selectbox("เพศ (Gender)", ["ไม่ระบุ", "ชาย", "หญิง", "อื่นๆ"])

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

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("💾 บันทึกข้อมูล Tool 1"):
            sheet = connect_to_sheet()
            if sheet:
                detail = f"A({q1_1},{q1_2})"
                sheet.append_row([now, audit_cycle, auditor_name, location, "Tool 1", resp_id, resp_group, resp_dept, resp_gender, "Policy Gap Analysis", detail, "", "", "", ""])
                st.success("✅ บันทึกข้อมูล Tool 1 เรียบร้อย")

# ----------------- TOOL 2 -----------------
elif choice == "Tool 2: แบบสอบถามหน้างาน (Worker Survey)":
    if not resp_id: st.warning("กรุณากรอกรหัสอ้างอิง ID ด้านบนสำหรับ Tool 1-4"); st.stop()
    with st.form("form_t2"):
        st.markdown("<h3 style='color:#005B31;'>Tool 2: แบบสอบถามการปฏิบัติหน้างาน</h3>", unsafe_allow_html=True)
        st.markdown("**หมวดที่ 1: สภาพการจ้างและค่าจ้าง**")
        s1_1 = st.select_slider("1.1 ท่านได้รับค่าจ้างตรงเวลาและครบถ้วนตามที่ตกลงไว้", options=[1,2,3,4,5], value=3)
        s1_2 = st.select_slider("1.2 ท่านเป็นผู้เก็บเอกสารประจำตัวไว้เอง", options=[1,2,3,4,5], value=3)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("🚀 บันทึกข้อมูล Tool 2"):
            sheet = connect_to_sheet()
            if sheet:
                detail = f"จ้างงาน({s1_1},{s1_2})"
                sheet.append_row([now, audit_cycle, auditor_name, location, "Tool 2", resp_id, resp_group, resp_dept, resp_gender, "Worker Survey", detail, "", "", "", ""])
                st.success("✅ ส่งข้อมูลแบบสอบถามสำเร็จ")

# ----------------- TOOL 3 -----------------
elif choice == "Tool 3: สัมภาษณ์เชิงลึก (Evidence Base)":
    if not resp_id: st.warning("กรุณากรอกรหัสอ้างอิง ID ด้านบนสำหรับ Tool 1-4"); st.stop()
    with st.form("form_t3"):
        st.markdown("<h3 style='color:#005B31;'>Tool 3: สัมภาษณ์เชิงลึก</h3><hr>", unsafe_allow_html=True)
        topics = st.multiselect("ประเด็นที่พูดคุย:", ["การสรรหา/ค่านายหน้า", "ความเข้าใจในสัญญาจ้าง", "สภาพที่พักอาศัย/โรงอาหาร", "กลไกการร้องเรียน", "การเลือกปฏิบัติ"], label_visibility="collapsed")
        testimony = st.text_area("สรุปคำพูดหรือหลักฐานที่พบ:", height=150)
        
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
        o1 = st.radio("1. มีการติดประกาศนโยบายในพื้นที่ที่พนักงานมองเห็นได้ชัดเจน", ["✔️ พบ", "❌ ไม่พบ", "➖ N/A"], horizontal=True)
        note_o1 = st.text_input("บันทึกเพิ่มเติมข้อ 1:", key="n1", label_visibility="collapsed")
        
        o2 = st.radio("2. ทางหนีไฟ อุปกรณ์ดับเพลิง ไม่มีสิ่งกีดขวางและพร้อมใช้งาน", ["✔️ พบ", "❌ ไม่พบ", "➖ N/A"], horizontal=True)
        note_o2 = st.text_input("บันทึกเพิ่มเติมข้อ 2:", key="n2", label_visibility="collapsed")
        
        if st.form_submit_button("💾 บันทึกข้อมูล Tool 4"):
            sheet = connect_to_sheet()
            if sheet:
                detail = f"Policy:{o1}({note_o1}) | Fire:{o2}({note_o2})"
                sheet.append_row([now, audit_cycle, auditor_name, location, "Tool 4", resp_id, resp_group, resp_dept, resp_gender, "Site Observation", detail, "", "", "", ""])
                st.success("✅ บันทึกการสังเกตการณ์สำเร็จ")

# ----------------- TOOL 5 (อัปเดต AI ดึงประเด็น) -----------------
elif choice == "Tool 5: ประเมินนัยสำคัญ (Salient Risk & AI Mitigation Plan)":
    st.markdown("<div class='standalone-form'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#005B31; margin-top:0;'>Tool 5: HR Risk Matrix (Issue-Based)</h3>", unsafe_allow_html=True)
    
    st.info("💡 **ขั้นตอนการทำ Tool 5:** ให้ดึงข้อมูลที่เก็บจาก Tool 1-4 ทั้งหมดมาวิเคราะห์รวมกันเป็น 'ประเด็นความเสี่ยงระดับองค์กร' (ทำทีละ 1 ประเด็น ไม่ใช่ทำรายบุคคล)")
    
    # 🌟 1. ปุ่มให้ AI สรุปประเด็นจากฐานข้อมูล
    st.markdown("<h5 style='color: #005B31; margin-top: 20px;'><i class='fa-solid fa-wand-magic-sparkles'></i> 1. สกัดประเด็นความเสี่ยงจากฐานข้อมูลทั้งหมด</h5>", unsafe_allow_html=True)
    if st.button("✨ ให้ Gemini AI วิเคราะห์ประเด็นจากข้อมูลที่สำรวจได้ (Mock: 135 Records)"):
        st.session_state.ai_scanned_issues = True
    
    # ถ้ากดปุ่ม AI Scan แล้ว ให้โชว์ List ที่ AI ดึงมาให้
    selected_issue = ""
    if st.session_state.get("ai_scanned_issues", False):
        st.markdown("""
        <div style="background: #E8F0FE; padding: 15px; border-radius: 8px; border-left: 4px solid #1967D2; margin-bottom: 20px;">
            <span style="color: #1967D2; font-weight: 700; font-size: 14px;">🤖 Gemini AI พบประเด็นความเสี่ยงที่น่ากังวล จากการประมวลผลข้อมูล 135 รายการ:</span>
        </div>
        """, unsafe_allow_html=True)
        
        # เพิ่มประเด็นให้ครอบคลุมและหลากหลายมากขึ้น
        selected_issue = st.selectbox("เลือกประเด็นความเสี่ยงเพื่อจัดทำแผน (Process Issue):", [
            "เลือกประเด็นความเสี่ยงเพื่อจัดการ...",
            "[สิทธิแรงงาน] พนักงาน 35% ร้องเรียนเรื่องการจ่ายเงิน OT ไม่ครบ/ล่าช้า",
            "[สิทธิแรงงาน] การหักค่าจ้างอย่างไม่เป็นธรรม (เช่น หักค่าอุปกรณ์ทำงาน)",
            "[แรงงานบังคับ] พบกลุ่มแรงงานข้ามชาติ 12 คน ถูกยึดพาสปอร์ตโดยเอเจนซี่",
            "[แรงงานบังคับ] ภาระหนี้ผูกพันจากการเรียกเก็บค่าธรรมเนียมสรรหาเกินจริง",
            "[แรงงานบังคับ] การบังคับทำโอทีโดยขู่เลิกจ้าง หรือจำกัดการเดินทาง",
            "[อาชีวอนามัย] พบเครื่องจักรโซน B ไม่มีฝาครอบป้องกันอันตราย 3 จุด",
            "[อาชีวอนามัย] สภาพแวดล้อมการทำงานมีสารเคมีอันตราย / ขาด PPE",
            "[อาชีวอนามัย] สภาพที่พักอาศัย/โรงอาหารไม่ถูกสุขลักษณะ",
            "[การเลือกปฏิบัติ] ความไม่เท่าเทียมด้านค่าจ้างระหว่างเพศ",
            "[การเลือกปฏิบัติ] การคุกคามทางเพศ / การล่วงละเมิดด้วยวาจาในที่ทำงาน",
            "[เสรีภาพสมาคม] การขัดขวางไม่ให้พนักงานรวมกลุ่มหรือเข้าร่วมสหภาพ",
            "[การใช้แรงงานเด็ก] พบการจ้างงานผู้ที่อายุต่ำกว่า 18 ปี ในงานที่มีความเสี่ยงอันตราย",
            "[ชุมชน] ข้อร้องเรียนจากชุมชนรอบข้างเรื่องน้ำเสียและกลิ่นเหม็น"
        ])

    # 🌟 2. เข้าสู่กระบวนการประเมินคะแนน
    st.markdown("<hr style='border: 1px dashed #ccc;'>", unsafe_allow_html=True)
    st.markdown("<h5 style='color: #005B31;'><i class='fa-solid fa-sliders'></i> 2. ประเมินระดับความรุนแรง (Severity) และ โอกาสเกิด (Likelihood)</h5>", unsafe_allow_html=True)
    
    # ระบบ AI ช่วยตั้งค่า Slider อัตโนมัติตามประเด็นที่เลือก
    def_scale, def_scope, def_remedy, def_lik = 1, 1, 1, 1
    if "โอที" in selected_issue or "หักค่าจ้าง" in selected_issue: def_scale, def_scope, def_remedy, def_lik = 3, 4, 2, 4
    elif "พาสปอร์ต" in selected_issue or "หนี้ผูกพัน" in selected_issue or "บังคับทำโอที" in selected_issue: def_scale, def_scope, def_remedy, def_lik = 5, 3, 3, 3
    elif "เครื่องจักร" in selected_issue or "สารเคมี" in selected_issue: def_scale, def_scope, def_remedy, def_lik = 4, 2, 2, 4
    elif "เด็ก" in selected_issue or "คุกคาม" in selected_issue: def_scale, def_scope, def_remedy, def_lik = 5, 1, 4, 2

    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1: scale = st.slider("Scale (ความรุนแรง)", 1, 5, def_scale)
    with col_s2: scope = st.slider("Scope (จำนวนผู้ได้รับผลกระทบ)", 1, 5, def_scope)
    with col_s3: remedy = st.slider("Remediability (ความยากในการเยียวยา)", 1, 5, def_remedy)
    
    sev_max = max(scale, scope, remedy)
    likelihood = st.slider("📌 Likelihood (โอกาสที่จะเกิด)", 1, 5, def_lik)
    score = sev_max * likelihood

    is_salient = "YES" if sev_max >= 4 else "NO"
    
    # 🌟 3. แสดง Heat Map
    st.markdown(f"<h4 style='color: #005B31; text-align:center; padding: 15px; background: #F4F7F6; border-radius: 8px;'>Severity Max: {sev_max} | โอกาสเกิด: {likelihood} | คะแนนรวม: {score}</h4>", unsafe_allow_html=True)
    rows = ""
    for l in range(5, 0, -1):
        rows += "<tr>"
        for s in range(1, 6):
            val = s * l
            color = "#EF4444" if val >= 16 or s == 5 else ("#F9A818" if val >= 8 else "#005B31")
            mark = "★" if s == sev_max and l == likelihood else ""
            rows += f"<td class='heat-cell' style='background-color:{color}; box-shadow: inset 0 0 10px rgba(0,0,0,0.1);'>{mark}</td>"
        rows += "</tr>"
    st.markdown(f"<table class='heat-table'>{rows}</table><p style='text-align:center; color: #666; margin-top: 10px;'><small>แนวนอน: Severity | แนวตั้ง: Likelihood</small></p>", unsafe_allow_html=True)
    
    # 🌟 4. ร่างแผน AI
    plan_text = ""
    if is_salient == "YES":
        st.markdown('<div class="salient-badge">🚨 SALIENT RISK: ประเด็นนี้มีความเสี่ยงระดับสูง (เข้าสู่กระบวนการอนุมัติแผนกลยุทธ์)</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="gemini-draft-box">
            <h4 class="gemini-title"><span class="gemini-icon">✨</span> Gemini AI: Draft Mitigation & Remediation Plan</h4>
            <p style="font-size: 14px; color: #666; margin-bottom: 15px;">ระบบช่วยร่างแผนปฏิบัติการเชิงกลยุทธ์เบื้องต้น คุณสามารถปรับแก้ก่อนกดบันทึกเพื่อ "อนุมัติ"</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Mock ข้อความ Draft สอดคล้องกับประเด็นใหม่
        ai_draft = ""
        if "โอที" in selected_issue or "หักค่าจ้าง" in selected_issue: ai_draft = "Preventive: ตรวจสอบระบบ Time Attendance และ Pay slip\nRemediation: จ่ายค่าจ้าง/OT ค้างชำระย้อนหลังพร้อมดอกเบี้ยในงวดถัดไป"
        elif "พาสปอร์ต" in selected_issue or "หนี้ผูกพัน" in selected_issue: ai_draft = "Preventive: สื่อสารนโยบาย Employer Pays Principle (EPP) ให้เอเจนซี่ และทำตู้ล็อกเกอร์ให้แรงงาน\nRemediation: คืนพาสปอร์ตให้พนักงานทันที (ภายใน 24 ชม.) และคืนค่าธรรมเนียม"
        elif "เครื่องจักร" in selected_issue or "สารเคมี" in selected_issue: ai_draft = "Preventive: กำหนดรอบตรวจสอบความปลอดภัย (Safety Patrol) ประจำสัปดาห์\nRemediation: หยุดการทำงานจุดเสี่ยง แจก PPE ใหม่ และรับผิดชอบค่ารักษาพยาบาล"
        elif "เด็ก" in selected_issue: ai_draft = "Preventive: ตรวจสอบบัตร ปชช. ต้นทางร่วมกับ Supplier อย่างเข้มงวด\nRemediation: โยกย้ายพนักงานอายุต่ำกว่า 18 ปีออกจากงานอันตรายทันที"
        elif "คุกคาม" in selected_issue or "เลือกปฏิบัติ" in selected_issue: ai_draft = "Preventive: อบรมเรื่องความหลากหลายและการคุกคาม (Harassment Zero Tolerance)\nRemediation: ตั้งกรรมการสอบสวนข้อเท็จจริง และเยียวยาจิตใจผู้ถูกกระทำ"
        elif "ชุมชน" in selected_issue: ai_draft = "Preventive: ตรวจวัดค่าน้ำเสียและกลิ่นรายสัปดาห์\nRemediation: ตั้งทีม CSR รับฟังปัญหาและชดเชยเยียวยาชุมชนที่ได้รับผลกระทบ"
        else: ai_draft = "[พิมพ์แผนบรรเทาผลกระทบและการเยียวยาที่นี่...]"

        plan_text = st.text_area("กล่องข้อความปรับแก้ (Edit & Approve):", value=ai_draft, height=100, label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # ป้องกันการบันทึกถ้ายังไม่ระบุประเด็น
    save_issue = selected_issue if selected_issue and "เลือกประเด็น" not in selected_issue else "ประเด็นที่ระบุเอง (Manual)"
    
    if st.button("💾 อนุมัติและบันทึกข้อมูล (Approve & Submit Issue)"):
        sheet = connect_to_sheet()
        if sheet:
            detail = f"Scale:{scale}, Scope:{scope}, Remedy:{remedy} | Action Plan: {plan_text}"
            sheet.append_row([now, audit_cycle, auditor_name, location, "Tool 5", "Issue-Based", resp_group, resp_dept, "N/A", save_issue, detail, sev_max, likelihood, score, is_salient])
            st.success(f"✅ บันทึกประเด็น {save_issue} และแผนกลยุทธ์เข้าสู่ระบบเรียบร้อยแล้ว (คุณสามารถดึงประเด็นต่อไปมาทำต่อได้เลย)")

# ----------------- TOOL 6 (Early Warning System) -----------------
elif choice == "Tool 6: ระบบเตือนภัยล่วงหน้า (AI Triangulation & Early Warning)":
    st.markdown("<div class='standalone-form'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#005B31; margin-top:0;'>Tool 6: AI Early Warning Radar</h3><p style='color:#666;'>ระบบครอสเช็คความขัดแย้งของข้อมูล เพื่อเตือนภัยก่อนบานปลายเป็น Salient Risk</p><hr>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background-color: #FFFFFF; padding: 25px; border-left: 6px solid #D3A129; border-radius: 12px; margin: 20px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #F3F4F6;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <h4 style="color: #D3A129; margin: 0;"><i class="fa-solid fa-triangle-exclamation"></i> Early Warning Signal: การเรียกเก็บค่าธรรมเนียม</h4>
            <span style="background: #FEF3C7; color: #D97706; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 700;">Weak Signal Detected</span>
        </div>
        <p style="font-size: 14px; color: #666; margin-top: 10px;">ระบบตรวจพบข้อมูลที่ขัดแย้งกัน (Contradiction) ระหว่างการสัมภาษณ์พนักงานและนโยบายฝ่ายบริหาร:</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 💡 ใช้คอลัมน์ของ Streamlit แทนโค้ด HTML grid เพื่อแก้ปัญหาบั๊กการแสดงผลโค้ดดิบ
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        st.markdown("""
        <div style="background: #F0FDF4; padding: 15px; border-radius: 8px; border: 1px solid #BBF7D0; height: 100%;">
            <span style="color: #166534; font-size: 12px; font-weight: 700;">📋 ข้อมูลนโยบาย (Tool 1)</span><br><br>
            <span style="color: #14532D; font-size: 14px;">ฝ่ายบริหารยืนยันว่า: "บริษัทใช้กลยุทธ์ Zero Recruitment Fees และออกค่าใช้จ่ายในการเดินทางให้พนักงานทั้งหมด"</span>
        </div>
        """, unsafe_allow_html=True)
    with col_w2:
        st.markdown("""
        <div style="background: #FEF2F2; padding: 15px; border-radius: 8px; border: 1px solid #FECACA; height: 100%;">
            <span style="color: #991B1B; font-size: 12px; font-weight: 700;">🗣️ ข้อมูลปฏิบัติจริง (Tool 3: EMP-012, 018)</span><br><br>
            <span style="color: #7F1D1D; font-size: 14px; font-style: italic;">"พวกเราต้องจ่ายให้เอเจนซี่ฝั่งพม่าไปคนละ 15,000 บาทก่อนเข้ามาทำงาน..."</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="gemini-draft-box" style="margin-top: 20px;">
        <h5 class="gemini-title"><span class="gemini-icon">✨</span> Gemini AI Suggestion (คำแนะนำเชิงป้องกัน):</h5>
        <p style="font-size: 14px; color: #444; margin: 0;">พบความเสี่ยงสูงด้าน <b>Debt Bondage (ภาระหนี้ผูกพัน)</b> แนะนำให้ทีม Audit สุ่มสัมภาษณ์กลุ่มแรงงานข้ามชาติจากเอเจนซี่ A เพิ่มเติมโดยด่วน และติดต่อเอเจนซี่ต้นทางเพื่อตรวจสอบเส้นทางการเงิน (Traceability)</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 รับทราบและตั้งให้เป็นหัวข้อเร่งด่วนสำหรับรอบ Audit ถัดไป"):
        sheet = connect_to_sheet()
        if sheet:
            sheet.append_row([now, audit_cycle, auditor_name, location, "Tool 6", "Issue-Based", "N/A", "N/A", "N/A", "Early Warning (Recruitment Fee)", "พบข้อขัดแย้งค่าหัวคิวระหว่าง Tool 1 และ Tool 3", "", "", "", ""])
            st.success("✅ บันทึกบันทึกสัญญาณเตือนภัยเข้าสู่ฐานข้อมูลเรียบร้อย")
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- TOOL 7 (Executive Dashboard) -----------------
elif choice == "Tool 7: แดชบอร์ดสรุปผลภาพรวม (Executive Dashboard)":
    st.markdown("<div class='standalone-form'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#005B31; margin-top:0;'>Tool 7: Executive Dashboard</h3><p style='color:#666;'>สรุปภาพรวมและกระจายตัวของความเสี่ยงสิทธิมนุษยชน (Interactive Risk Matrix)</p><hr>", unsafe_allow_html=True)
    
    # 🌟 Dashboard Metrics
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<div class='dash-card'><div class='dash-label'>ผู้เข้าร่วมสำรวจทั้งหมด</div><div class='dash-number'>135</div><div style='color: #005B31; font-size:12px;'>พนักงานและผู้มีส่วนได้เสีย</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='dash-card'><div class='dash-label'>Salient Issues (ปี 2026)</div><div class='dash-number' style='color:#DC2626;'>3</div><div style='color: #666; font-size:12px;'>ประเด็นความเสี่ยงระดับวิกฤต</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown("<div class='dash-card'><div class='dash-label'>Early Warning Signals</div><div class='dash-number' style='color:#D97706;'>2</div><div style='color: #666; font-size:12px;'>จุดเฝ้าระวังความขัดแย้งข้อมูล</div></div>", unsafe_allow_html=True)
    
    st.markdown("<br><h5 style='color: #005B31;'>📊 แผนผังกระจายตัวความเสี่ยง (Interactive Salient Risk Matrix)</h5>", unsafe_allow_html=True)
    
    # 🌟 สร้าง Interactive Heat Map ด้วย Altair (เอาเมาส์ชี้ดูข้อมูลได้)
    # ข้อมูลจำลอง (Mock Data)
    source = pd.DataFrame({
        'Severity': [4, 5, 3, 4, 2, 5, 3, 2, 4, 5],
        'Likelihood': [4, 3, 4, 5, 2, 4, 3, 3, 2, 5],
        'Issue': [
            'การจ่ายเงินล่าช้า / ไม่จ่ายโอที',
            'การยึดพาสปอร์ต',
            'สภาพแวดล้อมอันตราย (โซน B)',
            'ขาดอุปกรณ์ PPE',
            'ไม่มีที่พักผ่อนเพียงพอ',
            'การเรียกเก็บค่านายหน้า',
            'สวัสดิการอาหารไม่สะอาด',
            'การเลือกปฏิบัติต่อแรงงานหญิง',
            'ชั่วโมงทำงานติดต่อกันเกินกำหนด',
            'การใช้แรงงานเด็ก (Sub-contract)'
        ],
        'Risk_Level': ['Significant', 'Critical', 'Moderate', 'Significant', 'Minor', 'Critical', 'Moderate', 'Minor', 'Significant', 'Critical']
    })

    # วาดกราฟ Scatter แบบ Interactive
    matrix_chart = alt.Chart(source).mark_circle(size=600, opacity=0.8).encode(
        x=alt.X('Severity:O', title='Severity (ความรุนแรง)', scale=alt.Scale(domain=[1, 2, 3, 4, 5])),
        y=alt.Y('Likelihood:O', title='Likelihood (โอกาสเกิด)', scale=alt.Scale(domain=[1, 2, 3, 4, 5])),
        color=alt.Color('Risk_Level:N', 
                        scale=alt.Scale(domain=['Critical', 'Significant', 'Moderate', 'Minor'], 
                                        range=['#DC2626', '#F9A818', '#005B31', '#10B981']),
                        legend=alt.Legend(title="ระดับความเสี่ยง", orient="bottom")),
        tooltip=[
            alt.Tooltip('Issue', title='ประเด็น'),
            alt.Tooltip('Severity', title='ความรุนแรง'),
            alt.Tooltip('Likelihood', title='โอกาสเกิด'),
            alt.Tooltip('Risk_Level', title='ระดับเตือนภัย')
        ]
    ).interactive().properties(height=450)
    
    st.altair_chart(matrix_chart, use_container_width=True)
    st.info("💡 หมายเหตุ: เอาเมาส์ชี้ (Hover) ที่จุดวงกลมบนแผนผัง เพื่อดูรายละเอียดของแต่ละประเด็นความเสี่ยง เมื่อระบบพัฒนาเสร็จสมบูรณ์กราฟนี้จะดึงข้อมูลจริงจาก Google Sheet อัตโนมัติ")
    
    st.markdown("</div>", unsafe_allow_html=True)
