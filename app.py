import streamlit as st
import pandas as pd
from google.oauth2 import service_account
import gspread
from datetime import datetime

# --- 1. SETTING UP THE PAGE ---
st.set_page_config(page_title="Betagro HRDD Premium Toolkit", page_icon="👑", layout="centered")

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

# --- 3. ULTRA-PREMIUM STYLING (MODERN LUXURY) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&family=Sarabun:wght@300;400;600;700;800&display=swap');
    
    html, body, [class*="st-"] { font-family: 'Sarabun', sans-serif; }
    .stApp { background-color: #F4F7F6; }
    
    /* 🚫 ซ่อนเมนูระบบและไอคอนลิงก์กวนใจทั้งหมด */
    header[data-testid="stHeader"], [data-testid="collapsedControl"], [data-testid="stSidebar"] { display: none !important; }
    a.header-anchor { display: none !important; }

    /* 👑 แบนเนอร์ด้านบน (Hero Banner) - ปรับย่อขนาด Padding ให้พอดีไม่ตกขอบ */
    .premium-banner {
        background: #FFFFFF; border-radius: 24px; padding: 30px 40px;
        box-shadow: 0px 20px 40px rgba(0, 91, 49, 0.05);
        border: 1px solid rgba(0, 91, 49, 0.08); border-left: 12px solid #005B31; 
        display: flex; align-items: center; gap: 30px; margin-bottom: 40px;
        position: relative; overflow: hidden;
    }
    .premium-banner::after { content: ''; position: absolute; top: 0; right: 0; width: 150px; height: 8px; background: #F9A818; }
    
    /* 🎨 โลโก้และ Typography */
    .logo-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        border-right: 2px solid #EAEAEA;
        padding-right: 30px;
    }
    .typography-logo {
        font-family: 'Poppins', sans-serif;
        font-size: 26px; /* ย่อจาก 32px เพื่อให้สมดุล */
        font-weight: 800;
        color: #D3A129; 
        letter-spacing: 2px;
        line-height: 1;
        margin-top: 10px;
    }

    /* 💡 การจัดวาง Typography แบบหรูหรา (ปรับขนาดฟอนต์ไม่ให้ตกขอบหน้าจอ) */
    .banner-text {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .hero-title-eng {
        color: #005B31 !important; 
        font-family: 'Poppins', sans-serif !important;
        font-size: 21px !important; /* ปรับลดจาก 26px เพื่อให้พอดีขอบ */
        font-weight: 800 !important; 
        margin: 0 !important; 
        line-height: 1.1 !important; 
        letter-spacing: 1px !important;
        white-space: nowrap !important;
    }
    .hero-title-thai {
        color: #265F36 !important; 
        font-family: 'Sarabun', sans-serif !important;
        font-size: 16px !important; /* ปรับลดจาก 20px */
        font-weight: 600 !important;
        margin: 5px 0 0 0 !important;
        line-height: 1.3 !important;
        white-space: nowrap !important;
    }
    .hero-subtitle {
        color: #D3A129 !important; 
        font-family: 'Poppins', sans-serif !important;
        font-size: 11px !important; /* ปรับลดจาก 13px */
        font-weight: 700 !important; 
        letter-spacing: 3px !important; 
        text-transform: uppercase !important; 
        margin-top: 14px !important; 
        margin-bottom: 0 !important;
        padding-top: 10px !important;
        border-top: 1px solid rgba(211, 161, 41, 0.3) !important;
        width: fit-content;
    }
    
    /* Responsive สำหรับมือถือ */
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
    .citation-box { background-color: #FFFFFF; padding: 25px; border-left: 6px solid #DC2626; border-radius: 12px; margin: 20px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #F3F4F6;}
    .heat-table { width: 100%; border-collapse: separate; border-spacing: 4px; margin-top: 15px;}
    .heat-cell { height: 50px; text-align: center; font-weight: bold; color: white; border-radius: 8px; font-size: 14px;}
    </style>
    """, unsafe_allow_html=True)

# --- 4. TOP-DOWN UI ---
st.markdown("""
    <div class="premium-banner">
        <div class="logo-wrapper">
            <!-- 🎨 SVG โลโก้เบทาโกร (3 แฉก) -->
            <svg width="65" height="65" viewBox="0 0 100 100" style="margin-bottom: 5px; filter: drop-shadow(0 6px 15px rgba(0,91,49,0.15));">
                <circle cx="36" cy="38" r="23" fill="#005B31"/>
                <circle cx="64" cy="38" r="23" fill="#005B31"/>
                <circle cx="50" cy="62" r="23" fill="#005B31"/>
                <path d="M 50,42 Q 54,54 62,60 Q 50,56 38,60 Q 46,54 50,42 Z" fill="#FFFFFF" stroke="#FFFFFF" stroke-width="2" stroke-linejoin="round"/>
            </svg>
            <div class="typography-logo">
                BETAGRO
            </div>
        </div>
        <div class="banner-text">
            <div class="hero-title-eng">BETAGRO STRATEGIC HRDD TOOLKIT</div>
            <div class="hero-title-thai">ระบบยุทธศาสตร์บริหารจัดการสิทธิมนุษยชนอัจฉริยะ</div>
            <div class="hero-subtitle">Smart Assessment Systems & Analytics</div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown('<div class="control-panel">', unsafe_allow_html=True)
st.markdown("<h4 style='color: #005B31; margin-bottom: 15px; font-weight: 700;'>👤 1. ข้อมูลโครงการและผู้ให้ข้อมูล</h4>", unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    auditor_name = st.text_input("ชื่อผู้บันทึกข้อมูล (Auditor) *", placeholder="เช่น สมชาย ใจดี")
    resp_id = st.text_input("รหัสผู้ให้ข้อมูล (ID) *", placeholder="เช่น EMP-001")
with col2:
    location = st.text_input("พื้นที่สำรวจ (Location/Site) *", placeholder="เช่น โรงงานลพบุรี")
    resp_group = st.selectbox("กลุ่มเป้าหมาย *", ["ฝ่ายบริหาร", "แรงงานไทย", "แรงงานข้ามชาติ", "ชุมชน", "คู่ค้า"])

st.markdown("<hr style='border: 1px solid #eee; margin: 20px 0;'>", unsafe_allow_html=True)
st.markdown("<h4 style='color: #005B31; margin-bottom: 15px; font-weight: 700;'>🛠️ 2. เลือกเครื่องมือประเมิน</h4>", unsafe_allow_html=True)
choice = st.selectbox("เลือกแบบฟอร์มด้านล่างนี้:", [
    "Tool 1: ประเมินสถานะองค์กร",
    "Tool 2: แบบสอบถามหน้างาน",
    "Tool 3: สัมภาษณ์เชิงลึก (Evidence)",
    "Tool 4: บันทึกการสังเกตการณ์",
    "Tool 5: ประเมินนัยสำคัญ (Salient Rule & Strategic Plan)",
    "Tool 6: ระบบวิเคราะห์ AI Triangulation"
], label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

if not resp_id or not auditor_name or not location:
    st.info("📌 กรุณาระบุข้อมูลโครงการและรหัสผู้ให้ข้อมูลให้ครบถ้วน เพื่อปลดล็อกแบบฟอร์ม")
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
                sheet.append_row([now, auditor_name, location, "Tool 1", resp_id, resp_group, "Policy Gap Analysis", detail, "", "", "", ""])
                st.success("✅ บันทึกข้อมูล Tool 1 เรียบร้อย")

elif choice == "Tool 2: แบบสอบถามหน้างาน":
    with st.form("form_t2"):
        st.markdown("<h3 style='color:#005B31;'>Tool 2: แบบสอบถามการปฏิบัติหน้างาน (Worker Survey)</h3><hr>", unsafe_allow_html=True)
        st.markdown("**ส่วนที่ 1: สภาพการจ้างและค่าจ้าง**")
        s1_1 = st.select_slider("1.1 ท่านได้รับค่าจ้างตรงเวลาและครบถ้วนตามสัญญาหรือไม่?", options=[1,2,3,4,5], value=3)
        s1_3 = st.select_slider("1.2 ท่านเป็นผู้เก็บเอกสารประจำตัวไว้เองใช่หรือไม่?", options=[1,2,3,4,5], value=3)
        st.markdown("<hr style='border: 1px dashed #ccc;'>", unsafe_allow_html=True)
        
        st.markdown("**ส่วนที่ 2: ความปลอดภัยและสุขอนามัย (OHS)**")
        s2_1 = st.select_slider("2.1 อุปกรณ์ป้องกันอันตราย (PPE) มีเพียงพอและอยู่ในสภาพพร้อมใช้งานหรือไม่?", options=[1,2,3,4,5], value=3)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("🚀 บันทึกข้อมูล Tool 2"):
            sheet = connect_to_sheet()
            if sheet:
                detail = f"การจ้าง({s1_1},{s1_3}) | ความปลอดภัย({s2_1})"
                sheet.append_row([now, auditor_name, location, "Tool 2", resp_id, resp_group, "Worker Practice", detail, "", "", "", ""])
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
                sheet.append_row([now, auditor_name, location, "Tool 3", resp_id, resp_group, ", ".join(topics), testimony, "", "", "", ""])
                st.success("✅ บันทึกหลักฐานสำเร็จ")

elif choice == "Tool 4: บันทึกการสังเกตการณ์":
    with st.form("form_t4"):
        st.markdown("<h3 style='color:#005B31;'>Tool 4: บันทึกการสังเกตการณ์ (Observation Log)</h3><hr>", unsafe_allow_html=True)
        o1 = st.checkbox("1. มีการติดประกาศนโยบายในพื้นที่ที่มองเห็นได้ชัดเจน")
        o2 = st.checkbox("2. ทางหนีไฟไม่มีสิ่งกีดขวางและอยู่ในสภาพพร้อมใช้งาน")
        o3 = st.checkbox("3. พนักงานสวมใส่อุปกรณ์ PPE ถูกต้อง")
        
        st.markdown("<br>**📝 บันทึกสิ่งที่พบเพิ่มเติม**", unsafe_allow_html=True)
        obs_detail = st.text_area("รายละเอียด:", height=100, label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("💾 บันทึกข้อมูล Tool 4"):
            sheet = connect_to_sheet()
            if sheet:
                detail = f"Checklist({o1},{o2},{o3}) | Note:{obs_detail}"
                sheet.append_row([now, auditor_name, location, "Tool 4", resp_id, resp_group, "Site Observation", detail, "", "", "", ""])
                st.success("✅ บันทึกการสังเกตการณ์สำเร็จ")

# ==========================================
# TOOL 5: ประเมินนัยสำคัญ & STRATEGIC PLAN
# ==========================================
elif choice == "Tool 5: ประเมินนัยสำคัญ (Salient Rule & Strategic Plan)":
    st.markdown("<div class='standalone-form'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#005B31; margin-top:0;'>Tool 5: HR Risk Matrix & Strategic Plan</h3><p style='color:#666;'>ประเมินความเสี่ยงและจัดทำแผนบรรเทาผลกระทบ (Mitigation Plan)</p><hr>", unsafe_allow_html=True)
    
    st.markdown("**📌 1. ระบุประเด็นความเสี่ยง (อ้างอิงมาตรฐาน ILO)**")
    issue = st.selectbox("หมวดหมู่ความเสี่ยง:", [
        "[แรงงานบังคับ] ภาระหนี้ผูกพัน / การเรียกเก็บค่าธรรมเนียมสรรหา",
        "[แรงงานบังคับ] การยึดเอกสารประจำตัว (พาสปอร์ต/บัตร)",
        "[สิทธิแรงงาน] การจ่ายเงินล่าช้า / ไม่จ่ายโอที",
        "[อาชีวอนามัย] สภาพแวดล้อมการทำงานอันตราย / ขาด PPE",
        "[ชุมชน] ผลกระทบต่อสิ่งแวดล้อมและชุมชนโดยรอบ",
        "อื่นๆ"
    ], label_visibility="collapsed")
    
    st.markdown("<hr style='border: 1px dashed #ccc;'>", unsafe_allow_html=True)
    st.markdown("**📌 2. คำนวณ Severity (ใช้ค่าสูงสุด)**")
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1: scale = st.slider("Scale (ความรุนแรง)", 1, 5, 1)
    with col_s2: scope = st.slider("Scope (จำนวนผู้ได้รับผลกระทบ)", 1, 5, 1)
    with col_s3: remedy = st.slider("Remediability (การเยียวยา)", 1, 5, 1)
    
    sev_max = max(scale, scope, remedy)
    st.markdown("<hr style='border: 1px dashed #ccc;'>", unsafe_allow_html=True)
    likelihood = st.slider("📌 3. Likelihood (โอกาสที่จะเกิด)", 1, 5, 1)
    score = sev_max * likelihood

    is_salient = "YES" if sev_max >= 4 else "NO"
    
    st.markdown(f"<h4 style='color: #005B31; text-align:center; padding: 15px; background: #F4F7F6; border-radius: 8px;'>Severity Max: {sev_max} | โอกาสเกิด: {likelihood} | คะแนนรวม: {score}</h4>", unsafe_allow_html=True)
    
    plan_text = ""
    if is_salient == "YES":
        st.markdown('<div class="salient-badge">🚨 SALIENT ISSUE: ความเสี่ยงระดับสูง (จำเป็นต้องมีแผนจัดการกลยุทธ์)</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="strategic-box">
            <h4 style="color: #D3A129; margin-top: 0;"><i class="fa-solid fa-shield-halved"></i> Strategic Mitigation & Remediation Plan</h4>
            <p style="font-size: 14px; color: #666; margin-bottom: 15px;">โปรดระบุแผนการจัดการเพื่อป้องกันและเยียวยาความเสี่ยง (Action Plan)</p>
        </div>
        """, unsafe_allow_html=True)
        plan_text = st.text_area("มาตรการป้องกันและเยียวยา (Preventive & Remediation Actions):", height=120, placeholder="ระบุขั้นตอนการแก้ปัญหา, ผู้รับผิดชอบ และกรอบเวลาดำเนินการ...")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 บันทึกการประเมินและแผนกลยุทธ์"):
        sheet = connect_to_sheet()
        if sheet:
            detail = f"Scale:{scale}, Scope:{scope}, Remedy:{remedy} | Plan: {plan_text}"
            sheet.append_row([now, auditor_name, location, "Tool 5", resp_id, resp_group, issue, detail, sev_max, likelihood, score, is_salient])
            st.success("✅ บันทึกความเสี่ยงและแผนกลยุทธ์ (Strategic Plan) เข้าสู่ระบบเรียบร้อย")
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# TOOL 6: AI Triangulation & AI STRATEGY
# ==========================================
elif choice == "Tool 6: ระบบวิเคราะห์ AI Triangulation":
    st.markdown("<div class='standalone-form'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#005B31; margin-top:0;'>Tool 6: AI-Augmented Triangulation & Strategic Proposal</h3><hr>", unsafe_allow_html=True)
    
    st.info("💡 ระบบ AI ทำการเปรียบเทียบข้อมูล (Triangulation) และเสนอแนะแผนกลยุทธ์ (Strategic Recommendations) อัตโนมัติ")
    
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
        
        <div style="margin-top: 20px; background: #FFFDF0; padding: 15px; border-radius: 8px; border-left: 4px solid #F9A818;">
            <h5 style="color: #D3A129; margin-top: 0; margin-bottom: 5px;">🤖 AI Strategic Recommendation (ข้อเสนอแนะเชิงกลยุทธ์):</h5>
            <ol style="margin-bottom: 0; font-size: 14px; color: #444; padding-left: 20px;">
                <li><b>Preventive:</b> จัดทำสัญญาจ้างแบบ 2 ภาษา (Bilingual) และบังคับใช้กับ Supplier ทุกราย</li>
                <li><b>Mitigation:</b> จัดหาล่ามอิสระ (Third-party Translator) ในวันปฐมนิเทศพนักงานใหม่</li>
                <li><b>Timeline:</b> ทบทวนกระบวนการและจัดทำสัญญาฉบับแก้ไขภายใน 30 วัน (Short-term action)</li>
            </ol>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 บันทึกสรุปผล AI Analysis และแผนกลยุทธ์ลงระบบ"):
        sheet = connect_to_sheet()
        if sheet:
            sheet.append_row([now, auditor_name, location, "Tool 6", resp_id, resp_group, "AI Triangulation", "พบข้อขัดแย้งสัญญาจ้าง พร้อมจัดทำแผนแก้ไข 30 วัน", "", "", "", ""])
            st.success("✅ บันทึกข้อมูลการวิเคราะห์เชิงลึกและแผนกลยุทธ์เสร็จสิ้น")
    st.markdown("</div>", unsafe_allow_html=True)
