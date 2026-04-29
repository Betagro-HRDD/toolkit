import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- 1. SETTING UP THE PAGE ---
st.set_page_config(
    page_title="Betagro HRDD Digital Toolkit Full Version",
    page_icon="https://www.betagro.com/favicon.ico",
    layout="wide"
)

# --- 2. PREMIUM CSS (บังคับธีมและสีเบทาโกรให้ครบทุกจุด) ---
st.markdown("""
    <style>
    /* บังคับสีพื้นหลัง */
    .stApp { background-color: #F8FAF9 !important; }
    
    /* Sidebar: สีเขียวเบทาโกร */
    [data-testid="stSidebar"] {
        background-color: #1E3F26 !important;
        min-width: 300px !important;
    }
    [data-testid="stSidebar"] * { color: white !important; }

    /* หัวข้อ Header */
    h1 {
        color: #1E3F26 !important;
        border-bottom: 5px solid #F9A818 !important;
        padding-bottom: 15px;
        font-weight: 800 !important;
    }
    
    h2, h3 { color: #1E3F26 !important; font-weight: 700 !important; margin-top: 25px; }

    /* ปุ่มกด */
    .stButton>button {
        background-color: #1E3F26 !important;
        color: #FFFFFF !important;
        border: 2px solid #F9A818 !important;
        border-radius: 10px !important;
        padding: 15px !important;
        font-weight: bold !important;
        width: 100% !important;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #F9A818 !important; color: #1E3F26 !important; }

    /* ตกแต่ง Radio Buttons และ Sliders */
    .stRadio > label { font-weight: bold !important; color: #1E3F26 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER & LOGO ---
col1, col2 = st.columns([1, 4])
with col1:
    st.image("https://www.betagro.com/assets/img/logo/logo.png", width=150)
with col2:
    st.title("HRDD DIGITAL TOOLKIT")
    st.subheader("เครือเบทาโกร: ระบบตรวจสอบสิทธิมนุษยชนอย่างรอบด้าน (UNGPs/OECD Standards)")

st.write("---")

# --- 4. SIDEBAR NAVIGATION ---
choice = st.sidebar.radio("📋 เลือกเครื่องมือที่ต้องการใช้งาน:", [
    "Tool 1: แบบประเมินสถานะองค์กร", 
    "Tool 2: แบบสอบถามการปฏิบัติหน้างาน", 
    "Tool 3: แนวทางการสัมภาษณ์เชิงลึก", 
    "Tool 4: แบบบันทึกการสังเกตการณ์ภาคสนาม",
    "Tool 5: ตารางประเมินนัยสำคัญ (Salient Risk)",
    "Tool 6: ระบบวิเคราะห์ AI (NotebookLM)"
])

# --- 5. CONTENT SECTIONS (ใส่เนื้อหาละเอียดตามต้นฉบับ) ---

if choice == "Tool 1: แบบประเมินสถานะองค์กร":
    st.header("📋 Tool 1: แบบประเมินสถานะองค์กร (Internal Policy Gap Analysis)")
    with st.form("full_tool1"):
        st.subheader("หมวด A: การประกาศนโยบายและความมุ่งมั่น")
        q1_1 = st.radio("A1. องค์กรมีการจัดทำ 'นโยบายสิทธิมนุษยชน' เป็นลายลักษณ์อักษรที่อนุมัติโดยบอร์ดหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_2 = st.radio("A2. นโยบายครอบคลุมประเด็นสำคัญ (แรงงานข้ามชาติ, สิทธิชุมชน, ความหลากหลาย) หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_3 = st.radio("A3. มีการสื่อสารนโยบายในภาษาที่พนักงานและคู่ค้าเข้าใจหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_4 = st.radio("A4. มีการระบุความรับผิดชอบด้านสิทธิมนุษยชนในระดับผู้บริหารระดับสูงหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        
        st.subheader("หมวด B: กระบวนการตรวจสอบอย่างรอบด้าน (Due Diligence)")
        q2_1 = st.radio("B1. มีการประเมินความเสี่ยงด้านสิทธิมนุษยชน (HRA) เป็นประจำทุกปีหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q2_2 = st.radio("B2. มีกระบวนการตรวจสอบย้อนกลับ (Traceability) ในห่วงโซ่อุปทานหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q2_3 = st.radio("B3. มีการกำหนดตัวชี้วัด (KPIs) ด้านสิทธิมนุษยชนในระดับหน่วยปฏิบัติการหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        
        st.subheader("หมวด C: กลไกการร้องเรียนและการเยียวยา")
        q3_1 = st.radio("C1. มีช่องทางร้องเรียนที่เข้าถึงง่ายสำหรับกลุ่มเปราะบางหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q3_2 = st.radio("C2. มีมาตรการคุ้มครองผู้แจ้งเบาะแส (Whistleblower Protection) หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q3_3 = st.radio("C3. มีขั้นตอนการเยียวยา (Remediation Plan) ที่ชัดเจนเมื่อพบการละเมิดหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        
        if st.form_submit_button("บันทึกข้อมูล Tool 1"):
            st.success("บันทึกข้อมูลสำเร็จ")

elif choice == "Tool 2: แบบสอบถามการปฏิบัติหน้างาน":
    st.header("📊 Tool 2: แบบสอบถามการปฏิบัติ (Human Rights Survey)")
    with st.form("full_tool2"):
        st.subheader("Section 1: สภาพการจ้างและค่าตอบแทน")
        q2_1 = st.select_slider("1.1 ท่านได้รับค่าจ้างตรงเวลาและครบถ้วน?", options=[1,2,3,4,5], value=3)
        q2_2 = st.select_slider("1.2 ท่านมีวันหยุดตามกฎหมายกำหนด?", options=[1,2,3,4,5], value=3)
        q2_3 = st.select_slider("1.3 ท่านเก็บเอกสารสัญญาจ้างไว้กับตัวหรือไม่?", options=[1,2,3,4,5], value=3)
        
        st.subheader("Section 2: ความปลอดภัยและอาชีวอนามัย (OHS)")
        q3_1 = st.select_slider("2.1 อุปกรณ์ PPE เพียงพอและเหมาะสมกับงาน?", options=[1,2,3,4,5], value=3)
        q3_2 = st.select_slider("2.2 ท่านได้รับการฝึกอบรมเรื่องความปลอดภัย?", options=[1,2,3,4,5], value=3)
        
        st.subheader("Section 3: การไม่เลือกปฏิบัติและการคุกคาม")
        q4_1 = st.select_slider("3.1 ท่านได้รับการปฏิบัติเท่าเทียมโดยไม่คำนึงถึงเพศ/สัญชาติ?", options=[1,2,3,4,5], value=3)
        q4_2 = st.select_slider("3.2 บรรยากาศการทำงานปราศจากการข่มขู่/คุกคาม?", options=[1,2,3,4,5], value=3)
        
        if st.form_submit_button("ส่งแบบสอบถาม"):
            st.balloons()

elif choice == "Tool 3: แนวทางการสัมภาษณ์เชิงลึก":
    st.header("🎙️ Tool 3: แนวทางการสัมภาษณ์ (Interview Guide)")
    with st.form("full_tool3"):
        st.subheader("ส่วนที่ 1: การสรรหาและจัดจ้าง (Ethical Recruitment)")
        i1 = st.text_area("1. เล่าขั้นตอนก่อนมาทำงานที่นี่ (มีค่าหัวคิวหรือค่าใช้จ่ายแอบแฝงไหม?):")
        i2 = st.text_area("2. ท่านได้เห็นและเซ็นสัญญาในภาษาที่เข้าใจก่อนมาหรือไม่?")
        st.subheader("ส่วนที่ 2: สภาพความเป็นอยู่และความเชื่อมั่น")
        i3 = st.text_area("3. สภาพหอพักมีความปลอดภัยและเป็นส่วนตัวเพียงพอไหม?")
        i4 = st.text_area("4. หากมีปัญหา ท่านกล้าร้องเรียนผ่านช่องทางของบริษัทไหม เพราะอะไร?")
        if st.form_submit_button("บันทึกบทสัมภาษณ์"):
            st.success("บันทึกเรียบร้อย")

elif choice == "Tool 4: แบบบันทึกการสังเกตการณ์ภาคสนาม":
    st.header("🔎 Tool 4: แบบบันทึกการสังเกตการณ์ (Observation Log)")
    with st.form("full_tool4"):
        col1, col2 = st.columns(2)
        with col1:
            st.write("**ด้านความปลอดภัยและป้ายประกาศ**")
            o1 = st.checkbox("ป้ายประกาศสิทธิแรงงาน/เบอร์ร้องเรียนมีภาษา Native")
            o2 = st.checkbox("พนักงานสวม PPE ครบถ้วนตามความเสี่ยง")
            o3 = st.checkbox("ทางหนีไฟไม่มีสิ่งกีดขวางและถังดับเพลิงพร้อมใช้")
        with col2:
            st.write("**ด้านสวัสดิการและหอพัก**")
            o4 = st.checkbox("หอพักมีน้ำดื่มสะอาดและเข้าถึงได้ตลอด")
            o5 = st.checkbox("ห้องน้ำสะอาดและแยกชาย-หญิงชัดเจน")
            o6 = st.checkbox("หอพักไม่หนาแน่นจนเกินไป")
        obs_note = st.text_area("บันทึกเพิ่มเติมจากหน้างาน:")
        if st.form_submit_button("บันทึกการสังเกตการณ์"):
            st.success("บันทึกแล้ว")

elif choice == "Tool 5: ตารางประเมินนัยสำคัญ (Salient Risk)":
    st.header("⚖️ Tool 5: Salient Human Rights Risks Scoring Matrix")
    
    col_in, col_res = st.columns([1, 1.2])
    with col_in:
        st.subheader("วิเคราะห์ประเด็นความเสี่ยง")
        issue_name = st.text_input("ชื่อประเด็น:", "ความปลอดภัยแรงงานข้ามชาติ")
        
        st.write("**1. การประเมินความรุนแรง (Severity)**")
        s1 = st.slider("ขนาด (Scale)", 1, 5, 3)
        s2 = st.slider("ขอบเขต (Scope)", 1, 5, 3)
        s3 = st.slider("การเยียวยา (Remediability)", 1, 5, 3)
        severity_max = max(s1, s2, s3)
        
        st.write("**2. การประเมินโอกาสเกิด (Likelihood)**")
        likelihood = st.slider("โอกาสที่จะเกิดขึ้น", 1, 5, 2)
        final_score = severity_max * likelihood
        st.metric("Salience Score (Max S x L)", final_score)

    with col_res:
        st.subheader("Strategic Heat Map (5x5)")
        # สร้าง Matrix สี แดง-ส้ม-เขียว
        z_data = [[r*c for c in range(1, 6)] for r in range(1, 6)]
        fig = px.imshow(
            z_data,
            x=[1, 2, 3, 4, 5], y=[1, 2, 3, 4, 5],
            labels=dict(x="Severity", y="Likelihood", color="Score"),
            color_continuous_scale=[[0, 'green'], [0.4, 'orange'], [1, 'red']],
            origin='lower'
        )
        fig.add_scatter(x=[severity_max], y=[likelihood], mode='markers+text', 
                        marker=dict(color='white', size=15, symbol='x'),
                        text=["Current Risk"], textposition="top center")
        st.plotly_chart(fig, use_container_width=True)

elif choice == "Tool 6: ระบบวิเคราะห์ AI (NotebookLM)":
    st.header("🤖 Tool 6: AI-Driven Data Synthesis & Analysis")
    st.info("ใช้สำหรับการ Triangulation ข้อมูลจาก Tool 1-4 เพื่อหาข้อขัดแย้ง")
    input_text = st.text_area("ใส่ข้อมูลสรุปจากภาคสนาม:")
    if st.button("ประมวลผลด้วย NotebookLM Logic"):
        st.write("ระบบกำลังประมวลผลความสอดคล้อง...")

# --- 6. FOOTER ---
st.markdown("---")
st.markdown("<p style='text-align: center;'>© 2024 Betagro Group | HRDD Toolkit Version 2.0 (Full Script)</p>", unsafe_allow_html=True)