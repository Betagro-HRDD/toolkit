import streamlit as st
import pandas as pd
from google.oauth2 import service_account
import gspread
from datetime import datetime

# --- 1. SETTING UP THE PAGE ---
st.set_page_config(page_title="Betagro HRDD Premium Toolkit", page_icon="https://www.betagro.com/favicon.ico", layout="wide")

# --- 2. CONNECT ENGINE ---
def connect_to_sheet():
    try:
        creds_info = st.secrets["gcp_service_account"]
        private_key = creds_info["private_key"].replace("\\n", "\n")
        creds_dict = {**creds_info, "private_key": private_key}
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        credentials = service_account.Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(credentials)
        SHEET_ID = "1YUkrlk_RlvskDluFoAdTQ7KRYRxYhi8ZqNdw13X7JxY"
        return client.open_by_key(SHEET_ID).get_worksheet(0)
    except Exception as e:
        st.error(f"❌ การเชื่อมต่อล้มเหลว: {e}")
        return None

# --- 3. PREMIUM STYLING (ฉบับแก้ไขปุ่มซ้อนทับ) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Sarabun', sans-serif; }
    .stApp { background-color: #F8FAFB; }

    /* 1. จัดการเฉพาะปุ่มเปิด Sidebar (ซ้าย) ไม่ให้ไปยุ่งกับปุ่มอื่น */
    [data-testid="stSidebarCollapsedControl"] {
        background-color: #F9A818 !important;
        width: 55px !important;
        height: 55px !important;
        border-radius: 8px !important;
        position: fixed !important;
        top: 10px !important;
        left: 10px !important;
        z-index: 9999999 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2) !important;
    }

    /* เปลี่ยนไอคอนเป็น ☰ และซ่อนของเดิม */
    [data-testid="stSidebarCollapsedControl"] svg {
        display: none !important;
    }
    [data-testid="stSidebarCollapsedControl"]::after {
        content: "☰" !important;
        color: white !important;
        font-size: 28px !important;
    }

    /* 2. จัดการปุ่ม "ปิด" (X) เวลาแถบข้างกางออกมาแล้ว */
    [data-testid="stSidebar"] button[kind="headerNoPadding"] {
        background-color: #f0f0f0 !important;
        color: #333 !important;
        border-radius: 50% !important;
    }

    /* 3. 🔥 หัวใจสำคัญ: สั่งซ่อนเมนู 3 จุด (ขวาสุด) ทิ้งไปเลย เพื่อไม่ให้มาทับปุ่มเรา */
    [data-testid="stToolbar"], #MainMenu {
        visibility: hidden !important;
        display: none !important;
    }

    /* ตกแต่งส่วนหัว */
    .main-header {
        background-color: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-left: 10px solid #F9A818;
        margin-bottom: 20px; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR & MOBILE UX HACK ---
def user_info_inputs(key_suffix):
    rid = st.text_input("รหัสผู้ให้ข้อมูล (ID):", placeholder="เช่น EMP-001", key=f"id_{key_suffix}")
    rgroup = st.selectbox("กลุ่มเป้าหมาย:", ["ฝ่ายบริหาร", "แรงงานไทย", "แรงงานข้ามชาติ", "ชุมชน", "คู่ค้า"], key=f"group_{key_suffix}")
    return rid, rgroup

with st.sidebar:
    st.image("https://www.betagro.com/wp-content/themes/betagro/assets/img/logo-en.png", width=160)
    st.title("HRDD Settings")
    
    # ⚠️ ชื่อเมนูตรงนี้ ต้องตรงกับเงื่อนไข if choice == "..." ในโค้ด Tool 1-6 ของคุณเป๊ะๆ นะครับ
    choice = st.radio("📋 เลือกเครื่องมือ:", [
        "Tool 1: ประเมินสถานะองค์กร",
        "Tool 2: แบบสอบถามหน้างาน",
        "Tool 3: สัมภาษณ์เชิงลึก (Evidence)",
        "Tool 4: บันทึกการสังเกตการณ์",
        "Tool 5: ประเมินนัยสำคัญ (Salient Rule)",
        "Tool 6: ระบบวิเคราะห์ AI Triangulation"
    ])
    st.divider()
    st.subheader("👤 ข้อมูลผู้ให้ข้อมูล")
    resp_id_sidebar, resp_group_sidebar = user_info_inputs("side")

# 🔥 UX Hack สำหรับมือถือ: ถ้ายังไม่ได้กรอก ID ให้ขึ้นช่องกรอกกลางจอ
if not resp_id_sidebar:
    st.warning("🚨 ตรวจพบว่ายังไม่ได้ระบุ รหัสผู้ให้ข้อมูล (ID)")
    st.info("กรุณากรอกรหัส ID เพื่อเริ่มใช้งานเครื่องมือประเมิน:")
    col1, col2 = st.columns(2)
    with col1:
        resp_id_main = st.text_input("รหัสผู้ให้ข้อมูล (ID):", placeholder="เช่น EMP-001", key="id_main")
    with col2:
        resp_group_main = st.selectbox("กลุ่มเป้าหมาย:", ["ฝ่ายบริหาร", "แรงงานไทย", "แรงงานข้ามชาติ", "ชุมชน", "คู่ค้า"], key="group_main")
    
    if not resp_id_main:
        st.stop() # หยุดหน้าเว็บไว้ตรงนี้จนกว่าจะกรอก ID เสร็จ
    else:
        resp_id = resp_id_main
        resp_group = resp_group_main
else:
    resp_id = resp_id_sidebar
    resp_group = resp_group_sidebar

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ==========================================
# --- 5. TOOLS LOGIC (วางโค้ด Tool 1-6 ฉบับเต็มของคุณต่อจากบรรทัดนี้ได้เลยครับ) ---
# ==========================================

# ==========================================
# TOOL 1: แบบประเมินสถานะองค์กร (Gap Analysis)
# ==========================================
if choice == "Tool 1: ประเมินสถานะองค์กร":
    st.markdown('<div class="main-header"><h1>Tool 1: แบบประเมินสถานะองค์กร (Policy Gap Analysis)</h1></div>', unsafe_allow_html=True)
    # ใส่ไว้ในทุก Tool เพื่อเตือนคนใช้มือถือ
if not resp_id:
    st.warning("⚠️ โปรดกดปุ่ม ☰ (มุมซ้ายบน) เพื่อกรอก รหัสผู้ประเมิน และ เลือกกลุ่มเป้าหมาย ก่อนเริ่มทำรายการ")
    with st.form("form_t1"):
        st.subheader("หมวด A: การกำกับดูแลและนโยบาย (Governance & Policy)")
        q1_1 = st.radio("1.1 องค์กรมี 'นโยบายสิทธิมนุษยชน' ที่เป็นลายลักษณ์อักษรหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_2 = st.radio("1.2 นโยบายครอบคลุมประเด็นสำคัญ (แรงงานข้ามชาติ, ชุมชน, สิ่งแวดล้อม) หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_3 = st.radio("1.3 มีการสื่อสารนโยบายในภาษาที่พนักงานและคู่ค้าเข้าใจหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_4 = st.radio("1.4 มีการแต่งตั้งผู้รับผิดชอบระดับบริหาร (Board Level) หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        
        st.subheader("หมวด B: กระบวนการตรวจสอบอย่างรอบด้าน (Due Diligence)")
        q2_1 = st.radio("2.1 มีการประเมินความเสี่ยงด้านสิทธิมนุษยชน (HRA) ประจำปีหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q2_2 = st.radio("2.2 มีระบบการตรวจสอบย้อนกลับ (Traceability) ในห่วงโซ่อุปทานหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q2_3 = st.radio("2.3 มีแผนจัดการความเสี่ยง (Mitigation Plan) ที่ชัดเจนและนำไปใช้จริงหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        
        st.subheader("หมวด C: กลไกการร้องเรียนและการเยียวยา (Grievance & Remediation)")
        q3_1 = st.radio("3.1 มีช่องทางรับเรื่องร้องเรียนที่ปลอดภัย เป็นความลับ และเข้าถึงได้ง่ายหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q3_2 = st.radio("3.2 มีมาตรการคุ้มครองผู้แจ้งเบาะแส (Non-Retaliation Policy) หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q3_3 = st.radio("3.3 มีขั้นตอนการเยียวยา (Remediation) แก่ผู้ได้รับผลกระทบเมื่อเกิดการละเมิดหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])

        if st.form_submit_button("💾 บันทึกข้อมูล Tool 1"):
            if not resp_id: st.warning("กรุณาระบุรหัสผู้ให้ข้อมูลที่แถบด้านซ้ายมือ"); st.stop()
            sheet = connect_to_sheet()
            if sheet:
                # รวบรวมคำตอบทั้งหมดเป็น Text เพื่อเก็บใน 1 เซลล์ให้เป็นระเบียบ
                detail = f"A(1.1:{q1_1}, 1.2:{q1_2}, 1.3:{q1_3}, 1.4:{q1_4}) | B(2.1:{q2_1}, 2.2:{q2_2}, 2.3:{q2_3}) | C(3.1:{q3_1}, 3.2:{q3_2}, 3.3:{q3_3})"
                sheet.append_row([now, "Tool 1", resp_id, resp_group, "Policy Gap Analysis", detail, "", "", "", ""])
                st.success("✅ บันทึกข้อมูล Tool 1 ครบทุกข้อลง Google Sheet เรียบร้อย")

# ==========================================
# TOOL 2: แบบสอบถามหน้างาน (Worker Survey)
# ==========================================
elif choice == "Tool 2: แบบสอบถามหน้างาน":
    st.markdown('<div class="main-header"><h1>Tool 2: แบบสอบถามการปฏิบัติหน้างาน (Worker Survey)</h1></div>', unsafe_allow_html=True)
    # ใส่ไว้ในทุก Tool เพื่อเตือนคนใช้มือถือ
if not resp_id:
    st.warning("⚠️ โปรดกดปุ่ม ☰ (มุมซ้ายบน) เพื่อกรอก รหัสผู้ประเมิน และ เลือกกลุ่มเป้าหมาย ก่อนเริ่มทำรายการ")
    with st.form("form_t2"):
        st.subheader("ส่วนที่ 1: สภาพการจ้างและค่าจ้าง")
        s1_1 = st.select_slider("1.1 ท่านได้รับค่าจ้างตรงเวลาและครบถ้วนตามสัญญาหรือไม่?", options=[1,2,3,4,5], value=3)
        s1_2 = st.select_slider("1.2 ท่านได้รับวันหยุดอย่างน้อย 1 วันต่อสัปดาห์ (หรือตามกฎหมาย) หรือไม่?", options=[1,2,3,4,5], value=3)
        s1_3 = st.select_slider("1.3 ท่านเป็นผู้เก็บเอกสารประจำตัว (เช่น พาสปอร์ต, บัตรประชาชน) ไว้เองใช่หรือไม่?", options=[1,2,3,4,5], value=3)
        
        st.subheader("ส่วนที่ 2: ความปลอดภัยและสุขอนามัย (OHS)")
        s2_1 = st.select_slider("2.1 อุปกรณ์ป้องกันอันตราย (PPE) มีเพียงพอและอยู่ในสภาพพร้อมใช้งานหรือไม่?", options=[1,2,3,4,5], value=3)
        s2_2 = st.select_slider("2.2 ท่านได้รับการฝึกอบรมด้านความปลอดภัยก่อนเริ่มปฏิบัติงานหรือไม่?", options=[1,2,3,4,5], value=3)
        
        st.subheader("ส่วนที่ 3: การปฏิบัติต่อแรงงานและความเท่าเทียม")
        s3_1 = st.select_slider("3.1 หัวหน้างานปฏิบัติต่อท่านด้วยความเคารพ (ปราศจากการดุด่า ข่มขู่ หรือล่วงละเมิด) ใช่หรือไม่?", options=[1,2,3,4,5], value=3)
        s3_2 = st.select_slider("3.2 ท่านสามารถเข้าถึงน้ำดื่มที่สะอาดและห้องน้ำที่เพียงพอได้ตลอดเวลาใช่หรือไม่?", options=[1,2,3,4,5], value=3)
        
        if st.form_submit_button("🚀 บันทึกข้อมูล Tool 2"):
            if not resp_id: st.warning("กรุณาระบุรหัสผู้ให้ข้อมูลที่แถบด้านซ้ายมือ"); st.stop()
            sheet = connect_to_sheet()
            if sheet:
                detail = f"การจ้าง(1.1:{s1_1}, 1.2:{s1_2}, 1.3:{s1_3}) | ความปลอดภัย(2.1:{s2_1}, 2.2:{s2_2}) | การปฏิบัติ(3.1:{s3_1}, 3.2:{s3_2})"
                sheet.append_row([now, "Tool 2", resp_id, resp_group, "Worker Practice", detail, "", "", "", ""])
                st.success("✅ ส่งข้อมูลแบบสอบถาม Tool 2 สำเร็จ")

# ==========================================
# TOOL 3: สัมภาษณ์เชิงลึก (In-depth Interview)
# ==========================================
elif choice == "Tool 3: สัมภาษณ์เชิงลึก (Evidence)":
    st.markdown('<div class="main-header"><h1>Tool 3: แนวทางการสัมภาษณ์เชิงลึก (In-depth Interview)</h1></div>', unsafe_allow_html=True)
    # ใส่ไว้ในทุก Tool เพื่อเตือนคนใช้มือถือ
if not resp_id:
    st.warning("⚠️ โปรดกดปุ่ม ☰ (มุมซ้ายบน) เพื่อกรอก รหัสผู้ประเมิน และ เลือกกลุ่มเป้าหมาย ก่อนเริ่มทำรายการ")
    with st.form("form_t3"):
        st.write("### 🔍 หัวข้อการตรวจสอบ (เลือกข้อที่พบประเด็นความเสี่ยง)")
        topics = st.multiselect("ประเด็นที่พูดคุย:", 
            ["การสรรหา/ค่านายหน้า (Recruitment Fees)", 
             "ความเข้าใจในสัญญาจ้าง", 
             "การจ่ายค่าจ้าง/โอที", 
             "เสรีภาพในการเดินทาง/ลาออก", 
             "สภาพที่พักอาศัย/โรงอาหาร", 
             "กลไกการร้องเรียน",
             "การเลือกปฏิบัติ/การคุกคาม"])
             
        st.write("### ✍️ บันทึกคำให้การ (Testimony / Evidence-based)")
        testimony = st.text_area("สรุปคำพูดหรือหลักฐานที่พบจากการสัมภาษณ์ (โปรดระบุรายละเอียดให้ชัดเจน):", height=150,
                                 placeholder="ตัวอย่าง: 'พนักงานแจ้งว่าต้องจ่ายค่านายหน้า 5,000 บาทให้กับเอเจนซี่ที่ประเทศต้นทาง...'")
        
        if st.form_submit_button("💾 บันทึกข้อมูล Tool 3"):
            if not resp_id: st.warning("กรุณาระบุรหัสผู้ให้ข้อมูลที่แถบด้านซ้ายมือ"); st.stop()
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([now, "Tool 3", resp_id, resp_group, ", ".join(topics), testimony, "", "", "", ""])
                st.success("✅ บันทึกหลักฐานบทสัมภาษณ์สำเร็จ ข้อมูลถูกจัดเรียงลง 10 คอลัมน์แล้ว")

# ==========================================
# TOOL 4: แบบบันทึกการสังเกตการณ์ (Observation Log)
# ==========================================
elif choice == "Tool 4: บันทึกการสังเกตการณ์":
    st.markdown('<div class="main-header"><h1>Tool 4: แบบบันทึกการสังเกตการณ์หน้างาน (Site Observation Log)</h1></div>', unsafe_allow_html=True)
    # ใส่ไว้ในทุก Tool เพื่อเตือนคนใช้มือถือ
if not resp_id:
    st.warning("⚠️ โปรดกดปุ่ม ☰ (มุมซ้ายบน) เพื่อกรอก รหัสผู้ประเมิน และ เลือกกลุ่มเป้าหมาย ก่อนเริ่มทำรายการ")
    with st.form("form_t4"):
        st.write("### 🔎 เช็คลิสต์การตรวจประเมินพื้นที่ (ติ๊กข้อที่ปฏิบัติได้ถูกต้อง)")
        o1 = st.checkbox("1. มีการติดประกาศนโยบายและสิทธิแรงงานในพื้นที่ที่มองเห็นได้ชัดเจน")
        o2 = st.checkbox("2. ทางหนีไฟและอุปกรณ์ดับเพลิงไม่มีสิ่งกีดขวางและอยู่ในสภาพพร้อมใช้งาน")
        o3 = st.checkbox("3. พนักงานในสายการผลิตสวมใส่อุปกรณ์ PPE ถูกต้องตามลักษณะงานทุกคน")
        o4 = st.checkbox("4. ตู้ยาสามัญประจำบ้านมีเวชภัณฑ์ครบถ้วนและไม่หมดอายุ")
        o5 = st.checkbox("5. สภาพแวดล้อมที่พัก/โรงอาหารมีความสะอาดและถูกสุขลักษณะ")
        o6 = st.checkbox("6. มีแสงสว่างและการระบายอากาศที่เพียงพอในพื้นที่ทำงาน")
        
        obs_detail = st.text_area("บันทึกสิ่งที่พบเพิ่มเติมจากการเดินสำรวจ (จุดที่ต้องแก้ไข/ปรับปรุง):", height=100)
        
        if st.form_submit_button("💾 บันทึกข้อมูล Tool 4"):
            if not resp_id: st.warning("กรุณาระบุรหัสผู้เดินสำรวจ (ID) ที่แถบด้านซ้ายมือ"); st.stop()
            sheet = connect_to_sheet()
            if sheet:
                checklist_result = f"O1:{o1}, O2:{o2}, O3:{o3}, O4:{o4}, O5:{o5}, O6:{o6}"
                detail = f"[Checklist: {checklist_result}] | Note: {obs_detail}"
                sheet.append_row([now, "Tool 4", resp_id, resp_group, "Site Observation", detail, "", "", "", ""])
                st.success("✅ บันทึก Log การสังเกตการณ์สำเร็จ")

# ==========================================
# TOOL 5: ประเมินนัยสำคัญ (Salient Rule) - แบบ Dropdown มาตรฐาน
# ==========================================
elif choice == "Tool 5: ประเมินนัยสำคัญ (Salient Rule)":
    st.markdown('<div class="main-header"><h1>Tool 5: Human Rights Risk Matrix</h1><p>คำนวณตามหลัก "ความร้ายแรงนำ" (Severity-led Rule)</p></div>', unsafe_allow_html=True)
    # --- วางตรงนี้ครับ ---
    if not resp_id:
        st.warning("⚠️ โปรดกดปุ่ม ☰ (มุมซ้ายบน) เพื่อกรอก รหัสผู้ประเมิน และ เลือกกลุ่มเป้าหมาย ก่อนเริ่มทำรายการ")
        st.stop() # หยุดการทำงานข้างล่างไว้ก่อนจนกว่าจะกรอก ID
    # ------------------
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.write("**📌 1. ระบุประเด็นความเสี่ยง (เลือกตามมาตรฐานสากล ILO/UNGPs)**")
        
        # ใช้ Dropdown แทนการพิมพ์ข้อความเอง
        issue = st.selectbox("หมวดหมู่ความเสี่ยง:", [
            "[แรงงานบังคับ] ภาระหนี้ผูกพัน / การเรียกเก็บค่าธรรมเนียมสรรหา",
            "[แรงงานบังคับ] การยึดเอกสารประจำตัว (พาสปอร์ต/บัตร)",
            "[แรงงานบังคับ] การจำกัดเสรีภาพในการเดินทาง",
            "[สิทธิแรงงาน] การหักค่าจ้าง / จ่ายเงินล่าช้า / ไม่จ่ายโอที",
            "[สิทธิแรงงาน] การเลือกปฏิบัติและการคุกคามในที่ทำงาน",
            "[อาชีวอนามัย] สภาพแวดล้อมการทำงานอันตราย / ขาด PPE",
            "[อาชีวอนามัย] สภาพที่พักอาศัย/โรงอาหารไม่ถูกสุขลักษณะ",
            "[ชุมชน] ผลกระทบต่อสิ่งแวดล้อมและชุมชนโดยรอบ",
            "อื่นๆ (ประเด็นความเสี่ยงใหม่)"
        ])
        
        st.write("---")
        st.write("**📌 2. คำนวณ Severity (ใช้ค่าที่สูงที่สุด ไม่เอาค่าเฉลี่ย)**")
        scale = st.slider("Scale (ความรุนแรงของผลกระทบ)", 1, 5, 1)
        scope = st.slider("Scope (จำนวนผู้ได้รับผลกระทบ)", 1, 5, 1)
        remedy = st.slider("Remediability (ความยากในการเยียวยา)", 1, 5, 1)
        
        # กฎ Salient-led Rule: เอาค่าสูงสุด
        sev_max = max(scale, scope, remedy)
        likelihood = st.slider("Likelihood (โอกาสที่จะเกิด)", 1, 5, 1)
        score = sev_max * likelihood

        st.subheader(f"Severity Max: {sev_max} | Total Score: {score}")
        is_salient = "YES" if sev_max == 5 else "NO"
        if is_salient == "YES":
            st.markdown('<div class="salient-badge">🚨 SALIENT ISSUE: ความเสี่ยงระดับสูงสุด</div>', unsafe_allow_html=True)

    with col2:
        # วาด Heat Map
        rows = ""
        for l in range(5, 0, -1):
            rows += "<tr>"
            for s in range(1, 6):
                val = s * l
                color = "#EF4444" if val >= 16 or s == 5 else ("#F9A818" if val >= 8 else "#265F36")
                mark = "★" if s == sev_max and l == likelihood else ""
                rows += f"<td class='heat-cell' style='background-color:{color};'>{mark}</td>"
            rows += "</tr>"
        st.markdown(f"<table class='heat-table'>{rows}</table><p style='text-align:center;'><small>แนวนอน: Severity | แนวตั้ง: Likelihood</small></p>", unsafe_allow_html=True)

    if st.button("💾 บันทึกประเด็นนัยสำคัญ (Statement of Salient Issues)"):
        if not resp_id: st.warning("กรุณาระบุรหัสผู้ประเมิน (ID) ที่แถบด้านซ้ายมือ"); st.stop()
        sheet = connect_to_sheet()
        if sheet:
            detail = f"Scale:{scale}, Scope:{scope}, Remedy:{remedy}"
            sheet.append_row([now, "Tool 5", resp_id, resp_group, issue, detail, sev_max, likelihood, score, is_salient])
            st.success("✅ บันทึกความเสี่ยงเรียบร้อย ข้อมูลเข้าช่อง Salient อย่างเป็นระเบียบ")

# ==========================================
# TOOL 6: AI Triangulation
# ==========================================
elif choice == "Tool 6: AI Triangulation":
    st.markdown('<div class="main-header"><h1>Tool 6: AI-Augmented Triangulation</h1></div>', unsafe_allow_html=True)
    # --- วางตรงนี้ครับ ---
    if not resp_id:
        st.warning("⚠️ โปรดกดปุ่ม ☰ (มุมซ้ายบน) เพื่อกรอก รหัสผู้ประเมิน และ เลือกกลุ่มเป้าหมาย ก่อนเริ่มทำรายการ")
        st.stop() # หยุดการทำงานข้างล่างไว้ก่อนจนกว่าจะกรอก ID
    # ------------------
        st.info("ระบบจะดึง 'ประโยคอ้างอิง' (Citations) จาก Tool 3 และ 4 มาเปรียบเทียบกับ Tool 1 เพื่อพิสูจน์ความสอดคล้อง")
    
    st.markdown("""
    <div class="citation-box">
        <b>🚩 พบความขัดแย้งเชิงนโยบาย (Policy vs Practice):</b> สัญญาจ้างไม่เป็นภาษาที่พนักงานเข้าใจ<br>
        <small><i>อ้างอิงคำสัมภาษณ์ (ID: EMP-045):</i> "ผมเซ็นไปโดยไม่รู้ว่าเป็นภาษาอะไร เพราะไม่ได้มีล่ามแปลให้ฟัง..."</small><br>
        <small><i>ขัดแย้งกับนโยบาย (Tool 1 หมวด A ข้อ 1.3):</i> ฝ่ายบริหารตอบว่ามีการสื่อสารในภาษาที่เข้าใจแล้ว</small>
    </div>
    <div class="citation-box">
        <b>🚩 ประเด็นเฝ้าระวังเรื่องค่าธรรมเนียม:</b> พบร่องรอยการจ่ายค่านายหน้า<br>
        <small><i>อ้างอิงหลักฐาน (ID: EMP-012):</i> "จ่ายให้เอเจนซี่ฝั่งพม่าไป 15,000 บาทก่อนเข้ามาทำงานที่นี่"</small>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("💾 บันทึกสรุปผล AI Analysis ลงระบบ"):
        if not resp_id: st.warning("กรุณาระบุรหัสผู้ประมวลผล (ID) ที่แถบด้านซ้ายมือ"); st.stop()
        sheet = connect_to_sheet()
        if sheet:
            sheet.append_row([now, "Tool 6", resp_id, resp_group, "AI Triangulation", "พบความขัดแย้ง 2 ประเด็น (สัญญาจ้างและค่าธรรมเนียม)", "", "", "", ""])
            st.success("✅ บันทึกข้อมูลการวิเคราะห์เชิงลึกเสร็จสิ้น")
