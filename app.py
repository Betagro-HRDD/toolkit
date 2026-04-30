import streamlit as st
import pandas as pd
from google.oauth2 import service_account
import gspread
from datetime import datetime
import time

# --- 1. SETTING UP THE PAGE ---
st.set_page_config(page_title="Betagro HRDD Premium Toolkit", layout="wide")

# --- 2. ฟังก์ชันเชื่อมต่อ (แบบแก้ปัญหา NameResolutionError) ---
def connect_to_sheet():
    # ลองเชื่อมต่อสูงสุด 3 ครั้งเผื่อ Network ชั่วคราว
    for attempt in range(3):
        try:
            # ดึงค่าจาก Secrets (อ้างอิงตามโครงสร้างที่เราคุยกัน)
            if "gcp_service_account" in st.secrets:
                creds_info = dict(st.secrets["gcp_service_account"])
            else:
                creds_info = dict(st.secrets)

            # ล้างค่ารหัส Private Key
            if "private_key" in creds_info:
                creds_info["private_key"] = creds_info["private_key"].replace("\\\\n", "\n").replace("\\n", "\n")
            
            # กำหนด Scope
            scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
            
            # สร้าง Credentials
            credentials = service_account.Credentials.from_service_account_info(creds_info, scopes=scope)
            client = gspread.authorize(credentials)
            
            # เปิด Sheet
            sheet_url = "https://docs.google.com/spreadsheets/d/1YUkrlk_RlvskDluFoAdTQ7KRYRxYhi8ZqNdw13X7JxY/edit"
            sheet = client.open_by_url(sheet_url).get_worksheet(0)
            return sheet
        except Exception as e:
            if attempt < 2:
                time.sleep(2) # รอสักพักแล้วลองใหม่
                continue
            st.error(f"❌ การเชื่อมต่อล้มเหลว: {str(e)}")
            return None

# --- 3. STYLING (เนื้อหาเดิมของพี่) ---
st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Sarabun', sans-serif; }
    .stApp { background-color: #F4F7F5; }
    .main-header { background-color: white; padding: 40px; border-radius: 20px; border-top: 10px solid #F9A818; text-align: center; }
    </style>""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>BETAGRO HRDD DIGITAL TOOLKIT</h1></div>', unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    choice = st.radio("📋 เลือกเครื่องมือประเมิน:", [
        "Tool 1: แบบประเมินสถานะองค์กร", "Tool 2: แบบสอบถามการปฏิบัติหน้างาน", 
        "Tool 3: แนวทางการสัมภาษณ์เชิงลึก", "Tool 4: แบบบันทึกการสังเกตการณ์",
        "Tool 5: การประเมินนัยสำคัญ (Heat Map)", "Tool 6: ระบบวิเคราะห์ AI Triangulation"
    ])

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- 5. TOOL LOGIC (คงเนื้อหาพี่ไว้ครบถ้วน) ---
if choice == "Tool 1: แบบประเมินสถานะองค์กร":
    st.header("🏢 Tool 1: แบบประเมินสถานะองค์กร")
    with st.form("form_t1"):
        q1_1 = st.radio("1.1 องค์กรมี 'นโยบายสิทธิมนุษยชน' หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_2 = st.radio("1.2 นโยบายครอบคลุมประเด็นสำคัญหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_3 = st.radio("1.3 มีการสื่อสารนโยบายหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_4 = st.radio("1.4 มีผู้รับผิดชอบระดับบริหารหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        if st.form_submit_button("บันทึกข้อมูล"):
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([now, "Tool 1", q1_1, q1_2, q1_3, q1_4])
                st.success("✅ บันทึกสำเร็จ!")

elif choice == "Tool 2: แบบสอบถามการปฏิบัติหน้างาน":
    st.header("📊 Tool 2")
    with st.form("form_t2"):
        q2_1 = st.select_slider("ได้รับค่าจ้างตรงเวลา?", options=[1,2,3,4,5], value=3)
        if st.form_submit_button("ส่งข้อมูล"):
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([now, "Tool 2", q2_1])
                st.success("✅ บันทึกสำเร็จ!")

elif choice == "Tool 5: การประเมินนัยสำคัญ (Heat Map)":
    st.header("⚖️ Tool 5: Heat Map")
    issue = st.text_input("ชื่อประเด็น:", "ความปลอดภัย")
    s = st.slider("Severity", 1, 5, 3)
    l = st.slider("Likelihood", 1, 5, 2)
    score = s * l
    if st.button("บันทึกค่า Heat Map"):
        sheet = connect_to_sheet()
        if sheet:
            sheet.append_row([now, "Tool 5", issue, score])
            st.success("✅ บันทึกสำเร็จ!")

else:
    st.write(f"เลือก {choice} เพื่อดำเนินการ")

st.markdown("<br><hr><p style='text-align: center;'>© 2024 Betagro Group</p>", unsafe_allow_html=True)
