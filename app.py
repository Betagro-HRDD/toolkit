import streamlit as st
import pandas as pd
from google.oauth2 import service_account
import gspread
from datetime import datetime
import time

# --- 1. SETTING UP THE PAGE ---
st.set_page_config(
    page_title="Betagro HRDD Premium Toolkit",
    page_icon="https://www.betagro.com/favicon.ico",
    layout="wide"
)

# --- 2. เครื่องยนต์เชื่อมต่อ Google Sheet (แก้ไขเรื่อง DNS และ Private Key Format) ---
def connect_to_sheet():
    # ลองเชื่อมต่อสูงสุด 3 ครั้งเพื่อข้ามปัญหาชั่วคราวของ Network
    for attempt in range(3):
        try:
            # ดึงข้อมูลจาก Secrets ภายใต้หัวข้อ [gcp_service_account]
            if "gcp_service_account" in st.secrets:
                creds_info = dict(st.secrets["gcp_service_account"])
            else:
                creds_info = dict(st.secrets)
            
            # ล้างค่า \n ในรหัส private_key ให้ถูกต้อง (จุดที่ทำให้เชื่อมต่อไม่ได้)
            if "private_key" in creds_info:
                creds_info["private_key"] = creds_info["private_key"].replace("\\\\n", "\n").replace("\\n", "\n")
            
            # ปรับเปลี่ยน Token URI เป็น Domain หลักที่เสถียรกว่า (แก้ NameResolutionError)
            creds_info["token_uri"] = "https://accounts.google.com/o/oauth2/token"
            
            scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
            credentials = service_account.Credentials.from_service_account_info(creds_info, scopes=scope)
            client = gspread.authorize(credentials)
            
            # เชื่อมต่อกับ Sheet ของพี่
            sheet_url = "https://docs.google.com/spreadsheets/d/1YUkrlk_RlvskDluFoAdTQ7KRYRxYhi8ZqNdw13X7JxY/edit"
            sheet = client.open_by_url(sheet_url).get_worksheet(0)
            
            # ใส่หัวตารางถ้าชีตว่าง
            if not sheet.get_all_values():
                headers = ["Timestamp", "Tool", "Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Note/Score"]
                sheet.append_row(headers)
            return sheet
        except Exception as e:
            if attempt < 2:
                time.sleep(2)
                continue
            st.error(f"⚠️ การเชื่อมต่อล้มเหลว: {str(e)}")
            return None

