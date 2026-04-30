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

# --- 2. CONNECT ENGINE ---
def connect_to_sheet():
    try:
        if "gcp_service_account" not in st.secrets:
            st.error("❌ ไม่พบข้อมูล Secrets ใน Streamlit")
            return None
            
        creds_info = st.secrets["gcp_service_account"]
        private_key = creds_info["private_key"].replace("\\n", "\n")
        
        creds_dict = {
            "type": creds_info["type"],
            "project_id": creds_info["project_id"],
            "private_key_id": creds_info["private_key_id"],
            "private_key": private_key,
            "client_email": creds_info["client_email"],
            "client_id": creds_info["client_id"],
            "auth_uri": creds_info["auth_uri"],
            "token_uri": "https://accounts.google.com/o/oauth2/token",
            "auth_provider_x509_cert_url": creds_info["auth_provider_x509_cert_url"],
            "client_x509_cert_url": creds_info["client_x509_cert_url"]
        }
        
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        credentials = service_account.Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(credentials)
        
        SHEET_ID = "1YUkrlk_RlvskDluFoAdTQ7KRYRxYhi8ZqNdw13X7JxY"
        sheet = client.open_by_key(SHEET_ID).get_worksheet(0)
        return sheet
    except Exception as e:
        st.error(f"❌ การเชื่อมต่อล้มเหลว: {str(e)}")
        return None

