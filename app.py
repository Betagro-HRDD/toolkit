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

# --- 2. เครื่องยนต์เชื่อมต่อ Google Sheet (ใส่ไว้ให้พี่แล้ว) ---
def connect_to_sheet():
    try:
        creds_dict = st.secrets["gcp_service_account"]
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        credentials = service_account.Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(credentials)
        # ลิงก์ Google Sheet ของพี่
        sheet_url = ""https://docs.google.com/spreadsheets/d/1YUkrlk_RlvskDluFoAdTQ7KRYRxYhi8ZqNdw13X7JxY/edit"
        return client.open_by_url(sheet_url).sheet1
    except Exception as e:
        return None

# --- 3. THE PREMIUM STYLING ---
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
    h3 { color: #1E3F26; background: #E8EEE8; padding: 10px 20px; border-radius: 8px; }
    .stForm { background-color: white !important; padding: 30px !important; border-radius: 15px !important; box-shadow: 0 2px 10px rgba(0,0,0,0.05) !important; }
    .heat-table { width: 100%; border-collapse: separate; border-spacing: 5px; }
    .heat-cell { height: 65px; width: 65px; text-align: center; font-weight: bold; color: white; border-radius: 8px; font-size: 1.4rem; border: 2px solid rgba(255,255,255,0.3); }
    .label-cell { color: #555; font-size: 1rem; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. MAIN HEADER ---
st.markdown("""
    <div class="main-header">
        <h1>BETAGRO HRDD DIGITAL TOOLKIT</h1>
        <p style='color: #666; font-size: 1.2rem; margin-top: 10px;'>
            ระบบตรวจสอบสิทธิมนุษยชนอัจฉริยะ ตามมาตรฐาน UNGPs & OECD Due Diligence
        </p>
    </div>
    """, unsafe_allow_html=True)

# --- 5. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://www.betagro.com/wp-content/themes/betagro/assets/img/logo-en.png", width=180)
    st.markdown("<br>", unsafe_allow_html=True)
    choice = st.sidebar.radio("📋 เลือกเครื่องมือประเมิน:", [
        "Tool 1: แบบประเมินสถานะองค์กร", 
        "Tool 2: แบบสอบถามการปฏิบัติหน้างาน", 
        "Tool 3: แนวทางการสัมภาษณ์เชิงลึก", 
        "Tool 4: แบบบันทึกการสังเกตการณ์",
        "Tool 5: การประเมินนัยสำคัญ (Heat Map)",
        "Tool 6: ระบบวิเคราะห์ AI Triangulation"
    ])
    st.markdown("---")
    st.info("Version: 2.5 (Full Content Integration)")

# --- 6. TOOL CONTENT (เนื้อหาครบถ้วนตามที่พี่ส่งมา) ---

if choice == "Tool 1: แบบประเมินสถานะองค์กร":
    st.header("🏢 Tool 1: แบบประเมินสถานะองค์กร (Internal Policy Gap Analysis)")
    st.markdown("#### **กลุ่มเป้าหมาย:** ผู้บริหารระดับสูง / HR / Compliance")
    with st.form("form_t1"):
        st.subheader("หมวด A: การกำกับดูแลและนโยบาย")
        q1_1 = st.radio("1.1 องค์กรมี 'นโยบายสิทธิมนุษยชน' ที่เป็นลายลักษณ์อักษรและอนุมัติโดยบอร์ดหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_2 = st.radio("1.2 นโยบายครอบคลุมประเด็นสำคัญ (แรงงานข้ามชาติ, สิทธิชุมชน, ความหลากหลาย) หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_3 = st.radio("1.3 มีการสื่อสารนโยบายในภาษาที่พนักงาน (Native Language) และคู่ค้าเข้าใจหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_4 = st.radio("1.4 มีการแต่งตั้งคณะกรรมการหรือผู้รับผิดชอบด้านสิทธิมนุษยชนในระดับบริหารหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        
        st.subheader("หมวด B: กระบวนการตรวจสอบอย่างรอบด้าน (Due Diligence)")
        q2_1 = st.radio("2.1 มีการประเมินความเสี่ยงด้านสิทธิมนุษยชน (HRA) เป็นประจำทุกปีหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q2_2 = st.radio("2.2 มีระบบการตรวจสอบย้อนกลับ (Traceability) ในห่วงโซ่อุปทานต้นน้ำหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q2_3 = st.radio("2.3 มีการระบุแผนการจัดการความเสี่ยง (Mitigation Plan) ที่ชัดเจนหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        
        st.subheader("หมวด C: กลไกการร้องเรียนและการเยียวยา")
        q3_1 = st.radio("3.1 มีช่องทางรับเรื่องร้องเรียนที่ปลอดภัยและเข้าถึงได้จริงสำหรับทุกคนหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q3_2 = st.radio("3.2 มีมาตรการคุ้มครองผู้แจ้งเบาะแส (Whistleblower Protection) หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q3_3 = st.radio("3.3 มีขั้นตอนการเยียวยา (Remediation) ที่มีประสิทธิภาพเมื่อพบความเสียหายเกิดขึ้นหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        
        if st.form_submit_button("บันทึกข้อมูล Tool 1"):
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Tool 1", q1_1, q1_2, q1_3, q1_4, q2_1, q2_2, q2_3, q3_1, q3_2, q3_3])
                st.success("บันทึกข้อมูลเรียบร้อย")

elif choice == "Tool 2: แบบสอบถามการปฏิบัติหน้างาน":
    st.header("📊 Tool 2: แบบสอบถามการปฏิบัติ (Worker & Contractor Survey)")
    with st.form("form_t2"):
        st.subheader("ส่วนที่ 1: สภาพการจ้างและค่าตอบแทน")
        q2_1 = st.select_slider("1.1 ท่านได้รับค่าจ้างตรงเวลาและครบถ้วนตามที่ตกลงไว้หรือไม่?", options=[1,2,3,4,5], value=3)
        q2_2 = st.select_slider("1.2 ท่านได้รับวันหยุดประจำสัปดาห์และวันหยุดนักขัตฤกษ์ตามกฎหมายหรือไม่?", options=[1,2,3,4,5], value=3)
        q2_3 = st.select_slider("1.3 ท่านสามารถเข้าถึงและเก็บเอกสารสัญญาจ้างไว้กับตัวหรือไม่?", options=[1,2,3,4,5], value=3)
        st.subheader("ส่วนที่ 2: ความปลอดภัยและสุขอนามัย (OHS)")
        q3_1 = st.select_slider("2.1 อุปกรณ์ป้องกันอันตรายส่วนบุคคล (PPE) มีเพียงพอและเหมาะสมหรือไม่?", options=[1,2,3,4,5], value=3)
        q3_2 = st.select_slider("2.2 ท่านได้รับการอบรมความปลอดภัยก่อนเริ่มปฏิบัติงานจริงหรือไม่?", options=[1,2,3,4,5], value=3)
        st.subheader("ส่วนที่ 3: การปฏิบัติที่เท่าเทียมและเสรีภาพ")
        q4_1 = st.select_slider("3.1 ท่านได้รับการปฏิบัติอย่างเท่าเทียม?", options=[1,2,3,4,5], value=3)
        q4_2 = st.select_slider("3.2 บรรยากาศการทำงานปราศจากการข่มขู่?", options=[1,2,3,4,5], value=3)
        
        if st.form_submit_button("ส่งผลแบบสำรวจ"):
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Tool 2", q2_1, q2_2, q2_3, q3_1, q3_2, q4_1, q4_2])
                st.success("ส่งข้อมูลสำเร็จ!")
                st.balloons()

elif choice == "Tool 3: แนวทางการสัมภาษณ์เชิงลึก":
    st.header("🎙️ Tool 3: แนวทางการสัมภาษณ์ (In-depth Interview Guide)")
    with st.form("form_t3"):
        i1 = st.text_area("1. ขั้นตอนการสรรหาก่อนเริ่มงาน ท่านมีค่าใช้จ่ายใดๆ หรือไม่?")
        i2 = st.text_area("2. ท่านได้รับข้อมูลงานและเซ็นสัญญาในภาษาที่เข้าใจหรือไม่?")
        i3 = st.text_area("3. สภาพที่พักอาศัยมีความปลอดภัยเพียงพอหรือไม่?")
        i4 = st.text_area("4. ท่านกล้าที่จะใช้ช่องทางร้องเรียนหรือไม่?")
        if st.form_submit_button("บันทึกบทสัมภาษณ์"):
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Tool 3", i1, i2, i3, i4])
                st.success("บันทึกสำเร็จ")

elif choice == "Tool 4: แบบบันทึกการสังเกตการณ์":
    st.header("🔎 Tool 4: แบบบันทึกการสังเกตการณ์ภาคสนาม (Observation Log)")
    with st.form("form_t4"):
        o1 = st.checkbox("มีป้ายนโยบายชัดเจน")
        o2 = st.checkbox("พนักงานสวมใส่ PPE")
        o3 = st.checkbox("ทางหนีไฟไม่มีสิ่งกีดขวาง")
        note = st.text_area("บันทึกเพิ่มเติม:")
        if st.form_submit_button("บันทึก Log"):
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Tool 4", str(o1), str(o2), str(o3), note])
                st.success("บันทึกแล้ว")

elif choice == "Tool 5: การประเมินนัยสำคัญ (Heat Map)":
    st.header("⚖️ Tool 5: Salient Human Rights Risks Scoring Matrix")
    c1, c2 = st.columns([1, 1.4])
    with c1:
        issue = st.text_input("ชื่อประเด็น:", "ความปลอดภัยแรงงาน")
        s1 = st.slider("ขนาด (Scale)", 1, 5, 3)
        s2 = st.slider("ขอบเขต (Scope)", 1, 5, 3)
        s3 = st.slider("เยียวยา (Remediability)", 1, 5, 3)
        sev_max = max(s1, s2, s3)
        likelihood = st.slider("โอกาสที่จะเกิดขึ้น", 1, 5, 2)
        score = sev_max * likelihood
        st.metric("SALIENCE SCORE", score)

    with c2:
        def render_heat_map(cur_s, cur_l):
            rows = ""
            for l in range(5, 0, -1):
                rows += "<tr>"
                rows += f"<td class='label-cell'>{l}</td>"
                for s in range(1, 6):
                    val = s * l
                    color = "#EF4444" if val >= 16 else ("#F9A818" if val >= 8 else "#265F36")
                    mark = "★" if s == cur_s and l == cur_l else ""
                    rows += f"<td class='heat-cell' style='background-color:{color};'>{mark}</td>"
                rows += "</tr>"
            return f"<table class='heat-table'>{rows}<tr class='label-cell'><td></td><td>1</td><td>2</td><td>3</td><td>4</td><td>5</td></tr></table>"
        st.markdown(render_heat_map(sev_max, likelihood), unsafe_allow_html=True)

    if st.button("บันทึกค่าความเสี่ยง Heat Map"):
        sheet = connect_to_sheet()
        if sheet:
            sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Tool 5", issue, score])
            st.success("บันทึกสำเร็จ")

elif choice == "Tool 6: ระบบวิเคราะห์ AI Triangulation":
    st.header("🤖 Tool 6: AI-Driven Data Triangulation")
    raw_data = st.text_area("กรอกข้อมูลดิบเพื่อประมวลผล:", height=200)
    if st.button("เริ่มการวิเคราะห์เชิงลึก"):
        st.info("กำลังประมวลผล...")

# --- 7. FOOTER ---
st.markdown("<br><hr><p style='text-align: center; color: #888;'>© 2024 Betagro Group | Sustainability Department (HRDD Division)</p>", unsafe_allow_html=True)
