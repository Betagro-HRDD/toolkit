import streamlit as st
import pandas as pd
from google.oauth2 import service_account
import gspread
from datetime import datetime

# --- 1. SETTING UP THE PAGE ---
st.set_page_config(
    page_title="Betagro HRDD Premium Toolkit", 
    page_icon="https://www.betagro.com/favicon.ico", 
    layout="centered" # เน้นแสดงผลบนมือถือให้สวยงาม
)

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

# --- 3. PREMIUM MODERN STYLING (คืนชีพความหรูหรา) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&display=swap');
    
    html, body, [class*="st-"] { 
        font-family: 'Sarabun', sans-serif; 
    }
    
    /* พื้นหลังสีเทาอ่อนหรูหรา เพื่อให้กล่องสีขาวดูโดดเด่น */
    .stApp { background-color: #F4F7F9; }
    
    /* ซ่อนเมนูและปุ่มที่ไม่จำเป็นทั้งหมด */
    header {visibility: hidden !important;}
    [data-testid="collapsedControl"] {display: none !important;}
    
    /* ตกแต่งกล่อง Form ให้เป็น Card ล้ำสมัย */
    [data-testid="stForm"] {
        background-color: #FFFFFF;
        border-radius: 20px;
        padding: 30px 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.06);
        border: none;
        border-top: 6px solid #F9A818; /* เส้นขอบบนสีทอง Betagro */
        transition: transform 0.3s ease;
    }
    
    /* ตกแต่งปุ่ม Submit ให้ดูแพง (ไล่สี Gradient) */
    [data-testid="stFormSubmitButton"] > button, .stButton > button {
        background: linear-gradient(135deg, #265F36 0%, #388E3C 100%) !important; /* สีเขียว Betagro */
        color: white !important;
        border-radius: 30px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        border: none !important;
        padding: 12px 24px !important;
        box-shadow: 0 6px 15px rgba(38,95,54,0.3) !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }
    [data-testid="stFormSubmitButton"] > button:hover, .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(38,95,54,0.4) !important;
    }

    /* ตกแต่งหัวข้อส่วน Header ของแต่ละ Tool */
    .premium-header {
        background: linear-gradient(135deg, #1e3c27 0%, #265F36 100%);
        color: white;
        padding: 25px 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(38,95,54,0.2);
        margin-bottom: 25px;
        border-bottom: 5px solid #F9A818;
    }
    .premium-header h3 { color: white !important; margin: 0; font-weight: 700; }
    .premium-header p { margin: 5px 0 0 0; opacity: 0.9; font-weight: 300; font-size: 14px; }
    
    /* ป้ายเตือนความเสี่ยง (Salient Badge) พร้อมเอฟเฟกต์กระพริบเบาๆ */
    .salient-badge { 
        background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%); 
        color: white; padding: 15px; border-radius: 12px; 
        font-weight: bold; text-align: center; box-shadow: 0 4px 15px rgba(239,68,68,0.3);
        animation: pulse 2s infinite;
    }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.02); } 100% { transform: scale(1); } }
    
    /* ตาราง Heatmap Tool 5 */
    .heat-table { width: 100%; border-collapse: separate; border-spacing: 4px; margin-top: 15px;}
    .heat-cell { height: 45px; text-align: center; font-weight: bold; color: white; border-radius: 6px; box-shadow: inset 0 0 5px rgba(0,0,0,0.1);}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# --- 4. TOP-DOWN UI (หรูหรา และใช้งานง่าย) ---
# ==========================================
col_logo1, col_logo2, col_logo3 = st.columns([1,2,1])
with col_logo2:
    st.image("https://www.betagro.com/wp-content/themes/betagro/assets/img/logo-en.png", use_container_width=True)

st.markdown("<h2 style='text-align: center; color: #265F36; font-weight: 700; margin-bottom: 30px;'>ระบบประเมิน HRDD อัจฉริยะ</h2>", unsafe_allow_html=True)

st.markdown("#### 👤 1. ข้อมูลผู้ประเมิน/ผู้ให้ข้อมูล")
col1, col2 = st.columns(2)
with col1:
    resp_id = st.text_input("รหัสอ้างอิง (ID):", placeholder="เช่น EMP-001")
with col2:
    resp_group = st.selectbox("กลุ่มเป้าหมาย:", ["ฝ่ายบริหาร", "แรงงานไทย", "แรงงานข้ามชาติ", "ชุมชน", "คู่ค้า"])

