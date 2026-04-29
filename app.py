import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. SETTING UP THE PAGE ---
st.set_page_config(
    page_title="Betagro HRDD Full Digital Toolkit",
    page_icon="https://www.betagro.com/favicon.ico",
    layout="wide"
)

# --- 2. PREMIUM CSS (BETAGRO BRANDING) ---
st.markdown("""
    <style>
    .stApp { background-color: #F0F4F2 !important; }
    [data-testid="stSidebar"] { background-color: #265F36 !important; width: 350px !important; }
    [data-testid="stSidebar"] * { color: white !important; font-size: 15px; }
    h1 { color: #265F36 !important; border-bottom: 5px solid #F9A818 !important; font-weight: 800 !important; }
    h2 { color: #265F36 !important; border-left: 10px solid #F9A818; padding-left: 15px; margin-top: 30px; }
    h3 { color: #265F36 !important; background-color: #E8EEE8; padding: 10px; border-radius: 5px; }
    .stButton>button { 
        background-color: #265F36 !important; color: white !important; 
        border: 2px solid #F9A818 !important; border-radius: 10px !important;
        font-weight: bold !important; width: 100%; height: 4em; font-size: 18px !important;
    }
    .stRadio > label { font-weight: bold !important; font-size: 16px !important; color: #1E3F26 !important; }
    .stSelectbox > label { font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER ---
st.markdown("<h1 style='text-align: center;'>BETAGRO HRDD DIGITAL TOOLKIT (FULL VERSION)</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px; color: #555;'>เครื่องมือเก็บข้อมูลและวิเคราะห์ความเสี่ยงด้านสิทธิมนุษยชนครบวงจร</p>", unsafe_allow_html=True)

# --- 4. SIDEBAR SELECTION ---
st.sidebar.image("https://www.betagro.com/assets/img/logo/logo.png", width=150)
st.sidebar.title("Navigation Menu")
choice = st.sidebar.radio("โปรดเลือกเครื่องมือที่ต้องการใช้งาน:", 
    ["หน้าแรก: กรอบแนวคิด (Framework)",
     "Tool 1: แบบประเมินสถานะองค์กร", 
     "Tool 2: แบบสอบถามการปฏิบัติหน้างาน", 
     "Tool 3: แนวทางการสัมภาษณ์เชิงลึก", 
     "Tool 4: แบบบันทึกการสังเกตการณ์ภาคสนาม",
     "Tool 5: การประเมินนัยสำคัญ (Salient Risk)"])

# --- 5. CONTENT SECTIONS ---

# --- หน้าแรก: FRAMEWORK ---
if choice == "หน้าแรก: กรอบแนวคิด (Framework)":
    st.header("Strategic Framework & Methodology")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Reporting & Due Diligence")
        st.write("""
        - **UNGP Reporting Framework (UNGPRF):** เน้นคำถามเชิงยุทธศาสตร์
        - **OECD Due Diligence Guidance:** การตรวจสอบอย่างรอบด้านในห่วงโซ่อุปทาน
        - **EU CSDDD:** รองรับกฎระเบียบการค้าระดับโลก
        """)
    with col2:
        st.subheader("National Alignment")
        st.write("""
        - **NAP ระยะที่ 2:** แผนปฏิบัติการระดับชาติว่าด้วยธุรกิจกับสิทธิมนุษยชน
        - **SET 2567:** มาตรฐานการรายงานความยั่งยืนล่าสุดของไทย
        """)
    st.info("ระบบนี้บูรณาการ AI (Gemini 1.5 Pro) เพื่อวิเคราะห์ความสอดคล้องของข้อมูลแบบสามเส้า (Triangulation)")

# --- TOOL 1: FULL DETAIL ---
elif choice == "Tool 1: แบบประเมินสถานะองค์กร":
    st.header("เครื่องมือที่ 1: แบบประเมินสถานะองค์กร (Internal Policy Gap Analysis)")
    st.write("**กลุ่มเป้าหมาย:** ผู้บริหารระดับสูง / HR / Compliance / Sustainability")
    
    with st.form("full_tool1"):
        st.subheader("หมวด A: การกำกับดูแลและนโยบาย (Governance & Policy)")
        q1_1 = st.radio("A1. มีการจัดทำ 'นโยบายสิทธิมนุษยชน' ที่อนุมัติโดยคณะกรรมการบริษัทหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_2 = st.radio("A2. นโยบายครอบคลุมประเด็นสำคัญ (แรงงานข้ามชาติ, สิทธิชุมชน, ความหลากหลาย) หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_3 = st.radio("A3. มีการสื่อสารนโยบายในภาษาที่พนักงานและคู่ค้าเข้าใจ (Native Languages) หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_4 = st.radio("A4. มีการระบุความรับผิดชอบด้านสิทธิมนุษยชนในระดับบอร์ดหรือผู้บริหารระดับสูงหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        
        st.subheader("หมวด B: กระบวนการตรวจสอบ (Due Diligence)")
        q2_1 = st.radio("B1. มีการประเมินความเสี่ยงด้านสิทธิมนุษยชน (HRA) ประจำปีหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q2_2 = st.radio("B2. มีระบบการตรวจสอบย้อนกลับ (Traceability) ในห่วงโซ่อุปทานต้นน้ำหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q2_3 = st.radio("B3. มีการกำหนดตัวชี้วัด (KPIs) ด้านสิทธิมนุษยชนในระดับหน่วยปฏิบัติการหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        
        st.subheader("หมวด C: กลไกการร้องเรียนและการเยียวยา (Grievance & Remedy)")
        q3_1 = st.radio("C1. มีช่องทางร้องเรียนที่เข้าถึงง่ายสำหรับกลุ่มเปราะบาง (เช่น แอปพลิเคชัน, เบอร์โทรเฉพาะภาษา) หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q3_2 = st.radio("C2. มีมาตรการคุ้มครองผู้แจ้งเบาะแส (Whistleblower Protection) จากการถูกกลั่นแกล้งหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q3_3 = st.radio("C3. มีขั้นตอนการเยียวยา (Remediation Plan) เมื่อพบการละเมิดสิทธิหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        
        if st.form_submit_button("บันทึกข้อมูลเครื่องมือที่ 1"):
            st.success("บันทึกข้อมูลเรียบร้อยแล้ว")

# --- TOOL 2: FULL DETAIL ---
elif choice == "Tool 2: แบบสอบถามการปฏิบัติหน้างาน":
    st.header("เครื่องมือที่ 2: แบบสอบถามการปฏิบัติ (Human Rights Survey)")
    st.write("**กลุ่มเป้าหมาย:** พนักงานไทย, พนักงานต่างชาติ, เกษตรกรในพันธสัญญา")
    
    with st.form("full_tool2"):
        st.subheader("1. สิทธิแรงงานและสภาพการจ้าง (Labor Rights)")
        q2_1 = st.select_slider("1.1 ความถูกต้องของค่าจ้าง: ได้รับครบและตรงเวลา?", options=[1,2,3,4,5], value=3)
        q2_2 = st.select_slider("1.2 สัญญาจ้าง: มีสัญญาในภาษาที่ท่านเข้าใจและเก็บไว้กับตัว?", options=[1,2,3,4,5], value=3)
        q2_3 = st.select_slider("1.3 วันหยุด: มีวันหยุดประจำสัปดาห์และวันหยุดตามกฎหมาย?", options=[1,2,3,4,5], value=3)
        
        st.subheader("2. อาชีวอนามัยและความปลอดภัย (OHS)")
        q3_1 = st.select_slider("2.1 อุปกรณ์ป้องกัน (PPE): ได้รับเพียงพอและอยู่ในสภาพดี?", options=[1,2,3,4,5], value=3)
        q3_2 = st.select_slider("2.2 การอบรม: ได้รับการสอนเรื่องความปลอดภัยก่อนเริ่มงาน?", options=[1,2,3,4,5], value=3)
        q3_3 = st.select_slider("2.3 สภาพแวดล้อม: ระบบจัดการความร้อน ฝุ่น และสารเคมี?", options=[1,2,3,4,5], value=3)
        
        st.subheader("3. การไม่เลือกปฏิบัติและเสรีภาพ (Equality & Freedom)")
        q4_1 = st.select_slider("3.1 ท่านได้รับการปฏิบัติที่เท่าเทียมโดยไม่คำนึงถึงสัญชาติหรือเพศ?", options=[1,2,3,4,5], value=3)
        q4_2 = st.select_slider("3.2 บรรยากาศที่ทำงานปราศจากการดุด่าหรือการคุกคาม?", options=[1,2,3,4,5], value=3)
        
        st.subheader("4. กลไกการร้องเรียน (Grievance)")
        q5_1 = st.select_slider("4.1 ความเชื่อมั่นในระบบร้องเรียนและความลับข้อมูล?", options=[1,2,3,4,5], value=3)
        
        if st.form_submit_button("ส่งข้อมูลเครื่องมือที่ 2"):
            st.balloons()

# --- TOOL 3 & 4 (รวมรายละเอียดตาม Word) ---
elif choice == "Tool 3: แนวทางการสัมภาษณ์เชิงลึก":
    st.header("เครื่องมือที่ 3: แนวทางการสัมภาษณ์กึ่งโครงสร้าง (Interview Guide)")
    with st.form("full_tool3"):
        st.subheader("หมวดการสรรหา (Ethical Recruitment)")
        q1 = st.text_area("1. รายละเอียดค่าใช้จ่ายในการสมัครงาน (ค่าหัวคิว/ค่าดำเนินการ):")
        q2 = st.text_area("2. การเข้าถึงเอกสารสิทธิ์และพาสปอร์ต:")
        st.subheader("หมวดความเป็นอยู่ (Living Conditions)")
        q3 = st.text_area("3. สภาพหอพักและความเป็นส่วนตัว:")
        q4 = st.text_area("4. ข้อจำกัดในการเดินทางหรือการออกนอกพื้นที่:")
        if st.form_submit_button("บันทึกบทสัมภาษณ์"):
            st.success("Saved")

elif choice == "Tool 4: แบบบันทึกการสังเกตการณ์ภาคสนาม":
    st.header("เครื่องมือที่ 4: แบบบันทึกการสังเกตการณ์ (Observation Checklist)")
    with st.form("full_tool4"):
        col1, col2 = st.columns(2)
        with col1:
            st.write("**สภาพแวดล้อมการทำงาน**")
            o1 = st.checkbox("ป้ายประกาศสิทธิแรงงานเป็นภาษา Native")
            o2 = st.checkbox("อุปกรณ์ดับเพลิง/ทางหนีไฟไม่มีสิ่งกีดขวาง")
            o3 = st.checkbox("พนักงานสวมใส่ PPE สอดคล้องกับความเสี่ยงหน้างาน")
        with col2:
            st.write("**สภาพหอพักและสุขอนามัย**")
            o4 = st.checkbox("ห้องน้ำแยกชาย-หญิงและสะอาด")
            o5 = st.checkbox("มีน้ำดื่มสะอาดเข้าถึงได้ตลอดเวลา")
            o6 = st.checkbox("หอพักมีระบบล็อคและความปลอดภัยพื้นฐาน")
        obs_note = st.text_area("บันทึกเชิงพรรณนา (Narrative Note):")
        if st.form_submit_button("บันทึกการสังเกตการณ์"):
            st.success("บันทึกสำเร็จ")

# --- TOOL 5: THE CORE (SEVERITY-LED RULE) ---
elif choice == "Tool 5: การประเมินนัยสำคัญ (Salient Risk)":
    st.header("⚖️ เครื่องมือที่ 5: Salient Human Rights Risks Scoring Matrix")
    st.info("หลักการคำนวณ: Severity-led Rule (ใช้ค่าสูงสุดของ Scale/Scope/Remediability) x Likelihood")
    
    col_in, col_res = st.columns([1, 1.5])
    
    with col_in:
        issue_name = st.text_input("ระบุประเด็นความเสี่ยง:", "สิทธิแรงงานในห่วงโซ่อุปทาน")
        
        st.write("---")
        st.subheader("1. การประเมินความรุนแรง (Severity)")
        sc_scale = st.slider("ขนาดของผลกระทบ (Scale)", 1, 5, 3)
        sc_scope = st.slider("ขอบเขตของผลกระทบ (Scope)", 1, 5, 3)
        sc_remedy = st.slider("การเยียวยา (Remediability)", 1, 5, 3)
        
        severity_max = max(sc_scale, sc_scope, sc_remedy)
        
        st.write("---")
        st.subheader("2. การประเมินโอกาสเกิด (Likelihood)")
        likelihood = st.slider("โอกาสที่จะเกิดขึ้น (Likelihood)", 1, 5, 2)
        
        final_score = severity_max * likelihood
        st.metric("Salience Score (Max S x L)", final_score)

    with col_res:
        st.subheader("Strategic Risk Heat Map (Interactive)")
        
        # สร้างข้อมูลสำหรับ Heat Map 5x5
        # แกนนอน (x) = Severity, แกนตั้ง (y) = Likelihood
        z_data = [
            [1, 2, 3, 4, 5],
            [2, 4, 6, 8, 10],
            [3, 6, 9, 12, 15],
            [4, 8, 12, 16, 20],
            [5, 10, 15, 20, 25]
        ]
        
        # สร้างกราฟ Heatmap โดยใช้ Plotly
        fig = px.imshow(
            z_data,
            labels=dict(x="Severity", y="Likelihood", color="Score"),
            x=[1, 2, 3, 4, 5],
            y=[1, 2, 3, 4, 5],
            color_continuous_scale=[[0, "#265F36"], [0.35, "#F9A818"], [1, "#EF4444"]], # เขียว -> ส้ม -> แดง
            origin='lower'
        )
        
        # เพิ่มจุด (Marker) แสดงตำแหน่งความเสี่ยงปัจจุบัน
        fig.add_scatter(
            x=[severity_max], 
            y=[likelihood], 
            mode='markers+text',
            marker=dict(color='white', size=20, symbol='x', line=dict(width=2, color='black')),
            text=["จุดความเสี่ยง"],
            textposition="top center",
            name="Current Risk"
        )

        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            height=400,
            coloraxis_showscale=False # ปิดแถบสีข้างๆ เพื่อความสะอาดตา
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.caption("พิกัดปัจจุบัน: Severity = {} | Likelihood = {}".format(severity_max, likelihood))

    # ส่วนสรุปผลด้านล่างกราฟ
    st.write("---")
    if final_score >= 16:
        st.error(f"🚩 ประเด็น '{issue_name}': ระดับ **วิกฤต (Salient Risk)**")
    elif final_score >= 8:
        st.warning(f"⚠️ ประเด็น '{issue_name}': ระดับ **นัยสำคัญ (Significant Risk)**")
    else:
        st.success(f"✅ ประเด็น '{issue_name}': ระดับ **ปกติ (Manageable Risk)**")

# --- FOOTER ---
st.markdown("---")
st.markdown("<p style='text-align: center;'>© 2026 Betagro Group | Sustainability Development Department (HRDD Division)</p>", unsafe_allow_html=True)