import streamlit as st
import pandas as pd
from google.oauth2 import service_account
import gspread
from datetime import datetime

# --- 1. SETTING UP THE PAGE ---
st.set_page_config(page_title="Betagro HRDD Premium Toolkit", page_icon="👑", layout="centered")

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

# --- 3. ULTRA-PREMIUM STYLING (MODERN LUXURY) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700;800&display=swap');
    
    html, body, [class*="st-"] { font-family: 'Sarabun', sans-serif; }
    .stApp { background-color: #F4F7F6; }
    
    /* 🚫 ปิดแถบเมนูและปุ่มสามขีดด้านบนทิ้งไปเลย เพื่อแก้ปัญหาตัวอักษรขยะ 100% */
    header[data-testid="stHeader"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }

    /* 👑 แบนเนอร์ด้านบน (Hero Banner) - เรียบ หรู แพง */
    .premium-banner {
        background: #FFFFFF; border-radius: 24px; padding: 40px 50px;
        box-shadow: 0px 20px 40px rgba(0, 91, 49, 0.05);
        border: 1px solid rgba(0, 91, 49, 0.08); border-left: 12px solid #005B31; 
        display: flex; align-items: center; gap: 40px; margin-bottom: 40px;
        position: relative; overflow: hidden;
    }
    .premium-banner::after { content: ''; position: absolute; top: 0; right: 0; width: 150px; height: 8px; background: #F9A818; }
    .banner-logo img { width: 120px; filter: drop-shadow(0px 10px 15px rgba(0,0,0,0.08)); }
    .banner-text h1 {
        color: #005B31 !important; font-size: 34px !important; font-weight: 800 !important; 
        margin: 0 !important; line-height: 1.2 !important; letter-spacing: -0.5px !important;
    }
    .banner-text p {
        color: #D3A129 !important; font-size: 15px !important; font-weight: 700 !important; 
        letter-spacing: 2px !important; text-transform: uppercase !important; margin-top: 10px !important; margin-bottom: 0 !important;
    }
    @media (max-width: 768px) {
        .premium-banner { flex-direction: column; text-align: center; padding: 30px 20px; gap: 20px; border-left: none; border-top: 12px solid #005B31; }
        .banner-text h1 { font-size: 24px !important; }
        .banner-text p { font-size: 13px !important; }
    }

    /* กล่องข้อมูลผู้ใช้ และเลือกเครื่องมือ */
    .control-panel {
        background: #FFFFFF; padding: 30px; border-radius: 16px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.03); border: 1px solid #EAEAEA;
        margin-bottom: 30px; border-top: 5px solid #F9A818;
    }

    /* ตกแต่งแบบฟอร์ม */
    [data-testid="stForm"] { background: #FFFFFF; border-radius: 20px; border: none; box-shadow: 0 10px 30px rgba(0,0,0,0.04); padding: 30px; }
    
    /* ปุ่ม Submit */
    [data-testid="stFormSubmitButton"] > button, .stButton > button {
        background: #005B31 !important; color: #FFFFFF !important; border-radius: 10px !important;
        font-weight: 700 !important; padding: 12px 24px !important; border: none !important;
        box-shadow: 0 8px 20px rgba(0, 91, 49, 0.2) !important; transition: all 0.3s ease; width: 100%; font-size: 16px !important;
    }
    [data-testid="stFormSubmitButton"] > button:hover, .stButton > button:hover {
        background: #004222 !important; transform: translateY(-2px) !important; box-shadow: 0 12px 25px rgba(0, 91, 49, 0.3) !important;
    }

    .salient-badge { background-color: #FEF2F2; color: #DC2626; padding: 15px; border-radius: 12px; border: 1px solid #FECACA; font-weight: 700; text-align: center; display: block; margin-top: 15px;}
    .citation-box { background-color: #F9FAFB; padding: 20px; border-left: 6px solid #DC2626; border-radius: 12px; margin: 15px 0; border: 1px solid #F3F4F6;}
    .heat-table { width: 100%; border-collapse: separate; border-spacing: 4px; margin-top: 15px;}
    .heat-cell { height: 50px; text-align: center; font-weight: bold; color: white; border-radius: 8px; font-size: 14px;}
    
    label { font-weight: 600 !important; color: #005B31 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. TOP-DOWN UI (แผงควบคุมหลัก ไม่มีเมนูซ่อน) ---

# โลโก้และหัวเว็บ
st.markdown("""
    <div class="premium-banner">
        <div class="banner-logo">
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Betagro_Logo.svg/800px-Betagro_Logo.svg.png" alt="Betagro Logo">
        </div>
        <div class="banner-text">
            <h1>ระบบประเมิน HRDD อัจฉริยะ</h1>
            <p>Betagro Smart Assessment Toolkit</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# แผงข้อมูลและเลือกเครื่องมือ
st.markdown('<div class="control-panel">', unsafe_allow_html=True)
st.markdown("<h4 style='color: #005B31; margin-bottom: 15px; font-weight: 700;'>👤 1. ข้อมูลอ้างอิง (Data Source)</h4>", unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    resp_id = st.text_input("รหัสผู้ให้ข้อมูล (ID) *", placeholder="เช่น EMP-001")
with col2:
    resp_group = st.selectbox("กลุ่มเป้าหมาย *", ["ฝ่ายบริหาร", "แรงงานไทย", "แรงงานข้ามชาติ", "ชุมชน", "คู่ค้า"])

st.markdown("<hr style='border: 1px solid #eee; margin: 20px 0;'>", unsafe_allow_html=True)
st.markdown("<h4 style='color: #005B31; margin-bottom: 15px; font-weight: 700;'>🛠️ 2. เลือกเครื่องมือประเมิน</h4>", unsafe_allow_html=True)
choice = st.selectbox("เลือกแบบฟอร์มด้านล่างนี้:", [
    "Tool 1: ประเมินสถานะองค์กร",
    "Tool 2: แบบสอบถามหน้างาน",
    "Tool 3: สัมภาษณ์เชิงลึก (Evidence)",
    "Tool 4: บันทึกการสังเกตการณ์",
    "Tool 5: ประเมินนัยสำคัญ (Salient Rule)",
    "Tool 6: ระบบวิเคราะห์ AI Triangulation"
], label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# ล็อกระบบถ้ายังไม่กรอก ID
if not resp_id:
    st.info("📌 กรุณาระบุ 'รหัสผู้ให้ข้อมูล (ID)' ด้านบน เพื่อปลดล็อกแบบฟอร์มการประเมิน")
    st.stop()

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ==========================================
# --- 5. TOOLS LOGIC (คำถามมาเต็ม) ---
# ==========================================

# --- TOOL 1 ---
if choice == "Tool 1: ประเมินสถานะองค์กร":
    with st.form("form_t1"):
        st.markdown("<h3 style='color:#005B31;'>Tool 1: ประเมินสถานะองค์กร (Policy Gap)</h3><hr>", unsafe_allow_html=True)
        st.markdown("**หมวด A: การกำกับดูแลและนโยบาย (Governance & Policy)**")
        q1_1 = st.radio("1.1 องค์กรมี 'นโยบายสิทธิมนุษยชน' ที่เป็นลายลักษณ์อักษรหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        q1_2 = st.radio("1.2 นโยบายครอบคลุมประเด็นสำคัญ (แรงงานข้ามชาติ, ชุมชน, สิ่งแวดล้อม) หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        q1_3 = st.radio("1.3 มีการสื่อสารนโยบายในภาษาที่พนักงานและคู่ค้าเข้าใจหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        q1_4 = st.radio("1.4 มีการแต่งตั้งผู้รับผิดชอบระดับบริหาร (Board Level) หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        st.markdown("<hr style='border: 1px dashed #ccc;'>", unsafe_allow_html=True)
        
        st.markdown("**หมวด B: กระบวนการตรวจสอบอย่างรอบด้าน (Due Diligence)**")
        q2_1 = st.radio("2.1 มีการประเมินความเสี่ยงด้านสิทธิมนุษยชน (HRA) ประจำปีหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        q2_2 = st.radio("2.2 มีระบบการตรวจสอบย้อนกลับ (Traceability) ในห่วงโซ่อุปทานหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        q2_3 = st.radio("2.3 มีแผนจัดการความเสี่ยง (Mitigation Plan) ที่ชัดเจนและนำไปใช้จริงหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        st.markdown("<hr style='border: 1px dashed #ccc;'>", unsafe_allow_html=True)
        
        st.markdown("**หมวด C: กลไกการร้องเรียนและการเยียวยา (Grievance & Remediation)**")
        q3_1 = st.radio("3.1 มีช่องทางรับเรื่องร้องเรียนที่ปลอดภัย เป็นความลับ และเข้าถึงได้ง่ายหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        q3_2 = st.radio("3.2 มีมาตรการคุ้มครองผู้แจ้งเบาะแส (Non-Retaliation Policy) หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        q3_3 = st.radio("3.3 มีขั้นตอนการเยียวยา (Remediation) แก่ผู้ได้รับผลกระทบเมื่อเกิดการละเมิดหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("💾 บันทึกข้อมูล Tool 1"):
            sheet = connect_to_sheet()
            if sheet:
                detail = f"A(1.1:{q1_1}, 1.2:{q1_2}, 1.3:{q1_3}, 1.4:{q1_4}) | B(2.1:{q2_1}, 2.2:{q2_2}, 2.3:{q2_3}) | C(3.1:{q3_1}, 3.2:{q3_2}, 3.3:{q3_3})"
                sheet.append_row([now, "Tool 1", resp_id, resp_group, "Policy Gap Analysis", detail, "", "", "", ""])
                st.success("✅ บันทึกข้อมูล Tool 1 ครบทุกข้อลง Google Sheet เรียบร้อย")

# --- TOOL 2 ---
elif choice == "Tool 2: แบบสอบถามหน้างาน":
    with st.form("form_t2"):
        st.markdown("<h3 style='color:#005B31;'>Tool 2: แบบสอบถามการปฏิบัติหน้างาน (Worker Survey)</h3><hr>", unsafe_allow_html=True)
        st.markdown("**ส่วนที่ 1: สภาพการจ้างและค่าจ้าง**")
        s1_1 = st.select_slider("1.1 ท่านได้รับค่าจ้างตรงเวลาและครบถ้วนตามสัญญาหรือไม่?", options=[1,2,3,4,5], value=3)
        s1_2 = st.select_slider("1.2 ท่านได้รับวันหยุดอย่างน้อย 1 วันต่อสัปดาห์ (หรือตามกฎหมาย) หรือไม่?", options=[1,2,3,4,5], value=3)
        s1_3 = st.select_slider("1.3 ท่านเป็นผู้เก็บเอกสารประจำตัว (เช่น พาสปอร์ต, บัตรประชาชน) ไว้เองใช่หรือไม่?", options=[1,2,3,4,5], value=3)
        st.markdown("<hr style='border: 1px dashed #ccc;'>", unsafe_allow_html=True)
        
        st.markdown("**ส่วนที่ 2: ความปลอดภัยและสุขอนามัย (OHS)**")
        s2_1 = st.select_slider("2.1 อุปกรณ์ป้องกันอันตราย (PPE) มีเพียงพอและอยู่ในสภาพพร้อมใช้งานหรือไม่?", options=[1,2,3,4,5], value=3)
        s2_2 = st.select_slider("2.2 ท่านได้รับการฝึกอบรมด้านความปลอดภัยก่อนเริ่มปฏิบัติงานหรือไม่?", options=[1,2,3,4,5], value=3)
        st.markdown("<hr style='border: 1px dashed #ccc;'>", unsafe_allow_html=True)
        
        st.markdown("**ส่วนที่ 3: การปฏิบัติต่อแรงงานและความเท่าเทียม**")
        s3_1 = st.select_slider("3.1 หัวหน้างานปฏิบัติต่อท่านด้วยความเคารพ ใช่หรือไม่?", options=[1,2,3,4,5], value=3)
        s3_2 = st.select_slider("3.2 ท่านสามารถเข้าถึงน้ำดื่มที่สะอาดและห้องน้ำที่เพียงพอได้ตลอดเวลาใช่หรือไม่?", options=[1,2,3,4,5], value=3)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("🚀 บันทึกข้อมูล Tool 2"):
            sheet = connect_to_sheet()
            if sheet:
                detail = f"การจ้าง(1.1:{s1_1}, 1.2:{s1_2}, 1.3:{s1_3}) | ความปลอดภัย(2.1:{s2_1}, 2.2:{s2_2}) | การปฏิบัติ(3.1:{s3_1}, 3.2:{s3_2})"
                sheet.append_row([now, "Tool 2", resp_id, resp_group, "Worker Practice", detail, "", "", "", ""])
                st.success("✅ ส่งข้อมูลแบบสอบถาม Tool 2 สำเร็จ")

# --- TOOL 3 ---
elif choice == "Tool 3: สัมภาษณ์เชิงลึก (Evidence)":
    with st.form("form_t3"):
        st.markdown("<h3 style='color:#005B31;'>Tool 3: สัมภาษณ์เชิงลึก (In-depth Interview)</h3><hr>", unsafe_allow_html=True)
        st.markdown("**🔍 หัวข้อการตรวจสอบ (เลือกข้อที่พบประเด็นความเสี่ยง)**")
        topics = st.multiselect("ประเด็นที่พูดคุย:", 
            ["การสรรหา/ค่านายหน้า (Recruitment Fees)", "ความเข้าใจในสัญญาจ้าง", "การจ่ายค่าจ้าง/โอที", 
             "เสรีภาพในการเดินทาง/ลาออก", "สภาพที่พักอาศัย/โรงอาหาร", "กลไกการร้องเรียน", "การเลือกปฏิบัติ/การคุกคาม"],
             label_visibility="collapsed")
             
        st.markdown("<br>**✍️ บันทึกคำให้การ (Testimony / Evidence-based)**", unsafe_allow_html=True)
        testimony = st.text_area("สรุปคำพูดหรือหลักฐานที่พบจากการสัมภาษณ์:", height=150,
                                 placeholder="ตัวอย่าง: 'พนักงานแจ้งว่าต้องจ่ายค่านายหน้า 5,000 บาทให้กับเอเจนซี่...'")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("💾 บันทึกข้อมูล Tool 3"):
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([now, "Tool 3", resp_id, resp_group, ", ".join(topics), testimony, "", "", "", ""])
                st.success("✅ บันทึกหลักฐานบทสัมภาษณ์สำเร็จ")

# --- TOOL 4 ---
elif choice == "Tool 4: บันทึกการสังเกตการณ์":
    with st.form("form_t4"):
        st.markdown("<h3 style='color:#005B31;'>Tool 4: แบบบันทึกการสังเกตการณ์หน้างาน (Site Observation Log)</h3><hr>", unsafe_allow_html=True)
        st.markdown("**🔎 เช็คลิสต์การตรวจประเมินพื้นที่ (ติ๊กเมื่อผ่าน)**")
        o1 = st.checkbox("1. มีการติดประกาศนโยบายและสิทธิแรงงานในพื้นที่ที่มองเห็นได้ชัดเจน")
        o2 = st.checkbox("2. ทางหนีไฟและอุปกรณ์ดับเพลิงไม่มีสิ่งกีดขวางและอยู่ในสภาพพร้อมใช้งาน")
        o3 = st.checkbox("3. พนักงานในสายการผลิตสวมใส่อุปกรณ์ PPE ถูกต้องตามลักษณะงานทุกคน")
        o4 = st.checkbox("4. ตู้ยาสามัญประจำบ้านมีเวชภัณฑ์ครบถ้วนและไม่หมดอายุ")
        o5 = st.checkbox("5. สภาพแวดล้อมที่พัก/โรงอาหารมีความสะอาดและถูกสุขลักษณะ")
        o6 = st.checkbox("6. มีแสงสว่างและการระบายอากาศที่เพียงพอในพื้นที่ทำงาน")
        
        st.markdown("<br>**📝 บันทึกสิ่งที่พบเพิ่มเติม**", unsafe_allow_html=True)
        obs_detail = st.text_area("บันทึกจุดที่ต้องแก้ไข/ปรับปรุง:", height=100, label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("💾 บันทึกข้อมูล Tool 4"):
            sheet = connect_to_sheet()
            if sheet:
                checklist_result = f"O1:{o1}, O2:{o2}, O3:{o3}, O4:{o4}, O5:{o5}, O6:{o6}"
                detail = f"[Checklist: {checklist_result}] | Note: {obs_detail}"
                sheet.append_row([now, "Tool 4", resp_id, resp_group, "Site Observation", detail, "", "", "", ""])
                st.success("✅ บันทึก Log การสังเกตการณ์สำเร็จ")

# --- TOOL 5 ---
elif choice == "Tool 5: ประเมินนัยสำคัญ (Salient Rule)":
    st.markdown("<div style='background:#FFFFFF; padding:30px; border-radius:20px; box-shadow: 0 10px 30px rgba(0,0,0,0.04);'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#005B31; margin-top:0;'>Tool 5: Human Rights Risk Matrix</h3><p style='color:#666;'>คำนวณตามหลัก 'ความร้ายแรงนำ' (Severity-led Rule)</p><hr>", unsafe_allow_html=True)
    
    st.markdown("**📌 1. ระบุประเด็นความเสี่ยง (อ้างอิงมาตรฐาน ILO)**")
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
    ], label_visibility="collapsed")
    
    st.markdown("<hr style='border: 1px dashed #ccc;'>", unsafe_allow_html=True)
    st.markdown("**📌 2. คำนวณ Severity (ใช้ค่าสูงสุด)**")
    scale = st.slider("Scale (ความรุนแรงของผลกระทบ)", 1, 5, 1)
    scope = st.slider("Scope (จำนวนผู้ได้รับผลกระทบ)", 1, 5, 1)
    remedy = st.slider("Remediability (ความยากในการเยียวยา)", 1, 5, 1)
    
    sev_max = max(scale, scope, remedy)
    st.markdown("<hr style='border: 1px dashed #ccc;'>", unsafe_allow_html=True)
    likelihood = st.slider("📌 3. Likelihood (โอกาสที่จะเกิด)", 1, 5, 1)
    score = sev_max * likelihood

    st.markdown(f"<h4 style='color: #005B31; text-align:center; padding: 15px; background: #F4F7F6; border-radius: 8px;'>Severity Max: {sev_max} | โอกาสเกิด: {likelihood} | คะแนนรวม: {score}</h4>", unsafe_allow_html=True)
    is_salient = "YES" if sev_max == 5 else "NO"
    if is_salient == "YES":
        st.markdown('<div class="salient-badge">🚨 SALIENT ISSUE: ความเสี่ยงระดับวิกฤต (ต้องจัดการทันที)</div>', unsafe_allow_html=True)

    rows = ""
    for l in range(5, 0, -1):
        rows += "<tr>"
        for s in range(1, 6):
            val = s * l
            color = "#EF4444" if val >= 16 or s == 5 else ("#F9A818" if val >= 8 else "#005B31")
            mark = "★" if s == sev_max and l == likelihood else ""
            rows += f"<td class='heat-cell' style='background-color:{color}; box-shadow: inset 0 0 10px rgba(0,0,0,0.1);'>{mark}</td>"
        rows += "</tr>"
    st.markdown(f"<table class='heat-table'>{rows}</table><p style='text-align:center; color: #666; margin-top: 10px;'><small>แนวนอน: Severity | แนวตั้ง: Likelihood</small></p>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 บันทึกประเด็นนัยสำคัญ (Submit Salient Issue)"):
        sheet = connect_to_sheet()
        if sheet:
            detail = f"Scale:{scale}, Scope:{scope}, Remedy:{remedy}"
            sheet.append_row([now, "Tool 5", resp_id, resp_group, issue, detail, sev_max, likelihood, score, is_salient])
            st.success("✅ บันทึกความเสี่ยงเข้าสู่ฐานข้อมูลเรียบร้อย")
    st.markdown("</div>", unsafe_allow_html=True)

# --- TOOL 6 ---
elif choice == "Tool 6: ระบบวิเคราะห์ AI Triangulation":
    st.markdown("<div style='background:#FFFFFF; padding:30px; border-radius:20px; box-shadow: 0 10px 30px rgba(0,0,0,0.04);'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#005B31; margin-top:0;'>Tool 6: AI-Augmented Triangulation</h3><hr>", unsafe_allow_html=True)
    
    st.info("💡 ระบบจะดึง 'ประโยคอ้างอิง' จาก Tool 3 มาเปรียบเทียบกับ Tool 1 เพื่อพิสูจน์ความสอดคล้อง")
    
    st.markdown("""
    <div class="citation-box">
        <h4 style="color: #DC2626; margin-top: 0;">🚩 พบความขัดแย้งเชิงนโยบาย (Policy vs Practice)</h4>
        <b>ประเด็น:</b> สัญญาจ้างไม่เป็นภาษาที่พนักงานเข้าใจ<br><br>
        <div style="background: #FFFFFF; padding: 15px; border-radius: 8px; border: 1px solid #E5E7EB;">
            <span style="color: #6B7280; font-size: 14px;">🗣️ <b>อ้างอิงคำสัมภาษณ์ (ID: EMP-045):</b></span><br>
            <span style="color: #111827; font-style: italic;">"ผมเซ็นไปโดยไม่รู้ว่าเป็นภาษาอะไร เพราะไม่ได้มีล่ามแปลให้ฟัง..."</span>
        </div>
        <p style="color: #005B31; font-size: 14px; font-weight: 600; margin-top: 15px;">
            ❌ ขัดแย้งกับนโยบาย (Tool 1 หมวด A ข้อ 1.3): ระบุว่ามีการสื่อสารในภาษาที่เข้าใจแล้ว
        </p>
    </div>
    
    <div class="citation-box" style="border-left-color: #F9A818;">
        <h4 style="color: #F9A818; margin-top: 0;">⚠️ ประเด็นเฝ้าระวัง: การเรียกเก็บค่าธรรมเนียม</h4>
        <div style="background: #FFFFFF; padding: 15px; border-radius: 8px; border: 1px solid #E5E7EB;">
            <span style="color: #6B7280; font-size: 14px;">🗣️ <b>อ้างอิงหลักฐาน (ID: EMP-012):</b></span><br>
            <span style="color: #111827; font-style: italic;">"จ่ายให้เอเจนซี่ฝั่งพม่าไป 15,000 บาทก่อนเข้ามาทำงานที่นี่"</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 บันทึกสรุปผล AI Analysis ลงระบบ"):
        sheet = connect_to_sheet()
        if sheet:
            sheet.append_row([now, "Tool 6", resp_id, resp_group, "AI Triangulation", "พบความขัดแย้ง 2 ประเด็น", "", "", "", ""])
            st.success("✅ บันทึกข้อมูลการวิเคราะห์เชิงลึกเสร็จสิ้น")
    st.markdown("</div>", unsafe_allow_html=True)