st.markdown("<br>#### 🛠️ 2. เลือกเครื่องมือประเมิน", unsafe_allow_html=True)
choice = st.selectbox("คลิกเพื่อเลือกเครื่องมือที่ต้องการใช้งาน:", [
    "Tool 1: ประเมินสถานะองค์กร",
    "Tool 2: แบบสอบถามหน้างาน",
    "Tool 3: สัมภาษณ์เชิงลึก (Evidence)",
    "Tool 4: บันทึกการสังเกตการณ์",
    "Tool 5: ประเมินนัยสำคัญ (Salient Rule)",
    "Tool 6: ระบบวิเคราะห์ AI Triangulation"
])

st.markdown("<hr style='border: 1px solid #e0e0e0; margin: 30px 0;'>", unsafe_allow_html=True)

if not resp_id:
    st.info("👆 กรุณากรอก รหัสอ้างอิง (ID) ด้านบน เพื่อเปิดใช้งานแบบฟอร์มประเมิน")
    st.stop()

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ==========================================
# --- 5. TOOLS LOGIC (คำถามเต็ม 100% และจัด Layout ใหม่) ---
# ==========================================

# --- TOOL 1: แบบประเมินสถานะองค์กร ---
if choice == "Tool 1: ประเมินสถานะองค์กร":
    st.markdown('<div class="premium-header"><h3>Tool 1: ประเมินสถานะองค์กร</h3><p>Policy Gap Analysis</p></div>', unsafe_allow_html=True)
    with st.form("form_t1"):
        st.markdown("**หมวด A: การกำกับดูแลและนโยบาย (Governance & Policy)**")
        q1_1 = st.radio("1.1 องค์กรมี 'นโยบายสิทธิมนุษยชน' ที่เป็นลายลักษณ์อักษรหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        q1_2 = st.radio("1.2 นโยบายครอบคลุมประเด็นสำคัญ (แรงงานข้ามชาติ, ชุมชน, สิ่งแวดล้อม) หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        q1_3 = st.radio("1.3 มีการสื่อสารนโยบายในภาษาที่พนักงานและคู่ค้าเข้าใจหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        q1_4 = st.radio("1.4 มีการแต่งตั้งผู้รับผิดชอบระดับบริหาร (Board Level) หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        
        st.markdown("**หมวด B: กระบวนการตรวจสอบอย่างรอบด้าน (Due Diligence)**")
        q2_1 = st.radio("2.1 มีการประเมินความเสี่ยงด้านสิทธิมนุษยชน (HRA) ประจำปีหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        q2_2 = st.radio("2.2 มีระบบการตรวจสอบย้อนกลับ (Traceability) ในห่วงโซ่อุปทานหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        q2_3 = st.radio("2.3 มีแผนจัดการความเสี่ยง (Mitigation Plan) ที่ชัดเจนและนำไปใช้จริงหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        
        st.markdown("**หมวด C: กลไกการร้องเรียนและการเยียวยา (Grievance & Remediation)**")
        q3_1 = st.radio("3.1 มีช่องทางรับเรื่องร้องเรียนที่ปลอดภัย เป็นความลับ และเข้าถึงได้ง่ายหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        q3_2 = st.radio("3.2 มีมาตรการคุ้มครองผู้แจ้งเบาะแส (Non-Retaliation Policy) หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        q3_3 = st.radio("3.3 มีขั้นตอนการเยียวยา (Remediation) แก่ผู้ได้รับผลกระทบเมื่อเกิดการละเมิดหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("บันทึกข้อมูล Tool 1"):
            sheet = connect_to_sheet()
            if sheet:
                detail = f"A(1.1:{q1_1}, 1.2:{q1_2}, 1.3:{q1_3}, 1.4:{q1_4}) | B(2.1:{q2_1}, 2.2:{q2_2}, 2.3:{q2_3}) | C(3.1:{q3_1}, 3.2:{q3_2}, 3.3:{q3_3})"
                sheet.append_row([now, "Tool 1", resp_id, resp_group, "Policy Gap Analysis", detail, "", "", "", ""])
                st.success("✅ บันทึกข้อมูลครบทุกข้อลง Google Sheet เรียบร้อย")

# --- TOOL 2: แบบสอบถามหน้างาน ---
elif choice == "Tool 2: แบบสอบถามหน้างาน":
    st.markdown('<div class="premium-header"><h3>Tool 2: แบบสอบถามการปฏิบัติหน้างาน</h3><p>Worker Survey (ประเมินด้วยสไลเดอร์)</p></div>', unsafe_allow_html=True)
    with st.form("form_t2"):
        st.markdown("**ส่วนที่ 1: สภาพการจ้างและค่าจ้าง**")
        s1_1 = st.select_slider("1.1 ท่านได้รับค่าจ้างตรงเวลาและครบถ้วนตามสัญญาหรือไม่?", options=["แย่มาก (1)", "แย่ (2)", "ปานกลาง (3)", "ดี (4)", "ดีมาก (5)"], value="ปานกลาง (3)")
        s1_2 = st.select_slider("1.2 ท่านได้รับวันหยุดอย่างน้อย 1 วันต่อสัปดาห์ (หรือตามกฎหมาย) หรือไม่?", options=["แย่มาก (1)", "แย่ (2)", "ปานกลาง (3)", "ดี (4)", "ดีมาก (5)"], value="ปานกลาง (3)")
        s1_3 = st.select_slider("1.3 ท่านเป็นผู้เก็บเอกสารประจำตัว (เช่น พาสปอร์ต, บัตรประชาชน) ไว้เองใช่หรือไม่?", options=["แย่มาก (1)", "แย่ (2)", "ปานกลาง (3)", "ดี (4)", "ดีมาก (5)"], value="ปานกลาง (3)")
        st.markdown("<hr>", unsafe_allow_html=True)
        
        st.markdown("**ส่วนที่ 2: ความปลอดภัยและสุขอนามัย (OHS)**")
        s2_1 = st.select_slider("2.1 อุปกรณ์ป้องกันอันตราย (PPE) มีเพียงพอและอยู่ในสภาพพร้อมใช้งานหรือไม่?", options=["แย่มาก (1)", "แย่ (2)", "ปานกลาง (3)", "ดี (4)", "ดีมาก (5)"], value="ปานกลาง (3)")
        s2_2 = st.select_slider("2.2 ท่านได้รับการฝึกอบรมด้านความปลอดภัยก่อนเริ่มปฏิบัติงานหรือไม่?", options=["แย่มาก (1)", "แย่ (2)", "ปานกลาง (3)", "ดี (4)", "ดีมาก (5)"], value="ปานกลาง (3)")
        st.markdown("<hr>", unsafe_allow_html=True)
        
        st.markdown("**ส่วนที่ 3: การปฏิบัติต่อแรงงานและความเท่าเทียม**")
        s3_1 = st.select_slider("3.1 หัวหน้างานปฏิบัติต่อท่านด้วยความเคารพ (ปราศจากการดุด่า ข่มขู่ หรือล่วงละเมิด) ใช่หรือไม่?", options=["แย่มาก (1)", "แย่ (2)", "ปานกลาง (3)", "ดี (4)", "ดีมาก (5)"], value="ปานกลาง (3)")
        s3_2 = st.select_slider("3.2 ท่านสามารถเข้าถึงน้ำดื่มที่สะอาดและห้องน้ำที่เพียงพอได้ตลอดเวลาใช่หรือไม่?", options=["แย่มาก (1)", "แย่ (2)", "ปานกลาง (3)", "ดี (4)", "ดีมาก (5)"], value="ปานกลาง (3)")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("บันทึกข้อมูล Tool 2"):
            sheet = connect_to_sheet()
            if sheet:
                detail = f"การจ้าง(1.1:{s1_1}, 1.2:{s1_2}, 1.3:{s1_3}) | ความปลอดภัย(2.1:{s2_1}, 2.2:{s2_2}) | การปฏิบัติ(3.1:{s3_1}, 3.2:{s3_2})"
                sheet.append_row([now, "Tool 2", resp_id, resp_group, "Worker Practice", detail, "", "", "", ""])
                st.success("✅ ส่งข้อมูลแบบสอบถาม Tool 2 สำเร็จ")

# --- TOOL 3: สัมภาษณ์เชิงลึก ---
elif choice == "Tool 3: สัมภาษณ์เชิงลึก (Evidence)":
    st.markdown('<div class="premium-header"><h3>Tool 3: สัมภาษณ์เชิงลึก</h3><p>In-depth Interview & Evidence</p></div>', unsafe_allow_html=True)
    with st.form("form_t3"):
        st.markdown("**🔍 หัวข้อการตรวจสอบ (เลือกข้อที่พบประเด็นความเสี่ยง)**")
        topics = st.multiselect("คลิกเพื่อเลือกประเด็นที่พูดคุย:", 
            ["การสรรหา/ค่านายหน้า (Recruitment Fees)", "ความเข้าใจในสัญญาจ้าง", "การจ่ายค่าจ้าง/โอที", 
             "เสรีภาพในการเดินทาง/ลาออก", "สภาพที่พักอาศัย/โรงอาหาร", "กลไกการร้องเรียน", "การเลือกปฏิบัติ/การคุกคาม"])
             
        st.markdown("<br>**✍️ บันทึกคำให้การ (Testimony / Evidence-based)**", unsafe_allow_html=True)
        testimony = st.text_area("สรุปคำพูดหรือหลักฐานที่พบจากการสัมภาษณ์:", height=150,
                                 placeholder="ตัวอย่าง: 'พนักงานแจ้งว่าต้องจ่ายค่านายหน้า 5,000 บาทให้กับเอเจนซี่...'")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("บันทึกข้อมูล Tool 3"):
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([now, "Tool 3", resp_id, resp_group, ", ".join(topics), testimony, "", "", "", ""])
                st.success("✅ บันทึกหลักฐานบทสัมภาษณ์สำเร็จ")

# --- TOOL 4: บันทึกการสังเกตการณ์ ---
elif choice == "Tool 4: บันทึกการสังเกตการณ์":
    st.markdown('<div class="premium-header"><h3>Tool 4: บันทึกการสังเกตการณ์หน้างาน</h3><p>Site Observation Log</p></div>', unsafe_allow_html=True)
    with st.form("form_t4"):
        st.markdown("**🔎 เช็คลิสต์การตรวจประเมินพื้นที่ (ติ๊กข้อที่ปฏิบัติได้ถูกต้อง)**")
        o1 = st.checkbox("1. มีการติดประกาศนโยบายและสิทธิแรงงานในพื้นที่ที่มองเห็นได้ชัดเจน")
        o2 = st.checkbox("2. ทางหนีไฟและอุปกรณ์ดับเพลิงไม่มีสิ่งกีดขวางและอยู่ในสภาพพร้อมใช้งาน")
        o3 = st.checkbox("3. พนักงานในสายการผลิตสวมใส่อุปกรณ์ PPE ถูกต้องตามลักษณะงานทุกคน")
        o4 = st.checkbox("4. ตู้ยาสามัญประจำบ้านมีเวชภัณฑ์ครบถ้วนและไม่หมดอายุ")
        o5 = st.checkbox("5. สภาพแวดล้อมที่พัก/โรงอาหารมีความสะอาดและถูกสุขลักษณะ")
        o6 = st.checkbox("6. มีแสงสว่างและการระบายอากาศที่เพียงพอในพื้นที่ทำงาน")
        
        st.markdown("<br>", unsafe_allow_html=True)
        obs_detail = st.text_area("บันทึกสิ่งที่พบเพิ่มเติมจากการเดินสำรวจ (จุดที่ต้องแก้ไข/ปรับปรุง):", height=100)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("บันทึกข้อมูล Tool 4"):
            sheet = connect_to_sheet()
            if sheet:
                checklist_result = f"O1:{o1}, O2:{o2}, O3:{o3}, O4:{o4}, O5:{o5}, O6:{o6}"
                detail = f"[Checklist: {checklist_result}] | Note: {obs_detail}"
                sheet.append_row([now, "Tool 4", resp_id, resp_group, "Site Observation", detail, "", "", "", ""])
                st.success("✅ บันทึก Log การสังเกตการณ์สำเร็จ")

# --- TOOL 5: ประเมินนัยสำคัญ ---
elif choice == "Tool 5: ประเมินนัยสำคัญ (Salient Rule)":
    st.markdown('<div class="premium-header"><h3>Tool 5: Human Rights Risk Matrix</h3><p>คำนวณตามหลัก "ความร้ายแรงนำ" (Severity-led Rule)</p></div>', unsafe_allow_html=True)
    
    st.markdown("**📌 1. ระบุประเด็นความเสี่ยง (เลือกตามมาตรฐานสากล ILO/UNGPs)**")
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
    
    st.markdown("<hr style='border: 1px dashed #ccc;'>", unsafe_allow_html=True)
    st.markdown("**📌 2. ประเมินระดับความรุนแรง (Severity) ด้วยสไลเดอร์**")
    scale = st.slider("Scale (ความรุนแรงของผลกระทบ)", 1, 5, 1)
    scope = st.slider("Scope (จำนวนผู้ได้รับผลกระทบ)", 1, 5, 1)
    remedy = st.slider("Remediability (ความยากในการเยียวยา)", 1, 5, 1)
    
    sev_max = max(scale, scope, remedy)
    st.markdown("<hr style='border: 1px dashed #ccc;'>", unsafe_allow_html=True)
    likelihood = st.slider("📌 3. Likelihood (โอกาสที่จะเกิด)", 1, 5, 1)
    score = sev_max * likelihood

    st.info(f"**🔴 Severity Max (ระดับความรุนแรงสูงสุด): {sev_max} | 🟡 Likelihood (โอกาสเกิด): {likelihood} | 📊 Total Score: {score}**")
    
    is_salient = "YES" if sev_max == 5 else "NO"
    if is_salient == "YES":
        st.markdown('<div class="salient-badge">🚨 SALIENT ISSUE: ความเสี่ยงระดับสูงสุด</div>', unsafe_allow_html=True)

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
    st.markdown(f"<table class='heat-table'>{rows}</table><p style='text-align:center; color: #666; margin-top: 10px;'><small>แนวนอน: Severity | แนวตั้ง: Likelihood</small></p>", unsafe_allow_html=True)

    if st.button("บันทึกประเด็นนัยสำคัญ"):
        sheet = connect_to_sheet()
        if sheet:
            detail = f"Scale:{scale}, Scope:{scope}, Remedy:{remedy}"
            sheet.append_row([now, "Tool 5", resp_id, resp_group, issue, detail, sev_max, likelihood, score, is_salient])
            st.success("✅ บันทึกความเสี่ยงเรียบร้อย ข้อมูลเข้าช่อง Salient อย่างเป็นระเบียบ")

# --- TOOL 6: AI Triangulation ---
elif choice == "Tool 6: ระบบวิเคราะห์ AI Triangulation":
    st.markdown('<div class="premium-header"><h3>Tool 6: AI-Augmented Triangulation</h3><p>ระบบสอบทานความขัดแย้งของข้อมูล</p></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background-color: #FFFFFF; padding: 25px; border-left: 6px solid #EF4444; border-radius: 10px; margin-bottom: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
        <h4 style="color: #EF4444; margin-top: 0;">🚩 พบความขัดแย้งเชิงนโยบาย (Policy vs Practice)</h4>
        <p><b>ประเด็น:</b> สัญญาจ้างไม่เป็นภาษาที่พนักงานเข้าใจ</p>
        <p style="color: #555; background: #F8FAFB; padding: 10px; border-radius: 5px;"><i>🗣️ อ้างอิงคำสัมภาษณ์ (ID: EMP-045):</i> "ผมเซ็นไปโดยไม่รู้ว่าเป็นภาษาอะไร เพราะไม่ได้มีล่ามแปลให้ฟัง..."</p>
        <p style="color: #265F36; font-size: 14px;">❌ <i>ขัดแย้งกับนโยบาย (Tool 1 หมวด A ข้อ 1.3):</i> ฝ่ายบริหารตอบว่ามีการสื่อสารในภาษาที่เข้าใจแล้ว</p>
    </div>
    
    <div style="background-color: #FFFFFF; padding: 25px; border-left: 6px solid #F9A818; border-radius: 10px; margin-bottom: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
        <h4 style="color: #F9A818; margin-top: 0;">⚠️ ประเด็นเฝ้าระวังเรื่องค่าธรรมเนียม</h4>
        <p><b>ประเด็น:</b> พบร่องรอยการจ่ายค่านายหน้า</p>
        <p style="color: #555; background: #F8FAFB; padding: 10px; border-radius: 5px;"><i>📄 อ้างอิงหลักฐาน (ID: EMP-012):</i> "จ่ายให้เอเจนซี่ฝั่งพม่าไป 15,000 บาทก่อนเข้ามาทำงานที่นี่"</p>
    </div>
    """, unsafe_allow_html=True)
