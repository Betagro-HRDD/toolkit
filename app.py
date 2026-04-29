import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. SETTING UP THE PAGE ---
st.set_page_config(
    page_title="Betagro HRDD Digital Toolkit",
    layout="wide"
)

# --- 2. PREMIUM CSS (บังคับสีเบทาโกรเข้มข้น) ---
st.markdown("""
    <style>
    .stApp { background-color: #F0F4F2 !important; }
    [data-testid="stSidebar"] { background-color: #265F36 !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    h1 { color: #265F36 !important; border-bottom: 5px solid #F9A818 !important; font-weight: 800 !important; }
    h2, h3 { color: #265F36 !important; font-weight: 700 !important; }
    .stButton>button { 
        background-color: #265F36 !important; color: white !important; 
        border: 2px solid #F9A818 !important; border-radius: 10px !important;
        font-weight: bold !important; height: 3em !important;
    }
    .stButton>button:hover { background-color: #F9A818 !important; color: #265F36 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER ---
st.markdown("<h1 style='text-align: center;'>BETAGRO</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>HRDD DIGITAL TOOLKIT</h3>", unsafe_allow_html=True)
st.write("---")

# --- 4. SIDEBAR MENU ---
choice = st.sidebar.radio("📋 เมนูหลัก:", 
    ["Tool 1: แบบประเมินสถานะองค์กร", 
     "Tool 2: แบบสอบถามการปฏิบัติ", 
     "Tool 3: แนวทางการสัมภาษณ์", 
     "Tool 4: แบบบันทึกการสังเกตการณ์",
     "Tool 5: ตารางประเมินนัยสำคัญ"])

# --- 5. CONTENT SECTIONS ---

if choice == "Tool 1: แบบประเมินสถานะองค์กร":
    st.header("📋 Tool 1: Self-Assessment (Gap Analysis)")
    with st.form("tool1"):
        st.subheader("ส่วนที่ 1: นโยบาย")
        q1 = st.radio("1.1 มีนโยบายสิทธิมนุษยชนที่อนุมัติโดยบอร์ดหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q2 = st.radio("1.2 ครอบคลุมกลุ่มเปราะบางหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        if st.form_submit_button("บันทึกข้อมูล"):
            st.success("บันทึกสำเร็จ")

elif choice == "Tool 2: แบบสอบถามการปฏิบัติ":
    st.header("📊 Tool 2: Human Rights Survey")
    with st.form("tool2"):
        q1 = st.select_slider("ค่าจ้างตรงเวลา?", options=[1,2,3,4,5], value=3)
        q2 = st.select_slider("ความปลอดภัย PPE?", options=[1,2,3,4,5], value=3)
        if st.form_submit_button("ส่งคำตอบ"):
            st.balloons()

elif choice == "Tool 3: แนวทางการสัมภาษณ์":
    st.header("🎙️ Tool 3: Interview Guide")
    with st.form("tool3"):
        q1 = st.text_area("บันทึกการสรรหา/ค่าหัวคิว:")
        q2 = st.text_area("บันทึกสภาพความเป็นอยู่:")
        if st.form_submit_button("บันทึกบทสัมภาษณ์"):
            st.success("Saved")

elif choice == "Tool 4: แบบบันทึกการสังเกตการณ์":
    st.header("🔎 Tool 4: Observation Log")
    with st.form("tool4"):
        c1 = st.checkbox("สวม PPE ครบ")
        c2 = st.checkbox("มีป้ายประกาศสิทธิแรงงาน")
        note = st.text_area("บันทึกเพิ่มเติม:")
        if st.form_submit_button("บันทึกการสังเกตการณ์"):
            st.success("บันทึกแล้ว")

elif choice == "Tool 5: ตารางประเมินนัยสำคัญ":
    st.header("⚖️ Tool 5: Risk Matrix & Heat Map")
    
    # ส่วนคำนวณ
    col_input, col_map = st.columns([1, 1])
    
    with col_input:
        st.subheader("วิเคราะห์ความเสี่ยง")
        issue = st.text_input("ชื่อประเด็นความเสี่ยง:", "แรงงานข้ามชาติ")
        s = st.slider("ระดับความรุนแรง (Severity)", 1, 5, 3)
        l = st.slider("โอกาสเกิด (Likelihood)", 1, 5, 2)
        score = s * l
        st.metric("คะแนนความเสี่ยง (Salience Score)", score)

    with col_map:
        st.subheader("Risk Heat Map")
        # ฟังก์ชันใส่สีให้ตาราง
        def color_map(val):
            if val >= 16: return 'background-color: #ff4b4b; color: white' # แดง
            if val >= 8: return 'background-color: #ffa500; color: white'  # ส้ม
            return 'background-color: #265f36; color: white'               # เขียว

        # สร้างตาราง 5x5
        data = [[r*c for c in range(1, 6)] for r in range(5, 0, -1)]
        df = pd.DataFrame(data, index=[5,4,3,2,1], columns=[1,2,3,4,5])
        st.table(df.style.applymap(color_map))
        st.caption("แกนนอน: Severity | แกนตั้ง: Likelihood")

    # สรุปผล
    if score >= 16:
        st.error(f"🚨 ประเด็น '{issue}': ระดับวิกฤต (Salient Risk) - ต้องจัดการทันที")
    elif score >= 8:
        st.warning(f"⚠️ ประเด็น '{issue}': ระดับนัยสำคัญ - ต้องเฝ้าระวัง")
    else:
        st.success(f"✅ ประเด็น '{issue}': ระดับปกติ - บริหารจัดการได้")

# --- FOOTER ---
st.markdown("---")
st.markdown("<p style='text-align: center;'>© 2024 Betagro Group | Sustainability Department</p>", unsafe_allow_html=True)