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

# --- 2. เครื่องยนต์เชื่อมต่อ Google Sheet (แก้ไขส่วนการอ่าน Key) ---
def connect_to_sheet():
    try:
        # ดึงข้อมูลจาก Secrets (ดึงมาทั้งก้อน)
        creds_info = dict(st.secrets) 
        
        # แก้ไขปัญหาเรื่อง Private Key (ล้างค่า \\n ที่เกินมาออก)
        if "private_key" in creds_info:
            creds_info["private_key"] = creds_info["private_key"].replace("\\\\n", "\n").replace("\\n", "\n")
            
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        credentials = service_account.Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(credentials)
        
        sheet_url = "https://docs.google.com/spreadsheets/d/1YUkrlk_RlvskDluFoAdTQ7KRYRxYhi8ZqNdw13X7JxY/edit"
        sheet = client.open_by_url(sheet_url).get_worksheet(0)
        
        # ถ้าชีตว่าง ให้ใส่หัวตาราง
        if not sheet.get_all_values():
            headers = ["Timestamp", "Tool_Name", "Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q9", "Score/Note"]
            sheet.append_row(headers)
        return sheet
    except Exception as e:
        st.error(f"⚠️ การเชื่อมต่อล้มเหลว: {str(e)}")
        return None

# --- 3. THE PREMIUM STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Sarabun', sans-serif; }
    .stApp { background-color: #F4F7F5; }
    [data-testid="stSidebar"] { background-color: #1E3F26 !important; border-right: 5px solid #F9A818; min-width: 320px !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    .main-header {
        background-color: white; padding: 40px; border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08); border-top: 10px solid #F9A818;
        text-align: center; margin-bottom: 30px;
    }
    h1 { color: #1E3F26; font-weight: 800; font-size: 2.8rem; margin: 0; }
    h2 { color: #265F36; border-left: 12px solid #F9A818; padding-left: 20px; margin-top: 35px; }
    .stForm { background-color: white !important; padding: 30px !important; border-radius: 15px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. MAIN HEADER ---
st.markdown('<div class="main-header"><h1>BETAGRO HRDD DIGITAL TOOLKIT</h1></div>', unsafe_allow_html=True)

# --- 5. SIDEBAR ---
with st.sidebar:
    st.image("https://www.betagro.com/wp-content/themes/betagro/assets/img/logo-en.png", width=180)
    choice = st.radio("📋 เลือกเครื่องมือประเมิน:", [
        "Tool 1: แบบประเมินสถานะองค์กร", 
        "Tool 2: แบบสอบถามการปฏิบัติหน้างาน", 
        "Tool 3: แนวทางการสัมภาษณ์เชิงลึก", 
        "Tool 4: แบบบันทึกการสังเกตการณ์",
        "Tool 5: การประเมินนัยสำคัญ (Heat Map)",
        "Tool 6: ระบบวิเคราะห์ AI Triangulation"
    ])

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- 6. TOOL CONTENT (เนื้อหาครบตาม app.py เดิมของพี่) ---

if choice == "Tool 1: แบบประเมินสถานะองค์กร":
    st.header("🏢 Tool 1: แบบประเมินสถานะองค์กร")
    with st.form("form_t1"):
        st.subheader("หมวด A: การกำกับดูแลและนโยบาย")
        q1_1 = st.radio("1.1 องค์กรมี 'นโยบายสิทธิมนุษยชน' ที่เป็นลายลักษณ์อักษรหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_2 = st.radio("1.2 นโยบายครอบคลุมประเด็นสำคัญหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_3 = st.radio("1.3 มีการสื่อสารนโยบายในภาษาที่เข้าใจหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_4 = st.radio("1.4 มีการแต่งตั้งผู้รับผิดชอบระดับบริหารหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        st.subheader("หมวด B: กระบวนการตรวจสอบอย่างรอบด้าน")
        q2_1 = st.radio("2.1 มีการประเมินความเสี่ยง (HRA) เป็นประจำหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q2_2 = st.radio("2.2 มีระบบการตรวจสอบย้อนกลับหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q2_3 = st.radio("2.3 มีแผนการจัดการความเสี่ยงหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        st.subheader("หมวด C: กลไกการร้องเรียน")
        q3_1 = st.radio("3.1 มีช่องทางรับเรื่องร้องเรียนที่ปลอดภัยหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q3_2 = st.radio("3.2 มีมาตรการคุ้มครองผู้แจ้งเบาะแสหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q3_3 = st.radio("3.3 มีขั้นตอนการเยียวยาหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        
        if st.form_submit_button("บันทึกข้อมูล Tool 1"):
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([now, "Tool 1", q1_1, q1_2, q1_3, q1_4, q2_1, q2_2, q2_3, q3_1, q3_2, q3_3])
                st.success("✅ บันทึกสำเร็จ!")
                st.balloons()

elif choice == "Tool 2: แบบสอบถามการปฏิบัติหน้างาน":
    st.header("📊 Tool 2: แบบสอบถามการปฏิบัติหน้างาน")
    with st.form("form_t2"):
        q2_1 = st.select_slider("1.1 ได้รับค่าจ้างตรงเวลา?", options=[1,2,3,4,5], value=3)
        q2_2 = st.select_slider("1.2 ได้รับวันหยุดตามกฎหมาย?", options=[1,2,3,4,5], value=3)
        q2_3 = st.select_slider("1.3 เก็บสัญญาจ้างไว้กับตัว?", options=[1,2,3,4,5], value=3)
        if st.form_submit_button("ส่งผลแบบสำรวจ"):
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([now, "Tool 2", q2_1, q2_2, q2_3])
                st.success("✅ บันทึกสำเร็จ!")

elif choice == "Tool 3: แนวทางการสัมภาษณ์เชิงลึก":
    st.header("🎙️ Tool 3: แนวทางการสัมภาษณ์เชิงลึก")
    with st.form("form_t3"):
        i1 = st.text_area("บันทึกบทสัมภาษณ์:")
        if st.form_submit_button("บันทึกบทสัมภาษณ์"):
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([now, "Tool 3", i1])
                st.success("✅ บันทึกสำเร็จ")

elif choice == "Tool 4: แบบบันทึกการสังเกตการณ์":
    st.header("🔎 Tool 4: แบบบันทึกการสังเกตการณ์")
    with st.form("form_t4"):
        o1 = st.checkbox("มีป้ายนโยบายชัดเจน")
        note = st.text_area("บันทึกเพิ่มเติม:")
        if st.form_submit_button("บันทึก Log"):
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([now, "Tool 4", str(o1), note])
                st.success("✅ บันทึกสำเร็จ")

elif choice == "Tool 5: การประเมินนัยสำคัญ (Heat Map)":
    st.header("⚖️ Tool 5: Salient Human Rights Risks")
    issue = st.text_input("ชื่อประเด็น:", "ความปลอดภัย")
    s = st.slider("Severity", 1, 5, 3)
    l = st.slider("Likelihood", 1, 5, 2)
    score = s * l
    st.metric("SALIENCE SCORE", score)
    if st.button("บันทึกค่า Heat Map"):
        sheet = connect_to_sheet()
        if sheet:
            sheet.append_row([now, "Tool 5", issue, score])
            st.success("✅ บันทึกสำเร็จ!")
            st.balloons()

elif choice == "Tool 6: ระบบวิเคราะห์ AI Triangulation":
    st.header("🤖 Tool 6: AI Analysis")
    st.info("ส่วนนี้เตรียมไว้สำหรับเชื่อมต่อ API ในอนาคต")

st.markdown("<br><hr><p style='text-align: center; color: #888;'>© 2024 Betagro Group</p>", unsafe_allow_html=True)