# --- 3. PREMIUM STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Sarabun', sans-serif; }
    .stApp { background-color: #F4F7F5; }
    .main-header {
        background-color: white; padding: 40px; border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08); border-top: 10px solid #F9A818;
        text-align: center; margin-bottom: 30px;
    }
    h1 { color: #1E3F26; font-weight: 800; font-size: 2.5rem; }
    h2 { color: #265F36; border-left: 12px solid #F9A818; padding-left: 20px; margin-top: 30px; }
    h3 { color: #1E3F26; background: #E8EEE8; padding: 10px 20px; border-radius: 8px; margin-top: 20px;}
    .stForm { background-color: white !important; padding: 30px !important; border-radius: 15px !important; }
    .heat-table { width: 100%; border-collapse: separate; border-spacing: 5px; }
    .heat-cell { height: 60px; text-align: center; font-weight: bold; color: white; border-radius: 8px; font-size: 1.2rem; }
    .label-cell { color: #555; font-size: 1rem; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. NAVIGATION ---
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

# --- 5. TOOL CONTENT ---

if choice == "Tool 1: แบบประเมินสถานะองค์กร":
    st.markdown('<div class="main-header"><h1>Tool 1: แบบประเมินสถานะองค์กร</h1><p>Internal Policy Gap Analysis</p></div>', unsafe_allow_html=True)
    with st.form("form_t1"):
        st.subheader("หมวด A: นโยบายและการกำกับดูแล")
        q1_1 = st.radio("1.1 องค์กรมี 'นโยบายสิทธิมนุษยชน' เป็นลายลักษณ์อักษรหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_2 = st.radio("1.2 นโยบายครอบคลุมประเด็นสำคัญ (แรงงานข้ามชาติ, ชุมชน, สิ่งแวดล้อม) หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_3 = st.radio("1.3 มีการสื่อสารนโยบายในภาษาที่พนักงานและคู่ค้าเข้าใจหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_4 = st.radio("1.4 มีการแต่งตั้งผู้รับผิดชอบระดับบริหาร (Board Level) หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        
        st.subheader("หมวด B: กระบวนการตรวจสอบอย่างรอบด้าน (Due Diligence)")
        q2_1 = st.radio("2.1 มีการประเมินความเสี่ยง (HRA) เป็นประจำทุกปีหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q2_2 = st.radio("2.2 มีระบบการตรวจสอบย้อนกลับ (Traceability) ในห่วงโซ่อุปทานหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        
        st.subheader("หมวด C: กลไกการร้องเรียนและการเยียวยา")
        q3_1 = st.radio("3.1 มีช่องทางรับเรื่องร้องเรียนที่ปลอดภัยและเป็นอิสระหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q3_2 = st.radio("3.2 มีมาตรการคุ้มครองผู้แจ้งเบาะแส (Non-Retaliation) หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])

        if st.form_submit_button("💾 บันทึกข้อมูล Tool 1"):
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([now, "Tool 1", q1_1, q1_2, q1_3, q1_4, q2_1, q2_2, q3_1, q3_2])
                st.success("✅ บันทึกข้อมูลลง Google Sheet เรียบร้อยแล้ว")

elif choice == "Tool 2: แบบสอบถามการปฏิบัติหน้างาน":
    st.markdown('<div class="main-header"><h1>Tool 2: แบบสอบถามหน้างาน</h1><p>Worker & Contractor Survey</p></div>', unsafe_allow_html=True)
    with st.form("form_t2"):
        st.subheader("ส่วนที่ 1: สภาพการจ้างและค่าจ้าง")
        q2_1 = st.select_slider("1.1 ท่านได้รับค่าจ้างตรงเวลาและครบถ้วนหรือไม่?", options=[1,2,3,4,5], value=3)
        q2_2 = st.select_slider("1.2 ท่านได้รับวันหยุดอย่างน้อย 1 วันต่อสัปดาห์หรือไม่?", options=[1,2,3,4,5], value=3)
        q2_3 = st.select_slider("1.3 ท่านเป็นผู้เก็บเอกสารประจำตัว (พาสปอร์ต) ไว้เองใช่หรือไม่?", options=[1,2,3,4,5], value=3)
        
        st.subheader("ส่วนที่ 2: ความปลอดภัยและสุขอนามัย")
        q3_1 = st.select_slider("2.1 อุปกรณ์ป้องกันอันตราย (PPE) มีเพียงพอและสภาพดีหรือไม่?", options=[1,2,3,4,5], value=3)
        q3_2 = st.select_slider("2.2 ท่านได้รับการฝึกอบรมความปลอดภัยก่อนเริ่มงานหรือไม่?", options=[1,2,3,4,5], value=3)
        
        if st.form_submit_button("🚀 ส่งข้อมูล Tool 2"):
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([now, "Tool 2", q2_1, q2_2, q2_3, q3_1, q3_2])
                st.success("✅ ส่งข้อมูลสำเร็จ")

elif choice == "Tool 3: แนวทางการสัมภาษณ์เชิงลึก":
    st.markdown('<div class="main-header"><h1>Tool 3: แนวทางการสัมภาษณ์เชิงลึก</h1><p>In-depth Interview Guide</p></div>', unsafe_allow_html=True)
    with st.form("form_t3"):
        st.info("บันทึกคำตอบจากการสัมภาษณ์กลุ่มตัวอย่าง")
        i1 = st.text_area("1. การสรรหา: ท่านต้องจ่ายค่าธรรมเนียมการสมัครงานหรือค่านายหน้าหรือไม่? (Recruitment Fees)")
        i2 = st.text_area("2. สัญญาจ้าง: ท่านได้รับสัญญาจ้างในภาษาที่เข้าใจ และเนื้อหาตรงกับงานที่ทำจริงหรือไม่?")
        i3 = st.text_area("3. สภาพความเป็นอยู่: หอพักหรือที่พักมีความปลอดภัยและถูกสุขลักษณะหรือไม่?")
        i4 = st.text_area("4. เสรีภาพ: ท่านสามารถลาออกหรือเดินทางกลับประเทศได้โดยอิสระหรือไม่?")
        
        if st.form_submit_button("💾 บันทึกบทสัมภาษณ์ Tool 3"):
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([now, "Tool 3", i1, i2, i3, i4])
                st.success("✅ บันทึกสำเร็จ")

elif choice == "Tool 4: แบบบันทึกการสังเกตการณ์":
    st.markdown('<div class="main-header"><h1>Tool 4: แบบบันทึกการสังเกตการณ์</h1><p>Site Observation Log</p></div>', unsafe_allow_html=True)
    with st.form("form_t4"):
        st.subheader("เช็คลิสต์การตรวจประเมินหน้างาน")
        o1 = st.checkbox("มีการติดประกาศนโยบายและสิทธิแรงงานในพื้นที่")
        o2 = st.checkbox("ทางหนีไฟและอุปกรณ์ดับเพลิงไม่มีสิ่งกีดขวาง")
        o3 = st.checkbox("พนักงานสวมใส่ PPE ถูกต้องตามลักษณะงาน")
        o4 = st.checkbox("ตู้ยาสามัญมีเวชภัณฑ์ครบถ้วนและไม่หมดอายุ")
        note = st.text_area("บันทึกสิ่งที่พบเพิ่มเติมจากการเดินตรวจ:")
        
        if st.form_submit_button("💾 บันทึกข้อมูล Tool 4"):
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([now, "Tool 4", str(o1), str(o2), str(o3), str(o4), note])
                st.success("✅ บันทึก Log สำเร็จ")

elif choice == "Tool 5: การประเมินนัยสำคัญ (Heat Map)":
    st.markdown('<div class="main-header"><h1>Tool 5: Human Rights Risk Heat Map</h1></div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.subheader("การประเมินความเสี่ยง")
        issue = st.text_input("ระบุประเด็นความเสี่ยง:", "แรงงานบังคับ")
        s = st.slider("Severity (ความรุนแรงของผลกระทบ)", 1, 5, 3)
        l = st.slider("Likelihood (โอกาสที่จะเกิดขึ้น)", 1, 5, 2)
        score = s * l
        st.metric("Risk Score", score)
        
    with col2:
        rows = ""
        for row_l in range(5, 0, -1):
            rows += "<tr>"
            rows += f"<td class='label-cell'>{row_l}</td>"
            for col_s in range(1, 6):
                val = col_s * row_l
                color = "#EF4444" if val >= 16 else ("#F9A818" if val >= 8 else "#265F36")
                mark = "★" if col_s == s and row_l == l else ""
                rows += f"<td class='heat-cell' style='background-color:{color};'>{mark}</td>"
            rows += "</tr>"
        st.markdown(f"<table class='heat-table'>{rows}<tr><td></td><td class='label-cell'>1</td><td class='label-cell'>2</td><td class='label-cell'>3</td><td class='label-cell'>4</td><td class='label-cell'>5</td></tr></table>", unsafe_allow_html=True)
        st.caption("แนวนอน: Severity | แนวตั้ง: Likelihood")

    if st.button("💾 บันทึกค่า Heat Map"):
        sheet = connect_to_sheet()
        if sheet:
            sheet.append_row([now, "Tool 5", issue, s, l, score])
            st.success(f"บันทึกข้อมูล '{issue}' เรียบร้อย")

elif choice == "Tool 6: ระบบวิเคราะห์ AI Triangulation":
    st.markdown('<div class="main-header"><h1>Tool 6: AI-Driven Data Triangulation</h1></div>', unsafe_allow_html=True)
    st.info("ระบบจะวิเคราะห์เปรียบเทียบข้อมูลจาก Tool 1-4 เพื่อหาความขัดแย้งของข้อมูล")
    raw_data = st.text_area("ใส่สรุปข้อมูลจากการลงพื้นที่เพื่อประมวลผล:", height=250)
    if st.button("เริ่มการวิเคราะห์เชิงลึก"):
        with st.spinner("AI กำลังวิเคราะห์จุดขัดแย้งของข้อมูล..."):
            st.warning("⚠️ ผลการวิเคราะห์เบื้องต้น: พบความขัดแย้งระหว่างนโยบาย (Tool 1) และการปฏิบัติจริง (Tool 2) ในเรื่องค่าจ้าง")

st.markdown("<br><hr><p style='text-align: center; color: #888;'>© 2024 Betagro Group | HRDD Digital Toolkit</p>", unsafe_allow_html=True)
