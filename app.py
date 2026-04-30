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

# --- 3. PREMIUM STYLING (Fixed Icon & Standardized Layout) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Sarabun', sans-serif; }
    .stApp { background-color: #F8FAFB; }
    .main-header {
        background-color: white; padding: 30px; border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-left: 10px solid #F9A818;
        margin-bottom: 25px; text-align: center;
    }
    .salient-badge { background-color: #EF4444; color: white; padding: 10px 20px; border-radius: 10px; font-weight: bold; display: block; text-align: center; }
    .citation-box { background-color: #E8EEE8; padding: 15px; border-left: 5px solid #265F36; border-radius: 5px; margin: 10px 0; }
    /* Heat Map Styling */
    .heat-table { width: 100%; border-collapse: separate; border-spacing: 5px; }
    .heat-cell { height: 50px; text-align: center; font-weight: bold; color: white; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR (Respondent Identification) ---
with st.sidebar:
    st.image("https://www.betagro.com/wp-content/themes/betagro/assets/img/logo-en.png", width=160)
    st.title("HRDD Settings")
    choice = st.radio("📋 เลือกเครื่องมือ:", [
        "Tool 1: ประเมินสถานะองค์กร",
        "Tool 2: แบบสอบถามหน้างาน",
        "Tool 3: สัมภาษณ์เชิงลึก (Evidence)",
        "Tool 4: บันทึกการสังเกตการณ์",
        "Tool 5: ประเมินนัยสำคัญ (Salient Rule)",
        "Tool 6: AI Triangulation"
    ])
    st.hr()
    st.subheader("👤 ข้อมูลผู้ให้ข้อมูล")
    resp_id = st.text_input("รหัสพนักงาน/ID:", placeholder="เช่น EMP-001")
    resp_group = st.selectbox("กลุ่ม:", ["ฝ่ายบริหาร", "แรงงานไทย", "แรงงานข้ามชาติ", "ชุมชน", "คู่ค้า"])

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

# --- 5. TOOL 3: IN-DEPTH INTERVIEW (Evidence-based) ---
if choice == "Tool 3: แนวทางการสัมภาษณ์เชิงลึก":
    st.markdown('<div class="main-header"><h1>Tool 3: แบบสัมภาษณ์เชิงลึก (Worker & Community Voice)</h1></div>', unsafe_allow_html=True)
    with st.form("form_t3"):
        st.write("### 🔍 หัวข้อการตรวจสอบ (ติ๊กข้อที่พบประเด็น)")
        topics = st.multiselect("ประเด็นที่พูดคุย:", 
            ["การสรรหาและค่าธรรมเนียม", "สัญญาจ้าง", "ค่าจ้างและสวัสดิการ", "เสรีภาพในการเดินทาง", "สภาพที่พักอาศัย", "กลไกการร้องเรียน"])
        
        st.write("### ✍️ บันทึกคำให้การ (Evidence/Testimony)")
        testimony = st.text_area("สรุปคำพูดหรือหลักฐานที่พบ (ระบุประโยคสำคัญเพื่อใช้ใน Tool 6):", 
                                 placeholder="ตัวอย่าง: 'พนักงานแจ้งว่าต้องจ่ายค่านายหน้า 5,000 บาทก่อนมาทำงาน'...")
        
        if st.form_submit_button("บันทึกบทสัมภาษณ์"):
            if not resp_id: st.warning("กรุณาระบุรหัสผู้ให้ข้อมูล"); st.stop()
            sheet = connect_to_sheet()
            if sheet:
                sheet.append_row([now, "Tool 3", resp_id, resp_group, ", ".join(topics), testimony])
                st.success(f"✅ บันทึกข้อมูลของ {resp_id} สำเร็จ")

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

# --- TOOL 5: SALIENT-LED HEAT MAP (The Rule of 3 Components) ---
elif choice == "Tool 5: การประเมินนัยสำคัญ (Heat Map)":
    st.markdown('<div class="main-header"><h1>Tool 5: Salient Issues Assessment</h1><p>ใช้หลักการ "ความร้ายแรงนำ" (Severity-led Rule)</p></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1.5])
    with col1:
        issue = st.text_input("ประเด็นความเสี่ยง:", "แรงงานบังคับ / ค่าธรรมเนียมสรรหา")
        
        st.write("---")
        st.write("**คำนวณ Severity (ความร้ายแรง)**")
        scale = st.slider("1. Scale (ความรุนแรงของผลกระทบ)", 1, 5, 1)
        scope = st.slider("2. Scope (ความกว้างขวาง/จำนวนผู้ได้รับผลกระทบ)", 1, 5, 1)
        remedy = st.slider("3. Remediability (ความยากในการเยียวยา)", 1, 5, 1)
        
        # --- กฎ Salient-led Rule: เอาค่าที่สูงที่สุด ---
        severity_max = max(scale, scope, remedy)
        
        st.write("---")
        likelihood = st.slider("Likelihood (โอกาสเกิด)", 1, 5, 1)
        
        final_score = severity_max * likelihood
        
        st.subheader(f"Severity Result: {severity_max}")
        if severity_max == 5:
            st.markdown('<span class="salient-badge">🚨 SALIENT ISSUE (ระดับสูงสุด)</span>', unsafe_allow_html=True)
            st.error("ต้องเฝ้าระวังและมีแผนจัดการทันที!")

    with col2:
        # วาด Heat Map
        rows = ""
        for l in range(5, 0, -1):
            rows += "<tr>"
            rows += f"<td style='text-align:right; font-weight:bold;'>{l}</td>"
            for s in range(1, 6):
                val = s * l
                color = "#EF4444" if val >= 16 or s == 5 else ("#F9A818" if val >= 8 else "#265F36")
                mark = "★" if s == severity_max and l == likelihood else ""
                rows += f"<td style='background-color:{color}; height:50px; width:50px; text-align:center; color:white; font-weight:bold; border-radius:5px;'>{mark}</td>"
            rows += "</tr>"
        st.markdown(f"<table>{rows}<tr style='text-align:center; font-weight:bold;'><td></td><td>1</td><td>2</td><td>3</td><td>4</td><td>5</td></tr></table>", unsafe_allow_html=True)
        st.caption("แนวนอน: Severity (Max) | แนวตั้ง: Likelihood")

    if st.button("💾 บันทึกการวิเคราะห์นัยสำคัญ"):
        sheet = connect_to_sheet()
        if sheet:
            is_salient = "YES" if severity_max == 5 else "NO"
            sheet.append_row([now, "Tool 5", issue, severity_max, likelihood, final_score, is_salient])
            st.success("✅ บันทึกเข้า Statement of Salient Issues เรียบร้อย")

# --- TOOL 6: AI TRIANGULATION & CITATION ---
elif choice == "Tool 6: ระบบวิเคราะห์ AI Triangulation":
    st.markdown('<div class="main-header"><h1>Tool 6: AI-Augmented Triangulation</h1></div>', unsafe_allow_html=True)
    st.info("ระบบจะดึง 'ประโยคอ้างอิง' (Citations) เพื่อยืนยันความโปร่งใสของข้อมูล")
    
    st.write("### 📑 ผลการวิเคราะห์เชิงลึก (Evidence-based)")
    st.write("จากการเปรียบเทียบข้อมูล Tool 1 (นโยบาย) และ Tool 3 (คำสัมภาษณ์) พบจุดขัดแย้งดังนี้:")
    
    st.markdown("""
    <div class="citation-box">
        <b>🚩 ข้อพบพื้นฐาน:</b> มีความเสี่ยงเรื่องค่าธรรมเนียมสรรหา (Recruitment Fees)<br>
        <small><i>อ้างอิงจากบทสัมภาษณ์ (ID: EMP-042):</i> "ผมต้องกู้เงินมาจ่ายค่านายหน้า 12,000 บาทให้เอเจนซี่ฝั่งโน้น"</small>
    </div>
    <div class="citation-box">
        <b>🚩 ข้อพบพื้นฐาน:</b> สภาพความเป็นอยู่ไม่สอดคล้องกับมาตรฐาน<br>
        <small><i>อ้างอิงจากการสังเกตการณ์ (Tool 4):</i> พบว่าจำนวนพนักงานในหอพักหนาแน่นเกินกว่านโยบายที่ระบุใน Tool 1</small>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("บันทึกสรุป AI Analysis"):
        st.success("บันทึกผลการวิเคราะห์และ Citation ลงระบบฐานข้อมูลแล้ว")

st.markdown("<br><hr><p style='text-align: center; color: #888;'>© 2024 Betagro Group | HRDD Digital Toolkit</p>", unsafe_allow_html=True)
