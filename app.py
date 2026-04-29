import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. การตั้งค่าหน้าเว็บ ---
st.set_page_config(
    page_title="Betagro HRDD Full Digital Toolkit",
    page_icon="https://www.betagro.com/favicon.ico",
    layout="wide"
)

# --- 2. การตกแต่งหน้าตา (BETAGRO PREMIUM STYLE) ---
st.markdown("""
    <style>
    :root { --betagro-green: #265F36; --betagro-yellow: #F9A818; }
    .main { background-color: #f9fbf9; }
    h1 { color: var(--betagro-green); font-weight: 700; border-bottom: 3px solid var(--betagro-yellow); padding-bottom: 10px; }
    h2, h3 { color: var(--betagro-green); }
    .stButton>button { background-color: var(--betagro-green); color: white; border-radius: 5px; width: 100%; font-weight: bold; }
    .stButton>button:hover { background-color: var(--betagro-yellow); color: var(--betagro-green); }
    .stRadio > label { font-weight: bold; color: #333; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. ส่วนหัวและโลโก้ ---
col1, col2 = st.columns([1, 5])
with col1:
    st.image("https://www.betagro.com/img/logo.png", width=120)
with col2:
    st.title("HRDD Digital Toolkit")
    st.subheader("เครือเบทาโกร: ระบบตรวจสอบสิทธิมนุษยชนอย่างรอบด้าน (UNGPs/OECD Standards)")

# --- 4. เมนูหลักด้านข้าง ---
st.sidebar.header("เมนูเครื่องมือ 1-5")
choice = st.sidebar.radio("เลือกเครื่องมือที่ต้องการใช้งาน:", 
    ["Tool 1: แบบประเมินสถานะองค์กร", 
     "Tool 2: แบบสอบถามการปฏิบัติ", 
     "Tool 3: แนวทางการสัมภาษณ์", 
     "Tool 4: แบบบันทึกการสังเกตการณ์",
     "Tool 5: ตารางประเมินนัยสำคัญ"])

# ฟังก์ชันบันทึกข้อมูล (จำลองเพื่อเตรียมเชื่อม Google Sheets)
def record_data(tool_id, data_dict):
    # ในขั้นต่อไป เราจะเขียนโค้ดเชื่อม Google Sheets ตรงนี้ครับ
    st.success(f"บันทึกข้อมูล {tool_id} สำเร็จ! ข้อมูลเตรียมส่งไปยัง Google Sheets")
    st.balloons()

# --- 5. รายละเอียดเนื้อหาแต่ละเครื่องมือ (ครบถ้วนตามต้นฉบับ) ---

if choice == "Tool 1: แบบประเมินสถานะองค์กร":
    st.header("Tool 1: แบบประเมินสถานะองค์กร (Internal Policy Gap Analysis)")
    with st.form("tool1"):
        st.markdown("### ส่วนที่ 1: การประกาศนโยบายและความมุ่งมั่น")
        q1_1 = st.radio("1.1 องค์กรมีการจัดทำ 'นโยบายสิทธิมนุษยชน' เป็นลายลักษณ์อักษรที่อนุมัติโดยคณะกรรมการบริษัทหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_2 = st.radio("1.2 นโยบายครอบคลุมประเด็นสำคัญ (แรงงานข้ามชาติ, สิทธิชุมชน, ความหลากหลาย) หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_3 = st.radio("1.3 มีการสื่อสารนโยบายนี้ให้พนักงานและคู่ค้า (Suppliers) รับทราบในภาษาที่พวกเขาเข้าใจหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        
        st.markdown("### ส่วนที่ 2: กระบวนการตรวจสอบอย่างรอบด้าน (Due Diligence Process)")
        q2_1 = st.radio("2.1 องค์กรมีระบบการประเมินความเสี่ยงด้านสิทธิมนุษยชน (HRA) เป็นประจำทุกปีหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q2_2 = st.radio("2.2 มีกระบวนการตรวจสอบย้อนกลับ (Traceability) ในห่วงโซ่อุปทานต้นน้ำหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q2_3 = st.radio("2.3 มีการกำหนดตัวชี้วัด (KPIs) ด้านสิทธิมนุษยชนในระดับหน่วยงานปฏิบัติการหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])

        st.markdown("### ส่วนที่ 3: กลไกการร้องเรียนและการเยียวยา")
        q3_1 = st.radio("3.1 มีช่องทางการรับเรื่องร้องเรียนที่เข้าถึงง่ายสำหรับกลุ่มเปราะบางหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q3_2 = st.radio("3.2 มีกระบวนการคุ้มครองผู้แจ้งเบาะแส (Whistleblower Protection) หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q3_3 = st.radio("3.3 มีขั้นตอนการเยียวยา (Remediation Plan) ที่ชัดเจนเมื่อตรวจพบการละเมิดหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        
        if st.form_submit_button("บันทึกข้อมูล Tool 1"):
            record_data("Tool1", {"q1_1":q1_1, "q2_1":q2_1, "q3_1":q3_1})

elif choice == "Tool 2: แบบสอบถามการปฏิบัติ":
    st.header("Tool 2: แบบสอบถามการปฏิบัติ (Human Rights Survey)")
    st.info("เกณฑ์: 1 = น้อยที่สุด/ไม่เคยเลย, 5 = มากที่สุด/สม่ำเสมอ")
    with st.form("tool2"):
        st.subheader("ส่วนที่ 2: สภาพการจ้างงานและค่าตอบแทน")
        q2_1 = st.select_slider("2.1 ท่านได้รับค่าจ้างตรงตามเวลาและครบถ้วนหรือไม่?", options=[1,2,3,4,5], value=3)
        q2_2 = st.select_slider("2.2 ท่านมีวันหยุดประจำสัปดาห์และนักขัตฤกษ์ตามกฎหมายหรือไม่?", options=[1,2,3,4,5], value=3)
        
        st.subheader("ส่วนที่ 3: ความปลอดภัยและอาชีวอนามัย")
        q3_1 = st.select_slider("3.1 องค์กรมีการจัดอุปกรณ์ PPE ที่เหมาะสมและเพียงพอหรือไม่?", options=[1,2,3,4,5], value=3)
        q3_2 = st.select_slider("3.2 ท่านได้รับการอบรมเรื่องความปลอดภัยก่อนเริ่มงานหรือไม่?", options=[1,2,3,4,5], value=3)
        
        st.subheader("ส่วนที่ 4: การเลือกปฏิบัติและการคุกคาม")
        q4_1 = st.select_slider("4.1 ท่านได้รับการปฏิบัติเท่าเทียมโดยไม่คำนึงถึง เพศ/ศาสนา หรือไม่?", options=[1,2,3,4,5], value=3)
        q4_2 = st.select_slider("4.2 บรรยากาศที่ทำงานปราศจากการข่มขู่หรือคุกคามหรือไม่?", options=[1,2,3,4,5], value=3)
        
        if st.form_submit_button("บันทึกข้อมูล Tool 2"):
            record_data("Tool 2", {"q2_1":q2_1, "q3_1":q3_1})

elif choice == "Tool 3: แนวทางการสัมภาษณ์":
    st.header("Tool 3: แนวทางการสัมภาษณ์ (Semi-structured Interview Guide)")
    with st.form("tool3"):
        st.subheader("ส่วนที่ 1: การสรรหาและจัดจ้าง (Ethical Recruitment)")
        q1_1 = st.text_area("1. ขั้นตอนก่อนมาทำงานที่นี่ต้องเสียค่าใช้จ่าย (ค่าหัวคิว) อะไรบ้าง?")
        q1_2 = st.text_area("2. ท่านได้เซ็นสัญญาจ้างในภาษาที่ท่านเข้าใจก่อนเดินทางมาหรือไม่?")
        q1_3 = st.radio("3. มีใครเก็บพาสปอร์ตหรือเอกสารประจำตัวของท่านไว้หรือไม่?", ["เก็บเอง", "บริษัท/นายหน้าเก็บไว้"])
        
        st.subheader("ส่วนที่ 2: สภาพการทำงานและความเป็นอยู่")
        q2_1 = st.text_area("4. ในหนึ่งวันทำงานกี่ชั่วโมง และมีเวลาพักผ่อนเพียงพอไหม?")
        q2_2 = st.text_area("5. สภาพหอพักที่บริษัทจัดให้มีความปลอดภัยและเป็นส่วนตัวหรือไม่?")
        
        if st.form_submit_button("บันทึกข้อมูล Tool 3"):
            record_data("Tool 3", {"notes":q1_1})

elif choice == "Tool 4: แบบบันทึกการสังเกตการณ์":
    st.header("Tool 4: แบบบันทึกการสังเกตการณ์ (Observation Log)")
    with st.form("tool4"):
        st.subheader("1) สภาพแวดล้อม (Workplace Environment)")
        c1 = st.checkbox("พนักงานสวมใส่ PPE ครบถ้วนและอยู่ในสภาพดี")
        c2 = st.checkbox("มีป้ายประกาศสิทธิแรงงาน/ช่องทางร้องเรียนในภาษาต่างชาติ")
        c3 = st.checkbox("ทางหนีไฟและอุปกรณ์ดับเพลิงพร้อมใช้งาน")
        
        st.subheader("2) สภาพความเป็นอยู่ (Living Conditions)")
        c4 = st.checkbox("หอพักมีความหนาแน่นเหมาะสมและปลอดภัย")
        c5 = st.checkbox("มีน้ำดื่มสะอาดและห้องน้ำถูกสุขลักษณะ")
        
        obs_note = st.text_area("บันทึกความรู้สึกเชิงลึก (Narrative Notes):")
        if st.form_submit_button("บันทึกข้อมูล Tool 4"):
            record_data("Tool 4", {"note":obs_note})

elif choice == "Tool 5: ตารางประเมินนัยสำคัญ":
    st.header("Tool 5: ตารางประเมินนัยสำคัญ (Salient Risk Matrix)")
    st.write("คำนวณตามหลักการ: Severity x Likelihood")
    with st.form("tool5"):
        issue = st.text_input("ชื่อประเด็นความเสี่ยงที่พบ:")
        col1, col2, col3 = st.columns(3)
        with col1: s_scale = st.select_slider("ขนาด (Scale):", options=[1,2,3,4,5])
        with col2: s_scope = st.select_slider("ขอบเขต (Scope):", options=[1,2,3,4,5])
        with col3: s_rem = st.select_slider("การเยียวยา (Remediability):", options=[1,2,3,4,5])
        
        l_prob = st.select_slider("โอกาสเกิด (Likelihood):", options=[1,2,3,4,5])
        
        if st.form_submit_button("คำนวณและบันทึก"):
            sev_avg = (s_scale + s_scope + s_rem) / 3
            score = sev_avg * l_prob
            st.write(f"### คะแนนรวม: {score:.2f}")
            if score >= 16: st.error("ระดับ: วิกฤต (Red Zone)")
            elif score >= 6: st.warning("ระดับ: นัยสำคัญ (Yellow Zone)")
            else: st.success("ระดับ: บริหารจัดการได้ (Green Zone)")
            record_data("Tool 5", {"issue":issue, "score":score})

# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.write("© 2024 Betagro Group | HRDD Digital Toolkit")