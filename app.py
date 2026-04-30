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

# --- 2. เครื่องยนต์เชื่อมต่อ (แก้ไขโครงสร้างใหม่เพื่อไม่ให้ล้มเหลว) ---
def connect_to_sheet():
    try:
        # ดึงข้อมูลจาก st.secrets
        if "gcp_service_account" not in st.secrets:
            st.error("❌ ไม่พบข้อมูล 'gcp_service_account' ใน Secrets")
            return None
            
        creds_info = st.secrets["gcp_service_account"]
        
        # จัดรูปแบบ Private Key ให้ถูกต้อง (รองรับทั้งการอ่านจาก TOML และรหัสผ่าน)
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
        
        # เชื่อมต่อผ่าน URL ที่คุณระบุ
        sheet_url = "https://docs.google.com/spreadsheets/d/1YUkrlk_RlvskDluFoAdTQ7KRYRxYhi8ZqNdw13X7JxY/edit"
        sheet = client.open_by_url(sheet_url).get_worksheet(0)
        return sheet
    except Exception as e:
        st.error(f"❌ การเชื่อมต่อล้มเหลว: {str(e)}")
        return None

# --- 3. THE PREMIUM STYLING ---
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
    h2 { color: #265F36; border-left: 10px solid #F9A818; padding-left: 15px; margin-top: 30px; }
    .stForm { background-color: white !important; padding: 30px !important; border-radius: 15px !important; }
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

# --- 5. TOOL CONTENT (คืนรายละเอียดคำถามทั้งหมด) ---

if choice == "Tool 1: แบบประเมินสถานะองค์กร":
    st.markdown('<div class="main-header"><h1>Tool 1: แบบประเมินสถานะองค์กร</h1></div>', unsafe_allow_html=True)
    with st.form("form_t1"):
        st.subheader("หมวด A: การกำกับดูแลและนโยบาย")
        q1_1 = st.radio("1.1 องค์กรมี 'นโยบายสิทธิมนุษยชน' ที่เป็นลายลักษณ์อักษรหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_2 = st.radio("1.2 นโยบายครอบคลุมประเด็นสำคัญ (แรงงานข้ามชาติ, สิทธิชุมชน, สิ่งแวดล้อม) หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_3 = st.radio("1.3 มีการสื่อสารนโยบายในภาษาที่พนักงานและคู่ค้าเข้าใจหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_4 = st.radio("1.4 มีการแต่งตั้งผู้รับผิดชอบด้านสิทธิมนุษยชนในระดับบริหารหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        
        st.subheader("หมวด B: กระบวนการตรวจสอบอย่างรอบด้าน (Due Diligence)")
        q2_1 = st.radio("2.1 มีการประเมินความเสี่ยง (HRA) เป็นประจำทุกปีหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q2_2 = st.radio("2.2 มีระบบการตรวจสอบย้อนกลับ (Traceability) ในห่วงโซ่อุปทานหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q2_3 = st.radio("2.3 มีแผนการจัดการความเสี่ยง (Mitigation Plan) ที่ชัดเจนหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        
        st.subheader("หมวด C: กลไกการร้องเรียนและการเยียวยา")
        q3_1 = st.radio("3.1 มีช่องทางรับเรื่องร้องเรียนที่ปลอดภัยและเป็นอิสระหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q3_2 = st.radio("3.2 มีมาตรการคุ้มครองผู้แจ้งเบาะแส (Non-Retaliation Policy) หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q3_3 = st.radio("3.3 มีขั้นตอนการเยียวยา (Remediation) เมื่อเกิดการละเมิดหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        
        submitted = st.form_submit_button("💾 บันทึกข้อมูล Tool 1 เข้า Google Sheet")
        if submitted:
            sheet = connect_to_sheet()
            if sheet:
                data = [now, "Tool 1", q1_1, q1_2, q1_3, q1_4, q2_1, q2_2, q2_3, q3_1, q3_2, q3_3]
                sheet.append_row(data)
                st.success("✅ บันทึกข้อมูล Tool 1 เรียบร้อยแล้ว!")

elif choice == "Tool 2: แบบสอบถามการปฏิบัติหน้างาน":
    st.markdown('<div class="main-header"><h1>Tool 2: แบบสอบถามการปฏิบัติหน้างาน</h1></div>', unsafe_allow_html=True)
    with st.form("form_t2"):
        st.subheader("ส่วนที่ 1: สภาพการจ้างและค่าจ้าง")
        q2_1 = st.select_slider("1.1 ท่านได้รับค่าจ้างตรงตามที่ตกลงและตรงเวลาหรือไม่?", options=[1,2,3,4,5], value=3)
        q2_2 = st.select_slider("1.2 ท่านได้รับวันหยุดอย่างน้อย 1 วันต่อสัปดาห์หรือไม่?", options=[1,2,3,4,5], value=3)
        q2_3 = st.select_slider("1.3 ท่านเป็นผู้เก็บเอกสารประจำตัว (พาสปอร์ต/บัตร) ไว้เองใช่หรือไม่?", options=[1,2,3,4,5], value=3)
        
        st.subheader("ส่วนที่ 2: อาชีวอนามัยและความปลอดภัย")
        q3_1 = st.select_slider("2.1 อุปกรณ์ป้องกันอันตราย (PPE) มีความเพียงพอและอยู่ในสภาพดีหรือไม่?", options=[1,2,3,4,5], value=3)
        q3_2 = st.select_slider("2.2 ท่านได้รับการอบรมความปลอดภัยก่อนเริ่มงานหรือไม่?", options=[1,2,3,4,5], value=3)
        
        st.subheader("ส่วนที่ 3: การปฏิบัติต่อแรงงาน")
        q4_1 = st.select_slider("3.1 หัวหน้างานปฏิบัติต่อท่านด้วยความเคารพ (ไม่มีการข่มขู่) ใช่หรือไม่?", options=[1,2,3,4,5], value=3)
        q4_2 = st.select_slider("3.2 ท่านสามารถเข้าถึงน้ำดื่มและห้องน้ำที่สะอาดได้ตลอดเวลาใช่หรือไม่?", options=[1,2,3,4,5], value=3)
        
        submitted = st.form_submit_button("🚀 ส่งผลแบบสำรวจ Tool 2")
        if submitted:
            sheet = connect_to_sheet()
            if sheet:
                data = [now, "Tool 2", q2_1, q2_2, q2_3, q3_1, q3_2, q4_1, q4_2]
                sheet.append_row(data)
                st.success("✅ ส่งผลแบบสำรวจ Tool 2 เรียบร้อยแล้ว!")

elif choice == "Tool 3: แนวทางการสัมภาษณ์เชิงลึก":
    st.markdown('<div class="main-header"><h1>Tool 3: แนวทางการสัมภาษณ์เชิงลึก</h1></div>', unsafe_allow_html=True)
    with st.form("form_t3"):
        st.info("บันทึกคำตอบจากการสัมภาษณ์กลุ่มเป้าหมาย (พนักงาน/คู่ค้า/ชุมชน)")
        i1 = st.text_area("1. ขั้นตอนการสรรหา: ท่านต้องจ่ายค่าธรรมเนียมการสมัครงานให้กับใครหรือไม่? (Recruitment Fees)")
        i2 = st.text_area("2. สัญญาจ้าง: ท่านได้รับสัญญาจ้างในภาษาที่ท่านเข้าใจ และตรงกับงานที่ทำจริงหรือไม่?")
        i3 = st.text_area("3. สภาพความเป็นอยู่: (กรณีพักในหอพัก) ความเป็นอยู่มีความปลอดภัยและเป็นส่วนตัวเพียงพอหรือไม่?")
        i4 = st.text_area("4. กลไกร้องเรียน: หากมีปัญหา ท่านทราบหรือไม่ว่าต้องแจ้งใคร และกังวลเรื่องผลกระทบตามมาหรือไม่?")
        
        submitted = st.form_submit_button("💾 บันทึกบทสัมภาษณ์ Tool 3")
        if submitted:
            sheet = connect_to_sheet()
            if sheet:
                data = [now, "Tool 3", i1, i2, i3, i4]
                sheet.append_row(data)
                st.success("✅ บันทึกข้อมูลการสัมภาษณ์เรียบร้อย")

elif choice == "Tool 4: แบบบันทึกการสังเกตการณ์":
    st.markdown('<div class="main-header"><h1>Tool 4: แบบบันทึกการสังเกตการณ์</h1></div>', unsafe_allow_html=True)
    with st.form("form_t4"):
        o1 = st.checkbox("มีการติดประกาศนโยบายสิทธิมนุษยชน/จริยธรรมธุรกิจ ในพื้นที่ทำงาน")
        o2 = st.checkbox("พนักงานสวมใส่อุปกรณ์ PPE ครบถ้วนตามลักษณะงาน")
        o3 = st.checkbox("ทางหนีไฟและอุปกรณ์ดับเพลิงไม่มีสิ่งกีดขวางและพร้อมใช้งาน")
        o4 = st.checkbox("ตู้ยาสามัญประจำบ้านมีเวชภัณฑ์ครบถ้วนและไม่หมดอายุ")
        note = st.text_area("บันทึกสิ่งที่พบเพิ่มเติมจากการเดินสำรวจ:")
        
        submitted = st.form_submit_button("💾 บันทึก Log การสังเกตการณ์")
        if submitted:
            sheet = connect_to_sheet()
            if sheet:
                data = [now, "Tool 4", str(o1), str(o2), str(o3), str(o4), note]
                sheet.append_row(data)
                st.success("✅ บันทึก Log เรียบร้อย")

elif choice == "Tool 5: การประเมินนัยสำคัญ (Heat Map)":
    st.markdown('<div class="main-header"><h1>Tool 5: Human Rights Risk Heat Map</h1></div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        issue = st.text_input("ประเด็นความเสี่ยงที่ประเมิน:", "ความปลอดภัยในที่ทำงาน")
        s1 = st.slider("ขนาดของผลกระทบ (Scale)", 1, 5, 3)
        s2 = st.slider("ขอบเขตของผลกระทบ (Scope)", 1, 5, 3)
        s3 = st.slider("ความยากง่ายในการเยียวยา (Remediability)", 1, 5, 3)
        severity = max(s1, s2, s3)
        likelihood = st.slider("โอกาสที่จะเกิดขึ้น (Likelihood)", 1, 5, 2)
        score = severity * likelihood
    
    with col2:
        st.subheader("เกณฑ์การตัดสินนัยสำคัญ")
        if score >= 16: st.error(f"ระดับความเสี่ยง: สูงมาก (Critical) - Score: {score}")
        elif score >= 8: st.warning(f"ระดับความเสี่ยง: ปานกลาง (Medium) - Score: {score}")
        else: st.success(f"ระดับความเสี่ยง: ต่ำ (Low) - Score: {score}")

    if st.button("💾 บันทึกค่าความเสี่ยงลง Google Sheet"):
        sheet = connect_to_sheet()
        if sheet:
            sheet.append_row([now, "Tool 5", issue, severity, likelihood, score])
            st.success(f"บันทึกประเด็น '{issue}' สำเร็จ!")

elif choice == "Tool 6: ระบบวิเคราะห์ AI Triangulation":
    st.markdown('<div class="main-header"><h1>Tool 6: AI Data Triangulation</h1></div>', unsafe_allow_html=True)
    st.write("ระบบวิเคราะห์เปรียบเทียบข้อมูลจาก Tool 1-4 เพื่อหาจุดขัดแย้ง (Gap Analysis)")
    raw_data = st.text_area("วางสรุปข้อมูลจากการลงพื้นที่เพื่อประมวลผล:")
    if st.button("เริ่มการวิเคราะห์"):
        st.info("กำลังประมวลผลข้อมูลร่วมกับฐานข้อมูลสิทธิมนุษยชน...")

st.markdown("<br><hr><p style='text-align: center; color: #888;'>© 2024 Betagro Group | HRDD Digital Toolkit</p>", unsafe_allow_html=True)
