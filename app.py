import streamlit as st
import pandas as pd
from google.oauth2 import service_account
import gspread
from datetime import datetime
import time

# --- 1. SETTING UP THE PAGE ---
st.set_page_config(page_title="Betagro HRDD Premium Toolkit", layout="wide")

# --- 2. ฟังก์ชันเชื่อมต่อ (แก้ Indentation และ DNS) ---
def connect_to_sheet():
    try:
        # บรรทัดนี้ต้องย่อหน้าเข้าไป 4 spaces ให้ตรงกัน
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        creds_dict["token_uri"] = "https://accounts.google.com/o/oauth2/token"
        
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        credentials = service_account.Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(credentials)
        
        sheet_url = "https://docs.google.com/spreadsheets/d/1YUkrlk_RlvskDluFoAdTQ7KRYRxYhi8ZqNdw13X7JxY/edit"
        sheet = client.open_by_url(sheet_url).get_worksheet(0)
        return sheet
    except Exception as e:
        st.error(f"❌ การเชื่อมต่อล้มเหลว: {e}")
        return None

# --- 3. การตกแต่งหน้าจอ ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun&display=swap');
    html, body, [class*="st-"] { font-family: 'Sarabun', sans-serif; }
    .main-header { background-color: white; padding: 30px; border-radius: 15px; border-top: 8px solid #F9A818; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>BETAGRO HRDD DIGITAL TOOLKIT</h1></div>', unsafe_allow_html=True)

# --- 4. เมนูข้าง ---
with st.sidebar:
    st.image("https://www.betagro.com/wp-content/themes/betagro/assets/img/logo-en.png", width=150)
    choice = st.radio("📋 เลือกเครื่องมือ:", [
        "Tool 1: แบบประเมินสถานะองค์กร", 
        "Tool 2: แบบสอบถามการปฏิบัติหน้างาน", 
        "Tool 3: แนวทางการสัมภาษณ์เชิงลึก", 
        "Tool 4: แบบบันทึกการสังเกตการณ์",
        "Tool 5: การประเมินนัยสำคัญ (Heat Map)",
        "Tool 6: ระบบวิเคราะห์ AI Triangulation"
    ])

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- 5. เนื้อหาเครื่องมือ (คืนรายละเอียดให้ครบ) ---
if choice == "Tool 1: แบบประเมินสถานะองค์กร":
    st.header("🏢 Tool 1: แบบประเมินสถานะองค์กร")
    with st.form("form_t1"):
        q1 = st.radio("1.1 มีนโยบายสิทธิมนุษยชนหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q2 = st.radio("1.2 มีการประเมินความเสี่ยงหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        if st.form_submit_button("บันทึก Tool 1"):
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([now, "Tool 1", q1, q2])
                st.success("✅ บันทึกสำเร็จ")

elif choice == "Tool 2: แบบสอบถามการปฏิบัติหน้างาน":
    st.header("📊 Tool 2: แบบสอบถาม (รายละเอียดครบ)")
    with st.form("form_t2"):
        q2_1 = st.select_slider("1.1 ได้รับค่าจ้างตรงเวลา?", options=[1,2,3,4,5], value=3)
        q2_2 = st.select_slider("1.2 ได้รับวันหยุด?", options=[1,2,3,4,5], value=3)
        q2_3 = st.select_slider("1.3 เก็บสัญญาจ้างไว้ที่ตัว?", options=[1,2,3,4,5], value=3)
        q3_1 = st.select_slider("2.1 PPE เพียงพอ?", options=[1,2,3,4,5], value=3)
        q3_2 = st.select_slider("2.2 ได้รับการอบรม OHS?", options=[1,2,3,4,5], value=3)
        if st.form_submit_button("บันทึก Tool 2"):
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([now, "Tool 2", q2_1, q2_2, q2_3, q3_1, q3_2])
                st.success("✅ บันทึก Tool 2 สำเร็จ")

elif choice == "Tool 3: แนวทางการสัมภาษณ์เชิงลึก":
    st.header("🎙️ Tool 3: แนวทางสัมภาษณ์")
    with st.form("form_t3"):
        i1 = st.text_area("สัมภาษณ์เรื่องค่าใช้จ่ายในการสมัครงาน:")
        i2 = st.text_area("สัมภาษณ์เรื่องภาษาที่สื่อสาร:")
        if st.form_submit_button("บันทึก Tool 3"):
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([now, "Tool 3", i1, i2])
                st.success("✅ บันทึกสำเร็จ")

elif choice == "Tool 4: แบบบันทึกการสังเกตการณ์":
    st.header("🔎 Tool 4: การสังเกตการณ์")
    with st.form("form_t4"):
        o1 = st.checkbox("ป้ายนโยบายชัดเจน")
        o2 = st.checkbox("ทางหนีไฟพร้อม")
        if st.form_submit_button("บันทึก Tool 4"):
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([now, "Tool 4", str(o1), str(o2)])
                st.success("✅ บันทึกสำเร็จ")

elif choice == "Tool 5: การประเมินนัยสำคัญ (Heat Map)":
    st.header("⚖️ Tool 5: Salient Risk Heat Map")
    s = st.slider("ความรุนแรง (Severity)", 1, 5, 3)
    l = st.slider("โอกาสเกิด (Likelihood)", 1, 5, 3)
    if st.button("บันทึกค่า Heat Map"):
        sheet = connect_to_sheet()
        if sheet:
            sheet.append_row([now, "Tool 5", s, l, s*l])
            st.success(f"✅ บันทึกค่า {s*l} สำเร็จ")

elif choice == "Tool 6: ระบบวิเคราะห์ AI Triangulation":
    st.header("🤖 Tool 6: AI Analysis")
    st.info("กำลังรอการเชื่อมต่อ API...")

st.markdown("<br><hr><p style='text-align: center;'>© 2024 Betagro Group</p>", unsafe_allow_html=True)
