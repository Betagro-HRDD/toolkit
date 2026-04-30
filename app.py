import streamlit as st
import pandas as pd
from google.oauth2 import service_account
import gspread
from datetime import datetime

# --- 1. SETTING UP THE PAGE ---
st.set_page_config(
    page_title="Betagro HRDD Premium Toolkit", 
    page_icon="https://www.betagro.com/favicon.ico", 
    layout="centered" 
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

# --- 3. ULTRA PREMIUM BETAGRO STYLING ---
st.markdown("""
    <style>
    /* นำเข้าฟอนต์ Sarabun และปรับน้ำหนักให้ดูแพง */
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="st-"] { 
        font-family: 'Sarabun', sans-serif; 
    }
    
    /* พื้นหลังสีเทาอ่อนสุดหรู เพื่อขับให้กล่องสีขาวเด้งขึ้นมา */
    .stApp { background-color: #F8F9FA; }
    
    /* ซ่อนเมนูขยะทั้งหมด */
    header {visibility: hidden !important;}
    [data-testid="collapsedControl"], [data-testid="stToolbar"] {display: none !important;}
    
    /* -------------------------------------- */
    /* 🎨 BETAGRO CORPORATE IDENTITY (CI) */
    /* สีเขียวเบทาโกร: #005B31 */
    /* สีทองพรีเมียม: #D3A129 หรือ #E5B33A */
    /* -------------------------------------- */

    /* ตกแต่งกล่อง Form ให้หรูหราเหมือนแอปการเงิน/องค์กรชั้นนำ */
    [data-testid="stForm"] {
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 40px 30px;
        box-shadow: 0px 10px 40px rgba(0, 91, 49, 0.08); /* เงาสีเขียวอ่อนๆ */
        border: 1px solid rgba(0, 91, 49, 0.05);
        border-top: 6px solid #005B31; /* แถบบนสีเขียวเข้ม Betagro */
        transition: all 0.3s ease;
    }
    
    /* ตกแต่งปุ่ม Submit ให้ดูแพงแบบมีมิติ */
    [data-testid="stFormSubmitButton"] > button, .stButton > button {
        background: linear-gradient(135deg, #005B31 0%, #004222 100%) !important; /* ไล่สีเขียวเข้ม */
        color: white !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        letter-spacing: 0.5px;
        border: 1px solid #004222 !important;
        padding: 12px 24px !important;
        box-shadow: 0 4px 15px rgba(0, 91, 49, 0.2) !important;
        transition: all 0.3s ease !important;
        width: 100%;
        text-transform: uppercase;
    }
    [data-testid="stFormSubmitButton"] > button:hover, .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(0, 91, 49, 0.35) !important;
        background: linear-gradient(135deg, #006B3A 0%, #005B31 100%) !important;
    }

    /* ตกแต่งส่วนหัวของ Tool (Premium Header) */
    .premium-header {
        background: #FFFFFF;
        padding: 20px 25px;
        border-radius: 12px;
        text-align: left;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
        margin-bottom: 25px;
        border-left: 8px solid #D3A129; /* แถบข้างสีทองพรีเมียม */
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .premium-header h3 { color: #005B31 !important; margin: 0; font-weight: 700; font-size: 22px; }
    .premium-header p { color: #666 !important; margin: 5px 0 0 0; font-weight: 400; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }
    
    /* กล่องข้อมูลผู้ใช้ (User Profile Card) */
    .user-card {
        background: #FFFFFF;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.02);
        border: 1px solid #EAEAEA;
        margin-bottom: 30px;
    }

    /* ป้ายเตือนความเสี่ยง (Salient Badge) สไตล์มินิมอลแต่เตะตา */
    .salient-badge { 
        background-color: #FEF2F2;
        color: #DC2626; 
        padding: 15px; 
        border-radius: 8px; 
        border: 1px solid #FECACA;
        font-weight: 700; 
        text-align: center; 
        box-shadow: 0 4px 10px rgba(220,38,38,0.1);
        margin-top: 15px;
    }
    
    /* สไตล์ตาราง Heatmap สำหรับดีไซน์พรีเมียม */
    .heat-table { width: 100%; border-collapse: separate; border-spacing: 4px; margin-top: 15px;}
    .heat-cell { height: 45px; text-align: center; font-weight: bold; color: white; border-radius: 4px; font-size: 14px; }
    
    /* ปรับแต่งเส้นคั่น (Divider) ให้หรูขึ้น */
    hr { border-color: #EAEAEA !important; margin: 25px 0 !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# --- 4. TOP-DOWN UI (Clean & Elegant) ---
# ==========================================

# ส่วนโลโก้ตรงกลาง (ปรับโครงสร้างใหม่เพื่อลบเลข 0 ที่อาจโผล่มา)
st.markdown("""
    <div style="text-align: center; padding-top: 20px; margin-bottom: 10px;">
        <img src="https://www.betagro.com/wp-content/themes/betagro/assets/img/logo-en.png" width="180">
    </div>
    <h2 style='text-align: center; color: #005B31; font-weight: 700; font-size: 28px; margin-bottom: 30px;'>ระบบประเมิน HRDD อัจฉริยะ</h2>
""", unsafe_allow_html=True)

# กล่องข้อมูลผู้ใช้งาน (ดีไซน์ใหม่)
st.markdown('<div class="user-card">', unsafe_allow_html=True)
st.markdown("<h4 style='color: #333; font-weight: 600; font-size: 18px; margin-bottom: 20px;'>👤 ข้อมูลผู้ให้ข้อมูล (Data Source)</h4>", unsafe_allow_html=True)

# ใช้ Container ในการวางเลย์เอาท์แทนการใช้ st.columns บางจุดเพื่อลดปัญหาบั๊กบนมือถือ
resp_id = st.text_input("รหัสอ้างอิง (ID) *", placeholder="เช่น EMP-001 หรือ MGT-05")
resp_group = st.selectbox("กลุ่มเป้าหมาย (Target Group) *", ["ฝ่ายบริหาร", "แรงงานไทย", "แรงงานข้ามชาติ", "ชุมชน", "คู่ค้า"])
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<h4 style='color: #333; font-weight: 600; font-size: 18px; margin-top: 10px;'>🛠️ เลือกเครื่องมือประเมิน (Assessment Tools)</h4>", unsafe_allow_html=True)
choice = st.selectbox("คลิกที่นี่เพื่อเลือกแบบฟอร์มการประเมิน:", [
    "Tool 1: ประเมินสถานะองค์กร",
    "Tool 2: แบบสอบถามหน้างาน",
    "Tool 3: สัมภาษณ์เชิงลึก (Evidence)",
    "Tool 4: บันทึกการสังเกตการณ์",
    "Tool 5: ประเมินนัยสำคัญ (Salient Rule)",
    "Tool 6: ระบบวิเคราะห์ AI Triangulation"
], label_visibility="collapsed") # ซ่อน label เพื่อความคลีน

st.markdown("<hr>", unsafe_allow_html=True)

if not resp_id:
    st.info("📌 กรุณาระบุ 'รหัสอ้างอิง (ID)' ด้านบน เพื่อปลดล็อกแบบฟอร์มการประเมิน")
    st.stop()

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ==========================================
# --- 5. TOOLS LOGIC (คำถามเต็ม 100%) ---
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
        if st.form_submit_button("บันทึกข้อมูล (Submit)"):
            sheet = connect_to_sheet()
            if sheet:
                detail = f"A(1.1:{q1_1}, 1.2:{q1_2}, 1.3:{q1_3}, 1.4:{q1_4}) | B(2.1:{q2_1}, 2.2:{q2_2}, 2.3:{q2_3}) | C(3.1:{q3_1}, 3.2:{q3_2}, 3.3:{q3_3})"
                sheet.append_row([now, "Tool 1", resp_id, resp_group, "Policy Gap Analysis", detail, "", "", "", ""])
                st.success("✅ ระบบบันทึกข้อมูล Tool 1 ลงฐานข้อมูลเรียบร้อยแล้ว")

# --- TOOL 2: แบบสอบถามหน้างาน ---
elif choice == "Tool 2: แบบสอบถามหน้างาน":
    st.markdown('<div class="premium-header"><h3>Tool 2: แบบสอบถามการปฏิบัติหน้างาน</h3><p>Worker Survey</p></div>', unsafe_allow_html=True)
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
        if st.form_submit_button("บันทึกข้อมูล (Submit)"):
            sheet = connect_to_sheet()
            if sheet:
                detail = f"การจ้าง(1.1:{s1_1}, 1.2:{s1_2}, 1.3:{s1_3}) | ความปลอดภัย(2.1:{s2_1}, 2.2:{s2_2}) | การปฏิบัติ(3.1:{s3_1}, 3.2:{s3_2})"
                sheet.append_row([now, "Tool 2", resp_id, resp_group, "Worker Practice", detail, "", "", "", ""])
                st.success("✅ ระบบบันทึกข้อมูล Tool 2 สำเร็จ")

# --- TOOL 3: สัมภาษณ์เชิงลึก ---
elif choice == "Tool 3: สัมภาษณ์เชิงลึก (Evidence)":
    st.markdown('<div class="premium-header"><h3>Tool 3: สัมภาษณ์เชิงลึก</h3><p>In-depth Interview & Evidence Base</p></div>', unsafe_allow_html=True)
    with st.form("form_t3"):
        st.markdown("**🔍 ประเด็นที่พบจากการสัมภาษณ์ (ตรวจสอบและเลือกหัวข้อ)**")
        topics = st.multiselect("หัวข้อความเสี่ยง:", 
            ["การสรรหา/ค่านายหน้า (Recruitment Fees)", "ความเข้าใจในสัญญาจ้าง", "การจ่ายค่าจ้าง/โอที", 
             "เสรีภาพในการเดินทาง/ลาออก", "สภาพที่พักอาศัย/โรงอาหาร", "กลไกการร้องเรียน", "การเลือกปฏิบัติ/การคุกคาม"],
             label_visibility="collapsed")
             
        st.markdown("<br>**✍️ บันทึกคำให้การและข้อเท็จจริง (Testimony)**", unsafe_allow_html=True)
        testimony = st.text_area("สรุปคำพูดหรือหลักฐานที่พบ:", height=120,
                                 placeholder="เช่น: 'พนักงานยืนยันว่าต้องจ่ายค่านายหน้าจำนวน 10,000 บาท ผ่านเอเจนซี่...'")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("บันทึกข้อมูล (Submit)"):
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([now, "Tool 3", resp_id, resp_group, ", ".join(topics), testimony, "", "", "", ""])
                st.success("✅ บันทึกหลักฐานบทสัมภาษณ์สำเร็จ")

# --- TOOL 4: บันทึกการสังเกตการณ์ ---
elif choice == "Tool 4: บันทึกการสังเกตการณ์":
    st.markdown('<div class="premium-header"><h3>Tool 4: บันทึกการสังเกตการณ์หน้างาน</h3><p>Site Observation Log</p></div>', unsafe_allow_html=True)
    with st.form("form_t4"):
        st.markdown("**🔎 เช็คลิสต์การตรวจประเมินพื้นที่ (ทำเครื่องหมายหากปฏิบัติได้ถูกต้อง)**")
        o1 = st.checkbox("1. มีการติดประกาศนโยบายและสิทธิแรงงานในพื้นที่ที่มองเห็นได้ชัดเจน")
        o2 = st.checkbox("2. ทางหนีไฟและอุปกรณ์ดับเพลิงไม่มีสิ่งกีดขวางและอยู่ในสภาพพร้อมใช้งาน")
        o3 = st.checkbox("3. พนักงานในสายการผลิตสวมใส่อุปกรณ์ PPE ถูกต้องตามลักษณะงานทุกคน")
        o4 = st.checkbox("4. ตู้ยาสามัญประจำบ้านมีเวชภัณฑ์ครบถ้วนและไม่หมดอายุ")
        o5 = st.checkbox("5. สภาพแวดล้อมที่พัก/โรงอาหารมีความสะอาดและถูกสุขลักษณะ")
        o6 = st.checkbox("6. มีแสงสว่างและการระบายอากาศที่เพียงพอในพื้นที่ทำงาน")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**📝 บันทึกเพิ่มเติมจากการเดินสำรวจ (จุดที่ต้องแก้ไข/ปรับปรุง)**")
        obs_detail = st.text_area("รายละเอียด:", height=80, label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("บันทึกข้อมูล (Submit)"):
            sheet = connect_to_sheet()
            if sheet:
                checklist_result = f"O1:{o1}, O2:{o2}, O3:{o3}, O4:{o4}, O5:{o5}, O6:{o6}"
                detail = f"[Checklist: {checklist_result}] | Note: {obs_detail}"
                sheet.append_row([now, "Tool 4", resp_id, resp_group, "Site Observation", detail, "", "", "", ""])
                st.success("✅ บันทึก Log การสังเกตการณ์สำเร็จ")

# --- TOOL 5: ประเมินนัยสำคัญ ---
elif choice == "Tool 5: ประเมินนัยสำคัญ (Salient Rule)":
    st.markdown('<div class="premium-header"><h3>Tool 5: Human Rights Risk Matrix</h3><p>การประเมินนัยสำคัญ (Severity-led Rule)</p></div>', unsafe_allow_html=True)
    
    st.markdown("**📌 1. ระบุประเด็นความเสี่ยง (อ้างอิงมาตรฐาน ILO / UNGPs)**")
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
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("**📌 2. ประเมินระดับความรุนแรง (Severity) ด้วยเกณฑ์ 1-5**")
    scale = st.slider("Scale (ความรุนแรงของผลกระทบต่อบุคคล)", 1, 5, 1)
    scope = st.slider("Scope (วงกว้าง/จำนวนผู้ได้รับผลกระทบ)", 1, 5, 1)
    remedy = st.slider("Remediability (ความยากในการเยียวยากลับสู่สภาพเดิม)", 1, 5, 1)
    
    sev_max = max(scale, scope, remedy)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("**📌 3. โอกาสเกิด (Likelihood)**")
    likelihood = st.slider("โอกาสที่จะเกิดเหตุการณ์นี้ (1 = น้อยที่สุด, 5 = มากที่สุด)", 1, 5, 1)
    score = sev_max * likelihood

    st.info(f"📊 **Severity Max (ความรุนแรงสูงสุด): {sev_max} | โอกาสเกิด: {likelihood} | คะแนนความเสี่ยงรวม: {score}**")
    
    is_salient = "YES" if sev_max == 5 else "NO"
    if is_salient == "YES":
        st.markdown('<div class="salient-badge">🚨 SALIENT ISSUE : พบประเด็นความเสี่ยงระดับวิกฤต</div>', unsafe_allow_html=True)

    # วาด Heat Map
    rows = ""
    for l in range(5, 0, -1):
        rows += "<tr>"
        for s in range(1, 6):
            val = s * l
            color = "#EF4444" if val >= 16 or s == 5 else ("#F9A818" if val >= 8 else "#005B31")
            mark = "★" if s == sev_max and l == likelihood else ""
            rows += f"<td class='heat-cell' style='background-color:{color};'>{mark}</td>"
        rows += "</tr>"
    st.markdown(f"<table class='heat-table'>{rows}</table><p style='text-align:center; color: #888; font-size: 12px; margin-top: 5px;'>แกน X: Severity | แกน Y: Likelihood</p>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("บันทึกประเด็นนัยสำคัญ (Submit)"):
        sheet = connect_to_sheet()
        if sheet:
            detail = f"Scale:{scale}, Scope:{scope}, Remedy:{remedy}"
            sheet.append_row([now, "Tool 5", resp_id, resp_group, issue, detail, sev_max, likelihood, score, is_salient])
            st.success("✅ บันทึกความเสี่ยงเรียบร้อย ข้อมูลเข้าสู่ฐานข้อมูลประเด็นสำคัญ (Salient Issues)")

# --- TOOL 6: AI Triangulation ---
elif choice == "Tool 6: ระบบวิเคราะห์ AI Triangulation":
    st.markdown('<div class="premium-header"><h3>Tool 6: AI Triangulation Engine</h3><p>ระบบสอบทานความขัดแย้งของข้อมูลอัตโนมัติ (Mockup)</p></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background-color: #FFFFFF; padding: 25px; border-left: 6px solid #DC2626; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.04); border: 1px solid #F3F4F6;">
        <h4 style="color: #DC2626; margin-top: 0; font-size: 18px; font-weight: 600;">🚩 ตรวจพบความขัดแย้งเชิงนโยบาย (Policy vs Practice)</h4>
        <p style="color: #333; margin-bottom: 15px;"><b>ประเด็น:</b> สัญญาจ้างไม่เป็นภาษาที่พนักงานเข้าใจ</p>
        <div style="background: #F9FAFB; padding: 15px; border-radius: 8px; margin-bottom: 10px;">
            <span style="color: #4B5563; font-size: 14px;">🗣️ <b>คำสัมภาษณ์อ้างอิง (ID: EMP-045):</b></span><br>
            <span style="color: #111827; font-style: italic;">"ผมเซ็นไปโดยไม่รู้ว่าเป็นภาษาอะไร เพราะไม่ได้มีล่ามแปลให้ฟังเลยครับ"</span>
        </div>
        <div style="color: #005B31; font-size: 14px; font-weight: 500;">
            ❌ ขัดแย้งกับข้อมูลบริหาร (Tool 1 ข้อ 1.3): ระบุว่ามีการสื่อสารนโยบายในภาษาที่เข้าใจแล้ว
        </div>
    </div>
    
    <div style="background-color: #FFFFFF; padding: 25px; border-left: 6px solid #D3A129; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.04); border: 1px solid #F3F4F6;">
        <h4 style="color: #D3A129; margin-top: 0; font-size: 18px; font-weight: 600;">⚠️ ประเด็นเฝ้าระวังความเสี่ยง (Watchlist)</h4>
        <p style="color: #333; margin-bottom: 15px;"><b>ประเด็น:</b> ร่องรอยการจ่ายค่าธรรมเนียมสรรหา (Recruitment Fees)</p>
        <div style="background: #F9FAFB; padding: 15px; border-radius: 8px;">
            <span style="color: #4B5563; font-size: 14px;">📄 <b>หลักฐานอ้างอิง (ID: EMP-012):</b></span><br>
            <span style="color: #111827; font-style: italic;">"ต้องจ่ายให้เอเจนซี่ฝั่งพม่าไป 15,000 บาท ก่อนที่จะเข้ามาทำงานที่โรงงานนี้"</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
