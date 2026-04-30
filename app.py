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

# --- 2. CONNECT ENGINE (แก้ไขใหม่ทั้งหมดเพื่อให้เชื่อมต่อสำเร็จ) ---
def connect_to_sheet():
    try:
        # ดึงข้อมูลจาก st.secrets
        if "gcp_service_account" not in st.secrets:
            st.error("❌ ไม่พบข้อมูล 'gcp_service_account' ใน Secrets กรุณาตรวจสอบการตั้งค่า")
            return None
            
        creds_info = st.secrets["gcp_service_account"]
        
        # จัดรูปแบบ Private Key ให้ถูกต้อง (รองรับทั้งแบบ \n และบรรทัดจริง)
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
        
        # เชื่อมต่อผ่าน URL ของคุณ
        sheet_url = "https://docs.google.com/spreadsheets/d/1YUkrlk_RlvskDluFoAdTQ7KRYRxYhi8ZqNdw13X7JxY/edit"
        sheet = client.open_by_url(sheet_url).get_worksheet(0)
        return sheet
    except Exception as e:
        st.error(f"❌ การเชื่อมต่อล้มเหลว: {str(e)}")
        return None

# --- 3. THE PREMIUM STYLING (รวม Heat Map CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Sarabun', sans-serif; }
    .stApp { background-color: #F4F7F5; }
    [data-testid="stSidebar"] { background-color: #1E3F26 !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    .main-header {
        background-color: white; padding: 40px; border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08); border-top: 10px solid #F9A818;
        text-align: center; margin-bottom: 30px;
    }
    h1 { color: #1E3F26; font-weight: 800; }
    h2 { color: #265F36; border-left: 10px solid #F9A818; padding-left: 15px; }
    .heat-table { width: 100%; border-collapse: separate; border-spacing: 4px; }
    .heat-cell { 
        height: 50px; width: 50px; text-align: center; 
        font-weight: bold; color: white; border-radius: 5px; font-size: 0.9rem;
    }
    .label-cell { color: #555; font-size: 0.8rem; text-align: center; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://www.betagro.com/wp-content/themes/betagro/assets/img/logo-en.png", width=180)
    choice = st.radio("📋 เมนูเครื่องมือ:", [
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
    st.markdown('<div class="main-header"><h1>Tool 1: แบบประเมินสถานะองค์กร</h1></div>', unsafe_allow_html=True)
    with st.form("form_t1"):
        st.subheader("หมวด A: นโยบายและการกำกับดูแล")
        q1_1 = st.radio("1.1 องค์กรมี 'นโยบายสิทธิมนุษยชน' เป็นลายลักษณ์อักษรหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_2 = st.radio("1.2 นโยบายครอบคลุมประเด็นสำคัญ (แรงงาน, ชุมชน, สิ่งแวดล้อม) หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_3 = st.radio("1.3 มีการสื่อสารนโยบายในภาษาที่พนักงานเข้าใจหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_4 = st.radio("1.4 มีการแต่งตั้งผู้รับผิดชอบระดับบริหารหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        st.subheader("หมวด B: การประเมินความเสี่ยง")
        q2_1 = st.radio("2.1 มีการประเมินความเสี่ยง (HRA) ประจำปีหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q2_2 = st.radio("2.2 มีระบบการตรวจสอบย้อนกลับในห่วงโซ่อุปทานหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q2_3 = st.radio("2.3 มีแผนจัดการความเสี่ยง (Mitigation Plan) หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        st.subheader("หมวด C: กลไกร้องเรียน")
        q3_1 = st.radio("3.1 มีช่องทางรับเรื่องร้องเรียนที่ปลอดภัยหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q3_2 = st.radio("3.2 มีมาตรการคุ้มครองผู้แจ้งเบาะแสหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q3_3 = st.radio("3.3 มีขั้นตอนการเยียวยา (Remediation) หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        
        if st.form_submit_button("บันทึกข้อมูล Tool 1"):
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([now, "Tool 1", q1_1, q1_2, q1_3, q1_4, q2_1, q2_2, q2_3, q3_1, q3_2, q3_3])
                st.success("✅ บันทึกสำเร็จ!")

elif choice == "Tool 2: แบบสอบถามการปฏิบัติหน้างาน":
    st.markdown('<div class="main-header"><h1>Tool 2: แบบสอบถามการปฏิบัติหน้างาน</h1></div>', unsafe_allow_html=True)
    with st.form("form_t2"):
        q2_1 = st.select_slider("1.1 ท่านได้รับค่าจ้างตรงเวลาหรือไม่?", options=[1,2,3,4,5], value=3)
        q2_2 = st.select_slider("1.2 ท่านได้รับวันหยุดตามกฎหมายหรือไม่?", options=[1,2,3,4,5], value=3)
        q2_3 = st.select_slider("1.3 ท่านเก็บเอกสารประจำตัวไว้กับตัวหรือไม่?", options=[1,2,3,4,5], value=3)
        q3_1 = st.select_slider("2.1 อุปกรณ์ PPE เพียงพอหรือไม่?", options=[1,2,3,4,5], value=3)
        q3_2 = st.select_slider("2.2 ได้รับการอบรมก่อนเริ่มงานหรือไม่?", options=[1,2,3,4,5], value=3)
        q4_1 = st.select_slider("3.1 หัวหน้างานปฏิบัติอย่างเท่าเทียมหรือไม่?", options=[1,2,3,4,5], value=3)
        if st.form_submit_button("ส่งข้อมูล Tool 2"):
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([now, "Tool 2", q2_1, q2_2, q2_3, q3_1, q3_2, q4_1])
                st.success("✅ ส่งข้อมูลสำเร็จ!")

elif choice == "Tool 5: การประเมินนัยสำคัญ (Heat Map)":
    st.markdown('<div class="main-header"><h1>Human Rights Risk Heat Map</h1></div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.2])
    with col1:
        issue = st.text_input("ชื่อประเด็นความเสี่ยง:", "ความปลอดภัยแรงงาน")
        s1 = st.slider("ความรุนแรง (Severity)", 1, 5, 3)
        l1 = st.slider("โอกาสเกิด (Likelihood)", 1, 5, 2)
        score = s1 * l1
        
    with col2:
        # ฟังก์ชันวาด Heat Map ไล่สี
        def draw_map(cur_s, cur_l):
            html = "<table class='heat-table'>"
            for l in range(5, 0, -1):
                html += "<tr>"
                html += f"<td class='label-cell'>{l}</td>"
                for s in range(1, 6):
                    val = s * l
                    color = "#EF4444" if val >= 16 else ("#F9A818" if val >= 8 else "#265F36")
                    mark = "★" if s == cur_s and l == cur_l else ""
                    html += f"<td class='heat-cell' style='background-color:{color};'>{mark}</td>"
                html += "</tr>"
            html += "<tr><td></td>" + "".join([f"<td class='label-cell'>{i}</td>" for i in range(1,6)]) + "</tr></table>"
            return html
        st.markdown(draw_map(s1, l1), unsafe_allow_html=True)
        
    if st.button("💾 บันทึกค่า Heat Map"):
        sheet = connect_to_sheet()
        if sheet:
            sheet.append_row([now, "Tool 5", issue, s1, l1, score])
            st.success(f"บันทึกประเด็น '{issue}' เรียบร้อย")

# (หมายเหตุ: Tool 3, 4, 6 ใส่โค้ดแบบเดียวกันกับที่เคยส่งให้ก่อนหน้าเพื่อความครบถ้วน)