# --- 3. PREMIUM STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Sarabun', sans-serif; }
    .stApp { background-color: #F4F7F5; }
    [data-testid="stSidebar"] { background-color: #1E3F26 !important; border-right: 5px solid #F9A818; }
    [data-testid="stSidebar"] * { color: white !important; }
    .main-header {
        background-color: white; padding: 40px; border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08); border-top: 10px solid #F9A818;
        text-align: center; margin-bottom: 30px;
    }
    h1 { color: #1E3F26; font-weight: 800; font-size: 2.8rem; margin: 0; }
    h2 { color: #265F36; border-left: 12px solid #F9A818; padding-left: 20px; margin-top: 35px; }
    h3 { color: #1E3F26; background: #E8EEE8; padding: 10px 20px; border-radius: 8px; }
    .stForm { background-color: white !important; padding: 30px !important; border-radius: 15px !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>BETAGRO HRDD DIGITAL TOOLKIT</h1></div>', unsafe_allow_html=True)

# --- 4. SIDEBAR ---
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

# --- 5. TOOL CONTENT (คืนเนื้อหาครบ 100% ตามต้นฉบับของพี่) ---

if choice == "Tool 1: แบบประเมินสถานะองค์กร":
    st.header("🏢 Tool 1: แบบประเมินสถานะองค์กร (Internal Policy Gap Analysis)")
    with st.form("form_t1"):
        st.subheader("หมวด A: การกำกับดูแลและนโยบาย")
        q1_1 = st.radio("1.1 องค์กรมี 'นโยบายสิทธิมนุษยชน' ที่เป็นลายลักษณ์อักษรหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_2 = st.radio("1.2 นโยบายครอบคลุมประเด็นสำคัญหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_3 = st.radio("1.3 มีการสื่อสารนโยบายในภาษาที่เข้าใจหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_4 = st.radio("1.4 มีการแต่งตั้งผู้รับผิดชอบในระดับบริหารหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        st.subheader("หมวด B: กระบวนการตรวจสอบอย่างรอบด้าน")
        q2_1 = st.radio("2.1 มีการประเมินความเสี่ยง (HRA) เป็นประจำหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q2_2 = st.radio("2.2 มีระบบการตรวจสอบย้อนกลับ (Traceability) หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q2_3 = st.radio("2.3 มีแผนการจัดการความเสี่ยง (Mitigation Plan) หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        st.subheader("หมวด C: กลไกการร้องเรียน")
        q3_1 = st.radio("3.1 มีช่องทางรับเรื่องร้องเรียนที่ปลอดภัยหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q3_2 = st.radio("3.2 มีมาตรการคุ้มครองผู้แจ้งเบาะแสหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q3_3 = st.radio("3.3 มีขั้นตอนการเยียวยา (Remediation) หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        if st.form_submit_button("บันทึกข้อมูล Tool 1"):
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([now, "Tool 1", q1_1, q1_2, q1_3, q1_4, q2_1, q2_2, q2_3, q3_1, q3_2, q3_3])
                st.success("✅ บันทึกสำเร็จ!")

elif choice == "Tool 2: แบบสอบถามการปฏิบัติหน้างาน":
    st.header("📊 Tool 2: แบบสอบถามการปฏิบัติหน้างาน (On-site Worker Survey)")
    with st.form("form_t2"):
        st.subheader("ส่วนที่ 1: สภาพการจ้างและค่าจ้าง")
        q2_1 = st.select_slider("1.1 ท่านได้รับค่าจ้างตรงเวลาและครบถ้วนหรือไม่?", options=[1,2,3,4,5], value=3)
        q2_2 = st.select_slider("1.2 ท่านได้รับวันหยุดตามกฎหมายหรือไม่?", options=[1,2,3,4,5], value=3)
        q2_3 = st.select_slider("1.3 ท่านได้เก็บเอกสารประจำตัวและสัญญาจ้างไว้กับตัวหรือไม่?", options=[1,2,3,4,5], value=3)
        st.subheader("ส่วนที่ 2: ความปลอดภัย")
        q3_1 = st.select_slider("2.1 อุปกรณ์ป้องกันอันตราย (PPE) มีเพียงพอหรือไม่?", options=[1,2,3,4,5], value=3)
        q3_2 = st.select_slider("2.2 ท่านได้รับการอบรมด้านความปลอดภัยหรือไม่?", options=[1,2,3,4,5], value=3)
        st.subheader("ส่วนที่ 3: การปฏิบัติต่อแรงงาน")
        q4_1 = st.select_slider("3.1 ท่านได้รับการปฏิบัติอย่างเท่าเทียมหรือไม่?", options=[1,2,3,4,5], value=3)
        q4_2 = st.select_slider("3.2 บรรยากาศการทำงานปราศจากการข่มขู่หรือไม่?", options=[1,2,3,4,5], value=3)
        if st.form_submit_button("ส่งผลแบบสำรวจ Tool 2"):
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([now, "Tool 2", q2_1, q2_2, q2_3, q3_1, q3_2, q4_1, q4_2])
                st.success("✅ บันทึกข้อมูล Tool 2 สำเร็จ!")

elif choice == "Tool 3: แนวทางการสัมภาษณ์เชิงลึก":
    st.header("🎙️ Tool 3: แนวทางการสัมภาษณ์เชิงลึก")
    with st.form("form_t3"):
        i1 = st.text_area("1. ขั้นตอนการสรรหาก่อนเริ่มงาน ท่านมีค่าใช้จ่ายใดๆ หรือไม่?")
        i2 = st.text_area("2. ท่านได้รับข้อมูลสวัสดิการในภาษาที่เข้าใจหรือไม่?")
        i3 = st.text_area("3. สภาพที่พักอาศัยมีความปลอดภัยเพียงพอหรือไม่?")
        i4 = st.text_area("4. หากมีความกังวล ท่านกล้าที่จะใช้ช่องทางร้องเรียนหรือไม่?")
        if st.form_submit_button("บันทึกบทสัมภาษณ์ Tool 3"):
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([now, "Tool 3", i1, i2, i3, i4])
                st.success("✅ บันทึกสำเร็จ")

elif choice == "Tool 4: แบบบันทึกการสังเกตการณ์":
    st.header("🔎 Tool 4: แบบบันทึกการสังเกตการณ์")
    with st.form("form_t4"):
        o1 = st.checkbox("มีการติดป้ายนโยบายและช่องทางร้องเรียนชัดเจน")
        o2 = st.checkbox("พนักงานสวมใส่ PPE ถูกต้อง")
        o3 = st.checkbox("ทางหนีไฟพร้อมใช้งาน")
        o4 = st.checkbox("น้ำดื่มและห้องน้ำสะอาด")
        note = st.text_area("บันทึกเพิ่มเติม:")
        if st.form_submit_button("บันทึก Log Tool 4"):
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([now, "Tool 4", str(o1), str(o2), str(o3), str(o4), note])
                st.success("✅ บันทึกข้อมูลสำเร็จ")

elif choice == "Tool 5: การประเมินนัยสำคัญ (Heat Map)":
    st.header("⚖️ Tool 5: Heat Map Scoring Matrix")
    c1, c2 = st.columns([1, 1.4])
    with c1:
        issue = st.text_input("ชื่อประเด็นความเสี่ยง:", "ความปลอดภัยแรงงาน")
        s1 = st.slider("Scale", 1, 5, 3)
        s2 = st.slider("Scope", 1, 5, 3)
        s3 = st.slider("Remediability", 1, 5, 3)
        sev_max = max(s1, s2, s3)
        likelihood = st.slider("Likelihood", 1, 5, 2)
        score = sev_max * likelihood
        st.metric("SALIENCE SCORE", score)
    with c2:
        def render_heat_map(cur_s, cur_l):
            rows = ""
            for l in range(5, 0, -1):
                rows += "<tr>"
                for s in range(1, 6):
                    val = s * l
                    color = "#EF4444" if val >= 16 else ("#F9A818" if val >= 8 else "#265F36")
                    mark = "★" if s == cur_s and l == cur_l else ""
                    rows += f"<td style='height:50px; width:50px; background-color:{color}; color:white; text-align:center;'>{mark}</td>"
                rows += "</tr>"
            return f"<table>{rows}</table>"
        st.markdown(render_heat_map(sev_max, likelihood), unsafe_allow_html=True)
    if st.button("บันทึกค่า Heat Map"):
        sheet = connect_to_sheet()
        if sheet:
            sheet.append_row([now, "Tool 5", issue, score])
            st.success("✅ บันทึกสำเร็จ!")

elif choice == "Tool 6: ระบบวิเคราะห์ AI Triangulation":
    st.header("🤖 Tool 6: AI-Driven Data Analysis")
    st.info("ระบบกำลังเตรียมการเชื่อมต่อ API เพื่อวิเคราะห์ข้อมูล")

st.markdown("<br><hr><p style='text-align: center;'>© 2024 Betagro Group | HRDD Division</p>", unsafe_allow_html=True)
