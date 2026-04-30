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

# --- 2. เครื่องยนต์เชื่อมต่อ Google Sheet ---
def connect_to_sheet():
    try:
        creds_dict = st.secrets["gcp_service_account"]
        
        # จัดการเรื่อง private_key ให้รองรับการขึ้นบรรทัดใหม่ที่ถูกต้อง
        if "private_key" in creds_dict:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        credentials = service_account.Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(credentials)
        
        # ลิงก์ Google Sheet ของพี่
        sheet_url = "https://docs.google.com/spreadsheets/d/1YUkrlk_RlvskDluFoAdTQ7KRYRxYhi8ZqNdw13X7JxY/edit"
        sheet = client.open_by_url(sheet_url).get_worksheet(0)
        
        # ถ้าชีตว่าง ให้ใส่หัวตารางอัตโนมัติ
        if not sheet.get_all_values():
            headers = ["Timestamp", "Tool", "Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q9", "Score/Note"]
            sheet.append_row(headers)
            
        return sheet
    except Exception as e:
        st.error(f"⚠️ การเชื่อมต่อล้มเหลว: {e}")
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
    st.info("Version: 3.5 (Stable Connection)")

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- 6. TOOL CONTENT ---

if choice == "Tool 1: แบบประเมินสถานะองค์กร":
    st.header("🏢 Tool 1: แบบประเมินสถานะองค์กร (Internal Policy Gap Analysis)")
    with st.form("form_t1"):
        st.subheader("หมวด A: การกำกับดูแลและนโยบาย")
        q1_1 = st.radio("1.1 องค์กรมี 'นโยบายสิทธิมนุษยชน' ที่เป็นลายลักษณ์อักษรหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_2 = st.radio("1.2 นโยบายครอบคลุมประเด็นสำคัญหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_3 = st.radio("1.3 มีการสื่อสารนโยบายในภาษาที่เข้าใจหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_4 = st.radio("1.4 มีการแต่งตั้งผู้รับผิดชอบระดับบริหารหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        
        if st.form_submit_button("บันทึกข้อมูล Tool 1"):
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([now, "Tool 1", q1_1, q1_2, q1_3, q1_4])
                st.success("บันทึกข้อมูลเรียบร้อย")
                st.balloons()

elif choice == "Tool 2: แบบสอบถามการปฏิบัติหน้างาน":
    st.header("📊 Tool 2: แบบสอบถามการปฏิบัติ (Worker & Contractor Survey)")
    with st.form("form_t2"):
        q2_1 = st.select_slider("1.1 ได้รับค่าจ้างตรงเวลาหรือไม่?", options=[1,2,3,4,5], value=3)
        q2_2 = st.select_slider("1.2 ได้รับวันหยุดตามกฎหมายหรือไม่?", options=[1,2,3,4,5], value=3)
        
        if st.form_submit_button("ส่งผลแบบสำรวจ"):
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([now, "Tool 2", q2_1, q2_2])
                st.success("ส่งข้อมูลสำเร็จ!")
                st.balloons()

elif choice == "Tool 3: แนวทางการสัมภาษณ์เชิงลึก":
    st.header("🎙️ Tool 3: แนวทางการสัมภาษณ์ (In-depth Interview Guide)")
    with st.form("form_t3"):
        i1 = st.text_area("1. บันทึกรายละเอียดการสัมภาษณ์:")
        if st.form_submit_button("บันทึกบทสัมภาษณ์"):
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([now, "Tool 3", i1])
                st.success("บันทึกสำเร็จ")

elif choice == "Tool 4: แบบบันทึกการสังเกตการณ์":
    st.header("🔎 Tool 4: แบบบันทึกการสังเกตการณ์ภาคสนาม (Observation Log)")
    with st.form("form_t4"):
        o1 = st.checkbox("มีป้ายนโยบายชัดเจน")
        note = st.text_area("บันทึกเพิ่มเติม:")
        if st.form_submit_button("บันทึก Log"):
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([now, "Tool 4", str(o1), note])
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
            sheet.append_row([now, "Tool 5", issue, score])
            st.success(f"✅ บันทึกประเด็น '{issue}' สำเร็จ!")
            st.balloons()

elif choice == "Tool 6: ระบบวิเคราะห์ AI Triangulation":
    st.header("🤖 Tool 6: AI-Driven Data Triangulation")
    st.info("ส่วนนี้เตรียมไว้สำหรับการวิเคราะห์ข้อมูลเชิงลึกผ่าน AI")
    raw_data = st.text_area("กรอกข้อมูลดิบเพื่อประมวลผล:", height=200)
    if st.button("เริ่มการวิเคราะห์เชิงลึก"):
        st.warning("ระบบ AI กำลังอยู่ในช่วงพัฒนาการเชื่อมต่อ API")

# --- 7. FOOTER ---
st.markdown("<br><hr><p style='text-align: center; color: #888;'>© 2024 Betagro Group | Sustainability Department (HRDD Division)</p>", unsafe_allow_html=True)
