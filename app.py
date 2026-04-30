import streamlit as st
import pandas as pd
from google.oauth2 import service_account
import gspread
from datetime import datetime
import base64
import os

# --- 1. SETTING UP THE PAGE ---
st.set_page_config(
    page_title="Betagro HRDD Premium Toolkit", 
    page_icon="👑", 
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

# --- 3. HELPER FUNCTION: โหลดรูปภาพแบบพรีเมียม ---
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

# --- 4. THE BETAGRO SPIRIT (ULTRA PREMIUM CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="st-"] { font-family: 'Sarabun', sans-serif; }
    .stApp { background-color: #FAFCFB; }
    
    header {visibility: hidden !important;}
    [data-testid="collapsedControl"], [data-testid="stToolbar"] {display: none !important;}
    
    /* 👑 ป้ายแบนเนอร์ด้านบนสุด (Hero Banner แบบจัดระเบียบใหม่) */
    .hero-banner {
        background: linear-gradient(135deg, #005B31 0%, #003D20 100%);
        padding: 30px 40px;
        border-radius: 16px;
        border-bottom: 6px solid #D3A129; /* แถบสีทอง */
        box-shadow: 0 15px 35px rgba(0,91,49,0.2);
        margin-bottom: 35px;
        display: flex;
        align-items: center;
        gap: 30px;
    }
    .hero-title { 
        color: #FFFFFF; font-weight: 700; margin: 0; 
        font-size: 28px; letter-spacing: 1px; line-height: 1.3;
        text-align: left;
    }
    .hero-subtitle { 
        color: #D3A129; font-weight: 500; margin-top: 5px; 
        font-size: 15px; letter-spacing: 1px; text-transform: uppercase;
        text-align: left;
    }
    
    /* Responsive ให้มือถือเรียงโลโก้ไว้ด้านบน */
    @media (max-width: 768px) {
        .hero-banner { flex-direction: column; text-align: center; padding: 25px 20px; gap: 15px; }
        .hero-title { font-size: 22px; text-align: center; }
        .hero-subtitle { text-align: center; }
    }

    /* ตกแต่งกล่อง Form ให้หรูหรา */
    [data-testid="stForm"] {
        background-color: #FFFFFF; border-radius: 16px; padding: 40px 30px;
        box-shadow: 0px 10px 40px rgba(0, 91, 49, 0.06);
        border: 1px solid rgba(211, 161, 41, 0.2); 
        border-top: 6px solid #005B31; border-bottom: 6px solid #D3A129;
    }
    
    /* ตกแต่งปุ่ม Submit หรูหรา (เขียว-ทอง) */
    [data-testid="stFormSubmitButton"] > button, .stButton > button {
        background: linear-gradient(135deg, #005B31 0%, #004222 100%) !important;
        color: #F9A818 !important; border-radius: 8px !important; font-weight: 700 !important;
        font-size: 16px !important; letter-spacing: 1px; border: 1px solid #D3A129 !important;
        padding: 12px 24px !important; box-shadow: 0 6px 20px rgba(0, 91, 49, 0.25) !important; width: 100%; text-transform: uppercase;
    }
    [data-testid="stFormSubmitButton"] > button:hover, .stButton > button:hover {
        transform: translateY(-2px) !important; box-shadow: 0 8px 25px rgba(211, 161, 41, 0.4) !important; color: #FFFFFF !important;
    }

    .premium-header {
        background: #FFFFFF; padding: 20px 25px; border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03); margin-bottom: 25px;
        border-left: 8px solid #005B31; border-right: 8px solid #D3A129;
    }
    .premium-header h3 { color: #005B31 !important; margin: 0; font-weight: 700; font-size: 20px; }
    .premium-header p { color: #D3A129 !important; margin: 5px 0 0 0; font-weight: 600; font-size: 14px; text-transform: uppercase;}
    
    .user-card {
        background: #FFFFFF; padding: 25px; border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.04); border: 1px solid #EAEAEA; margin-bottom: 30px; border-top: 4px solid #D3A129;
    }

    .salient-badge { 
        background-color: #FEF2F2; color: #DC2626; padding: 15px; border-radius: 8px; 
        border: 1px solid #FECACA; font-weight: 700; text-align: center; 
        box-shadow: 0 4px 10px rgba(220,38,38,0.1); margin-top: 15px;
    }
    
    .heat-table { width: 100%; border-collapse: separate; border-spacing: 4px; margin-top: 15px;}
    .heat-cell { height: 45px; text-align: center; font-weight: bold; color: white; border-radius: 4px; font-size: 14px; }
    hr { border-color: #EAEAEA !important; margin: 25px 0 !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# --- 5. TOP-DOWN UI (The Betagro Spirit) ---
# ==========================================

# 👑 สร้าง Banner ที่รวม โลโก้ และ หัวข้อ ไว้ด้วยกัน (สวยงาม ไม่แย่งซีน)
logo_b64 = get_base64_image("logo.png") # ต้องมีไฟล์ logo.png อยู่ในโฟลเดอร์เดียวกับโค้ด
if logo_b64:
    logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="width: 110px; background: white; padding: 10px; border-radius: 50%; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">'
else:
    # เผื่อกรณีลืมอัปรูป จะโชว์แค่ไอคอนมงกุฎแทน จะได้ไม่พัง
    logo_html = '<div style="font-size: 60px;">👑</div>'

st.markdown(f"""
    <div class="hero-banner">
        <div>{logo_html}</div>
        <div>
            <h1 class="hero-title">ระบบประเมิน HRDD อัจฉริยะ</h1>
            <div class="hero-subtitle">Betagro Smart Assessment Toolkit</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# กล่องข้อมูลอ้างอิง
st.markdown('<div class="user-card">', unsafe_allow_html=True)
st.markdown("<h4 style='color: #005B31; font-weight: 600; font-size: 18px; margin-bottom: 20px;'>👤 ข้อมูลอ้างอิง (Data Source)</h4>", unsafe_allow_html=True)
resp_id = st.text_input("รหัสอ้างอิง (ID) *", placeholder="เช่น EMP-001 หรือ MGT-05")
resp_group = st.selectbox("กลุ่มเป้าหมาย (Target Group) *", ["ฝ่ายบริหาร", "แรงงานไทย", "แรงงานข้ามชาติ", "ชุมชน", "คู่ค้า"])
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<h4 style='color: #005B31; font-weight: 600; font-size: 18px; margin-top: 10px;'>🛠️ เลือกเครื่องมือประเมิน (Assessment Tools)</h4>", unsafe_allow_html=True)
choice = st.selectbox("คลิกที่นี่เพื่อเลือกแบบฟอร์มการประเมิน:", [
    "Tool 1: ประเมินสถานะองค์กร",
    "Tool 2: แบบสอบถามหน้างาน",
    "Tool 3: สัมภาษณ์เชิงลึก (Evidence)",
    "Tool 4: บันทึกการสังเกตการณ์",
    "Tool 5: ประเมินนัยสำคัญ (Salient Rule)",
    "Tool 6: ระบบวิเคราะห์ AI Triangulation"
], label_visibility="collapsed") 

st.markdown("<hr>", unsafe_allow_html=True)

if not resp_id:
    st.info("📌 กรุณาระบุ 'รหัสอ้างอิง (ID)' ด้านบน เพื่อปลดล็อกแบบฟอร์มการประเมิน")
    st.stop()

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ==========================================
# --- 6. TOOLS LOGIC (คำถามเต็ม 100%) ---
# ==========================================

# --- TOOL 1 ---
if choice == "Tool 1: ประเมินสถานะองค์กร":
    st.markdown('<div class="premium-header"><h3>Tool 1: ประเมินสถานะองค์กร</h3><p>Policy Gap Analysis</p></div>', unsafe_allow_html=True)
    with st.form("form_t1"):
        st.markdown("**หมวด A: การกำกับดูแลและนโยบาย**")
        q1_1 = st.radio("1.1 องค์กรมี 'นโยบายสิทธิมนุษยชน' ที่เป็นลายลักษณ์อักษรหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        q1_2 = st.radio("1.2 นโยบายครอบคลุมประเด็นสำคัญ (แรงงานข้ามชาติ, ชุมชน) หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        q1_3 = st.radio("1.3 มีการสื่อสารนโยบายในภาษาที่พนักงานและคู่ค้าเข้าใจหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        q1_4 = st.radio("1.4 มีการแต่งตั้งผู้รับผิดชอบระดับบริหาร (Board Level) หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        
        st.markdown("**หมวด B: กระบวนการตรวจสอบอย่างรอบด้าน**")
        q2_1 = st.radio("2.1 มีการประเมินความเสี่ยงด้านสิทธิมนุษยชน (HRA) ประจำปีหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        q2_2 = st.radio("2.2 มีระบบการตรวจสอบย้อนกลับในห่วงโซ่อุปทานหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        q2_3 = st.radio("2.3 มีแผนจัดการความเสี่ยง (Mitigation Plan) ที่ใช้จริงหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        
        st.markdown("**หมวด C: กลไกการร้องเรียนและการเยียวยา**")
        q3_1 = st.radio("3.1 มีช่องทางรับเรื่องร้องเรียนที่ปลอดภัย เป็นความลับ หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        q3_2 = st.radio("3.2 มีมาตรการคุ้มครองผู้แจ้งเบาะแส (Non-Retaliation Policy) หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)
        q3_3 = st.radio("3.3 มีขั้นตอนการเยียวยา (Remediation) หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"], horizontal=True)

        if st.form_submit_button("บันทึกข้อมูล (Submit)"):
            sheet = connect_to_sheet()
            if sheet:
                detail = f"A(1.1:{q1_1}, 1.2:{q1_2}, 1.3:{q1_3}, 1.4:{q1_4}) | B(2.1:{q2_1}, 2.2:{q2_2}, 2.3:{q2_3}) | C(3.1:{q3_1}, 3.2:{q3_2}, 3.3:{q3_3})"
                sheet.append_row([now, "Tool 1", resp_id, resp_group, "Policy Gap Analysis", detail, "", "", "", ""])
                st.success("✅ บันทึกข้อมูล Tool 1 ลงฐานข้อมูลเรียบร้อยแล้ว")

# --- TOOL 2 ---
elif choice == "Tool 2: แบบสอบถามหน้างาน":
    st.markdown('<div class="premium-header"><h3>Tool 2: แบบสอบถามการปฏิบัติหน้างาน</h3><p>Worker Survey</p></div>', unsafe_allow_html=True)
    with st.form("form_t2"):
        st.markdown("**ส่วนที่ 1: สภาพการจ้างและค่าจ้าง**")
        s1_1 = st.select_slider("1.1 ท่านได้รับค่าจ้างตรงเวลาและครบถ้วนตามสัญญาหรือไม่?", options=["แย่มาก (1)", "แย่ (2)", "ปานกลาง (3)", "ดี (4)", "ดีมาก (5)"], value="ปานกลาง (3)")
        s1_2 = st.select_slider("1.2 ท่านได้รับวันหยุดอย่างน้อย 1 วันต่อสัปดาห์ (หรือตามกฎหมาย) หรือไม่?", options=["แย่มาก (1)", "แย่ (2)", "ปานกลาง (3)", "ดี (4)", "ดีมาก (5)"], value="ปานกลาง (3)")
        s1_3 = st.select_slider("1.3 ท่านเป็นผู้เก็บเอกสารประจำตัวไว้เองใช่หรือไม่?", options=["แย่มาก (1)", "แย่ (2)", "ปานกลาง (3)", "ดี (4)", "ดีมาก (5)"], value="ปานกลาง (3)")
        st.markdown("<hr>", unsafe_allow_html=True)
        
        st.markdown("**ส่วนที่ 2: ความปลอดภัยและสุขอนามัย (OHS)**")
        s2_1 = st.select_slider("2.1 อุปกรณ์ป้องกันอันตราย (PPE) มีเพียงพอและพร้อมใช้งานหรือไม่?", options=["แย่มาก (1)", "แย่ (2)", "ปานกลาง (3)", "ดี (4)", "ดีมาก (5)"], value="ปานกลาง (3)")
        s2_2 = st.select_slider("2.2 ท่านได้รับการฝึกอบรมด้านความปลอดภัยก่อนเริ่มงานหรือไม่?", options=["แย่มาก (1)", "แย่ (2)", "ปานกลาง (3)", "ดี (4)", "ดีมาก (5)"], value="ปานกลาง (3)")
        st.markdown("<hr>", unsafe_allow_html=True)
        
        st.markdown("**ส่วนที่ 3: การปฏิบัติต่อแรงงานและความเท่าเทียม**")
        s3_1 = st.select_slider("3.1 หัวหน้างานปฏิบัติต่อท่านด้วยความเคารพใช่หรือไม่?", options=["แย่มาก (1)", "แย่ (2)", "ปานกลาง (3)", "ดี (4)", "ดีมาก (5)"], value="ปานกลาง (3)")
        s3_2 = st.select_slider("3.2 ท่านสามารถเข้าถึงน้ำดื่มที่สะอาดและห้องน้ำได้ตลอดเวลาใช่หรือไม่?", options=["แย่มาก (1)", "แย่ (2)", "ปานกลาง (3)", "ดี (4)", "ดีมาก (5)"], value="ปานกลาง (3)")
        
        if st.form_submit_button("บันทึกข้อมูล (Submit)"):
            sheet = connect_to_sheet()
            if sheet:
                detail = f"การจ้าง(1.1:{s1_1}, 1.2:{s1_2}, 1.3:{s1_3}) | ความปลอดภัย(2.1:{s2_1}, 2.2:{s2_2}) | การปฏิบัติ(3.1:{s3_1}, 3.2:{s3_2})"
                sheet.append_row([now, "Tool 2", resp_id, resp_group, "Worker Practice", detail, "", "", "", ""])
                st.success("✅ บันทึกข้อมูล Tool 2 สำเร็จ")

# --- TOOL 3 ---
elif choice == "Tool 3: สัมภาษณ์เชิงลึก (Evidence)":
    st.markdown('<div class="premium-header"><h3>Tool 3: สัมภาษณ์เชิงลึก</h3><p>In-depth Interview & Evidence Base</p></div>', unsafe_allow_html=True)
    with st.form("form_t3"):
        st.markdown("**🔍 ประเด็นที่พบจากการสัมภาษณ์ (เลือกหัวข้อ)**")
        topics = st.multiselect("หัวข้อความเสี่ยง:", ["การสรรหา/ค่านายหน้า", "สัญญาจ้าง", "ค่าจ้าง/โอที", "เสรีภาพในการเดินทาง", "สภาพที่พัก/โรงอาหาร", "การร้องเรียน", "การเลือกปฏิบัติ"], label_visibility="collapsed")
             
        st.markdown("<br>**✍️ บันทึกคำให้การและข้อเท็จจริง (Testimony)**", unsafe_allow_html=True)
        testimony = st.text_area("สรุปคำพูดหรือหลักฐานที่พบ:", height=120)
        
        if st.form_submit_button("บันทึกข้อมูล (Submit)"):
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([now, "Tool 3", resp_id, resp_group, ", ".join(topics), testimony, "", "", "", ""])
                st.success("✅ บันทึกหลักฐานบทสัมภาษณ์สำเร็จ")

# --- TOOL 4 ---
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
        
        st.markdown("<br>**📝 บันทึกเพิ่มเติมจากการเดินสำรวจ**", unsafe_allow_html=True)
        obs_detail = st.text_area("รายละเอียด:", height=80, label_visibility="collapsed")
        
        if st.form_submit_button("บันทึกข้อมูล (Submit)"):
            sheet = connect_to_sheet()
            if sheet:
                checklist_result = f"O1:{o1}, O2:{o2}, O3:{o3}, O4:{o4}, O5:{o5}, O6:{o6}"
                detail = f"[Checklist: {checklist_result}] | Note: {obs_detail}"
                sheet.append_row([now, "Tool 4", resp_id, resp_group, "Site Observation", detail, "", "", "", ""])
                st.success("✅ บันทึก Log การสังเกตการณ์สำเร็จ")

# --- TOOL 5 ---
elif choice == "Tool 5: ประเมินนัยสำคัญ (Salient Rule)":
    st.markdown('<div class="premium-header"><h3>Tool 5: Human Rights Risk Matrix</h3><p>การประเมินนัยสำคัญ (Severity-led Rule)</p></div>', unsafe_allow_html=True)
    
    st.markdown("**📌 1. ระบุประเด็นความเสี่ยง (อ้างอิงมาตรฐาน ILO)**")
    issue = st.selectbox("หมวดหมู่ความเสี่ยง:", [
        "[แรงงานบังคับ] ภาระหนี้ผูกพัน / การเรียกเก็บค่าธรรมเนียมสรรหา",
        "[แรงงานบังคับ] การยึดเอกสารประจำตัว (พาสปอร์ต/บัตร)",
        "[แรงงานบังคับ] การจำกัดเสรีภาพในการเดินทาง",
        "[สิทธิแรงงาน] การหักค่าจ้าง / จ่ายเงินล่าช้า / ไม่จ่ายโอที",
        "[สิทธิแรงงาน] การเลือกปฏิบัติและการคุกคามในที่ทำงาน",
        "[อาชีวอนามัย] สภาพแวดล้อมการทำงานอันตราย / ขาด PPE",
        "[ชุมชน] ผลกระทบต่อสิ่งแวดล้อมและชุมชนโดยรอบ",
        "อื่นๆ"
    ], label_visibility="collapsed")
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("**📌 2. ประเมินระดับความรุนแรง (Severity)**")
    scale = st.slider("Scale (ความรุนแรงต่อบุคคล)", 1, 5, 1)
    scope = st.slider("Scope (วงกว้าง)", 1, 5, 1)
    remedy = st.slider("Remediability (ความยากในการเยียวยา)", 1, 5, 1)
    
    sev_max = max(scale, scope, remedy)
    st.markdown("<hr>", unsafe_allow_html=True)
    likelihood = st.slider("📌 3. โอกาสเกิด (Likelihood)", 1, 5, 1)
    score = sev_max * likelihood

    st.info(f"📊 **Severity Max: {sev_max} | โอกาสเกิด: {likelihood} | คะแนนความเสี่ยง: {score}**")
    
    is_salient = "YES" if sev_max == 5 else "NO"
    if is_salient == "YES":
        st.markdown('<div class="salient-badge">🚨 SALIENT ISSUE : พบประเด็นความเสี่ยงระดับวิกฤต</div>', unsafe_allow_html=True)

    rows = ""
    for l in range(5, 0, -1):
        rows += "<tr>"
        for s in range(1, 6):
            val = s * l
            color = "#EF4444" if val >= 16 or s == 5 else ("#F9A818" if val >= 8 else "#005B31")
            mark = "★" if s == sev_max and l == likelihood else ""
            rows += f"<td class='heat-cell' style='background-color:{color};'>{mark}</td>"
        rows += "</tr>"
    st.markdown(f"<table class='heat-table'>{rows}</table>", unsafe_allow_html=True)

    if st.button("บันทึกประเด็นนัยสำคัญ (Submit)"):
        sheet = connect_to_sheet()
        if sheet:
            detail = f"Scale:{scale}, Scope:{scope}, Remedy:{remedy}"
            sheet.append_row([now, "Tool 5", resp_id, resp_group, issue, detail, sev_max, likelihood, score, is_salient])
            st.success("✅ บันทึกความเสี่ยงเรียบร้อย")

# --- TOOL 6 ---
elif choice == "Tool 6: ระบบวิเคราะห์ AI Triangulation":
    st.markdown('<div class="premium-header"><h3>Tool 6: AI Triangulation Engine</h3><p>ระบบสอบทานความขัดแย้งของข้อมูลอัตโนมัติ (Mockup)</p></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background-color: #FFFFFF; padding: 25px; border-left: 6px solid #DC2626; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.04);">
        <h4 style="color: #DC2626; margin-top: 0; font-size: 18px;">🚩 ตรวจพบความขัดแย้งเชิงนโยบาย (Policy vs Practice)</h4>
        <p style="color: #333; margin-bottom: 15px;"><b>ประเด็น:</b> สัญญาจ้างไม่เป็นภาษาที่พนักงานเข้าใจ</p>
        <div style="background: #F9FAFB; padding: 15px; border-radius: 8px;">
            <span style="color: #4B5563; font-size: 14px;">🗣️ <b>อ้างอิง (ID: EMP-045):</b></span><br>
            <span style="color: #111827; font-style: italic;">"เซ็นไปโดยไม่รู้ว่าเป็นภาษาอะไร..."</span>
        </div>
        <div style="color: #005B31; font-size: 14px; font-weight: 600; padding-top: 10px;">
            ❌ ขัดแย้งกับข้อมูล Tool 1 ข้อ 1.3: ระบุว่าสื่อสารเข้าใจแล้ว
        </div>
    </div>
    """, unsafe_allow_html=True)
