import streamlit as st
import pandas as pd
from google.oauth2 import service_account
import gspread
from datetime import datetime

# --- 1. SETTING UP THE PAGE ---
st.set_page_config(
    page_title="Betagro HRDD Premium Toolkit",
    page_icon="https://www.betagro.com/favicon.ico",
    layout="wide"
)

# --- ฟังก์ชันเชื่อมต่อ Google Sheet (เครื่องยนต์) ---
def connect_to_sheet():
    try:
        # ดึงรหัสจาก Secrets ที่พี่วางไว้สำเร็จแล้ว
        creds_dict = st.secrets["gcp_service_account"]
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        credentials = service_account.Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(credentials)
        
        # !!! พี่เอาลิงก์ Google Sheet ของพี่มาวางแทนที่ XXXXX ด้านล่างนี้ครับ !!!
        sheet_url = "https://docs.google.com/spreadsheets/d/XXXXXXXXXX/edit" 
        
        return client.open_by_url(sheet_url).sheet1
    except Exception as e:
        st.error(f"การเชื่อมต่อผิดพลาด: {e}")
        return None

# --- 2. THE PREMIUM STYLING (BETAGRO CORPORATE IDENTITY) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Sarabun', sans-serif; }
    .stApp { background-color: #F4F7F5; }
    [data-testid="stSidebar"] { 
        background-color: #1E3F26 !important; 
        border-right: 5px solid #F9A818;
        min-width: 320px !important;
    }
    [data-testid="stSidebar"] * { color: white !important; font-size: 16px; }
    .main-header {
        background-color: white; padding: 40px; border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08); border-top: 10px solid #F9A818;
        text-align: center; margin-bottom: 30px;
    }
    h1 { color: #1E3F26; font-weight: 800; font-size: 2.8rem; margin: 0; }
    h2 { color: #265F36; border-left: 12px solid #F9A818; padding-left: 20px; margin-top: 35px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGO & MAIN HEADER ---
st.markdown("""
    <div class="main-header">
        <h1>BETAGRO HRDD DIGITAL TOOLKIT</h1>
        <p style='color: #666; font-size: 1.2rem; margin-top: 10px;'>
            ระบบตรวจสอบสิทธิมนุษยชนอัจฉริยะ ตามมาตรฐาน UNGPs & OECD Due Diligence
        </p>
    </div>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://www.betagro.com/wp-content/themes/betagro/assets/img/logo-en.png", width=180)
    st.markdown("<br>", unsafe_allow_html=True)
    choice = st.radio("📋 เลือกเครื่องมือประเมิน:", [
        "Tool 1: แบบประเมินสถานะองค์กร", 
        "Tool 2: แบบสอบถามการปฏิบัติหน้างาน", 
        "Tool 3: แนวทางการสัมภาษณ์เชิงลึก", 
        "Tool 4: แบบบันทึกการสังเกตการณ์",
        "Tool 5: การประเมินนัยสำคัญ (Heat Map)",
        "Tool 6: ระบบวิเคราะห์ AI Triangulation"
    ])
    st.markdown("---")
    st.info("Version: 2.5 (Full Content Integration)")

# --- 5. TOOL CONTENT ---

if choice == "Tool 1: แบบประเมินสถานะองค์กร":
    st.header("🏢 Tool 1: แบบประเมินสถานะองค์กร")
    with st.form("form_t1"):
        q1_1 = st.radio("1.1 องค์กรมี 'นโยบายสิทธิมนุษยชน' เป็นลายลักษณ์อักษรหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_2 = st.radio("1.2 นโยบายครอบคลุมประเด็นสำคัญหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        
        if st.form_submit_button("บันทึกข้อมูล Tool 1"):
            sheet = connect_to_sheet()
            if sheet:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sheet.append_row([now, "Tool 1", q1_1, q1_2])
                st.success("บันทึกข้อมูลลง Google Sheet เรียบร้อย!")

elif choice == "Tool 2: แบบสอบถามการปฏิบัติหน้างาน":
    st.header("📊 Tool 2: แบบสอบถามการปฏิบัติ")
    with st.form("form_t2"):
        q2_1 = st.select_slider("1.1 ท่านได้รับค่าจ้างตรงเวลาหรือไม่?", options=[1,2,3,4,5], value=3)
        if st.form_submit_button("ส่งผลแบบสำรวจ"):
            sheet = connect_to_sheet()
            if sheet:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sheet.append_row([now, "Tool 2", q2_1])
                st.success("ส่งข้อมูลสำเร็จ!")
                st.balloons()

elif choice == "Tool 3: แนวทางการสัมภาษณ์เชิงลึก":
    st.header("🎙️ Tool 3: แนวทางการสัมภาษณ์")
    with st.form("form_t3"):
        i1 = st.text_area("1. ขั้นตอนการสรรหาก่อนเริ่มงาน ท่านมีค่าใช้จ่ายใดๆ หรือไม่?")
        if st.form_submit_button("บันทึกบทสัมภาษณ์"):
            sheet = connect_to_sheet()
            if sheet:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sheet.append_row([now, "Tool 3", i1])
                st.success("บันทึกสำเร็จ")

elif choice == "Tool 4: แบบบันทึกการสังเกตการณ์":
    st.header("🔎 Tool 4: แบบบันทึกการสังเกตการณ์ภาคสนาม")
    with st.form("form_t4"):
        o1 = st.checkbox("มีป้ายนโยบายชัดเจน")
        note = st.text_area("บันทึกเพิ่มเติม:")
        if st.form_submit_button("บันทึก Log"):
            sheet = connect_to_sheet()
            if sheet:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sheet.append_row([now, "Tool 4", str(o1), note])
                st.success("บันทึกแล้ว")

elif choice == "Tool 5: การประเมินนัยสำคัญ (Heat Map)":
    st.header("⚖️ Tool 5: Salient Human Rights Risks")
    issue = st.text_input("ชื่อประเด็น:", "ความปลอดภัย")
    s1 = st.slider("ความรุนแรง (Severity)", 1, 5, 3)
    l1 = st.slider("โอกาสเกิด (Likelihood)", 1, 5, 2)
    if st.button("บันทึกค่าความเสี่ยง"):
        sheet = connect_to_sheet()
        if sheet:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sheet.append_row([now, "Tool 5", issue, s1, l1, s1*l1])
            st.success("บันทึกค่าความเสี่ยงเรียบร้อย")

elif choice == "Tool 6: ระบบวิเคราะห์ AI Triangulation":
    st.header("🤖 Tool 6: AI-Driven Analysis")
    raw_data = st.text_area("กรอกข้อมูลดิบเพื่อประมวลผล:")
    if st.button("เริ่มการวิเคราะห์"):
        st.info("ระบบกำลังเตรียมการวิเคราะห์ข้อมูล...")

# --- 6. FOOTER ---
st.markdown("<br><hr><p style='text-align: center; color: #888;'>© 2024 Betagro Group | Sustainability Department</p>", unsafe_allow_html=True)
