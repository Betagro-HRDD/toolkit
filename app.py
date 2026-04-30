import streamlit as st
import pandas as pd
from google.oauth2 import service_account
import gspread
from datetime import datetime

# --- 1. SETTING UP THE PAGE ---
st.set_page_config(page_title="Betagro HRDD Premium Toolkit", page_icon="https://www.betagro.com/favicon.ico", layout="wide")

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

# --- 3. PREMIUM STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Sarabun', sans-serif; }
    .stApp { background-color: #F8FAFB; }
    .main-header {
        background-color: white; padding: 30px; border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-left: 10px solid #F9A818;
        margin-bottom: 25px; text-align: center;
    }
    .salient-badge { background-color: #EF4444; color: white; padding: 10px 20px; border-radius: 10px; font-weight: bold; display: block; text-align: center; }
    .citation-box { background-color: #E8EEE8; padding: 15px; border-left: 5px solid #265F36; border-radius: 5px; margin: 10px 0; }
    .heat-table { width: 100%; border-collapse: separate; border-spacing: 5px; }
    .heat-cell { height: 50px; text-align: center; font-weight: bold; color: white; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.image("https://www.betagro.com/wp-content/themes/betagro/assets/img/logo-en.png", width=160)
    st.title("HRDD Settings")
    # ชื่อในลิสต์นี้ ต้องตรงกับเงื่อนไข if/elif ข้างล่างเป๊ะๆ
    choice = st.radio("📋 เลือกเครื่องมือ:", [
        "Tool 1: ประเมินสถานะองค์กร",
        "Tool 2: แบบสอบถามหน้างาน",
        "Tool 3: สัมภาษณ์เชิงลึก (Evidence)",
        "Tool 4: บันทึกการสังเกตการณ์",
        "Tool 5: ประเมินนัยสำคัญ (Salient Rule)",
        "Tool 6: AI Triangulation"
    ])
    st.divider()
    st.subheader("👤 ข้อมูลผู้ให้ข้อมูล")
    resp_id = st.text_input("รหัสพนักงาน/ID:", placeholder="เช่น EMP-001")
    resp_group = st.selectbox("กลุ่ม:", ["ฝ่ายบริหาร", "แรงงานไทย", "แรงงานข้ามชาติ", "ชุมชน", "คู่ค้า"])

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- 5. TOOL CONTENT ---

# --- TOOL 1 ---
if choice == "Tool 1: ประเมินสถานะองค์กร":
    st.markdown('<div class="main-header"><h1>Tool 1: แบบประเมินสถานะองค์กร</h1></div>', unsafe_allow_html=True)
    with st.form("form_t1"):
        q1 = st.radio("มีนโยบายด้านสิทธิมนุษยชนที่ลงนามโดยผู้บริหารสูงสุดหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q2 = st.radio("นโยบายครอบคลุมห่วงโซ่อุปทาน (Supply Chain) หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        if st.form_submit_button("💾 บันทึกข้อมูล Tool 1"):
            sheet = connect_to_sheet()
            if sheet:
                # บันทึกลง 10 คอลัมน์มาตรฐาน
                detail = f"Policy Signed: {q1}, Supply Chain Cover: {q2}"
                sheet.append_row([now, "Tool 1", resp_id, resp_group, "Gap Analysis", detail, "", "", "", ""])
                st.success("✅ บันทึกสำเร็จ")

# --- TOOL 2 ---
elif choice == "Tool 2: แบบสอบถามหน้างาน":
    st.markdown('<div class="main-header"><h1>Tool 2: แบบสอบถามการปฏิบัติหน้างาน</h1></div>', unsafe_allow_html=True)
    with st.form("form_t2"):
        q2_1 = st.slider("ความพึงพอใจต่อสภาพแวดล้อมในการทำงาน (1-5)", 1, 5, 3)
        q2_2 = st.radio("ท่านได้รับค่าจ้างตรงเวลาทุกเดือนหรือไม่?", ["ใช่", "ไม่ใช่"])
        if st.form_submit_button("💾 บันทึกข้อมูล Tool 2"):
            sheet = connect_to_sheet()
            if sheet:
                detail = f"Satisfaction: {q2_1}, On-time Payment: {q2_2}"
                sheet.append_row([now, "Tool 2", resp_id, resp_group, "Worker Survey", detail, "", "", "", ""])
                st.success("✅ บันทึกสำเร็จ")

# --- TOOL 3 ---
elif choice == "Tool 3: สัมภาษณ์เชิงลึก (Evidence)":
    st.markdown('<div class="main-header"><h1>Tool 3: แนวทางการสัมภาษณ์เชิงลึก</h1></div>', unsafe_allow_html=True)
    with st.form("form_t3"):
        topics = st.multiselect("หัวข้อที่พบประเด็น:", ["ค่าธรรมเนียมสรรหา", "สัญญาจ้าง", "ค่าจ้าง/โอที", "การเลือกปฏิบัติ"])
        testimony = st.text_area("✍️ บันทึกคำพูด/หลักฐาน (Evidence-based):", placeholder="เช่น 'พนักงานแจ้งว่า...'")
        if st.form_submit_button("💾 บันทึกข้อมูล Tool 3"):
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([now, "Tool 3", resp_id, resp_group, ", ".join(topics), testimony, "", "", "", ""])
                st.success("✅ บันทึกสำเร็จ")

# --- TOOL 4 ---
elif choice == "Tool 4: บันทึกการสังเกตการณ์":
    st.markdown('<div class="main-header"><h1>Tool 4: แบบบันทึกการสังเกตการณ์</h1></div>', unsafe_allow_html=True)
    with st.form("form_t4"):
        obs = st.multiselect("สิ่งที่ตรวจพบ:", ["ป้ายประกาศนโยบาย", "อุปกรณ์ PPE", "จุดล้างมือ/สุขอนามย", "ทางหนีไฟ"])
        obs_detail = st.text_input("รายละเอียดที่สังเกตเห็น:")
        if st.form_submit_button("💾 บันทึกข้อมูล Tool 4"):
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([now, "Tool 4", resp_id, resp_group, ", ".join(obs), obs_detail, "", "", "", ""])
                st.success("✅ บันทึกสำเร็จ")

# --- TOOL 5 ---
elif choice == "Tool 5: ประเมินนัยสำคัญ (Salient Rule)":
    st.markdown('<div class="main-header"><h1>Tool 5: Salient Issues Assessment</h1></div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.2])
    with col1:
        issue = st.text_input("ชื่อประเด็นความเสี่ยง:", "แรงงานบังคับ")
        st.write("**คำนวณ Severity (Max Rule)**")
        scale = st.slider("Scale", 1, 5, 1)
        scope = st.slider("Scope", 1, 5, 1)
        remedy = st.slider("Remediability", 1, 5, 1)
        sev_max = max(scale, scope, remedy)
        likelihood = st.slider("Likelihood", 1, 5, 1)
        score = sev_max * likelihood
        is_salient = "YES" if sev_max == 5 else "NO"
        if is_salient == "YES": st.markdown('<div class="salient-badge">🚨 SALIENT ISSUE</div>', unsafe_allow_html=True)
    with col2:
        rows = ""
        for l in range(5, 0, -1):
            rows += "<tr>"
            for s in range(1, 6):
                val = s * l
                color = "#EF4444" if val >= 16 or s == 5 else ("#F9A818" if val >= 8 else "#265F36")
                mark = "★" if s == sev_max and l == likelihood else ""
                rows += f"<td class='heat-cell' style='background-color:{color};'>{mark}</td>"
            rows += "</tr>"
        st.markdown(f"<table class='heat-table'>{rows}</table>", unsafe_allow_html=True)
    if st.button("💾 บันทึกค่า Salient Rule"):
        sheet = connect_to_sheet()
        if sheet:
            detail = f"Scale:{scale}, Scope:{scope}, Remedy:{remedy}"
            sheet.append_row([now, "Tool 5", resp_id, resp_group, issue, detail, sev_max, likelihood, score, is_salient])
            st.success("✅ บันทึกเข้า Sheet เรียบร้อย")

# --- TOOL 6 ---
elif choice == "Tool 6: AI Triangulation":
    st.markdown('<div class="main-header"><h1>Tool 6: AI Triangulation</h1></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="citation-box">
        <b>🚩 ข้อพบเชิงประจักษ์:</b> สัญญาจ้างไม่เป็นภาษาที่พนักงานเข้าใจ<br>
        <small>อ้างอิงคำสัมภาษณ์ (ID: EMP-001): "ผมอ่านไม่ออกเลยตอนเซ็น..."</small>
    </div>
    """, unsafe_allow_html=True)
    if st.button("💾 บันทึกสรุป AI Analysis"):
        sheet = connect_to_sheet()
        if sheet:
            sheet.append_row([now, "Tool 6", resp_id, resp_group, "AI Analysis", "พบความขัดแย้งเชิงนโยบาย", "", "", "", ""])
            st.success("✅ บันทึกสำเร็จ")

st.markdown("<br><hr><p style='text-align: center; color: #888;'>© 2024 Betagro Group | HRDD Digital Toolkit</p>", unsafe_allow_html=True)
